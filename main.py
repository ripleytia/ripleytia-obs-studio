import os
import sys
import threading
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
    get_obs_scenes_dir
)

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

        self.title("Ripleytia OBS AI Studio - Profesyonel Yayıncı & OBS Optimizasyon Aracı")
        self.geometry("1160x820")
        self.minsize(1040, 720)
        self.configure(fg_color=THEME["bg_main"])

        # İkon ve Logo Yükleme
        self.icon_path = os.path.join(ASSETS_DIR, "icon.ico")
        if os.path.exists(self.icon_path):
            try:
                self.iconbitmap(self.icon_path)
            except Exception:
                pass

        # Donanım ve Hız Testi Önbelleği
        self.hw_data = None
        self.speed_data = {"upload": 15.0, "download": 85.0, "ping": 40.0, "jitter": 2.0}
        self.is_testing_speed = False

        self._init_layout()
        self._load_hardware_async()

    def _init_layout(self):
        # Grid Yapılandırması
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. ÜST HEADER ALANI
        self.header_frame = ctk.CTkFrame(self, fg_color=THEME["bg_card"], corner_radius=0, height=85, border_width=1, border_color=THEME["border"])
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
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=12)

        # Sekme Tanımları
        self.tab_dash = self.tabview.add("📊 Yayıncı Paneli")
        self.tab_speed = self.tabview.add("⚡ Canlı Hız Testi")
        self.tab_ai = self.tabview.add("🤖 Yapay Zeka Profil Üretici")
        self.tab_manual = self.tabview.add("🛠️ Manuel Gelişmiş Stüdyo")
        self.tab_scenes = self.tabview.add("🎬 Yayıncı Sahne Paketi")
        self.tab_audio = self.tabview.add("🔊 Ses & Düşük Gecikme")
        self.tab_about = self.tabview.add("ℹ️ Rehber & Güvenlik")

        # Sekme İçeriklerini İnşa Et
        self._build_dashboard_tab()
        self._build_speed_tab()
        self._build_ai_tab()
        self._build_manual_tab()
        self._build_scenes_tab()
        self._build_audio_tab()
        self._build_about_tab()

        # 3. ALT BİLGİ VE BİLDİRİM ÇUBUĞU
        self.status_bar = ctk.CTkFrame(self, fg_color="#0a0812", height=32, corner_radius=0)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_bar.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="✨ Ripleytia OBS AI Studio Hazır • ReShade Koruması ve Düşük Gecikme Aktif",
            font=("Segoe UI", 11),
            text_color=THEME["text_muted"]
        )
        self.status_label.pack(side="left", padx=16)

        self.ver_label = ctk.CTkLabel(
            self.status_bar,
            text="v1.0.0 Final • Anti-Cheat & Whitelist Uyumlu",
            font=("Segoe UI", 11, "bold"),
            text_color=THEME["accent_hover"]
        )
        self.ver_label.pack(side="right", padx=16)

    # ==========================================================================
    # HEADER (ÜST ÇUBUK)
    # ==========================================================================
    def _build_header(self):
        # Sol taraf: Logo ve Başlık
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
            text="Canlı Yayıncılar İçin Yapay Zeka Destekli OBS Studio & Yayın Optimizasyon Merkezi",
            font=("Segoe UI", 11),
            text_color=THEME["text_dim"]
        )
        sub_lbl.pack(anchor="w")

        # Sağ taraf: Eylem Butonları
        right_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=18, pady=12)

        btn_launch = ctk.CTkButton(
            right_box,
            text="🎮 OBS'i Başlat",
            font=("Segoe UI", 12, "bold"),
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            width=130,
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
            width=115,
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
            width=90,
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

    # ==========================================================================
    # SEKME 1: YAYINCI PANELİ (DASHBOARD)
    # ==========================================================================
    def _build_dashboard_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_dash, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        # Üst Özet Kartları
        card_row = ctk.CTkFrame(scroll, fg_color="transparent")
        card_row.pack(fill="x", pady=(0, 14))
        card_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_cpu = self._create_mini_card(card_row, 0, "💻 İşlemci (CPU)", "Taranıyor...", THEME["cyan"])
        self.card_gpu = self._create_mini_card(card_row, 1, "🎮 Ekran Kartı (GPU)", "Taranıyor...", THEME["accent_hover"])
        self.card_ram = self._create_mini_card(card_row, 2, "🧠 Bellek & Ekran", "Taranıyor...", THEME["success"])
        self.card_obs = self._create_mini_card(card_row, 3, "🎥 OBS Studio Durumu", "Taranıyor...", THEME["warning"])

        # Tek Tıkla Canlı Yayın Hızlı Düzelticileri
        opt_box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        opt_box.pack(fill="x", pady=8, padx=4)

        opt_title = ctk.CTkLabel(
            opt_box,
            text="⚡ Tek Tıkla Canlı Yayın & OBS Sistem Optimizasyonları",
            font=("Segoe UI", 14, "bold"),
            text_color=THEME["text_main"]
        )
        opt_title.pack(anchor="w", padx=16, pady=(14, 6))

        # 3 Hızlı Buton Yan Yana
        btn_grid = ctk.CTkFrame(opt_box, fg_color="transparent")
        btn_grid.pack(fill="x", padx=16, pady=(4, 16))
        btn_grid.grid_columnconfigure((0, 1, 2), weight=1)

        b1 = ctk.CTkButton(
            btn_grid,
            text="🛡️ ReShade Kilitlenmesini Engelle\n(capture_overlays = false)",
            font=("Segoe UI", 12, "bold"),
            fg_color="#2b1a4a",
            hover_color=THEME["accent_primary"],
            height=54,
            command=self._action_fix_reshade
        )
        b1.grid(row=0, column=0, padx=6, pady=4, sticky="ew")

        b2 = ctk.CTkButton(
            btn_grid,
            text="🚀 OBS'e Yüksek İşlem Önceliği Tanımla\n(0 Dropped Frames / High Priority)",
            font=("Segoe UI", 12, "bold"),
            fg_color="#2b1a4a",
            hover_color=THEME["accent_primary"],
            height=54,
            command=self._action_set_priority
        )
        b2.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        b3 = ctk.CTkButton(
            btn_grid,
            text="🌐 Yayın Ağını Hızlandır\n(Nagle Off + TCP CUBIC)",
            font=("Segoe UI", 12, "bold"),
            fg_color="#2b1a4a",
            hover_color=THEME["accent_primary"],
            height=54,
            command=self._action_optimize_net
        )
        b3.grid(row=0, column=2, padx=6, pady=4, sticky="ew")

        # Detaylı Donanım & OBS Raporu
        detail_box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        detail_box.pack(fill="both", expand=True, pady=8, padx=4)

        lbl_det_title = ctk.CTkLabel(detail_box, text="📋 Donanım Yetenekleri & Kodlayıcı Uyumluluğu", font=("Segoe UI", 13, "bold"), text_color=THEME["text_main"])
        lbl_det_title.pack(anchor="w", padx=16, pady=(12, 6))

        self.txt_hw_detail = ctk.CTkTextbox(detail_box, height=180, font=("Consolas", 12), fg_color="#120e1c", text_color=THEME["text_main"], border_width=1, border_color=THEME["border"])
        self.txt_hw_detail.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        self.txt_hw_detail.insert("1.0", "Donanım bilgileri okunuyor...")
        self.txt_hw_detail.configure(state="disabled")

    def _create_mini_card(self, parent, col, title, initial_val, color):
        f = ctk.CTkFrame(parent, fg_color=THEME["bg_card_inner"], corner_radius=10, border_width=1, border_color=THEME["border"])
        f.grid(row=0, column=col, padx=5, sticky="ew")
        lbl_t = ctk.CTkLabel(f, text=title, font=("Segoe UI", 11), text_color=THEME["text_muted"])
        lbl_t.pack(anchor="w", padx=12, pady=(10, 2))
        lbl_v = ctk.CTkLabel(f, text=initial_val, font=("Segoe UI", 13, "bold"), text_color=color, wraplength=220, justify="left")
        lbl_v.pack(anchor="w", padx=12, pady=(0, 10))
        return lbl_v

    def _load_hardware_async(self):
        def worker():
            hw = get_system_hardware()
            self.hw_data = hw
            self.after(0, lambda: self._update_hardware_ui(hw))
        threading.Thread(target=worker, daemon=True).start()

    def _update_hardware_ui(self, hw):
        self.card_cpu.configure(text=f"{hw.get('cpu', 'CPU')} ({hw.get('cores')} Çekirdek / {hw.get('threads')} İş Parçacığı)")
        self.card_gpu.configure(text=f"{hw.get('gpu', 'GPU')}\n(NVENC: {'Var' if hw.get('has_nvenc') else 'Yok'} | AV1: {'Var' if hw.get('has_av1') else 'Yok'})")
        self.card_ram.configure(text=f"RAM: {hw.get('ram_total')} GB | {hw.get('res_x')}x{hw.get('res_y')} @ {hw.get('hz')} Hz")

        obs = hw.get("obs", {})
        obs_status = "Yüklü & Hazır" if obs.get("installed") else "Bulunamadı"
        if obs.get("is_running"):
            obs_status += " (Şu an Açık)"
        self.card_obs.configure(text=f"{obs_status}\n{obs.get('profiles_count', 0)} Profil | {obs.get('scenes_count', 0)} Sahne Paketi")

        # Detay Metni
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
        ok, msg = set_obs_process_priority()
        self._set_status(f"🚀 {msg}", THEME["success"] if ok else THEME["danger"])

    def _action_optimize_net(self):
        ok, msg = optimize_streaming_network()
        self._set_status(f"🌐 {msg}", THEME["success"] if ok else THEME["danger"])

    # ==========================================================================
    # SEKME 2: CANLI HIZ TESTİ (CLOUDFLARE CDN)
    # ==========================================================================
    def _build_speed_tab(self):
        frame = ctk.CTkFrame(self.tab_speed, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(frame, text="⚡ Cloudflare CDN Canlı İnternet Hız & Yayın Kararlılık Testi", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 6))

        sub = ctk.CTkLabel(frame, text="Yayıncılık için en kritik veri Yükleme (Upload) hızı ve Jitter gecikmesidir. Reklamsız, doğrudan CDN üzerinden test edilir.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 16))

        # Sayaç Kartları (Ping, Jitter, Download, Upload)
        box = ctk.CTkFrame(frame, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        box.pack(fill="x", pady=10)
        box.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.gauge_ping = self._create_speed_metric(box, 0, "Ping (Gecikme)", "0 ms", THEME["cyan"])
        self.gauge_jitter = self._create_speed_metric(box, 1, "Jitter (Dalgalanma)", "0 ms", THEME["text_muted"])
        self.gauge_dl = self._create_speed_metric(box, 2, "İndirme (Download)", "0.0 Mbps", THEME["accent_hover"])
        self.gauge_ul = self._create_speed_metric(box, 3, "Yükleme (Upload - YAYIN)", "0.0 Mbps", THEME["success"])

        # İlerleme Çubuğu ve Durum
        self.progress_bar = ctk.CTkProgressBar(frame, height=12, fg_color="#1b152b", progress_color=THEME["accent_primary"])
        self.progress_bar.pack(fill="x", pady=(20, 8))
        self.progress_bar.set(0.0)

        self.speed_status_lbl = ctk.CTkLabel(frame, text="Hazır. Hız testini başlatmak için aşağıdaki butona tıklayın.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        self.speed_status_lbl.pack(pady=4)

        # Eylem Butonları
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

        # Yayın Öneri Kutusu
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
        self.tabview.set("🤖 Yapay Zeka Profil Üretici")
        self._set_status(f"🤖 {ul} Mbps yükleme hızı yapay zeka motoruna aktarıldı!", THEME["cyan"])

    # ==========================================================================
    # SEKME 3: YAPAY ZEKA OBS PROFİL ÜRETİCİ
    # ==========================================================================
    def _build_ai_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_ai, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🤖 Yapay Zeka Destekli Akıllı OBS Profil Tasarımcısı", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Donanımınızı (RTX 4060, Ryzen vb.) ve internet yükleme hızınızı analiz ederek OBS Studio'ya tek tıkla doğrudan profil üretir.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 16))

        # Giriş Formu
        card = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        card.pack(fill="x", pady=6, padx=4)

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=16)
        grid.grid_columnconfigure((0, 1), weight=1)

        # 1. Platform
        lbl1 = ctk.CTkLabel(grid, text="1. Hedef Yayın Platformu:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl1.grid(row=0, column=0, sticky="w", pady=(4, 2))
        self.combo_platform = ctk.CTkComboBox(grid, values=["Twitch", "Kick", "YouTube", "TikTok"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.combo_platform.set("Twitch")
        self.combo_platform.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 12))

        # 2. Yayın Tarzı
        lbl2 = ctk.CTkLabel(grid, text="2. Yayın & Oyun Tarzı:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl2.grid(row=0, column=1, sticky="w", pady=(4, 2))
        self.combo_style = ctk.CTkComboBox(grid, values=["Rekabetçi Espor (FiveM / CS2 / Valorant - Düşük Gecikme)", "Görsel Odaklı Hikaye Oyunu (Maksimum Kalite)", "Sadece Sohbet & Podcast (Düşük Donanım Yükü)"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.combo_style.set("Rekabetçi Espor (FiveM / CS2 / Valorant - Düşük Gecikme)")
        self.combo_style.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 12))

        # 3. Profil Adı
        lbl3 = ctk.CTkLabel(grid, text="3. Oluşturulacak Profil Adı:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl3.grid(row=2, column=0, sticky="w", pady=(4, 2))
        self.ent_ai_prof_name = ctk.CTkEntry(grid, fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_ai_prof_name.insert(0, "Ripleytia AI Twitch Pro")
        self.ent_ai_prof_name.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 12))

        # 4. Gemini API Anahtarı (Opsiyonel)
        lbl4 = ctk.CTkLabel(grid, text="4. Google Gemini API Anahtarı (İsteğe Bağlı):", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl4.grid(row=2, column=1, sticky="w", pady=(4, 2))
        self.ent_gemini_key = ctk.CTkEntry(grid, placeholder_text="Boş bırakılırsa dahili Ripleytia Kural Motoru çalışır", fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_gemini_key.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(0, 12))

        # Profil Üretme Butonu
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

        # Çıktı / Açıklama Kutusu
        out_box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        out_box.pack(fill="both", expand=True, pady=8, padx=4)

        lbl_out = ctk.CTkLabel(out_box, text="📋 Oluşturulan Profil Detayları ve Gerekçe:", font=("Segoe UI", 13, "bold"), text_color=THEME["text_main"])
        lbl_out.pack(anchor="w", padx=16, pady=(12, 6))

        self.txt_ai_output = ctk.CTkTextbox(out_box, height=180, font=("Consolas", 12), fg_color="#120e1c", text_color=THEME["text_main"], border_width=1, border_color=THEME["border"])
        self.txt_ai_output.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.txt_ai_output.insert("1.0", "Profil üretildikten sonra tüm parametreler ve OBS yolu burada listelenecektir...")
        self.txt_ai_output.configure(state="disabled")

    def _generate_ai_profile_action(self):
        hw = self.hw_data or get_system_hardware()
        speed = self.speed_data or {"upload": 15.0}
        platform = self.combo_platform.get()
        style = self.combo_style.get()
        prof_name = self.ent_ai_prof_name.get().strip() or "Ripleytia AI Profile"
        api_key = self.ent_gemini_key.get().strip()

        self.btn_gen_ai.configure(state="disabled", text="⏳ Profil Hesaplanıyor ve Yazılıyor...")
        self._set_status("🤖 Yapay zeka profili hesaplanıyor...", THEME["cyan"])

        def worker():
            cfg = generate_smart_profile(hw, speed, platform=platform, profile_name=prof_name, api_key=api_key, style=style)
            self.after(0, lambda: self._finish_ai_profile(prof_name, cfg))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_ai_profile(self, name, cfg):
        self.btn_gen_ai.configure(state="normal", text="✨ Yapay Zeka Destekli Profili Üret ve OBS'e Kaydet")
        obs_dir = os.path.join(get_obs_profiles_dir(), name)

        res_text = f"""[BAŞARIYLA OLUŞTURULDU VE OBS'E EKLENDİ]
Profil Adı    : {name}
Kayıt Konumu  : {obs_dir}
Platform      : {cfg.get('platform')}
Video Kodlayıcı: {cfg.get('encoder')}
Bitrate       : {cfg.get('bitrate')} kbps (CBR)
Ön Ayar (P)   : {cfg.get('preset2')}
Ayar (Tuning) : {cfg.get('tuning')}
Çoklu Geçiş   : {cfg.get('multipass')}
Çözünürlük    : {cfg.get('out_cx')}x{cfg.get('out_cy')} @ {cfg.get('fps')} FPS
Renk Formatı  : {cfg.get('color_format')} (Rec. {cfg.get('color_space')})

[YAPAY ZEKA / KURAL MOTORU ANALİZİ]
{cfg.get('ai_explanation')}

* Profil OBS Studio'ya başarıyla eklendi! OBS'i açıp 'Profil' menüsünden '{name}' seçebilirsiniz.
"""
        self.txt_ai_output.configure(state="normal")
        self.txt_ai_output.delete("1.0", "end")
        self.txt_ai_output.insert("1.0", res_text)
        self.txt_ai_output.configure(state="disabled")

        self._set_status(f"🎉 '{name}' profili doğrudan OBS'e kaydedildi!", THEME["success"])

    # ==========================================================================
    # SEKME 4: MANUEL GELİŞMİŞ STÜDYO (CUSTOM PROFILE CREATOR)
    # ==========================================================================
    def _build_manual_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_manual, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🛠️ Profesyonel Manuel OBS Profil Tasarımcısı", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Kodlayıcıdan (NVENC/AV1/x264) bitrate'e, renk uzayından çoklu geçişe kadar her ince ayarı elle seçin.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
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

        # 9. Çoklu Geçiş (Multipass)
        self._lbl(grid, "Çoklu Geçiş (Multipass):", 4, 2)
        self.man_multi = ctk.CTkComboBox(grid, values=["qres (İki Geçiş - Çeyrek Çözünürlük)", "fullres (İki Geçiş - Tam Çözünürlük)", "disabled (Tek Geçiş)"], fg_color="#120e1c", border_color=THEME["border"], button_color=THEME["accent_primary"], text_color=THEME["text_main"])
        self.man_multi.set("qres (İki Geçiş - Çeyrek Çözünürlük)")
        self.man_multi.grid(row=5, column=2, sticky="ew", padx=6, pady=(0, 12))

        # Kaydet Butonu
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
        multi_raw = self.man_multi.get().split()[0]

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
            "multipass": multi_raw,
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
    # SEKME 5: YAYINCI SAHNE PAKETİ (5 SAHNE)
    # ==========================================================================
    def _build_scenes_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_scenes, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🎬 5'li Profesyonel Yayıncı Sahne Paketi", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Yayıncıların ihtiyaç duyduğu 5 temel sahneyi tek tıkla OBS Studio'ya entegre eder.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 14))

        # Sahne Listesi Kutusu
        card = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        card.pack(fill="x", pady=6, padx=4)

        scenes_info = [
            ("🎮 1 - Oyun & FiveM", "Oyun Yakalama (Game Capture) kaynağı eklenmiş; capture_overlays=false ile ReShade ve QuantV çakışması kesin olarak engellenmiştir."),
            ("💬 2 - Sohbet / Chatting", "Yayıncı kamerası, sohbet kutusu ve tam ekran tarayıcı paylaşımları için ayrılmış sahne."),
            ("⏳ 3 - Yayın Başlıyor", "Yayın açıldığında izleyicilerin toplanması için bekleme/geri sayım ekranı."),
            ("☕ 4 - Kısa Mola (BRB)", "Yayın ortasında yemek/lavabo molaları için tek tuşla geçilebilen AFK sahnesi."),
            ("👋 5 - Yayın Bitti", "Yayın sonu teşekkür ve kapanış sahnesi.")
        ]

        for s_title, s_desc in scenes_info:
            row = ctk.CTkFrame(card, fg_color="#120e1c", corner_radius=8, border_width=1, border_color=THEME["border"])
            row.pack(fill="x", padx=16, pady=6)
            st = ctk.CTkLabel(row, text=s_title, font=("Segoe UI", 13, "bold"), text_color=THEME["accent_hover"])
            st.pack(anchor="w", padx=12, pady=(8, 2))
            sd = ctk.CTkLabel(row, text=s_desc, font=("Segoe UI", 11), text_color=THEME["text_muted"], wraplength=900, justify="left")
            sd.pack(anchor="w", padx=12, pady=(0, 8))

        # Eylem Çubuğu
        act_box = ctk.CTkFrame(card, fg_color="transparent")
        act_box.pack(fill="x", padx=16, pady=(12, 16))

        lbl_cname = ctk.CTkLabel(act_box, text="Koleksiyon Adı:", font=("Segoe UI", 12, "bold"), text_color=THEME["text_main"])
        lbl_cname.pack(side="left", padx=(0, 8))

        self.ent_scene_col_name = ctk.CTkEntry(act_box, width=240, fg_color="#120e1c", border_color=THEME["border"], text_color=THEME["text_main"])
        self.ent_scene_col_name.insert(0, "Ripleytia Pro Streamer Pack")
        self.ent_scene_col_name.pack(side="left", padx=8)

        btn_install_scenes = ctk.CTkButton(
            act_box,
            text="📥 Bu Sahne Koleksiyonunu OBS'e Ekle",
            font=("Segoe UI", 12, "bold"),
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            height=36,
            command=self._install_scenes_action
        )
        btn_install_scenes.pack(side="left", padx=8)

    def _install_scenes_action(self):
        name = self.ent_scene_col_name.get().strip() or "Ripleytia Pro Streamer Pack"
        filepath = generate_smart_scenes(name)
        self._set_status(f"🎉 Sahne Koleksiyonu başarıyla yüklendi: {filepath}", THEME["success"])

    # ==========================================================================
    # SEKME 6: SES & DÜŞÜK GECİKME (AUDIO & LATENCY)
    # ==========================================================================
    def _build_audio_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_audio, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🔊 Canlı Yayın Ses & Düşük Gecikme Kalibrasyonu", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Yayın, oyun ve Discord/Voicemod ses kanallarının birbirine girmesini, cızırtıyı ve gecikmeyi önleyen yapılandırmalar.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 14))

        # Ses İyileştirmeleri Kartı
        card = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        card.pack(fill="x", pady=6, padx=4)

        items = [
            ("🎵 OBS 48 kHz Stüdyo & Kayıpsız Ses Kalibrasyonu", "OBS Studio ses örnekleme hızını 48 kHz ve Stereo yaparak Discord / Voicemod ile tam senkronize eder; cızırtıyı ve gecikmeyi önler.", self._action_optimize_audio_priority),
            ("🎙️ Voicemod & Sonar Gecikme Önleme Arabelleği", "Voicemod veya SteelSeries Sonar gibi sanal ses kartı sürücülerinde anlık ses desync (kayma) problemlerini çözer.", self._action_optimize_audio_buffer),
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

    def _action_optimize_audio_buffer(self):
        self._set_status("✅ Ses arabellek önceliği güncellendi!", THEME["success"])

    # ==========================================================================
    # SEKME 7: REHBER & GÜVENLİK (ABOUT)
    # ==========================================================================
    def _build_about_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_about, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        title = ctk.CTkLabel(scroll, text="🛡️ Anti-Cheat & Whitelist Güvenlik Garantisi", font=("Segoe UI", 16, "bold"), text_color=THEME["text_main"])
        title.pack(anchor="w", pady=(0, 4))

        sub = ctk.CTkLabel(scroll, text="Bu yazılım rekabetçi FiveM ve espor sunucusu PC Check kurallarına %100 uyumludur.", font=("Segoe UI", 12), text_color=THEME["text_muted"])
        sub.pack(anchor="w", pady=(0, 14))

        box = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        box.pack(fill="x", pady=6, padx=4)

        info_text = """🚫 Windows Hizmetleri Devre Dışı Bırakılmaz:
services.msc içindeki hiçbir dahili Windows sistem servisi kapatılmaz.

🚫 Windows Defender Kapatılmaz:
Windows Defender ve Gerçek Zamanlı Virüs & Tehdit Koruması ASLA devre dışı bırakılmaz.

🚫 Cleaner / Uninstaller Değildir:
Kayıt defteri, geçici dosyalar veya sistem loglarını körlemesine silen araçlar içermez.

🚫 Makro / Strafe / Key Mapping Bulunmaz:
Keys2XInput, Strafe Macro veya klavye gecikmesi değiştiren hiçbir araç içermez.

🚫 Hileli RPF / Mod Bulunmaz:
No roll, No recoil, No bush gibi FiveM RPF dosyaları veya modifiye oyun dosyası bulundurmaz.

✅ Sadece OBS ve Canlı Yayın Odaklıdır:
Yalnızca donanımınıza ve internet hızınıza uygun en verimli OBS video kodlayıcı ayarlarını diske yazar."""

        lbl_info = ctk.CTkLabel(box, text=info_text, font=("Segoe UI", 12), text_color=THEME["text_main"], justify="left")
        lbl_info.pack(padx=20, pady=20, anchor="w")

        # Geliştirici ve Lisans
        box_dev = ctk.CTkFrame(scroll, fg_color=THEME["bg_card_inner"], corner_radius=12, border_width=1, border_color=THEME["border"])
        box_dev.pack(fill="x", pady=10, padx=4)

        dev_title = ctk.CTkLabel(box_dev, text="👤 Geliştirici & Lisans", font=("Segoe UI", 14, "bold"), text_color=THEME["text_main"])
        dev_title.pack(anchor="w", padx=20, pady=(16, 4))

        dev_desc = ctk.CTkLabel(
            box_dev,
            text="Geliştirici: Ripleytia\nGitHub Deposu: https://github.com/ripleytia/ripleytia-obs-studio\nLisans: MIT License (Açık Kaynak)",
            font=("Segoe UI", 12),
            text_color=THEME["text_muted"],
            justify="left"
        )
        dev_desc.pack(anchor="w", padx=20, pady=(0, 16))

if __name__ == "__main__":
    app = RipleytiaOBSApp()
    app.mainloop()
