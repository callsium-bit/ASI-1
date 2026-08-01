# -*- coding: utf-8 -*-
"""RelationEngine testi: modus ponens + gecislilik + hipotez uretimi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, RelationEngine

k = ASIKernel()
re_ = k.relations

print('=== MODUS PONENS TESTI ===')
# A isa B, B isa C zinciri kur
k.hooks.create_node(ne="Köpek", properties={"isa": "Memeli"}, source="test")
k.hooks.create_node(ne="Memeli", properties={"isa": "Hayvan"}, source="test")
k.hooks.create_node(ne="Hayvan", properties={"isa": "Canlı"}, source="test")

derived = re_.derive_isa_chain("Köpek", max_depth=3)
print(f"Köpek isa zincirinden turetilebilen: {len(derived)}")
for d in derived:
    print(f"  {d['subject']} isa {d['target']}  [kural: {d['rule']}, zincir: {'->'.join(d['chain'])}]")

# Hipotezleri uygula
result = re_.apply_hypotheses("Köpek", max_depth=3)
print(f"\nUygulama: {result['hypotheses']} hipotez, {result['accepted']} kabul, {result['rejected']} ret")

# Dogrula: Köpek isa Hayvan ve Canli artik var mi?
for node in k.hooks.nodes.values():
    if node.ne == "Köpek" and not node.isolated:
        print(f"\nKöpek dugumu: {node.properties}")

print("\n=== GECISLILIK TESTI (part_of) ===")
k.hooks.create_node(ne="Çekirdek", properties={"part_of": "CPU"}, source="test")
k.hooks.create_node(ne="CPU", properties={"part_of": "Bilgisayar"}, source="test")
derived2 = re_.derive_transitive("Çekirdek", "part_of", max_depth=3)
for d in derived2:
    print(f"  {d['subject']} part_of {d['target']}  [zincir: {'->'.join(d['chain'])}]")

print("\nRelationEngine istatistik:", re_.get_stats()["derived_count"], "turetim")
