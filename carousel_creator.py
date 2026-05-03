import os
from PIL import Image, ImageDraw, ImageFont

_DIR = os.path.dirname(os.path.abspath(__file__))

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"

COLOR_BG      = (12, 35, 75)
COLOR_ACCENT  = (0, 120, 215)
COLOR_WHITE   = (255, 255, 255)
COLOR_GRAY    = (180, 200, 220)
COLOR_STRIPE  = (0, 90, 170)
COLOR_DARK    = (8, 24, 52)

W, H = 1080, 1080


def _load_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap_text(text: str, font, draw, max_width: int) -> list:
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_base(img: Image.Image, draw: ImageDraw.ImageDraw, footer_url: str = "www.pcyredes.com"):
    draw.rectangle([0, 0, 8, H], fill=COLOR_ACCENT)
    draw.rectangle([0, 0, W, 6], fill=COLOR_ACCENT)
    draw.rectangle([0, H - 100, W, H], fill=COLOR_STRIPE)
    draw.rectangle([0, H - 102, W, H - 100], fill=COLOR_ACCENT)

    font_logo = _load_font(FONT_BOLD, 36)
    font_sub = _load_font(FONT_REGULAR, 20)
    draw.text((40, 40), "pcyredes", fill=COLOR_ACCENT, font=font_logo)
    draw.text((40, 82), "Soporte IT · Redes · Barcelona", fill=COLOR_GRAY, font=font_sub)
    draw.rectangle([40, 122, W - 40, 125], fill=COLOR_ACCENT)

    font_footer = _load_font(FONT_BOLD, 20)
    draw.text((40, H - 68), footer_url, fill=COLOR_WHITE, font=font_footer)
    draw.text((W - 340, H - 68), "#SoporteIT  #PymesEspaña", fill=COLOR_GRAY, font=font_footer)


def _draw_slide1(slide_data: dict, output_path: str) -> str:
    img = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)
    _draw_base(img, draw)

    lines = slide_data.get("lines", [])
    title = lines[0] if lines else "SOPORTE IT"
    subtitle = lines[1] if len(lines) > 1 else "PCyRedes Barcelona"

    font_title = _load_font(FONT_BOLD, 72)
    font_sub = _load_font(FONT_REGULAR, 32)

    title_words = " ".join(title.split()[:8]).upper()
    wrapped = _wrap_text(title_words, font_title, draw, W - 80)
    y = 200
    for line in wrapped[:4]:
        draw.text((40, y), line, fill=COLOR_WHITE, font=font_title)
        y += 90

    sub_wrapped = _wrap_text(subtitle, font_sub, draw, W - 80)
    y += 20
    for line in sub_wrapped[:2]:
        draw.text((40, y), line, fill=COLOR_GRAY, font=font_sub)
        y += 45

    font_cta = _load_font(FONT_BOLD, 26)
    draw.text((40, H - 160), "Desliza para saber más →", fill=COLOR_ACCENT, font=font_cta)

    font_url = _load_font(FONT_BOLD, 22)
    draw.rectangle([40, H - 200, 420, H - 170], fill=COLOR_ACCENT)
    draw.text((52, H - 197), "🌐 www.pcyredes.com", fill=COLOR_WHITE, font=font_url)

    img.save(output_path, "JPEG", quality=92)
    return output_path


def _draw_slide2(slide_data: dict, output_path: str) -> str:
    img = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)
    _draw_base(img, draw)

    lines = slide_data.get("lines", [])
    font_point = _load_font(FONT_REGULAR, 34)
    font_bold = _load_font(FONT_BOLD, 34)

    y = 180
    header = _load_font(FONT_BOLD, 42)
    draw.text((40, y), "Lo que debes saber:", fill=COLOR_ACCENT, font=header)
    y += 70

    for point in lines[:3]:
        draw.rectangle([40, y, W - 40, y + 2], fill=COLOR_STRIPE)
        y += 20
        wrapped = _wrap_text(point, font_point, draw, W - 100)
        for line in wrapped[:2]:
            draw.text((40, y), line, fill=COLOR_WHITE, font=font_point)
            y += 48
        y += 20

    font_url = _load_font(FONT_BOLD, 22)
    draw.rectangle([40, H - 160, 420, H - 130], fill=COLOR_ACCENT)
    draw.text((52, H - 157), "🌐 www.pcyredes.com", fill=COLOR_WHITE, font=font_url)

    img.save(output_path, "JPEG", quality=92)
    return output_path


CONTACT_URL = "www.pcyredes.com/contacto"


def _draw_slide3(slide_data: dict, output_path: str) -> str:
    img = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)
    _draw_base(img, draw, footer_url=CONTACT_URL)

    lines = slide_data.get("lines", [])
    question = lines[0] if lines else "¿Tu empresa tiene soporte IT de confianza?"
    cta = lines[1] if len(lines) > 1 else "Solicita tu agente IT ahora"

    font_q = _load_font(FONT_BOLD, 52)
    font_cta = _load_font(FONT_BOLD, 32)
    font_url_label = _load_font(FONT_REGULAR, 24)
    font_url_big = _load_font(FONT_BOLD, 30)

    y = 190
    wrapped_q = _wrap_text(question, font_q, draw, W - 80)
    for line in wrapped_q[:4]:
        draw.text((40, y), line, fill=COLOR_WHITE, font=font_q)
        y += 70

    y += 30
    draw.rectangle([40, y, W - 40, y + 4], fill=COLOR_ACCENT)
    y += 28

    wrapped_cta = _wrap_text(cta, font_cta, draw, W - 80)
    for line in wrapped_cta[:2]:
        draw.text((40, y), line, fill=COLOR_GRAY, font=font_cta)
        y += 48

    y += 20
    draw.text((40, y), "Solicita tu agente IT en:", fill=COLOR_GRAY, font=font_url_label)
    y += 34
    draw.rectangle([40, y, W - 40, y + 60], fill=COLOR_ACCENT)
    draw.text((60, y + 12), f"🌐  {CONTACT_URL}", fill=COLOR_WHITE, font=font_url_big)

    img.save(output_path, "JPEG", quality=92)
    return output_path


def create_carousel_images(slides_data: list, prefix: str = "carousel") -> list:
    output_dir = os.path.join(_DIR, "carousel_images")
    os.makedirs(output_dir, exist_ok=True)

    paths = []
    for i, slide in enumerate(slides_data[:3]):
        path = os.path.join(output_dir, f"{prefix}_slide{i+1}.jpg")
        if i == 0:
            _draw_slide1(slide, path)
        elif i == 1:
            _draw_slide2(slide, path)
        else:
            _draw_slide3(slide, path)
        paths.append(path)

    return paths
