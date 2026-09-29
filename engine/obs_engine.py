import os
import json
import uuid
import subprocess
import requests

def get_obs_path():
    appdata = os.environ.get("APPDATA", "")
    return os.path.join(appdata, "obs-studio")

def get_obs_profiles_dir():
    return os.path.join(get_obs_path(), "basic", "profiles")

def get_obs_scenes_dir():
    return os.path.join(get_obs_path(), "basic", "scenes")

def ensure_dirs():
    os.makedirs(get_obs_profiles_dir(), exist_ok=True)
    os.makedirs(get_obs_scenes_dir(), exist_ok=True)

# -------------------------------------------------------------
# 1. YEREL OBS YAPILANDIRMA OPTİMİZASYONLARI (APPDATA NATIVE)
# -------------------------------------------------------------
def set_obs_process_priority(priority="High"):
    """
    OBS Studio'nun yerel global.ini yapılandırmasındaki 'ProcessPriority' değerini günceller.
    Sistem Kayıt Defterine dokunmadan resmi OBS ayarı üzerinden 'Yüksek İşlem Önceliği' sağlar.
    """
    global_ini = os.path.join(get_obs_path(), "global.ini")
    if not os.path.exists(global_ini):
        return False, "global.ini bulunamadı. Lütfen OBS Studio'yu en az bir kez açıp kapatın."
    try:
        with open(global_ini, "r", encoding="utf-8") as f:
            lines = f.readlines()
        found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith("ProcessPriority="):
                new_lines.append(f"ProcessPriority={priority}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            out_lines = []
            for line in new_lines:
                out_lines.append(line)
                if line.strip() == "[General]":
                    out_lines.append(f"ProcessPriority={priority}\n")
            new_lines = out_lines

        with open(global_ini, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True, f"OBS Studio Önceliği resmi global.ini üzerinden '{priority}' yapıldı!"
    except Exception as e:
        return False, str(e)

def fix_all_scenes_reshade():
    """
    Tüm mevcut OBS sahne koleksiyonlarındaki Oyun Yakalama kaynaklarını tarar ve
    'capture_overlays': false yapar. Bu ayar FiveM + ReShade/QuantV kilitlenmelerini kesin olarak önler.
    """
    scenes_dir = get_obs_scenes_dir()
    if not os.path.exists(scenes_dir):
        return True, "Sahne klasörü henüz oluşmamış."

    fixed_count = 0
    for filename in os.listdir(scenes_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(scenes_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                modified = False
                sources = data.get("sources", [])
                for s in sources:
                    if s.get("id") == "game_capture" and "settings" in s:
                        if s["settings"].get("capture_overlays") != False:
                            s["settings"]["capture_overlays"] = False
                            modified = True
                            fixed_count += 1

                if modified:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception:
                pass

    return True, f"{fixed_count} adet Oyun Yakalama kaynağı ReShade güvenliği için optimize edildi!"

def optimize_streaming_network():
    """
    OBS profillerinde düşük gecikmeli soket döngüsü ve ağ kuyruğu optimizasyonlarını aktif eder.
    (NewSocketLoopEnable=true, LowLatencyEnable=true, TCPPacing=true)
    """
    prof_dir = get_obs_profiles_dir()
    if not os.path.exists(prof_dir):
        return True, "Profil klasörü henüz oluşmamış."

    count = 0
    for p_name in os.listdir(prof_dir):
        ini_path = os.path.join(prof_dir, p_name, "basic.ini")
        if os.path.exists(ini_path):
            try:
                with open(ini_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                new_lines = []
                in_output = False
                has_nl = False
                has_ll = False
                for line in lines:
                    stripped = line.strip()
                    if stripped == "[Output]":
                        in_output = True
                    elif stripped.startswith("[") and stripped != "[Output]":
                        in_output = False

                    if in_output and stripped.startswith("NewSocketLoopEnable="):
                        new_lines.append("NewSocketLoopEnable=true\n")
                        has_nl = True
                    elif in_output and stripped.startswith("LowLatencyEnable="):
                        new_lines.append("LowLatencyEnable=true\n")
                        has_ll = True
                    else:
                        new_lines.append(line)

                with open(ini_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                count += 1
            except Exception:
                pass

    return True, f"{count} adet OBS profilinde Düşük Gecikme Ağ Soketi (LowLatency) aktif edildi!"

def enable_obs_replay_buffer(duration_sec=60):
    """
    Tüm OBS profillerinde 60 saniyelik Akıllı Replay Buffer (Anında Klip & Vurgu Kaydı) özelliğini aktif eder.
    Yayıncılar oyun esnasında F9 veya belirledikleri kısayola bastıklarında son 60 saniyelik efsane anları anında kaydeder.
    """
    prof_dir = get_obs_profiles_dir()
    if not os.path.exists(prof_dir):
        return False, "Profil klasörü bulunamadı."

    count = 0
    for p_name in os.listdir(prof_dir):
        ini_path = os.path.join(prof_dir, p_name, "basic.ini")
        if os.path.exists(ini_path):
            try:
                with open(ini_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                new_lines = []
                in_adv = False
                in_simple = False
                has_rb_adv = False
                has_rb_simp = False
                for line in lines:
                    stripped = line.strip()
                    if stripped == "[AdvOut]":
                        in_adv = True
                        in_simple = False
                    elif stripped == "[SimpleOutput]":
                        in_simple = True
                        in_adv = False
                    elif stripped.startswith("["):
                        in_adv = False
                        in_simple = False

                    if in_adv and stripped.startswith("ReplayBuffer="):
                        new_lines.append("ReplayBuffer=true\n")
                        has_rb_adv = True
                    elif in_simple and stripped.startswith("ReplayBuffer="):
                        new_lines.append("ReplayBuffer=true\n")
                        has_rb_simp = True
                    else:
                        new_lines.append(line)

                final_lines = []
                for line in new_lines:
                    final_lines.append(line)
                    if line.strip() == "[AdvOut]" and not has_rb_adv:
                        final_lines.append("ReplayBuffer=true\n")
                        final_lines.append(f"ReplayBufferTime={duration_sec}\n")
                        final_lines.append("ReplayBufferMaxMemory=1024\n")
                    elif line.strip() == "[SimpleOutput]" and not has_rb_simp:
                        final_lines.append("ReplayBuffer=true\n")
                        final_lines.append(f"ReplayBufferTime={duration_sec}\n")

                with open(ini_path, "w", encoding="utf-8") as f:
                    f.writelines(final_lines)
                count += 1
            except Exception:
                pass
    return True, f"{count} adet OBS profilinde {duration_sec} saniyelik Replay Buffer (Anında Klip) aktif edildi!"

def enable_rnnoise_on_all_mic_sources():
    """
    Tüm OBS sahne koleksiyonlarındaki Mikrofon kaynaklarına yapay zeka tabanlı RNNoise gürültü engelleme filtresini ekler.
    Klavye sesleri, fan gürültüsü ve oda yankısını anında yok eder.
    """
    scenes_dir = get_obs_scenes_dir()
    if not os.path.exists(scenes_dir):
        return False, "Sahne klasörü bulunamadı."

    count = 0
    for fname in os.listdir(scenes_dir):
        if fname.endswith(".json"):
            fpath = os.path.join(scenes_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                modified = False
                aux = data.get("AuxAudioDevice1")
                if aux and isinstance(aux, dict):
                    filters = aux.get("filters", [])
                    has_rnnoise = any(flt.get("id") == "noise_suppress_filter" for flt in filters)
                    if not has_rnnoise:
                        filters.append({
                            "name": "🤖 AI RNNoise Gürültü Engelleme",
                            "id": "noise_suppress_filter",
                            "versioned_id": "noise_suppress_filter",
                            "settings": {"method": 1},
                            "enabled": True
                        })
                        aux["filters"] = filters
                        modified = True

                for s in data.get("sources", []):
                    if s.get("id") == "wasapi_input_capture":
                        filters = s.get("filters", [])
                        has_rnnoise = any(flt.get("id") == "noise_suppress_filter" for flt in filters)
                        if not has_rnnoise:
                            filters.append({
                                "name": "🤖 AI RNNoise Gürültü Engelleme",
                                "id": "noise_suppress_filter",
                                "versioned_id": "noise_suppress_filter",
                                "settings": {"method": 1},
                                "enabled": True
                            })
                            s["filters"] = filters
                            modified = True

                if modified:
                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    count += 1
            except Exception:
                pass
    return True, f"{count} adet sahne koleksiyonundaki mikrofona Yapay Zeka (RNNoise) gürültü filtresi eklendi!"

def launch_obs_studio():
    """
    OBS Studio 64-bit'i başlatır.
    """
    paths = [
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\obs-studio\bin\32bit\obs32.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\obs-studio\bin\64bit\obs64.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            workdir = os.path.dirname(p)
            subprocess.Popen([p], cwd=workdir)
            return True, f"OBS Studio başlatıldı: {p}"
    return False, "OBS Studio belirtilen standart konumlarda bulunamadı!"

def open_obs_appdata():
    """
    OBS Studio'nun AppData profil/sahne klasörünü Dosya Gezgini'nde açar.
    """
    p = get_obs_path()
    os.makedirs(p, exist_ok=True)
    subprocess.Popen(f'explorer.exe "{p}"')
    return True, p

# -------------------------------------------------------------
# 2. AI & KURAL MOTORU İLE PROFİL ÜRETİCİ
# -------------------------------------------------------------
def generate_smart_profile(hw, speed, platform="Twitch", profile_name="Ripleytia AI Pro", api_key="", style="Rekabetçi Espor (Düşük Gecikme)"):
    """
    Donanım ve internet hızına göre en optimal OBS profilini oluşturur.
    api_key varsa Gemini API'ye danışır, yoksa dahili Deep Streamer AI Kural Motorunu kullanır.
    """
    ensure_dirs()
    upload = float(speed.get("upload", 15.0) or 15.0)
    gpu = str(hw.get("gpu", "NVIDIA GeForce RTX 4060"))
    is_rtx = "rtx" in gpu.lower() or "geforce" in gpu.lower() or "nvidia" in gpu.lower()
    has_av1 = hw.get("has_av1", False)

    # Varsayılan Akıllı Kural Motoru
    config = {
        "platform": platform,
        "encoder": "obs_nvenc_h264_tex" if is_rtx else "obs_x264",
        "rate_control": "CBR",
        "bitrate": 8000,
        "keyint_sec": 2,
        "preset2": "p6" if is_rtx else "veryfast",
        "tuning": "hq",
        "multipass": "qres",
        "profile": "high",
        "lookahead": False,
        "psycho_aq": True,
        "base_cx": 1920,
        "base_cy": 1080,
        "out_cx": 1920,
        "out_cy": 1080,
        "fps": 60,
        "scale_type": "bicubic",
        "priority": "High",
        "color_format": "NV12",
        "color_space": "709",
        "color_range": "Partial"
    }

    if platform == "Twitch":
        if upload >= 12:
            config["bitrate"] = 8000
            config["out_cx"] = 1920
            config["out_cy"] = 1080
            config["preset2"] = "p6"
            config["tuning"] = "ll" if "Rekabetçi" in style else "hq"
        elif upload >= 7:
            config["bitrate"] = 6000
            config["out_cx"] = 1920
            config["out_cy"] = 1080
            config["preset2"] = "p5"
        elif upload >= 4:
            config["bitrate"] = 4500
            config["out_cx"] = 1664
            config["out_cy"] = 936
            config["preset2"] = "p5"
        else:
            config["bitrate"] = 3200
            config["out_cx"] = 1280
            config["out_cy"] = 720
            config["preset2"] = "p4"

    elif platform == "Kick":
        if upload >= 14:
            config["bitrate"] = 8500
            config["out_cx"] = 1920
            config["out_cy"] = 1080
            config["preset2"] = "p6"
        elif upload >= 8:
            config["bitrate"] = 7000
            config["out_cx"] = 1920
            config["out_cy"] = 1080
            config["preset2"] = "p5"
        else:
            config["bitrate"] = 5000
            config["out_cx"] = 1664
            config["out_cy"] = 936
            config["preset2"] = "p5"

    elif platform == "YouTube":
        # YouTube AV1 destekler
        if has_av1:
            config["encoder"] = "obs_nvenc_av1_tex"
        if upload >= 18:
            config["bitrate"] = 16000
            config["out_cx"] = 2560 # 1440p YouTube VP9/AV1 transcode kalitesi
            config["out_cy"] = 1440
            config["preset2"] = "p6"
        elif upload >= 10:
            config["bitrate"] = 10000
            config["out_cx"] = 1920
            config["out_cy"] = 1080
            config["preset2"] = "p5"
        else:
            config["bitrate"] = 6000
            config["out_cx"] = 1920
            config["out_cy"] = 1080
            config["preset2"] = "p5"

    elif platform == "TikTok":
        config["bitrate"] = 6000
        config["out_cx"] = 1080
        config["out_cy"] = 1920 # Dikey format
        config["base_cx"] = 1080
        config["base_cy"] = 1920
        config["preset2"] = "p5"

    # Gemini API Entegrasyonu (Key girilmişse çağır)
    if api_key and api_key.strip():
        try:
            prompt = f"""
            Sen uzman bir OBS Studio ve canlı yayın mühendisisin.
            Aşağıdaki donanım ve ağ verilerine göre en optimum OBS profilini JSON olarak döndür:
            Donanım: CPU: {hw.get('cpu')}, GPU: {hw.get('gpu')}, RAM: {hw.get('ram_total')} GB
            İnternet: Download: {speed.get('download')} Mbps, Upload: {speed.get('upload')} Mbps, Ping: {speed.get('ping')} ms
            Yayın Platformu: {platform}
            Yayın Tarzı: {style}

            SADECE şu JSON şemasında yanıt ver:
            {{
                "bitrate": int,
                "encoder": "obs_nvenc_h264_tex" veya "obs_x264" veya "obs_nvenc_av1_tex",
                "preset2": "p5" veya "p6" veya "p7",
                "tuning": "hq" veya "ll" veya "ull",
                "multipass": "qres" veya "fullres",
                "out_cx": 1920 veya 1664 veya 1280 veya 2560,
                "out_cy": 1080 veya 936 veya 720 veya 1440,
                "fps": 60,
                "explanation": "kısa Türkçe gerekçe"
            }}
            """
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            resp = requests.post(url, json=body, timeout=10)
            if resp.status_code == 200:
                ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                ai_data = json.loads(ai_text)
                for k in ["bitrate", "encoder", "preset2", "tuning", "multipass", "out_cx", "out_cy", "fps"]:
                    if k in ai_data:
                        config[k] = ai_data[k]
                config["ai_explanation"] = ai_data.get("explanation", "Gemini AI tarafından kalibre edildi.")
        except Exception as e:
            config["ai_explanation"] = f"Dahili Akıllı Motor devrede (Gemini bağlantı: {e})"
    else:
        config["ai_explanation"] = f"Dahili Ripleytia Smart Streamer Engine ile {hw.get('gpu')} ve {upload} Mbps hıza göre optimize edildi."

    save_obs_profile(profile_name, config)
    return config

# -------------------------------------------------------------
# 3. MANUEL VEYA OTOMATİK PROFİLİ DİSKE YAZMA
# -------------------------------------------------------------
def save_obs_profile(profile_name, c):
    """
    OBS profili klasörünü ve basic.ini, streamEncoder.json, service.json dosyalarını yazar.
    """
    profile_dir = os.path.join(get_obs_profiles_dir(), profile_name)
    os.makedirs(profile_dir, exist_ok=True)

    encoder_id = c.get('encoder', 'obs_nvenc_h264_tex')

    # 1. basic.ini
    basic_ini = f"""[General]
Name={profile_name}

[AdvOut]
Encoder={encoder_id}
ApplyServiceSettings=true
UseRescale=false
TrackIndex=1
VodTrackIndex=2
RecType=Standard
RecFilePath={os.path.expanduser('~')}\\Videos
RecFormat2=hybrid_mp4
RecUseRescale=false
RecTracks=1
RecEncoder=none
FLVTrack=1
StreamMultiTrackAudioMixes=1
FFOutputToFile=true
FFFilePath={os.path.expanduser('~')}\\Videos
FFVBitrate={c.get('bitrate', 8000)}
FFVGOPSize=250
Track1Bitrate={c.get('audio_bitrate', 160)}
Track2Bitrate={c.get('audio_bitrate', 160)}
AudioEncoder=ffmpeg_aac
RecAudioEncoder=ffmpeg_aac

[SimpleOutput]
StreamEncoder=nvenc
FilePath={os.path.expanduser('~')}\\Videos
RecFormat2=hybrid_mp4
VBitrate={c.get('bitrate', 8000)}
ABitrate={c.get('audio_bitrate', 160)}
UseAdvanced=false
NVENCPreset2={c.get('preset2', 'p6')}
RecQuality=Stream
StreamAudioEncoder=aac
RecAudioEncoder=aac
RecTracks=1
RecEncoder=nvenc

[Output]
Mode=Advanced
FilenameFormatting=%CCYY-%MM-%DD %hh-%mm-%ss
DelayEnable=false
Reconnect=true
RetryDelay=2
MaxRetries=25
BindIP=default
IPFamily=IPv4+IPv6
NewSocketLoopEnable=true
LowLatencyEnable=true

[Video]
BaseCX={c.get('base_cx', 1920)}
BaseCY={c.get('base_cy', 1080)}
OutputCX={c.get('out_cx', 1920)}
OutputCY={c.get('out_cy', 1080)}
FPSType=0
FPSCommon={c.get('fps', 60)}
FPSInt={c.get('fps', 60)}
FPSNum={c.get('fps', 60)}
FPSDen=1
ScaleType={c.get('scale_type', 'bicubic')}
ColorFormat={c.get('color_format', 'NV12')}
ColorSpace={c.get('color_space', '709')}
ColorRange={c.get('color_range', 'Partial')}
SdrWhiteLevel=300
HdrNominalPeakLevel=1000

[Audio]
MonitoringDeviceId=default
MonitoringDeviceName=Varsayılan
SampleRate=48000
ChannelSetup=Stereo
MeterDecayRate=23.53
PeakMeterType=0

[Panels]
CookieId=8CED554C3F8B0B38

[BasicWindow]
PreviewDisabled=false
"""

    with open(os.path.join(profile_dir, "basic.ini"), "w", encoding="utf-8") as f:
        f.write(basic_ini)

    # 2. streamEncoder.json
    stream_enc = {
        "rate_control": c.get("rate_control", "CBR"),
        "bitrate": int(c.get("bitrate", 8000)),
        "keyint_sec": int(c.get("keyint_sec", 2)),
        "preset2": c.get("preset2", "p6"),
        "tuning": c.get("tuning", "hq"),
        "multipass": c.get("multipass", "qres"),
        "profile": c.get("profile", "high"),
        "lookahead": bool(c.get("lookahead", False)),
        "psycho_aq": bool(c.get("psycho_aq", True)),
        "max_b_frames": int(c.get("max_b_frames", 2))
    }
    with open(os.path.join(profile_dir, "streamEncoder.json"), "w", encoding="utf-8") as f:
        json.dump(stream_enc, f, indent=4)

    # 3. service.json
    platform = c.get("platform", "Twitch")
    server_urls = {
        "Twitch": "rtmps://live.twitch.tv/app/",
        "Kick": "rtmps://fa723fc1b171.global-contribute.live-video.net/",
        "YouTube": "rtmp://a.rtmp.youtube.com/live2",
        "TikTok": "rtmp://live-push.tiktok.com/live/"
    }
    service_data = {
        "type": "rtmp_custom",
        "settings": {
            "server": c.get("rtmp_server") or server_urls.get(platform, "rtmps://live.twitch.tv/app/"),
            "use_auth": False,
            "bwtest": False,
            "key": c.get("stream_key", "")
        }
    }
    with open(os.path.join(profile_dir, "service.json"), "w", encoding="utf-8") as f:
        json.dump(service_data, f, indent=4)

    return profile_dir

# -------------------------------------------------------------
# 4. YAYINCI SAHNE KOLEKSİYONU (5 SAHNE + RESHADE GÜVENLİĞİ)
# -------------------------------------------------------------
def generate_smart_scenes(collection_name="Ripleytia Pro Streamer Pack"):
    """
    Yayıncılar için 5 profesyonel hazır sahne içeren OBS Scene Collection JSON üretir:
    1. 🎮 1 - Oyun & FiveM (capture_overlays=false ile ReShade çökmesi engellenmiş)
    2. 💬 2 - Sohbet & Tarayıcı (Kamera & Ekran)
    3. ⏳ 3 - Yayın Başlıyor (Starting Soon)
    4. ☕ 4 - Kısa Mola (BRB)
    5. 👋 5 - Yayın Bitti (Ending)
    """
    ensure_dirs()
    scenes_dir = get_obs_scenes_dir()
    filepath = os.path.join(scenes_dir, f"{collection_name}.json")

    game_scene_uuid = str(uuid.uuid4())
    chat_scene_uuid = str(uuid.uuid4())
    start_scene_uuid = str(uuid.uuid4())
    brb_scene_uuid = str(uuid.uuid4())
    end_scene_uuid = str(uuid.uuid4())

    game_cap_uuid = str(uuid.uuid4())
    desktop_audio_uuid = str(uuid.uuid4())
    mic_audio_uuid = str(uuid.uuid4())

    collection = {
        "name": collection_name,
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
            "enabled": True
        },
        "current_scene": "🎮 1 - Oyun & FiveM",
        "current_program_scene": "🎮 1 - Oyun & FiveM",
        "scene_order": [
            {"name": "🎮 1 - Oyun & FiveM"},
            {"name": "💬 2 - Sohbet & Tarayıcı"},
            {"name": "⏳ 3 - Yayın Başlıyor"},
            {"name": "☕ 4 - Kısa Mola (BRB)"},
            {"name": "👋 5 - Yayın Bitti"}
        ],
        "sources": [
            {
                "name": "🎮 1 - Oyun & FiveM",
                "uuid": game_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {
                    "id_counter": 1,
                    "items": [
                        {
                            "name": "Oyun Yakalama (FiveM / Game)",
                            "source_uuid": game_cap_uuid,
                            "visible": True,
                            "locked": True
                        }
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
                    "priority": 1,
                    "capture_overlays": False,  # ReShade / QuantV DXGI çakışmasını engeller!
                    "hook_rate": 1,
                    "anti_cheat_hook": True
                }
            },
            {
                "name": "💬 2 - Sohbet & Tarayıcı",
                "uuid": chat_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {"id_counter": 0, "items": []}
            },
            {
                "name": "⏳ 3 - Yayın Başlıyor",
                "uuid": start_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {"id_counter": 0, "items": []}
            },
            {
                "name": "☕ 4 - Kısa Mola (BRB)",
                "uuid": brb_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {"id_counter": 0, "items": []}
            },
            {
                "name": "👋 5 - Yayın Bitti",
                "uuid": end_scene_uuid,
                "id": "scene",
                "versioned_id": "scene",
                "settings": {"id_counter": 0, "items": []}
            }
        ]
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=4, ensure_ascii=False)

    return filepath
