# -*- coding: utf-8 -*-
"""Araştır-öğren testi: bilinmeyen kavram → internetten öğren → hatırla"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)
norm = k.axioms._normalize_tr

# Bilinmeyen kavram seç
adaylar = ["kuark", "klorofil", "heliyum", "buzul", "gezegenimsi bulutsu"]
bilinmeyen = []
for a in adaylar:
    var = any(norm(a) in norm(n.ne) for n in k.hooks.nodes.values())
    if not var:
        bilinmeyen.append(a)
print(f"Bilinmeyen adaylar: {bilinmeyen}")

if not bilinmeyen:
    print("Hepsi biliniyor!")
    sys.exit(0)

kavram = bilinmeyen[0]
print(f"\n=== '{kavram}' ARAŞTIR-ÖĞREN ===")

# 1. soru: bilmiyor olmalı
r1 = chat.sohbet(f"{kavram} nedir?")
print(f"\n[1] İLK SORU: {r1['cevap'][:130]}")

# 2. Wikipedia'dan araştır (aracı zorla)
tool = k.tools.call(f"{kavram} nedir?")
if tool.get("tool") == "wikipedia_ara" and tool.get("result"):
    res = tool["result"]
    print(f"\n[2] İNTERNETTEN: {str(res.get('extract',''))[:130]}")
    ogrenildi = res.get("ogrenildi", False)
    print(f"    ogrenildi: {ogrenildi}")
else:
    print(f"\n[2] Araç çıktısı: {str(tool)[:100]}")

# Kalıcı kaydet
k.save_knowledge()

# 3. tekrar sor: hafızadan cevap vermeli
r3 = chat.sohbet(f"{kavram} nedir?")
print(f"\n[3] TEKRAR SORU: {r3['cevap'][:130]}")
