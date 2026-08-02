# -*- coding: utf-8 -*-
"""wiki_tr_v2 tanımlarından son-2-kelime stratejisiyle isa (yeniden)"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

k = ASIKernel()
SON_EK = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür", "dırlar", "dirler")

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

kabul = 0
tekrar = 0
filtre = 0
yeni_ornek = []
with open(r'veri\wiki_tr_v2.jsonl', 'r', encoding='utf-8') as f:
    for satir in f:
        try:
            rec = json.loads(satir)
        except Exception:
            continue
        konu = rec.get("konu", "").strip()
        tanim = rec.get("tanim", "")
        hedef = isa_cikar(tanim)
        if not hedef:
            continue
        if not hedef_kaliteli(konu, "isa", hedef):
            filtre += 1
            continue
        r = k.relations.add_relation(konu, "isa", hedef,
                                      source="wiki_tr_v3", confidence=0.9)
        if r["accepted"]:
            kabul += 1
            if len(yeni_ornek) < 12:
                yeni_ornek.append((konu, hedef))
        elif r.get("is_duplicate"):
            tekrar += 1

k.save_knowledge()
print(f"wiki_tr_v2: +{kabul} kabul, {tekrar} tekrar, {filtre} filtre")
print(f"Toplam düğüm: {len(k.hooks.nodes)}")
print("\nYeni örnekler:")
for s, h in yeni_ornek:
    print(f"  {s[:35]:37} isa {h[:40]}")
