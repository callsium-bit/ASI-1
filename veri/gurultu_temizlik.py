# -*- coding: utf-8 -*-
"""Gürültü temizliği: wiki_tr_v3 kaynaklı düğümlerde kalite kontrolü
1. "ve X" önekli hedefler → X yap (Cengiz Han → hükümdar)
2. Kalite filtresinden geçmeyenleri sil
"""
import sys, os, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

k = ASIKernel()
norm = k.axioms._normalize_tr

once = len(k.hooks.nodes)
duzeltilen = 0
silinen = 0
ornek_duzelt = []
ornek_sil = []

for nid, n in list(k.hooks.nodes.items()):
    if not n.source.startswith("wiki_tr_v3"):
        continue
    yeni_props = {}
    temiz = True
    for pname, pval in n.properties.items():
        if pname != "isa":
            yeni_props[pname] = pval
            continue
        v = str(pval)
        # 1. "ve X" → X
        if v.startswith("ve "):
            v = v[3:].strip()
        # 2. Kalite filtresi
        if not hedef_kaliteli(n.ne, "isa", v):
            temiz = False
            if len(ornek_sil) < 8:
                ornek_sil.append((n.ne[:30], str(pval)[:35]))
            break
        yeni_props[pname] = v
        if v != str(pval) and len(ornek_duzelt) < 5:
            ornek_duzelt.append((n.ne[:30], str(pval)[:35], v[:35]))
    if temiz:
        if yeni_props != n.properties:
            n.properties = yeni_props
            duzeltilen += 1
    else:
        del k.hooks.nodes[nid]
        silinen += 1

k.save_knowledge()
print(f"Once: {once} | Duzenlenen: {duzeltilen} | Silinen: {silinen} | Sonra: {len(k.hooks.nodes)}")
print("\nDüzeltilen örnekler:")
for s, e, y in ornek_duzelt:
    print(f"  {s:32} '{e}' → '{y}'")
print("\nSilinen örnekler:")
for s, e in ornek_sil:
    print(f"  {s:32} isa '{e}'")
