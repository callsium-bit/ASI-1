# -*- coding: utf-8 -*-
"""Modus ponens türetim: 175K düğümde zincirler"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
norm = k.axioms._normalize_tr

# 1. Örnek kategorilerin düğüm durumu
for kavram in ["mahalle", "köy", "şehir", "bitki türü", "hayvan türü", "belediye", "cins"]:
    d = k.hooks.search_5n1k(ne=kavram)
    if d:
        props = {p: v for n in d for p, v in n.properties.items() if p == "isa"}
        print(f"{kavram:15} → {str(props)[:70]}")
    else:
        print(f"{kavram:15} → DÜĞÜM YOK")

# 2. derive_isa_chain ile zincir türet
print("\n=== ZİNCİR TÜRETİMİ ===")
toplam = 0
ornekler = []
for i, node in enumerate(list(k.hooks.nodes.values())):
    if node.isolated:
        continue
    for p, v in node.properties.items():
        if p == "isa":
            # "X isa Y" varsa, Y'nin isa'sı varsa → X isa Y'nin isa'sı
            ustler = k.hooks.search_5n1k(ne=str(v))
            for ust in ustler:
                for up, uv in ust.properties.items():
                    if up == "isa" and norm(str(uv)) != norm(node.ne):
                        # Çoklu üyelik kontrolü (zaten isa ise atla)
                        mevcut = [str(pv) for pv in
                                  [pp for nn in k.hooks.search_5n1k(ne=node.ne)
                                   for pp, pv in nn.properties.items() if pp == "isa"]]
                        if norm(str(uv)) in [norm(m) for m in mevcut]:
                            continue
                        r = k.relations.add_relation(node.ne, "isa", str(uv),
                                                     source="turetim|modus_ponens",
                                                     confidence=0.7)
                        if r["accepted"]:
                            toplam += 1
                            if len(ornekler) < 8:
                                ornekler.append((node.ne, str(v), str(uv)))
                            break
            if toplam > 2000:
                break
    if i > 30000:
        break

print(f"Türetilen zincir: {toplam}")
for s, a, b in ornekler:
    print(f"  {s[:30]:32} isa {a[:25]:27} isa {b[:30]}")
