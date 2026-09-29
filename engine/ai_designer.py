# -*- coding: utf-8 -*-
"""
engine/ai_designer.py
================================================================================
OBS AI Studio - Radikal Prosedürel Tasarım, Tipografi & Anti-Repetition Motoru
Sürüm: 1.3.0
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
import requests
from PIL import Image, ImageDraw, ImageFont


# ==============================================================================
# 1. TEMEL VERİ YAPILARI (MODELS)
# ==============================================================================

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


def hsl_to_rgba(h_deg: float, s_pct: float, l_pct: float, alpha: int = 255) -> Tuple[int, int, int, int]:
    """HSL derecesini RGBA formatına dönüştürür."""
    h = (h_deg % 360) / 360.0
    s = max(0.0, min(1.0, s_pct / 100.0))
    l = max(0.0, min(1.0, l_pct / 100.0))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255), alpha)


# ==============================================================================
# 2. SANAT AKIMLARI VE GÖRSEL FİZİK KURALLARI (ART MOVEMENTS)
# ==============================================================================

class ArtMovement(str, Enum):
    CYBERPUNK_HUD = "Cyberpunk HUD & High-Tech"
    NEO_BRUTALISM = "Neo-Brutalism & Industrial Raw"
    SWISS_INTERNATIONAL = "Swiss International & Clean Grid"
    MINIMAL_ARCHITECTURAL = "Minimal Architectural & Fine Line"
    Y2K_RETRO_FUTURISM = "Y2K Acid & Retro-Futurism"
    DARK_ESPORTS_MECHA = "Dark Esports Mecha & Angular Aggression"


@dataclass
class MovementPhysics:
    corner_style: str            # 'sharp', 'chamfer', 'rounded', 'pill'
    border_width: int            # 1, 2, 3, 4 piksel
    shadow_type: str             # 'hard_offset', 'soft_ambient', 'neon_glow', 'none'
    shadow_offset: Tuple[int, int]
    box_opacity: float           # 0.0 - 1.0
    decor_style: str             # 'brackets', 'raw_numbers', 'grid_cross', 'minimal_dot', 'chroma_pill', 'hazard'
    diffusion_style: str


MOVEMENT_PHYSICS_MAP: Dict[ArtMovement, MovementPhysics] = {
    ArtMovement.CYBERPUNK_HUD: MovementPhysics(
        corner_style="chamfer",
        border_width=2,
        shadow_type="neon_glow",
        shadow_offset=(0, 0),
        box_opacity=0.75,
        decor_style="brackets",
        diffusion_style="cyberpunk aesthetic, high-tech holographic HUD interface, glowing neon vector lines, tech brackets, scifi user interface"
    ),
    ArtMovement.NEO_BRUTALISM: MovementPhysics(
        corner_style="sharp",
        border_width=4,
        shadow_type="hard_offset",
        shadow_offset=(8, 8),
        box_opacity=1.0,
        decor_style="raw_numbers",
        diffusion_style="neo-brutalism graphic design, ultra bold borders, stark contrast, offset drop shadows, industrial typography, raw aesthetic"
    ),
    ArtMovement.SWISS_INTERNATIONAL: MovementPhysics(
        corner_style="sharp",
        border_width=1,
        shadow_type="none",
        shadow_offset=(0, 0),
        box_opacity=0.92,
        decor_style="grid_cross",
        diffusion_style="international typographic style, swiss style graphic design, asymmetrical balance, mathematical grid, clean elegance"
    ),
    ArtMovement.MINIMAL_ARCHITECTURAL: MovementPhysics(
        corner_style="rounded",
        border_width=1,
        shadow_type="soft_ambient",
        shadow_offset=(0, 4),
        box_opacity=0.45,
        decor_style="minimal_dot",
        diffusion_style="minimalist luxury design, architectural clean layout, ultra-thin wireframes, subtle frosted glassmorphism"
    ),
    ArtMovement.Y2K_RETRO_FUTURISM: MovementPhysics(
        corner_style="pill",
        border_width=3,
        shadow_type="neon_glow",
        shadow_offset=(4, 4),
        box_opacity=0.85,
        decor_style="chroma_pill",
        diffusion_style="Y2K aesthetic, early 2000s cyber rave, liquid chrome badges, rounded pill forms, vaporwave cybercore"
    ),
    ArtMovement.DARK_ESPORTS_MECHA: MovementPhysics(
        corner_style="chamfer",
        border_width=3,
        shadow_type="hard_offset",
        shadow_offset=(4, 4),
        box_opacity=0.90,
        decor_style="hazard",
        diffusion_style="competitive esports broadcast package, Valorant Champions UI aesthetic, mecha armor cuts, aggressive diagonal accents"
    ),
}


# ==============================================================================
# 3. RADİKAL DÜZEN VE KOMPOZİSYON ŞEMALARI (LAYOUT MUTATION)
# ==============================================================================

class LayoutArchetype(str, Enum):
    LEFT_VERTICAL_MONOLITH = "left_vertical_monolith"
    BOTTOM_HORIZONTAL_DOCK = "bottom_horizontal_dock"
    ASYMMETRIC_SPLIT_DIAGONAL = "asymmetric_split_diagonal"
    FRAMELESS_DECENTRALIZED_HUD = "frameless_decentralized_hud"
    CORNER_PINNED_COMPACT = "corner_pinned_compact"
    BRUTALIST_STACKED_CARDS = "brutalist_stacked_cards"


@dataclass
class ElementBox:
    x: float
    y: float
    width: float
    height: float


@dataclass
class LayoutComposition:
    archetype: LayoutArchetype
    webcam_box: ElementBox
    chat_box: ElementBox
    ticker_box: ElementBox
    pattern_type: str            # 'hex_mesh', 'scanlines', 'diagonal_stripes', 'dot_matrix', 'cyber_grid', 'none'
    align_mode: str              # 'left', 'center', 'right'


LAYOUT_CATALOG: Dict[LayoutArchetype, LayoutComposition] = {
    LayoutArchetype.LEFT_VERTICAL_MONOLITH: LayoutComposition(
        archetype=LayoutArchetype.LEFT_VERTICAL_MONOLITH,
        webcam_box=ElementBox(x=0.03, y=0.05, width=0.20, height=0.20),
        chat_box=ElementBox(x=0.03, y=0.28, width=0.20, height=0.55),
        ticker_box=ElementBox(x=0.03, y=0.86, width=0.20, height=0.08),
        pattern_type="diagonal_stripes",
        align_mode="left"
    ),
    LayoutArchetype.BOTTOM_HORIZONTAL_DOCK: LayoutComposition(
        archetype=LayoutArchetype.BOTTOM_HORIZONTAL_DOCK,
        webcam_box=ElementBox(x=0.76, y=0.72, width=0.21, height=0.23),
        chat_box=ElementBox(x=0.03, y=0.68, width=0.18, height=0.26),
        ticker_box=ElementBox(x=0.23, y=0.88, width=0.51, height=0.07),
        pattern_type="cyber_grid",
        align_mode="center"
    ),
    LayoutArchetype.ASYMMETRIC_SPLIT_DIAGONAL: LayoutComposition(
        archetype=LayoutArchetype.ASYMMETRIC_SPLIT_DIAGONAL,
        webcam_box=ElementBox(x=0.77, y=0.05, width=0.20, height=0.21),
        chat_box=ElementBox(x=0.03, y=0.58, width=0.22, height=0.37),
        ticker_box=ElementBox(x=0.28, y=0.05, width=0.46, height=0.06),
        pattern_type="hex_mesh",
        align_mode="center"
    ),
    LayoutArchetype.FRAMELESS_DECENTRALIZED_HUD: LayoutComposition(
        archetype=LayoutArchetype.FRAMELESS_DECENTRALIZED_HUD,
        webcam_box=ElementBox(x=0.04, y=0.70, width=0.19, height=0.23),
        chat_box=ElementBox(x=0.80, y=0.45, width=0.17, height=0.48),
        ticker_box=ElementBox(x=0.30, y=0.02, width=0.40, height=0.05),
        pattern_type="dot_matrix",
        align_mode="center"
    ),
    LayoutArchetype.CORNER_PINNED_COMPACT: LayoutComposition(
        archetype=LayoutArchetype.CORNER_PINNED_COMPACT,
        webcam_box=ElementBox(x=0.78, y=0.72, width=0.19, height=0.22),
        chat_box=ElementBox(x=0.78, y=0.22, width=0.19, height=0.46),
        ticker_box=ElementBox(x=0.03, y=0.03, width=0.38, height=0.06),
        pattern_type="scanlines",
        align_mode="center"
    ),
    LayoutArchetype.BRUTALIST_STACKED_CARDS: LayoutComposition(
        archetype=LayoutArchetype.BRUTALIST_STACKED_CARDS,
        webcam_box=ElementBox(x=0.74, y=0.06, width=0.22, height=0.26),
        chat_box=ElementBox(x=0.74, y=0.36, width=0.22, height=0.48),
        ticker_box=ElementBox(x=0.74, y=0.87, width=0.22, height=0.07),
        pattern_type="none",
        align_mode="left"
    ),
}


# ==============================================================================
# 4. TİPOGRAFİ EŞLEŞMELERİ (TYPOGRAPHY PAIRINGS)
# ==============================================================================

@dataclass
class TypographyPairing:
    name: str
    header_category: str        # 'display_heavy', 'monospace', 'serif', 'geometric', 'swiss'
    body_category: str
    header_weight: str
    tracking_px: int
    uppercase: bool
    recommended_movements: List[ArtMovement]


TYPOGRAPHY_CATALOG: List[TypographyPairing] = [
    TypographyPairing(
        name="Industrial Heavy & Terminal Mono",
        header_category="display_heavy",
        body_category="monospace",
        header_weight="Black (900)",
        tracking_px=2,
        uppercase=True,
        recommended_movements=[ArtMovement.NEO_BRUTALISM, ArtMovement.DARK_ESPORTS_MECHA]
    ),
    TypographyPairing(
        name="Akzidenz Swiss & Precision Grotesk",
        header_category="swiss",
        body_category="swiss",
        header_weight="Bold (700)",
        tracking_px=-1,
        uppercase=False,
        recommended_movements=[ArtMovement.SWISS_INTERNATIONAL, ArtMovement.MINIMAL_ARCHITECTURAL]
    ),
    TypographyPairing(
        name="Cyber HUD Matrix & Space Mono",
        header_category="monospace",
        body_category="monospace",
        header_weight="Bold (700)",
        tracking_px=5,
        uppercase=True,
        recommended_movements=[ArtMovement.CYBERPUNK_HUD]
    ),
    TypographyPairing(
        name="Y2K Chromatic & Rounded Display",
        header_category="geometric",
        body_category="display_heavy",
        header_weight="ExtraBold (800)",
        tracking_px=3,
        uppercase=True,
        recommended_movements=[ArtMovement.Y2K_RETRO_FUTURISM]
    ),
    TypographyPairing(
        name="Architectural Fine Line & Serif",
        header_category="serif",
        body_category="geometric",
        header_weight="Light (300)",
        tracking_px=6,
        uppercase=True,
        recommended_movements=[ArtMovement.MINIMAL_ARCHITECTURAL]
    ),
]


def get_font_by_category(category: str, size: int = 36, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Windows sistem fontlarından kategoriye göre en uygun yazı tipini yükler."""
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fonts_dir = os.path.join(windir, "Fonts")

    mapping = {
        "display_heavy": ["impact.ttf", "arialbd.ttf", "segoeuib.ttf"],
        "monospace": ["consolab.ttf" if bold else "consola.ttf", "courbd.ttf" if bold else "cour.ttf"],
        "serif": ["georgiab.ttf" if bold else "georgia.ttf", "timesbd.ttf" if bold else "times.ttf"],
        "geometric": ["trebucbd.ttf" if bold else "trebuc.ttf", "verdanab.ttf" if bold else "verdana.ttf"],
        "swiss": ["arialbd.ttf" if bold else "arial.ttf", "segoeuib.ttf" if bold else "segoeui.ttf"]
    }

    candidates = mapping.get(category, ["segoeuib.ttf" if bold else "segoeui.ttf", "arial.ttf"])
    for fn in candidates:
        fp = os.path.join(fonts_dir, fn)
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ==============================================================================
# 5. AI & NLP DESTEKLİ RENK ENTEGRATÖRÜ (COLOR HARMONIZER)
# ==============================================================================

