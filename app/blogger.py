import re

import requests

from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime

from app.config import (
    RSS_URL,
    HEADERS,
)

def _get_latest_post_homepage():

    response = requests.get(
        "https://blog.scssoft.com",
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "lxml",
    )

    post = soup.select_one(
        "h3.post-title.entry-title a"
    )

    if not post:
        raise Exception("No post found")

    return {
        "title": post.get_text(strip=True),
        "url": post["href"],
        "date": "",
    }


def _get_latest_post_rss():
    """
    Supports Atom and RSS feeds.
    """

    response = requests.get(
        RSS_URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "xml",
    )

    # Atom
    entry = soup.find("entry")

    if entry:

        title = ""

        if entry.title:
            title = entry.title.get_text(
                strip=True
            )

        url = ""

        for link in entry.find_all("link"):

            if link.get("rel") == "alternate":
                url = (
                    link.get("href")
                    or ""
                )
                break

        print(url)

        pub_date = ""

        updated = entry.find("updated")

        if updated:
            pub_date = updated.get_text(
                strip=True
            )

        return {
            "title": title,
            "url": url,
            "date": pub_date,
        }

    # RSS
    item = soup.find("item")

    if item:

        title = item.title.get_text(
            strip=True
        )

        url = item.link.get_text(
            strip=True
        )

        pub_date = ""

        if item.pubDate:
            try:
                pub_date = (
                    parsedate_to_datetime(
                        item.pubDate.text
                    ).isoformat()
                )
            except Exception:
                pub_date = item.pubDate.text

        return {
            "title": title,
            "url": url,
            "date": pub_date,
        }

    raise Exception(
        "No feed entries found"
    )


def _extract_youtube_link(iframe):

    src = iframe.get("src", "")

    if not src:
        return None

    if "youtube.com" in src:
        return src

    if "youtu.be" in src:
        return src

    return None


def _get_teaser(text, limit=400):

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    if len(text) <= limit:
        return text

    return (
        text[:limit].rstrip(" ", 1)[0]
        + "..."
    )
    

def get_latest_post():
    """
    Try homepage first.
    Fallback to RSS.
    """

    try:
        return _get_latest_post_homepage()

    except Exception as e:
        print(f"Homepage failed: {e}")

        return _get_latest_post_rss()


def fetch_article(url):
    """
    Returns:
    {
        title,
        url,
        hero_image,
        teaser,
        youtube_links,
        html
    }
    """

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "lxml",
    )

    title = ""

    title_tag = soup.select_one(
        "h3.post-title.entry-title"
    )

    if title_tag:
        title = title_tag.get_text(strip=True)

    body = (
        soup.select_one(".post-body")
        or
        soup.select_one(".entry-content")
    )

    if not body:
        raise Exception("Post body not found")

    hero_image = None

    for img in body.find_all("img"):

        parent = img.parent

        if (
            parent
            and parent.name == "a"
            and parent.get("href")
        ):
            hero_image = parent["href"]
            break

        src = (
            img.get("data-src")
            or img.get("src")
        )

        if src:
            hero_image = src
            break

    youtube_links = []

    for iframe in body.find_all("iframe"):

        yt = _extract_youtube_link(iframe)

        if yt:
            youtube_links.append(yt)

    for img in body.find_all("img"):

        parent = img.parent

        if (
            parent
            and parent.name == "a"
            and parent.get("href")
        ):
            img["src"] = parent["href"]

    article_text = body.get_text(
        "\n",
        strip=True,
    )

    teaser = _get_teaser(
        article_text,
        limit=400,
    )

    return {
        "title": title,
        "url": url,
        "hero_image": hero_image,
        "teaser": teaser,
        "youtube_links": youtube_links,
        "html": str(body),
    }
