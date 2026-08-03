# -*- coding: utf-8 -*-
"""Wikipedia TR 2. cümleler → isa (ilk cümle bitti, 2. cümlelerde de tanımlar var)
Ayrıca: 3. ve 4. cümleler de taranır — düşük verim ama 535K makale büyük havuz."""
import sys, os, json, re, time
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

SRC = r'C:\Users\alipranac\.cache\huggingface\hub\datasets--wikimedia--wikipedia\snapshots\b04c8d1ceb2f5cd4588862100d08de323dccfbaa\20231101.tr'
SON_EK = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür", "dırlar", "dirler")
k = ASIKernel()
norm = k.axioms._normalize_tr

def isa_cikar(cumle):
    t = cumle.strip().rstrip('.').strip()
    if t.count(',') < 1 or len(t) > 250:
        return None
    for ek in SON_EK:
        if t.endswith(ek) and len(t) > len(ek) + 3:
            govde = t[:-len(ek)].strip()
            # 2. cümle: subject virgülden önceki kısım değil — ilk cümle gibi değil.
            # Tanım kalıbı: "... bir Y'dir" — son 2 kelime + virgül şartı
            if ',' not in govde:
                continue
            kelimeler = govde.split(',')[-1].split()
            hedef = " ".join(kelimeler[-2:]) if len(kelimeler) >= 2 else govde
            hedef = re.sub(r'^(bir|bu|o|her)\s+', '', hedef).strip()
            if 2 <= len(hedef) <= 50:
                return hedef
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
        if not text or title.startswith(("Dosya:", "File:", "Kategori:", "Şablon:")):
            continue
        # 2-4. cümleleri al (1. cümle zaten işlendi)
        cumleler = re.split(r'(?<=[.!?])\s', text.strip())[1:4]
        for cumle in cumleler:
            hedef = isa_cikar(cumle)
            if not hedef:
                continue
            if not hedef_kaliteli(title, "isa", hedef):
                filtre += 1
                continue
            r = k.relations.add_relation(title, "isa", hedef,
                                          source="wiki_tr_v4", confidence=0.75)
            if r["accepted"]:
                kabul += 1
                if len(ornekler) < 10:
                    ornekler.append((title, hedef))
            elif r.get("is_duplicate"):
                tekrar += 1
            break  # makale başına 1 ilişki
        # PERİYODİK SAVE: her 50K makalede kaydet (save hatası = max 50K kayıp)
        if toplam % 50000 == 0:
            for deneme in range(3):
                try:
                    k.save_knowledge()
                    break
                except Exception as e:
                    print(f"  ! save deneme {deneme+1} basarisiz: {str(e)[:50]}", flush=True)
                    time.sleep(2)

k.save_knowledge()
print(f"\nTAMAM: {toplam} makale | +{kabul} kabul, {tekrar} tekrar, {filtre} filtre")
print(f"Toplam düğüm: {len(k.hooks.nodes)}")
for s, h in ornekler:
    print(f"  {s[:35]:37} isa {h[:40]}")
