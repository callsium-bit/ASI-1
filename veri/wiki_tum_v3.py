# -*- coding: utf-8 -*-
"""Wikipedia TR parquet (535K) → TÜM ilk cümleler → son-2-kelime isa → gate"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

SRC = r'C:\Users\alipranac\.cache\huggingface\hub\datasets--wikimedia--wikipedia\snapshots\b04c8d1ceb2f5cd4588862100d08de323dccfbaa\20231101.tr'
SON_EK = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür", "dırlar", "dirler")

k = ASIKernel()

def isa_cikar(tanim):
    t = str(tanim).strip().rstrip('.').strip()
    for ek in SON_EK:
        if t.endswith(ek) and len(t) > len(ek) + 2:
            govde = t[:-len(ek)].strip()
            kelimeler = govde.split()
            son = " ".join(kelimeler[-2:]) if len(kelimeler) >= 2 else govde
            son = re.sub(r'^(bir|bu|o|her)\s+', '', son).strip()
            if 2 <= len(son) <= 45:
                return son
    return None

import pyarrow.parquet as pq
kabul = 0
tekrar = 0
filtre = 0
toplam = 0
ornekler = []

for dosya in sorted(os.listdir(SRC)):
    if not dosya.endswith('.parquet'):
        continue
    table = pq.read_table(os.path.join(SRC, dosya), columns=['title', 'text'])
    for title, text in zip(table.column('title').to_pylist(),
                           table.column('text').to_pylist()):
        toplam += 1
        if toplam % 100000 == 0:
            print(f"  {toplam} makale | +{kabul} kabul", flush=True)
        if not text:
            continue
        # İlk cümle
        ilk = re.split(r'(?<=[.!?])\s', text.strip())[0]
        if ilk.count(',') < 1:
            continue
        # Özel önek atla
        if title.startswith(("Dosya:", "File:", "Kategori:", "Şablon:")):
            continue
        hedef = isa_cikar(ilk)
        if not hedef:
            continue
        if not hedef_kaliteli(title, "isa", hedef):
            filtre += 1
            continue
        r = k.relations.add_relation(title, "isa", hedef,
                                      source="wiki_tr_v3", confidence=0.9)
        if r["accepted"]:
            kabul += 1
            if len(ornekler) < 12:
                ornekler.append((title, hedef))
        elif r.get("is_duplicate"):
            tekrar += 1

k.save_knowledge()
print(f"\nTAMAM: {toplam} makale | +{kabul} kabul, {tekrar} tekrar, {filtre} filtre")
print(f"Toplam düğüm: {len(k.hooks.nodes)}")
for s, h in ornekler:
    print(f"  {s[:35]:37} isa {h[:40]}")
