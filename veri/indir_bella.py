#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BellaTurca akademik-derlem toplu indirici (kalan dosyalar)"""
import subprocess, sys, os, time

BASE = "https://huggingface.co/datasets/turkish-nlp-suite/BellaTurca/resolve/main/akademik-derlem"
OUT = r"C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\bella_akademik"

os.makedirs(OUT, exist_ok=True)

# dergi_2 .. dergi_20 (dergi_ ve dergi_1 indi)
dosyalar = [f"dergi_{i}.jsonl" for i in range(2, 21)]

for dosya in dosyalar:
    hedef = os.path.join(OUT, dosya)
    if os.path.exists(hedef) and os.path.getsize(hedef) > 1000:
        print(f"✓ atlandi (var): {dosya}")
        continue
    print(f"📥 {dosya} ...", flush=True)
    r = subprocess.run(
        ["curl", "-sL", f"{BASE}/{dosya}", "-o", hedef],
        capture_output=True, timeout=1800
    )
    boyut = os.path.getsize(hedef) if os.path.exists(hedef) else 0
    print(f"   → {boyut//1024//1024}MB", flush=True)
    if boyut < 1000:
        print(f"   ⚠️ bozuk indirme, siliniyor")
        os.remove(hedef)
    time.sleep(1)

print("TAMAM")
