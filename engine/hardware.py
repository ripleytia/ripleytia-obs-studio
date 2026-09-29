# -*- coding: utf-8 -*-
import os
import sys
import ctypes
from ctypes import wintypes
import winreg

# Win32 Process Snapshot Constants & Structures
TH32CS_SNAPPROCESS = 0x00000002

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.c_size_t),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', wintypes.LONG),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', wintypes.WCHAR * 260)
    ]

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.c_ulong),
        ('dwMemoryLoad', ctypes.c_ulong),
        ('ullTotalPhys', ctypes.c_ulonglong),
        ('ullAvailPhys', ctypes.c_ulonglong),
        ('ullTotalPageFile', ctypes.c_ulonglong),
        ('ullAvailPageFile', ctypes.c_ulonglong),
        ('ullTotalVirtual', ctypes.c_ulonglong),
        ('ullAvailVirtual', ctypes.c_ulonglong),
        ('sullAvailExtendedVirtual', ctypes.c_ulonglong)
    ]

class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ('dmDeviceName', wintypes.WCHAR * 32),
        ('dmSpecVersion', wintypes.WORD),
        ('dmDriverVersion', wintypes.WORD),
        ('dmSize', wintypes.WORD),
        ('dmDriverExtra', wintypes.WORD),
        ('dmFields', wintypes.DWORD),
        ('dmOrientation', wintypes.SHORT),
        ('dmPaperSize', wintypes.SHORT),
        ('dmPaperLength', wintypes.SHORT),
        ('dmPaperWidth', wintypes.SHORT),
        ('dmScale', wintypes.SHORT),
        ('dmCopies', wintypes.SHORT),
        ('dmDefaultSource', wintypes.SHORT),
        ('dmPrintQuality', wintypes.SHORT),
        ('dmColor', wintypes.SHORT),
        ('dmDuplex', wintypes.SHORT),
        ('dmYResolution', wintypes.SHORT),
        ('dmTTOption', wintypes.SHORT),
        ('dmCollate', wintypes.SHORT),
        ('dmFormName', wintypes.WCHAR * 32),
        ('dmLogPixels', wintypes.WORD),
        ('dmBitsPerPel', wintypes.DWORD),
        ('dmPelsWidth', wintypes.DWORD),
        ('dmPelsHeight', wintypes.DWORD),
        ('dmDisplayFlags', wintypes.DWORD),
        ('dmDisplayFrequency', wintypes.DWORD),
    ]

def find_running_process(name):
    """
    Windows Kernel32 Toolhelp32 Snapshot kullanarak bir sürecin çalışıp çalışmadığını
    ve varsa PID değerini 0 gecikmeyle (konsol/PowerShell penceresi açmadan) sorgular.
    """
    kernel32 = ctypes.windll.kernel32
    hSnapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if hSnapshot == -1 or hSnapshot == 0:
        return None

    pe = PROCESSENTRY32W()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
    target = name.lower()
    found_pid = None

    if kernel32.Process32FirstW(hSnapshot, ctypes.byref(pe)):
        while True:
            if pe.szExeFile.lower() == target:
                found_pid = pe.th32ProcessID
                break
            if not kernel32.Process32NextW(hSnapshot, ctypes.byref(pe)):
                break

    kernel32.CloseHandle(hSnapshot)
    return found_pid

def get_obs_info():
    """
    OBS Studio'nun yüklü olduğu konumu, çalışma durumunu ve profil sayısını denetler.
    Hiçbir harici konsol süreci başlatmaz.
    """
    obs_paths = [
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\obs-studio\bin\32bit\obs32.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\obs-studio\bin\64bit\obs64.exe")
    ]

    installed = False
    exe_path = ""
    for p in obs_paths:
        if os.path.exists(p):
            installed = True
            exe_path = p
            break

    appdata = os.path.expandvars(r"%APPDATA%\obs-studio")
    appdata_exists = os.path.exists(appdata)

    # Sıfır gecikmeli yerel Win32 süreç kontrolü
    pid = find_running_process("obs64.exe") or find_running_process("obs32.exe")
    is_running = pid is not None

    profiles_count = 0
    scenes_count = 0
    if appdata_exists:
        prof_dir = os.path.join(appdata, "basic", "profiles")
        scene_dir = os.path.join(appdata, "basic", "scenes")
        if os.path.exists(prof_dir):
            profiles_count = len([d for d in os.listdir(prof_dir) if os.path.isdir(os.path.join(prof_dir, d))])
        if os.path.exists(scene_dir):
            scenes_count = len([f for f in os.listdir(scene_dir) if f.endswith(".json")])

    return {
        "installed": installed,
        "exe_path": exe_path,
        "is_running": is_running,
        "pid": pid,
        "appdata": appdata,
        "appdata_exists": appdata_exists,
        "profiles_count": profiles_count,
        "scenes_count": scenes_count
    }

