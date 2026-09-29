# -*- coding: utf-8 -*-
"""
engine/ai_designer.py
================================================================================
OBS AI Studio - Profesyonel Yayıncı Katmanlı Grafik & Anti-Repetition Motoru
Sürüm: 1.4.0
Shroud, Ninja, VCT ve Espor Turnuva Seviyesinde Çok Katmanlı Grafik Üreticisi
================================================================================
"""

import os
import json
import uuid
import math
import random
import time
import hashlib
import colorsys
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Tuple, Any
from PIL import Image, ImageDraw, ImageFont


# ==============================================================================
# 1. PROFESYONEL YAYINCI TASARIM TRENDLERİ (ART DIRECTION TRENDS)
# ==============================================================================

class ArtDirectionTrend(str, Enum):
    ESPORTS_AGGRESSIVE = "🔥 ESPOR / AGRESİF (Valorant Champions / VCT)"
    BOLD_BRUTALISM = "⬛ BOLD BRUTALISM (Endüstriyel & Devasa Tipografi)"
    TECH_FUTURE_HUD = "⚡ TECH / MINIMALIST FUTURE (Cyberpunk HUD)"
    PREMIUM_STREAM = "💎 PREMIUM STREAM (Modern Lüks & Glassmorphism)"


class SkeletonLayout(str, Enum):
    CENTER_HERO_CARD = "center_hero_card"
    LEFT_MONOLITH_DOCK = "left_monolith_dock"
    ASYMMETRIC_SPLIT_WEDGE = "asymmetric_split_wedge"
    CINEMATIC_BROADCAST_RIBBON = "cinematic_broadcast_ribbon"


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


