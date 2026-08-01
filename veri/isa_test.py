# -*- coding: utf-8 -*-
"""turkish-wiki-qa verisinden isa cikarim testi"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from kernel_v2 import ASIKernel
from dataset_ingester import DatasetIngester

k = ASIKernel()
ing = DatasetIngester(k)

veri = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\turkish-wiki-qa.jsonl'

# İlk cümlelerden isa cikarim
bulunan = 0
ornek = []
with open(veri, 'r', encoding='utf-8') as f:
    for line in f:
        rec = json.loads(line)
        metin = rec.get('original_text', '')
        # İlk anlamlı cümle
        cumleler = [c.strip() for c in metin.split('.') if len(c.strip()) > 20]
        if not cumleler:
            continue
        ilk = cumleler[0]
        # Altin regex: "X, ... bir Y'dir"
        m = re.search(r'^([\w\sğüşıöçĞÜŞİÖÇ]{2,40}?),\s*(?:[\w\sğüşıöçĞÜŞİÖÇ,]{0,80}?)\s*bir\s+([\w\sğüşıöçĞÜŞİÖÇ]{2,40}?)(?:\'?dir|\'?dır|tir|tır)[\s.!]', ilk)
        if m:
            subj = m.group(1).strip()
            target = m.group(2).strip()
            bulunan += 1
            if len(ornek) < 8:
                ornek.append((subj, target, ilk[:120]))
        if bulunan >= 500:
            break

print(f'Ilk 5000 satirda isa kalibi: {bulunan}')
print()
for s, t, ilk in ornek:
    print(f'  {s[:30]:32} -> {t[:40]:42} | {ilk[:60]}')
