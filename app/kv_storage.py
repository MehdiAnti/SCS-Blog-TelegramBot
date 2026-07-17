import json
import requests

from app.config import (
    CF_ACCOUNT_ID,
    CF_NAMESPACE_ID,
    CF_API_TOKEN,
)

KEY = "latest_article"


def _headers():
    return {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
    }


def _url():
    return (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CF_ACCOUNT_ID}/storage/kv/namespaces/"
        f"{CF_NAMESPACE_ID}/values/{KEY}"
    )


def _normalize_url(url):
    return (
        url.replace("http://", "https://")
        .rstrip("/")
        .strip()
    )


def _load_detected():

    response = requests.get(
        _url(),
        headers=_headers(),
        timeout=30,
    )

    if response.status_code == 404:
        return {
            "url": "",
            "title": "",
        }

    response.raise_for_status()

    try:
        return response.json()
    except Exception:
        return {
            "url": "",
            "title": "",
        }


def get_last_article():
    return _load_detected()


def article_is_new(article_url):

    stored = _load_detected()

    return (
        _normalize_url(article_url)
        !=
        _normalize_url(
            stored.get("url", "")
        )
    )


def save_detected(url_value, title):

    payload = {
        "url": _normalize_url(url_value),
        "title": title,
    }

    response = requests.put(
        _url(),
        headers=_headers(),
        data=json.dumps(payload),
        timeout=30,
    )

    response.raise_for_status()

    return True
