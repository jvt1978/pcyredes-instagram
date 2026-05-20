import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

LINKEDIN_API = "https://api.linkedin.com/rest/posts"


def post_to_linkedin(text: str, article_url: str = None, article_title: str = None, article_description: str = None) -> str:
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN")  # ej: urn:li:organization:12345

    if not token or not author_urn:
        raise ValueError("LINKEDIN_ACCESS_TOKEN y LINKEDIN_AUTHOR_URN deben estar en .env")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202506",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    body = {
        "author": author_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    if article_url:
        body["content"] = {
            "article": {
                "source": article_url,
                "title": article_title or "PCyRedes Blog",
                "description": article_description or "",
            }
        }

    resp = requests.post(LINKEDIN_API, headers=headers, data=json.dumps(body))

    if not resp.ok:
        raise RuntimeError(f"Error publicando en LinkedIn: {resp.status_code} {resp.text}")

    post_id = resp.headers.get("x-restli-id", resp.headers.get("X-RestLi-Id", "OK"))
    return post_id
