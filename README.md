# 🎥 Ripleytia OBS AI Studio

<p align="center">
  <img src="assets/logo.png" width="160" alt="Ripleytia Logo" />
</p>

<p align="center">
  <b>Canlı Yayıncılar ve Rekabetçi Espor Oyuncuları İçin Yapay Zeka Destekli OBS Studio & Yayın Optimizasyon Merkezi</b><br>
  <i>Sıfır Kare Kaybı (0 Dropped Frames) • ReShade & FiveM Çökme Koruması • Yapay Zeka ve Kural Motoruyla Otomatik OBS Profilleri</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20(64--bit)-blue?style=for-the-badge&logo=windows" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-blueviolet?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Anti--Cheat-100%25%20Uyumlu%20(Safe)-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Sürüm-v1.0.0%20Final-purple?style=for-the-badge" />
</p>

---

## 📖 Genel Bakış

**Ripleytia OBS AI Studio**, Twitch, Kick, YouTube ve TikTok platformlarında canlı yayın yapan yayıncıların donanım ve internet bağlantılarını en yüksek verimle kullanmalarını sağlayan bağımsız, profesyonel bir OBS Studio optimizasyon ve profil üretim aracıdır.

Sıradan rehberlerin karmaşık ayarları yerine; sisteminizin donanımını (ekran kartı mimarisi, NVENC/AV1 yetenekleri, işlemci çekirdek sayısı, RAM, monitör yenileme hızı) ve Cloudflare CDN üzerinden gerçek yükleme (upload) hızınızı tarayarak doğrudan `%APPDATA%\obs-studio` içine **tek tıkla kullanıma hazır profiller ve sahne koleksiyonları** üretir.

---

## 🎯 Temel Özellikler

### 1. 📊 Yayıncı Paneli & Donanım Analizi
* **CIMInstance Derin Donanım Taraması:** CPU modeli, çekirdek/thread sayıları, ekran kartı (RTX/GTX/Radeon), toplam/boş RAM ve monitör yenileme hızı (Hz).
* **Kodlayıcı (Encoder) Yetenek Tespiti:** Sisteminizde NVIDIA NVENC H.264, Yeni Nesil AV1, HEVC, AMD AMF veya Intel QuickSync donanımsal kodlayıcılarının bulunup bulunmadığını anında raporlar.
* **OBS Studio Sağlık Denetimi:** OBS Studio'nun kurulu olup olmadığını, çalışma durumunu, mevcut profil ve sahne sayısını gösterir.

### 2. ⚡ Tek Tıkla Canlı Yayın Hızlı Düzelticileri
* 🛡️ **ReShade & FiveM Çökme Koruması:** OBS Oyun Yakalama kaynaklarında `capture_overlays = false` ayarını zorunlu kılar; böylece FiveM'de ReShade ve QuantV kullanan yayıncıların oyununun kilitlenmesini veya çökmesini kesin olarak engeller.
* 🚀 **OBS Yüksek İşlem Önceliği (High Priority):** Windows düzeyinde `obs64.exe` işlemine "Yüksek Öncelik" tanımlar. Ağır oyun çatışmalarında GPU/CPU %100 yüklense bile yayında tek bir kare düşmez (0 Dropped Frames).
* 🌐 **Yayın Ağ Hızlandırma:** Nagle algoritmasını kapatır ve TCP CUBIC tıkanıklık sağlayıcısını aktif ederek canlı yayın paketlerinin gecikmesiz iletilmesini sağlar.

### 3. ⚡ Cloudflare CDN Canlı İnternet Hız & Kararlılık Testi
* **Canlı Metrikler:** Ping (ms), Jitter (gecikme dalgalanması), İndirme (Download Mbps) ve Yükleme (Upload Mbps).
* **Yayıncı Odaklı Değerlendirme:** Yükleme hızınızı baz alarak Twitch, Kick ve YouTube için ideal bitrate değerlerini hesaplar.
* **Tek Tıkla Aktarım:** Test edilen upload hızını tek tuşla Yapay Zeka motoruna iletir.

### 4. 🤖 Yapay Zeka Destekli OBS Profil Üretici
* **Platformlar:** Twitch (Maks 8000 kbps), Kick (8500-9000 kbps), YouTube (1440p AV1 / 16000 kbps), TikTok (Dikey 1080x1920).
* **Yayın Tarzları:** Rekabetçi Espor (Düşük Gecikme), Görsel Odaklı Hikaye Oyunu (Maksimum Kalite), Sadece Sohbet/Podcast.
* **Hibrit Zeka:** Google Gemini API entegrasyonu (isteğe bağlı) veya dahili **Deep Streamer AI Rule-Engine**; donanımınıza en uygun NVENC P6/P5, Tuning HQ/LL, Multipass ve çözünürlük ayarlarını üretip doğrudan OBS'e yazar.

### 5. 🛠️ Manuel Gelişmiş Stüdyo (İnce Ayar Tasarımcısı)
* **Video Kodlayıcı:** NVENC H.264, NVENC AV1, NVENC HEVC, x264 CPU, AMD AMF, Intel QSV.
* **Bitrate:** 3000 kbps'den 25000 kbps'ye kadar serbest seçim.
* **Ön Ayar & Tuning:** P1 (En Hızlı) - P7 (En Kaliteli), High Quality, Low Latency, Ultra Low Latency.
* **Çoklu Geçiş:** Tek Geçiş, İki Geçiş (Çeyrek Çözünürlük), İki Geçiş (Tam Çözünürlük).
* **Çözünürlük & FPS:** 1080p60, 936p60 (rekabetçi espor standardı), 1440p60, 120 FPS, 144 FPS.

