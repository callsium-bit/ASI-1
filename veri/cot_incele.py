# -*- coding: utf-8 -*-
"""5n1k_cot_train.jsonl inceleme"""
import sys, os, json
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from collections import Counter

YOL = r'C:\Users\alipranac\5n1k-synthetic-data\5n1k_cot_train.jsonl'
tipler = Counter()
metin_uzunluk = []
cevap_var = 0
with open(YOL, 'r', encoding='utf-8') as f:
    for i, satir in enumerate(f):
        if i >= 5000:
            break
        rec = json.loads(satir)
        tipler[rec.get("tip", "?")] += 1
        metin_uzunluk.append(len(rec.get("metin", "")))
        if rec.get("cevap"):
            cevap_var += 1

print(f"İlk 5000 kayıt tip dağılımı: {dict(tipler.most_common(10))}")
print(f"Metin ort. uzunluk: {sum(metin_uzunluk)//len(metin_uzunluk)} karakter")
print(f"cevap alanı olan: {cevap_var}")
