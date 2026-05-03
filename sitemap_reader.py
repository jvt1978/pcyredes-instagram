import os
import json
import requests
from bs4 import BeautifulSoup

_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLISHED_FILE = os.path.join(_DIR, "published_instagram.json")
SITEMAP_URL = os.getenv("SITEMAP_URL", "https://www.pcyredes.com/sitemap-blog-es.xml")


def slug_to_title(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    return slug.replace("-", " ").capitalize()


def get_blog_posts(limit: int = 5) -> list:
    try:
        resp = requests.get(SITEMAP_URL, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
        urls = [loc.text.strip() for loc in soup.find_all("loc")]
        posts = []
        for u in urls:
            parts = u.rstrip("/").split("/")
            if "blog" in parts and parts[-1] != "blog":
                posts.append({"link": u, "title": slug_to_title(u)})
        return posts[:limit]
    except Exception as e:
        print(f"⚠️  Error leyendo sitemap: {e}")
        return []


def get_published() -> set:
    if not os.path.exists(PUBLISHED_FILE):
        return set()
    with open(PUBLISHED_FILE, "r") as f:
        return set(json.load(f))


def mark_as_published(url: str):
    published = get_published()
    published.add(url)
    with open(PUBLISHED_FILE, "w") as f:
        json.dump(list(published), f)


def get_recent_posts(n: int = 3) -> list:
    return get_blog_posts(limit=n)
