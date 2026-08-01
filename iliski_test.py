# -*- coding: utf-8 -*-
"""İlişki genişletme testi: 5N1K nerede/neden -> located_in/causes"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel
from dataset_ingester import DatasetIngester

k = ASIKernel()
# Temiz başla (tohum dışında)
k.hooks.nodes.clear()
k.hooks.hooks.clear()
k.contradictions.isolation_zone.clear()
k._seed_knowledge()

ing = DatasetIngester(k)
result = ing.ingest_jsonl(os.path.join(os.path.expanduser('~'), 'Desktop', '5n1k_temiz_59k.jsonl'), limit=3000)

print('=== İLİŞKİ GENİŞLETME SONUCU ===')
print(f"Kabul: {result['accepted']} | Ret: {result['rejected']} | Tekrar: {result['duplicates']}")

# İlişki türü dağılımı
from collections import Counter
pc = Counter()
for node in k.hooks.nodes.values():
    if node.isolated: continue
    for p in node.properties:
        pc[p] += 1
print(f"\nİlişki dağılımı: {dict(pc.most_common(12))}")

# Örnekler
print('\n=== YENİ İLİŞKİ ÖRNEKLERİ ===')
g = 0
for n in sorted(k.hooks.nodes.values(), key=lambda x: x.ne):
    if n.isolated: continue
    for p, v in n.properties.items():
        if p in ('located_in', 'causes', 'invented_by', 'part_of', 'used_for') and g < 12:
            print(f'  {n.ne[:30]:32} --{p}--> {str(v)[:45]}')
            g += 1
