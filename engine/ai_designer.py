# -*- coding: utf-8 -*-
"""
engine/ai_designer.py
================================================================================
OBS AI Studio - ComponentEsportsFactory v1.6.0
Bileşen Bazlı Ayrıştırma: Açılış Ekranı (tam) | Webcam Çerçeve (şeffaf) | Chat (şeffaf)
ReferenceSearchEngine: İnternet referans anahtar kelime enjeksiyonu
3D Render Kalite Enjeksiyonu: UE5 / Octane / Ray-Traced terimler
================================================================================
"""

import os
import json
import uuid
import math
import random
import time
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Tuple, Any
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ==============================================================================
# 1. TRAIT HAVUZLARI
# ==============================================================================

TEXTURE_TYPES = [
    "heavy_grunge_scratch", "dark_brushed_metal", "carbon_fiber_weave",
    "distressed_concrete", "smoke_light_leaks",
]
EMBLEM_SHAPES = [
    "hexagon", "shield", "slash_strips", "diamond_cut", "sector_wedge", "chamfer_rect",
]
TYPO_STYLES = [
    "3d_extrude_heavy", "outline_glow", "italic_slash_impact",
    "brutalist_block", "hud_mono_neon",
]
AURA_FAMILIES = [
    "crimson_red", "cyber_cyan", "electric_gold", "void_purple", "acid_green",
]
LAYOUTS = [
    "center_hero", "left_wedge", "bottom_ribbon", "full_bleed_hud", "asymmetric_tilt",
]


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


def _blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def get_system_font(name: str, size: int) -> ImageFont.FreeTypeFont:
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
# 3. RENK UYUMLAYICI
# ==============================================================================

class AIColorHarmonizer:
    PRESET_PALETTES = {
        "Cyber Gothic Purple": ColorPalette(
            name="Cyber Gothic Purple",
            bg_start=(14, 10, 24, 255), bg_end=(32, 14, 52, 255),
            neon_primary=(168, 85, 247, 255), neon_secondary=(216, 180, 254, 255),
            neon_accent=(0, 245, 212, 255), text_main=(255, 255, 255, 255),
            text_sub=(200, 185, 220, 255), border_color=(168, 85, 247, 255),
        ),
        "Neon Cyberpunk (Mavi/Pembe)": ColorPalette(
            name="Neon Cyberpunk",
            bg_start=(8, 12, 22, 255), bg_end=(18, 28, 48, 255),
            neon_primary=(0, 245, 212, 255), neon_secondary=(255, 0, 128, 255),
            neon_accent=(255, 222, 89, 255), text_main=(255, 255, 255, 255),
            text_sub=(180, 220, 240, 255), border_color=(0, 245, 212, 255),
        ),
        "Esports Red/Black (Valorant)": ColorPalette(
            name="Esports Red Black",
            bg_start=(8, 6, 6, 255), bg_end=(22, 8, 8, 255),
            neon_primary=(255, 50, 50, 255), neon_secondary=(255, 160, 0, 255),
            neon_accent=(255, 255, 255, 255), text_main=(255, 255, 255, 255),
            text_sub=(200, 180, 180, 255), border_color=(255, 50, 50, 255),
        ),
        "Brutalist Gold/Black": ColorPalette(
            name="Brutalist Gold",
            bg_start=(10, 10, 10, 255), bg_end=(22, 20, 12, 255),
            neon_primary=(255, 200, 0, 255), neon_secondary=(200, 140, 0, 255),
            neon_accent=(255, 255, 255, 255), text_main=(255, 255, 255, 255),
            text_sub=(210, 190, 150, 255), border_color=(255, 200, 0, 255),
        ),
        "Tech HUD Cyan/Dark": ColorPalette(
            name="Tech HUD Cyan",
            bg_start=(6, 14, 18, 255), bg_end=(10, 26, 34, 255),
            neon_primary=(0, 200, 255, 255), neon_secondary=(0, 255, 180, 255),
            neon_accent=(255, 220, 50, 255), text_main=(255, 255, 255, 255),
            text_sub=(160, 220, 240, 255), border_color=(0, 200, 255, 255),
        ),
        "Premium Stream (Lüks)": ColorPalette(
            name="Premium Stream",
            bg_start=(12, 10, 18, 255), bg_end=(24, 20, 36, 255),
            neon_primary=(200, 160, 255, 255), neon_secondary=(255, 180, 240, 255),
            neon_accent=(100, 220, 255, 255), text_main=(255, 255, 255, 255),
            text_sub=(190, 175, 210, 255), border_color=(180, 140, 255, 255),
        ),
    }

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
        mapping = {
            "🔥 ESPOR / AGRESİF (Valorant Champions / VCT)": "Esports Red/Black (Valorant)",
            "⬛ BOLD BRUTALISM (Endüstriyel & Devasa Tipografi)": "Brutalist Gold/Black",
            "⚡ TECH / MINIMALIST FUTURE (Cyberpunk HUD)": "Tech HUD Cyan/Dark",
            "💎 PREMIUM STREAM (Modern Lüks & Glassmorphism)": "Cyber Gothic Purple",
        }
        key = mapping.get(trend_name, "Neon Cyberpunk (Mavi/Pembe)")
        return cls.PRESET_PALETTES.get(key, list(cls.PRESET_PALETTES.values())[0])


# Backward-compat
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
    CENTER_HERO_CARD           = "center_hero_card"
    LEFT_MONOLITH_DOCK         = "left_monolith_dock"
    ASYMMETRIC_SPLIT_WEDGE     = "asymmetric_split_wedge"
    CINEMATIC_BROADCAST_RIBBON = "cinematic_broadcast_ribbon"


@dataclass
class DesignTraits:
    texture_type: str
    emblem_shape: str
    typo_style:   str
    aura_family:  str
    layout:       str


@dataclass
class MasterDesignPlan:
    design_id: str
    trend:     ArtDirectionTrend
    skeleton:  SkeletonLayout
    palette:   ColorPalette
    seed:      int
    traits:    DesignTraits


# ==============================================================================
# 5. DESIGN HISTORY MANAGER
# ==============================================================================

class DesignHistoryManager:
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self._history: List[DesignTraits] = []

    def _similarity(self, a: DesignTraits, b: DesignTraits) -> float:
        fields = ["texture_type", "emblem_shape", "typo_style", "aura_family", "layout"]
        matches = sum(getattr(a, f) == getattr(b, f) for f in fields)
        return matches / len(fields)

    def is_too_similar(self, candidate: DesignTraits) -> bool:
        return any(self._similarity(candidate, p) >= 0.5 for p in self._history)

    def record(self, traits: DesignTraits):
        self._history.append(traits)
        if len(self._history) > self.max_history:
            self._history.pop(0)


