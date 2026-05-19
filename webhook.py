import os
import threading
import logging
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

app = Flask(__name__)
_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename=os.path.join(_DIR, "instagram.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "pcyredes_webhook_2025")
TRIGGER_KEYWORD = "marketing instagram"
TRIGGER_LINKEDIN = "linkedin"


def _send_whatsapp_reply(to: str, text: str):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    requests.post(
        f"https://graph.facebook.com/v18.0/{phone_id}/messages",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    )


def _run_post_in_background(sender: str):
    try:
        _send_whatsapp_reply(sender, "⏳ Generando y publicando post en Instagram...")
        from main import run
        run()
        _send_whatsapp_reply(sender, "✅ Post publicado en Instagram correctamente.")
        logging.info(f"Post Instagram manual disparado por WhatsApp desde {sender}")
    except Exception as e:
        logging.error(f"Error en post Instagram manual: {e}")
        _send_whatsapp_reply(sender, f"❌ Error al publicar en Instagram: {str(e)[:200]}")


def _run_linkedin_in_background(sender: str):
    try:
        _send_whatsapp_reply(sender, "⏳ Revisando blog y publicando en LinkedIn...")
        from linkedin_main import run
        result = run()
        title = result.get("title", "")
        url = result.get("url", "")
        _send_whatsapp_reply(sender, f"✅ Post publicado en LinkedIn.\n📝 {title}\n🔗 {url}")
        logging.info(f"Post LinkedIn manual disparado por WhatsApp desde {sender}")
    except Exception as e:
        logging.error(f"Error en post LinkedIn manual: {e}")
        _send_whatsapp_reply(sender, f"❌ Error al publicar en LinkedIn: {str(e)[:200]}")


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json(silent=True) or {}
    try:
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        for msg in messages:
            if msg.get("type") != "text":
                continue
            text = msg.get("text", {}).get("body", "").lower().strip()
            sender = msg.get("from", "")

            if TRIGGER_KEYWORD in text:
                logging.info(f"Keyword Instagram detectada de {sender}: '{text}'")
                t = threading.Thread(target=_run_post_in_background, args=(sender,))
                t.daemon = True
                t.start()
            elif TRIGGER_LINKEDIN in text:
                logging.info(f"Keyword LinkedIn detectada de {sender}: '{text}'")
                t = threading.Thread(target=_run_linkedin_in_background, args=(sender,))
                t.daemon = True
                t.start()

    except Exception as e:
        logging.error(f"Error procesando webhook: {e}")

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
