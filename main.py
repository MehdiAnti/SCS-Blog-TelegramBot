from datetime import (
    datetime,
)

from time import (
    perf_counter,
)

from flask import (
    Flask,
    jsonify,
    request,
)

from app.config import (
    ALLOWED_USER,
    PORT,
)

from app.status import (
    LAST_STATUS,
)


from app.blogger import (
    get_latest_post,
)

from app.kv_storage import (
    article_is_new,
    get_last_article,
    save_detected,
    get_status,
    save_status,
)

from app.telegram import (
    send_article,
    send_message,
)

app = Flask(__name__)

try:
    LAST_STATUS.update(get_status())
except Exception:
    pass

def cmd_start(chat_id):

    send_message(
        chat_id,
        (
            "<b>SCS Blog Telegram Bot</b>\n\n"
            
            "<b>Commands</b>\n"
            
            "/latest - Last stored article\n"
            "/status - Bot status\n"
            "/checknow - Check immediately\n"
            "/preview URL - Preview article\n"
            "/publish URL - Publish article\n"
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


def cmd_preview(chat_id, text):

    parts = text.split(
        " ",
        1,
    )

    if len(parts) != 2:

        send_message(
            chat_id,
            "Usage:\n/preview ARTICLE_URL",
        )

        return

    article_url = parts[1].strip()

    send_article(
        chat_id,
        article_url,
        publish_channel=False,
    )


def cmd_publish(chat_id, text):

    parts = text.split(
        " ",
        1,
    )

    if len(parts) != 2:

        send_message(
            chat_id,
            "Usage:\n/publish ARTICLE_URL",
        )

        return

    article_url = parts[1].strip()

    article = send_article(
        chat_id,
        article_url,
        publish_channel=True,
    )

    save_detected(
        article["url"],
        article["title"],
    )

    LAST_STATUS["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LAST_STATUS["last_result"] = "posted"
    LAST_STATUS["latest_title"] = article["title"]
    LAST_STATUS["latest_url"] = article["url"]
    LAST_STATUS["last_error"] = ""
    LAST_STATUS["kv"] = 0.0
    LAST_STATUS["total"] = 0.0

    save_status(LAST_STATUS)

    send_message(
        chat_id,
        (
            "✅ Published.\n\n"
            f"{article['title']}"
        ),
    )


def cmd_checknow(chat_id):

    try:

        result = run_check()

        if result["status"] == "no_new_article":

            send_message(
                chat_id,
                "ℹ️ No new article found.",
            )

            return

        send_message(
            chat_id,
            (
                "✅ Published successfully.\n\n"
                f"{result['title']}"
            ),
        )

    except Exception as e:

        send_message(
            chat_id,
            f"❌ {e}",
        )


def cmd_status(chat_id):

    s = get_status()

    text = (
        "<b>📊 Bot Status</b>\n\n"

        f"<b>Last Result:</b> {s['last_result']}\n"
        f"<b>Last Check:</b> {s['last_check']}\n\n"

        f"<b>Latest Article:</b>\n"
        f"{s['latest_title']}\n"
        f"{s['latest_url']}\n\n"

        "<b>Timings</b>\n"
        f"RSS: {s['rss']:.2f}s\n"
        f"Article: {s['article']:.2f}s\n"
        f"Clean: {s['clean']:.2f}s\n"
        f"Telegram: {s['telegram']:.2f}s\n"
        f"KV: {s['kv']:.2f}s\n"
        f"Total: {s['total']:.2f}s\n\n"

        f"<b>Last Error:</b>\n{s['last_error'] or 'None'}"
    )

    send_message(
        chat_id,
        text,
    )
    

def run_check():

    total_start = perf_counter()

    try:

        rss_start = perf_counter()
        latest = get_latest_post()
        LAST_STATUS["rss"] = round(
            perf_counter() - rss_start,
            2,
        )

        if not article_is_new(latest["url"]):

            return {
                "status": "no_new_article",
            }

        article = send_article(
            ALLOWED_USER,
            latest["url"],
            publish_channel=True,
        )
        
        kv_start = perf_counter()

        save_detected(
            article["url"],
            article["title"],
        )

        LAST_STATUS["kv"] = round(
            perf_counter() - kv_start,
            2,
        )

        LAST_STATUS["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LAST_STATUS["last_result"] = "posted"
        LAST_STATUS["latest_title"] = article["title"]
        LAST_STATUS["latest_url"] = article["url"]
        LAST_STATUS["last_error"] = ""
        LAST_STATUS["total"] = round(
            perf_counter() - total_start,
            2,
        )

        save_status(LAST_STATUS)

        return {
            "status": "posted",
            "url": article["url"],
            "title": article["title"],
        }

    except Exception as e:

        LAST_STATUS["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        LAST_STATUS["last_result"] = "failed"
        LAST_STATUS["last_error"] = str(e)

        save_status(LAST_STATUS)

        raise
        

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

        elif text.startswith("/preview "):

            cmd_preview(
                chat_id,
                text,
            )

        elif text.startswith("/publish "):
            
            cmd_publish(
                chat_id,
                text,
            )
        
        elif text == "/checknow":
            
            cmd_checknow(chat_id)
        
        elif text == "/status":
            
            cmd_status(chat_id)

    except Exception as e:

        send_message(
            chat_id,
            f"Error:\n{e}",
        )

    return jsonify({"ok": True}), 200


@app.route("/check", methods=["GET"])
def check():

    try:

        result = run_check()

        return (
            jsonify(result),
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