class AIColorHarmonizer:
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
            bg_start=(8, 18, 14, 255),
            bg_end=(12, 38, 24, 255),
            neon_primary=(46, 196, 182, 255),
            neon_secondary=(82, 183, 136, 255),
            neon_accent=(255, 209, 102, 255),
            text_main=(240, 255, 250, 255),
            text_sub=(160, 215, 195, 255),
            border_color=(46, 196, 182, 255)
        ),
        "Retro Synthwave": ColorPalette(
            name="Retro Synthwave",
            bg_start=(24, 10, 36, 255),
            bg_end=(48, 12, 54, 255),
            neon_primary=(255, 110, 199, 255),
            neon_secondary=(255, 175, 64, 255),
            neon_accent=(58, 134, 255, 255),
            text_main=(255, 245, 255, 255),
            text_sub=(220, 170, 210, 255),
            border_color=(255, 110, 199, 255)
        ),
        "Minimalist & Clean": ColorPalette(
            name="Minimalist & Clean",
            bg_start=(14, 14, 18, 255),
            bg_end=(22, 22, 28, 255),
            neon_primary=(230, 230, 240, 255),
            neon_secondary=(180, 180, 200, 255),
            neon_accent=(120, 120, 140, 255),
            text_main=(250, 250, 255, 255),
            text_sub=(160, 160, 180, 255),
            border_color=(80, 80, 100, 255)
        )
    }

    def resolve_palette(self, preset_name: str = "Tamamen Rastgele", color_text: str = "", api_key: str = "", art_movement: Optional[ArtMovement] = None) -> ColorPalette:
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

        if preset_name in self.PRESET_PALETTES:
            return self.PRESET_PALETTES[preset_name]

        # Altın Oran HSL Üreticisi
        base_h = (time.time() * 1000 % 360) + random.uniform(0, 50)
        golden_angle = 137.508
        sec_h = (base_h + golden_angle) % 360
        acc_h = (base_h + golden_angle * 2) % 360

        is_brutalist = (art_movement == ArtMovement.NEO_BRUTALISM)
        if is_brutalist:
            bg_start = (244, 240, 234, 255)
            bg_end = (235, 230, 222, 255)
            text_main = (18, 16, 20, 255)
            text_sub = (70, 68, 75, 255)
            border = (18, 16, 20, 255)
        else:
            bg_start = hsl_to_rgba(base_h, 45, 7, 255)
            bg_end = hsl_to_rgba(sec_h, 50, 14, 255)
            text_main = (248, 248, 255, 255)
            text_sub = (185, 180, 205, 255)
            border = hsl_to_rgba(base_h, 85, 55, 255)

        primary = hsl_to_rgba(base_h, 85, 55, 255)
        secondary = hsl_to_rgba(sec_h, 85, 65, 255)
        accent = hsl_to_rgba(acc_h, 95, 60, 255)

        return ColorPalette(
            name=f"Procedural {int(base_h)}° Palette",
            bg_start=bg_start,
            bg_end=bg_end,
            neon_primary=primary,
            neon_secondary=secondary,
            neon_accent=accent,
            text_main=text_main,
            text_sub=text_sub,
            border_color=border
        )


