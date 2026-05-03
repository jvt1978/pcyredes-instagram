import os
import logging
import requests
import time
from dotenv import load_dotenv
from sitemap_reader import get_recent_posts
from content_generator import generate_post_content, build_caption
from notifier import notify_ceo

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename=os.path.join(_DIR, "instagram.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)

BASE_URL = "https://graph.facebook.com/v19.0"
IMAGE_URL = "https://www.pcyredes.com/og-image.png"


def post_single_image(caption: str) -> dict:
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    if not token or not account_id:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN y INSTAGRAM_ACCOUNT_ID deben estar configurados en .env")

    resp = requests.post(
        f"{BASE_URL}/{account_id}/media",
        params={
            "access_token": token,
            "image_url": IMAGE_URL,
            "caption": caption,
        }
    )
    if not resp.ok:
        raise RuntimeError(f"Error creando container: {resp.status_code} {resp.text}")

    container_id = resp.json()["id"]

    for _ in range(12):
        r = requests.get(
            f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": token}
        )
        status = r.json().get("status_code", "")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError(f"Container error: {r.json()}")
        time.sleep(5)

    pub = requests.post(
        f"{BASE_URL}/{account_id}/media_publish",
        params={"access_token": token, "creation_id": container_id}
    )
    if not pub.ok:
        raise RuntimeError(f"Error publicando: {pub.status_code} {pub.text}")

    return pub.json()


def run():
    print("=== PCyRedes Instagram Bot ===\n")

    posts = get_recent_posts(n=3)
    if posts:
        post = posts[0]
        print(f"Usando artículo: {post['title']}")
        content = generate_post_content(post["title"], post["link"])
        caption = build_caption(content, post["link"])
        title = post["title"]
    else:
        print("Sin artículos recientes. Generando contenido educativo IT...\n")
        content = generate_post_content()
        caption = build_caption(content)
        title = content.get("TITULO", "Post IT")

    print("\n=== CAPTION ===")
    print(caption)
    print("\n=== Publicando... ===")

    result = post_single_image(caption)
    instagram_id = result.get("id", "OK")
    print(f"\n✓ Publicado en Instagram: {instagram_id}")

    logging.info(f"Post publicado: {instagram_id} | {title}")
    notify_ceo(title, instagram_id)


if __name__ == "__main__":
    run()
