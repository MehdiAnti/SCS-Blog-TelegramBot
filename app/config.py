import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ALLOWED_USER = int(os.getenv("ALLOWED_USER"))

CHANNEL_ID = os.getenv("CHANNEL_ID")

POST_TO_CHANNEL = (
    os.getenv("POST_TO_CHANNEL", "false").lower()
    == "true"
)

API_BASE = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
)

RSS_URL = (
    "https://feeds.feedburner.com/ScsSoftwaresBlog"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64)"
    )
}

CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_NAMESPACE_ID = os.getenv("CF_NAMESPACE_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")

PORT = int(
    os.getenv("PORT", 10000)
)