def get_system_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Windows sistem fontlarını güvenle yükler."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fp = os.path.join(windir, "Fonts", name)
    if os.path.exists(fp):
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            pass
    # Alternatif font listesi
    for alt in ["arialbd.ttf", "impact.ttf", "segoeuib.ttf", "arial.ttf"]:
        alt_fp = os.path.join(windir, "Fonts", alt)
        if os.path.exists(alt_fp):
            try:
                return ImageFont.truetype(alt_fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ==============================================================================
# 2. RENK UYUMLAYICI (AI COLOR HARMONIZER)
# ==============================================================================

class AIColorHarmonizer:
    PRESET_PALETTES = {
        "Cyber Gothic Purple": ColorPalette(
            name="Cyber Gothic Purple",
            bg_start=(14, 10, 24, 255),
            bg_end=(32, 14, 52, 255),
            neon_primary=(168, 85, 247, 255),
            neon_secondary=(216, 180, 254, 255),
            neon_accent=(0, 245, 212, 255),
            text_main=(255, 255, 255, 255),
            text_sub=(200, 185, 220, 255),
            border_color=(168, 85, 247, 255)
        ),
        "Neon Cyberpunk (Mavi/Pembe)": ColorPalette(
            name="Neon Cyberpunk",
            bg_start=(8, 12, 22, 255),
            bg_end=(18, 28, 48, 255),
            neon_primary=(0, 245, 212, 255),
            neon_secondary=(255, 0, 128, 255),
            neon_accent=(255, 222, 89, 255),
            text_main=(245, 250, 255, 255),
            text_sub=(160, 210, 235, 255),
            border_color=(0, 245, 212, 255)
        ),
        "Blood Red (Kırmızı/Siyah)": ColorPalette(
            name="Blood Red",
            bg_start=(18, 8, 10, 255),
            bg_end=(45, 12, 16, 255),
            neon_primary=(239, 68, 68, 255),
            neon_secondary=(252, 165, 165, 255),
            neon_accent=(245, 158, 11, 255),
            text_main=(255, 255, 255, 255),
            text_sub=(220, 170, 170, 255),
            border_color=(239, 68, 68, 255)
        ),
        "Emerald Green (Yeşil/Siyah)": ColorPalette(
            name="Emerald Green",
            bg_start=(6, 16, 12, 255),
            bg_end=(14, 38, 26, 255),
            neon_primary=(16, 185, 129, 255),
            neon_secondary=(110, 231, 183, 255),
            neon_accent=(251, 191, 36, 255),
            text_main=(245, 255, 250, 255),
            text_sub=(165, 225, 200, 255),
            border_color=(16, 185, 129, 255)
        ),
        "Retro Synthwave": ColorPalette(
            name="Retro Synthwave",
            bg_start=(24, 8, 36, 255),
            bg_end=(48, 14, 56, 255),
            neon_primary=(255, 0, 128, 255),
            neon_secondary=(255, 175, 64, 255),
            neon_accent=(0, 220, 255, 255),
            text_main=(255, 255, 255, 255),
            text_sub=(230, 180, 220, 255),
            border_color=(255, 0, 128, 255)
        ),
        "Minimalist & Clean": ColorPalette(
            name="Minimalist & Clean",
            bg_start=(14, 14, 18, 255),
            bg_end=(24, 24, 32, 255),
            neon_primary=(240, 240, 245, 255),
            neon_secondary=(180, 180, 200, 255),
            neon_accent=(99, 102, 241, 255),
            text_main=(255, 255, 255, 255),
            text_sub=(170, 170, 190, 255),
            border_color=(120, 120, 145, 255)
        )
    }

    def resolve(self, trend: ArtDirectionTrend, preset_name: str = "", query: str = "") -> ColorPalette:
        if query:
            q = query.lower()
            if "mor" in q or "purple" in q:
                return self.PRESET_PALETTES["Cyber Gothic Purple"]
            elif "siber" in q or "cyber" in q or "mavi" in q:
                return self.PRESET_PALETTES["Neon Cyberpunk (Mavi/Pembe)"]
            elif "kırmızı" in q or "red" in q:
                return self.PRESET_PALETTES["Blood Red (Kırmızı/Siyah)"]
            elif "yeşil" in q or "green" in q:
                return self.PRESET_PALETTES["Emerald Green (Yeşil/Siyah)"]
            elif "retro" in q or "synth" in q or "pembe" in q:
                return self.PRESET_PALETTES["Retro Synthwave"]

        if preset_name in self.PRESET_PALETTES:
            return self.PRESET_PALETTES[preset_name]

        # Trende göre ideal renk paleti
        if trend == ArtDirectionTrend.ESPORTS_AGGRESSIVE:
            choices = [
                ColorPalette("Esports VCT Red", (16, 10, 14, 255), (32, 14, 20, 255), (255, 51, 85, 255), (255, 180, 190, 255), (255, 215, 0, 255), (255, 255, 255, 255), (210, 180, 190, 255), (255, 51, 85, 255)),
                ColorPalette("Esports Cyber Cyan", (8, 14, 24, 255), (14, 28, 48, 255), (0, 245, 212, 255), (255, 0, 128, 255), (255, 222, 89, 255), (255, 255, 255, 255), (170, 215, 235, 255), (0, 245, 212, 255)),
                ColorPalette("Esports Gold / Black", (14, 12, 10, 255), (32, 26, 16, 255), (255, 200, 0, 255), (255, 235, 150, 255), (0, 210, 255, 255), (255, 255, 255, 255), (220, 200, 160, 255), (255, 200, 0, 255)),
            ]
            return random.choice(choices)
        elif trend == ArtDirectionTrend.BOLD_BRUTALISM:
            choices = [
                ColorPalette("Brutalist Acid Yellow", (242, 238, 230, 255), (232, 226, 214, 255), (15, 15, 18, 255), (245, 220, 0, 255), (255, 45, 85, 255), (15, 15, 18, 255), (55, 55, 65, 255), (15, 15, 18, 255)),
                ColorPalette("Brutalist Stark Black", (12, 12, 14, 255), (20, 20, 24, 255), (245, 220, 0, 255), (255, 255, 255, 255), (0, 240, 255, 255), (255, 255, 255, 255), (190, 190, 200, 255), (245, 220, 0, 255)),
            ]
            return random.choice(choices)
        elif trend == ArtDirectionTrend.TECH_FUTURE_HUD:
            choices = [
                ColorPalette("Holo Cyan Sci-Fi", (6, 10, 20, 255), (12, 20, 38, 255), (0, 235, 255, 255), (140, 90, 255, 255), (0, 255, 170, 255), (245, 250, 255, 255), (150, 200, 230, 255), (0, 235, 255, 255)),
                ColorPalette("Matrix Cyber Green", (5, 16, 10, 255), (10, 32, 18, 255), (0, 255, 136, 255), (150, 255, 200, 255), (0, 215, 255, 255), (245, 255, 250, 255), (160, 225, 195, 255), (0, 255, 136, 255)),
            ]
            return random.choice(choices)
        else: # PREMIUM_STREAM
            choices = [
                ColorPalette("Luxury Royal Purple", (12, 8, 22, 255), (28, 14, 46, 255), (168, 85, 247, 255), (236, 72, 153, 255), (255, 215, 0, 255), (255, 255, 255, 255), (210, 195, 230, 255), (168, 85, 247, 255)),
                ColorPalette("Deep Obsidian Frost", (10, 12, 18, 255), (18, 24, 36, 255), (129, 140, 248, 255), (192, 132, 252, 255), (56, 189, 248, 255), (255, 255, 255, 255), (190, 205, 235, 255), (129, 140, 248, 255)),
            ]
            return random.choice(choices)


THEME_PALETTES = AIColorHarmonizer.PRESET_PALETTES


# ==============================================================================
# 3. YAYIN TASARIM PLANI & KATI GEÇMİŞ KONTROLÜ (HARD ANTI-REPETITION)
# ==============================================================================

@dataclass
class MasterDesignPlan:
    design_id: str
    trend: ArtDirectionTrend
    skeleton: SkeletonLayout
    palette: ColorPalette
    seed: int


class MasterDesignMutator:
    def __init__(self, history_len: int = 15):
        self.history: List[Tuple[ArtDirectionTrend, SkeletonLayout]] = []
        self.history_len = history_len
        self.harmonizer = AIColorHarmonizer()

    def generate_plan(self, requested_trend: str = "", query: str = "") -> MasterDesignPlan:
        # Trend Eşleştirme
        trend_map = {
            "ESPOR": ArtDirectionTrend.ESPORTS_AGGRESSIVE,
            "BRUTALISM": ArtDirectionTrend.BOLD_BRUTALISM,
            "TECH": ArtDirectionTrend.TECH_FUTURE_HUD,
            "PREMIUM": ArtDirectionTrend.PREMIUM_STREAM,
        }

        chosen_trend = None
        for k, v in trend_map.items():
            if k in requested_trend.upper():
                chosen_trend = v
                break

        # Döngü ile asla tekrar etmeyen kombinasyon türetme
        for _ in range(35):
            trend = chosen_trend if chosen_trend else random.choice(list(ArtDirectionTrend))
            skeleton = random.choice(list(SkeletonLayout))

            # Son tasarımla uyuşuyorsa yeni kombinasyon zorla
            if self.history and (trend, skeleton) == self.history[-1]:
                continue
            if self.history.count((trend, skeleton)) >= 2:
                continue

            # Geçerli plan bulundu
            seed = int(time.time() * 1000) ^ random.randint(100, 99999)
            palette = self.harmonizer.resolve(trend, preset_name=requested_trend, query=query)
            d_id = f"PRO-{hashlib.md5(f'{trend.value}_{skeleton.value}_{seed}'.encode()).hexdigest()[:8].upper()}"

            self.history.append((trend, skeleton))
            if len(self.history) > self.history_len:
                self.history.pop(0)

            return MasterDesignPlan(design_id=d_id, trend=trend, skeleton=skeleton, palette=palette, seed=seed)

        # Fallback
        trend = random.choice(list(ArtDirectionTrend))
        skeleton = random.choice(list(SkeletonLayout))
        palette = self.harmonizer.resolve(trend)
        d_id = f"PRO-{random.randint(1000, 9999)}"
        return MasterDesignPlan(design_id=d_id, trend=trend, skeleton=skeleton, palette=palette, seed=123)


_mutator = MasterDesignMutator()


def get_appdata_obs_assets_dir() -> str:
    appdata = os.environ.get("APPDATA", "")
    obs_assets = os.path.join(appdata, "obs-studio", "ripleytia_assets")
    os.makedirs(obs_assets, exist_ok=True)
    return obs_assets


# ==============================================================================
# 4. ÇOK KATMANLI BANNER ÜRETİCİSİ (1920x1080 STARTING / BRB / ENDING)
# ==============================================================================

def generate_channel_banner(channel_name: str = "Ripleytia", 
                            plan: Optional[MasterDesignPlan] = None, 
                            mode: str = "starting", 
                            custom_title: Optional[str] = None) -> str:
    if plan is None:
        plan = _mutator.generate_plan()

    w, h = 1920, 1080
    pal = plan.palette
    trend = plan.trend
    skel = plan.skeleton

    img = Image.new("RGBA", (w, h), pal.bg_start)
    draw = ImageDraw.Draw(img)

    # 1. ZEMİN VE ARKA PLAN KATMANI (BACKGROUND MESH & SHAPES)
    is_brutalist = (trend == ArtDirectionTrend.BOLD_BRUTALISM)
    
    # Dikey / Radyal Gradyan
    for y in range(h):
        blend = y / h
        r = int(pal.bg_start[0] * (1 - blend) + pal.bg_end[0] * blend)
        g = int(pal.bg_start[1] * (1 - blend) + pal.bg_end[1] * blend)
        b = int(pal.bg_start[2] * (1 - blend) + pal.bg_end[2] * blend)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Arka Plan Şekilleri ve Dinamik Çizgiler
    if trend == ArtDirectionTrend.ESPORTS_AGGRESSIVE:
        # 45 Derecelik Espor Şeritleri ve Agresif Polygonlar
        for i in range(-2, 10):
            sx = i * 260
            poly = [(sx, 0), (sx + 120, 0), (sx + 120 + 400, h), (sx + 400, h)]
            fill_c = (pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 28)
            draw.polygon(poly, fill=fill_c)
        # Ekranın arkasından taşan devasa silik kanal harfi
        font_watermark = get_system_font("impact.ttf", 450)
        draw.text((w - 550, -60), channel_name[0].upper(), font=font_watermark, fill=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 22))

    elif trend == ArtDirectionTrend.BOLD_BRUTALISM:
        # Dev arka plan brutalist watermark yazısı
        font_watermark = get_system_font("impact.ttf", 260)
        wm_text = channel_name.upper()
        draw.text((60, 40), wm_text, font=font_watermark, fill=(pal.border_color[0], pal.border_color[1], pal.border_color[2], 30))
        # Kalın endüstriyel çizgiler
        draw.line([(0, 180), (w, 180)], fill=pal.border_color, width=6)
        draw.line([(0, h - 140), (w, h - 140)], fill=pal.border_color, width=6)
        # Çapraz ikaz çizgisi şeridi
        for x in range(0, w, 40):
            draw.line([(x, h - 140), (x + 25, h)], fill=(pal.neon_secondary[0], pal.neon_secondary[1], pal.neon_secondary[2], 120), width=4)

    elif trend == ArtDirectionTrend.TECH_FUTURE_HUD:
        # Bal peteği veya siber ızgara
        step = 60
        for x in range(0, w, step):
            draw.line([(x, 0), (x, h)], fill=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 24), width=1)
        for y in range(0, h, step):
            draw.line([(0, y), (w, y)], fill=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 24), width=1)
        # 4 Köşede Yüksek Teknoloji Braketleri
        m = 45
        for px, py in [(m, m), (w - m, m), (m, h - m), (w - m, h - m)]:
            dx = 1 if px == m else -1
            dy = 1 if py == m else -1
            draw.line([(px, py), (px + dx * 80, py)], fill=pal.neon_primary, width=5)
            draw.line([(px, py), (px, py + dy * 80)], fill=pal.neon_primary, width=5)
            draw.rectangle([(px + dx * 12 - 4, py + dy * 12 - 4), (px + dx * 12 + 4, py + dy * 12 + 4)], fill=pal.neon_accent)

    else: # PREMIUM_STREAM
        # Yumuşak Difüze Ambient Neon Küreler (Glow Orbs)
        cx1, cy1 = int(w * 0.25), int(h * 0.35)
        cx2, cy2 = int(w * 0.75), int(h * 0.65)
        draw.ellipse([(cx1 - 280, cy1 - 280), (cx1 + 280, cy1 + 280)], fill=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 35))
        draw.ellipse([(cx2 - 320, cy2 - 320), (cx2 + 320, cy2 + 320)], fill=(pal.neon_secondary[0], pal.neon_secondary[1], pal.neon_secondary[2], 30))
        # İnce lüks altın oran halkaları
        draw.ellipse([(w // 2 - 380, h // 2 - 380), (w // 2 + 380, h // 2 + 380)], outline=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 55), width=2)

    # 2. HERO PANEL KATMANI (METNİN ARKASINDAKİ ZENGİN ŞEKİL KUTUSU)
    # Metinlerin boyutuna ve iskelet düzenine göre dinamik panel hesaplama
    if skel == SkeletonLayout.LEFT_MONOLITH_DOCK:
        pw, ph = 920, 520
        cx = 120
        cy = (h - ph) // 2
    elif skel == SkeletonLayout.ASYMMETRIC_SPLIT_WEDGE:
        pw, ph = 1140, 480
        cx = (w - pw) // 2 + 40
        cy = (h - ph) // 2
    elif skel == SkeletonLayout.CINEMATIC_BROADCAST_RIBBON:
        pw, ph = 1760, 420
        cx = (w - pw) // 2
        cy = (h - ph) // 2
    else: # CENTER_HERO_CARD
        pw, ph = 1180, 480
        cx = (w - pw) // 2
        cy = (h - ph) // 2

    # Paneli Trende Göre Çiz
    if trend == ArtDirectionTrend.ESPORTS_AGGRESSIVE:
        slant = 35
        # Dış Neon Gölge / Şerit Katmanı
        d_poly = [(cx + slant - 10, cy - 8), (cx + pw + 10, cy - 8), (cx + pw - slant + 10, cy + ph + 8), (cx - 10, cy + ph + 8)]
        draw.polygon(d_poly, fill=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 45))
        
        # Ana Karbon/Metal Paralelkenar Panel
        m_poly = [(cx + slant, cy), (cx + pw, cy), (cx + pw - slant, cy + ph), (cx, cy + ph)]
        draw.polygon(m_poly, fill=(16, 12, 24, 240), outline=pal.neon_primary, width=4)
        
        # Sol Taraf Hazard İkaz Şeritleri (///)
        for i in range(6):
            hx = cx + 24 + i * 16
            draw.line([(hx + slant, cy + 18), (hx, cy + ph - 18)], fill=pal.neon_secondary, width=5)

        # Sağ Üst Köşe Espor Turnuva Rozeti
        badge_poly = [(cx + pw - 280, cy), (cx + pw, cy), (cx + pw - 25, cy + 42), (cx + pw - 305, cy + 42)]
        draw.polygon(badge_poly, fill=pal.neon_primary)
        draw.text((cx + pw - 275, cy + 10), "VCT CHAMPIONS // LIVE", font=get_system_font("impact.ttf", 18), fill=(10, 8, 16, 255))

        # Sağ Alt Ses Dalgası / Equalizer Çubukları
        for i in range(24):
            bx = cx + pw - 280 + i * 9
            bh = 12 + int(48 * abs(math.sin(i * 0.45 + 1.2)))
            draw.rectangle([(bx, cy + ph - 25 - bh), (bx + 5, cy + ph - 25)], fill=pal.neon_accent)

    elif trend == ArtDirectionTrend.BOLD_BRUTALISM:
        # Sert 14px Ofset Blok Gölge (Bulanıklık Yok)
        draw.rectangle([(cx + 14, cy + 14), (cx + pw + 14, cy + ph + 14)], fill=(10, 10, 12, 255))
        # Kalın 6px Çerçeveli Ham Gövde
        bg_fill = (245, 240, 232, 255) if pal.bg_start[0] > 100 else (18, 18, 22, 245)
        draw.rectangle([(cx, cy), (cx + pw, cy + ph)], fill=bg_fill, outline=pal.border_color, width=6)
        
        # Üst Siyah Başlık Bandı
        draw.rectangle([(cx, cy), (cx + pw, cy + 48)], fill=pal.border_color)
        draw.text((cx + 24, cy + 12), f"[ ACTIVE TRANSMISSION // {plan.design_id} ]", font=get_system_font("consola.ttf", 18), fill=pal.neon_primary)
        
        # Barkod Deseni (Sağ Köşede)
        b_x = cx + pw - 180
        for i in range(20):
            bw = 2 if i % 3 == 0 else 4
            draw.line([(b_x + i * 8, cy + ph - 60), (b_x + i * 8, cy + ph - 18)], fill=pal.border_color, width=bw)

    elif trend == ArtDirectionTrend.TECH_FUTURE_HUD:
        # 45 Derece Pah Kırılmış (Chamfer) Siber Panel
        c = 32
        pts = [
            (cx + c, cy), (cx + pw - c, cy),
            (cx + pw, cy + c), (cx + pw, cy + ph - c),
            (cx + pw - c, cy + ph), (cx + c, cy + ph),
            (cx, cy + ph - c), (cx, cy + c)
        ]
        # Neon Dış Işıma
        draw.polygon(pts, fill=(10, 18, 36, 230), outline=pal.neon_primary, width=3)
        
        # Üst Telemetri Şeridi
        draw.line([(cx + c, cy + 45), (cx + pw - c, cy + 45)], fill=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 120), width=1)
        draw.text((cx + 40, cy + 14), "SYS.STATUS: BROADCAST LOCK  •  BITRATE: 8500K  •  FPS: 144  •  AI ENGINE ACTIVE", font=get_system_font("consola.ttf", 14), fill=pal.neon_accent)

        # Audio Visualizer Çubukları
        for i in range(28):
            bx = cx + 50 + i * 14
            bh = 10 + int(42 * abs(math.sin(i * 0.4)))
            draw.rectangle([(bx, cy + ph - 30 - bh), (bx + 8, cy + ph - 30)], fill=pal.neon_primary)

    else: # PREMIUM_STREAM
        # Lüks Buzlu Cam Efekti (Frosted Glassmorphism)
        # Dış yumuşak glow
        draw.rounded_rectangle([(cx - 5, cy - 5), (cx + pw + 5, cy + ph + 5)], radius=26, outline=(pal.neon_secondary[0], pal.neon_secondary[1], pal.neon_secondary[2], 90), width=5)
        draw.rounded_rectangle([(cx, cy), (cx + pw, cy + ph)], radius=24, fill=(20, 16, 36, 220), outline=pal.neon_primary, width=3)

        # Lüks Canlı Yayın Hap Rozeti
        pill_w, pill_h = 240, 38
        draw.rounded_rectangle([(cx + 45, cy + 35), (cx + 45 + pill_w, cy + 35 + pill_h)], radius=19, fill=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 40), outline=pal.neon_primary, width=1)
        draw.ellipse([(cx + 60, cy + 48), (cx + 72, cy + 60)], fill=(239, 68, 68, 255))
        draw.text((cx + 82, cy + 44), "CANLI YAYIN • ON AIR", font=get_system_font("arialbd.ttf", 13), fill=pal.text_main)

    # 3. TİPOGRAFİ KATMANI (BÜYÜK, GÖSTERİŞLİ VE HİYERARŞİK)
    font_hero = get_system_font("impact.ttf", 96)
    font_sub = get_system_font("arialbd.ttf", 26)
    font_tag = get_system_font("arial.ttf", 18)

    ch_text = channel_name.upper()

    if mode == "starting":
        sub_text = custom_title or "YAYIN BİRAZDAN BAŞLIYOR..."
        tagline = "Canlı Yayın & Espor Heyecanı Başlamak Üzere • Hazırlanın!"
    elif mode == "brb":
        sub_text = custom_title or "KISA BİR MOLA • HEMEN DÖNÜYORUM"
        tagline = "Kahve/İçecek Molası • Yayından Sakın Ayrılmayın!"
    else:
        sub_text = custom_title or "YAYIN SONA ERDİ • TEŞEKKÜRLER!"
        tagline = "Takip Etmeyi ve Bildirimleri Açmayı Unutmayın!"

    # Metin Konumlandırma (Hero Panel İçine Kusursuz Ortalama)
    text_x = cx + 80 if (trend != ArtDirectionTrend.ESPORTS_AGGRESSIVE) else cx + 140
    text_y = cy + 105

    # Başlık Metni ve Kalın Gölge
    draw.text((text_x + 5, text_y + 5), ch_text, font=font_hero, fill=(0, 0, 0, 240))
    draw.text((text_x, text_y), ch_text, font=font_hero, fill=pal.text_main)

    # Alt Başlık Plakası (Metin arkasına renkli kurdele/şerit)
    sub_y = text_y + 125
    if trend == ArtDirectionTrend.ESPORTS_AGGRESSIVE:
        s_slant = 20
        draw.polygon([(text_x + s_slant, sub_y), (text_x + 640, sub_y), (text_x + 640 - s_slant, sub_y + 52), (text_x, sub_y + 52)], fill=pal.neon_primary)
        draw.text((text_x + 25, sub_y + 12), sub_text, font=font_sub, fill=(12, 10, 20, 255))
    elif trend == ArtDirectionTrend.BOLD_BRUTALISM:
        draw.rectangle([(text_x, sub_y), (text_x + 660, sub_y + 54)], fill=pal.neon_secondary, outline=pal.border_color, width=3)
        draw.text((text_x + 20, sub_y + 12), sub_text, font=font_sub, fill=(10, 10, 12, 255))
    elif trend == ArtDirectionTrend.TECH_FUTURE_HUD:
        draw.rectangle([(text_x, sub_y), (text_x + 640, sub_y + 48)], fill=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 50), outline=pal.neon_accent, width=2)
        draw.text((text_x + 20, sub_y + 10), f">>> {sub_text}", font=font_sub, fill=pal.neon_accent)
    else: # PREMIUM_STREAM
        draw.line([(text_x, sub_y - 10), (text_x + 500, sub_y - 10)], fill=pal.neon_secondary, width=2)
        draw.text((text_x, sub_y + 10), sub_text, font=font_sub, fill=pal.neon_secondary)

    # Açıklama Metni (Tagline)
    tag_y = sub_y + 68
    draw.text((text_x, tag_y), tagline, font=font_tag, fill=pal.text_sub)

    # 4. ALT YAYINCI BİLGİ KUŞAĞI (FOOTER TICKER)
    foot_y = h - 70
    draw.line([(80, foot_y), (w - 80, foot_y)], fill=(pal.border_color[0], pal.border_color[1], pal.border_color[2], 90), width=1)
    
    footer_text = f"TWITCH / KICK: @{channel_name}   •   YOUTUBE: @{channel_name}   •   DİSCORD TOPLULUĞUMUZA KATILIN"
    f_box = draw.textbbox((0, 0), footer_text, font=get_system_font("arial.ttf", 15))
    draw.text(((w - (f_box[2] - f_box[0])) // 2, foot_y + 22), footer_text, font=get_system_font("arial.ttf", 15), fill=pal.text_sub)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_{mode}.png")
    img.save(out_file, "PNG")
    return out_file


# ==============================================================================
# 5. ÇOK KATMANLI ŞEFFAF WEBCAM ÇERÇEVESİ (1920x1080)
# ==============================================================================

def generate_webcam_overlay(channel_name: str = "Ripleytia", plan: Optional[MasterDesignPlan] = None) -> str:
    if plan is None:
        plan = _mutator.generate_plan()

    w, h = 1920, 1080
    pal = plan.palette
    trend = plan.trend

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cam_x, cam_y = 1360, 60
    cam_w, cam_h = 490, 276

    if trend == ArtDirectionTrend.ESPORTS_AGGRESSIVE:
        # Espor Açılı Kamera Çerçevesi
        draw.rectangle([(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)], outline=pal.neon_primary, width=3)
        # 4 Köşede Agresif Çapraz Köşebentler
        k = 40
        for px, py in [(cam_x, cam_y), (cam_x + cam_w, cam_y), (cam_x, cam_y + cam_h), (cam_x + cam_w, cam_y + cam_h)]:
            dx = 1 if px == cam_x else -1
            dy = 1 if py == cam_y else -1
            draw.line([(px, py), (px + dx * k, py)], fill=pal.neon_accent, width=5)
            draw.line([(px, py), (px, py + dy * k)], fill=pal.neon_accent, width=5)
        # Alt Paralelkenar İsim Rozeti
        slant = 20
        badge_y = cam_y + cam_h
        draw.polygon([(cam_x + slant, badge_y), (cam_x + cam_w, badge_y), (cam_x + cam_w - slant, badge_y + 36), (cam_x, badge_y + 36)], fill=(16, 12, 24, 240), outline=pal.neon_primary, width=2)
        draw.text((cam_x + 28, badge_y + 8), f"🔴 {channel_name.upper()}", font=get_system_font("impact.ttf", 16), fill=pal.text_main)
        draw.text((cam_x + cam_w - 95, badge_y + 8), "60 FPS", font=get_system_font("impact.ttf", 15), fill=pal.neon_accent)

    elif trend == ArtDirectionTrend.BOLD_BRUTALISM:
        # Sert Ofset Gölgeli Kalın Brutalist Çerçeve
        draw.rectangle([(cam_x + 8, cam_y + 8), (cam_x + cam_w + 8, cam_y + cam_h + 8)], fill=(0, 0, 0, 220))
        draw.rectangle([(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)], outline=pal.border_color, width=5)
        # Üst Etiket
        draw.rectangle([(cam_x, cam_y - 28), (cam_x + 180, cam_y)], fill=pal.border_color)
        draw.text((cam_x + 14, cam_y - 24), "CAM 01 // LIVE", font=get_system_font("consola.ttf", 14), fill=pal.neon_primary)
        # Alt İsim
        draw.rectangle([(cam_x, cam_y + cam_h), (cam_x + cam_w, cam_y + cam_h + 32)], fill=pal.border_color)
        draw.text((cam_x + 14, cam_y + cam_h + 6), f">> {channel_name.upper()}", font=get_system_font("impact.ttf", 16), fill=(255, 255, 255, 255))

    elif trend == ArtDirectionTrend.TECH_FUTURE_HUD:
        # 45 Derece Chamfer Kesimli Siber Çerçeve
        c = 20
        pts = [
            (cam_x + c, cam_y), (cam_x + cam_w - c, cam_y),
            (cam_x + cam_w, cam_y + c), (cam_x + cam_w, cam_y + cam_h - c),
            (cam_x + cam_w - c, cam_y + cam_h), (cam_x + c, cam_y + cam_h),
            (cam_x, cam_y + cam_h - c), (cam_x, cam_y + c)
        ]
        draw.polygon(pts, outline=pal.neon_primary, width=3)
        # Telemetri
        draw.text((cam_x + 10, cam_y - 22), f"OPTICAL_FEED // {channel_name.upper()}", font=get_system_font("consola.ttf", 13), fill=pal.neon_accent)
        draw.text((cam_x + cam_w - 110, cam_y - 22), "1080P // LOCK", font=get_system_font("consola.ttf", 13), fill=pal.neon_primary)

    else: # PREMIUM_STREAM
        # Lüks Frosted Glass Çerçeve
        draw.rounded_rectangle([(cam_x - 3, cam_y - 3), (cam_x + cam_w + 3, cam_y + cam_h + 3)], radius=16, outline=(pal.neon_primary[0], pal.neon_primary[1], pal.neon_primary[2], 90), width=4)
        draw.rounded_rectangle([(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)], radius=14, outline=pal.neon_primary, width=2)
        # Alt Zarif İsim Plakası
        draw.rounded_rectangle([(cam_x, cam_y + cam_h + 6), (cam_x + cam_w, cam_y + cam_h + 40)], radius=10, fill=(20, 16, 36, 230), outline=pal.neon_primary, width=1)
        draw.ellipse([(cam_x + 18, cam_y + cam_h + 17), (cam_x + 28, cam_y + cam_h + 27)], fill=(239, 68, 68, 255))
        draw.text((cam_x + 36, cam_y + cam_h + 12), f"LIVE • {channel_name.upper()}", font=get_system_font("arialbd.ttf", 13), fill=pal.text_main)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_webcam_overlay.png")
    img.save(out_file, "PNG")
    return out_file


# ==============================================================================
# 6. ÇOK KATMANLI ŞEFFAF SOHBET KUTUSU (1920x1080)
# ==============================================================================

def generate_chat_overlay(channel_name: str = "Ripleytia", plan: Optional[MasterDesignPlan] = None) -> str:
    if plan is None:
        plan = _mutator.generate_plan()

    w, h = 1920, 1080
    pal = plan.palette
    trend = plan.trend

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 60, 360
    cw, ch = 440, 650

    if trend == ArtDirectionTrend.ESPORTS_AGGRESSIVE:
        # Açılı Espor Başlık Şeridi
        slant = 18
        draw.rectangle([(cx, cy + 42), (cx + cw, cy + ch)], fill=(14, 10, 22, 160), outline=pal.neon_primary, width=2)
        draw.polygon([(cx + slant, cy), (cx + cw, cy), (cx + cw - slant, cy + 42), (cx, cy + 42)], fill=pal.neon_primary)
        draw.text((cx + 25, cy + 10), f"💬 CANLI SOHBET // {channel_name.upper()}", font=get_system_font("impact.ttf", 16), fill=(10, 8, 16, 255))
        
    elif trend == ArtDirectionTrend.BOLD_BRUTALISM:
        # Kalın Brutalist Kutu ve Başlık
        draw.rectangle([(cx + 6, cy + 6), (cx + cw + 6, cy + ch + 6)], fill=(0, 0, 0, 210))
        draw.rectangle([(cx, cy), (cx + cw, cy + ch)], fill=(18, 18, 22, 190), outline=pal.border_color, width=4)
        draw.rectangle([(cx, cy), (cx + cw, cy + 40)], fill=pal.border_color)
        draw.text((cx + 16, cy + 10), f"[ CHAT FEED // @{channel_name.upper()} ]", font=get_system_font("consola.ttf", 15), fill=pal.neon_primary)

    elif trend == ArtDirectionTrend.TECH_FUTURE_HUD:
        # Siber Chamfer Kutu
        c = 16
        pts = [
            (cx + c, cy), (cx + cw - c, cy),
            (cx + cw, cy + c), (cx + cw, cy + ch - c),
            (cx + cw - c, cy + ch), (cx + c, cy + ch),
            (cx, cy + ch - c), (cx, cy + c)
        ]
        draw.polygon(pts, fill=(10, 16, 32, 175), outline=pal.neon_primary, width=2)
        draw.line([(cx + c, cy + 40), (cx + cw - c, cy + 40)], fill=pal.neon_primary, width=2)
        draw.text((cx + 18, cy + 12), f"SYS.CHAT // STREAM FEED", font=get_system_font("consola.ttf", 14), fill=pal.neon_accent)

    else: # PREMIUM_STREAM
        # Lüks Frosted Glass Gövde
        draw.rounded_rectangle([(cx, cy), (cx + cw, cy + ch)], radius=16, fill=(20, 16, 36, 170), outline=pal.neon_primary, width=2)
        draw.rounded_rectangle([(cx, cy), (cx + cw, cy + 44)], radius=14, fill=(pal.bg_start[0], pal.bg_start[1], pal.bg_start[2], 230), outline=pal.neon_secondary, width=1)
        draw.text((cx + 20, cy + 12), f"💬 Canlı Sohbet • @{channel_name}", font=get_system_font("arialbd.ttf", 14), fill=pal.text_main)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_chat_overlay.png")
    img.save(out_file, "PNG")
    return out_file


# ==============================================================================
# 7. ÇOK KATMANLI SEGMENTLİ ETKİNLİK ŞERİDİ (EVENT TICKER 1920x1080)
# ==============================================================================

def generate_event_ticker(channel_name: str = "Ripleytia", plan: Optional[MasterDesignPlan] = None) -> str:
    if plan is None:
        plan = _mutator.generate_plan()

    w, h = 1920, 1080
    pal = plan.palette
    trend = plan.trend

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    tx, ty = 140, 20
    tw, th = 1640, 52

    # 3 Ayrı Bağımsız Lüks Modül Çizimi (Segmented Cards)
    card_w = (tw - 40) // 3
    
    modules = [
        ("⭐ SON TAKİPÇİ", "Topluluk Üyesi", pal.neon_primary),
        ("💎 SON ABONE", "VIP Destekçi", pal.neon_secondary),
        ("🎯 HEDEF", "%85 (850/1000)", pal.neon_accent)
    ]

    for i, (title, val, color) in enumerate(modules):
        mx = tx + i * (card_w + 20)
        
        if trend == ArtDirectionTrend.ESPORTS_AGGRESSIVE:
            slant = 14
            poly = [(mx + slant, ty), (mx + card_w, ty), (mx + card_w - slant, ty + th), (mx, ty + th)]
            draw.polygon(poly, fill=(16, 12, 24, 235), outline=color, width=2)
            draw.text((mx + 22, ty + 15), title, font=get_system_font("impact.ttf", 15), fill=color)
            draw.text((mx + 155, ty + 15), val, font=get_system_font("arialbd.ttf", 14), fill=pal.text_main)
            
        elif trend == ArtDirectionTrend.BOLD_BRUTALISM:
            draw.rectangle([(mx + 4, ty + 4), (mx + card_w + 4, ty + th + 4)], fill=(0, 0, 0, 220))
            draw.rectangle([(mx, ty), (mx + card_w, ty + th)], fill=(20, 20, 24, 240), outline=color, width=3)
            draw.text((mx + 16, ty + 15), title, font=get_system_font("consola.ttf", 14), fill=color)
            draw.text((mx + 150, ty + 15), val, font=get_system_font("impact.ttf", 16), fill=(255, 255, 255, 255))

        else: # TECH & PREMIUM
            draw.rounded_rectangle([(mx, ty), (mx + card_w, ty + th)], radius=12, fill=(18, 14, 30, 225), outline=color, width=2)
            draw.text((mx + 18, ty + 16), title, font=get_system_font("arialbd.ttf", 13), fill=color)
            draw.text((mx + 145, ty + 16), val, font=get_system_font("arial.ttf", 14), fill=pal.text_main)

        # Hedef Modülü için Canlı İlerleme Çubuğu (Mini Progress Bar)
        if i == 2:
            bar_x = mx + 260
            bar_y = ty + 18
            bar_w = card_w - 280
            draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + 14)], radius=7, fill=(35, 30, 50, 255))
            draw.rounded_rectangle([(bar_x, bar_y), (bar_x + int(bar_w * 0.85), bar_y + 14)], radius=7, fill=color)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_ticker_overlay.png")
    img.save(out_file, "PNG")
    return out_file


