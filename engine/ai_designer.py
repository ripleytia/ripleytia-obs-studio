# -*- coding: utf-8 -*-
"""
engine/ai_designer.py
================================================================================
OBS AI Studio - EsportsDesignFactory v1.5.0
Syhd3 / WTCN / VCT Espor Kalitesi: Grunge Doku, 3D Tipografi, Neon Aura
Anti-Repetition DesignHistoryManager ile %50 Benzerlik Eşiği
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ==============================================================================
# 1. SABIT HAVUZLAR (Trait Pools for DesignHistoryManager)
# ==============================================================================

TEXTURE_TYPES  = ["heavy_grunge_scratch", "dark_brushed_metal", "carbon_fiber_weave",
                   "distressed_concrete", "smoke_light_leaks"]

EMBLEM_SHAPES  = ["hexagon", "shield", "slash_strips", "diamond_cut",
                   "sector_wedge", "chamfer_rect"]

TYPO_STYLES    = ["3d_extrude_heavy", "outline_glow", "italic_slash_impact",
                   "brutalist_block", "hud_mono_neon"]

AURA_FAMILIES  = ["crimson_red", "cyber_cyan", "electric_gold",
                   "void_purple", "acid_green"]

LAYOUTS        = ["center_hero", "left_wedge", "bottom_ribbon",
                   "full_bleed_hud", "asymmetric_tilt"]


# ==============================================================================
# 2. RENK PALETİ VE YARDIMCI FONKSİYONLAR
# ==============================================================================

@dataclass
class ColorPalette:
    name:           str
    bg_start:       Tuple[int, int, int, int]
    bg_end:         Tuple[int, int, int, int]
    neon_primary:   Tuple[int, int, int, int]
    neon_secondary: Tuple[int, int, int, int]
    neon_accent:    Tuple[int, int, int, int]
    text_main:      Tuple[int, int, int, int]
    text_sub:       Tuple[int, int, int, int]
    border_color:   Tuple[int, int, int, int]


def hex_to_rgba(h: str, a: int = 255) -> Tuple[int, int, int, int]:
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, a)


def _blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def get_system_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Windows sistem fontlarını güvenle yükler."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fp = os.path.join(windir, "Fonts", name)
    if os.path.exists(fp):
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            pass
    for alt in ["impact.ttf", "arialbd.ttf", "segoeuib.ttf", "arial.ttf"]:
        alt_fp = os.path.join(windir, "Fonts", alt)
        if os.path.exists(alt_fp):
            try:
                return ImageFont.truetype(alt_fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def get_appdata_obs_assets_dir() -> str:
    base = os.path.join(os.environ.get("APPDATA", ""), "obs-studio", "ripleytia_assets")
    os.makedirs(base, exist_ok=True)
    return base


# ==============================================================================
# 3. RENK UYUMLAYICI (AI Color Harmonizer)
# ==============================================================================

class AIColorHarmonizer:
    PRESET_PALETTES = {
        "Cyber Gothic Purple": ColorPalette(
            name="Cyber Gothic Purple",
            bg_start=(14, 10, 24, 255), bg_end=(32, 14, 52, 255),
            neon_primary=(168, 85, 247, 255), neon_secondary=(216, 180, 254, 255),
            neon_accent=(0, 245, 212, 255), text_main=(255, 255, 255, 255),
            text_sub=(200, 185, 220, 255), border_color=(168, 85, 247, 255)
        ),
        "Neon Cyberpunk (Mavi/Pembe)": ColorPalette(
            name="Neon Cyberpunk",
            bg_start=(8, 12, 22, 255), bg_end=(18, 28, 48, 255),
            neon_primary=(0, 245, 212, 255), neon_secondary=(255, 0, 128, 255),
            neon_accent=(255, 222, 89, 255), text_main=(255, 255, 255, 255),
            text_sub=(180, 220, 240, 255), border_color=(0, 245, 212, 255)
        ),
        "Esports Red/Black (Valorant)": ColorPalette(
            name="Esports Red Black",
            bg_start=(8, 6, 6, 255), bg_end=(22, 8, 8, 255),
            neon_primary=(255, 50, 50, 255), neon_secondary=(255, 160, 0, 255),
            neon_accent=(255, 255, 255, 255), text_main=(255, 255, 255, 255),
            text_sub=(200, 180, 180, 255), border_color=(255, 50, 50, 255)
        ),
        "Brutalist Gold/Black": ColorPalette(
            name="Brutalist Gold",
            bg_start=(10, 10, 10, 255), bg_end=(22, 20, 12, 255),
            neon_primary=(255, 200, 0, 255), neon_secondary=(200, 140, 0, 255),
            neon_accent=(255, 255, 255, 255), text_main=(255, 255, 255, 255),
            text_sub=(210, 190, 150, 255), border_color=(255, 200, 0, 255)
        ),
        "Tech HUD Cyan/Dark": ColorPalette(
            name="Tech HUD Cyan",
            bg_start=(6, 14, 18, 255), bg_end=(10, 26, 34, 255),
            neon_primary=(0, 200, 255, 255), neon_secondary=(0, 255, 180, 255),
            neon_accent=(255, 220, 50, 255), text_main=(255, 255, 255, 255),
            text_sub=(160, 220, 240, 255), border_color=(0, 200, 255, 255)
        ),
        "Premium Stream (Lüks)": ColorPalette(
            name="Premium Stream",
            bg_start=(12, 10, 18, 255), bg_end=(24, 20, 36, 255),
            neon_primary=(200, 160, 255, 255), neon_secondary=(255, 180, 240, 255),
            neon_accent=(100, 220, 255, 255), text_main=(255, 255, 255, 255),
            text_sub=(190, 175, 210, 255), border_color=(180, 140, 255, 255)
        ),
    }

    # Aura Family → RGB core color
    AURA_COLORS = {
        "crimson_red":   (255, 40,  40),
        "cyber_cyan":    (0,   220, 255),
        "electric_gold": (255, 200, 0),
        "void_purple":   (160, 60,  255),
        "acid_green":    (80,  255, 60),
    }

    @classmethod
    def resolve(cls, trend_name: str, preset_name: str, query: str) -> "ColorPalette":
        if preset_name and preset_name in cls.PRESET_PALETTES:
            return cls.PRESET_PALETTES[preset_name]
        # trend-based default
        mapping = {
            "🔥 ESPOR / AGRESİF (Valorant Champions / VCT)": "Esports Red/Black (Valorant)",
            "⬛ BOLD BRUTALISM (Endüstriyel & Devasa Tipografi)": "Brutalist Gold/Black",
            "⚡ TECH / MINIMALIST FUTURE (Cyberpunk HUD)": "Tech HUD Cyan/Dark",
            "💎 PREMIUM STREAM (Modern Lüks & Glassmorphism)": "Cyber Gothic Purple",
        }
        key = mapping.get(trend_name, "Neon Cyberpunk (Mavi/Pembe)")
        return cls.PRESET_PALETTES.get(key, list(cls.PRESET_PALETTES.values())[0])


# Backward-compat export for main.py
THEME_PALETTES = AIColorHarmonizer.PRESET_PALETTES


# ==============================================================================
# 4. DESIGN PLAN
# ==============================================================================

class ArtDirectionTrend(str, Enum):
    ESPORTS_AGGRESSIVE = "🔥 ESPOR / AGRESİF (Valorant Champions / VCT)"
    BOLD_BRUTALISM     = "⬛ BOLD BRUTALISM (Endüstriyel & Devasa Tipografi)"
    TECH_FUTURE_HUD    = "⚡ TECH / MINIMALIST FUTURE (Cyberpunk HUD)"
    PREMIUM_STREAM     = "💎 PREMIUM STREAM (Modern Lüks & Glassmorphism)"


class SkeletonLayout(str, Enum):
    CENTER_HERO_CARD          = "center_hero_card"
    LEFT_MONOLITH_DOCK        = "left_monolith_dock"
    ASYMMETRIC_SPLIT_WEDGE    = "asymmetric_split_wedge"
    CINEMATIC_BROADCAST_RIBBON = "cinematic_broadcast_ribbon"


@dataclass
class DesignTraits:
    texture_type:    str
    emblem_shape:    str
    typo_style:      str
    aura_family:     str
    layout:          str


@dataclass
class MasterDesignPlan:
    design_id: str
    trend:     ArtDirectionTrend
    skeleton:  SkeletonLayout
    palette:   ColorPalette
    seed:      int
    traits:    DesignTraits


# ==============================================================================
# 5. DESIGN HISTORY MANAGER (%50 Benzerlik Eşiği)
# ==============================================================================

class DesignHistoryManager:
    """Son 10 tasarımı saklar; %50+ benzerlik varsa yeni plan reddedilir."""

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self._history: List[DesignTraits] = []

    def _similarity(self, a: DesignTraits, b: DesignTraits) -> float:
        fields = ["texture_type", "emblem_shape", "typo_style", "aura_family", "layout"]
        matches = sum(getattr(a, f) == getattr(b, f) for f in fields)
        return matches / len(fields)

    def is_too_similar(self, candidate: DesignTraits) -> bool:
        for past in self._history:
            if self._similarity(candidate, past) >= 0.5:
                return True
        return False

    def record(self, traits: DesignTraits):
        self._history.append(traits)
        if len(self._history) > self.max_history:
            self._history.pop(0)


# ==============================================================================
# 6. ESPORTS DESIGN FACTORY — GLOBAL SINGLETON
# ==============================================================================

class EsportsDesignFactory:
    """
    Her çağrıda:
      • Rastgele bir DesignTraits seçer
      • DesignHistoryManager ile %50 benzerlik kontrolü yapar (max 15 deneme)
      • Pillow ile tam katmanlı esports görseli üretir
    """

    def __init__(self):
        self._history = DesignHistoryManager(max_history=10)
        self._trend_history: List[Tuple[ArtDirectionTrend, SkeletonLayout]] = []

    # ------------------------------------------------------------------
    # Plan Üretici
    # ------------------------------------------------------------------

    MAX_MUTATION_RETRIES = 3  # Fail-safe: 3 denemede bulunamazsa en iyi adayı kabul et

    def generate_plan(
        self,
        requested_trend: Optional[str],
        query: str,
        preset_name: str = ""
    ) -> MasterDesignPlan:
        rng = random.Random(int(time.time() * 1000))
        best_traits = None
        best_skeleton = None
        best_trend = None

        for attempt in range(self.MAX_MUTATION_RETRIES):
            rng = random.Random(int(time.time() * 1000) + attempt * 7919)

            # Trend seç
            if requested_trend:
                try:
                    trend = ArtDirectionTrend(requested_trend)
                except ValueError:
                    trend = rng.choice(list(ArtDirectionTrend))
            else:
                trend = rng.choice(list(ArtDirectionTrend))

            skeleton = rng.choice(list(SkeletonLayout))

            traits = DesignTraits(
                texture_type = rng.choice(TEXTURE_TYPES),
                emblem_shape = rng.choice(EMBLEM_SHAPES),
                typo_style   = rng.choice(TYPO_STYLES),
                aura_family  = rng.choice(AURA_FAMILIES),
                layout       = rng.choice(LAYOUTS),
            )

            # İlk adayı her zaman kaydet (en kötü ihtimal için)
            if best_traits is None:
                best_traits  = traits
                best_skeleton = skeleton
                best_trend   = trend

            if not self._history.is_too_similar(traits):
                # Benzersiz aday bulundu — hemen kullan
                best_traits  = traits
                best_skeleton = skeleton
                best_trend   = trend
                break
            # else: benzer → bir sonraki denemeye geç (max 3)

        # Garantili devam: en iyi (veya 3. deneme) aday kullanılır
        palette = AIColorHarmonizer.resolve(best_trend.value, preset_name, query)
        self._history.record(best_traits)
        self._trend_history.append((best_trend, best_skeleton))
        if len(self._trend_history) > 15:
            self._trend_history.pop(0)

        return MasterDesignPlan(
            design_id=str(uuid.uuid4())[:8],
            trend=best_trend,
            skeleton=best_skeleton,
            palette=palette,
            seed=rng.randint(0, 2**31),
            traits=best_traits,
        )

    # ------------------------------------------------------------------
    # KATMAN 1: Grunge / Doku Arka Plan
    # ------------------------------------------------------------------
    def _draw_background(self, img: Image.Image, plan: MasterDesignPlan, rng: random.Random):
        draw = ImageDraw.Draw(img, "RGBA")
        w, h = img.size
        p = plan.palette
        tex = plan.traits.texture_type

        # Gradyan taban
        for y in range(h):
            t = y / h
            c = _blend(p.bg_start, p.bg_end, t)
            draw.line([(0, y), (w, y)], fill=c)

        # Tekstür katmanı
        if tex == "heavy_grunge_scratch":
            self._grunge_scratches(draw, w, h, p.bg_start, rng, count=400, alpha_max=55)
        elif tex == "dark_brushed_metal":
            self._brushed_metal(draw, w, h, p.bg_start, rng)
        elif tex == "carbon_fiber_weave":
            self._carbon_fiber(draw, w, h, rng)
        elif tex == "distressed_concrete":
            self._distressed_concrete(draw, w, h, p.bg_start, rng)
        elif tex == "smoke_light_leaks":
            self._smoke_light_leaks(img, w, h, p.neon_primary, rng)

    def _grunge_scratches(self, draw, w, h, base_color, rng, count=350, alpha_max=55):
        for _ in range(count):
            y     = rng.randint(0, h)
            x0    = rng.randint(0, w // 4)
            x1    = rng.randint(3 * w // 4, w)
            alpha = rng.randint(8, alpha_max)
            r     = _clamp(base_color[0] + rng.randint(20, 70))
            g     = _clamp(base_color[1] + rng.randint(20, 70))
            b     = _clamp(base_color[2] + rng.randint(20, 70))
            draw.line([(x0, y), (x1, y + rng.randint(-2, 2))], fill=(r, g, b, alpha), width=rng.randint(1, 2))

    def _brushed_metal(self, draw, w, h, base_color, rng):
        for _ in range(500):
            y     = rng.randint(0, h)
            alpha = rng.randint(5, 35)
            brt   = rng.randint(30, 80)
            r = _clamp(base_color[0] + brt)
            g = _clamp(base_color[1] + brt)
            b = _clamp(base_color[2] + brt)
            draw.line([(0, y), (w, y)], fill=(r, g, b, alpha), width=1)
        for _ in range(120):
            x     = rng.randint(0, w)
            alpha = rng.randint(3, 20)
            brt   = rng.randint(10, 40)
            r = _clamp(base_color[0] + brt)
            g = _clamp(base_color[1] + brt)
            b = _clamp(base_color[2] + brt)
            draw.line([(x, 0), (x + rng.randint(-30, 30), h)], fill=(r, g, b, alpha), width=1)

    def _carbon_fiber(self, draw, w, h, rng):
        tile = 12
        for row in range(0, h + tile, tile):
            for col in range(0, w + tile, tile):
                offset = tile // 2 if (row // tile) % 2 == 0 else 0
                x0 = col + offset
                y0 = row
                x1 = x0 + tile // 2 - 1
                y1 = y0 + tile - 1
                dark  = rng.randint(18, 28)
                light = rng.randint(35, 50)
                draw.rectangle([x0, y0, x1, y1], fill=(dark, dark, dark, 220))
                draw.rectangle([x1 + 1, y0, x1 + tile // 2, y1], fill=(light, light, light, 180))
                # highlight edge
                draw.line([(x0, y0), (x1, y0)], fill=(60, 60, 60, 80))

    def _distressed_concrete(self, draw, w, h, base_color, rng):
        for _ in range(800):
            x     = rng.randint(0, w)
            y     = rng.randint(0, h)
            size  = rng.randint(1, 6)
            alpha = rng.randint(5, 40)
            v     = rng.randint(-30, 30)
            c     = tuple(_clamp(base_color[i] + v) for i in range(3)) + (alpha,)
            draw.ellipse([x - size, y - size, x + size, y + size], fill=c)
        for _ in range(60):
            x0    = rng.randint(0, w)
            y0    = rng.randint(0, h)
            x1    = x0 + rng.randint(-100, 100)
            y1    = y0 + rng.randint(-60, 60)
            alpha = rng.randint(6, 25)
            draw.line([(x0, y0), (x1, y1)], fill=(120, 110, 100, alpha), width=rng.randint(1, 3))

    def _smoke_light_leaks(self, img: Image.Image, w, h, neon_color, rng):
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")
        for _ in range(6):
            cx = rng.randint(0, w)
            cy = rng.randint(0, h)
            radius = rng.randint(120, 350)
            for step in range(15):
                t     = step / 14
                r_cur = int(radius * (1 - t * 0.85))
                alpha = int((1 - t) * rng.randint(8, 25))
                c     = (neon_color[0], neon_color[1], neon_color[2], alpha)
                draw.ellipse([cx - r_cur, cy - r_cur, cx + r_cur, cy + r_cur], fill=c)
        img.alpha_composite(overlay)

    # ------------------------------------------------------------------
    # KATMAN 2: Neon Volumetric Bloom Aura
    # ------------------------------------------------------------------
    def _draw_neon_bloom(
        self,
        img: Image.Image,
        cx: int, cy: int,
        aura_family: str,
        radius: int,
        rng: random.Random,
    ):
        base_rgb = AIColorHarmonizer.AURA_COLORS.get(aura_family, (0, 200, 255))
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")
        steps = 22
        for i in range(steps):
            t       = i / (steps - 1)
            r_cur   = max(8, int(radius * (1 - t * 0.92)))
            alpha   = int(t * 0 + (1 - t) * rng.randint(12, 48))  # outer dim, inner bright
            # Reverse: inner bright
            alpha   = int((1 - t) * 10 + t * 0)  # outer fades
            alpha   = int(55 * (1 - t) ** 1.8)
            c       = (base_rgb[0], base_rgb[1], base_rgb[2], _clamp(alpha))
            draw.ellipse([cx - r_cur, cy - r_cur, cx + r_cur, cy + r_cur], fill=c)
        img.alpha_composite(overlay)

    # ------------------------------------------------------------------
    # KATMAN 3: Emblem Şekli
    # ------------------------------------------------------------------
    def _draw_emblem(
        self,
        draw: ImageDraw.ImageDraw,
        cx: int, cy: int,
        shape: str,
        palette: ColorPalette,
        rng: random.Random,
        size: int = 180,
    ):
        col  = palette.neon_primary
        col2 = palette.neon_secondary
        fill = (col[0], col[1], col[2], 30)
        line_col = (col[0], col[1], col[2], 200)

        if shape == "hexagon":
            pts = [
                (cx + size * math.cos(math.radians(60 * i - 30)),
                 cy + size * math.sin(math.radians(60 * i - 30)))
                for i in range(6)
            ]
            draw.polygon(pts, fill=fill, outline=line_col)
            pts2 = [
                (cx + (size * 0.7) * math.cos(math.radians(60 * i - 30)),
                 cy + (size * 0.7) * math.sin(math.radians(60 * i - 30)))
                for i in range(6)
            ]
            draw.polygon(pts2, fill=(0, 0, 0, 0), outline=(col2[0], col2[1], col2[2], 140))

        elif shape == "shield":
            s = size
            pts = [
                (cx, cy - s),
                (cx + s * 0.75, cy - s * 0.4),
                (cx + s * 0.75, cy + s * 0.3),
                (cx, cy + s),
                (cx - s * 0.75, cy + s * 0.3),
                (cx - s * 0.75, cy - s * 0.4),
            ]
            draw.polygon(pts, fill=fill, outline=line_col)

        elif shape == "slash_strips":
            for i in range(-3, 4):
                offset = i * (size // 3)
                x0 = cx + offset - size // 6
                x1 = cx + offset + size // 6
                pts = [(x0 - size // 2, cy - size), (x1 - size // 2, cy - size),
                       (x1 + size // 2, cy + size), (x0 + size // 2, cy + size)]
                alpha = rng.randint(15, 45)
                draw.polygon(pts, fill=(col[0], col[1], col[2], alpha))

        elif shape == "diamond_cut":
            s = size
            pts = [(cx, cy - s), (cx + s * 0.6, cy), (cx, cy + s), (cx - s * 0.6, cy)]
            draw.polygon(pts, fill=fill, outline=line_col)
            inner = [(cx, cy - s * 0.5), (cx + s * 0.3, cy), (cx, cy + s * 0.5), (cx - s * 0.3, cy)]
            draw.polygon(inner, fill=(col2[0], col2[1], col2[2], 45))

        elif shape == "sector_wedge":
            s = size
            pts = [(cx, cy), (cx - s * 1.4, cy - s * 0.6), (cx - s * 1.4, cy + s * 0.6)]
            draw.polygon(pts, fill=fill, outline=line_col)
            pts2 = [(cx, cy), (cx - s * 0.9, cy - s * 0.38), (cx - s * 0.9, cy + s * 0.38)]
            draw.polygon(pts2, fill=(col2[0], col2[1], col2[2], 50))

        elif shape == "chamfer_rect":
            s = size
            c2 = int(s * 0.25)
            pts = [
                (cx - s + c2, cy - s * 0.6),
                (cx + s - c2, cy - s * 0.6),
                (cx + s,       cy - s * 0.6 + c2),
                (cx + s,       cy + s * 0.6 - c2),
                (cx + s - c2, cy + s * 0.6),
                (cx - s + c2, cy + s * 0.6),
                (cx - s,       cy + s * 0.6 - c2),
                (cx - s,       cy - s * 0.6 + c2),
            ]
            draw.polygon(pts, fill=fill, outline=line_col)

    # ------------------------------------------------------------------
    # KATMAN 4: 3D Extruded Typography
    # ------------------------------------------------------------------
    def _draw_3d_text(
        self,
        draw: ImageDraw.ImageDraw,
        x: int, y: int,
        text: str,
        font: ImageFont.FreeTypeFont,
        face_color: Tuple,
        stroke_color: Tuple,
        extrude_color: Tuple,
        extrude_depth: int = 10,
        anchor: str = "mm",
    ):
        # Shadow passes (deep to shallow)
        for depth in range(extrude_depth, 0, -1):
            t = depth / extrude_depth
            alpha = int(180 * t)
            c = (extrude_color[0], extrude_color[1], extrude_color[2], alpha)
            draw.text((x + depth, y + depth), text, font=font, fill=c, anchor=anchor)

        # Thick stroke ring (outer glow)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx == 0 and dy == 0:
                    continue
                if abs(dx) + abs(dy) <= 4:
                    draw.text((x + dx, y + dy), text, font=font,
                              fill=(stroke_color[0], stroke_color[1], stroke_color[2], 200),
                              anchor=anchor)

        # Face text on top
        draw.text((x, y), text, font=font, fill=face_color, anchor=anchor)

    # ------------------------------------------------------------------
    # LAYOUT RENDERERS
    # ------------------------------------------------------------------
    def _render_center_hero(self, img, plan, draw, w, h, channel_name, rng, mode):
        p = plan.palette
        cx, cy = w // 2, h // 2

        # Neon bloom behind emblem
        self._draw_neon_bloom(img, cx, cy, plan.traits.aura_family, int(h * 0.38), rng)

        # Emblem
        draw2 = ImageDraw.Draw(img, "RGBA")
        self._draw_emblem(draw2, cx, cy, plan.traits.emblem_shape, p, rng, size=int(min(w, h) * 0.22))

        # 3D Title
        font_title = get_system_font("impact.ttf", int(h * 0.13))
        font_sub   = get_system_font("arialbd.ttf", int(h * 0.045))
        face   = p.text_main
        stroke = p.neon_primary
        extrude = (_clamp(stroke[0] - 80), _clamp(stroke[1] - 80), _clamp(stroke[2] - 80), 255)

        title = channel_name.upper()
        self._draw_3d_text(draw2, cx, cy - int(h * 0.03), title, font_title,
                           face, stroke, extrude, extrude_depth=12)

        # Sub-line
        sub_texts = {"banner": "CANLI YAYINDA", "webcam": "CAM ÇERÇEVE", "chat": "SOHBET",
                     "ticker": "ETKİNLİK AKIŞI", "starting": "BAŞLIYOR"}
        sub_text = sub_texts.get(mode, channel_name)
        draw2.text((cx, cy + int(h * 0.10)), sub_text, font=font_sub,
                   fill=(p.neon_secondary[0], p.neon_secondary[1], p.neon_secondary[2], 220),
                   anchor="mm")

        # Horizontal accent lines
        line_y1 = cy + int(h * 0.16)
        lw = int(w * 0.35)
        draw2.line([(cx - lw, line_y1), (cx + lw, line_y1)], fill=p.neon_primary, width=3)
        draw2.line([(cx - lw + 20, line_y1 + 6), (cx + lw - 20, line_y1 + 6)],
                   fill=(p.neon_primary[0], p.neon_primary[1], p.neon_primary[2], 100), width=1)

    def _render_left_wedge(self, img, plan, draw, w, h, channel_name, rng, mode):
        p = plan.palette
        draw2 = ImageDraw.Draw(img, "RGBA")

        # Left aggressive wedge panel
        panel_pts = [
            (0, 0), (int(w * 0.55), 0),
            (int(w * 0.45), h), (0, h)
        ]
        c = p.neon_primary
        draw2.polygon(panel_pts, fill=(c[0], c[1], c[2], 22))
        draw2.polygon(panel_pts, outline=(c[0], c[1], c[2], 160))

        # Bloom on left
        self._draw_neon_bloom(img, int(w * 0.25), h // 2, plan.traits.aura_family, int(h * 0.32), rng)

        # Emblem left center
        self._draw_emblem(draw2, int(w * 0.25), h // 2, plan.traits.emblem_shape, p, rng, size=int(min(w, h) * 0.18))

        # Title — large, left-anchored
        font_title = get_system_font("impact.ttf", int(h * 0.12))
        font_sub   = get_system_font("arialbd.ttf", int(h * 0.04))
        face   = p.text_main
        stroke = p.neon_primary
        extrude = (_clamp(stroke[0] - 80), _clamp(stroke[1] - 80), _clamp(stroke[2] - 80), 255)

        tx = int(w * 0.62)
        self._draw_3d_text(draw2, tx, h // 2 - int(h * 0.07), channel_name.upper(),
                           font_title, face, stroke, extrude, extrude_depth=10, anchor="lm")
        draw2.text((tx, h // 2 + int(h * 0.07)), mode.upper(), font=font_sub,
                   fill=(p.neon_secondary[0], p.neon_secondary[1], p.neon_secondary[2], 200),
                   anchor="lm")

        # Slash accent
        draw2.line([(tx, h // 2 + int(h * 0.13)), (tx + int(w * 0.3), h // 2 + int(h * 0.13))],
                   fill=p.neon_primary, width=3)

    def _render_bottom_ribbon(self, img, plan, draw, w, h, channel_name, rng, mode):
        p = plan.palette
        draw2 = ImageDraw.Draw(img, "RGBA")

        # Bloom center-top
        self._draw_neon_bloom(img, w // 2, int(h * 0.38), plan.traits.aura_family, int(h * 0.35), rng)
        self._draw_emblem(draw2, w // 2, int(h * 0.35), plan.traits.emblem_shape, p, rng, size=int(min(w, h) * 0.2))

        # Bottom ribbon bar
        ribbon_y = int(h * 0.72)
        ribbon_h = int(h * 0.2)
        c = p.neon_primary
        draw2.rectangle([0, ribbon_y, w, ribbon_y + ribbon_h],
                        fill=(c[0], c[1], c[2], 35))
        draw2.line([(0, ribbon_y), (w, ribbon_y)], fill=p.neon_primary, width=4)

        # Parallelogram accents inside ribbon
        for i in range(0, w, 60):
            if rng.random() > 0.6:
                pts = [(i, ribbon_y + 4), (i + 40, ribbon_y + 4),
                       (i + 30, ribbon_y + ribbon_h - 4), (i - 10, ribbon_y + ribbon_h - 4)]
                draw2.polygon(pts, fill=(c[0], c[1], c[2], 25))

        # Title in ribbon
        font_title = get_system_font("impact.ttf", int(ribbon_h * 0.6))
        font_sub   = get_system_font("arialbd.ttf", int(ribbon_h * 0.28))
        face   = p.text_main
        stroke = p.neon_primary
        extrude = (_clamp(stroke[0] - 80), _clamp(stroke[1] - 80), _clamp(stroke[2] - 80), 255)

        self._draw_3d_text(draw2, w // 2, ribbon_y + ribbon_h // 2, channel_name.upper(),
                           font_title, face, stroke, extrude, extrude_depth=8, anchor="mm")
        draw2.text((w // 2, ribbon_y + ribbon_h - int(ribbon_h * 0.12)), mode.upper(),
                   font=font_sub,
                   fill=(p.neon_secondary[0], p.neon_secondary[1], p.neon_secondary[2], 180),
                   anchor="mb")

    def _render_full_bleed_hud(self, img, plan, draw, w, h, channel_name, rng, mode):
        p = plan.palette
        draw2 = ImageDraw.Draw(img, "RGBA")

        # HUD grid lines
        for i in range(1, 4):
            y = h * i // 4
            x = w * i // 4
            alpha = rng.randint(15, 40)
            c = p.neon_primary
            draw2.line([(0, y), (w, y)], fill=(c[0], c[1], c[2], alpha), width=1)
            draw2.line([(x, 0), (x, h)], fill=(c[0], c[1], c[2], alpha), width=1)

        # Corner HUD brackets
        blen = 50
        bthick = 3
        corners = [(0, 0), (w - blen, 0), (0, h - blen), (w - blen, h - blen)]
        c = p.neon_primary
        for (bx, by) in corners:
            sx = 1 if bx == 0 else -1
            sy = 1 if by == 0 else -1
            draw2.line([(bx, by), (bx + sx * blen, by)], fill=c, width=bthick)
            draw2.line([(bx, by), (bx, by + sy * blen)], fill=c, width=bthick)

        # Bloom
        self._draw_neon_bloom(img, w // 2, h // 2, plan.traits.aura_family, int(h * 0.3), rng)
        self._draw_emblem(draw2, w // 2, h // 2, plan.traits.emblem_shape, p, rng, size=int(min(w, h) * 0.17))

        # Title
        font_title = get_system_font("consola.ttf", int(h * 0.1))
        font_sub   = get_system_font("consola.ttf", int(h * 0.035))
        face   = p.neon_primary
        stroke = p.neon_secondary
        extrude = (_clamp(stroke[0] - 80), _clamp(stroke[1] - 80), _clamp(stroke[2] - 80), 255)

        self._draw_3d_text(draw2, w // 2, h // 2 - int(h * 0.06),
                           f"// {channel_name.upper()} //",
                           font_title, face, stroke, extrude, extrude_depth=6, anchor="mm")
        draw2.text((w // 2, h // 2 + int(h * 0.09)), f"[ {mode.upper()} ]",
                   font=font_sub,
                   fill=(p.neon_secondary[0], p.neon_secondary[1], p.neon_secondary[2], 200),
                   anchor="mm")

    def _render_asymmetric_tilt(self, img, plan, draw, w, h, channel_name, rng, mode):
        p = plan.palette
        draw2 = ImageDraw.Draw(img, "RGBA")
        c = p.neon_primary

        # Diagonal slash divider
        slash_x = int(w * 0.52)
        tilt = int(h * 0.12)
        pts_left = [(0, 0), (slash_x + tilt, 0), (slash_x - tilt, h), (0, h)]
        draw2.polygon(pts_left, fill=(c[0], c[1], c[2], 20))
        draw2.line([(slash_x + tilt, 0), (slash_x - tilt, h)], fill=c, width=4)
        draw2.line([(slash_x + tilt - 12, 0), (slash_x - tilt - 12, h)],
                   fill=(c[0], c[1], c[2], 80), width=2)

        # Bloom left side
        self._draw_neon_bloom(img, int(w * 0.28), h // 2, plan.traits.aura_family, int(h * 0.3), rng)
        self._draw_emblem(draw2, int(w * 0.28), h // 2, plan.traits.emblem_shape, p, rng, size=int(min(w, h) * 0.19))

        # Right side text
        font_title = get_system_font("impact.ttf", int(h * 0.11))
        font_sub   = get_system_font("arialbd.ttf", int(h * 0.04))
        face   = p.text_main
        stroke = p.neon_primary
        extrude = (_clamp(stroke[0] - 80), _clamp(stroke[1] - 80), _clamp(stroke[2] - 80), 255)

        rx = int(w * 0.72)
        self._draw_3d_text(draw2, rx, h // 2 - int(h * 0.06),
                           channel_name.upper(), font_title, face, stroke, extrude,
                           extrude_depth=10, anchor="mm")
        draw2.text((rx, h // 2 + int(h * 0.08)), mode.upper(), font=font_sub,
                   fill=(p.neon_secondary[0], p.neon_secondary[1], p.neon_secondary[2], 200),
                   anchor="mm")

    # ------------------------------------------------------------------
    # BORDER / FRAME DEKORASYONLARI
    # ------------------------------------------------------------------
    def _draw_border_decoration(self, draw, w, h, palette: ColorPalette, plan: MasterDesignPlan, rng: random.Random):
        c = palette.neon_primary
        c2 = palette.neon_secondary

        # Outer neon border
        draw.rectangle([3, 3, w - 4, h - 4], outline=(c[0], c[1], c[2], 180), width=3)
        draw.rectangle([8, 8, w - 9, h - 9], outline=(c[0], c[1], c[2], 80), width=1)

        # Hazard stripes on corners
        stripe_len = int(min(w, h) * 0.06)
        stripe_colors = [(c[0], c[1], c[2], 120), (0, 0, 0, 0)]
        for corner_x, corner_y, dx, dy in [(0, 0, 1, 1), (w, 0, -1, 1), (0, h, 1, -1), (w, h, -1, -1)]:
            for i in range(6):
                sx = corner_x + dx * i * stripe_len // 3
                sy = corner_y + dy * i * stripe_len // 3
                col = stripe_colors[i % 2]
                draw.line([(sx, sy), (sx + dx * stripe_len, sy + dy * stripe_len // 4)],
                          fill=col, width=stripe_len // 8)

        # Bottom accent bar
        bar_h = max(4, int(h * 0.007))
        draw.rectangle([0, h - bar_h, w, h], fill=palette.neon_primary)

    # ------------------------------------------------------------------
    # ANA RENDER PIPELINE
    # ------------------------------------------------------------------
    def render(
        self,
        channel_name: str,
        plan: MasterDesignPlan,
        mode: str,
        size: Tuple[int, int],
        output_path: str,
    ) -> str:
        rng = random.Random(plan.seed + hash(mode) % 10000)
        w, h = size

        img  = Image.new("RGBA", (w, h), (0, 0, 0, 255))

        # Layer 1: Background + Texture
        self._draw_background(img, plan, rng)

        draw = ImageDraw.Draw(img, "RGBA")

        # Layer 2–4: Layout (includes bloom, emblem, 3D text)
        layout = plan.traits.layout
        if layout == "center_hero":
            self._render_center_hero(img, plan, draw, w, h, channel_name, rng, mode)
        elif layout == "left_wedge":
            self._render_left_wedge(img, plan, draw, w, h, channel_name, rng, mode)
        elif layout == "bottom_ribbon":
            self._render_bottom_ribbon(img, plan, draw, w, h, channel_name, rng, mode)
        elif layout == "full_bleed_hud":
            self._render_full_bleed_hud(img, plan, draw, w, h, channel_name, rng, mode)
        elif layout == "asymmetric_tilt":
            self._render_asymmetric_tilt(img, plan, draw, w, h, channel_name, rng, mode)
        else:
            self._render_center_hero(img, plan, draw, w, h, channel_name, rng, mode)

        # Layer 5: Border decorations
        draw3 = ImageDraw.Draw(img, "RGBA")
        self._draw_border_decoration(draw3, w, h, plan.palette, plan, rng)

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        return output_path


# Global singleton
_factory = EsportsDesignFactory()


# ==============================================================================
# 7. PUBLIC API (main.py ile uyumlu)
# ==============================================================================

def generate_channel_banner(
    channel_name: str,
    plan: MasterDesignPlan,
    mode: str = "banner",
    custom_title: Optional[str] = None,
) -> str:
    name = custom_title if custom_title else channel_name
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out = os.path.join(assets_dir, f"{safe}_banner_{plan.design_id}.png")
    return _factory.render(name, plan, mode, (1920, 1080), out)


def generate_webcam_overlay(channel_name: str, plan: MasterDesignPlan) -> str:
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out = os.path.join(assets_dir, f"{safe}_webcam_{plan.design_id}.png")
    return _factory.render(channel_name, plan, "webcam", (640, 480), out)


def generate_chat_overlay(channel_name: str, plan: MasterDesignPlan) -> str:
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out = os.path.join(assets_dir, f"{safe}_chat_{plan.design_id}.png")
    return _factory.render(channel_name, plan, "chat", (420, 600), out)


def generate_event_ticker(channel_name: str, plan: MasterDesignPlan) -> str:
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out = os.path.join(assets_dir, f"{safe}_ticker_{plan.design_id}.png")
    return _factory.render(channel_name, plan, "ticker", (1920, 120), out)


def _generate_starting_soon(channel_name: str, plan: MasterDesignPlan) -> str:
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out = os.path.join(assets_dir, f"{safe}_starting_{plan.design_id}.png")
    return _factory.render(channel_name, plan, "starting", (1920, 1080), out)


def _generate_brb(channel_name: str, plan: MasterDesignPlan) -> str:
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out = os.path.join(assets_dir, f"{safe}_brb_{plan.design_id}.png")
    return _factory.render(channel_name, plan, "AZ SONRA DÖNÜYORUM", (1920, 1080), out)


def build_ai_scene_collection(
    channel_name: str,
    theme_name: str,
    collection_name: str,
    custom_color_query: str = "",
) -> dict:
    """
    Tam AI sahne koleksiyonu oluşturur.
    Returns: {success, collection_name, filepath, plan, assets: {6 paths}}
    """
    try:
        plan = _factory.generate_plan(
            requested_trend=theme_name,
            query=custom_color_query,
            preset_name=theme_name,
        )

        assets = {}
        assets["banner"]   = generate_channel_banner(channel_name, plan, "banner")
        assets["webcam"]   = generate_webcam_overlay(channel_name, plan)
        assets["chat"]     = generate_chat_overlay(channel_name, plan)
        assets["ticker"]   = generate_event_ticker(channel_name, plan)
        assets["starting"] = _generate_starting_soon(channel_name, plan)
        assets["brb"]      = _generate_brb(channel_name, plan)

        # OBS Scene Collection JSON
        safe_col = re.sub(r"[^\w\s\-]", "", collection_name)[:50]
        obs_scenes_dir = os.path.join(
            os.environ.get("APPDATA", ""), "obs-studio", "basic", "scenes"
        )
        os.makedirs(obs_scenes_dir, exist_ok=True)
        safe_file = re.sub(r"[^\w\-]", "_", safe_col)
        scene_path = os.path.join(obs_scenes_dir, f"{safe_file}.json")

        obs_json = _build_obs_scene_json(collection_name, channel_name, assets, plan)
        with open(scene_path, "w", encoding="utf-8") as f:
            json.dump(obs_json, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "collection_name": collection_name,
            "filepath": scene_path,
            "plan": {
                "design_id": plan.design_id,
                "trend": plan.trend.value,
                "skeleton": plan.skeleton.value,
                "palette": plan.palette.name,
                "traits": {
                    "texture": plan.traits.texture_type,
                    "emblem":  plan.traits.emblem_shape,
                    "typo":    plan.traits.typo_style,
                    "aura":    plan.traits.aura_family,
                    "layout":  plan.traits.layout,
                },
                "seed": plan.seed,
            },
            "assets": assets,
        }
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def _build_obs_scene_json(collection_name, channel_name, assets, plan) -> dict:
    """OBS sahneleri için JSON yapısı oluşturur."""
    def make_source(name, path, x=0, y=0, w=1920, h=1080):
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "type": "image_source",
            "settings": {"file": path, "unload": False},
            "pos": {"x": x, "y": y},
            "bounds": {"x": w, "y": h, "type": "OBS_BOUNDS_SCALE_INNER"},
            "scale": {"x": 1.0, "y": 1.0},
        }

    scenes = [
        {"id": str(uuid.uuid4()), "name": f"🎮 1 - {channel_name} CANLI",    "sources": [make_source("Banner", assets["banner"]), make_source("Ticker", assets["ticker"], y=960, h=120), make_source("Chat", assets["chat"], x=1500, w=420, h=600), make_source("Webcam Frame", assets["webcam"], x=30, y=30, w=640, h=480)]},
        {"id": str(uuid.uuid4()), "name": f"💬 2 - Sohbet Sahnesi",           "sources": [make_source("Banner", assets["banner"]), make_source("Chat Full", assets["chat"], x=750, w=420, h=600)]},
        {"id": str(uuid.uuid4()), "name": f"⏳ 3 - Az Sonra Başlıyor",        "sources": [make_source("Starting", assets["starting"])]},
        {"id": str(uuid.uuid4()), "name": f"☕ 4 - Az Sonra Dönüyorum",       "sources": [make_source("BRB", assets["brb"])]},
        {"id": str(uuid.uuid4()), "name": f"👋 5 - Kapanış",                  "sources": [make_source("Banner", assets["banner"])]},
    ]
    return {
        "name": collection_name,
        "ripleytia_studio": True,
        "version": "1.5.0",
        "design_id": plan.design_id,
        "trend": plan.trend.value,
        "scenes": scenes,
    }


# ==============================================================================
# 8. AI STREAM STRATEJİSİ (Değişmedi)
# ==============================================================================

def generate_ai_stream_strategy(
    channel_name: str,
    game_type: str,
    style: str,
    api_key: str = "",
) -> dict:
    """Basit kural tabanlı yayın stratejisi üretici (API bağımsız)."""
    tips = {
        "fps": ["Ses kalitesine öncelik ver.", "Clip sistemi kur.", "Turnuvalara katıl."],
        "rpg": ["Lore yorum bölümleri ekle.", "Karakter build rehberleri yayınla.", "Viewer kararlarına izin ver."],
        "moba": ["Maç analizi yap.", "Draft açıkla.", "Takım oluşturmayı göster."],
    }
    game_key = game_type.lower().split()[0] if game_type else "fps"
    selected_tips = tips.get(game_key, tips["fps"])

    return {
        "channel": channel_name,
        "game": game_type,
        "style": style,
        "strategy": selected_tips,
        "schedule": "Hafta içi 20:00–23:00, Hafta sonu 15:00–22:00",
        "growth_tip": "İlk 90 günde tutarlılık büyümenin %70'ini belirler.",
    }
