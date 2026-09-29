import os
import json
import uuid
import math
import requests
from PIL import Image, ImageDraw, ImageFont

def get_appdata_obs_assets_dir():
    appdata = os.environ.get("APPDATA", "")
    obs_assets = os.path.join(appdata, "obs-studio", "ripleytia_assets")
    os.makedirs(obs_assets, exist_ok=True)
    return obs_assets

THEME_PALETTES = {
    "cyber_purple": {
        "bg_start": (15, 10, 26, 255),
        "bg_end": (35, 12, 60, 255),
        "neon_primary": (138, 43, 226, 255),    # BlueViolet
        "neon_secondary": (199, 125, 255, 255), # Light Violet
        "neon_accent": (0, 245, 212, 255),      # Cyan
        "text_main": (245, 235, 255, 255),
        "text_sub": (180, 160, 210, 255),
        "border_color": (160, 60, 255, 255)
    },
    "neon_cyberpunk": {
        "bg_start": (10, 14, 25, 255),
        "bg_end": (20, 30, 50, 255),
        "neon_primary": (0, 245, 212, 255),     # Cyan
        "neon_secondary": (255, 0, 128, 255),   # Hot Pink
        "neon_accent": (255, 222, 89, 255),     # Yellow
        "text_main": (240, 250, 255, 255),
        "text_sub": (150, 200, 230, 255),
        "border_color": (0, 245, 212, 255)
    },
    "blood_red": {
        "bg_start": (18, 8, 10, 255),
        "bg_end": (45, 12, 16, 255),
        "neon_primary": (230, 57, 70, 255),     # Crimson Red
        "neon_secondary": (255, 107, 107, 255),
        "neon_accent": (244, 162, 97, 255),     # Orange
        "text_main": (255, 240, 240, 255),
        "text_sub": (210, 160, 160, 255),
        "border_color": (230, 57, 70, 255)
    },
    "emerald_green": {
        "bg_start": (8, 20, 15, 255),
        "bg_end": (15, 45, 30, 255),
        "neon_primary": (16, 185, 129, 255),    # Emerald
        "neon_secondary": (52, 211, 153, 255),
        "neon_accent": (110, 231, 183, 255),
        "text_main": (240, 255, 245, 255),
        "text_sub": (150, 210, 180, 255),
        "border_color": (16, 185, 129, 255)
    }
}

