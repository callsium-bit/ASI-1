# -*- coding: utf-8 -*-
"""Türetim döngüsü: bilgi tabanındaki isa zincirlerinden yeni ilişkiler türet.
A isa B ∧ B isa C → A isa C (modus ponens) + çapraz kompozisyon."""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
norm = k.axioms._normalize_tr

# isa grafiği kur: kavram -> isa değerleri
isa_grafik = {}  # kavram_norm -> [isa hedefleri]
for node in k.hooks.nodes.values():
    if node.isolated:
        continue
    for p, v in node.properties.items():
        if p in ("isa", "instance_of", "subclass_of"):
            kavram = norm(node.ne)
            isa_grafik.setdefault(kavram, set()).add(norm(str(v)))

print(f"isa grafiği: {len(isa_grafik)} kavram")

# Modus ponens: A isa B, B isa C → A isa C (B'nin isa'ları A'ya geçer)
turetilen = 0
kabul = 0
adimlar = []
for kavram, hedefler in list(isa_grafik.items()):
    for hedef in list(hedefler):
        if hedef in isa_grafik:  # B'nin kendi isa'ları var
            for c in isa_grafik[hedef]:
                if c == kavram:
                    continue
                sonuc = k.relations.add_relation(
                    kavram, "isa", c,
                    source=f"turetim|modus_ponens|{hedef}", confidence=0.75
                )
                turetilen += 1
                if sonuc["accepted"]:
                    kabul += 1
                    if len(adimlar) < 10:
                        adimlar.append((kavram, hedef, c))

k.save_knowledge()
print(f"Türetim: {turetilen} aday, {kabul} kabul")
print(f"Toplam düğüm: {len(k.hooks.nodes)}")
print("\nZincir örnekleri (A isa B ∧ B isa C → A isa C):")
for a, b, c in adimlar:
    print(f"  {a} isa {b} ∧ {b} isa {c} → {a} isa {c}")
