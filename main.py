import os
import sys
import threading
import time
import webbrowser
import re
from PIL import Image
import customtkinter as ctk

# Engine imports
from engine.hardware import get_system_hardware, get_obs_info
from engine.speedtest import run_speed_test
from engine.obs_engine import (
    generate_smart_profile,
    generate_smart_scenes,
    save_obs_profile,
    set_obs_process_priority,
    fix_all_scenes_reshade,
    optimize_streaming_network,
    launch_obs_studio,
    open_obs_appdata,
    get_obs_profiles_dir,
    get_obs_scenes_dir,
    enable_obs_replay_buffer,
    enable_rnnoise_on_all_mic_sources
)
from engine.ai_designer import (
    build_ai_scene_collection,
    generate_channel_banner,
    generate_webcam_overlay,
    generate_chat_overlay,
    generate_event_ticker,
    generate_ai_stream_strategy,
    get_appdata_obs_assets_dir
)
from engine.performance_monitor import get_monitor

# ------------------------------------------------------------------------------
# GÖRSEL TEMA VE RENK PALETİ (GOTHIC PURPLE / RIPLEYTIA THEME)
# ------------------------------------------------------------------------------
THEME = {
    "bg_main": "#0e0b16",
    "bg_card": "#181326",
    "bg_card_inner": "#221b36",
    "border": "#3b2b5c",
    "border_focus": "#8a2be2",
    "accent_primary": "#8a2be2",      # BlueViolet
    "accent_hover": "#9d4edd",        # Light Violet
    "accent_subtle": "#371c66",
    "text_main": "#f3e8ff",
    "text_muted": "#b3a5c9",
    "text_dim": "#7d6e94",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "cyan": "#06b6d4"
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class RipleytiaOBSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ripleytia OBS AI Studio v1.6.0 (ComponentEsportsFactory: Şeffaf Webcam/Chat Overlay + UE5 Render Kalitesi) - Profesyonel Yapay Zeka Destekli Sahne & Yayın Stüdyosu")
        self.geometry("1200x860")
        self.minsize(1080, 740)
        self.configure(fg_color=THEME["bg_main"])

        # İkon Yükleme
        self.icon_path = os.path.join(ASSETS_DIR, "icon.ico")
        if os.path.exists(self.icon_path):
            try:
                self.iconbitmap(self.icon_path)
            except Exception:
                pass

        # Durum ve Önbellek
        self.hw_data = None
        self.speed_data = {"upload": 15.0, "download": 85.0, "ping": 40.0, "jitter": 2.0}
        self.is_testing_speed = False
        self.generated_previews = {}
        self.monitor = get_monitor()

        self._init_layout()
        self._load_hardware_async()
        self._start_live_monitor_loop()

    def _init_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. ÜST HEADER
        self.header_frame = ctk.CTkFrame(self, fg_color=THEME["bg_card"], corner_radius=0, height=88, border_width=1, border_color=THEME["border"])
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_propagate(False)
        self._build_header()

        # 2. SEKMELER (TABVIEW)
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=THEME["bg_card"],
            segmented_button_fg_color="#140f21",
            segmented_button_selected_color=THEME["accent_primary"],
            segmented_button_selected_hover_color=THEME["accent_hover"],
            segmented_button_unselected_color="#1d1630",
            segmented_button_unselected_hover_color="#2b2047",
            text_color=THEME["text_main"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=10)

        # Sekme İsimleri (v1.4.0 Genişletilmiş)
        self.tab_ai_scenes = self.tabview.add("🎨 AI Sahne & Overlay Stüdyosu")
        self.tab_dash = self.tabview.add("📊 Performans & Donanım")
        self.tab_speed = self.tabview.add("⚡ Canlı Hız Testi")
        self.tab_ai_prof = self.tabview.add("🤖 AI Profil & İçerik Stratejisi")
        self.tab_manual = self.tabview.add("🛠️ Manuel Gelişmiş Stüdyo")
        self.tab_media = self.tabview.add("🖼️ Medya & Varlık Kütüphanesi")
        self.tab_audio = self.tabview.add("🎙️ Ses & AI Gürültü Engelleme")
        self.tab_about = self.tabview.add("ℹ️ Rehber & Yenilikler (v1.6.0)")

        # Sekme Yapıcıları
        self._build_ai_scenes_tab()
        self._build_dashboard_tab()
        self._build_speed_tab()
        self._build_ai_profile_tab()
        self._build_manual_tab()
        self._build_media_tab()
        self._build_audio_tab()
        self._build_about_tab()

        # 3. ALT BİLGİ VE BİLDİRİM ÇUBUĞU
        self.status_bar = ctk.CTkFrame(self, fg_color="#0a0812", height=32, corner_radius=0)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_bar.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="✨ Ripleytia OBS AI Studio v1.6.0 Hazır • Şeffaf Webcam/Chat Overlay + UE5 Render Kalitesi + ReferenceSearchEngine",
            font=("Segoe UI", 11),
            text_color=THEME["text_muted"]
        )
        self.status_label.pack(side="left", padx=16)

        self.ver_label = ctk.CTkLabel(
            self.status_bar,
            text="v1.6.0 (Güncel Versiyon) • %100 PC Check & Whitelist Uyumlu",
            font=("Segoe UI", 11, "bold"),
            text_color=THEME["accent_hover"]
        )
        self.ver_label.pack(side="right", padx=16)

    # ==========================================================================
    # HEADER (ÜST BAR)
    # ==========================================================================
    def _build_header(self):
        left_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        left_box.pack(side="left", padx=18, pady=10)

        logo_64 = os.path.join(ASSETS_DIR, "logo_64.png")
        if os.path.exists(logo_64):
            try:
                img = Image.open(logo_64).resize((48, 48), Image.Resampling.LANCZOS)
                self.tk_logo = ctk.CTkImage(img, size=(48, 48))
                lbl_img = ctk.CTkLabel(left_box, image=self.tk_logo, text="")
                lbl_img.pack(side="left", padx=(0, 12))
            except Exception:
                pass

        titles = ctk.CTkFrame(left_box, fg_color="transparent")
        titles.pack(side="left")

        title_lbl = ctk.CTkLabel(
            titles,
            text="Ripleytia OBS AI Studio",
            font=("Segoe UI", 18, "bold"),
            text_color=THEME["text_main"]
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            titles,
            text="Yapay Zeka Destekli Otomatik Sahne & Overlay Üretici • v1.1.0 (Güncel Versiyon)",
            font=("Segoe UI", 11),
            text_color=THEME["text_dim"]
        )
        sub_lbl.pack(anchor="w")

        # Canlı Sistem & OBS Hapı (Center Live Pill)
        self.pill_frame = ctk.CTkFrame(self.header_frame, fg_color="#120e1f", corner_radius=20, border_width=1, border_color=THEME["border"])
        self.pill_frame.pack(side="left", padx=30, pady=14)

        self.lbl_live_metrics = ctk.CTkLabel(
            self.pill_frame,
            text="CPU: %-- • RAM: %-- • OBS: Kontrol ediliyor...",
            font=("Consolas", 11, "bold"),
            text_color=THEME["cyan"]
        )
        self.lbl_live_metrics.pack(padx=16, pady=4)

        # Sağ Taraf Butonları
        right_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=18, pady=12)

        btn_launch = ctk.CTkButton(
            right_box,
            text="🎮 OBS'i Başlat",
            font=("Segoe UI", 12, "bold"),
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            width=125,
            height=34,
            command=self._launch_obs_action
        )
        btn_launch.pack(side="left", padx=6)

        btn_appdata = ctk.CTkButton(
            right_box,
            text="📁 OBS Klasörü",
            font=("Segoe UI", 12),
            fg_color="#2b2047",
            hover_color="#3d2d66",
            width=110,
            height=34,
            command=open_obs_appdata
        )
        btn_appdata.pack(side="left", padx=6)

        btn_git = ctk.CTkButton(
            right_box,
            text="🌐 GitHub",
            font=("Segoe UI", 12),
            fg_color="#1c162e",
            hover_color="#2d224a",
            width=85,
            height=34,
            command=lambda: webbrowser.open("https://github.com/ripleytia/ripleytia-obs-studio")
        )
        btn_git.pack(side="left", padx=6)

    def _set_status(self, msg, color=None):
        self.status_label.configure(text=msg, text_color=color or THEME["text_muted"])

    def _launch_obs_action(self):
        ok, msg = launch_obs_studio()
        if ok:
            self._set_status("🚀 " + msg, THEME["success"])
        else:
            self._set_status("⚠️ " + msg, THEME["danger"])

    def _start_live_monitor_loop(self):
        def monitor_worker():
            while True:
                try:
                    snap = self.monitor.get_live_snapshot()
                    cpu_txt = f"CPU: %{snap['cpu_pct']}"
                    ram_txt = f"RAM: %{snap['mem']['load_pct']}"
                    obs_txt = f"🟢 OBS Aktif (PID: {snap['obs']['pid']})" if snap['obs']['is_running'] else "⚪ OBS Kapalı"
                    pill_text = f"{cpu_txt}  |  {ram_txt}  |  {obs_txt}"
                    color = THEME["danger"] if snap["status"] == "warning" else THEME["cyan"]
                    self.after(0, lambda t=pill_text, c=color: self.lbl_live_metrics.configure(text=t, text_color=c))
                except Exception:
                    pass
                time.sleep(1.8)

        threading.Thread(target=monitor_worker, daemon=True).start()

    # ==========================================================================
    # SEKME 1: AI AKILLI SAHNE & OVERLAY STÜDYOSU (CORE FEATURE)
    # ==========================================================================
    def _build_ai_scenes_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_ai_scenes, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🎨 Yapay Zeka Destekli Akıllı Sahne & Overlay Stüdyosu", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(
            scroll,
            text="Sadece kanal adınızı ve temanızı girin. Yapay zeka; kişiselleştirilmiş Açılış Banner'ı, Webcam Çerçevesi, Chatbox, Hedef Barı ve AI Gürültü Engelleme filtrelerini otomatik üretip OBS'e ekler.",
            font=("Segoe UI", 12),
            text_color=THEME["text_muted"],
            wraplength=1080,
            justify="left"
        )
        sub.pack(anchor="w", pady=(0, 14))

        # Giriş Kontrolleri Kartı
        form_card = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        form_card.pack(fill="x", pady=6, padx=4)

        grid = ctk.CTkFrame(form_card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=16)
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Kanal Adı
        lbl_ch = ctk.CTkLabel(grid, text="1. Yayıncı / Kanal Adınız:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_ch.grid(row=0, column=0, sticky="w", pady=(4, 2))
        self.ent_scene_channel = ctk.CTkEntry(grid, fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_scene_channel.insert(0, "Ripleytia")
        self.ent_scene_channel.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        # 2. Profesyonel Yayıncı Trendi & Stil Seçimi
        lbl_th = ctk.CTkLabel(grid, text="2. Profesyonel Yayıncı Stili (Anti-Repetition):", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_th.grid(row=0, column=1, sticky="w", pady=(4, 2))
        self.combo_theme = ctk.CTkComboBox(
            grid,
            values=[
                "🎲 Tamamen Rastgele (Profesyonel Yayıncı Trendleri)",
                "🔥 ESPOR / AGRESİF (Valorant Champions / VCT)",
                "⬛ BOLD BRUTALISM (Endüstriyel & Devasa Tipografi)",
                "⚡ TECH / MINIMALIST FUTURE (Cyberpunk HUD)",
                "💎 PREMIUM STREAM (Modern Lüks & Glassmorphism)",
                "Cyber Gothic Purple",
                "Neon Cyberpunk (Mavi/Pembe)",
                "Blood Red (Kırmızı/Siyah)",
                "Emerald Green (Yeşil/Siyah)",
                "Retro Synthwave",
                "Minimalist & Clean"
            ],
            fg_color="#120e1c",
            border_color=THEME["border"],
            button_color=THEME["accent_primary"],
            text_color=THEME["text_main"]
        )
        self.combo_theme.set("🎲 Tamamen Rastgele (Profesyonel Yayıncı Trendleri)")
        self.combo_theme.grid(row=1, column=1, sticky="ew", padx=8, pady=(0, 12))

        # 3. Oyun / Yayın Kategorisi
        lbl_cat = ctk.CTkLabel(grid, text="3. Oyun & İçerik Türü:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_cat.grid(row=0, column=2, sticky="w", pady=(4, 2))
        self.combo_game = ctk.CTkComboBox(grid, values=["FiveM / GTA V (Roleplay)", "Valorant / CS2 (Rekabetçi FPS)", "RPG / Hikaye Oyunları", "Sohbet / Just Chatting"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.combo_game.set("FiveM / GTA V (Roleplay)")
        self.combo_game.grid(row=1, column=2, sticky="ew", padx=(8, 0), pady=(0, 12))

        # 4. Doğal Dilde Özel Renk Talebi (AI Prompt)
        lbl_col_q = ctk.CTkLabel(grid, text="4. Özel Renk Talebi (Doğal Dil / AI):", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_col_q.grid(row=2, column=0, sticky="w", pady=(4, 2))
        self.ent_ai_color_query = ctk.CTkEntry(grid, placeholder_text="Örn: siberpunk moru ve neon yeşil, pastel mavi...", fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_ai_color_query.grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))

        # 5. Koleksiyon Adı & Özel Slogan
        lbl_col = ctk.CTkLabel(grid, text="5. OBS Sahne Koleksiyonu Adı:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_col.grid(row=2, column=1, sticky="w", pady=(4, 2))
        self.ent_ai_col_name = ctk.CTkEntry(grid, fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_ai_col_name.insert(0, "Ripleytia AI Stream Pack")
        self.ent_ai_col_name.grid(row=3, column=1, sticky="ew", padx=8, pady=(0, 12))

        lbl_slog = ctk.CTkLabel(grid, text="6. Açılış Ekranı Sloganı (Opsiyonel):", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_slog.grid(row=2, column=2, sticky="w", pady=(4, 2))
        self.ent_ai_slogan = ctk.CTkEntry(grid, placeholder_text="Boş bırakılırsa AI en uygun sloganı yazar...", fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_ai_slogan.grid(row=3, column=2, sticky="ew", padx=(8, 0), pady=(0, 12))

        # Üret Butonu
        self.btn_create_ai_pack = ctk.CTkButton(
            form_card,
            text="🎲 Benzersiz Yeni Tasarım Türet & OBS'e Ekle (Anti-Repetition)",
            font=("Segoe UI", 14, "bold"),
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            height=46,
            command=self._generate_full_ai_pack_action
        )
        self.btn_create_ai_pack.pack(fill="x", padx=16, pady=(4, 16))

        # Canlı Görsel Önizleme Galerisi (Live Preview Gallery)
        gal_box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        gal_box.pack(fill="both", expand=True, pady=10, padx=4)

        lbl_gal_title = ctk.CTkLabel(gal_box, text="🖼️ Oluşturulan Kişisel Grafikler & Overlay Önizlemesi", font=("Segoe UI", 13, "bold"), text_color=THEME["text_main"])
        lbl_gal_title.pack(anchor="w", padx=16, pady=(12, 4))

        self.gal_cards_frame = ctk.CTkFrame(gal_box, fg_color="transparent")
        self.gal_cards_frame.pack(fill="x", padx=16, pady=(4, 14))
        self.gal_cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.lbl_prev_start = self._create_preview_slot(self.gal_cards_frame, 0, "Açılış Ekranı (1920x1080)")
        self.lbl_prev_cam = self._create_preview_slot(self.gal_cards_frame, 1, "Webcam Çerçevesi (Şeffaf)")
        self.lbl_prev_chat = self._create_preview_slot(self.gal_cards_frame, 2, "Sohbet Kutusu Çerçevesi")

        # Bilgi ve Çıktı Raporu
        self.txt_ai_scene_log = ctk.CTkTextbox(gal_box, height=140, font=("Consolas", 12), fg_color="#120e1c", text_color=THEME["text_main"], border_width=1, border_color=THEME["border"])
        self.txt_ai_scene_log.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.txt_ai_scene_log.insert("1.0", "Yukarıdaki butona tıkladığınızda benzersiz şablon ve renk paleti hesaplanıp burada önizlenecektir...")
        self.txt_ai_scene_log.configure(state="disabled")

    def _create_preview_slot(self, parent, col, title):
        card = ctk.CTkFrame(parent, fg_color="#120e1c", corner_radius=10, border_width=1, border_color=THEME["border"])
        card.grid(row=0, column=col, padx=8, pady=4, sticky="nsew")

        t = ctk.CTkLabel(card, text=title, font=("Segoe UI", 11, "bold"), text_color=THEME["text_muted"])
        t.pack(pady=(8, 4))

        img_lbl = ctk.CTkLabel(card, text="[Önizleme Bekleniyor]", width=280, height=155, fg_color="#181326", corner_radius=6)
        img_lbl.pack(padx=10, pady=(0, 10))
        return img_lbl

    def _generate_full_ai_pack_action(self):
        ch_name = self.ent_scene_channel.get().strip() or "Ripleytia"
        raw_theme = self.combo_theme.get()
        color_query = self.ent_ai_color_query.get().strip()
        col_name = self.ent_ai_col_name.get().strip() or f"Ripleytia AI - {ch_name}"

        self.btn_create_ai_pack.configure(state="disabled", text="⏳ Eşsiz Şablon Türetiliyor & Grafikler Çiziliyor...")
        self._set_status("🎨 Yapay zeka eşsiz yayın paketini tasarlıyor...", THEME["cyan"])

        def worker():
            try:
                res = build_ai_scene_collection(
                    channel_name=ch_name,
                    theme_name=raw_theme,
                    collection_name=col_name,
                    custom_color_query=color_query
                )
                self.after(0, lambda: self._finish_ai_pack(ch_name, res))
            except Exception as exc:
                import traceback
                err_msg = f"⚠️ Grafik motoru hatası: {exc}"
                tb = traceback.format_exc()
                def _on_error():
                    self.btn_create_ai_pack.configure(
                        state="normal",
                        text="🎲 Benzersiz Yeni Tasarım Türet & OBS'e Ekle (Anti-Repetition)"
                    )
                    self._set_status(err_msg, THEME["danger"])
                    self.txt_ai_scene_log.configure(state="normal")
                    self.txt_ai_scene_log.delete("1.0", "end")
                    self.txt_ai_scene_log.insert("1.0", f"{err_msg}\n\n{tb}")
                    self.txt_ai_scene_log.configure(state="disabled")
                self.after(0, _on_error)

        threading.Thread(target=worker, daemon=True).start()

    def _finish_ai_pack(self, ch_name, res):
        self.btn_create_ai_pack.configure(
            state="normal",
            text="🎲 Benzersiz Yeni Tasarım Türet & OBS'e Ekle (Anti-Repetition)"
        )

        # --- Hata kontrolü ---
        if not res.get("success", False):
            err = res.get("error", "Bilinmeyen hata")
            tb  = res.get("traceback", "")
            self._set_status(f"⚠️ Grafik motoru hatası: {err}", THEME["danger"])
            self.txt_ai_scene_log.configure(state="normal")
            self.txt_ai_scene_log.delete("1.0", "end")
            self.txt_ai_scene_log.insert("1.0", f"HATA: {err}\n\n{tb}")
            self.txt_ai_scene_log.configure(state="disabled")
            return

        assets = res.get("assets", {})
        # Doğru key adları: build_ai_scene_collection'dan dönen dict
        start_p = assets.get("starting") or assets.get("start_banner")
        cam_p   = assets.get("webcam")   or assets.get("webcam_overlay")
        chat_p  = assets.get("chat")     or assets.get("chat_overlay")

        try:
            if start_p and os.path.exists(start_p):
                im1 = Image.open(start_p).resize((280, 155), Image.Resampling.LANCZOS)
                self.tk_p1 = ctk.CTkImage(im1, size=(280, 155))
                self.lbl_prev_start.configure(image=self.tk_p1, text="")

            if cam_p and os.path.exists(cam_p):
                im2 = Image.open(cam_p).resize((280, 155), Image.Resampling.LANCZOS)
                self.tk_p2 = ctk.CTkImage(im2, size=(280, 155))
                self.lbl_prev_cam.configure(image=self.tk_p2, text="")

            if chat_p and os.path.exists(chat_p):
                im3 = Image.open(chat_p).resize((280, 155), Image.Resampling.LANCZOS)
                self.tk_p3 = ctk.CTkImage(im3, size=(280, 155))
                self.lbl_prev_chat.configure(image=self.tk_p3, text="")
        except Exception as img_err:
            self._set_status(f"⚠️ Önizleme yüklenemedi: {img_err}", THEME["warning"])

        # plan artık bir dict olarak geliyor (MasterDesignPlan objesi değil)
        plan = res.get("plan") or {}
        if isinstance(plan, dict):
            trend_name = plan.get("trend", "Özgün Espor / Yayıncı Trendi")
            skel_name  = plan.get("skeleton", "Çok Katmanlı Geometri")
            pal_name   = plan.get("palette", "Özel")
            design_id  = plan.get("design_id", "PRO-STREAM")
            traits     = plan.get("traits", {})
        else:
            # eski obje formatı (geriye uyumluluk)
            trend_name = getattr(plan, "trend", type("", (), {"value": "Özgün"})()).value if plan else "Özgün"
            skel_name  = getattr(plan, "skeleton", type("", (), {"value": "Çok Katmanlı"})()).value if plan else "Çok Katmanlı"
            pal_name   = getattr(getattr(plan, "palette", None), "name", "Özel") if plan else "Özel"
            design_id  = getattr(plan, "design_id", "PRO-STREAM")
            traits     = {}

        ticker_p = assets.get("ticker", assets.get("ticker_overlay", ""))

        log_txt = f"""🎉 ESPORTS DESIGN FACTORY — SIFIRDAN ÜRETİLDİ!
- Tasarım Kimliği (Design ID)     : {design_id} (Anti-Repetition Onaylı)
- Tasarım Trendi (Art Direction)  : {trend_name}
- İskelet Düzeni (Skeleton Layout): {skel_name}
- Renk Paleti (Harmonizer)        : {pal_name}
- Grunge Doku Türü                : {traits.get("texture", "—")}
- Emblem Şekli                    : {traits.get("emblem", "—")}
- Tipografi Stili                 : {traits.get("typo", "—")}
- Neon Aura Ailesi                : {traits.get("aura", "—")}
- Kompozisyon Düzeni              : {traits.get("layout", "—")}
- Sahne Koleksiyonu Adı           : {res.get('collection_name')}
- OBS JSON Dosya Yolu             : {res.get('filepath')}
- Açılış Ekranı Bannerı           : {start_p}
- Webcam Çerçevesi                : {cam_p}
- Sohbet Çerçevesi                : {chat_p}
- Etkinlik Şeridi (Ticker)        : {ticker_p}

OBS Studio'yu açıp üst menüden 'Sahne Koleksiyonu' -> '{res.get('collection_name')}' seçerek yayına başlayabilirsiniz!
Her butona bastığınızda görsel hiyerarşi, doku katmanı ve kompozisyon tamamen değişir!
"""
        self.txt_ai_scene_log.configure(state="normal")
        self.txt_ai_scene_log.delete("1.0", "end")
        self.txt_ai_scene_log.insert("1.0", log_txt)
        self.txt_ai_scene_log.configure(state="disabled")

        self._set_status(
            f"🎉 '{res.get('collection_name')}' sahne paketi OBS'e eklendi! ({trend_name})",
            THEME["success"]
        )

    # ==========================================================================
    # SEKME 2: PERFORMANS MONİTÖRÜ & DONANIM (DASHBOARD)
    # ==========================================================================
    def _build_dashboard_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_dash, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        # Üst Metrik Kartları
        card_row = ctk.CTkFrame(scroll, fg_color="transparent")
        card_row.pack(fill="x", pady=(0, 14))
        card_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_cpu = self._create_mini_card(card_row, 0, "💻 İşlemci (CPU)", "Taranıyor...", THEME["cyan"])
        self.card_gpu = self._create_mini_card(card_row, 1, "🎮 Ekran Kartı (GPU)", "Taranıyor...", THEME["accent_hover"])
        self.card_ram = self._create_mini_card(card_row, 2, "🧠 Bellek & Ekran", "Taranıyor...", THEME["success"])
        self.card_obs = self._create_mini_card(card_row, 3, "🎥 OBS Studio Durumu", "Taranıyor...", THEME["warning"])

        # Canlı Kaynak Kullanım Çubukları
        live_box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        live_box.pack(fill="x", pady=8, padx=4)

        lbl_live_title = ctk.CTkLabel(live_box, text="📈 Gerçek Zamanlı Sistem & Kaynak Monitörü (0 Dropped Frames Koruması)", font=("Segoe UI", 13, "bold"), text_color=THEME["text_main"])
        lbl_live_title.pack(anchor="w", padx=16, pady=(12, 6))

        bars_grid = ctk.CTkFrame(live_box, fg_color="transparent")
        bars_grid.pack(fill="x", padx=16, pady=(4, 14))
        bars_grid.grid_columnconfigure((0, 1), weight=1)

        # CPU Bar
        self.lbl_cpu_meter = ctk.CTkLabel(bars_grid, text="İşlemci Yükü: %0.0", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        self.lbl_cpu_meter.grid(row=0, column=0, sticky="w", pady=(2, 4))
        self.bar_cpu = ctk.CTkProgressBar(bars_grid, fg_color="#181326", progress_color=THEME["accent_primary"], height=10)
        self.bar_cpu.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 8))
        self.bar_cpu.set(0.1)

        # RAM Bar
        self.lbl_ram_meter = ctk.CTkLabel(bars_grid, text="Bellek (RAM) Yükü: %0.0", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        self.lbl_ram_meter.grid(row=0, column=1, sticky="w", pady=(2, 4))
        self.bar_ram = ctk.CTkProgressBar(bars_grid, fg_color="#181326", progress_color=THEME["cyan"], height=10)
        self.bar_ram.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 8))
        self.bar_ram.set(0.5)

        # 4 Tek Tıkla Canlı Yayın Hızlı Düzelticileri
        opt_box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        opt_box.pack(fill="x", pady=8, padx=4)

        opt_title = ctk.CTkLabel(opt_box, text="⚡ Tek Tıkla Canlı Yayın & OBS Sistem Optimizasyonları", font=("Segoe UI", 13, "bold"), text_color=THEME["text_main"])
        opt_title.pack(anchor="w", padx=16, pady=(12, 6))

        btn_grid = ctk.CTkFrame(opt_box, fg_color="transparent")
        btn_grid.pack(fill="x", padx=16, pady=(4, 14))
        btn_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        b1 = ctk.CTkButton(btn_grid, text="🛡️ ReShade Kilitlenmesini Engelle\n(capture_overlays = false)", font=("Segoe UI", 11, "bold"), fg_color="#2b1a4a", hover_color=THEME["accent_primary"], height=48, command=self._action_fix_reshade)
        b1.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        b2 = ctk.CTkButton(btn_grid, text="🚀 OBS'e Yüksek İşlem Önceliği\n(global.ini ProcessPriority=High)", font=("Segoe UI", 11, "bold"), fg_color="#2b1a4a", hover_color=THEME["accent_primary"], height=48, command=self._action_set_priority)
        b2.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        b3 = ctk.CTkButton(btn_grid, text="🎬 Akıllı Replay Buffer Aktif Et\n(60s Anında Vurgu / Klip Kaydı)", font=("Segoe UI", 11, "bold"), fg_color="#2b1a4a", hover_color=THEME["accent_primary"], height=48, command=self._action_enable_replay_buffer)
        b3.grid(row=0, column=2, padx=4, pady=4, sticky="ew")

        b4 = ctk.CTkButton(btn_grid, text="🤖 Mikrofona AI RNNoise Ekle\n(Arka Plan Gürültü Engelleyici)", font=("Segoe UI", 11, "bold"), fg_color="#2b1a4a", hover_color=THEME["accent_primary"], height=48, command=self._action_enable_rnnoise)
        b4.grid(row=0, column=3, padx=4, pady=4, sticky="ew")

        # Detay Raporu
        detail_box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        detail_box.pack(fill="both", expand=True, pady=8, padx=4)

        lbl_det_title = ctk.CTkLabel(detail_box, text="📋 Donanım Taraması & Kodlayıcı (Encoder) Dökümü", font=("Segoe UI", 13, "bold"), text_color=THEME["text_main"])
        lbl_det_title.pack(anchor="w", padx=16, pady=(12, 6))

        self.txt_hw_detail = ctk.CTkTextbox(detail_box, height=160, font=("Consolas", 12), fg_color="#120e1c", text_color=THEME["text_main"], border_width=1, border_color=THEME["border"])
        self.txt_hw_detail.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self.txt_hw_detail.insert("1.0", "Donanım bilgileri okunuyor...")
        self.txt_hw_detail.configure(state="disabled")

    def _create_mini_card(self, parent, col, title, initial_val, color):
        f = ctk.CTkFrame(parent, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        f.grid(row=0, column=col, padx=4, sticky="ew")
        lbl_t = ctk.CTkLabel(f, text=title, font=("Segoe UI", 11), text_color=THEME["text_muted"])
        lbl_t.pack(anchor="w", padx=12, pady=(10, 2))
        lbl_v = ctk.CTkLabel(f, text=initial_val, font=("Segoe UI", 13, "bold"), text_color=color, wraplength=230, justify="left")
        lbl_v.pack(anchor="w", padx=12, pady=(0, 10))
        return lbl_v

    def _load_hardware_async(self):
        def worker():
            hw = get_system_hardware()
            self.hw_data = hw
            self.after(0, lambda: self._update_hardware_ui(hw))
        threading.Thread(target=worker, daemon=True).start()

    def _update_hardware_ui(self, hw):
        self.card_cpu.configure(text=f"{hw.get('cpu', 'CPU')} ({hw.get('cores')} Çekirdek / {hw.get('threads')} Thread)")
        self.card_gpu.configure(text=f"{hw.get('gpu', 'GPU')}\n(NVENC: {'Var' if hw.get('has_nvenc') else 'Yok'} | AV1: {'Var' if hw.get('has_av1') else 'Yok'})")
        self.card_ram.configure(text=f"RAM: {hw.get('ram_total')} GB | {hw.get('res_x')}x{hw.get('res_y')} @ {hw.get('hz')} Hz")

        obs = hw.get("obs", {})
        obs_status = "Yüklü & Hazır" if obs.get("installed") else "Bulunamadı"
        if obs.get("is_running"):
            obs_status += " (Şu an Açık)"
        self.card_obs.configure(text=f"{obs_status}\n{obs.get('profiles_count', 0)} Profil | {obs.get('scenes_count', 0)} Sahne Paketi")

        report = f"""[DONANIM ANALİZ RAPORU]
İşlemci: {hw.get('cpu')} ({hw.get('cores')} Çekirdek, {hw.get('threads')} Thread)
Ekran Kartı: {hw.get('gpu')}
Bellek: {hw.get('ram_total')} GB RAM (Boşta: {hw.get('ram_free')} GB)
Monitör: {hw.get('res_x')}x{hw.get('res_y')} @ {hw.get('hz')} Hz
İşletim Sistemi: {hw.get('os')} (Build {hw.get('build')})

[KODLAYICI (ENCODER) DESTEĞİ]
- NVIDIA NVENC H.264/HEVC : {'DESTEKLENİYOR (Önerilen)' if hw.get('has_nvenc') else 'Mevcut Değil'}
- Donanımsal AV1 Kodlama  : {'DESTEKLENİYOR (YouTube / Kick Yeni Nesil)' if hw.get('has_av1') else 'Mevcut Değil'}
- AMD AMF Kodlama         : {'DESTEKLENİYOR' if hw.get('has_amf') else 'Mevcut Değil'}
- Intel QuickSync (QSV)   : {'DESTEKLENİYOR' if hw.get('has_qsv') else 'Mevcut Değil'}

[OBS STUDIO DURUMU]
- Kurulum Yolu : {obs.get('exe_path') or 'Varsayılan yolda yok'}
- AppData Yolu : {obs.get('appdata')}
- Profil Sayısı: {obs.get('profiles_count')} adet profil mevcut
- Sahne Sayısı : {obs.get('scenes_count')} adet koleksiyon mevcut
"""
        self.txt_hw_detail.configure(state="normal")
        self.txt_hw_detail.delete("1.0", "end")
        self.txt_hw_detail.insert("1.0", report)
        self.txt_hw_detail.configure(state="disabled")

    def _action_fix_reshade(self):
        ok, msg = fix_all_scenes_reshade()
        self._set_status(f"🛡️ {msg}", THEME["success"] if ok else THEME["danger"])

    def _action_set_priority(self):
        ok, msg = set_obs_process_priority("High")
        self._set_status(f"🚀 {msg}", THEME["success"] if ok else THEME["danger"])

    def _action_enable_replay_buffer(self):
        ok, msg = enable_obs_replay_buffer(60)
        self._set_status(f"🎬 {msg}", THEME["success"] if ok else THEME["danger"])

    def _action_enable_rnnoise(self):
        ok, msg = enable_rnnoise_on_all_mic_sources()
        self._set_status(f"🤖 {msg}", THEME["success"] if ok else THEME["danger"])

    # ==========================================================================
    # SEKME 3: CANLI HIZ TESTİ (CLOUDFLARE CDN)
    # ==========================================================================
    def _build_speed_tab(self):
        frame = ctk.CTkFrame(self.tab_speed, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(frame, text="⚡ Cloudflare CDN Canlı İnternet Hız & Yayın Kararlılık Testi", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 6))

        sub = ctk.CTkLabel(frame, text="Yayıncılık için en kritik veri Yükleme (Upload) hızı ve Jitter gecikmesidir. Reklamsız, doğrudan CDN üzerinden test edilir.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 16))

        box = ctk.CTkFrame(frame, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        box.pack(fill="x", pady=10)
        box.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.gauge_ping = self._create_speed_metric(box, 0, "Ping (Gecikme)", "0 ms", THEME["cyan"])
        self.gauge_jitter = self._create_speed_metric(box, 1, "Jitter (Dalgalanma)", "0 ms", THEME["text_muted"])
        self.gauge_dl = self._create_speed_metric(box, 2, "İndirme (Download)", "0.0 Mbps", THEME["accent_hover"])
        self.gauge_ul = self._create_speed_metric(box, 3, "Yükleme (Upload - YAYIN)", "0.0 Mbps", THEME["success"])

        self.progress_bar = ctk.CTkProgressBar(frame, height=12, fg_color="#1b152b", progress_color=THEME["accent_primary"])
        self.progress_bar.pack(fill="x", pady=(20, 8))
        self.progress_bar.set(0.0)

        self.speed_status_lbl = ctk.CTkLabel(frame, text="Hazır. Hız testini başlatmak için aşağıdaki butona tıklayın.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        self.speed_status_lbl.pack(pady=4)

        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(pady=16)

        self.btn_run_speed = ctk.CTkButton(
            btn_box,
            text="🚀 Canlı Hız Testini Başlat",
            font=("Segoe UI", 13, "bold"),
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            width=220,
            height=40,
            command=self._start_speed_test
        )
        self.btn_run_speed.pack(side="left", padx=8)

        self.btn_apply_to_ai = ctk.CTkButton(
            btn_box,
            text="🤖 Bu Hızı Yapay Zeka Sekmesine Aktar",
            font=("Segoe UI", 13),
            fg_color="#2b1f47",
            hover_color=THEME["accent_primary"],
            width=250,
            height=40,
            command=self._apply_speed_to_ai
        )
        self.btn_apply_to_ai.pack(side="left", padx=8)

        self.speed_summary_box = ctk.CTkFrame(frame, fg_color="#120e1f", corner_radius=10, border_width=1, border_color=THEME["border"])
        self.speed_summary_box.pack(fill="both", expand=True, pady=(10, 0))

        self.speed_summary_lbl = ctk.CTkLabel(
            self.speed_summary_box,
            text="📊 Test tamamlandığında Twitch, Kick ve YouTube için ideal yayın bitrate ve çözünürlük önerileri burada görünecektir.",
            font=("Segoe UI", 12),
            text_color=THEME["text_muted"],
            justify="left"
        )
        self.speed_summary_lbl.pack(padx=20, pady=20, anchor="w")

    def _create_speed_metric(self, parent, col, title, initial_val, color):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=0, column=col, padx=10, pady=16)
        t = ctk.CTkLabel(f, text=title, font=("Segoe UI", 11), text_color=THEME["text_muted"])
        t.pack()
        v = ctk.CTkLabel(f, text=initial_val, font=("Segoe UI", 20, "bold"), text_color=color)
        v.pack(pady=(4, 0))
        return v

    def _start_speed_test(self):
        if self.is_testing_speed:
            return
        self.is_testing_speed = True
        self.btn_run_speed.configure(state="disabled", text="⏳ Test Yapılıyor...")
        self.progress_bar.set(0.0)

        def progress_cb(msg, pct):
            self.after(0, lambda: self._update_speed_progress(msg, pct))

        def worker():
            res = run_speed_test(progress_cb)
            self.speed_data = res
            self.after(0, lambda: self._finish_speed_test(res))

        threading.Thread(target=worker, daemon=True).start()

    def _update_speed_progress(self, msg, pct):
        self.progress_bar.set(pct)
        self.speed_status_lbl.configure(text=msg)

    def _finish_speed_test(self, res):
        self.is_testing_speed = False
        self.btn_run_speed.configure(state="normal", text="🚀 Canlı Hız Testini Başlat")

        if res.get("status") == "success":
            self.gauge_ping.configure(text=f"{res['ping']} ms")
            self.gauge_jitter.configure(text=f"{res['jitter']} ms")
            self.gauge_dl.configure(text=f"{res['download']} Mbps")
            self.gauge_ul.configure(text=f"{res['upload']} Mbps")

            summary = f"""🎯 HIZ & YAYIN UYGUNLUK SONUCU:
- Yükleme (Upload)   : {res['upload']} Mbps ({res['quality_score']})
- Tavsiye Bitrate    : {res['recommended_bitrate']} kbps
- Tavsiye Çözünürlük : {res['recommended_res']}
- Twitch Uyumluluğu  : {'Mükemmel (8000 kbps)' if res['upload'] >= 12 else 'İyi (6000 kbps)'}
- Kick Uyumluluğu    : {'Kusursuz (8500-9000 kbps)' if res['upload'] >= 14 else 'Stabil (7000 kbps)'}
- YouTube Uyumluluğu : {'1440p 2K Yüksek Kalite (14000+ kbps)' if res['upload'] >= 18 else '1080p60'}
"""
            self.speed_summary_lbl.configure(text=summary, text_color=THEME["text_main"])
            self._set_status(f"✅ Hız testi tamamlandı: Upload {res['upload']} Mbps", THEME["success"])
        else:
            self._set_status(f"❌ Test başarısız: {res.get('error')}", THEME["danger"])

    def _apply_speed_to_ai(self):
        ul = self.speed_data.get("upload", 15.0)
        self.tabview.set("🤖 AI Profil & İçerik Stratejisi")
        self._set_status(f"🤖 {ul} Mbps yükleme hızı yapay zeka motoruna aktarıldı!", THEME["cyan"])

    # ==========================================================================
    # SEKME 4: YAPAY ZEKA PROFİL & İÇERİK STRATEJİSİ
    # ==========================================================================
    def _build_ai_profile_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_ai_prof, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🤖 Yapay Zeka Destekli OBS Profil & İçerik Stratejisi", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Donanımınızı ve yükleme hızınızı analiz edip en kusursuz OBS profili ile birlikte dikkat çekici yayın başlıkları ve etkileşim fikirleri üretir.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 14))

        card = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        card.pack(fill="x", pady=6, padx=4)

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=16)
        grid.grid_columnconfigure((0, 1), weight=1)

        # Platform
        lbl1 = ctk.CTkLabel(grid, text="1. Hedef Yayın Platformu:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl1.grid(row=0, column=0, sticky="w", pady=(4, 2))
        self.combo_platform = ctk.CTkComboBox(grid, values=["Twitch", "Kick", "YouTube", "TikTok"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.combo_platform.set("Twitch")
        self.combo_platform.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 12))

        # Tarz
        lbl2 = ctk.CTkLabel(grid, text="2. Yayın & Oyun Tarzı:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl2.grid(row=0, column=1, sticky="w", pady=(4, 2))
        self.combo_style = ctk.CTkComboBox(grid, values=["Rekabetçi Espor (FiveM / CS2 / Valorant - Düşük Gecikme)", "Görsel Odaklı Hikaye Oyunu (Maksimum Kalite)", "Sadece Sohbet & Podcast (Düşük Donanım Yükü)"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.combo_style.set("Rekabetçi Espor (FiveM / CS2 / Valorant - Düşük Gecikme)")
        self.combo_style.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 12))

        # Profil Adı
        lbl3 = ctk.CTkLabel(grid, text="3. Oluşturulacak Profil Adı:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl3.grid(row=2, column=0, sticky="w", pady=(4, 2))
        self.ent_ai_prof_name = ctk.CTkEntry(grid, fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_ai_prof_name.insert(0, "Ripleytia AI Twitch Pro")
        self.ent_ai_prof_name.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 12))

        # Gemini API Key (Opsiyonel)
        lbl4 = ctk.CTkLabel(grid, text="4. Google Gemini API Anahtarı (Opsiyonel):", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl4.grid(row=2, column=1, sticky="w", pady=(4, 2))
        self.ent_gemini_key = ctk.CTkEntry(grid, placeholder_text="Boş bırakılırsa dahili Ripleytia Kural Motoru çalışır", fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_gemini_key.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(0, 12))

        self.btn_gen_ai = ctk.CTkButton(
            card,
            text="✨ Yapay Zeka Destekli Profili Üret ve OBS'e Kaydet",
            font=("Segoe UI", 13, "bold"),
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            height=42,
            command=self._generate_ai_profile_action
        )
        self.btn_gen_ai.pack(fill="x", padx=16, pady=(0, 16))

        # AI İçerik & Çıktı Kutuları Yan Yana
        split_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, pady=6, padx=4)
        split_frame.grid_columnconfigure((0, 1), weight=1)

        # Sol: Profil Detayları
        box_left = ctk.CTkFrame(split_frame, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        box_left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        lbl_l = ctk.CTkLabel(box_left, text="📋 Oluşturulan OBS Profil Parametreleri:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_l.pack(anchor="w", padx=14, pady=(10, 4))
        self.txt_ai_prof_out = ctk.CTkTextbox(box_left, height=220, font=("Consolas", 11), fg_color="#120e1c", text_color=THEME["text_main"], border_width=1, border_color=THEME["border"])
        self.txt_ai_prof_out.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.txt_ai_prof_out.insert("1.0", "Profil üretildikten sonra detaylar burada listelenecektir...")
        self.txt_ai_prof_out.configure(state="disabled")

        # Sağ: AI Yayın Başlıkları & Etkileşim
        box_right = ctk.CTkFrame(split_frame, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        box_right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        lbl_r = ctk.CTkLabel(box_right, text="💡 AI İçerik & Etkileşim Stratejisi:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_r.pack(anchor="w", padx=14, pady=(10, 4))
        self.txt_ai_strat_out = ctk.CTkTextbox(box_right, height=220, font=("Consolas", 11), fg_color="#120e1c", text_color=THEME["text_main"], border_width=1, border_color=THEME["border"])
        self.txt_ai_strat_out.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.txt_ai_strat_out.insert("1.0", "Yayın başlıkları ve anket fikirleri burada görünecektir...")
        self.txt_ai_strat_out.configure(state="disabled")

    def _generate_ai_profile_action(self):
        hw = self.hw_data or get_system_hardware()
        speed = self.speed_data or {"upload": 15.0}
        platform = self.combo_platform.get()
        style = self.combo_style.get()
        prof_name = self.ent_ai_prof_name.get().strip() or "Ripleytia AI Profile"
        api_key = self.ent_gemini_key.get().strip()

        self.btn_gen_ai.configure(state="disabled", text="⏳ Profil Hesaplanıyor ve Yazılıyor...")
        self._set_status("🤖 Yapay zeka profili ve içerik stratejisi hesaplanıyor...", THEME["cyan"])

        def worker():
            cfg = generate_smart_profile(hw, speed, platform=platform, profile_name=prof_name, api_key=api_key, style=style)
            strat = generate_ai_stream_strategy(channel_name="Ripleytia", game_type=style, api_key=api_key)
            self.after(0, lambda: self._finish_ai_profile(prof_name, cfg, strat))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_ai_profile(self, name, cfg, strat):
        self.btn_gen_ai.configure(state="normal", text="✨ Yapay Zeka Destekli Profili Üret ve OBS'e Kaydet")
        obs_dir = os.path.join(get_obs_profiles_dir(), name)

        res_text = f"""[BAŞARIYLA OBS'E KAYDEDİLDİ]
Profil: {name}
Konum: {obs_dir}
Platform: {cfg.get('platform')}
Kodlayıcı: {cfg.get('encoder')}
Bitrate: {cfg.get('bitrate')} kbps (CBR)
Ön Ayar: {cfg.get('preset2')} | Tuning: {cfg.get('tuning')}
Çözünürlük: {cfg.get('out_cx')}x{cfg.get('out_cy')} @ {cfg.get('fps')} FPS
Replay Buffer: 60 saniye (hybrid_mp4)

{cfg.get('ai_explanation')}
"""
        self.txt_ai_prof_out.configure(state="normal")
        self.txt_ai_prof_out.delete("1.0", "end")
        self.txt_ai_prof_out.insert("1.0", res_text)
        self.txt_ai_prof_out.configure(state="disabled")

        strat_text = f"""🔥 DİKKAT ÇEKİCİ YAYIN BAŞLIKLARI:
1. {strat.get('titles', [''])[0]}
2. {strat.get('titles', ['', ''])[1]}

💬 İZLEYİCİ ANKET FİKİRLERİ:
- {strat.get('polls', [''])[0]}

🎯 ETKİLEŞİM / CHALLENGE:
- {strat.get('challenges', [''])[0]}

💡 TAKTİK:
{strat.get('advice', '')}
"""
        self.txt_ai_strat_out.configure(state="normal")
        self.txt_ai_strat_out.delete("1.0", "end")
        self.txt_ai_strat_out.insert("1.0", strat_text)
        self.txt_ai_strat_out.configure(state="disabled")

        self._set_status(f"🎉 '{name}' profili doğrudan OBS'e kaydedildi!", THEME["success"])

    # ==========================================================================
    # SEKME 5: MANUEL GELİŞMİŞ STÜDYO (CUSTOM PROFILE CREATOR)
    # ==========================================================================
    def _build_manual_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_manual, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🛠️ Profesyonel Manuel OBS Profil Tasarımcısı", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Kodlayıcıdan (NVENC/AV1/x264) bitrate'e, Replay Buffer süresinden çoklu geçişe kadar her ince ayarı elle seçin.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 14))

        card = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        card.pack(fill="x", pady=6, padx=4)

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=16)
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Profil Adı
        self._lbl(grid, "Profil Adı:", 0, 0)
        self.man_name = ctk.CTkEntry(grid, fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.man_name.insert(0, "Ripleytia Custom Studio")
        self.man_name.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 12))

        # 2. Platform
        self._lbl(grid, "Yayın Platformu:", 0, 1)
        self.man_plat = ctk.CTkComboBox(grid, values=["Twitch", "Kick", "YouTube", "TikTok", "Özel RTMP"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_plat.set("Twitch")
        self.man_plat.grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 12))

        # 3. Video Kodlayıcı
        self._lbl(grid, "Video Kodlayıcı (Encoder):", 0, 2)
        self.man_enc = ctk.CTkComboBox(grid, values=["NVIDIA NVENC H.264 (new)", "NVIDIA NVENC AV1", "NVIDIA NVENC HEVC", "x264 (CPU Yazılımsal)", "AMD HW H.264 (AMF)", "Intel QuickSync"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_enc.set("NVIDIA NVENC H.264 (new)")
        self.man_enc.grid(row=1, column=2, sticky="ew", padx=6, pady=(0, 12))

        # 4. Bitrate
        self._lbl(grid, "Video Bitrate (kbps):", 2, 0)
        self.man_bitrate = ctk.CTkComboBox(grid, values=["3500", "4500", "6000", "7500", "8000", "8500", "10000", "14000", "18000", "25000"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_bitrate.set("8000")
        self.man_bitrate.grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 12))

        # 5. Ön Ayar (Preset)
        self._lbl(grid, "NVENC Preset (P1-P7):", 2, 1)
        self.man_preset = ctk.CTkComboBox(grid, values=["p1 (En Hızlı)", "p2", "p3", "p4 (Orta)", "p5 (Yavaş / İyi)", "p6 (Daha Yavaş / Yüksek Kalite)", "p7 (En Yavaş / Maks Kalite)"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_preset.set("p6 (Daha Yavaş / Yüksek Kalite)")
        self.man_preset.grid(row=3, column=1, sticky="ew", padx=6, pady=(0, 12))

        # 6. Ayarlama (Tuning)
        self._lbl(grid, "Tuning (Ayar):", 2, 2)
        self.man_tuning = ctk.CTkComboBox(grid, values=["hq (Yüksek Kalite)", "ll (Düşük Gecikme)", "ull (Ultra Düşük Gecikme)"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_tuning.set("hq (Yüksek Kalite)")
        self.man_tuning.grid(row=3, column=2, sticky="ew", padx=6, pady=(0, 12))

        # 7. Çözünürlük (Çıkış)
        self._lbl(grid, "Çıkış Çözünürlüğü:", 4, 0)
        self.man_res = ctk.CTkComboBox(grid, values=["1920x1080 (Full HD)", "1664x936 (936p Rekabetçi)", "2560x1440 (2K QHD)", "1280x720 (HD)", "1080x1920 (TikTok Dikey)"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_res.set("1920x1080 (Full HD)")
        self.man_res.grid(row=5, column=0, sticky="ew", padx=6, pady=(0, 12))

        # 8. FPS
        self._lbl(grid, "Yayın Kare Hızı (FPS):", 4, 1)
        self.man_fps = ctk.CTkComboBox(grid, values=["60 FPS", "120 FPS", "144 FPS", "30 FPS"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_fps.set("60 FPS")
        self.man_fps.grid(row=5, column=1, sticky="ew", padx=6, pady=(0, 12))

        # 9. Replay Buffer (Anında Klip) Süresi
        self._lbl(grid, "Replay Buffer (Klip) Süresi:", 4, 2)
        self.man_rb_time = ctk.CTkComboBox(grid, values=["60 saniye (Önerilen)", "30 saniye", "120 saniye (2 dakika)", "180 saniye"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_rb_time.set("60 saniye (Önerilen)")
        self.man_rb_time.grid(row=5, column=2, sticky="ew", padx=6, pady=(0, 12))

        btn_save = ctk.CTkButton(
            card,
            text="💾 Bu Özel OBS Profilini Oluştur ve OBS'e Ekle",
            font=("Segoe UI", 13, "bold"),
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            height=42,
            command=self._save_manual_profile_action
        )
        btn_save.pack(fill="x", padx=16, pady=(8, 16))

    def _lbl(self, parent, text, r, c):
        lbl = ctk.CTkLabel(parent, text=text, font=("Segoe UI", 11, "bold"), text_color=THEME["text_muted"])
        lbl.grid(row=r, column=c, sticky="w", padx=6, pady=(4, 2))

    def _save_manual_profile_action(self):
        name = self.man_name.get().strip() or "Ripleytia Manual Pro"
        plat = self.man_plat.get()

        enc_raw = self.man_enc.get()
        if "AV1" in enc_raw:
            enc_id = "obs_nvenc_av1_tex"
        elif "HEVC" in enc_raw:
            enc_id = "obs_nvenc_hevc_tex"
        elif "x264" in enc_raw:
            enc_id = "obs_x264"
        elif "AMF" in enc_raw:
            enc_id = "amf_h264"
        elif "QuickSync" in enc_raw:
            enc_id = "obs_qsv11"
        else:
            enc_id = "obs_nvenc_h264_tex"

        bitrate = int(self.man_bitrate.get())
        preset_raw = self.man_preset.get().split()[0]
        tuning_raw = self.man_tuning.get().split()[0]

        res_str = self.man_res.get().split()[0]
        cx, cy = res_str.split("x")
        fps_val = int(self.man_fps.get().split()[0])

        c = {
            "platform": plat,
            "encoder": enc_id,
            "rate_control": "CBR",
            "bitrate": bitrate,
            "keyint_sec": 2,
            "preset2": preset_raw,
            "tuning": tuning_raw,
            "multipass": "qres",
            "profile": "high",
            "lookahead": False,
            "psycho_aq": True,
            "base_cx": 1920,
            "base_cy": 1080,
            "out_cx": int(cx),
            "out_cy": int(cy),
            "fps": fps_val,
            "audio_bitrate": 160,
            "color_format": "NV12",
            "color_space": "709",
            "color_range": "Partial"
        }

        save_obs_profile(name, c)
        self._set_status(f"🎉 Özel OBS Profili '{name}' başarıyla oluşturuldu ve OBS'e eklendi!", THEME["success"])

    # ==========================================================================
    # SEKME 6: MEDYA & VARLIK KÜTÜPHANESİ
    # ==========================================================================
    def _build_media_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_media, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🖼️ Entegre Medya & Overlay Varlık Kütüphanesi", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Yapay zeka tarafından üretilen tüm banner, overlay ve grafik varlıklarını görüntüleyebilir, doğrudan klasörde açabilir veya sahnelere ekleyebilirsiniz.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 14))

        act_card = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        act_card.pack(fill="x", pady=6, padx=4)

        b_open_folder = ctk.CTkButton(
            act_card,
            text="📁 Varlık Klasörünü Dosya Gezgininde Aç",
            font=("Segoe UI", 12, "bold"),
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            height=38,
            command=self._open_assets_folder
        )
        b_open_folder.pack(side="left", padx=16, pady=14)

        b_refresh = ctk.CTkButton(
            act_card,
            text="🔄 Kütüphaneyi Yenile",
            font=("Segoe UI", 12),
            fg_color="#2b2047",
            hover_color="#3d2d66",
            height=38,
            command=self._refresh_media_list
        )
        b_refresh.pack(side="left", padx=8, pady=14)

        self.media_list_frame = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        self.media_list_frame.pack(fill="both", expand=True, pady=10, padx=4)

        self.txt_media_list = ctk.CTkTextbox(self.media_list_frame, height=220, font=("Consolas", 12), fg_color="#120e1c", text_color=THEME["text_main"], border_width=1, border_color=THEME["border"])
        self.txt_media_list.pack(fill="both", expand=True, padx=16, pady=16)

        self._refresh_media_list()

    def _open_assets_folder(self):
        folder = get_appdata_obs_assets_dir()
        os.system(f'explorer.exe "{folder}"')

    def _refresh_media_list(self):
        folder = get_appdata_obs_assets_dir()
        files = os.listdir(folder) if os.path.exists(folder) else []
        text = f"[KÜTÜPHANE DİZİNİ: {folder}]\n\nToplam {len(files)} adet medya varlığı bulundu:\n\n"
        for i, f in enumerate(files, 1):
            fp = os.path.join(folder, f)
            sz_kb = round(os.path.getsize(fp) / 1024, 1)
            text += f"  {i}. {f} ({sz_kb} KB)\n"
        self.txt_media_list.configure(state="normal")
        self.txt_media_list.delete("1.0", "end")
        self.txt_media_list.insert("1.0", text)
        self.txt_media_list.configure(state="disabled")

    # ==========================================================================
    # SEKME 7: SES MİKSERİ & AI GÜRÜLTÜ ENGELLEME
    # ==========================================================================
    def _build_audio_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_audio, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🎙️ Gelişmiş Ses Mikseri & AI Gürültü Engelleme (RNNoise)", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Yayın, oyun ve Discord seslerinin birbirine girmesini engeller; mikrofona yapay zeka tabanlı RNNoise filtresi bağlayarak klavye ve fan seslerini yok eder.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 14))

        card = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        card.pack(fill="x", pady=6, padx=4)

        items = [
            ("🤖 Tüm Mikrofona AI RNNoise Gürültü Filtresi Ekle", "Tüm OBS sahne koleksiyonlarındaki mikrofona derin öğrenme tabanlı RNNoise filtresi bağlar; klavye takırtısı ve fan sesini sıfırlar.", self._action_enable_rnnoise),
            ("🎵 OBS 48 kHz Stüdyo & Kayıpsız Ses Kalibrasyonu", "OBS Studio ses örnekleme hızını 48 kHz ve Stereo yaparak Discord / Voicemod ile tam senkronize eder; cızırtıyı ve gecikmeyi önler.", self._action_optimize_audio_priority),
            ("📡 OBS Düşük Gecikme Ağ Soketi (Low Latency Network Socket)", "OBS yayın soketinin ağ gecikmesini minimize eder (NewSocketLoopEnable & LowLatency).", self._action_optimize_net)
        ]

        for it_title, it_desc, it_func in items:
            row = ctk.CTkFrame(card, fg_color="#120e1c", corner_radius=8, border_width=1, border_color=THEME["border"])
            row.pack(fill="x", padx=16, pady=8)

            txts = ctk.CTkFrame(row, fg_color="transparent")
            txts.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            t = ctk.CTkLabel(txts, text=it_title, font=("Segoe UI", 13, "bold"), text_color=THEME["text_main"])
            t.pack(anchor="w")

            d = ctk.CTkLabel(txts, text=it_desc, font=("Segoe UI", 11), text_color=THEME["text_muted"], wraplength=700, justify="left")
            d.pack(anchor="w", pady=(2, 0))

            btn = ctk.CTkButton(row, text="Uygula", width=100, height=34, font=("Segoe UI", 12, "bold"), fg_color=THEME["accent_primary"], hover_color=THEME["accent_hover"], command=it_func)
            btn.pack(side="right", padx=14, pady=10)

    def _action_optimize_audio_priority(self):
        try:
            prof_dir = get_obs_profiles_dir()
            count = 0
            if os.path.exists(prof_dir):
                for p_name in os.listdir(prof_dir):
                    ini_path = os.path.join(prof_dir, p_name, "basic.ini")
                    if os.path.exists(ini_path):
                        with open(ini_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        if "SampleRate=" in content:
                            content = re.sub(r"SampleRate=\d+", "SampleRate=48000", content)
                        with open(ini_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        count += 1
            self._set_status(f"✅ {count} adet OBS profilinde ses örnekleme hızı 48 kHz Stüdyo standardına ayarlandı!", THEME["success"])
        except Exception as e:
            self._set_status(f"Hata: {e}", THEME["danger"])

    def _action_optimize_net(self):
        ok, msg = optimize_streaming_network()
        self._set_status(f"🌐 {msg}", THEME["success"] if ok else THEME["danger"])

    # ==========================================================================
    # SEKME 8: REHBER & YENİLİKLER (V1.1.0)
    # ==========================================================================
    def _build_about_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_about, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🚀 Sürüm 1.1.0 Yenilikleri & Anti-Cheat Güvencesi", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="v1.1.0 (Güncel Versiyon), canlı yayın deneyiminizi baştan sona yapay zeka ile otomatikleştirir.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 14))

        box_whatsnew = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        box_whatsnew.pack(fill="x", pady=6, padx=4)

        whatsnew_text = """🌟 SÜRÜM 1.1.0 YENİLİKLERİ:
1. 🎨 Yapay Zeka Destekli Otomatik Sahne & Overlay Stüdyosu:
   - Sadece kanal adınızı girerek 1920x1080 Kişisel Açılış Bannerı, Mola Ekranı, Şeffaf Webcam Çerçevesi, Chatbox ve Hedef Barı üretme.
   - Tüm bu grafiklerin doğrudan 5'li OBS sahne koleksiyonu JSON'una otomatik yerleştirilmesi.
2. 🤖 Yapay Zeka RNNoise Gürültü Engelleme:
   - Mikrofona bağlanan derin öğrenme filtresi ile fan, klavye ve oda yankısını anında yok etme.
3. 📈 Gerçek Zamanlı Performans Monitörü:
   - 0 ms gecikmeyle anlık CPU %, RAM % ve OBS Studio canlı süreç takibi.
4. 🎬 Akıllı Replay Buffer (Anında Klip Kaydı):
   - Tek tıkla son 60 saniyelik oyun vurgularını kaydeden Replay Buffer entegrasyonu.
5. 💡 AI İçerik & Yayın Stratejisti:
   - Kanalınıza ve oyununuza özel dikkat çekici yayın başlıkları, anket fikirleri ve challenge önerileri.
6. 🖼️ Entegre Medya Varlık Kütüphanesi."""

        lbl_wn = ctk.CTkLabel(box_whatsnew, text=whatsnew_text, font=("Segoe UI", 12), text_color=THEME["text_main"], justify="left")
        lbl_wn.pack(padx=20, pady=16, anchor="w")

        # Güvenlik Garantisi
        box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        box.pack(fill="x", pady=10, padx=4)

        info_text = """🛡️ %100 ANTICHEAT & PC CHECK UYUMLULUĞU:
* 🚫 Windows Hizmetleri Devre Dışı Bırakılmaz: services.msc içindeki hiçbir dahili Windows servisine dokunulmaz.
* 🚫 Windows Defender Kapatılmaz: Virüs ve tehdit koruması açık kalır; Defender Control vb. kullanılmaz.
* 🚫 Cleaner & Uninstaller Değildir: Sistem temizleyici veya uninstaller barındırmaz.
* 🚫 Makro / Strafe / Key Mapping İçermez: Keys2XInput veya klavye gecikme hilesi içermez.
* 🚫 Hileli RPF / Mod İçermez: No roll, No recoil, No bush gibi modifiye oyun dosyaları barındırmaz.
* ✅ Sadece OBS Odaklıdır: Yalnızca OBS Studio yapılandırma profillerini ve sahnelerini oluşturur."""

        lbl_info = ctk.CTkLabel(box, text=info_text, font=("Segoe UI", 12), text_color=THEME["text_main"], justify="left")
        lbl_info.pack(padx=20, pady=16, anchor="w")

        # Geliştirici ve Lisans
        box_dev = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        box_dev.pack(fill="x", pady=6, padx=4)

        dev_desc = ctk.CTkLabel(
            box_dev,
            text="Geliştirici: Ripleytia\nGitHub Deposu: https://github.com/ripleytia/ripleytia-obs-studio\nSürüm: v1.1.0 (Güncel Versiyon)\nLisans: MIT License (Açık Kaynak)",
            font=("Segoe UI", 12),
            text_color=THEME["text_muted"],
            justify="left"
        )
        dev_desc.pack(anchor="w", padx=20, pady=16)

if __name__ == "__main__":
    app = RipleytiaOBSApp()
    app.mainloop()
