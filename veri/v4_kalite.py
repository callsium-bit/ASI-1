# -*- coding: utf-8 -*-
"""wiki_tr_v4 kalite kontrolü: filtre + örneklem ölçümü"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

k = ASIKernel()
norm = k.axioms._normalize_tr

v4 = [n for n in k.hooks.nodes.values() if n.source.startswith("wiki_tr_v4")]
print(f"wiki_tr_v4 düğümü: {len(v4)}")

# 1. Filtreden geçmeyenleri sil
silinen = 0
ornek_sil = []
for nid, n in list(k.hooks.nodes.items()):
    if not n.source.startswith("wiki_tr_v4"):
        continue
    for p, v in n.properties.items():
        if p == "isa" and not hedef_kaliteli(n.ne, "isa", str(v)):
            del k.hooks.nodes[nid]
            silinen += 1
            if len(ornek_sil) < 8:
                ornek_sil.append((n.ne[:30], str(v)[:40]))
            break

# 2. Kalanların örneklemi
kalan = [n for n in k.hooks.nodes.values() if n.source.startswith("wiki_tr_v4")]
print(f"Filtre sonrası silinen: {silinen} | Kalan: {len(kalan)}")

# 3. Örneklem kalite değerlendirmesi (ilk 20)
print("\nÖrneklem (ilk 15):")
for n in kalan[:15]:
    for p, v in n.properties.items():
        print(f"  {n.ne[:32]:34} isa {str(v)[:45]}")
        break

k.save_knowledge()
print(f"\nToplam düğüm: {len(k.hooks.nodes)}")
