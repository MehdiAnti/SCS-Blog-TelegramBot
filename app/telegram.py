import requests

from time import perf_counter

from app.status import (
    LAST_STATUS,
)

from app.config import (
    API_BASE,
    CHANNEL_ID,
    POST_TO_CHANNEL,
)

from app.blogger import fetch_article

from app.html_build import (
    clean_article,
    build_preview,
    build_rich_article,
)

def send_message(chat_id, text):

    response = requests.post(
        f"{API_BASE}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=60,
    )

    if not response.ok:
        raise Exception(response.text)

    return response.json()


def send_photo(chat_id, photo, caption):

    response = requests.post(
        f"{API_BASE}/sendPhoto",
        json={
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
            "parse_mode": "HTML",
        },
        timeout=60,
    )

    if not response.ok:
        raise Exception(response.text)

    return response.json()


def send_rich_message(
    chat_id,
    html,
    reply_to_message_id=None,
):

    payload = {
        "chat_id": chat_id,
        "rich_message": {
            "html": html,
        },
    }

    if reply_to_message_id:
        payload["reply_parameters"] = {
            "message_id": reply_to_message_id,
        }

    response = requests.post(
        f"{API_BASE}/sendRichMessage",
        json=payload,
        timeout=120,
    )

#    print(
#        "RichMSG Text:",
#        response.text,
#    )

    if not response.ok:
        raise Exception(response.text)

    return response.json()
  

def send_channel_article(
    preview,
    html,
    hero_image=None,
):

    if not POST_TO_CHANNEL:
        return

    try:

        reply_id = None

        if hero_image:

            photo = send_photo(
                CHANNEL_ID,
                hero_image,
                preview[:1024],
            )

            try:
                reply_id = (
                    photo["result"]["message_id"]
                )

            except Exception:
                pass

        send_rich_message(
            CHANNEL_ID,
            html,
            reply_id,
        )

    except Exception as e:

        print(
            f"Channel publish failed: {e}"
        )


def send_article(
    chat_id,
    article_url,
    publish_channel=False,
):

    article_start = perf_counter()

    article = fetch_article(article_url)

    LAST_STATUS["article"] = round(
        perf_counter() - article_start,
        3,
    )

    clean_start = perf_counter()

    article_html = clean_article(
        article["html"]
    )

    rich_html = build_rich_article(
        article_html
    )

    LAST_STATUS["clean"] = round(
        perf_counter() - clean_start,
        3,
    )

    preview = build_preview(
        article["title"],
        article["url"],
        article["teaser"],
    )

    telegram_start = perf_counter()

    try:

        photo_result = None

        if article["hero_image"]:

            photo_result = send_photo(
                chat_id,
                article["hero_image"],
                preview[:1024],
            )

        if publish_channel:

            print(
                f"Posting article to channel {CHANNEL_ID}"
            )

            send_channel_article(
                preview,
                rich_html,
                article["hero_image"],
            )

        reply_id = None

        try:

            if photo_result:

                reply_id = (
                    photo_result["result"]["message_id"]
                )

        except Exception:
            pass

        send_rich_message(
            chat_id,
            rich_html,
            reply_id,
        )

    finally:

        LAST_STATUS["telegram"] = round(
            perf_counter() - telegram_start,
            2,
        )

    return article