THEME_PALETTES = AIColorHarmonizer.PRESET_PALETTES


# ==============================================================================
# 6. RADİKAL TASARIM SPESİFİKASYONU VE MUTASYON MOTORU
# ==============================================================================

@dataclass
class RadicalDesignSpec:
    design_id: str
    structural_hash: str
    art_movement: ArtMovement
    movement_physics: MovementPhysics
    layout: LayoutComposition
    typography: TypographyPairing
    palette: ColorPalette
    diffusion_structural_prompt: str


class RadicalDesignMutator:
    """
    Tasarımı 4 bağımsız eksende (Kompozisyon, Tipografi, Sanat Akımı, Geometri)
    mutasyona uğratan ve geçmişle benzerliği %80 altında tutan katı motor.
    """
    def __init__(self, history_limit: int = 15, similarity_threshold: float = 0.80):
        self.history_limit = history_limit
        self.similarity_threshold = similarity_threshold
        self.history: List[Dict[str, str]] = []
        self.harmonizer = AIColorHarmonizer()

    def _extract_vector(self, movement: ArtMovement, layout: LayoutArchetype, typo: str, corner: str) -> Dict[str, str]:
        return {
            "movement": movement.value,
            "layout": layout.value,
            "typography": typo,
            "corner": corner
        }

    def _similarity(self, v1: Dict[str, str], v2: Dict[str, str]) -> float:
        matches = sum(1 for k in v1 if v1[k] == v2.get(k))
        return matches / float(len(v1))

    def derive_radical_design(self, preset_theme: str = "🎲 Tamamen Rastgele (Radikal Mutasyon & Anti-Repetition)", color_query: str = "") -> RadicalDesignSpec:
        max_attempts = 40
        for _ in range(max_attempts):
            # 1. Sanat Akımı Seçimi
            if "Cyberpunk" in preset_theme:
                movement = ArtMovement.CYBERPUNK_HUD
            elif "Brutalism" in preset_theme:
                movement = ArtMovement.NEO_BRUTALISM
            elif "Swiss" in preset_theme:
                movement = ArtMovement.SWISS_INTERNATIONAL
            elif "Minimal" in preset_theme:
                movement = ArtMovement.MINIMAL_ARCHITECTURAL
            elif "Y2K" in preset_theme:
                movement = ArtMovement.Y2K_RETRO_FUTURISM
            elif "Esports" in preset_theme or "Mecha" in preset_theme:
                movement = ArtMovement.DARK_ESPORTS_MECHA
            else:
                movement = random.choice(list(ArtMovement))

            physics = MOVEMENT_PHYSICS_MAP[movement]

            # 2. Kompozisyon Seçimi
            layout_archetype = random.choice(list(LayoutArchetype))
            layout = LAYOUT_CATALOG[layout_archetype]

            # 3. Tipografi Eşleşmesi
            compat_typos = [t for t in TYPOGRAPHY_CATALOG if movement in t.recommended_movements]
            typography = random.choice(compat_typos) if compat_typos and random.random() < 0.85 else random.choice(TYPOGRAPHY_CATALOG)

            # 4. Katı Geçmiş Kontrolü (Hard Unique Cache)
            current_vector = self._extract_vector(movement, layout_archetype, typography.name, physics.corner_style)
            too_similar = False
            for past in self.history:
                if self._similarity(current_vector, past) >= self.similarity_threshold:
                    too_similar = True
                    break

            if too_similar:
                continue # Reddet ve yeni varyasyon dene

            # 5. Renk Paletini Çöz
            palette = self.harmonizer.resolve_palette(preset_name=preset_theme, color_text=color_query, art_movement=movement)

            # 6. İmzayı ve Kimliği Üret
            sig = f"{movement.value}_{layout_archetype.value}_{typography.name}_{physics.corner_style}_{random.randint(100, 999)}"
            s_hash = hashlib.md5(sig.encode("utf-8")).hexdigest()[:10]
            design_id = f"RIPLEYTIA-{s_hash.upper()}"

            # 7. Diffusion AI Modeline Yönelik Yapısal Prompt
            diff_prompt = (
                f"{physics.diffusion_style}, {layout_archetype.value.replace('_', ' ')} layout, "
                f"header typography {typography.header_category} {typography.header_weight}, "
                f"{physics.corner_style} borders, {physics.shadow_type} effect, "
                f"colors {palette.name}, professional twitch overlay stream pack, clean vector graphic"
            )

            spec = RadicalDesignSpec(
                design_id=design_id,
                structural_hash=s_hash,
                art_movement=movement,
                movement_physics=physics,
                layout=layout,
                typography=typography,
                palette=palette,
                diffusion_structural_prompt=diff_prompt
            )

            # Geçmiş havuzuna ekle
            self.history.append(current_vector)
            if len(self.history) > self.history_limit:
                self.history.pop(0)

            return spec

        # Fallback
        self.history.clear()
        return self.derive_radical_design(preset_theme, color_query)