def get_system_hardware():
    """
    Sistem donanım bilgilerini (CPU, GPU, RAM, Monitör, İşletim Sistemi)
    PowerShell veya harici konsol komutları OLMADAN, doğrudan Windows Registry
    ve Win32 Ctypes API'leri üzerinden mikro-saniyeler içinde tespit eder.
    Böylece başlangıçta herhangi bir PowerShell penceresi açılıp kapanmaz.
    """
    # 1. CPU Tespiti (Windows Registry)
    cpu = "Bilinmeyen İşlemci"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            cpu = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    except Exception:
        pass

    cores = os.cpu_count() or 6
    threads = cores

    # 2. RAM Tespiti (GlobalMemoryStatusEx)
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    ram_total = round(stat.ullTotalPhys / (1024**3), 1)
    ram_free = round(stat.ullAvailPhys / (1024**3), 1)

    # 3. GPU Tespiti (Windows Display Adapter Registry Enum)
    gpus = []
    try:
        base = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as k:
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(k, i)
                    i += 1
                    if sub.isdigit():
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{base}\\{sub}") as sk:
                            try:
                                g_name = winreg.QueryValueEx(sk, "DriverDesc")[0]
                                if g_name and "Basic" not in g_name and g_name not in gpus:
                                    gpus.append(g_name)
                            except Exception:
                                pass
                except OSError:
                    break
    except Exception:
        pass
    gpu = ", ".join(gpus) if gpus else "Harici GPU"

    # 4. Ekran Çözünürlüğü ve Yenileme Hızı (Hz)
    user32 = ctypes.windll.user32
    res_x = user32.GetSystemMetrics(0) or 1920
    res_y = user32.GetSystemMetrics(1) or 1080

    dm = DEVMODEW()
    dm.dmSize = ctypes.sizeof(DEVMODEW)
    hz = 60
    try:
        if user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm)):
            hz = dm.dmDisplayFrequency or 60
    except Exception:
        hz = 60

    # 5. İşletim Sistemi ve Yapı Numarası
    wv = sys.getwindowsversion()
    os_name = f"Windows {11 if wv.build >= 22000 else 10}"
    build = str(wv.build)

    # 6. Donanım Kodlayıcı Yetenekleri
    gpu_upper = gpu.upper()
    has_nvenc = any(x in gpu_upper for x in ["NVIDIA", "GEFORCE", "RTX", "GTX", "QUADRO"])
    has_amf = any(x in gpu_upper for x in ["RADEON", "AMD", "RX "])
    has_qsv = ("INTEL" in cpu.upper() or "INTEL" in gpu_upper or "ARC" in gpu_upper)
    has_av1 = any(x in gpu_upper for x in ["RTX 40", "RTX 50", "RX 7", "ARC", "AV1"])

    obs_info = get_obs_info()

    return {
        "cpu": cpu,
        "cores": cores,
        "threads": threads,
        "gpu": gpu,
        "ram_total": ram_total,
        "ram_free": ram_free,
        "os": os_name,
        "build": build,
        "res_x": res_x,
        "res_y": res_y,
        "hz": hz,
        "has_nvenc": has_nvenc,
        "has_amf": has_amf,
        "has_qsv": has_qsv,
        "has_av1": has_av1,
        "obs": obs_info,
        "success": True
    }

if __name__ == "__main__":
    hw = get_system_hardware()
    print("Tespit edilen donanım & OBS (Sıfır Konsol / 0 ms):")
    for k, v in hw.items():
        print(f"  {k}: {v}")
