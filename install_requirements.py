import subprocess
import os
import sys

def install_requirements(file_path="requirements.txt"):
    if not os.path.exists(file_path):
        print(f"❌ File '{file_path}' tidak ditemukan.")
        return

    print(f"📦 Menginstal dependensi dari '{file_path}'...\n")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", file_path])
        print("\n✅ Instalasi selesai tanpa error.")
    except subprocess.CalledProcessError as e:
        print(f"\n⚠️ Terjadi error saat instalasi: {e}")
        print("Coba jalankan perintah manual:\n")
        print(f"    pip install -r {file_path}")

if __name__ == "__main__":
    install_requirements()
