# -*- coding: utf-8 -*-
import os
import json
import uuid
import math
import random
import time
import hashlib
import colorsys
import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
import requests
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------------------
# 1. VERİ YAPILARI (MODELS)
# ------------------------------------------------------------------------------

@dataclass
class ColorPalette:
    name: str
    bg_start: Tuple[int, int, int, int]
    bg_end: Tuple[int, int, int, int]
    neon_primary: Tuple[int, int, int, int]
    neon_secondary: Tuple[int, int, int, int]
    neon_accent: Tuple[int, int, int, int]
    text_main: Tuple[int, int, int, int]
    text_sub: Tuple[int, int, int, int]
    border_color: Tuple[int, int, int, int]

@dataclass
class LayoutSpec:
    archetype: str          # "centered_hero", "split_asymmetric", "cyber_hud", "minimalist_floating", "slant_esports"
    alignment: str          # "left", "center", "right"
    border_style: str       # "tech_brackets", "neon_glow", "double_chamfer", "minimal_rounded"
    pattern_type: str       # "hex_mesh", "scanlines", "diagonal_stripes", "dot_matrix", "cyber_grid", "none"
    badge_position: str     # "top_left", "bottom_center", "floating_right"
    decor_density: float    # 0.2 - 0.9
    seed: int = 0

    def compute_signature(self) -> str:
        """Tasarımın yapısal parmak izini hesaplar."""
        raw = f"{self.archetype}|{self.alignment}|{self.border_style}|{self.pattern_type}|{self.badge_position}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

