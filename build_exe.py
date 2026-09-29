import subprocess
import shutil
import os

print("=== Ripleytia OBS AI Studio EXE Derlemesi Başlıyor ===")
base_dir = r"C:\Users\Ripleytia\Documents\Ripleytia_OBS_Studio"
desktop_path = r"C:\Users\Ripleytia\Desktop"
output_name = "Ripleytia OBS AI Studio"
ico_path = os.path.join(base_dir, "assets", "icon.ico")

version_path = os.path.join(base_dir, "version_info.txt")

cmd = [
    "pyinstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    f"--name={output_name}",
    f"--icon={ico_path}",
    f"--version-file={version_path}",
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
    
    # ZIP paketi oluştur
    dest_zip = os.path.join(desktop_path, f"{output_name}.zip")
    import zipfile
    with zipfile.ZipFile(dest_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(dest_exe, arcname=f"{output_name}.exe")
    print("BAŞARILI: ZIP arşivi oluşturuldu ->", dest_zip)
    
    # SHA-256 hesapla
    import hashlib
    h = hashlib.sha256()
    with open(dest_exe, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    sha256_hash = h.hexdigest()
    print("SHA-256:", sha256_hash)
else:
    print("HATA: dist içinde exe bulunamadı!")
    print("STDOUT:", res.stdout[-1500:])
    print("STDERR:", res.stderr[-1500:])
