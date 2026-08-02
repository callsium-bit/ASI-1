# -*- coding: utf-8 -*-
"""Araştır-öğren döngüsü testi v2 (gerçekten bilinmeyen kavram)"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()

# Bilgi tabanında olmayan kavramları bul
def biliniyor_mu(kavram):
    norm = k.axioms._normalize_tr
    for node in k.hooks.nodes.values():
        if norm(kavram) in norm(node.ne):
            return True
    return False

adaylar = ["zirkonyum", "boksit", "kalsiyum", "ametist", "granit"]
bilinmeyen = [a for a in adaylar if not biliniyor_mu(a)]
print(f'Bilinmeyen adaylar: {bilinmeyen}')

if not bilinmeyen:
    print("Tümü biliniyor — başka aday denenecek")
    sys.exit(0)

kavram = bilinmeyen[0]
print(f'\n=== "{kavram}" ARAŞTIR-ÖĞREN TESTİ ===')

# İlk soru
r = k.ask(f"{kavram} nedir?")
cevap = str(r.get("answer", r))
print(f'[1] İlk: {cevap[:100]}')
print(f'    tool: {r.get("tool")}')

# Öğrenme oldu mu?
norm = k.axioms._normalize_tr
ogrenildi = False
for node in k.hooks.nodes.values():
    if norm(node.ne) == norm(kavram) and "arastirma" in node.source:
        ogrenildi = True
        print(f'    ✅ ÖĞRENDİ: {node.ne} isa {node.properties}')
        break

k.save_knowledge()

# İkinci soru
r2 = k.ask(f"{kavram} nedir?")
cevap2 = str(r2.get("answer", r2))
print(f'[2] İkinci: {cevap2[:100]}')
