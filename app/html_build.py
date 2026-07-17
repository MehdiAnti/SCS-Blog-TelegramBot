import re

from bs4 import BeautifulSoup


REMOVE_TEXTS = [
    "Email This",
    "BlogThis",
    "Share to X",
    "Share to Facebook",
    "Share to Pinterest",
    "No comments",
    "Post a Comment",
]

SUPPORTED_TAGS = {
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "a",
    "b",
    "strong",
    "i",
    "em",
    "u",
    "ins",
    "s",
    "strike",
    "del",
    "blockquote",
    "ul",
    "ol",
    "li",
    "br",
    "img",
}

def _remove_unwanted_blocks(soup):
    """
    Remove Blogger share buttons and other unwanted blocks.
    """

    for text in REMOVE_TEXTS:

        nodes = soup.find_all(
            string=lambda s: (
                s and text.lower() in s.lower()
            )
        )

        for node in nodes:
            try:
                parent = node.parent

                if parent:
                    parent.decompose()

            except Exception:
                pass

    return soup


def _convert_iframes(soup):
    """
    Convert supported iframe widgets into Telegram-friendly links.
    """

    for iframe in soup.find_all("iframe"):

        src = iframe.get("src", "")

        if not src:
            iframe.decompose()
            continue

        if "youtube.com" in src:

            text = "\n🎥 Watch Video"

        elif "store.steampowered.com/widget/" in src:

            appid = re.search(
                r"/widget/(\d+)/",
                src,
            )

            if not appid:
                iframe.decompose()
                continue

            src = (
                "https://store.steampowered.com/app/"
                f"{appid.group(1)}/"
            )

            text = "\n🎮 Steam Store"

        else:
            iframe.decompose()
            continue

        link = soup.new_tag(
            "a",
            href=src,
        )

        link.string = text

        paragraph = soup.new_tag("p")
        paragraph.append(link)

        iframe.replace_with(paragraph)

    return soup


def _clean_tags(soup):
    """
    Remove unsupported HTML tags.
    """

    for tag in soup.find_all(True):

        if tag.name in ("html", "body"):
            continue

        if tag.name not in SUPPORTED_TAGS:

            if tag.name in (
                "script",
                "style",
                "iframe",
                "svg",
                "noscript",
            ):
                tag.decompose()

            else:
                tag.unwrap()

    return soup


def _cleanup_images_and_links(soup):
    """
    Remove empty links/headings/paragraphs.
    Convert GIF images into clickable links.
    """

    for img in soup.find_all("img"):

        src = img.get("src", "")

        if ".gif" in src.lower():

            link = soup.new_tag(
                "a",
                href=src,
            )

            link.string = "🎞 View Animation"

            paragraph = soup.new_tag("p")
            paragraph.append(link)

            img.replace_with(paragraph)

    for link in soup.find_all("a"):

        if not link.get_text(strip=True):

            if link.find("img"):
                link.unwrap()

            else:
                link.decompose()

    for paragraph in soup.find_all("p"):

        if (
            not paragraph.get_text(strip=True)
            and
            not paragraph.find("img")
        ):
            paragraph.decompose()

    for heading in soup.find_all([
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    ]):

        if not heading.get_text(strip=True):
            heading.decompose()

    return soup


def _strip_attributes(soup):
    """
    Keep only attributes supported by Telegram.
    """

    for tag in soup.find_all(True):

        if tag.name == "a":

            href = tag.get("href")

            tag.attrs = {}

            if href:
                tag["href"] = href

        elif tag.name == "img":

            src = tag.get("src")

            tag.attrs = {}

            if src:
                tag["src"] = src

        else:

            tag.attrs = {}

    return soup


def clean_article(article_html):
    """
    Clean Blogger article HTML for Telegram Rich Messages.
    """

    soup = BeautifulSoup(
        article_html,
        "lxml",
    )

    soup = _remove_unwanted_blocks(soup)

    soup = _convert_iframes(soup)

    soup = _clean_tags(soup)

    soup = _cleanup_images_and_links(soup)

    soup = _strip_attributes(soup)

    html = soup.body.decode_contents()

    print(
        f"Article cleaned | Length={len(html)}"
    )

    if not soup.find([
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "li",
    ]):
        print(
            "WARNING: No text blocks found"
        )

    return html.strip()


def build_preview(
    title,
    article_url,
    teaser,
):
    """
    Build Telegram photo caption.
    """

    return (
        f"<b>{title}</b>\n\n"
        f"{teaser}\n\n"
        f"🔗 {article_url}\n\n"
        f"🐳\n"
        f"Join: @SCSSoftwareFeed"
    )


def build_rich_article(article_html):
    """
    Build Telegram RichMessage HTML.
    Telegram currently accepts up to ~32k HTML.
    """

    html = article_html.strip()

    if len(html) > 32000:
        html = html[:32000]

    return html