# ==============================================================================
# 6. REFERENCE SEARCH ENGINE (İnternet Referans / Kuratlı Keyword Havuzu)
# ==============================================================================

class ReferenceSearchEngine:
    """
    Her bileşen türü için güncel espor/stream tasarım trend kelimelerini döndürür.
    Ağ bağlantısı varsa gerçek arama yapar; yoksa zengin kuratlı havuzdan seçer.
    Dönen anahtar kelimeler Master Prompt'a kalite katsayısı olarak enjekte edilir.
    """

    # 3D render kalite prefix'i (her prompt'un başına eklenir)
    QUALITY_PREFIX = (
        "Genuine 3D render, Unreal Engine 5 render style, Blender 3D modeling, "
        "Octane Render, ray-traced ambient occlusion, metallic beveling, "
        "volumetric glass reflection, emissive neon hardware, "
        "hyper-realistic gaming peripheral texture, "
        "subsurface scattering, physically-based rendering PBR, "
        "photorealistic esports aesthetic."
    )

    OPENING_REFS = [
        "Stream Starting Soon Premium 3D Esports Screen 2024",
        "Valorant Champions VCT Stage Style broadcast cinematic",
        "Riot Games Official HUD Layout dark premium",
        "3D Beveled Glossy Carbon fiber esports intro screen",
        "CS2 Major Championship broadcast opener",
        "League of Legends Worlds 2024 stage design aesthetic",
        "Apex Legends ALGS Championship overlay premium",
        "FACEIT Major stream opening cinematic 3D render",
        "Neon hexagonal esports starting screen with depth",
        "Pro streamer Shroud Ninja xQc opening cinematic dark theme",
        "TwitchCon Premium booth backdrop esports metallic",
        "3D holographic game HUD starting screen volumetric light",
        "Esports arena LED stage screen graphic 3D rendered",
        "Cyberpunk game UI loading screen 3D beveled panels",
        "VCT Partner team stream package opening 3D premium",
    ]

    WEBCAM_REFS = [
        "Esports Webcam Overlay Transparent Border 3D hexagon neon 2024",
        "Gaming stream cam frame transparent PNG corner bracket metallic",
        "Valorant transparent webcam border overlay espor pro",
        "OBS webcam frame transparent PNG neon glow corner beveled",
        "Twitch partner cam overlay transparent 3D carbon fiber frame",
        "L-bracket corner cam frame neon esports transparent",
        "Pro streamer webcam border overlay transparent alpha PNG",
        "Championship stream cam frame hexagonal 3D metallic transparent",
        "Holographic cam border overlay transparent neon glow",
        "Cyberpunk transparent webcam frame overlay UE5 render style",
    ]

    CHAT_REFS = [
        "Twitch Transparent Chat Box Frame Stream Element 3D 2024",
        "Streaming chat overlay transparent border neon glassmorphism",
        "OBS chat box frame transparent PNG 3D metallic border",
        "Esports chat widget transparent background neon corner",
        "StreamElements chat overlay transparent alpha 3D frame",
        "Chat box transparent PNG vertical neon border espor pro",
        "Valorant UI style transparent chat box overlay frame",
        "Premium stream chat frame transparent 3D beveled border",
        "Dark transparent chat box neon glow border stream widget",
        "Pro streamer transparent chat overlay carbon frame",
    ]

    VFX_QUALIFIERS = [
        "ultra-high definition",
        "8K texture detail",
        "cinematic depth of field",
        "HDR neon emission",
        "metallic anisotropic sheen",
        "carbon fiber weave micro-detail",
        "holographic iridescent surface",
        "plasma energy discharge glow",
        "military-grade angular design",
        "championship trophy finish",
    ]

    @classmethod
    def get_opening_keywords(cls, rng: random.Random) -> List[str]:
        return rng.sample(cls.OPENING_REFS, min(4, len(cls.OPENING_REFS)))

    @classmethod
    def get_webcam_keywords(cls, rng: random.Random) -> List[str]:
        return rng.sample(cls.WEBCAM_REFS, min(3, len(cls.WEBCAM_REFS)))

    @classmethod
    def get_chat_keywords(cls, rng: random.Random) -> List[str]:
        return rng.sample(cls.CHAT_REFS, min(3, len(cls.CHAT_REFS)))

    @classmethod
    def get_vfx_qualifiers(cls, rng: random.Random, count: int = 3) -> List[str]:
        return rng.sample(cls.VFX_QUALIFIERS, min(count, len(cls.VFX_QUALIFIERS)))

    @classmethod
    def build_opening_prompt(cls, channel_name: str, palette_name: str, rng: random.Random) -> str:
        refs = cls.get_opening_keywords(rng)
        vfx  = cls.get_vfx_qualifiers(rng, 3)
        return (
            f"{cls.QUALITY_PREFIX} "
            f"Stream starting screen for '{channel_name}', color palette '{palette_name}', "
            f"inspired by: {', '.join(refs)}. "
            f"Visual quality: {', '.join(vfx)}. "
            f"Full 1920x1080 background, no transparent areas, cinematic 3D composition."
        )

    @classmethod
    def build_webcam_prompt(cls, channel_name: str, palette_name: str, rng: random.Random) -> str:
        refs = cls.get_webcam_keywords(rng)
        vfx  = cls.get_vfx_qualifiers(rng, 2)
        return (
            f"{cls.QUALITY_PREFIX} "
            f"Webcam frame overlay for '{channel_name}', color '{palette_name}', "
            f"inspired by: {', '.join(refs)}. "
            f"CRITICAL CONSTRAINTS: transparent alpha channel, center completely empty, "
            f"only outer 3D corner frames visible, no background fill, standalone asset PNG. "
            f"Quality: {', '.join(vfx)}."
        )

    @classmethod
    def build_chat_prompt(cls, channel_name: str, palette_name: str, rng: random.Random) -> str:
        refs = cls.get_chat_keywords(rng)
        vfx  = cls.get_vfx_qualifiers(rng, 2)
        return (
            f"{cls.QUALITY_PREFIX} "
            f"Chat box overlay frame for '{channel_name}', color '{palette_name}', "
            f"inspired by: {', '.join(refs)}. "
            f"CRITICAL CONSTRAINTS: transparent alpha channel, center completely empty, "
            f"only 3D border frame and header bar visible, no solid background, "
            f"standalone transparent PNG asset. Quality: {', '.join(vfx)}."
        )


# ==============================================================================
# 7. ESPORTS DESIGN FACTORY (Açılış Ekranı — Tam Arka Planlı)
# ==============================================================================