# ==============================================================================
# 8. OBS SAHNE KOLEKSİYONU PAKETLEYİCİSİ
# ==============================================================================

def build_ai_scene_collection(channel_name: str = "Ripleytia", 
                              theme_name: str = "🎲 Tamamen Rastgele (Profesyonel Yayıncı Trendleri)", 
                              collection_name: Optional[str] = None, 
                              custom_color_query: str = "") -> Dict[str, Any]:
    plan = _mutator.generate_plan(requested_trend=theme_name, query=custom_color_query)

    start_banner = generate_channel_banner(channel_name=channel_name, plan=plan, mode="starting")
    brb_banner = generate_channel_banner(channel_name=channel_name, plan=plan, mode="brb")
    end_banner = generate_channel_banner(channel_name=channel_name, plan=plan, mode="ending")
    webcam_overlay = generate_webcam_overlay(channel_name=channel_name, plan=plan)
    chat_overlay = generate_chat_overlay(channel_name=channel_name, plan=plan)
    ticker_overlay = generate_event_ticker(channel_name=channel_name, plan=plan)

    appdata = os.environ.get("APPDATA", "")
    scenes_dir = os.path.join(appdata, "obs-studio", "basic", "scenes")
    os.makedirs(scenes_dir, exist_ok=True)

    c_name = collection_name or f"Ripleytia Pro AI - {channel_name} ({plan.design_id})"
    safe_name = "".join(c for c in c_name if c.isalnum() or c in (" ", "_", "-")).strip()
    filepath = os.path.join(scenes_dir, f"{safe_name}.json")

    start_scene_uuid = str(uuid.uuid4())
    brb_scene_uuid = str(uuid.uuid4())
    end_scene_uuid = str(uuid.uuid4())
    game_scene_uuid = str(uuid.uuid4())
    cam_scene_uuid = str(uuid.uuid4())

    start_img_uuid = str(uuid.uuid4())
    brb_img_uuid = str(uuid.uuid4())
    end_img_uuid = str(uuid.uuid4())
    cam_overlay_uuid = str(uuid.uuid4())
    chat_overlay_uuid = str(uuid.uuid4())
    ticker_uuid = str(uuid.uuid4())
    game_cap_uuid = str(uuid.uuid4())

    collection = {
        "current_scene": "🎮 1 - Ana Oyun & Canlı Yayın",
        "current_program_scene": "🎮 1 - Ana Oyun & Canlı Yayın",
        "name": c_name,
        "scene_order": [
            {"name": "🎮 1 - Ana Oyun & Canlı Yayın"},
            {"name": "💬 2 - Tam Ekran Kamera & Sohbet"},
            {"name": "⏳ 3 - Yayın Başlıyor"},
            {"name": "☕ 4 - Kısa Mola (BRB)"},
            {"name": "👋 5 - Yayın Bitti"}
        ],
        "sources": [
            {
                "name": "🎮 1 - Ana Oyun & Canlı Yayın",
                "uuid": game_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {
                    "id_counter": 4,
                    "items": [
                        {"name": "Oyun Yakalama (FiveM / Game)", "source_uuid": game_cap_uuid, "visible": True, "locked": True},
                        {"name": "Webcam Çerçevesi (AI)", "source_uuid": cam_overlay_uuid, "visible": True, "locked": True},
                        {"name": "Sohbet Kutusu Çerçevesi (AI)", "source_uuid": chat_overlay_uuid, "visible": True, "locked": True},
                        {"name": "Etkinlik & Hedef Şeridi (AI)", "source_uuid": ticker_uuid, "visible": True, "locked": True}
                    ]
                }
            },
            {
                "name": "💬 2 - Tam Ekran Kamera & Sohbet",
                "uuid": cam_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {
                    "id_counter": 2,
                    "items": [
                        {"name": "Sohbet Kutusu Çerçevesi (AI)", "source_uuid": chat_overlay_uuid, "visible": True, "locked": True},
                        {"name": "Etkinlik & Hedef Şeridi (AI)", "source_uuid": ticker_uuid, "visible": True, "locked": True}
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
        "plan": plan,
        "assets": {
            "start_banner": start_banner,
            "brb_banner": brb_banner,
            "end_banner": end_banner,
            "webcam_overlay": webcam_overlay,
            "chat_overlay": chat_overlay,
            "ticker_overlay": ticker_overlay
        }
    }


def generate_ai_stream_strategy(channel_name: str = "Ripleytia", game_type: str = "FiveM / GTA V", style: str = "Eğlenceli & Dinamik", api_key: str = ""):
    strategies = {
        "FiveM / GTA V (Roleplay)": {
            "titles": [
                f"🚨 [{channel_name}] LOS SANTOS SOKAKLARI HAREKETLİ! | Hard RP | 0 Dropped Frames",
                f"🔫 GİZLİ OPERASYON & SOYGUN PLANI | {channel_name} ile FiveM Gecesi",
                f"🚔 DEPARTMAN ACİL DURUM KODU! | Roleplay Zirvesi | {channel_name}"
            ],
            "polls": [
                "Polisten kaçarken hangi aracı tercih edelim? (Sultan RS / Dominator)",
                "Bu gece yasa dışı işlere bulaşalım mı? (Evet / Hayır)"
            ],
            "challenges": [
                "15 dakika boyunca sadece telsiz komutlarına uyarak operasyon yönet!"
            ],
            "advice": "FiveM için OBS sahnenizde ReShade koruması devrede. Discord ve oyun içi telsiz ses düzeylerini dengeleyin."
        },
        "Valorant / CS2 (Rekabetçi FPS)": {
            "titles": [
                f"🎯 RADYANT / GLOBAL YOLCULUĞU! | [{channel_name}] | 144Hz+ 0 Input Lag",
                f"🔥 KAFADAN VURUŞ MAKİNESİ! | Dereceli Maçlar | {channel_name} Canlıda",
                f"⚡ CLUTCH OR LOSE! | Espor Modu Aktif | {channel_name}"
            ],
            "polls": [
                "Sonraki elde hangi silahı alayım? (Vandal / Phantom)",
                "Bölgeye agresif mi girelim pasif mi bekleyelim?"
            ],
            "challenges": [
                "Eco round'unda sadece tabanca ile clutch at!"
            ],
            "advice": "FPS oyunlarında düşük gecikme için NVENC P6 Tuning Ultra-Low Latency profilini ve RNNoise mikrofon filtresini aktif tuttuk."
        }
    }
    return strategies.get(game_type, {
        "titles": [f"🚀 {channel_name} CANLI YAYINDA! | Keyifli Sohbet & Oyunlar", f"✨ {channel_name} ile Yayın Vakti"],
        "polls": ["Bir sonraki yayında hangi oyunu oynayalım?"],
        "challenges": ["İzleyicilerden gelen zorlu meydan okumayı tamamla!"],
        "advice": "OBS ayarlarınız donanımınıza göre optimize edildi."
    })