# Global Tekil Örnek
_mutator_instance = RadicalDesignMutator()


def get_appdata_obs_assets_dir() -> str:
    appdata = os.environ.get("APPDATA", "")
    obs_assets = os.path.join(appdata, "obs-studio", "ripleytia_assets")
    os.makedirs(obs_assets, exist_ok=True)
    return obs_assets


# ==============================================================================
# 7. ÇİZİM YARDIMCILARI (GEOMETRY & PHYSICS RENDERERS)
# ==============================================================================

def draw_cornered_box(draw: ImageDraw.Draw, 
                      rect: Tuple[int, int, int, int], 
                      corner_style: str, 
                      fill_color: Tuple[int, int, int, int], 
                      outline_color: Tuple[int, int, int, int], 
                      border_width: int, 
                      shadow_type: str = "none", 
                      shadow_offset: Tuple[int, int] = (0, 0)):
    """
    Sanat akımının fizik kurallarına göre (Pah kırma, Sert gölge, Neon ışıma, Keskin köşe) panel çizer.
    """
    x, y, w, h = rect

    # 1. Gölge Çizimi
    if shadow_type == "hard_offset" and shadow_offset != (0, 0):
        sx, sy = x + shadow_offset[0], y + shadow_offset[1]
        draw.rectangle([(sx, sy), (sx + w, sy + h)], fill=(15, 12, 22, 230))
    elif shadow_type == "neon_glow":
        glow_col = (outline_color[0], outline_color[1], outline_color[2], 65)
        draw.rectangle([(x - 4, y - 4), (x + w + 4, y + h + 4)], outline=glow_col, width=border_width + 4)

    # 2. Ana Kutu Çizimi
    if corner_style == "chamfer":
        c = 22
        points = [
            (x + c, y), (x + w - c, y),
            (x + w, y + c), (x + w, y + h - c),
            (x + w - c, y + h), (x + c, y + h),
            (x, y + h - c), (x, y + c)
        ]
        draw.polygon(points, fill=fill_color, outline=outline_color, width=border_width)
    elif corner_style == "rounded":
        r = 16
        draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=r, fill=fill_color, outline=outline_color, width=border_width)
    elif corner_style == "pill":
        r = min(w, h) // 6
        draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=r, fill=fill_color, outline=outline_color, width=border_width)
    else: # sharp (Neo-Brutalism & Swiss)
        draw.rectangle([(x, y), (x + w, y + h)], fill=fill_color, outline=outline_color, width=border_width)


