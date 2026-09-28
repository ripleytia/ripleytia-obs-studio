import subprocess
import shutil
import os

print("=== Ripleytia OBS AI Studio EXE Derlemesi Başlıyor ===")
base_dir = r"C:\Users\Ripleytia\Documents\Ripleytia_OBS_Studio"
desktop_path = r"C:\Users\Ripleytia\Desktop"
output_name = "Ripleytia OBS AI Studio"
ico_path = os.path.join(base_dir, "assets", "icon.ico")

cmd = [
    "pyinstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--uac-admin",
    f"--name={output_name}",
    f"--icon={ico_path}",
    "--collect-all=customtkinter",
    "--add-data=engine;engine",
    "--add-data=assets;assets",
    os.path.join(base_dir, "main.py")
]

print("PyInstaller çalıştırılıyor:")
print(" ".join(cmd))
res = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True)
print("Return code:", res.returncode)

built_exe = os.path.join(base_dir, "dist", f"{output_name}.exe")
if os.path.exists(built_exe):
    dest_exe = os.path.join(desktop_path, f"{output_name}.exe")
    shutil.copy2(built_exe, dest_exe)
    print("BAŞARILI: Masaüstüne kopyalandı ->", dest_exe)
else:
    print("HATA: dist içinde exe bulunamadı!")
    print("STDOUT:", res.stdout[-1500:])
    print("STDERR:", res.stderr[-1500:])