### 6. 🎬 5'li Profesyonel Yayıncı Sahne Paketi
Tek tıkla OBS Studio'ya profesyonel bir sahne paketi ekler:
1. `🎮 1 - Oyun & FiveM` (ReShade korumalı Oyun Yakalama, Mikrofon ve Masaüstü Sesi eklenmiş)
2. `💬 2 - Sohbet & Tarayıcı` (Kamera ve tam ekran tarayıcı)
3. `⏳ 3 - Yayın Başlıyor` (Geri sayım ve bekleme sahnesi)
4. `☕ 4 - Kısa Mola (BRB)` (AFK sahnesi)
5. `👋 5 - Yayın Bitti` (Kapanış sahnesi)

### 7. 🔊 Ses & Düşük Gecikme Kalibrasyonu
* Windows Ses Zamanlayıcı Önceliğini `High` yapar (MMCSS Audio Priority).
* Voicemod, SteelSeries Sonar ve Wave Link kullanıcılarında ses patlamalarını ve desync sorunlarını giderir.

---

## 🛡️ Anti-Cheat & Whitelist Güvenlik Garantisi (PC Check Uyumlu)

Bu yazılım rekabetçi FiveM ve espor sunucularındaki en katı **Anti-Cheat ve PC Check (Bilgisayar Kontrol)** kurallarına %100 uyumlu olarak geliştirilmiştir:

* 🚫 **Windows Hizmetleri Devre Dışı Bırakılmaz:** Windows'un hiçbir dahili sistem servisi (`services.msc`) kapatılmaz, bozulmaz.
* 🚫 **Defender Kapatılmaz:** Windows Defender / Gerçek Zamanlı Virüs ve Tehdit Koruması ASLA kapatılmaz. `Defender Control` vb. araçlar kullanılmaz.
* 🚫 **Cleaner & Uninstaller Değildir:** Sistemde kayıt silici, dosya silici veya uninstaller bulundurmaz.
* 🚫 **Makro / Strafe / Key Mapping İçermez:** `Keys2XInput`, `Strafe Macro` gibi hile programları içermez.
* 🚫 **Hileli RPF / Mod İçermez:** `No roll`, `No recoil`, `No bush` gibi oyun bütünlüğünü bozan modifiye dosyalar barındırmaz.
* ✅ **Sadece OBS Odaklıdır:** Yalnızca OBS Studio yapılandırma dosyalarını (`basic.ini`, `service.json`, `scenes.json`) oluşturur. Yetkili kontrollerinde güvenle kullanılabilir.

---

## 🔐 Güvenlik & Dosya Doğrulama

Uygulama açık kaynak kodludur, hiçbir reklam veya arka plan zararlısı içermez.

* **Dosya Adı:** `Ripleytia OBS AI Studio.exe`
* **SHA-256 Özeti:**
  ```text
  b06440e73b26f8459e26dc980d6512c88b65b6bb553417784cb57c472ad79658
  ```
* **VirusTotal Raporu:** [VirusTotal Doğrulama Bağlantısı](https://www.virustotal.com/gui/file/b06440e73b26f8459e26dc980d6512c88b65b6bb553417784cb57c472ad79658)

---

## 🚀 Kurulum ve Çalıştırma

### Yöntem 1: Hazır `.exe` İle Çalıştırma (Önerilen)
1. [Releases](../../releases) bölümünden **`Ripleytia.OBS.AI.Studio.exe`** veya **`Ripleytia.OBS.AI.Studio.zip`** dosyasını indirin.
2. Dosyayı çalıştırın.
3. Donanım ve hız testinizi yapın, dilediğiniz profili veya sahne paketini tek tıkla OBS'e ekleyin!

### Yöntem 2: Kaynak Koddan Çalıştırma
```powershell
# Depoyu klonlayın
git clone https://github.com/ripleytia/ripleytia-obs-studio.git
cd ripleytia-obs-studio

# Bağımlılıkları yükleyin
pip install customtkinter pillow requests

# Uygulamayı başlatın
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
│   ├── icon.ico            # Windows .ico simgesi (16x16 - 256x256)
│   ├── logo.png            # 512x512 yüksek çözünürlüklü R logosu
│   ├── logo_64.png         # Başlık çubuğu için 64x64 logo
│   └── bg_dark.png         # Düşük opaklıklı gothic mor arka plan
├── engine/
│   ├── hardware.py         # Donanım, encoder ve OBS tespit motoru
│   ├── speedtest.py        # Cloudflare CDN canlı hız testi motoru
│   └── obs_engine.py       # OBS profil, sahne ve öncelik motoru
├── main.py                 # CustomTkinter modern grafik arayüzü
├── build_exe.py            # PyInstaller derleme betiği
├── .gitignore              # Git yoksayma kuralları
└── README.md               # Detaylı dokümantasyon
```

---

## 👤 Geliştirici & Lisans

* **Geliştirici:** Ripleytia
* **Lisans:** [MIT License](LICENSE)
* **Destek & Geri Bildirim:** Her türlü öneri veya hata bildirimi için [Issues](../../issues) bölümünü kullanabilirsiniz.
