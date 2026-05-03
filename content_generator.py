import os
import random
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)

client = Anthropic()

_TOPICS = [
    "ciberseguridad para pymes en 2025",
    "backup y recuperación ante desastres",
    "firewall y protección perimetral empresarial",
    "WiFi empresarial de alta densidad",
    "mantenimiento preventivo de servidores",
    "Microsoft 365 y productividad en pymes",
    "virtualización con VMware o Hyper-V",
    "VPN y acceso remoto seguro",
    "monitorización proactiva de infraestructura IT",
    "antivirus corporativo y endpoint protection",
    "Windows Server: novedades y buenas prácticas",
    "cableado estructurado Cat6A en oficinas",
    "directiva NIS2 y cumplimiento en España",
    "cloud híbrida para empresas europeas",
    "GDPR e infraestructura IT: lo que debes saber",
    "phishing y ingeniería social en empresas",
    "zero trust: el nuevo modelo de seguridad",
    "recuperación ante ransomware: guía práctica",
    "actualizaciones críticas de sistemas: por qué importan",
    "IT como ventaja competitiva para pymes",
    "soporte IT externalizado vs departamento propio",
    "SD-WAN para empresas con varias sedes",
    "Azure y Microsoft Cloud para empresas en España",
    "copias de seguridad en la nube: opciones para pymes",
    "gestión de dispositivos móviles (MDM) en empresas",
    "switches gestionables y segmentación de red",
    "continuidad de negocio: plan de contingencia IT",
    "inteligencia artificial en el soporte IT",
    "digitalización de pymes: por dónde empezar",
    "reducir costes IT sin perder seguridad",
]


def generate_post_content(post_title: str = None, post_url: str = None) -> dict:
    topic = post_title if post_title else random.choice(_TOPICS)
    source_hint = f" (basado en el artículo: {post_title})" if post_title else ""

    prompt = f"""Eres el community manager de PCyRedes, empresa de soporte IT y redes en Barcelona que trabaja con pymes en España y Europa.

Crea el texto para un post de Instagram sobre: "{topic}"{source_hint}.

El público son responsables de empresa o directores de pymes en España que no tienen departamento IT propio.

Formato de respuesta:

TITULO: (gancho en mayúsculas, máx 8 palabras, impactante)
SUBTITULO: (frase explicativa, máx 12 palabras)
PUNTO1: (dato o consejo clave con emoji, máx 12 palabras)
PUNTO2: (dato o consejo clave con emoji, máx 12 palabras)
PUNTO3: (dato o consejo clave con emoji, máx 12 palabras)
CIERRE: (pregunta retórica o dato impactante, máx 15 palabras)
CTA: (llamada a la acción corta sin URL, máx 10 palabras)

Responde solo con el contenido, sin explicaciones."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    result = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip().upper()] = value.strip()

    return result


def build_caption(content: dict, post_url: str = None) -> str:
    lines = []

    titulo = content.get("TITULO", "SOPORTE IT PARA TU EMPRESA")
    subtitulo = content.get("SUBTITULO", "")
    p1 = content.get("PUNTO1", "")
    p2 = content.get("PUNTO2", "")
    p3 = content.get("PUNTO3", "")
    cierre = content.get("CIERRE", "")
    cta = content.get("CTA", "Solicita tu Agente IT ahora")

    if titulo:
        lines.append(titulo)
    if subtitulo:
        lines.append(subtitulo)
    lines.append("")
    if p1:
        lines.append(p1)
    if p2:
        lines.append(p2)
    if p3:
        lines.append(p3)
    lines.append("")
    if cierre:
        lines.append(cierre)
    lines.append("")
    lines.append(f"👉 {cta}")
    lines.append("🌐 www.pcyredes.com/contacto")
    lines.append("")
    if post_url:
        lines.append(f"🔗 {post_url}")
        lines.append("")
    lines.append("#SoporteIT #PymesEspaña #Barcelona #CiberseguridadEuropa #InfraestructuraIT #PCyRedes #TechEspaña #SoporteInformatico #MarketingInstagram #MarketingDigital")

    return "\n".join(lines)[:2200]


# Mantener compatibilidad con código anterior
def generate_carousel_slides(post_title: str = None, post_url: str = None) -> list:
    content = generate_post_content(post_title, post_url)
    slides = [
        {"slide": 1, "lines": [content.get("TITULO", ""), content.get("SUBTITULO", "")]},
        {"slide": 2, "lines": [content.get("PUNTO1", ""), content.get("PUNTO2", ""), content.get("PUNTO3", "")]},
        {"slide": 3, "lines": [content.get("CIERRE", ""), content.get("CTA", "")]},
    ]
    return slides
