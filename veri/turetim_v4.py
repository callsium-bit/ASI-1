# -*- coding: utf-8 -*-
"""Modus ponens türetim v4: flush'lu, ölçekli"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
norm = k.axioms._normalize_tr

toplam = 0
ornekler = []
islenen = 0
kategori_isa = {}

# Önce kategori → isa haritasını kur (175K düğümü 1 kez tara)
for n in k.hooks.nodes.values():
    if n.isolated:
        continue
    for p, v in n.properties.items():
        if p == "isa":
            kategori_isa.setdefault(norm(str(v)), set()).add(norm(n.ne))

print(f"Kategori haritası: {len(kategori_isa)} kategori", flush=True)

# Şimdi zincir türet: her "X isa Kategori" için Kategori'nin isa'sı varsa
for n in list(k.hooks.nodes.values()):
    if n.isolated:
        continue
    islenen += 1
    for p, v in n.properties.items():
        if p != "isa":
            continue
        v_norm = norm(str(v))
        # Kategori'nin kendi isa'sı var mı (düğüm olarak)?
        ustler = k.hooks.search_5n1k(ne=str(v))
        for ust in ustler:
            for up, uv in ust.properties.items():
                if up != "isa":
                    continue
                uv_norm = norm(str(uv))
                if uv_norm == norm(n.ne) or uv_norm == v_norm:
                    continue
                r = k.relations.add_relation(n.ne, "isa", str(uv),
                                             source="turetim|modus_ponens",
                                             confidence=0.7)
                if r["accepted"]:
                    toplam += 1
                    if len(ornekler) < 8:
                        ornekler.append((n.ne, str(v), str(uv)))
                break
    if islenen >= 20000:
        break

k.save_knowledge()
print(f"\nTüretilen zincir: {toplam}", flush=True)
for s, a, b in ornekler:
    print(f"  {s[:28]:30} isa {a[:22]:24} isa {b[:30]}")
