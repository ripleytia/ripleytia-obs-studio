import ctypes
import time

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

class FILETIME(ctypes.Structure):
    _fields_ = [('dwLowDateTime', ctypes.c_ulong), ('dwHighDateTime', ctypes.c_ulong)]

class PerformanceMonitor:
    def __init__(self):
        self._prev_idle = 0
        self._prev_kernel = 0
        self._prev_user = 0
        self._prev_time = 0.0
        self._init_cpu_times()

    def _get_times(self):
        idle, kernel, user = FILETIME(), FILETIME(), FILETIME()
        ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user))
        def to_int(ft):
            return (ft.dwHighDateTime << 32) + ft.dwLowDateTime
        return to_int(idle), to_int(kernel), to_int(user)

    def _init_cpu_times(self):
        self._prev_idle, self._prev_kernel, self._prev_user = self._get_times()
        self._prev_time = time.time()

    def get_cpu_load(self):
        i2, k2, u2 = self._get_times()
        idle = i2 - self._prev_idle
        kernel = k2 - self._prev_kernel
        user = u2 - self._prev_user
        self._prev_idle, self._prev_kernel, self._prev_user = i2, k2, u2

        total = kernel + user
        if total > 0:
            cpu_pct = (1.0 - (idle / total)) * 100.0
            return round(max(0.0, min(100.0, cpu_pct)), 1)
        return 0.0

    def get_memory_info(self):
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

        total_gb = round(stat.ullTotalPhys / (1024**3), 1)
        free_gb = round(stat.ullAvailPhys / (1024**3), 1)
        used_gb = round(total_gb - free_gb, 1)
        load_pct = int(stat.dwMemoryLoad)

        return {
            "load_pct": load_pct,
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb
        }

    def check_obs_process(self):
        try:
            from engine.hardware import find_running_process
        except ImportError:
            from hardware import find_running_process
        pid = find_running_process("obs64.exe") or find_running_process("obs32.exe")
        return {
            "is_running": pid is not None,
            "pid": pid
        }

    def get_live_snapshot(self):
        cpu = self.get_cpu_load()
        mem = self.get_memory_info()
        obs = self.check_obs_process()

        status = "normal"
        alert_msg = "✅ Sistem Stabil • Yayın ve Kayıt İçin Mükemmel Durumda (0 Dropped Frames)"

        if cpu >= 85.0:
            status = "warning"
            alert_msg = f"⚠️ Yüksek CPU Kullanımı (%{cpu})! NVENC donanım kodlayıcısını seçtiğinizden emin olun."
        elif mem["load_pct"] >= 90:
            status = "warning"
            alert_msg = f"⚠️ Bellek Yükü Kritik (%{mem['load_pct']})! Arka planda gereksiz tarayıcı sekmelerini kapatın."

        return {
            "cpu_pct": cpu,
            "mem": mem,
            "obs": obs,
            "status": status,
            "alert_msg": alert_msg
        }

_monitor_instance = None
def get_monitor():
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PerformanceMonitor()
    return _monitor_instance

if __name__ == "__main__":
    mon = get_monitor()
    time.sleep(0.3)
    snap = mon.get_live_snapshot()
    print("Snapshot: CPU:", snap['cpu_pct'], "RAM Load:", snap['mem']['load_pct'], "OBS:", snap['obs'])
