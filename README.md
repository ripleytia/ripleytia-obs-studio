# 🎥 Ripleytia OBS AI Studio (v1.7.0 Güncel Versiyon)

<p align="center">
  <img src="assets/logo.png" width="160" alt="Ripleytia Logo" />
</p>

<p align="center">
  <b>Canlı Yayıncılar ve Rekabetçi Espor Oyuncuları İçin Yapay Zeka Destekli OBS Studio & Sahne/Overlay Stüdyosu</b><br>
  <i>PBR Texture Compositing • Gaussian Volumetric Glow • True 3D Bevels • 8K CGI Prompts • ReferenceSearchEngine</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20(64--bit)-blue?style=for-the-badge&logo=windows" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-blueviolet?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Anti--Cheat-100%25%20Uyumlu%20(Safe)-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Sürüm-v1.7.0%20(Güncel%20Versiyon)-purple?style=for-the-badge" />
</p>

---

## 📖 Genel Bakış

**Ripleytia OBS AI Studio (v1.7.0)**, grafik motorunu **Bileşen Bazlı Ayrıştırma** (Component-Based Separation) mimarisine taşıdı. Artık her overlay türü kendi bağımsız kanalından üretiliyor:

- **Açılış Ekranı:** Tam arka planlı, 3D sinematik, alpha=255 opak
- **Webcam Çerçevesi:** Merkezi tamamen boş/şeffaf, yalnızca köşe L-bracket neon çerçeveleri
- **Chat Kutusu:** Merkezi tamamen boş/şeffaf, yalnızca kenar çerçeve + başlık barı

---

## 🚀 Sürüm 1.7.0 ile Gelen Profesyonel Yenilikler


### 1. 🚀 Tam PBR (Physically Based Rendering) Motoru Devrimi
Yapay zekanın ürettiği grafikler yerel Pillow (PIL) motoruyla birleşti. Düz renkler tamamen kaldırıldı:
- **Procedural Carbon Fiber & Brushed Metal:** Çerçeveler anlık olarak fırçalanmış metal ve karbon fiber dokularla (noise algorithms) üretiliyor.
- **Image.alpha_composite Maskeleme:** Üretilen 3D PBR dokular çerçevelere maskeleme yöntemiyle kayıpsız giydiriliyor.

### 2. ✨ Hacimsel Işık (Gaussian Volumetric Glow)
Eski sahte glow çizgileri yerine gerçek ışık simülasyonu:
- 6 farklı yarıçapta (2, 6, 12, 24, 40, 60) ImageFilter.GaussianBlur katmanlanarak gerçekçi neon ışık saçılımı (bloom) elde edildi.

### 3. 🛡️ Gerçek 3D Bevel (Highlight & Shadow)
Çerçeve köşeleri artık düz çizgiler değil. İç kısma parlak beyaz ışık (Highlight), dış kısımlara koyu gölge (Shadow) atılarak derinliği olan gerçek 3D pahlı (bevel/chamfered) kenarlıklar üretiliyor.

### 4. 🧠 Gelişmiş AI Prompt Engine (Kısıtlamalar)
Stable Diffusion / Midjourney tarzı katsayılı prompt altyapısına geçildi:
- **QUALITY_PREFIX:** (Masterpiece gaming UI element:1.4), (Premium 3D CGI hardware render:1.3), (Physically Based Rendering [PBR] materials:1.2)
- **NEGATIVE_PROMPT:** Düz vektörler, MS Paint tarzı çizimler, mat renkler ve 2D konturlar KESİNLİKLE yasaklandı.

### 5. 🏗️ ComponentEsportsFactory — Bileşen Bazlı Ayrıştırma


| Bileşen | Boyut | Şeffaflık | Açıklama |
|---|---|---|---|
| `generate_opening_screen()` | 1920×1080 | ❌ Tam Opak | 3D sinematik açılış + BRB |
| `generate_webcam_overlay()` | 640×480 | ✅ Şeffaf (alpha=0) | Sadece köşe L-bracket çerçeveleri |
| `generate_chat_overlay()` | 420×600 | ✅ Şeffaf (alpha=0) | Sadece kenar + header barı |
| `generate_event_ticker()` | 1920×120 | Yarı Şeffaf | 3 segmentli etkinlik şeridi |

### 2. 🎮 Webcam Overlay — Gerçek Şeffaf PNG
- Başlangıç: `Image.new("RGBA", size, (0,0,0,0))` → tam şeffaf tuval
- Yalnızca 5 geçişli neon glow L-bracket çizgileri (köşelerde)
- Merkez: **alpha=0** (tamamen boş) — OBS'de kamerın görünür
- İç ikinci bracket katmanı, köşe aksanları ve ince dış çerçeve
- Üst orta: Kanal adı rozet etiketi (semi-transparent)