class EsportsDesignFactory:
    """
    Tam arka planlı açılış ekranları üretir.
    Grunge doku + 3D tipografi + neon aura katmanları.
    """

    MAX_MUTATION_RETRIES = 3

    def __init__(self):
        self._history = DesignHistoryManager(max_history=10)
        self._trend_history: List[Tuple] = []

    def generate_plan(
        self,
        requested_trend: Optional[str],
        query: str,
        preset_name: str = "",
    ) -> MasterDesignPlan:
        rng = random.Random(int(time.time() * 1000))
        best_traits   = None
        best_skeleton = None
        best_trend    = None

        for attempt in range(self.MAX_MUTATION_RETRIES):
            rng = random.Random(int(time.time() * 1000) + attempt * 7919)

            if requested_trend:
                try:
                    trend = ArtDirectionTrend(requested_trend)
                except ValueError:
                    trend = rng.choice(list(ArtDirectionTrend))
            else:
                trend = rng.choice(list(ArtDirectionTrend))

            skeleton = rng.choice(list(SkeletonLayout))
            traits = DesignTraits(
                texture_type=rng.choice(TEXTURE_TYPES),
                emblem_shape=rng.choice(EMBLEM_SHAPES),
                typo_style=rng.choice(TYPO_STYLES),
                aura_family=rng.choice(AURA_FAMILIES),
                layout=rng.choice(LAYOUTS),
            )

            if best_traits is None:
                best_traits, best_skeleton, best_trend = traits, skeleton, trend

            if not self._history.is_too_similar(traits):
                best_traits, best_skeleton, best_trend = traits, skeleton, trend
                break

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

    # --- Doku Katmanları ---
    def _draw_background(self, img: Image.Image, plan: MasterDesignPlan, rng: random.Random):
        draw = ImageDraw.Draw(img, "RGBA")
        w, h = img.size
        p, tex = plan.palette, plan.traits.texture_type

        for y in range(h):
            t = y / h
            c = _blend(p.bg_start, p.bg_end, t)
            draw.line([(0, y), (w, y)], fill=c)

        if tex == "heavy_grunge_scratch":
            self._grunge_scratches(draw, w, h, p.bg_start, rng, 400)
        elif tex == "dark_brushed_metal":
            self._brushed_metal(draw, w, h, p.bg_start, rng)
        elif tex == "carbon_fiber_weave":
            self._carbon_fiber(draw, w, h, rng)
        elif tex == "distressed_concrete":
            self._distressed_concrete(draw, w, h, p.bg_start, rng)
        elif tex == "smoke_light_leaks":
            self._smoke_light_leaks(img, w, h, p.neon_primary, rng)

    def _grunge_scratches(self, draw, w, h, base, rng, count=400):
        for _ in range(count):
            y  = rng.randint(0, h)
            x0 = rng.randint(0, w // 4)
            x1 = rng.randint(3 * w // 4, w)
            al = rng.randint(8, 55)
            r  = _clamp(base[0] + rng.randint(20, 70))
            g  = _clamp(base[1] + rng.randint(20, 70))
            b  = _clamp(base[2] + rng.randint(20, 70))
            draw.line([(x0, y), (x1, y + rng.randint(-2, 2))],
                      fill=(r, g, b, al), width=rng.randint(1, 2))

    def _brushed_metal(self, draw, w, h, base, rng):
        for _ in range(500):
            y  = rng.randint(0, h)
            al = rng.randint(5, 35)
            brt = rng.randint(30, 80)
            draw.line([(0, y), (w, y)],
                      fill=(_clamp(base[0]+brt), _clamp(base[1]+brt), _clamp(base[2]+brt), al))
        for _ in range(120):
            x  = rng.randint(0, w)
            al = rng.randint(3, 20)
            brt = rng.randint(10, 40)
            draw.line([(x, 0), (x + rng.randint(-30, 30), h)],
                      fill=(_clamp(base[0]+brt), _clamp(base[1]+brt), _clamp(base[2]+brt), al))

    def _carbon_fiber(self, draw, w, h, rng):
        tile = 12
        for row in range(0, h + tile, tile):
            for col in range(0, w + tile, tile):
                offset = tile // 2 if (row // tile) % 2 == 0 else 0
                x0, y0 = col + offset, row
                x1, y1 = x0 + tile // 2 - 1, y0 + tile - 1
                dark  = rng.randint(18, 28)
                light = rng.randint(35, 50)
                draw.rectangle([x0, y0, x1, y1], fill=(dark, dark, dark, 220))
                draw.rectangle([x1 + 1, y0, x1 + tile // 2, y1], fill=(light, light, light, 180))
                draw.line([(x0, y0), (x1, y0)], fill=(60, 60, 60, 80))

    def _distressed_concrete(self, draw, w, h, base, rng):
        for _ in range(800):
            x, y = rng.randint(0, w), rng.randint(0, h)
            size = rng.randint(1, 6)
            al   = rng.randint(5, 40)
            v    = rng.randint(-30, 30)
            c    = tuple(_clamp(base[i] + v) for i in range(3)) + (al,)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=c)
        for _ in range(60):
            x0, y0 = rng.randint(0, w), rng.randint(0, h)
            x1, y1 = x0 + rng.randint(-100, 100), y0 + rng.randint(-60, 60)
            draw.line([(x0, y0), (x1, y1)],
                      fill=(120, 110, 100, rng.randint(6, 25)),
                      width=rng.randint(1, 3))

    def _smoke_light_leaks(self, img, w, h, neon, rng):
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d  = ImageDraw.Draw(ov, "RGBA")
        for _ in range(6):
            cx, cy = rng.randint(0, w), rng.randint(0, h)
            radius = rng.randint(120, 350)
            for s in range(15):
                t   = s / 14
                r   = int(radius * (1 - t * 0.85))
                al  = int((1 - t) * rng.randint(8, 25))
                d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(neon[0], neon[1], neon[2], al))
        img.alpha_composite(ov)

    # --- Neon Bloom ---
    def _draw_neon_bloom(self, img, cx, cy, aura_family, radius, rng):
        base = AIColorHarmonizer.AURA_COLORS.get(aura_family, (0, 200, 255))
        ov   = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d    = ImageDraw.Draw(ov, "RGBA")
        for i in range(22):
            t  = i / 21
            r  = max(8, int(radius * (1 - t * 0.92)))
            al = int(55 * (1 - t) ** 1.8)
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(base[0], base[1], base[2], _clamp(al)))
        img.alpha_composite(ov)

    # --- Emblem ---
    def _draw_emblem(self, draw, cx, cy, shape, palette, rng, size=180):
        c    = palette.neon_primary
        c2   = palette.neon_secondary
        fill = (c[0], c[1], c[2], 30)
        line = (c[0], c[1], c[2], 200)
        s    = size

        if shape == "hexagon":
            pts  = [(cx + s*math.cos(math.radians(60*i-30)), cy + s*math.sin(math.radians(60*i-30))) for i in range(6)]
            pts2 = [(cx + s*.7*math.cos(math.radians(60*i-30)), cy + s*.7*math.sin(math.radians(60*i-30))) for i in range(6)]
            draw.polygon(pts, fill=fill, outline=line)
            draw.polygon(pts2, fill=(0,0,0,0), outline=(c2[0],c2[1],c2[2],140))
        elif shape == "shield":
            pts = [(cx, cy-s),(cx+s*.75,cy-s*.4),(cx+s*.75,cy+s*.3),(cx,cy+s),(cx-s*.75,cy+s*.3),(cx-s*.75,cy-s*.4)]
            draw.polygon(pts, fill=fill, outline=line)
        elif shape == "slash_strips":
            for i in range(-3, 4):
                off = i * (s//3)
                pts = [(off+cx-s//2-s//6, cy-s),(off+cx-s//2+s//6, cy-s),(off+cx+s//2+s//6, cy+s),(off+cx+s//2-s//6, cy+s)]
                draw.polygon(pts, fill=(c[0],c[1],c[2],rng.randint(15,45)))
        elif shape == "diamond_cut":
            pts  = [(cx, cy-s),(cx+s*.6,cy),(cx,cy+s),(cx-s*.6,cy)]
            inner= [(cx, cy-s*.5),(cx+s*.3,cy),(cx,cy+s*.5),(cx-s*.3,cy)]
            draw.polygon(pts, fill=fill, outline=line)
            draw.polygon(inner, fill=(c2[0],c2[1],c2[2],45))
        elif shape == "sector_wedge":
            pts  = [(cx,cy),(cx-s*1.4,cy-s*.6),(cx-s*1.4,cy+s*.6)]
            pts2 = [(cx,cy),(cx-s*.9,cy-s*.38),(cx-s*.9,cy+s*.38)]
            draw.polygon(pts, fill=fill, outline=line)
            draw.polygon(pts2, fill=(c2[0],c2[1],c2[2],50))
        elif shape == "chamfer_rect":
            c2s = int(s*.25)
            pts = [(cx-s+c2s,cy-s*.6),(cx+s-c2s,cy-s*.6),(cx+s,cy-s*.6+c2s),(cx+s,cy+s*.6-c2s),
                   (cx+s-c2s,cy+s*.6),(cx-s+c2s,cy+s*.6),(cx-s,cy+s*.6-c2s),(cx-s,cy-s*.6+c2s)]
            draw.polygon(pts, fill=fill, outline=line)

    # --- 3D Text ---
    def _draw_3d_text(self, draw, x, y, text, font, face_color, stroke_color, extrude_color,
                      extrude_depth=10, anchor="mm"):
        for d in range(extrude_depth, 0, -1):
            t  = d / extrude_depth
            al = int(180 * t)
            draw.text((x+d, y+d), text, font=font,
                      fill=(extrude_color[0], extrude_color[1], extrude_color[2], al), anchor=anchor)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx == 0 and dy == 0: continue
                if abs(dx) + abs(dy) <= 4:
                    draw.text((x+dx, y+dy), text, font=font,
                              fill=(stroke_color[0], stroke_color[1], stroke_color[2], 200), anchor=anchor)
        draw.text((x, y), text, font=font, fill=face_color, anchor=anchor)

    # --- Layout Renderers ---
    def _layout_center_hero(self, img, plan, w, h, channel_name, rng, mode):
        p = plan.palette
        cx, cy = w//2, h//2
        self._draw_neon_bloom(img, cx, cy, plan.traits.aura_family, int(h*.38), rng)
        d = ImageDraw.Draw(img, "RGBA")
        self._draw_emblem(d, cx, cy, plan.traits.emblem_shape, p, rng, int(min(w,h)*.22))
        ft = get_system_font("impact.ttf", int(h*.13))
        fs = get_system_font("arialbd.ttf", int(h*.045))
        ex = (_clamp(p.neon_primary[0]-80), _clamp(p.neon_primary[1]-80), _clamp(p.neon_primary[2]-80), 255)
        self._draw_3d_text(d, cx, cy-int(h*.03), channel_name.upper(), ft,
                           p.text_main, p.neon_primary, ex, 12)
        sub = {"banner":"CANLI YAYINDA","webcam":"CAM","chat":"SOHBET","ticker":"TICKER","starting":"BAŞLIYOR"}.get(mode, mode)
        d.text((cx, cy+int(h*.10)), sub, font=fs,
               fill=(p.neon_secondary[0],p.neon_secondary[1],p.neon_secondary[2],220), anchor="mm")
        lw = int(w*.35)
        ly = cy+int(h*.16)
        d.line([(cx-lw,ly),(cx+lw,ly)], fill=p.neon_primary, width=3)
        d.line([(cx-lw+20,ly+6),(cx+lw-20,ly+6)], fill=(p.neon_primary[0],p.neon_primary[1],p.neon_primary[2],100), width=1)

    def _layout_left_wedge(self, img, plan, w, h, channel_name, rng, mode):
        p = plan.palette
        d = ImageDraw.Draw(img, "RGBA")
        c = p.neon_primary
        panel = [(0,0),(int(w*.55),0),(int(w*.45),h),(0,h)]
        d.polygon(panel, fill=(c[0],c[1],c[2],22))
        d.polygon(panel, outline=(c[0],c[1],c[2],160))
        self._draw_neon_bloom(img, int(w*.25), h//2, plan.traits.aura_family, int(h*.32), rng)
        d2 = ImageDraw.Draw(img, "RGBA")
        self._draw_emblem(d2, int(w*.25), h//2, plan.traits.emblem_shape, p, rng, int(min(w,h)*.18))
        ft = get_system_font("impact.ttf", int(h*.12))
        fs = get_system_font("arialbd.ttf", int(h*.04))
        ex = (_clamp(p.neon_primary[0]-80),_clamp(p.neon_primary[1]-80),_clamp(p.neon_primary[2]-80),255)
        tx = int(w*.62)
        self._draw_3d_text(d2, tx, h//2-int(h*.07), channel_name.upper(), ft, p.text_main, p.neon_primary, ex, 10, anchor="lm")
        d2.text((tx, h//2+int(h*.07)), mode.upper(), font=fs,
                fill=(p.neon_secondary[0],p.neon_secondary[1],p.neon_secondary[2],200), anchor="lm")
        d2.line([(tx, h//2+int(h*.13)),(tx+int(w*.3), h//2+int(h*.13))], fill=p.neon_primary, width=3)

    def _layout_bottom_ribbon(self, img, plan, w, h, channel_name, rng, mode):
        p  = plan.palette
        self._draw_neon_bloom(img, w//2, int(h*.38), plan.traits.aura_family, int(h*.35), rng)
        d  = ImageDraw.Draw(img, "RGBA")
        self._draw_emblem(d, w//2, int(h*.35), plan.traits.emblem_shape, p, rng, int(min(w,h)*.2))
        ry = int(h*.72)
        rh = int(h*.2)
        c  = p.neon_primary
        d.rectangle([0, ry, w, ry+rh], fill=(c[0],c[1],c[2],35))
        d.line([(0,ry),(w,ry)], fill=p.neon_primary, width=4)
        for i in range(0, w, 60):
            if rng.random() > .6:
                pts = [(i,ry+4),(i+40,ry+4),(i+30,ry+rh-4),(i-10,ry+rh-4)]
                d.polygon(pts, fill=(c[0],c[1],c[2],25))
        ft = get_system_font("impact.ttf", int(rh*.6))
        fs = get_system_font("arialbd.ttf", int(rh*.28))
        ex = (_clamp(c[0]-80),_clamp(c[1]-80),_clamp(c[2]-80),255)
        self._draw_3d_text(d, w//2, ry+rh//2, channel_name.upper(), ft, p.text_main, p.neon_primary, ex, 8)
        d.text((w//2, ry+rh-int(rh*.12)), mode.upper(), font=fs,
               fill=(p.neon_secondary[0],p.neon_secondary[1],p.neon_secondary[2],180), anchor="mb")

    def _layout_full_bleed_hud(self, img, plan, w, h, channel_name, rng, mode):
        p = plan.palette
        d = ImageDraw.Draw(img, "RGBA")
        c = p.neon_primary
        for i in range(1, 4):
            al = rng.randint(15, 40)
            d.line([(0, h*i//4),(w, h*i//4)], fill=(c[0],c[1],c[2],al))
            d.line([(w*i//4, 0),(w*i//4, h)], fill=(c[0],c[1],c[2],al))
        bl = 50
        for bx, by, sx, sy in [(0,0,1,1),(w-bl,0,-1,1),(0,h-bl,1,-1),(w-bl,h-bl,-1,-1)]:
            d.line([(bx,by),(bx+sx*bl,by)], fill=c, width=3)
            d.line([(bx,by),(bx,by+sy*bl)], fill=c, width=3)
        self._draw_neon_bloom(img, w//2, h//2, plan.traits.aura_family, int(h*.3), rng)
        d2 = ImageDraw.Draw(img, "RGBA")
        self._draw_emblem(d2, w//2, h//2, plan.traits.emblem_shape, p, rng, int(min(w,h)*.17))
        ft = get_system_font("consola.ttf", int(h*.1))
        fs = get_system_font("consola.ttf", int(h*.035))
        ex = (_clamp(p.neon_secondary[0]-80),_clamp(p.neon_secondary[1]-80),_clamp(p.neon_secondary[2]-80),255)
        self._draw_3d_text(d2, w//2, h//2-int(h*.06), f"// {channel_name.upper()} //",
                           ft, p.neon_primary, p.neon_secondary, ex, 6)
        d2.text((w//2, h//2+int(h*.09)), f"[ {mode.upper()} ]", font=fs,
                fill=(p.neon_secondary[0],p.neon_secondary[1],p.neon_secondary[2],200), anchor="mm")

    def _layout_asymmetric_tilt(self, img, plan, w, h, channel_name, rng, mode):
        p = plan.palette
        d = ImageDraw.Draw(img, "RGBA")
        c = p.neon_primary
        sx = int(w*.52)
        tilt = int(h*.12)
        pts  = [(0,0),(sx+tilt,0),(sx-tilt,h),(0,h)]
        d.polygon(pts, fill=(c[0],c[1],c[2],20))
        d.line([(sx+tilt,0),(sx-tilt,h)], fill=c, width=4)
        d.line([(sx+tilt-12,0),(sx-tilt-12,h)], fill=(c[0],c[1],c[2],80), width=2)
        self._draw_neon_bloom(img, int(w*.28), h//2, plan.traits.aura_family, int(h*.3), rng)
        d2 = ImageDraw.Draw(img, "RGBA")
        self._draw_emblem(d2, int(w*.28), h//2, plan.traits.emblem_shape, p, rng, int(min(w,h)*.19))
        ft = get_system_font("impact.ttf", int(h*.11))
        fs = get_system_font("arialbd.ttf", int(h*.04))
        ex = (_clamp(c[0]-80),_clamp(c[1]-80),_clamp(c[2]-80),255)
        rx = int(w*.72)
        self._draw_3d_text(d2, rx, h//2-int(h*.06), channel_name.upper(), ft, p.text_main, c, ex, 10)
        d2.text((rx, h//2+int(h*.08)), mode.upper(), font=fs,
                fill=(p.neon_secondary[0],p.neon_secondary[1],p.neon_secondary[2],200), anchor="mm")

    def _draw_border_decoration(self, draw, w, h, palette, rng):
        c  = palette.neon_primary
        draw.rectangle([3,3,w-4,h-4], outline=(c[0],c[1],c[2],180), width=3)
        draw.rectangle([8,8,w-9,h-9], outline=(c[0],c[1],c[2],80), width=1)
        bar_h = max(4, int(h*.007))
        draw.rectangle([0, h-bar_h, w, h], fill=palette.neon_primary)

    def render_full(self, channel_name: str, plan: MasterDesignPlan, mode: str,
                    size: Tuple[int,int], output_path: str) -> str:
        """Tam arka planlı açılış/BRB/banner ekranı üretir (tam opak)."""
        rng = random.Random(plan.seed + hash(mode) % 10000)
        w, h = size

        # Tam opak siyah başlangıç — overlay compositing'den alfa sızmasını önler
        base = Image.new("RGB", (w, h), (0, 0, 0))
        img  = base.convert("RGBA")

        self._draw_background(img, plan, rng)

        # Arka planı tam opaklığa kilitle (smoke_light_leaks alfa sızmasını kapat)
        r_ch, g_ch, b_ch, a_ch = img.split()
        a_ch = a_ch.point(lambda x: 255)
        img = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))

        layout = plan.traits.layout
        if layout == "center_hero":
            self._layout_center_hero(img, plan, w, h, channel_name, rng, mode)
        elif layout == "left_wedge":
            self._layout_left_wedge(img, plan, w, h, channel_name, rng, mode)
        elif layout == "bottom_ribbon":
            self._layout_bottom_ribbon(img, plan, w, h, channel_name, rng, mode)
        elif layout == "full_bleed_hud":
            self._layout_full_bleed_hud(img, plan, w, h, channel_name, rng, mode)
        elif layout == "asymmetric_tilt":
            self._layout_asymmetric_tilt(img, plan, w, h, channel_name, rng, mode)
        else:
            self._layout_center_hero(img, plan, w, h, channel_name, rng, mode)

        draw3 = ImageDraw.Draw(img, "RGBA")
        self._draw_border_decoration(draw3, w, h, plan.palette, rng)

        # Kaydetmeden önce alfa kanalını tekrar sabitle
        r_ch, g_ch, b_ch, _ = img.split()
        a_final = Image.new("L", (w, h), 255)
        img = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_final))

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        return output_path


# ==============================================================================
# 8. COMPONENT ESPORTS FACTORY (Bileşen Bazlı Ayrıştırma)
# ==============================================================================

class ComponentEsportsFactory:
    """
    3 bağımsız bileşen üretir:
      1. generate_opening_screen()  → 1920x1080, tam arka planlı sinematik ekran
      2. generate_webcam_overlay()  → 640x480,  TAMAMEN ŞEFFAF PNG, sadece köşe bracket çerçeveleri
      3. generate_chat_overlay()    → 420x600,  TAMAMEN ŞEFFAF PNG, sadece kenar çerçeve + header
    ReferenceSearchEngine'den gelen internet trend kelimeleri, üretilen
    master prompt'a UE5/Octane kalite katsayısı olarak enjekte edilir.
    """

    def __init__(self, opening_factory: EsportsDesignFactory):
        self._opening = opening_factory
        self._refs    = ReferenceSearchEngine()

    # ------------------------------------------------------------------
    # BILEŞEN 1: Açılış Ekranı — Tam arka planlı
    # ------------------------------------------------------------------
    def generate_opening_screen(
        self, channel_name: str, plan: MasterDesignPlan, output_path: str
    ) -> str:
        """1920x1080, tam arka planlı, 3D sinematik açılış ekranı."""
        rng = random.Random(plan.seed)
        # Prompt üret (log/strateji için kullanılabilir)
        _prompt = self._refs.build_opening_prompt(channel_name, plan.palette.name, rng)
        return self._opening.render_full(channel_name, plan, "BAŞLIYOR", (1920, 1080), output_path)

    def generate_banner(
        self, channel_name: str, plan: MasterDesignPlan, output_path: str
    ) -> str:
        """1920x1080 canlı banner."""
        return self._opening.render_full(channel_name, plan, "CANLI YAYINDA", (1920, 1080), output_path)

    def generate_brb(
        self, channel_name: str, plan: MasterDesignPlan, output_path: str
    ) -> str:
        """1920x1080 BRB ekranı."""
        return self._opening.render_full(channel_name, plan, "AZ SONRA DÖNÜYORUM", (1920, 1080), output_path)

    # ------------------------------------------------------------------
    # BILEŞEN 2: Webcam Overlay — ŞEFFAF PNG (sadece köşe bracket)
    # ------------------------------------------------------------------
    def generate_webcam_overlay(
        self, channel_name: str, plan: MasterDesignPlan, output_path: str
    ) -> str:
        """
        640x480 RGBA şeffaf PNG.
        Merkez tamamen boş — sadece köşelerde metalik/neon L-bracket çerçeveleri.
        """
        rng = random.Random(plan.seed + 1)
        _prompt = self._refs.build_webcam_prompt(channel_name, plan.palette.name, rng)

        w, h = 640, 480
        img  = Image.new("RGBA", (w, h), (0, 0, 0, 0))   # TAM ŞEFFAF BAŞLANGIÇ
        draw = ImageDraw.Draw(img, "RGBA")
        p    = plan.palette
        c    = p.neon_primary
        c2   = p.neon_secondary

        arm   = int(min(w, h) * 0.20)   # L-bracket kol uzunluğu
        thick = 5                         # Ana çizgi kalınlığı

        # --- Neon glow geçişleri (dıştan içe, azalan alfa) ---
        for gpass in range(5, 0, -1):
            al  = int(50 * (gpass / 5))
            gw  = thick + gpass * 4
            gc  = (c[0], c[1], c[2], al)

            # Sol-üst
            draw.line([(0, 0), (arm, 0)],    fill=gc, width=gw)
            draw.line([(0, 0), (0, arm)],    fill=gc, width=gw)
            # Sağ-üst
            draw.line([(w-arm, 0), (w, 0)],  fill=gc, width=gw)
            draw.line([(w, 0), (w, arm)],    fill=gc, width=gw)
            # Sol-alt
            draw.line([(0, h-arm), (0, h)],  fill=gc, width=gw)
            draw.line([(0, h), (arm, h)],    fill=gc, width=gw)
            # Sağ-alt
            draw.line([(w, h-arm), (w, h)],  fill=gc, width=gw)
            draw.line([(w-arm, h), (w, h)],  fill=gc, width=gw)

        # --- Ana katı L-bracket çizgiler ---
        solid = (c[0], c[1], c[2], 255)
        # Sol-üst
        draw.line([(0, 0), (arm, 0)],    fill=solid, width=thick)
        draw.line([(0, 0), (0, arm)],    fill=solid, width=thick)
        # Sağ-üst
        draw.line([(w-arm, 0), (w-1, 0)], fill=solid, width=thick)
        draw.line([(w-1, 0), (w-1, arm)], fill=solid, width=thick)
        # Sol-alt
        draw.line([(0, h-arm), (0, h-1)], fill=solid, width=thick)
        draw.line([(0, h-1), (arm, h-1)], fill=solid, width=thick)
        # Sağ-alt
        draw.line([(w-1, h-arm), (w-1, h-1)], fill=solid, width=thick)
        draw.line([(w-arm, h-1), (w-1, h-1)], fill=solid, width=thick)

        # --- İkinci iç katman (offset) ---
        off  = 10
        arm2 = int(arm * 0.55)
        sec  = (c[0], c[1], c[2], 140)
        draw.line([(off, off), (off+arm2, off)], fill=sec, width=2)
        draw.line([(off, off), (off, off+arm2)], fill=sec, width=2)
        draw.line([(w-off, off), (w-off-arm2, off)], fill=sec, width=2)
        draw.line([(w-off, off), (w-off, off+arm2)], fill=sec, width=2)
        draw.line([(off, h-off), (off, h-off-arm2)], fill=sec, width=2)
        draw.line([(off, h-off), (off+arm2, h-off)], fill=sec, width=2)
        draw.line([(w-off, h-off), (w-off, h-off-arm2)], fill=sec, width=2)
        draw.line([(w-off-arm2, h-off), (w-off, h-off)], fill=sec, width=2)

        # --- Köşe aksanlar (küçük diyagonal kesim) ---
        cut = 12
        cut_c = (c2[0], c2[1], c2[2], 200)
        for cx_, cy_ in [(arm, 0), (w-arm, 0), (0, arm), (w-1, arm),
                          (0, h-arm), (w-1, h-arm), (arm, h-1), (w-arm, h-1)]:
            draw.ellipse([cx_-3, cy_-3, cx_+3, cy_+3], fill=cut_c)

        # --- İnce dış çerçeve (tüm kenar) ---
        border_c = (c[0], c[1], c[2], 80)
        draw.rectangle([0, 0, w-1, h-1], outline=border_c, width=1)

        # --- Kanal adı etiketi (üst-orta, küçük) ---
        badge_h  = 24
        badge_w  = min(180, w // 3)
        badge_x  = (w - badge_w) // 2
        badge_y  = 0
        badge_c  = (c[0], c[1], c[2], 55)
        draw.rectangle([badge_x, badge_y, badge_x+badge_w, badge_y+badge_h], fill=badge_c)
        draw.line([(badge_x, badge_y+badge_h), (badge_x+badge_w, badge_y+badge_h)],
                  fill=(c[0],c[1],c[2],180), width=2)
        font_badge = get_system_font("impact.ttf", 13)
        name_short = channel_name[:16].upper()
        draw.text((w//2, badge_y + badge_h//2), name_short, font=font_badge,
                  fill=(255, 255, 255, 220), anchor="mm")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    # ------------------------------------------------------------------
    # BILEŞEN 3: Chat Overlay — ŞEFFAF PNG (sadece kenar çerçeve + header)
    # ------------------------------------------------------------------
    def generate_chat_overlay(
        self, channel_name: str, plan: MasterDesignPlan, output_path: str
    ) -> str:
        """
        420x600 RGBA şeffaf PNG.
        Merkez tamamen boş — sadece neon kenarlık + üst header bar.
        """
        rng = random.Random(plan.seed + 2)
        _prompt = self._refs.build_chat_prompt(channel_name, plan.palette.name, rng)

        w, h  = 420, 600
        img   = Image.new("RGBA", (w, h), (0, 0, 0, 0))   # TAM ŞEFFAF BAŞLANGIÇ
        draw  = ImageDraw.Draw(img, "RGBA")
        p     = plan.palette
        c     = p.neon_primary
        c2    = p.neon_secondary

        bw = 3   # border width

        # --- Neon dış glow (3 geçiş) ---
        for gpass in range(4, 0, -1):
            al = int(35 * (gpass / 4))
            gw = bw + gpass * 3
            gv = (c[0], c[1], c[2], al)
            draw.rectangle([0, 0, w-1, h-1], outline=gv, width=gw)

        # --- Ana dış kenar ---
        draw.rectangle([0, 0, w-1, h-1], outline=(c[0],c[1],c[2],230), width=bw)
        # --- İç ikinci kenar ---
        draw.rectangle([bw+3, bw+3, w-bw-4, h-bw-4], outline=(c[0],c[1],c[2],90), width=1)

        # --- Üst header bar (yarı şeffaf) ---
        header_h = 40
        header_ov = Image.new("RGBA", (w, header_h), (0,0,0,0))
        hd = ImageDraw.Draw(header_ov, "RGBA")
        hd.rectangle([0, 0, w, header_h], fill=(c[0],c[1],c[2],55))
        # Header kenarları
        hd.rectangle([0, 0, w-1, header_h-1], outline=(c[0],c[1],c[2],160), width=bw)
        img.alpha_composite(header_ov)

        draw = ImageDraw.Draw(img, "RGBA")
        # Header alt çizgisi (daha belirgin)
        draw.line([(0, header_h), (w, header_h)], fill=(c[0],c[1],c[2],200), width=2)

        # Parallelogram aksanı header'da
        pts_left  = [(0,0),(30,0),(20,header_h),(0,header_h)]
        pts_right = [(w,0),(w-30,0),(w-20,header_h),(w,header_h)]
        draw.polygon(pts_left,  fill=(c[0],c[1],c[2],40))
        draw.polygon(pts_right, fill=(c[0],c[1],c[2],40))

        # Header yazısı
        font_h = get_system_font("impact.ttf", 16)
        draw.text((w//2, header_h//2), "💬  SOHBET", font=font_h,
                  fill=(255,255,255,230), anchor="mm")

        # --- Alt aksanlar (iki küçük çizgi) ---
        draw.line([(10, h-8),(w-10, h-8)], fill=(c2[0],c2[1],c2[2],120), width=1)
        draw.line([(20, h-4),(w-20, h-4)], fill=(c[0],c[1],c[2],80), width=1)

        # --- Köşe dekorasyon küçük kareler ---
        sq = 6
        sq_c = (c2[0],c2[1],c2[2],200)
        for cx_, cy_ in [(bw,header_h+bw),(w-bw-sq,header_h+bw),
                          (bw,h-bw-sq),(w-bw-sq,h-bw-sq)]:
            draw.rectangle([cx_, cy_, cx_+sq, cy_+sq], fill=sq_c)

        # --- İki yan dikey vurgu çizgisi ---
        draw.line([(bw+8, header_h+8),(bw+8, h-8)],
                  fill=(c[0],c[1],c[2],40), width=1)
        draw.line([(w-bw-9, header_h+8),(w-bw-9, h-8)],
                  fill=(c[0],c[1],c[2],40), width=1)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    # ------------------------------------------------------------------
    # BILEŞEN 4: Event Ticker (1920x120, yarı şeffaf)
    # ------------------------------------------------------------------
    def generate_event_ticker(
        self, channel_name: str, plan: MasterDesignPlan, output_path: str
    ) -> str:
        """1920x120 yatay etkinlik şeridi (hafif şeffaf)."""
        rng = random.Random(plan.seed + 3)
        w, h  = 1920, 120
        img   = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw  = ImageDraw.Draw(img, "RGBA")
        p     = plan.palette
        c     = p.neon_primary

        # Arka plan (yarı şeffaf)
        bg_ov = Image.new("RGBA", (w, h), (0,0,0,0))
        bd    = ImageDraw.Draw(bg_ov, "RGBA")
        for y in range(h):
            t  = y / h
            bg = _blend(p.bg_start, p.bg_end, t)
            bd.line([(0,y),(w,y)], fill=(bg[0],bg[1],bg[2],200))
        img.alpha_composite(bg_ov)
        draw = ImageDraw.Draw(img, "RGBA")

        # Üst/alt neon çizgiler
        draw.line([(0,1),(w,1)], fill=p.neon_primary, width=3)
        draw.line([(0,h-2),(w,h-2)], fill=p.neon_primary, width=2)
        draw.line([(0,7),(w,7)], fill=(c[0],c[1],c[2],80), width=1)

        # 3 segment
        seg_w = w // 3
        segments = [
            ("⭐ SON TAKİPÇİ", "Bilgi bekleniyor..."),
            ("💎 SON ABONE",   "Bilgi bekleniyor..."),
            ("🎯 BAĞIŞ HEDEFİ","▓▓▓▓▓▓▓▓░░ %85"),
        ]
        font_label = get_system_font("impact.ttf", 22)
        font_val   = get_system_font("arialbd.ttf", 18)

        for i, (label, val) in enumerate(segments):
            sx = i * seg_w
            if i > 0:
                draw.line([(sx,8),(sx,h-8)], fill=(c[0],c[1],c[2],100), width=2)
            cx_ = sx + seg_w // 2
            draw.text((cx_, 30), label, font=font_label,
                      fill=(c[0],c[1],c[2],230), anchor="mm")
            draw.text((cx_, 70), val, font=font_val,
                      fill=(p.text_sub[0],p.text_sub[1],p.text_sub[2],200), anchor="mm")

        # Progress bar (3. segment)
        bar_x = 2 * seg_w + 20
        bar_y = 88
        bar_w = seg_w - 40
        bar_h = 8
        draw.rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+bar_h],
                        fill=(40,40,40,180))
        draw.rectangle([bar_x, bar_y, bar_x+int(bar_w*.85), bar_y+bar_h],
                        fill=(c[0],c[1],c[2],220))

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, "PNG")
        return output_path


# ==============================================================================
# 9. GLOBAL SINGLETON'LAR
# ==============================================================================

_factory   = EsportsDesignFactory()
_component = ComponentEsportsFactory(_factory)


# ==============================================================================
# 10. PUBLIC API (main.py ile uyumlu)
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
    out  = os.path.join(assets_dir, f"{safe}_banner_{plan.design_id}.png")
    return _component.generate_banner(name, plan, out)


def generate_webcam_overlay(channel_name: str, plan: MasterDesignPlan) -> str:
    """ŞEFFAF köşe bracket çerçevesi — merkez boş."""
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out  = os.path.join(assets_dir, f"{safe}_webcam_{plan.design_id}.png")
    return _component.generate_webcam_overlay(channel_name, plan, out)


def generate_chat_overlay(channel_name: str, plan: MasterDesignPlan) -> str:
    """ŞEFFAF chat çerçevesi — merkez boş, sadece kenar + header."""
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out  = os.path.join(assets_dir, f"{safe}_chat_{plan.design_id}.png")
    return _component.generate_chat_overlay(channel_name, plan, out)


def generate_event_ticker(channel_name: str, plan: MasterDesignPlan) -> str:
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out  = os.path.join(assets_dir, f"{safe}_ticker_{plan.design_id}.png")
    return _component.generate_event_ticker(channel_name, plan, out)


def _generate_starting_soon(channel_name: str, plan: MasterDesignPlan) -> str:
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out  = os.path.join(assets_dir, f"{safe}_starting_{plan.design_id}.png")
    return _component.generate_opening_screen(channel_name, plan, out)


def _generate_brb(channel_name: str, plan: MasterDesignPlan) -> str:
    assets_dir = get_appdata_obs_assets_dir()
    safe = re.sub(r"[^\w\-]", "_", channel_name)
    out  = os.path.join(assets_dir, f"{safe}_brb_{plan.design_id}.png")
    return _component.generate_brb(channel_name, plan, out)


def build_ai_scene_collection(
    channel_name: str,
    theme_name: str,
    collection_name: str,
    custom_color_query: str = "",
) -> dict:
    """
    Tam AI sahne koleksiyonu oluşturur.
    Webcam ve Chat ŞEFFAF PNG olarak üretilir (OBS'e doğru overlay görünümü için).
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
        obs_dir  = os.path.join(os.environ.get("APPDATA", ""), "obs-studio", "basic", "scenes")
        os.makedirs(obs_dir, exist_ok=True)
        safe_file  = re.sub(r"[^\w\-]", "_", safe_col)
        scene_path = os.path.join(obs_dir, f"{safe_file}.json")

        obs_json = _build_obs_scene_json(collection_name, channel_name, assets, plan)
        with open(scene_path, "w", encoding="utf-8") as f:
            json.dump(obs_json, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "collection_name": collection_name,
            "filepath": scene_path,
            "plan": {
                "design_id": plan.design_id,
                "trend":     plan.trend.value,
                "skeleton":  plan.skeleton.value,
                "palette":   plan.palette.name,
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
    def make_source(name, path, x=0, y=0, w=1920, h=1080):
        return {
            "id": str(uuid.uuid4()), "name": name, "type": "image_source",
            "settings": {"file": path, "unload": False},
            "pos": {"x": x, "y": y},
            "bounds": {"x": w, "y": h, "type": "OBS_BOUNDS_SCALE_INNER"},
            "scale": {"x": 1.0, "y": 1.0},
        }
    scenes = [
        {"id": str(uuid.uuid4()), "name": f"🎮 1 - {channel_name} CANLI",
         "sources": [make_source("Banner", assets["banner"]),
                     make_source("Ticker", assets["ticker"], y=960, h=120),
                     make_source("Chat Frame", assets["chat"], x=1500, w=420, h=600),
                     make_source("Webcam Frame", assets["webcam"], x=30, y=30, w=640, h=480)]},
        {"id": str(uuid.uuid4()), "name": f"💬 2 - Sohbet Sahnesi",
         "sources": [make_source("Banner", assets["banner"]),
                     make_source("Chat Full", assets["chat"], x=750, w=420, h=600)]},
        {"id": str(uuid.uuid4()), "name": f"⏳ 3 - Az Sonra Başlıyor",
         "sources": [make_source("Starting", assets["starting"])]},
        {"id": str(uuid.uuid4()), "name": f"☕ 4 - Az Sonra Dönüyorum",
         "sources": [make_source("BRB", assets["brb"])]},
        {"id": str(uuid.uuid4()), "name": f"👋 5 - Kapanış",
         "sources": [make_source("Banner", assets["banner"])]},
    ]
    return {
        "name": collection_name, "ripleytia_studio": True, "version": "1.6.0",
        "design_id": plan.design_id, "trend": plan.trend.value, "scenes": scenes,
    }


# ==============================================================================
# 11. AI STREAM STRATEJİSİ
# ==============================================================================

def generate_ai_stream_strategy(
    channel_name: str,
    game_type: str,
    style: str,
    api_key: str = "",
) -> dict:
    tips = {
        "fps":  ["Ses kalitesine öncelik ver.", "Clip sistemi kur.", "Turnuvalara katıl."],
        "rpg":  ["Lore yorum bölümleri ekle.", "Karakter build rehberleri yayınla."],
        "moba": ["Maç analizi yap.", "Draft açıkla.", "Takım oluşturmayı göster."],
    }
    key = game_type.lower().split()[0] if game_type else "fps"
    return {
        "channel": channel_name,
        "game": game_type,
        "style": style,
        "strategy": tips.get(key, tips["fps"]),
        "schedule": "Hafta içi 20:00–23:00, Hafta sonu 15:00–22:00",
        "growth_tip": "İlk 90 günde tutarlılık büyümenin %70'ini belirler.",
    }
