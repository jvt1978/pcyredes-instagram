import os
import time
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

BASE_URL = "https://graph.facebook.com/v19.0"
PUBLIC_IMAGES_BASE_URL = os.getenv("PUBLIC_IMAGES_BASE_URL", "")


def _create_carousel_item(account_id: str, token: str, image_url: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/{account_id}/media",
        params={
            "access_token": token,
            "image_url": image_url,
            "is_carousel_item": "true",
        }
    )
    if not resp.ok:
        raise RuntimeError(f"Error creando container: {resp.status_code} {resp.text}")
    return resp.json()["id"]


def _wait_for_media(container_id: str, token: str, max_wait: int = 60):
    for _ in range(max_wait // 5):
        resp = requests.get(
            f"{BASE_URL}/{container_id}",
            params={"fields": "status_code", "access_token": token}
        )
        status = resp.json().get("status_code", "")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Media container error: {resp.json()}")
        time.sleep(5)
    raise TimeoutError(f"Media container {container_id} not ready after {max_wait}s")


def post_carousel(image_paths: list, caption: str) -> dict:
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    if not token or not account_id:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN y INSTAGRAM_ACCOUNT_ID deben estar configurados en .env")

    base_url = os.getenv("PUBLIC_IMAGES_BASE_URL", "").rstrip("/")
    if not base_url:
        raise ValueError("PUBLIC_IMAGES_BASE_URL debe estar configurado en .env")

    print("Creando containers de Instagram...")
    children = []
    for path in image_paths:
        filename = os.path.basename(path)
        public_url = f"{base_url}/{filename}"
        print(f"  {filename} → {public_url}")
        container_id = _create_carousel_item(account_id, token, public_url)
        _wait_for_media(container_id, token)
        children.append(container_id)
        print(f"  Container listo: {container_id}")

    print("Creando carrusel...")
    carousel_resp = requests.post(
        f"{BASE_URL}/{account_id}/media",
        params={
            "access_token": token,
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
        }
    )
    if not carousel_resp.ok:
        raise RuntimeError(f"Error creando carrusel: {carousel_resp.status_code} {carousel_resp.text}")
    carousel_id = carousel_resp.json()["id"]
    _wait_for_media(carousel_id, token)

    print("Publicando...")
    publish_resp = requests.post(
        f"{BASE_URL}/{account_id}/media_publish",
        params={
            "access_token": token,
            "creation_id": carousel_id,
        }
    )
    if not publish_resp.ok:
        raise RuntimeError(f"Error publicando: {publish_resp.status_code} {publish_resp.text}")
    return publish_resp.json()
