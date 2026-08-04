# -*- coding: utf-8 -*-
"""Paradoks/çelişki stres testi — 'çelişki korumalı' iddiasını sınar"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
ok = 0

print('═══ ÇELİŞKİ STRES TESTİ ═══\n')

# 1. Aynı kavrama çelişkili özellikler → ikincisi izole
r1 = k.relations.add_relation("stres_nesne", "has_property", "kati", source="stres", confidence=0.9)
r2 = k.relations.add_relation("stres_nesne", "has_property", "sivi", source="stres", confidence=0.9)
print(f'[1] has_property kati → {r1["accepted"]} | has_property sivi → {r2["accepted"]} (biri izole olmali)')
assert r1["accepted"] and not r2["accepted"], (r1, r2)
ok += 1

# 2. Feynman kuralı: "kar isa sıvı" engellenmeli (kar has_property kati)
r2k = k.relations.add_relation("stres_kar", "has_property", "kati", source="stres", confidence=0.9)
r3 = k.relations.add_relation("stres_kar", "isa", "sıvı", source="stres", confidence=0.9)
print(f'[2] kar isa sıvı (zıt özellik) → {r3["accepted"]} (engellenmeli)')
assert not r3["accepted"], r3
ok += 1

# 3. Çoklu sınıf üyeliği çelişki DEĞİL
r = k.relations.add_relation("stres_kopek", "isa", "memeli", source="stres", confidence=0.9)
r2m = k.relations.add_relation("stres_kopek", "isa", "hayvan", source="stres", confidence=0.9)
print(f'[3] kopek isa memeli → {r["accepted"]} | kopek isa hayvan → {r2m["accepted"]} (ikisi de kabul)')
assert r["accepted"] and r2m["accepted"]
ok += 1

# 4. Tutarlılık: en yüksek confidence seçilir
r = k.relations.add_relation("stres_tutarlilik", "isa", "zorlu", source="stres", confidence=0.7)
r2t = k.relations.add_relation("stres_tutarlilik", "isa", "test", source="stres", confidence=0.9)
cevap = k.ask("stres_tutarlilik nedir?")
print(f'[4] {cevap["answer"]} (0.9 secilmeli)')
assert "test" in cevap["answer"]
ok += 1

# Temizlik
for nid, n in list(k.hooks.nodes.items()):
    if n.source == "stres":
        del k.hooks.nodes[nid]
k.save_knowledge()

print(f'\nALL {ok} OK — çelişki koruması çalışıyor')
