import os

from flask import (
    Flask,
    jsonify,
    request,
)

from app.config import (
    ALLOWED_USER,
    PORT,
)

from app.blogger import (
    get_latest_post,
)

from app.kv_storage import (
    article_is_new,
    get_last_article,
    save_detected,
)

from app.telegram import (
    send_article,
    send_message,
    send_rich_message,
)

app = Flask(__name__)

def cmd_start(chat_id):

    send_message(
        chat_id,
        (
            "bib"
        ),
    )


def cmd_latest(chat_id):

    article = get_last_article()

    text = (
        f"Title:\n"
        f"{article.get('title', '')}\n\n"
        f"URL:\n"
        f"{article.get('url', '')}"
    )

    send_message(
        chat_id,
        text,
    )


def cmd_test(chat_id, text):

    parts = text.split(
        " ",
        1,
    )

    if len(parts) != 2:

        send_message(
            chat_id,
            "Usage:\n/test ARTICLE_URL",
        )

        return

    article_url = parts[1].strip()

    send_article(
        chat_id,
        article_url,
    )

@app.route("/", methods=["GET"])
def home():

    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():

    update = request.get_json(silent=True) or {}

    message = (
        update.get("message")
        or update.get("edited_message")
        or {}
    )

    chat = message.get("chat") or {}

    chat_id = chat.get("id")

    if chat_id != ALLOWED_USER:
        return jsonify({"ok": True}), 200

    text = (
        message.get("text", "")
        .strip()
    )

    try:

        if text == "/start":

            cmd_start(chat_id)

        elif text == "/latest":

            cmd_latest(chat_id)

        elif text.startswith("/test "):

            cmd_test(
                chat_id,
                text,
            )

    except Exception as e:

        send_message(
            chat_id,
            f"Error:\n{e}",
        )

    return jsonify({"ok": True}), 200


@app.route("/check", methods=["GET"])
def check():

    try:

        latest = get_latest_post()

        if not article_is_new(
            latest["url"]
        ):

            return (
                jsonify({
                    "status": "no_new_article",
                }),
                200,
            )

        article = send_article(
            ALLOWED_USER,
            latest["url"],
        )

        save_detected(
            article["url"],
            article["title"],
        )

        return (
            jsonify({
                "status": "posted",
                "url": article["url"],
            }),
            200,
        )

    except Exception as e:

        return (
            jsonify({
                "error": str(e),
            }),
            500,
        )

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=PORT,
  )
