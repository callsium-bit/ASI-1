#!/usr/bin/env python3
"""
ASI Prototip - Tek Tıkla Başlatıcı
Kullanım: python run.py [mod]

Modlar:
  test       → Tüm testleri çalıştır (22 test)
  ask        → İnteraktif soru-cevap modu
  gaps       → Hafızadaki boşlukları listele
  distill    → LLM ile kavram damıtma (yerel LLM gerekir)
  web        → Web'den bilgi çekme (Wikipedia + LLM)
  web-loop   → Kesintisiz web döngüsü
  gui        → PySide6 kontrol paneli
  auto       → Otomatik: önce test, sonra interaktif
"""
import sys
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Python yolu: önce çalıştıran Python (taşınabilir), ortam değişkeniyle ezilebilir
# ASI_PYTHON ortam değişkeni varsa onu kullan (PySide6 kurulu sistem Python'u gibi)
SYSTEM_PYTHON = os.environ.get("ASI_PYTHON", sys.executable)
PYTHON = SYSTEM_PYTHON if os.path.exists(SYSTEM_PYTHON) else sys.executable

KERNEL = os.path.join(SCRIPT_DIR, "kernel_v2.py")
GUI = os.path.join(SCRIPT_DIR, "gui.py")

# Yerel LLM ayarları


def run(cmd_args, use_system_python=False):
    """Komut çalıştır"""
    python = SYSTEM_PYTHON if use_system_python else PYTHON
    full_cmd = [python] + cmd_args
    return subprocess.run(full_cmd, cwd=SCRIPT_DIR)


def print_banner():
    print(r"""
    ╔══════════════════════════════════════════════╗
    ║         ASI PROTOTİP v2.0                    ║
    ║  Sembolik Zeka + 5N1K + Web + LLM            ║
    ║  "Mavi düşmez. Renk algıdır, madde değil."   ║
    ╚══════════════════════════════════════════════╝
    """)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "auto"

    print_banner()

    if mode == "test":
        print("🧪 22 test çalıştırılıyor...\n")
        run([KERNEL, "--test"])

    elif mode == "ask":
        print("🧠 İnteraktif soru-cevap modu\n")
        run([KERNEL, "--interactive"])

    elif mode == "gaps":
        print("🔍 Boşluk analizi...\n")
        run([KERNEL, "--gaps"])

    elif mode == "distill":
        concept = sys.argv[2] if len(sys.argv) > 2 else input("Kavram: ").strip()
        print(f"🔬 '{concept}' damıtılıyor (LLM gerekir)...\n")
        run([KERNEL, "--distill", concept])

    elif mode == "web":
        concept = sys.argv[2] if len(sys.argv) > 2 else input("Kavram: ").strip()
        print(f"🌐 '{concept}' web'den çekiliyor...\n")
        run([KERNEL, "--web-ingest", concept])

    elif mode == "web-loop":
        n = sys.argv[2] if len(sys.argv) > 2 else input("Kaç tur (0=sonsuz): ").strip()
        print(f"🔄 Kesintisiz web döngüsü ({n} tur)...\n")
        run([KERNEL, "--web-loop", str(n)])

    elif mode == "gui":
        print("🖥️ PySide6 kontrol paneli başlatılıyor...\n")
        run([GUI], use_system_python=True)

    elif mode == "auto":
        print("⚡ Otomatik mod: önce testler, sonra interaktif\n")
        print("─" * 50)
        run([KERNEL, "--test"])
        print("\n" + "─" * 50)
        run([KERNEL, "--interactive"])

    else:
        print(f"""
KULLANIM: python run.py [mod]

MODLAR:
  test        → 22 testi çalıştır
  ask         → İnteraktif soru-cevap (Mavi düşer mi?)
  gaps        → Hafıza boşluklarını listele
  distill     → LLM ile kavram damıt (yerel LLM gerekir)
  web         → Web'den tek kavram çek (Wikipedia + LLM)
  web-loop    → Kesintisiz web bilgi çekme döngüsü
  gui         → PySide6 kontrol paneli
  auto        → Test + İnteraktif (varsayılan)

ÖRNEK:
  python run.py ask
  python run.py web deprem
  python run.py web-loop 10
  python run.py gui
""")


if __name__ == "__main__":
    main()
