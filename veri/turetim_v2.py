# -*- coding: utf-8 -*-
"""Türetim döngüsü v2: 175K düğümde modus ponens zincirleri"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel
from collections import Counter

k = ASIKernel()
norm = k.axioms._normalize_tr

# 1. Kategori hedeflerini say (isa hedefleri)
hedefler = Counter()
for n in k.hooks.nodes.values():
    if n.isolated:
        continue
    for p, v in n.properties.items():
        if p == "isa":
            hedefler[norm(str(v))] += 1

print(f"Toplam kategori hedefi: {len(hedefler)}")
print("En yaygın kategoriler:")
for h, c in hedefler.most_common(12):
    print(f"  {c:>6} × {h[:45]}")

# 2. Kategorilerin kendi isa'sı var mı? (zincir kurulabilir mi?)
zincir_aday = 0
for h in list(hedefler.keys()):
    if hedefler[h] >= 3:  # 3+ kavram paylaşıyor
        var = k.hooks.search_5n1k(ne=h)
        if var:
            zincir_aday += 1
print(f"\n3+ kavram paylaşan ve DÜĞÜM olarak var olan kategori: {zincir_aday}")