def get_system_font(size=36, bold=False):
    """
    Windows yerleşik yazı tiplerini (Segoe UI, Arial vb.) güvenli şekilde yükler.
    """
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
# 1. KİŞİSELLEŞTİRİLMİŞ AÇILIŞ VE MOLA BANNER ÜRETİCİ (1920x1080)
# ------------------------------------------------------------------------------
def generate_channel_banner(channel_name="Ripleytia", theme_name="cyber_purple", mode="starting", custom_title=None):
    """
    Kullanıcının kanal adına özel, 1920x1080 yüksek çözünürlüklü estetik açılış/mola ekranı üretir.
    mode: 'starting' (Yayın Başlıyor), 'brb' (Kısa Mola), 'ending' (Yayın Bitti)
    """
    palette = THEME_PALETTES.get(theme_name, THEME_PALETTES["cyber_purple"])
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), palette["bg_start"])
    draw = ImageDraw.Draw(img)

    # Arka Plan Gradient & Geometrik Çizgiler
    for y in range(h):
        blend = y / h
        r = int(palette["bg_start"][0] * (1 - blend) + palette["bg_end"][0] * blend)
        g = int(palette["bg_start"][1] * (1 - blend) + palette["bg_end"][1] * blend)
        b = int(palette["bg_start"][2] * (1 - blend) + palette["bg_end"][2] * blend)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Geometrik Izgara (Gamer Grid) Çizgileri
    grid_color = (palette["neon_primary"][0], palette["neon_primary"][1], palette["neon_primary"][2], 25)
    for x in range(0, w, 80):
        draw.line([(x, 0), (x, h)], fill=grid_color, width=1)
    for y in range(0, h, 80):
        draw.line([(0, y), (w, y)], fill=grid_color, width=1)

    # Dış Neon Çerçeve (Çift katmanlı parıltı hissi)
    draw.rectangle([(40, 40), (w - 40, h - 40)], outline=palette["border_color"], width=3)
    draw.rectangle([(48, 48), (w - 48, h - 48)], outline=(palette["neon_secondary"][0], palette["neon_secondary"][1], palette["neon_secondary"][2], 120), width=1)

    # Köşe Geometrik Aksanlar
    corner_len = 60
    for cx, cy in [(40, 40), (w - 40, 40), (40, h - 40), (w - 40, h - 40)]:
        dx = 1 if cx == 40 else -1
        dy = 1 if cy == 40 else -1
        draw.line([(cx, cy), (cx + dx * corner_len, cy)], fill=palette["neon_accent"], width=5)
        draw.line([(cx, cy), (cx, cy + dy * corner_len)], fill=palette["neon_accent"], width=5)

    # Tipografi: Başlık ve Kanal Adı
    font_huge = get_system_font(size=72, bold=True)
    font_title = get_system_font(size=38, bold=True)
    font_sub = get_system_font(size=24, bold=False)

    if mode == "starting":
        sub_text = custom_title or "YAYIN BİRAZDAN BAŞLIYOR..."
        tagline = "Canlı Yayın & Yüksek Performans • Hazırlanın!"
    elif mode == "brb":
        sub_text = custom_title or "KISA BİR MOLA • HEMEN DÖNÜYORUM"
        tagline = "Kahve/İçecek Molası • Yayından Ayrılmayın!"
    else:
        sub_text = custom_title or "YAYIN SONA ERDİ • İZLEDİĞİNİZ İÇİN TEŞEKKÜRLER!"
        tagline = "Takip Etmeyi ve Bildirimleri Açmayı Unutmayın!"

    channel_text = channel_name.upper()

    # Kanal Adı Gölgesi ve Kendisi (Ortalanmış)
    ch_box = draw.textbbox((0, 0), channel_text, font=font_huge)
    ch_w = ch_box[2] - ch_box[0]
    ch_x = (w - ch_w) // 2
    ch_y = 380

    # Gölge
    draw.text((ch_x + 4, ch_y + 4), channel_text, font=font_huge, fill=(0, 0, 0, 180))
    # Ana Metin
    draw.text((ch_x, ch_y), channel_text, font=font_huge, fill=palette["text_main"])

    # Alt Başlık
    sub_box = draw.textbbox((0, 0), sub_text, font=font_title)
    sub_w = sub_box[2] - sub_box[0]
    sub_x = (w - sub_w) // 2
    draw.text((sub_x, 480), sub_text, font=font_title, fill=palette["neon_secondary"])

    # Tagline
    tag_box = draw.textbbox((0, 0), tagline, font=font_sub)
    tag_w = tag_box[2] - tag_box[0]
    draw.text(((w - tag_w) // 2, 550), tagline, font=font_sub, fill=palette["text_sub"])

    # Durum & Yükleme Çubuğu Kutusu (Center Box)
    box_w, box_h = 500, 50
    box_x = (w - box_w) // 2
    box_y = 650
    draw.rounded_rectangle([(box_x, box_y), (box_x + box_w, box_y + box_h)], radius=12, fill=(0, 0, 0, 160), outline=palette["border_color"], width=2)
    
    # Kırmızı Canlı Noktası
    draw.ellipse([(box_x + 20, box_y + 17), (box_x + 36, box_y + 33)], fill=(239, 68, 68, 255))
    draw.text((box_x + 48, box_y + 14), "CANLI YAYIN BEKLEME MODU", font=get_system_font(18, bold=True), fill=palette["text_main"])

    # Alt Bilgi Şeridi: Sosyal Medya İpuçları
    bot_y = h - 120
    draw.line([(100, bot_y), (w - 100, bot_y)], fill=(palette["border_color"][0], palette["border_color"][1], palette["border_color"][2], 100), width=1)
    footer_text = f"TWITCH / KICK: @{channel_name}   •   YOUTUBE: @{channel_name}   •   DISCORD TOPLULUĞU"
    fb_box = draw.textbbox((0, 0), footer_text, font=get_system_font(18, False))
    draw.text(((w - (fb_box[2] - fb_box[0])) // 2, bot_y + 25), footer_text, font=get_system_font(18, False), fill=palette["text_sub"])

    # Dosyayı kaydet
    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_{mode}.png")
    img.save(out_file, "PNG")
    return out_file

# ------------------------------------------------------------------------------
# 2. ŞEFFAF WEBCAM OVERLAY ÇERÇEVESİ (1920x1080 Transparent PNG)
# ------------------------------------------------------------------------------
def generate_webcam_overlay(channel_name="Ripleytia", theme_name="cyber_purple"):
    """
    Oyun sahnesinde kamera üzerine tam oturan 1920x1080 şeffaf webcam çerçevesi üretir.
    Webcam varsayılan olarak sağ üstte 480x270 (16:9) oranında konumlandırılır.
    """
    palette = THEME_PALETTES.get(theme_name, THEME_PALETTES["cyber_purple"])
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Webcam Konumu (Sağ Üst: X=1380, Y=60, W=480, H=270)
    cam_x, cam_y = 1380, 60
    cam_w, cam_h = 480, 270

    # Dış Çerçeve
    draw.rectangle([(cam_x, cam_y), (cam_x + cam_w, cam_y + cam_h)], outline=palette["neon_primary"], width=3)
    draw.rectangle([(cam_x - 3, cam_y - 3), (cam_x + cam_w + 3, cam_y + cam_h + 3)], outline=(palette["neon_secondary"][0], palette["neon_secondary"][1], palette["neon_secondary"][2], 100), width=1)

    # Köşe Aksanları
    c_len = 25
    for px, py in [(cam_x, cam_y), (cam_x + cam_w, cam_y), (cam_x, cam_y + cam_h), (cam_x + cam_w, cam_y + cam_h)]:
        dx = 1 if px == cam_x else -1
        dy = 1 if py == cam_y else -1
        draw.line([(px, py), (px + dx * c_len, py)], fill=palette["neon_accent"], width=4)
        draw.line([(px, py), (px, py + dy * c_len)], fill=palette["neon_accent"], width=4)

    # Alt İsim Şeridi
    badge_h = 32
    draw.rectangle([(cam_x, cam_y + cam_h), (cam_x + cam_w, cam_y + cam_h + badge_h)], fill=(12, 10, 20, 230), outline=palette["neon_primary"], width=2)
    font_badge = get_system_font(16, bold=True)
    draw.text((cam_x + 16, cam_y + cam_h + 6), f"🔴 {channel_name.upper()}", font=font_badge, fill=palette["text_main"])
    draw.text((cam_x + cam_w - 95, cam_y + cam_h + 8), "LIVE HD", font=get_system_font(13, bold=True), fill=palette["neon_accent"])

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_webcam_overlay.png")
    img.save(out_file, "PNG")
    return out_file

# ------------------------------------------------------------------------------
# 3. ŞEFFAF SOHBET (CHAT) OVERLAY ALANI (1920x1080 Transparent PNG)
# ------------------------------------------------------------------------------
def generate_chat_overlay(channel_name="Ripleytia", theme_name="cyber_purple"):
    """
    Sohbet sahnesi veya oyun sahnesi için şık yarı saydam cam efektli chatbox üretir.
    Sol Altta X=60, Y=350, W=400, H=660
    """
    palette = THEME_PALETTES.get(theme_name, THEME_PALETTES["cyber_purple"])
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 60, 350
    cw, ch = 420, 660

    # Yarı saydam gövde
    draw.rounded_rectangle([(cx, cy), (cx + cw, cy + ch)], radius=14, fill=(10, 8, 18, 140), outline=palette["neon_primary"], width=2)

    # Başlık Çubuğu
    draw.rounded_rectangle([(cx, cy), (cx + cw, cy + 42)], radius=12, fill=(25, 15, 45, 230), outline=palette["border_color"], width=2)
    font_h = get_system_font(16, bold=True)
    draw.text((cx + 16, cy + 10), f"💬 CANLI SOHBET • @{channel_name}", font=font_h, fill=palette["text_main"])

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_chat_overlay.png")
    img.save(out_file, "PNG")
    return out_file

# ------------------------------------------------------------------------------
# 4. ÜST HEDEF & ETKİNLİK ŞERİDİ (EVENT TICKER)
# ------------------------------------------------------------------------------
def generate_event_ticker(channel_name="Ripleytia", theme_name="cyber_purple"):
    """
    Ekranın en üstüne yerleşen şeffaf etkinlik şeridi: Son Takipçi, Son Abone, Hedef Barı
    """
    palette = THEME_PALETTES.get(theme_name, THEME_PALETTES["cyber_purple"])
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    tx, ty = 200, 20
    tw, th = 1520, 48

    draw.rounded_rectangle([(tx, ty), (tx + tw, ty + th)], radius=10, fill=(12, 10, 22, 210), outline=palette["border_color"], width=2)

    font_t = get_system_font(15, bold=True)
    font_v = get_system_font(15, bold=False)

    # Bölüm 1: Takipçi
    draw.text((tx + 30, ty + 14), "⭐ SON TAKİPÇİ:", font=font_t, fill=palette["neon_secondary"])
    draw.text((tx + 180, ty + 14), "Topluluk Üyesi", font=font_v, fill=palette["text_main"])

    # Bölüm 2: Abone
    draw.text((tx + 540, ty + 14), "💎 SON ABONE:", font=font_t, fill=palette["neon_accent"])
    draw.text((tx + 680, ty + 14), "Vip Destekçi", font=font_v, fill=palette["text_main"])

    # Bölüm 3: Hedef
    draw.text((tx + 1040, ty + 14), "🎯 TAKİPÇİ HEDEFİ: 84 / 100", font=font_t, fill=palette["text_main"])

    out_dir = get_appdata_obs_assets_dir()
    clean_name = "".join(c for c in channel_name if c.isalnum() or c in ("_", "-"))
    out_file = os.path.join(out_dir, f"{clean_name}_ticker_overlay.png")
    img.save(out_file, "PNG")
    return out_file

# ------------------------------------------------------------------------------
# 5. TAM AKILLI OBS SAHNE KOLEKSİYONU ENTEGRATÖRÜ
# ------------------------------------------------------------------------------
def build_ai_scene_collection(channel_name="Ripleytia", theme_name="cyber_purple", collection_name=None):
    r"""
    1. Kanal adına özel açılış, mola ve kapanış banner'larını oluşturur.
    2. Şeffaf webcam çerçevesi ve chat overlay'ini üretir.
    3. OBS Mikrofonuna AI Gürültü Engelleme (RNNoise) filtresini bağlar.
    4. ReShade kilitlenmesini engelleyen Oyun Yakalama (`capture_overlays=false`) kaynağını ekler.
    5. Koleksiyonu doğrudan %APPDATA%\obs-studio\basic\scenes\<name>.json dosyasına yazar.
    """
    appdata = os.environ.get("APPDATA", "")
    scenes_dir = os.path.join(appdata, "obs-studio", "basic", "scenes")
    os.makedirs(scenes_dir, exist_ok=True)

    c_name = collection_name or f"Ripleytia AI - {channel_name}"
    filepath = os.path.join(scenes_dir, f"{c_name}.json")

    # Grafikleri oluştur
    start_banner = generate_channel_banner(channel_name, theme_name, mode="starting")
    brb_banner = generate_channel_banner(channel_name, theme_name, mode="brb")
    end_banner = generate_channel_banner(channel_name, theme_name, mode="ending")
    webcam_overlay = generate_webcam_overlay(channel_name, theme_name)
    chat_overlay = generate_chat_overlay(channel_name, theme_name)
    ticker_overlay = generate_event_ticker(channel_name, theme_name)

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
            # AI RNNOISE GÜRÜLTÜ ENGELLEME FİLTRESİ
            "filters": [
                {
                    "name": "🤖 AI RNNoise Gürültü Engelleme",
                    "id": "noise_suppress_filter",
                    "versioned_id": "noise_suppress_filter",
                    "settings": {
                        "method": 1  # 1 = RNNoise (Yüksek Kalite, Yapay Zeka tabanlı)
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
            # ---------------- 1. OYUN SAHNESİ ----------------
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
            # ---------------- 2. SOHBET SAHNESİ ----------------
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
            # ---------------- 3. YAYIN BAŞLIYOR SAHNESİ ----------------
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
            # ---------------- 4. MOLA SAHNESİ ----------------
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
            # ---------------- 5. BİTTİ SAHNESİ ----------------
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
            # ---------------- KAYNAK TANIMLARI ----------------
            {
                "name": "Oyun Yakalama (FiveM / Game)",
                "uuid": game_cap_uuid,
                "id": "game_capture",
                "versioned_id": "game_capture",
                "settings": {
                    "capture_mode": "any_fullscreen",
                    "priority": 1,
                    "capture_overlays": False,  # ReShade Çökme Koruması
                    "hook_rate": 1,
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
        "collection_name": c_name,
        "filepath": filepath,
        "assets": {
            "start_banner": start_banner,
            "brb_banner": brb_banner,
            "end_banner": end_banner,
            "webcam_overlay": webcam_overlay,
            "chat_overlay": chat_overlay,
            "ticker_overlay": ticker_overlay
        }
    }

# ------------------------------------------------------------------------------
# 6. AI İÇERİK STRATEJİSİ & YAYIN FİKİRLERİ
# ------------------------------------------------------------------------------
def generate_ai_stream_strategy(channel_name="Ripleytia", game_type="FiveM / GTA V", api_key=""):
    """
    Kanal adına ve oyun türüne göre etkileşim artıran yayın başlıkları, anket fikirleri ve trend stratejiler üretir.
    """
    if api_key and api_key.strip():
        try:
            prompt = f"""
            Sen profesyonel bir espor yayıncısı ve canlı yayın danışmanısın.
            Kanal Adı: {channel_name}
            Oyun / Kategori: {game_type}

            Aşağıdaki alanları içeren Türkçe JSON döndür:
            {{
                "titles": ["3 adet dikkat çekici yayın başlığı"],
                "polls": ["2 adet izleyici anket sorusu"],
                "challenges": ["2 adet yayın içi etkileşim görevi / ceza challenge"],
                "advice": "Yayın akıcılığı ve etkileşim için 2 cümlelik profesyonel taktik"
            }}
            """
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            resp = requests.post(url, json=body, timeout=8)
            if resp.status_code == 200:
                txt = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(txt)
        except Exception:
            pass

    # Dahili Akıllı Kural Motoru Fallback
    return {
        "titles": [
            f"🔥 {channel_name.upper()} İLE {game_type.upper()} • SIFIR KARE KAYBI & FULL FPS!",
            f"⚡ YAYINDAYIZ! {channel_name} • Rekabetçi Kaos & Sohbet",
            f"🎯 1080P60 AKICI YAYIN • {channel_name} ile Dereceli / Macera"
        ],
        "polls": [
            "Bugün hangi silahı / taktiği deneyelim?",
            "Yayın sonunda topluluk etkinliği / özel lobi yapılsın mı?"
        ],
        "challenges": [
            "Öldüğünde 10 şınav çek / su molası ver.",
            "Chat'in seçeceği mod veya arabayla görevi tamamla."
        ],
        "advice": f"Yayın başlangıcında ilk 10 dakika sohbet sahnesini kullanarak izleyicilerin toplanmasını bekleyin. {game_type} oynarken NVENC kodlayıcısını ve 8000 kbps'yi koruyun."
    }
