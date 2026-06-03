import os
import re
import html
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Pages Facebook à suivre.
# Tu peux ajouter/enlever des lignes ici.
PAGES = [
    {
        "name": "USD Athlétisme",
        "url": "https://www.facebook.com/people/USD-Athl%C3%A9tisme/100057378042903/",
    },
    {
        "name": "Gravelines Athlétisme",
        "url": "https://www.facebook.com/people/Gravelines-Athl%C3%A9tisme/61585380171800/",
    },
]

OUTPUT_FILE = "public/rss.xml"
SITE_URL = os.getenv("SITE_URL", "https://example.github.io/facebook-rss/")
FEED_TITLE = os.getenv("FEED_TITLE", "Flux Facebook Athlétisme")
FEED_DESCRIPTION = os.getenv("FEED_DESCRIPTION", "Flux RSS généré automatiquement depuis des pages Facebook publiques.")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def fb_variants(url: str):
    """Construit quelques variantes plus légères que facebook.com classique."""
    clean = url.rstrip("/") + "/"
    variants = [clean]
    variants.append(clean.replace("www.facebook.com", "m.facebook.com"))
    variants.append(clean.replace("www.facebook.com", "mbasic.facebook.com"))
    return list(dict.fromkeys(variants))


def clean_text(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"\s+", " ", text).strip()
    bad = ["Se connecter", "Créer nouveau compte", "Mot de passe oublié", "Facebook"]
    for b in bad:
        if text == b:
            return ""
    return text


def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r.text


def extract_posts_from_html(page_name: str, source_url: str, text_html: str):
    soup = BeautifulSoup(text_html, "lxml")
    posts = []

    # Méthode 1 : liens permalink/story_fbid sur versions mobile/basic.
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(key in href for key in ["story_fbid", "/posts/", "/photos/", "permalink.php"]):
            container = a
            for _ in range(5):
                if container.parent:
                    container = container.parent
            text = clean_text(container.get_text(" "))
            link = urljoin(source_url, href)
            if text and len(text) > 40:
                posts.append({"title": f"{page_name} - publication Facebook", "text": text[:900], "link": link})

    # Méthode 2 : fallback sur gros blocs textuels publics.
    if not posts:
        for tag in soup.find_all(["article", "div"]):
            text = clean_text(tag.get_text(" "))
            if 80 <= len(text) <= 1600 and not any(x in text.lower() for x in ["cookies", "connexion", "mot de passe"]):
                posts.append({"title": f"{page_name} - publication Facebook", "text": text[:900], "link": source_url})

    # Déduplication simple.
    seen = set()
    unique = []
    for p in posts:
        key = re.sub(r"\W+", "", p["text"][:160].lower())
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique[:8]


def get_posts_for_page(page):
    for variant in fb_variants(page["url"]):
        try:
            content = fetch(variant)
            posts = extract_posts_from_html(page["name"], variant, content)
            if posts:
                return posts
        except Exception as exc:
            print(f"Erreur avec {variant}: {exc}")
    return [{
        "title": f"{page['name']} - flux non récupéré",
        "text": "Facebook a bloqué la récupération automatique de cette page lors de cette exécution. Réessaie plus tard ou vérifie que la page est publique.",
        "link": page["url"],
    }]


def build_feed(all_posts):
    fg = FeedGenerator()
    fg.id(SITE_URL)
    fg.title(FEED_TITLE)
    fg.link(href=SITE_URL, rel="alternate")
    fg.description(FEED_DESCRIPTION)
    fg.language("fr")
    fg.updated(datetime.now(timezone.utc))

    for idx, post in enumerate(all_posts):
        fe = fg.add_entry()
        guid = post.get("link", SITE_URL) + f"#{idx}"
        fe.id(guid)
        fe.title(post["title"])
        fe.link(href=post.get("link", SITE_URL))
        fe.description(post["text"])
        fe.pubDate(datetime.now(timezone.utc))

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    fg.rss_file(OUTPUT_FILE, pretty=True)
    print(f"Flux généré : {OUTPUT_FILE} avec {len(all_posts)} entrée(s)")


def main():
    all_posts = []
    for page in PAGES:
        all_posts.extend(get_posts_for_page(page))
    build_feed(all_posts)


if __name__ == "__main__":
    main()
