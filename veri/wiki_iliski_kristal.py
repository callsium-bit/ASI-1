# -*- coding: utf-8 -*-
"""wiki_iliskiler.jsonl -> KALİTE FİLTRESİ -> gate -> kristal"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

k = ASIKernel()
re_ = k.relations

YOL = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\wiki_iliskiler.jsonl'

kabul = 0
ret = 0
tekrar = 0
filtre = 0
ornekler = []
with open(YOL, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if not hedef_kaliteli(rec["subject"], rec["relation"], rec["target"]):
            filtre += 1
            continue
        sonuc = re_.add_relation(
            rec["subject"], rec["relation"], rec["target"],
            source="wiki_iliskiler", confidence=0.8
        )
        if sonuc["accepted"]:
            kabul += 1
            if len(ornekler) < 12:
                ornekler.append(rec)
        elif sonuc.get("is_duplicate"):
            tekrar += 1
        else:
            ret += 1

k.save_knowledge()
print(f"İlişki: +{kabul} kabul, {ret} ret, {tekrar} tekrar, {filtre} filtre")
print(f"Toplam düğüm: {len(k.hooks.nodes)}")
print("\nKabul edilen örnekler:")
for o in ornekler:
    print(f"  {o['subject'][:35]:37} --{o['relation']}--> {o['target'][:40]}")