def hex_to_rgba(hex_code: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Hex kodunu (örn: #bc13fe) RGBA tuple formatına dönüştürür."""
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join([c * 2 for c in hex_code])
    if len(hex_code) >= 6:
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return (r, g, b, alpha)
    return (138, 43, 226, alpha)

# ------------------------------------------------------------------------------
# 2. AI & NLP DESTEKLİ RENK ENTEGRATÖRÜ (COLOR HARMONIZER)
# ------------------------------------------------------------------------------

class AIColorHarmonizer:
    """
    Doğal dildeki renk taleplerini (örn: 'siberpunk moru ve neon yeşil')
    yayıncı overlay'leri için yüksek kontrastlı 5'li renk paletine dönüştürür.
    """
    PRESET_PALETTES = {
        "Cyber Gothic Purple": ColorPalette(
            name="Cyber Gothic Purple",
            bg_start=(15, 10, 26, 255),
            bg_end=(35, 12, 60, 255),
            neon_primary=(138, 43, 226, 255),
            neon_secondary=(199, 125, 255, 255),
            neon_accent=(0, 245, 212, 255),
            text_main=(245, 235, 255, 255),
            text_sub=(180, 160, 210, 255),
            border_color=(160, 60, 255, 255)
        ),
        "Neon Cyberpunk (Mavi/Pembe)": ColorPalette(
            name="Neon Cyberpunk",
            bg_start=(10, 14, 25, 255),
            bg_end=(20, 30, 50, 255),
            neon_primary=(0, 245, 212, 255),
            neon_secondary=(255, 0, 128, 255),
            neon_accent=(255, 222, 89, 255),
            text_main=(240, 250, 255, 255),
            text_sub=(150, 200, 230, 255),
            border_color=(0, 245, 212, 255)
        ),
        "Blood Red (Kırmızı/Siyah)": ColorPalette(
            name="Blood Red",
            bg_start=(18, 8, 10, 255),
            bg_end=(45, 12, 16, 255),
            neon_primary=(230, 57, 70, 255),
            neon_secondary=(255, 107, 107, 255),
            neon_accent=(244, 162, 97, 255),
            text_main=(255, 240, 240, 255),
            text_sub=(210, 160, 160, 255),
            border_color=(230, 57, 70, 255)
        ),
        "Emerald Green (Yeşil/Siyah)": ColorPalette(
            name="Emerald Green",
            bg_start=(8, 20, 15, 255),
            bg_end=(15, 45, 30, 255),
            neon_primary=(16, 185, 129, 255),
            neon_secondary=(52, 211, 153, 255),
            neon_accent=(110, 231, 183, 255),
            text_main=(240, 255, 245, 255),
            text_sub=(150, 210, 180, 255),
            border_color=(16, 185, 129, 255)
        ),
        "Retro Synthwave": ColorPalette(
            name="Retro Synthwave",
            bg_start=(20, 8, 35, 255),
            bg_end=(45, 15, 65, 255),
            neon_primary=(255, 0, 128, 255),
            neon_secondary=(121, 40, 202, 255),
            neon_accent=(0, 245, 212, 255),
            text_main=(255, 245, 255, 255),
            text_sub=(215, 180, 230, 255),
            border_color=(255, 0, 128, 255)
        ),
        "Minimalist & Clean": ColorPalette(
            name="Minimalist & Clean",
            bg_start=(12, 12, 14, 255),
            bg_end=(22, 22, 26, 255),
            neon_primary=(255, 255, 255, 255),
            neon_secondary=(170, 170, 180, 255),
            neon_accent=(56, 239, 125, 255),
            text_main=(255, 255, 255, 255),
            text_sub=(160, 160, 175, 255),
            border_color=(200, 200, 210, 255)
        )
    }

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def resolve_palette(self, color_text: str = "", preset_name: str = "Tamamen Rastgele") -> ColorPalette:
        color_text = (color_text or "").strip()

        # 1. Kullanıcı serbest metin girdiyse ve API key varsa Gemini AI'ya sor
        if self.api_key and color_text:
            ai_pal = self._query_gemini_palette(color_text, preset_name)
            if ai_pal:
                return ai_pal

        # 2. Heuristic Doğal Dil Kelime Taraması (Yerel Akıllı Ayrıştırıcı)
        if color_text:
            text_lower = color_text.lower()
            if "mor" in text_lower or "purple" in text_lower:
                return self.PRESET_PALETTES["Cyber Gothic Purple"]
            elif "siber" in text_lower or "cyber" in text_lower or "neon" in text_lower or "pembe" in text_lower:
                return self.PRESET_PALETTES["Neon Cyberpunk (Mavi/Pembe)"]
            elif "kırmızı" in text_lower or "red" in text_lower or "kan" in text_lower:
                return self.PRESET_PALETTES["Blood Red (Kırmızı/Siyah)"]
            elif "yeşil" in text_lower or "green" in text_lower or "mint" in text_lower:
                return self.PRESET_PALETTES["Emerald Green (Yeşil/Siyah)"]
            elif "retro" in text_lower or "synth" in text_lower:
                return self.PRESET_PALETTES["Retro Synthwave"]
            elif "minimal" in text_lower or "sade" in text_lower or "beyaz" in text_lower:
                return self.PRESET_PALETTES["Minimalist & Clean"]

        # 3. Hazır Preset Seçimi
        for k, v in self.PRESET_PALETTES.items():
            if k.lower() in preset_name.lower():
                return v

        # 4. Tamamen Rastgele HSL Tabanlı Harmonik Palet Üretimi
        return self._generate_procedural_palette()

    def _generate_procedural_palette(self) -> ColorPalette:
        base_hue = random.random()
        comp_hue = (base_hue + 0.5) % 1.0
        acc_hue = (base_hue + 0.25) % 1.0

        def to_rgb(h, l, s):
            return tuple([int(c * 255) for c in colorsys.hls_to_rgb(h, l, s)] + [255])

        bg_s = to_rgb(base_hue, 0.05, 0.40)
        bg_e = to_rgb(base_hue, 0.12, 0.50)
        p_rgb = to_rgb(base_hue, 0.55, 0.95)
        s_rgb = to_rgb(comp_hue, 0.65, 0.90)
        a_rgb = to_rgb(acc_hue, 0.70, 1.0)

        return ColorPalette(
            name=f"Procedural #{int(base_hue*360)}",
            bg_start=bg_s,
            bg_end=bg_e,
            neon_primary=p_rgb,
            neon_secondary=s_rgb,
            neon_accent=a_rgb,
            text_main=(250, 250, 255, 255),
            text_sub=(190, 185, 210, 255),
            border_color=p_rgb
        )

    def _query_gemini_palette(self, color_text: str, preset: str) -> Optional[ColorPalette]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        prompt = f"""
        Sen profesyonel bir espor yayın grafik tasarımcısısın.
        Kullanıcının talep ettiği renk tanımı: '{color_text}' (Preset: '{preset}').
        OBS yayın overlay seti için 5 renkli uyumlu palet üret.
        YALNIZCA aşağıdaki JSON formatını döndür:
        {{
            "name": "Palet Adı",
            "bg_start": "#0a0a14",
            "bg_end": "#1e1028",
            "neon_primary": "#8a2be2",
            "neon_secondary": "#c77dff",
            "neon_accent": "#00f5d4"
        }}
        """
        try:
            r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=5)
            if r.status_code == 200:
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    d = json.loads(match.group(0))
                    return ColorPalette(
                        name=d.get("name", "Gemini AI Palette"),
                        bg_start=hex_to_rgba(d.get("bg_start", "#0a0a14")),
                        bg_end=hex_to_rgba(d.get("bg_end", "#1e1028")),
                        neon_primary=hex_to_rgba(d.get("neon_primary", "#8a2be2")),
                        neon_secondary=hex_to_rgba(d.get("neon_secondary", "#c77dff")),
                        neon_accent=hex_to_rgba(d.get("neon_accent", "#00f5d4")),
                        text_main=(250, 250, 255, 255),
                        text_sub=(190, 185, 210, 255),
                        border_color=hex_to_rgba(d.get("neon_primary", "#8a2be2"))
                    )
        except Exception:
            pass
        return None

THEME_PALETTES = AIColorHarmonizer.PRESET_PALETTES

# ------------------------------------------------------------------------------
# 3. EŞSİZLİK & RASTGELELİK MOTORU (ANTI-REPETITION ENGINE)
# ------------------------------------------------------------------------------

class AntiRepetitionEngine:
    """
    Üretilen tasarımların şablon parmak izlerini hafızada tutar
    ve her butona basıldığında daha önce üretilmemiş, özgün bir kompozisyon türetir.
    """
    ARCHETYPES = [
        "centered_hero",       # Ortalanmış büyük kanal logosu ve simetrik çizgiler
        "split_asymmetric",    # Sol taraf panel, sağ taraf dinamik soyut geometri
        "cyber_hud",           # Siberpunk bilimkurgu HUD arayüzü, köşeli parantezler
        "minimalist_floating", # Ultra temiz, zarif ince çizgiler
        "slant_esports"        # Agresif açılı diyagonal çizgiler, espor stili
    ]

    BORDER_STYLES = ["tech_brackets", "neon_glow", "double_chamfer", "minimal_rounded"]
    PATTERNS = ["hex_mesh", "scanlines", "diagonal_stripes", "dot_matrix", "cyber_grid", "none"]
    ALIGNMENTS = ["center", "left", "center"]
    BADGE_POSITIONS = ["bottom_center", "top_left", "floating_right"]

    def __init__(self, cache_limit: int = 40):
        self.cache_limit = cache_limit
        self.history: List[str] = []

    def derive_unique_layout(self, preset_name: str = "Tamamen Rastgele") -> LayoutSpec:
        for _ in range(30):
            seed = int(time.time() * 1000) ^ random.randint(1000, 999999)
            rng = random.Random(seed)

            if "Minimalist" in preset_name:
                arch = "minimalist_floating"
                b_style = "minimal_rounded"
                pattern = "none"
                density = 0.2
            elif "Siberpunk" in preset_name or "Cyber" in preset_name:
                arch = rng.choice(["cyber_hud", "slant_esports"])
                b_style = rng.choice(["tech_brackets", "double_chamfer"])
                pattern = rng.choice(["hex_mesh", "scanlines", "cyber_grid"])
                density = 0.8
            elif "Blood" in preset_name or "Gothic" in preset_name:
                arch = rng.choice(["split_asymmetric", "centered_hero"])
                b_style = rng.choice(["neon_glow", "double_chamfer"])
                pattern = rng.choice(["diagonal_stripes", "scanlines"])
                density = 0.6
            else: # Tamamen Rastgele
                arch = rng.choice(self.ARCHETYPES)
                b_style = rng.choice(self.BORDER_STYLES)
                pattern = rng.choice(self.PATTERNS)
                density = rng.uniform(0.3, 0.85)

            layout = LayoutSpec(
                archetype=arch,
                alignment=rng.choice(self.ALIGNMENTS),
                border_style=b_style,
                pattern_type=pattern,
                badge_position=rng.choice(self.BADGE_POSITIONS),
                decor_density=density,
                seed=seed
            )

            sig = layout.compute_signature()
            if sig not in self.history:
                self._record(sig)
                return layout

        if self.history:
            self.history.pop(0)
        return layout

    def _record(self, sig: str):
        self.history.append(sig)
        if len(self.history) > self.cache_limit:
            self.history.pop(0)

# Global Tekil Örnekler
_harmonizer_instance = AIColorHarmonizer()
_repetition_instance = AntiRepetitionEngine()

def get_appdata_obs_assets_dir():
    appdata = os.environ.get("APPDATA", "")
    obs_assets = os.path.join(appdata, "obs-studio", "ripleytia_assets")
    os.makedirs(obs_assets, exist_ok=True)
    return obs_assets

def get_system_font(size=36, bold=False):
    font_names = [
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "tahoma.ttf"
    ]
    for fn in font_names:
        font_path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fn)
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ------------------------------------------------------------------------------
# 4. DİNAMİK AÇILIŞ VE MOLA BANNER ÜRETİCİSİ (PROSEDÜREL 1920x1080)
# ------------------------------------------------------------------------------
def generate_channel_banner(channel_name="Ripleytia", palette=None, layout=None, mode="starting", custom_title=None):
    """
    LayoutSpec ve ColorPalette'e göre kendini asla tekrar etmeyen dinamik 1920x1080 banner üretir.
    """
    if palette is None:
        palette = _harmonizer_instance.resolve_palette()
    if layout is None:
        layout = _repetition_instance.derive_unique_layout()

    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), palette.bg_start)
    draw = ImageDraw.Draw(img)
    rng = random.Random(layout.seed)

    # 1. Dinamik Dikey Gradyan
    for y in range(h):
        blend = y / h
        r = int(palette.bg_start[0] * (1 - blend) + palette.bg_end[0] * blend)
        g = int(palette.bg_start[1] * (1 - blend) + palette.bg_end[1] * blend)
        b = int(palette.bg_start[2] * (1 - blend) + palette.bg_end[2] * blend)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # 2. Prosedürel Arka Plan Deseni (Pattern)
    pat = layout.pattern_type
    p_alpha = int(40 * layout.decor_density)
    pat_col = (palette.neon_primary[0], palette.neon_primary[1], palette.neon_primary[2], p_alpha)

    if pat == "diagonal_stripes":
        step = 50
        for x in range(-w, w * 2, step):
            draw.line([(x, 0), (x + h, h)], fill=pat_col, width=1)
    elif pat == "hex_mesh":
        step = 70
        for y in range(0, h + step, step):
            for x in range(0, w + step, step):
                draw.regular_polygon((x, y, 16), 6, rotation=0, outline=pat_col)
    elif pat == "cyber_grid":
        step = 80
        for x in range(0, w, step):
            draw.line([(x, 0), (x, h)], fill=pat_col, width=1)
        for y in range(0, h, step):
            draw.line([(0, y), (w, y)], fill=pat_col, width=1)
    elif pat == "dot_matrix":
        step = 40
        for y in range(0, h, step):
            for x in range(0, w, step):
                draw.point((x, y), fill=(palette.neon_accent[0], palette.neon_accent[1], palette.neon_accent[2], p_alpha * 2))

    # 3. Kompozisyon Düzeni (Archetype Logic)
    margin = 50
    if layout.archetype == "split_asymmetric":
        # Sol asimetrik teknolojik panel
        split_x = int(w * 0.46)
        poly = [(0, 0), (split_x, 0), (split_x - 140, h), (0, h)]
        draw.polygon(poly, fill=(palette.bg_start[0], palette.bg_start[1], palette.bg_start[2], 220))
        draw.line([(split_x, 0), (split_x - 140, h)], fill=palette.neon_primary, width=4)
        draw.line([(split_x - 10, 0), (split_x - 150, h)], fill=palette.neon_accent, width=1)

        # Tipografi Konumu: Sol Hizalı
        ch_x = 120
        ch_y = h // 2 - 100
        sub_x = 125
        sub_y = ch_y + 115
        align_center = False
    elif layout.archetype == "cyber_hud":
        # Siberpunk HUD Çerçevesi
        draw.rectangle([(margin, margin), (w - margin, h - margin)], outline=(palette.neon_primary[0], palette.neon_primary[1], palette.neon_primary[2], 80), width=2)
        # Köşe aksanları
        k = 70
        for px, py in [(margin, margin), (w - margin, margin), (margin, h - margin), (w - margin, h - margin)]:
            dx = 1 if px == margin else -1
            dy = 1 if py == margin else -1
            draw.line([(px, py), (px + dx * k, py)], fill=palette.neon_accent, width=5)
            draw.line([(px, py), (px, py + dy * k)], fill=palette.neon_accent, width=5)
            draw.rectangle([(px + dx * 10 - 3, py + dy * 10 - 3), (px + dx * 10 + 3, py + dy * 10 + 3)], fill=palette.neon_secondary)

        ch_x = w // 2
        ch_y = 370
        sub_x = w // 2
        sub_y = 490
        align_center = True
    elif layout.archetype == "slant_esports":
        # Agresif espor çizgileri
        for i in range(3):
            sx = 250 + i * 25
            draw.line([(sx, 0), (sx + 200, h)], fill=(palette.neon_primary[0], palette.neon_primary[1], palette.neon_primary[2], 40 + i * 30), width=6)
        ch_x = w // 2
        ch_y = 360
        sub_x = w // 2
        sub_y = 480
        align_center = True
    elif layout.archetype == "minimalist_floating":
        # Ultra temiz ince neon çizgi
        draw.line([(w // 2 - 300, h // 2 + 35), (w // 2 + 300, h // 2 + 35)], fill=palette.neon_primary, width=2)
        ch_x = w // 2
        ch_y = h // 2 - 80
        sub_x = w // 2
        sub_y = h // 2 + 65
        align_center = True
    else: # centered_hero
        # Ortalanmış kahraman daire
        cx, cy = w // 2, h // 2 - 20
        draw.ellipse([(cx - 320, cy - 320), (cx + 320, cy + 320)], outline=(palette.neon_primary[0], palette.neon_primary[1], palette.neon_primary[2], 70), width=2)
        draw.ellipse([(cx - 340, cy - 340), (cx + 340, cy + 340)], outline=(palette.neon_accent[0], palette.neon_accent[1], palette.neon_accent[2], 30), width=1)
        ch_x = w // 2
        ch_y = 370
        sub_x = w // 2
        sub_y = 485
        align_center = True

    # 4. Tipografi Render
    font_huge = get_system_font(size=76, bold=True)
    font_title = get_system_font(size=34, bold=True)
    font_sub = get_system_font(size=22, bold=False)

    if mode == "starting":
        sub_text = custom_title or "YAYIN BİRAZDAN BAŞLIYOR..."
        tagline = "Canlı Yayın & Yüksek Performans • Hazırlanın!"
    elif mode == "brb":
        sub_text = custom_title or "KISA BİR MOLA • HEMEN DÖNÜYORUM"
        tagline = "Kahve/İçecek Molası • Yayından Ayrılmayın!"
    else:
        sub_text = custom_title or "YAYIN SONA ERDİ • TEŞEKKÜRLER!"
        tagline = "Takip Etmeyi ve Bildirimleri Açmayı Unutmayın!"

    channel_text = channel_name.upper()

    if align_center:
        ch_box = draw.textbbox((0, 0), channel_text, font=font_huge)
        sub_box = draw.textbbox((0, 0), sub_text, font=font_title)
        tag_box = draw.textbbox((0, 0), tagline, font=font_sub)

        # Gölge + Ana Metin
        draw.text(((w - (ch_box[2] - ch_box[0])) // 2 + 3, ch_y + 3), channel_text, font=font_huge, fill=(0, 0, 0, 200))
        draw.text(((w - (ch_box[2] - ch_box[0])) // 2, ch_y), channel_text, font=font_huge, fill=palette.text_main)

        # Alt Başlık
        draw.text(((w - (sub_box[2] - sub_box[0])) // 2, sub_y), sub_text, font=font_title, fill=palette.neon_secondary)
        draw.text(((w - (tag_box[2] - tag_box[0])) // 2, sub_y + 60), tagline, font=font_sub, fill=palette.text_sub)
    else:
        # Sol Hizalama (Split Modu)
        draw.text((ch_x + 3, ch_y + 3), channel_text, font=font_huge, fill=(0, 0, 0, 200))
        draw.text((ch_x, ch_y), channel_text, font=font_huge, fill=palette.text_main)
        draw.text((sub_x, sub_y), sub_text, font=font_title, fill=palette.neon_secondary)
        draw.text((sub_x, sub_y + 55), tagline, font=font_sub, fill=palette.text_sub)

    # 5. Durum Pill Rozeti
    pill_w, pill_h = 440, 46
    pill_x = (w - pill_w) // 2 if align_center else 125
    pill_y = h - 230 if align_center else h - 250
    draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)], radius=12, fill=(10, 8, 16, 220), outline=palette.border_color, width=2)
    # Canlı Kırmızı Işık
    draw.ellipse([(pill_x + 18, pill_y + 15), (pill_x + 32, pill_y + 29)], fill=(239, 68, 68, 255))
    draw.text((pill_x + 44, pill_y + 12), f"CANLI BEKLEME • [{palette.name}]", font=get_system_font(15, bold=True), fill=palette.text_main)

    # 6. Alt Sosyal Medya Şeridi
    bot_y = h - 90
    draw.line([(100, bot_y), (w - 100, bot_y)], fill=(palette.border_color[0], palette.border_color[1], palette.border_color[2], 80), width=1)
    footer_text = f"TWITCH / KICK: @{channel_name}   •   YOUTUBE: @{channel_name}   •   DİSCORD TOPLULUĞU"
    fb_box = draw.textbbox((0, 0), footer_text, font=get_system_font(16, False))
    draw.text(((w - (fb_box[2] - fb_box[0])) // 2, bot_y + 20), footer_text, font=get_system_font(16, False), fill=palette.text_sub)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_{mode}.png")
    img.save(out_file, "PNG")
    return out_file

# ------------------------------------------------------------------------------
# 5. DİNAMİK ŞEFFAF WEBCAM ÇERÇEVESİ (PROSEDÜREL 1920x1080 PNG)
# ------------------------------------------------------------------------------
def generate_webcam_overlay(channel_name="Ripleytia", palette=None, layout=None):
    if palette is None:
        palette = _harmonizer_instance.resolve_palette()
    if layout is None:
        layout = _repetition_instance.derive_unique_layout()

    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cam_x, cam_y = 1380, 60
    cam_w, cam_h = 480, 270

    if layout.border_style == "tech_brackets":
        # Siberpunk Köşeli Braketler
        draw.rectangle([(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)], outline=(palette.neon_primary[0], palette.neon_primary[1], palette.neon_primary[2], 70), width=1)
        k = 36
        for px, py in [(cam_x, cam_y), (cam_x + cam_w, cam_y), (cam_x, cam_y + cam_h), (cam_x + cam_w, cam_y + cam_h)]:
            dx = 1 if px == cam_x else -1
            dy = 1 if py == cam_y else -1
            draw.line([(px, py), (px + dx * k, py)], fill=palette.neon_accent, width=4)
            draw.line([(px, py), (px, py + dy * k)], fill=palette.neon_accent, width=4)
    elif layout.border_style == "double_chamfer":
        # 45 Derece Pah Kırılmış Köşeler
        c = 18
        points = [
            (cam_x + c, cam_y), (cam_x + cam_w - c, cam_y),
            (cam_x + cam_w, cam_y + c), (cam_x + cam_w, cam_y + cam_h - c),
            (cam_x + cam_w - c, cam_y + cam_h), (cam_x + c, cam_y + cam_h),
            (cam_x, cam_y + cam_h - c), (cam_x, cam_y + c)
        ]
        draw.polygon(points, outline=palette.neon_primary, width=3)
    elif layout.border_style == "minimal_rounded":
        # Yuvarlatılmış Zarif Çerçeve
        draw.rounded_rectangle([(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)], radius=14, outline=palette.neon_primary, width=3)
    else: # neon_glow
        # Çift Katmanlı Parlayan Neon
        draw.rectangle([(cam_x - 3, cam_y - 3), (cam_x + cam_w + 3, cam_y + cam_h + 3)], outline=(palette.neon_secondary[0], palette.neon_secondary[1], palette.neon_secondary[2], 90), width=6)
        draw.rectangle([(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)], outline=palette.neon_primary, width=3)

    # İsim Plakası
    badge_h = 32
    draw.rectangle([(cam_x, cam_y + cam_h), (cam_x + cam_w, cam_y + cam_h + badge_h)], fill=(12, 10, 20, 230), outline=palette.neon_primary, width=2)
    draw.text((cam_x + 16, cam_y + cam_h + 6), f"🔴 {channel_name.upper()}", font=get_system_font(15, bold=True), fill=palette.text_main)
    draw.text((cam_x + cam_w - 90, cam_y + cam_h + 7), "LIVE HD", font=get_system_font(13, bold=True), fill=palette.neon_accent)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_webcam_overlay.png")
    img.save(out_file, "PNG")
    return out_file

# ------------------------------------------------------------------------------
# 6. DİNAMİK ŞEFFAF CHAT OVERLAY ÇERÇEVESİ (PROSEDÜREL 1920x1080 PNG)
# ------------------------------------------------------------------------------
def generate_chat_overlay(channel_name="Ripleytia", palette=None, layout=None):
    if palette is None:
        palette = _harmonizer_instance.resolve_palette()
    if layout is None:
        layout = _repetition_instance.derive_unique_layout()

    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 60, 350
    cw, ch = 420, 660

    # Cam Efektli Yarı Saydam Gövde
    draw.rounded_rectangle([(cx, cy), (cx + cw, cy + ch)], radius=14, fill=(10, 8, 18, 140), outline=palette.neon_primary, width=2)
    # Başlık Şeridi
    draw.rounded_rectangle([(cx, cy), (cx + cw, cy + 42)], radius=12, fill=(palette.bg_start[0], palette.bg_start[1], palette.bg_start[2], 230), outline=palette.border_color, width=2)
    draw.text((cx + 16, cy + 10), f"💬 CANLI SOHBET • @{channel_name}", font=get_system_font(15, bold=True), fill=palette.text_main)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_chat_overlay.png")
    img.save(out_file, "PNG")
    return out_file

# ------------------------------------------------------------------------------
# 7. DİNAMİK ETKİNLİK & HEDEF ŞERİDİ (EVENT TICKER)
# ------------------------------------------------------------------------------
def generate_event_ticker(channel_name="Ripleytia", palette=None, layout=None):
    if palette is None:
        palette = _harmonizer_instance.resolve_palette()
    if layout is None:
        layout = _repetition_instance.derive_unique_layout()

    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    tx, ty = 200, 20
    tw, th = 1520, 48

    draw.rounded_rectangle([(tx, ty), (tx + tw, ty + th)], radius=10, fill=(12, 10, 22, 215), outline=palette.border_color, width=2)

    font_t = get_system_font(14, bold=True)
    font_v = get_system_font(14, bold=False)

    draw.text((tx + 30, ty + 15), "⭐ SON TAKİPÇİ:", font=font_t, fill=palette.neon_secondary)
    draw.text((tx + 180, ty + 15), "Topluluk Üyesi", font=font_v, fill=palette.text_main)

    draw.text((tx + 540, ty + 15), "💎 SON ABONE:", font=font_t, fill=palette.neon_accent)
    draw.text((tx + 680, ty + 15), "VIP Destekçi", font=font_v, fill=palette.text_main)

    draw.text((tx + 1040, ty + 15), "🎯 TAKİPÇİ HEDEFİ: 85 / 100", font=font_t, fill=palette.text_main)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_ticker_overlay.png")
    img.save(out_file, "PNG")
    return out_file

# ------------------------------------------------------------------------------
# 8. TAM AKILLI OBS SAHNE KOLEKSİYONU ENTEGRATÖRÜ (v1.2.0)
# ------------------------------------------------------------------------------
def build_ai_scene_collection(channel_name="Ripleytia", theme_name="Cyber Gothic Purple", collection_name=None, custom_color_query="", api_key=""):
    """
    1. AI Color Harmonizer ile renk paletini çözer.
    2. AntiRepetitionEngine ile geçmişte kullanılmamış eşsiz bir Layout türetir.
    3. Tüm grafikleri prosedürel olarak render edip kaydeder.
    4. 5 sahneli eksiksiz OBS Studio koleksiyonu JSON'ını oluşturup APPDATA'ya bağlar.
    """
    appdata = os.environ.get("APPDATA", "")
    scenes_dir = os.path.join(appdata, "obs-studio", "basic", "scenes")
    os.makedirs(scenes_dir, exist_ok=True)

    c_name = collection_name or f"Ripleytia AI - {channel_name}"
    filepath = os.path.join(scenes_dir, f"{c_name}.json")

    # 1. Renk Çözümleme
    harmonizer = AIColorHarmonizer(api_key=api_key)
    palette = harmonizer.resolve_palette(color_text=custom_color_query, preset_name=theme_name)

    # 2. Eşsiz Şablon Türetme (Anti-Repetition)
    layout = _repetition_instance.derive_unique_layout(preset_name=theme_name)

    # 3. Grafikleri Prosedürel Üret
    start_banner = generate_channel_banner(channel_name, palette=palette, layout=layout, mode="starting")
    brb_banner = generate_channel_banner(channel_name, palette=palette, layout=layout, mode="brb")
    end_banner = generate_channel_banner(channel_name, palette=palette, layout=layout, mode="ending")
    webcam_overlay = generate_webcam_overlay(channel_name, palette=palette, layout=layout)
    chat_overlay = generate_chat_overlay(channel_name, palette=palette, layout=layout)
    ticker_overlay = generate_event_ticker(channel_name, palette=palette, layout=layout)

    # UUID'ler
    game_scene_uuid = str(uuid.uuid4())
    chat_scene_uuid = str(uuid.uuid4())
    start_scene_uuid = str(uuid.uuid4())
    brb_scene_uuid = str(uuid.uuid4())
    end_scene_uuid = str(uuid.uuid4())

    game_cap_uuid = str(uuid.uuid4())
    cam_overlay_uuid = str(uuid.uuid4())
    chat_overlay_uuid = str(uuid.uuid4())
    ticker_uuid = str(uuid.uuid4())
    start_img_uuid = str(uuid.uuid4())
    brb_img_uuid = str(uuid.uuid4())
    end_img_uuid = str(uuid.uuid4())

    desktop_audio_uuid = str(uuid.uuid4())
    mic_audio_uuid = str(uuid.uuid4())

    collection = {
        "name": c_name,
        "DesktopAudioDevice1": {
            "name": "Masaüstü Sesi",
            "uuid": desktop_audio_uuid,
            "id": "wasapi_output_capture",
            "versioned_id": "wasapi_output_capture",
            "settings": {"device_id": "default"},
            "volume": 1.0,
            "muted": False,
            "enabled": True
        },
        "AuxAudioDevice1": {
            "name": "Yayıncı Mikrofonu",
            "uuid": mic_audio_uuid,
            "id": "wasapi_input_capture",
            "versioned_id": "wasapi_input_capture",
            "settings": {"device_id": "default"},
            "volume": 1.0,
            "muted": False,
            "enabled": True,
            "filters": [
                {
                    "name": "🤖 AI RNNoise Gürültü Engelleme",
                    "id": "noise_suppress_filter",
                    "versioned_id": "noise_suppress_filter",
                    "settings": {
                        "method": 1
                    },
                    "enabled": True
                }
            ]
        },
        "current_scene": "🎮 1 - Oyun & FiveM",
        "current_program_scene": "🎮 1 - Oyun & FiveM",
        "scene_order": [
            {"name": "🎮 1 - Oyun & FiveM"},
            {"name": "💬 2 - Sohbet / Chatting"},
            {"name": "⏳ 3 - Yayın Başlıyor"},
            {"name": "☕ 4 - Kısa Mola (BRB)"},
            {"name": "👋 5 - Yayın Bitti"}
        ],
        "sources": [
            {
                "name": "🎮 1 - Oyun & FiveM",
                "uuid": game_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {
                    "id_counter": 3,
                    "items": [
                        {"name": "Oyun Yakalama (FiveM / Game)", "source_uuid": game_cap_uuid, "visible": True, "locked": True},
                        {"name": "Webcam Çerçevesi (AI)", "source_uuid": cam_overlay_uuid, "visible": True, "locked": False},
                        {"name": "Etkinlik & Hedef Şeridi (AI)", "source_uuid": ticker_uuid, "visible": True, "locked": False}
                    ]
                }
            },
            {
                "name": "💬 2 - Sohbet / Chatting",
                "uuid": chat_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {
                    "id_counter": 3,
                    "items": [
                        {"name": "Sohbet Kutusu Çerçevesi (AI)", "source_uuid": chat_overlay_uuid, "visible": True, "locked": False},
                        {"name": "Webcam Çerçevesi (AI)", "source_uuid": cam_overlay_uuid, "visible": True, "locked": False},
                        {"name": "Etkinlik & Hedef Şeridi (AI)", "source_uuid": ticker_uuid, "visible": True, "locked": False}
                    ]
                }
            },
            {
                "name": "⏳ 3 - Yayın Başlıyor",
                "uuid": start_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {
                    "id_counter": 1,
                    "items": [
                        {"name": f"Açılış Ekranı ({channel_name})", "source_uuid": start_img_uuid, "visible": True, "locked": True}
                    ]
                }
            },
            {
                "name": "☕ 4 - Kısa Mola (BRB)",
                "uuid": brb_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {
                    "id_counter": 1,
                    "items": [
                        {"name": f"Mola Ekranı ({channel_name})", "source_uuid": brb_img_uuid, "visible": True, "locked": True}
                    ]
                }
            },
            {
                "name": "👋 5 - Yayın Bitti",
                "uuid": end_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {
                    "id_counter": 1,
                    "items": [
                        {"name": f"Kapanış Ekranı ({channel_name})", "source_uuid": end_img_uuid, "visible": True, "locked": True}
                    ]
                }
            },
            {
                "name": "Oyun Yakalama (FiveM / Game)",
                "uuid": game_cap_uuid,
                "id": "game_capture",
                "versioned_id": "game_capture",
                "settings": {
                    "capture_mode": "any_fullscreen",
                    "capture_overlays": False,
                    "anti_cheat_hook": True
                }
            },
            {
                "name": "Webcam Çerçevesi (AI)",
                "uuid": cam_overlay_uuid,
                "id": "image_source",
                "versioned_id": "image_source",
                "settings": {"file": webcam_overlay}
            },
            {
                "name": "Sohbet Kutusu Çerçevesi (AI)",
                "uuid": chat_overlay_uuid,
                "id": "image_source",
                "versioned_id": "image_source",
                "settings": {"file": chat_overlay}
            },
            {
                "name": "Etkinlik & Hedef Şeridi (AI)",
                "uuid": ticker_uuid,
                "id": "image_source",
                "versioned_id": "image_source",
                "settings": {"file": ticker_overlay}
            },
            {
                "name": f"Açılış Ekranı ({channel_name})",
                "uuid": start_img_uuid,
                "id": "image_source",
                "versioned_id": "image_source",
                "settings": {"file": start_banner}
            },
            {
                "name": f"Mola Ekranı ({channel_name})",
                "uuid": brb_img_uuid,
                "id": "image_source",
                "versioned_id": "image_source",
                "settings": {"file": brb_banner}
            },
            {
                "name": f"Kapanış Ekranı ({channel_name})",
                "uuid": end_img_uuid,
                "id": "image_source",
                "versioned_id": "image_source",
                "settings": {"file": end_banner}
            }
        ]
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=4, ensure_ascii=False)

    return {
        "success": True,
        "collection_name": c_name,
        "filepath": filepath,
        "layout": layout,
        "palette": palette,
        "assets": {
            "start_banner": start_banner,
            "brb_banner": brb_banner,
            "end_banner": end_banner,
            "webcam_overlay": webcam_overlay,
            "chat_overlay": chat_overlay,
            "ticker_overlay": ticker_overlay
        }
    }

def generate_ai_stream_strategy(channel_name="Ripleytia", game_type="FiveM / GTA V", style="Eğlenceli & Dinamik"):
    strategies = {
        "FiveM / GTA V (Roleplay)": {
            "titles": [
                f"🚨 [{channel_name}] LOS SANTOS SOKAKLARI HAREKETLİ! | Hard RP | 0 Dropped Frames",
                f"🔫 GİZLİ OPERASYON & SOYGUN PLANI | {channel_name} ile FiveM Gecesi",
                f"🚔 DEPARTMAN ACİL DURUM KODU! | Roleplay Zirvesi | {channel_name}"
            ],
            "poll_ideas": [
                "Polisten kaçarken hangi aracı tercih edelim? (Sultan RS / Dominator)",
                "Bu gece yasa dışı işlere bulaşalım mı? (Evet / Hayır)",
                "Hangi bölgede devriye atalım? (Sandy Shores / Şehir Merkezi)"
            ],
            "stream_tips": "FiveM için OBS sahnenizde ReShade koruması devrede. Oyun içi telsiz ve Discord ses düzeylerini ayrıştırmak için Application Audio Capture kullanın."
        },
        "Valorant / CS2 (Rekabetçi FPS)": {
            "titles": [
                f"🎯 RADYANT / GLOBAL YOLCULUĞU! | [{channel_name}] | 144Hz+ 0 Input Lag",
                f"🔥 KAFADAN VURUŞ MAKİNESİ! | Dereceli Maçlar | {channel_name} Canlıda",
                f"⚡ CLUTCH OR LOSE! | Espor Modu Aktif | {channel_name}"
            ],
            "poll_ideas": [
                "Sonraki elde hangi silahı alayım? (Vandal / Phantom)",
                "Bölgeye agresif mi girelim pasif mi bekleyelim?",
                "Bu maç kaç kill alırız? (20+ / 15-20 / 15 altı)"
            ],
            "stream_tips": "FPS oyunlarında düşük gecikme için NVENC P6 Tuning Ultra-Low Latency profilini ve RNNoise mikrofon filtresini aktif tuttuk."
        }
    }
    return strategies.get(game_type, {
        "titles": [f"🚀 {channel_name} CANLI YAYINDA! | Keyifli Sohbet & Oyunlar"],
        "poll_ideas": ["Bir sonraki yayında hangi oyunu oynayalım?"],
        "stream_tips": "OBS ayarlarınız donanımınıza göre optimize edildi."
    })