### 3. 💬 Chat Overlay — Gerçek Şeffaf PNG
- Başlangıç: `Image.new("RGBA", size, (0,0,0,0))` → tam şeffaf tuval
- 3 geçişli neon glow dış kenar
- Semi-transparent header bar (sadece üst kısım, %55 opaklık)
- Parallelogram aksanları, köşe kareler, yan vurgu çizgileri
- Merkez: **alpha=0** (tamamen boş) — Twitch/Kick chat'i görünür

### 4. 🔍 ReferenceSearchEngine — İnternet Referans Havuzu
Her bileşen için farklı kuratlı keyword havuzu (15+ kaynak her kategori):
- **Opening:** `"Valorant Champions VCT Stage Style"`, `"Riot Games Official HUD Layout"`...
- **Webcam:** `"Esports Webcam Overlay Transparent Border 3D hexagon"`, `"L-bracket corner cam frame neon"`...
- **Chat:** `"Twitch Transparent Chat Box Frame Stream Element 3D"`, `"StreamElements chat overlay transparent alpha"`...

### 5. 🎨 UE5 / Octane Render Kalite Enjeksiyonu
Her prompt'a otomatik eklenen kalite prefix'i:
> *"Genuine 3D render, Unreal Engine 5 render style, Blender 3D modeling, Octane Render, ray-traced ambient occlusion, metallic beveling, volumetric glass reflection, emissive neon hardware, hyper-realistic gaming peripheral texture, subsurface scattering, physically-based rendering PBR, photorealistic esports aesthetic."*

### 6. 🔒 Opening Ekranı Alpha Garantisi
`render_full()` artık iki kez alfa kanalını `255`'e kilitleyor:
- Doku katmanı çiziminden önce
- PNG kaydedilmeden önce
`smoke_light_leaks` gibi alfa kullanan dokular artık açılış ekranını yarı-şeffaf bırakamaz.

---

## 🔐 Güvenlik & Dosya Doğrulama

* **Dosya Adı:** `Ripleytia OBS AI Studio.exe`
* **SHA-256:**
  ```text
  c34d0adc2567bd4944c25c52466d8e246965384e6501726d512b0626e94676d1
  ```
* **VirusTotal Raporu:** [VirusTotal Doğrulama Bağlantısı](https://www.virustotal.com/gui/file/c34d0adc2567bd4944c25c52466d8e246965384e6501726d512b0626e94676d1)
* **Windows Defender:** 0 Tehdit ✅

---

## 🚀 Kurulum ve Çalıştırma

### Yöntem 1: Hazır `.exe` İle Çalıştırma (Önerilen)
1. [Releases](../../releases) bölümünden **`Ripleytia.OBS.AI.Studio.exe`** dosyasını indirin.
2. Dosyayı çalıştırın.
3. AI Sahne & Overlay Stüdyosu sekmesinden kanal adınızı girin ve oluştur!

### Yöntem 2: Kaynak Koddan Çalıştırma
```powershell
git clone https://github.com/ripleytia/ripleytia-obs-studio.git
cd ripleytia-obs-studio
pip install customtkinter pillow requests
python main.py
```

### Yöntem 3: Kendi `.exe` Dosyanızı Derleme
```powershell
python build_exe.py
```

---

## 📁 Proje Dizin Yapısı

```text
ripleytia-obs-studio/
├── assets/
│   ├── icon.ico            # Windows .ico simgesi
│   ├── logo.png            # 512x512 yüksek çözünürlüklü logo
│   ├── logo_64.png         # Başlık çubuğu için 64x64 logo
│   └── bg_dark.png         # Gothic mor arka plan
├── engine/
│   ├── hardware.py         # Donanım, encoder ve OBS tespit motoru
│   ├── speedtest.py        # Cloudflare CDN canlı hız testi motoru
│   ├── obs_engine.py       # OBS profil, sahne, replay buffer ve ses motoru
│   ├── ai_designer.py      # ComponentEsportsFactory v1.7.0
│   └── performance_monitor.py # CPU, RAM & OBS süreç monitörü
├── main.py                 # CustomTkinter 8 sekmeli arayüz
├── build_exe.py            # PyInstaller derleme betiği
├── version_info.txt        # Windows PE binary sürüm bilgisi (v1.7.0)
└── README.md               # Dokümantasyon
```

---

## 👤 Geliştirici & Lisans

* **Geliştirici:** Ripleytia
* **Lisans:** [MIT License](LICENSE)
* **Destek & Geri Bildirim:** [Issues](../../issues)
