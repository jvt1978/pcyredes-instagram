import os
import json
import random
import logging
from anthropic import Anthropic
from dotenv import load_dotenv
from sitemap_reader import get_blog_posts
from linkedin_poster import post_to_linkedin

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLISHED_FILE = os.path.join(_DIR, "published_linkedin.json")

logging.basicConfig(
    filename=os.path.join(_DIR, "instagram.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)

client = Anthropic()


def _get_published() -> set:
    if not os.path.exists(PUBLISHED_FILE):
        return set()
    with open(PUBLISHED_FILE, "r") as f:
        return set(json.load(f))


def _mark_published(url: str):
    published = _get_published()
    published.add(url)
    with open(PUBLISHED_FILE, "w") as f:
        json.dump(list(published), f)


def _generate_linkedin_text(title: str, url: str) -> str:
    prompt = f"""Eres el responsable de comunicación B2B de PCyRedes, empresa de soporte IT y redes en Barcelona especializada en pymes en España y Europa (www.pcyredes.com).

Escribe un post para LinkedIn basado en el artículo del blog: "{title}"
URL del artículo: {url}

El público son directores de empresa, responsables de IT y gerentes de pymes en España.

Formato del post:
- Gancho inicial impactante (1-2 líneas)
- 3-4 puntos clave con valor real para el lector (usa emojis sutiles ✅ 🔐 💡 etc.)
- Cierre con pregunta o reflexión que invite a comentar
- CTA claro para leer el artículo completo
- 4-5 hashtags B2B relevantes al final

Tono: profesional pero cercano, directo, sin jerga innecesaria. Máximo 1200 caracteres.
Responde solo con el texto del post, listo para publicar."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def run() -> dict:
    posts = get_blog_posts(limit=10)
    published = _get_published()

    new_post = None
    for p in posts:
        if p["link"] not in published:
            new_post = p
            break

    if not new_post:
        # No hay post nuevo: publicar sobre el más reciente igualmente
        if posts:
            new_post = posts[0]
        else:
            raise RuntimeError("No se encontraron artículos en el blog de PCyRedes.")

    title = new_post["title"]
    url = new_post["link"]

    print(f"Generando post LinkedIn para: {title}")
    text = _generate_linkedin_text(title, url)

    print("\n=== TEXTO LINKEDIN ===")
    print(text)
    print("\n=== Publicando en LinkedIn... ===")

    post_id = post_to_linkedin(
        text=text,
        article_url=url,
        article_title=title,
        article_description=f"Artículo del blog de PCyRedes: {title}",
    )

    _mark_published(url)
    logging.info(f"LinkedIn post publicado: {post_id} | {title} | {url}")
    print(f"✓ Publicado en LinkedIn: {post_id}")

    return {"post_id": post_id, "title": title, "url": url}


if __name__ == "__main__":
    run()