# ==============================================================================
# 8. DİNAMİK AÇILIŞ VE MOLA BANNER ÜRETİCİSİ (PROSEDÜREL 1920x1080)
# ==============================================================================

def generate_channel_banner(channel_name: str = "Ripleytia", 
                            spec: Optional[RadicalDesignSpec] = None, 
                            mode: str = "starting", 
                            custom_title: Optional[str] = None) -> str:
    if spec is None:
        spec = _mutator_instance.derive_radical_design()

    w, h = 1920, 1080
    palette = spec.palette
    physics = spec.movement_physics
    layout = spec.layout
    typo = spec.typography

    img = Image.new("RGBA", (w, h), palette.bg_start)
    draw = ImageDraw.Draw(img)

    # 1. Dikey Gradyan Zemin
    for y in range(h):
        blend = y / h
        r = int(palette.bg_start[0] * (1 - blend) + palette.bg_end[0] * blend)
        g = int(palette.bg_start[1] * (1 - blend) + palette.bg_end[1] * blend)
        b = int(palette.bg_start[2] * (1 - blend) + palette.bg_end[2] * blend)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # 2. Desen Algoritmaları
    pat = layout.pattern_type
    p_alpha = 45 if spec.art_movement != ArtMovement.NEO_BRUTALISM else 18
    pat_col = (palette.neon_primary[0], palette.neon_primary[1], palette.neon_primary[2], p_alpha)

    if pat == "diagonal_stripes":
        step = 55
        for x in range(-w, w * 2, step):
            draw.line([(x, 0), (x + h, h)], fill=pat_col, width=2)
    elif pat == "hex_mesh":
        step = 75
        for y in range(0, h + step, step):
            for x in range(0, w + step, step):
                draw.regular_polygon((x, y, 18), 6, rotation=0, outline=pat_col)
    elif pat == "cyber_grid":
        step = 80
        for x in range(0, w, step):
            draw.line([(x, 0), (x, h)], fill=pat_col, width=1)
        for y in range(0, h, step):
            draw.line([(0, y), (w, y)], fill=pat_col, width=1)
    elif pat == "dot_matrix":
        step = 42
        for y in range(0, h, step):
            for x in range(0, w, step):
                draw.point((x, y), fill=(palette.neon_accent[0], palette.neon_accent[1], palette.neon_accent[2], p_alpha * 2))

    # 3. Sanat Akımına Özgü Geometrik Arka Plan Katmanları
    if spec.art_movement == ArtMovement.NEO_BRUTALISM:
        # Dev arka plan numarası ve ham endüstriyel çizgiler
        font_bg_huge = get_font_by_category("display_heavy", size=240, bold=True)
        draw.text((100, 160), "01", font=font_bg_huge, fill=(palette.border_color[0], palette.border_color[1], palette.border_color[2], 25))
        draw.line([(0, h - 160), (w, h - 160)], fill=palette.border_color, width=4)
    elif spec.art_movement == ArtMovement.SWISS_INTERNATIONAL:
        # Kılavuz kolonlar ve matematiksel grid çizgileri
        for col_x in [320, 640, 960, 1280, 1600]:
            draw.line([(col_x, 0), (col_x, h)], fill=(palette.border_color[0], palette.border_color[1], palette.border_color[2], 25), width=1)
        draw.text((80, 60), f"GRID // SYSTEM 24.1  •  {spec.design_id}", font=get_font_by_category("swiss", 14), fill=palette.text_sub)
    elif spec.art_movement == ArtMovement.CYBERPUNK_HUD:
        # HUD Telemetri çerçevesi ve köşebentler
        m = 50
        draw.rectangle([(m, m), (w - m, h - m)], outline=(palette.neon_primary[0], palette.neon_primary[1], palette.neon_primary[2], 90), width=2)
        for px, py in [(m, m), (w - m, m), (m, h - m), (w - m, h - m)]:
            dx = 1 if px == m else -1
            dy = 1 if py == m else -1
            draw.line([(px, py), (px + dx * 60, py)], fill=palette.neon_accent, width=5)
            draw.line([(px, py), (px, py + dy * 60)], fill=palette.neon_accent, width=5)

    # 4. Tipografi Başlıkları
    font_main = get_font_by_category(typo.header_category, size=78, bold=True)
    font_sub = get_font_by_category(typo.body_category, size=32, bold=True)
    font_tag = get_font_by_category("swiss", size=20, bold=False)

    ch_text = channel_name.upper() if typo.uppercase else channel_name

    if mode == "starting":
        sub_text = custom_title or "YAYIN BİRAZDAN BAŞLIYOR..."
        tagline = f"{spec.art_movement.value} • 0 Dropped Frames • Canlı Yayın"
    elif mode == "brb":
        sub_text = custom_title or "KISA BİR MOLA • HEMEN DÖNÜYORUM"
        tagline = "Kahve Molası • Lütfen Yayından Ayrılmayın!"
    else:
        sub_text = custom_title or "YAYIN SONA ERDİ • TEŞEKKÜRLER!"
        tagline = "Takip Etmeyi ve Bildirimleri Açmayı Unutmayın!"

    align_center = (layout.align_mode == "center")
    if align_center:
        ch_box = draw.textbbox((0, 0), ch_text, font=font_main)
        sub_box = draw.textbbox((0, 0), sub_text, font=font_sub)
        tag_box = draw.textbbox((0, 0), tagline, font=font_tag)

        cy_main = h // 2 - 80
        draw.text(((w - (ch_box[2] - ch_box[0])) // 2 + 4, cy_main + 4), ch_text, font=font_main, fill=(0, 0, 0, 220))
        draw.text(((w - (ch_box[2] - ch_box[0])) // 2, cy_main), ch_text, font=font_main, fill=palette.text_main)

        cy_sub = cy_main + 110
        draw.text(((w - (sub_box[2] - sub_box[0])) // 2, cy_sub), sub_text, font=font_sub, fill=palette.neon_secondary)

        cy_tag = cy_sub + 60
        draw.text(((w - (tag_box[2] - tag_box[0])) // 2, cy_tag), tagline, font=font_tag, fill=palette.text_sub)
    else:
        cx_main = 120
        cy_main = h // 2 - 90
        draw.text((cx_main + 4, cy_main + 4), ch_text, font=font_main, fill=(0, 0, 0, 220))
        draw.text((cx_main, cy_main), ch_text, font=font_main, fill=palette.text_main)
        draw.text((cx_main, cy_main + 110), sub_text, font=font_sub, fill=palette.neon_secondary)
        draw.text((cx_main, cy_main + 170), tagline, font=font_tag, fill=palette.text_sub)

    # 5. Rozet & Alt Bilgi
    pill_w, pill_h = 480, 48
    pill_x = (w - pill_w) // 2 if align_center else 120
    pill_y = h - 220 if align_center else h - 240
    draw_cornered_box(
        draw, (pill_x, pill_y, pill_w, pill_h),
        corner_style=physics.corner_style,
        fill_color=(12, 10, 20, 240),
        outline_color=palette.border_color,
        border_width=physics.border_width,
        shadow_type=physics.shadow_type,
        shadow_offset=(4, 4)
    )
    draw.ellipse([(pill_x + 18, pill_y + 16), (pill_x + 32, pill_y + 30)], fill=(239, 68, 68, 255))
    draw.text((pill_x + 44, pill_y + 13), f"LIVE • {spec.art_movement.value}", font=get_font_by_category("monospace", 14, True), fill=palette.text_main)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_{mode}.png")
    img.save(out_file, "PNG")
    return out_file


# ==============================================================================
# 9. DİNAMİK ŞEFFAF WEBCAM ÇERÇEVESİ (KOMPOZİSYONA GÖRE YERLEŞEN 1920x1080)
# ==============================================================================

def generate_webcam_overlay(channel_name: str = "Ripleytia", spec: Optional[RadicalDesignSpec] = None) -> str:
    if spec is None:
        spec = _mutator_instance.derive_radical_design()

    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    palette = spec.palette
    physics = spec.movement_physics
    box = spec.layout.webcam_box

    # Radikal Kompozisyondan Piksel Koordinatlarına Dönüştürme
    cam_x = int(box.x * w)
    cam_y = int(box.y * h)
    cam_w = int(box.width * w)
    cam_h = int(box.height * h)

    # Çerçeveyi Sanat Akımına Göre Çiz
    draw_cornered_box(
        draw, (cam_x, cam_y, cam_w, cam_h),
        corner_style=physics.corner_style,
        fill_color=(0, 0, 0, 0), # Şeffaf kamera penceresi
        outline_color=palette.neon_primary,
        border_width=physics.border_width,
        shadow_type=physics.shadow_type,
        shadow_offset=physics.shadow_offset
    )

    # İsim Plakası ve Dekoratif Etiketler
    badge_h = 34
    draw_cornered_box(
        draw, (cam_x, cam_y + cam_h, cam_w, badge_h),
        corner_style="sharp" if physics.corner_style == "sharp" else "rounded",
        fill_color=(14, 12, 22, int(255 * physics.box_opacity)),
        outline_color=palette.border_color,
        border_width=max(1, physics.border_width - 1),
        shadow_type="none"
    )

    badge_font = get_font_by_category(spec.typography.body_category, size=14, bold=True)
    draw.text((cam_x + 14, cam_y + cam_h + 8), f"🔴 {channel_name.upper()}", font=badge_font, fill=palette.text_main)
    draw.text((cam_x + cam_w - 95, cam_y + cam_h + 8), f"60 FPS HD", font=badge_font, fill=palette.neon_accent)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_webcam_overlay.png")
    img.save(out_file, "PNG")
    return out_file


# ==============================================================================
# 10. DİNAMİK ŞEFFAF SOHBET KUTUSU (KOMPOZİSYONA GÖRE YERLEŞEN 1920x1080)
# ==============================================================================

def generate_chat_overlay(channel_name: str = "Ripleytia", spec: Optional[RadicalDesignSpec] = None) -> str:
    if spec is None:
        spec = _mutator_instance.derive_radical_design()

    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    palette = spec.palette
    physics = spec.movement_physics
    box = spec.layout.chat_box

    chat_x = int(box.x * w)
    chat_y = int(box.y * h)
    chat_w = int(box.width * w)
    chat_h = int(box.height * h)

    body_opacity = int(255 * physics.box_opacity * 0.70)
    draw_cornered_box(
        draw, (chat_x, chat_y, chat_w, chat_h),
        corner_style=physics.corner_style,
        fill_color=(12, 10, 20, body_opacity),
        outline_color=palette.border_color,
        border_width=physics.border_width,
        shadow_type=physics.shadow_type,
        shadow_offset=physics.shadow_offset
    )

    # Başlık Şeridi
    header_h = 38
    draw_cornered_box(
        draw, (chat_x, chat_y, chat_w, header_h),
        corner_style=physics.corner_style,
        fill_color=(palette.bg_start[0], palette.bg_start[1], palette.bg_start[2], 230),
        outline_color=palette.border_color,
        border_width=physics.border_width,
        shadow_type="none"
    )

    head_font = get_font_by_category(spec.typography.header_category, size=14, bold=True)
    draw.text((chat_x + 14, chat_y + 10), f"💬 CHAT • @{channel_name}", font=head_font, fill=palette.text_main)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_chat_overlay.png")
    img.save(out_file, "PNG")
    return out_file


# ==============================================================================
# 11. DİNAMİK ETKİNLİK ŞERİDİ (EVENT TICKER 1920x1080)
# ==============================================================================

def generate_event_ticker(channel_name: str = "Ripleytia", spec: Optional[RadicalDesignSpec] = None) -> str:
    if spec is None:
        spec = _mutator_instance.derive_radical_design()

    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    palette = spec.palette
    physics = spec.movement_physics
    box = spec.layout.ticker_box

    tx = int(box.x * w)
    ty = int(box.y * h)
    tw = int(box.width * w)
    th = int(box.height * h)

    draw_cornered_box(
        draw, (tx, ty, tw, th),
        corner_style=physics.corner_style,
        fill_color=(12, 10, 22, int(255 * physics.box_opacity)),
        outline_color=palette.border_color,
        border_width=physics.border_width,
        shadow_type=physics.shadow_type,
        shadow_offset=(3, 3)
    )

    font_t = get_font_by_category(spec.typography.body_category, size=13, bold=True)
    font_v = get_font_by_category("swiss", size=13, bold=False)

    draw.text((tx + 20, ty + (th // 2 - 9)), "⭐ SON TAKİPÇİ:", font=font_t, fill=palette.neon_secondary)
    draw.text((tx + 145, ty + (th // 2 - 9)), "Topluluk Üyesi", font=font_v, fill=palette.text_main)

    draw.text((tx + tw // 2, ty + (th // 2 - 9)), "💎 SON ABONE:", font=font_t, fill=palette.neon_accent)
    draw.text((tx + tw // 2 + 125, ty + (th // 2 - 9)), "VIP Destekçi", font=font_v, fill=palette.text_main)

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_ticker_overlay.png")
    img.save(out_file, "PNG")
    return out_file


# ==============================================================================
# 12. OBS SAHNE KOLEKSİYONU OLUŞTURUCUSU
# ==============================================================================

def build_ai_scene_collection(channel_name: str = "Ripleytia", 
                              theme_name: str = "🎲 Tamamen Rastgele (Radikal Mutasyon & Anti-Repetition)", 
                              collection_name: Optional[str] = None, 
                              custom_color_query: str = "") -> Dict[str, Any]:
    """
    Radikal tasarım mutasyonunu çalıştırır, 6 varlığı üretir ve OBS JSON koleksiyonunu yazar.
    """
    spec = _mutator_instance.derive_radical_design(preset_theme=theme_name, color_query=custom_color_query)

    start_banner = generate_channel_banner(channel_name=channel_name, spec=spec, mode="starting")
    brb_banner = generate_channel_banner(channel_name=channel_name, spec=spec, mode="brb")
    end_banner = generate_channel_banner(channel_name=channel_name, spec=spec, mode="ending")
    webcam_overlay = generate_webcam_overlay(channel_name=channel_name, spec=spec)
    chat_overlay = generate_chat_overlay(channel_name=channel_name, spec=spec)
    ticker_overlay = generate_event_ticker(channel_name=channel_name, spec=spec)

    appdata = os.environ.get("APPDATA", "")
    scenes_dir = os.path.join(appdata, "obs-studio", "basic", "scenes")
    os.makedirs(scenes_dir, exist_ok=True)

    c_name = collection_name or f"Ripleytia AI - {channel_name} ({spec.design_id})"
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
        "spec": spec,
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
