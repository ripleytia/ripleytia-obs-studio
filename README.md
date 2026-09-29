# 🎥 Ripleytia OBS AI Studio (v1.1.0 Güncel Versiyon)

<p align="center">
  <img src="assets/logo.png" width="160" alt="Ripleytia Logo" />
</p>

<p align="center">
  <b>Canlı Yayıncılar ve Rekabetçi Espor Oyuncuları İçin Yapay Zeka Destekli OBS Studio & Sahne/Overlay Stüdyosu</b><br>
  <i>Kişisel Açılış Bannerı • Şeffaf Webcam & Chat Çerçeveleri • RNNoise AI Ses Filtresi • Replay Buffer (Anında Klip) • Sıfır Kare Kaybı (0 Dropped Frames)</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20(64--bit)-blue?style=for-the-badge&logo=windows" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-blueviolet?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Anti--Cheat-100%25%20Uyumlu%20(Safe)-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Sürüm-v1.1.0%20(Güncel%20Versiyon)-purple?style=for-the-badge" />
</p>

---

## 📖 Genel Bakış

**Ripleytia OBS AI Studio (v1.1.0)**, Twitch, Kick, YouTube ve TikTok yayıncılarının sahne tasarım sürecini ve yayın kalibrasyonunu baştan sona otomatikleştiren yapay zeka destekli profesyonel bir ekosistemdir.

Kullanıcı yalnızca **Kanal Adı** ve **Tema** seçer; yapay zeka grafik motoru anında **1920x1080 Kişiselleştirilmiş Açılış Ekranı (Starting Soon Banner)**, **Şeffaf Webcam Çerçevesi**, **Sohbet Kutusu (Chatbox)** ve **Etkinlik/Hedef Şeridi** çizerek doğrudan OBS sahne koleksiyonuna entegre eder.

---

## 🚀 Sürüm 1.1.0 ile Gelen Yeni Özellikler

### 1. 🎨 Yapay Zeka Destekli Akıllı Sahne & Overlay Stüdyosu
* **Kişiselleştirilmiş Yayın Başlangıç & Mola Sahneleri:** Kanal adınızdan ve temanızdan ilham alan 1920x1080 afişler otomatik üretilerek `⏳ 3 - Yayın Başlıyor` ve `☕ 4 - Kısa Mola (BRB)` sahnelerine yerleştirilir.
* **Akıllı Webcam Çerçevesi (16:9):** 1920x1080 şeffaf PNG formatında, neon aksanlar ve kanal adı etiketli şık kamera çerçevesi.
* **Akıllı Sohbet (Chat) & Etkinlik Şeritleri:** Canlı sohbeti ekranda şık göstermek için yarı saydam cam efektli çerçeve ve ekran üstü Son Takipçi / Son Abone / Hedef barı.
* **Canlı Görsel Önizleme:** Üretilen tüm banner ve overlay'ler uygulama içerisindeki görsel galeri kartlarında anında önizlenir.

### 2. 🤖 Yapay Zeka Tabanlı RNNoise Gürültü Engelleme
* Tüm OBS sahne koleksiyonlarındaki mikrofona derin öğrenme destekli **RNNoise (AI Noise Suppression)** filtresi otomatik bağlanır; mekanik klavye sesleri, fan uğultusu ve oda yankısı sıfırlanır.

### 3. 📈 Gerçek Zamanlı Performans Monitörü (0 ms Gecikme)
* Windows `kernel32` ve `GetSystemTimes` üzerinden sıfır gecikmeli **anlık CPU %**, **RAM %** ve **OBS Studio canlı süreç takibi**.
* Sistem kaynakları aşırı yüklendiğinde yayıncıyı uyaran akıllı bildirim sistemi.

### 4. 🎬 Akıllı Replay Buffer (Anında Klip & Vurgu Kaydı)
* Tek tıkla OBS profiline 60 saniyelik Replay Buffer entegre eder. Oyun esnasında tek bir kısayol tuşuyla (F9 / Alt+F10) son 60 saniyelik harika anlar `hybrid_mp4` formatında anında diske kaydedilir.

### 5. 💡 AI İçerik & Yayın Stratejisti
* Gemini AI veya dahili kural motoru ile yayınınıza özel dikkat çekici başlıklar, izleyici anket soruları ve eğlenceli etkileşim/challenge fikirleri.

### 6. ⚡ Cloudflare CDN Canlı İnternet Hız & Kararlılık Testi
* Ping, Jitter, İndirme ve Yükleme (Upload Mbps) testi ve tek tıkla upload hızını yapay zeka profiline aktarma.

### 7. 🛡️ ReShade Koruması & Yüksek İşlem Önceliği
* Oyun Yakalama kaynaklarında `capture_overlays = false` yaparak FiveM / GTA V çökmesini engeller.
* OBS Studio'nun yerel `global.ini` dosyasına `ProcessPriority=High` tanımlayarak ağır oyun çatışmalarında sıfır kare kaybı (0 Dropped Frames) sağlar.

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
  b34dd4b55c6b4454fe77b47fee21efe16ec645125d2463e99c831d691ff62999
  ```
* **VirusTotal Raporu:** [VirusTotal Doğrulama Bağlantısı](https://www.virustotal.com/gui/file/b34dd4b55c6b4454fe77b47fee21efe16ec645125d2463e99c831d691ff62999)

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
│   ├── obs_engine.py       # OBS profil, sahne, replay buffer ve ses motoru
│   ├── ai_designer.py      # AI Banner, Webcam, Chat, Ticker & Sahne Tasarım Motoru
│   └── performance_monitor.py # 0 ms gecikmeli CPU, RAM & OBS süreç monitörü
├── main.py                 # CustomTkinter 8 sekmeli modern grafik arayüzü
├── build_exe.py            # PyInstaller derleme betiği
├── version_info.txt        # Windows PE binary sürüm bilgisi (v1.1.0)
├── .gitignore              # Git yoksayma kuralları
└── README.md               # Detaylı dokümantasyon
```

---

## 👤 Geliştirici & Lisans

* **Geliştirici:** Ripleytia
* **Lisans:** [MIT License](LICENSE)
* **Destek & Geri Bildirim:** Her türlü öneri veya hata bildirimi için [Issues](../../issues) bölümünü kullanabilirsiniz.
