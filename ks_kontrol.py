# -*- coding: utf-8 -*-
"""knowledge_store durumu: düğüm sayısı + kaynak dağılımı"""
import sys, os, json
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from collections import Counter

with open('knowledge_store.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get("nodes", [])
print(f"Toplam düğüm: {len(nodes)}")
kaynaklar = Counter(n.get("source", "?") for n in nodes)
print(f"Kaynaklar: {dict(kaynaklar.most_common(6))}")
