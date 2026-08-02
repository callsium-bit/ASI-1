# -*- coding: utf-8 -*-
"""Kişilik testi: Adın ne? + kimsin + nasılsın"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)
ok = 0

for soru, beklenen in [
    ("Adın ne?", "ASI-1"),
    ("Kimsin sen?", "ASI-1"),
    ("Nasılsın?", "İyiyim"),
    ("Kaç yaşındasın?", "doğmadım"),
]:
    r = chat.sohbet(soru)
    cevap = r["cevap"]
    ok_ = "ASI-1" in cevap or "doğmadım" in cevap or "İyiyim" in cevap
    print(f'[{"✅" if ok_ else "❌"}] {soru} → {cevap[:70]}')
    if ok_:
        ok += 1

print(f'\nKişilik testi: {ok}/4')
