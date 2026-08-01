# -*- coding: utf-8 -*-
"""Regex kalite testi: eski vs yeni filtre"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
from kernel_v2 import ASIKernel
from dataset_ingester import DatasetIngester

k = ASIKernel()
# Tohum veriyle temiz başla
k.hooks.nodes.clear()
k.hooks.hooks.clear()
k.contradictions.isolation_zone.clear()
k._seed_knowledge()

ing = DatasetIngester(k)
result = ing.ingest_jsonl(os.path.join(os.path.expanduser('~'), 'Desktop', '5n1k_temiz_59k.jsonl'))

print('=== YENİ FİLTRE SONUÇLARI ===')
print('isa çıkarılan:', result['isa_extracted'])
print('Kabul:', result['accepted'], '| Ret:', result['rejected'], '| Tekrar:', result['duplicates'])
status = k.get_status()
print('Düğüm:', status['total_nodes'], '| İzole:', status['isolated_nodes'])
print()

# Yeni düğümlerin kalitesini örnekle
yeni = [n for n in k.hooks.nodes.values() if n.source.startswith('dataset')]
print(f'=== YENİ DÜĞÜM ÖRNEKLERİ ({len(yeni)} tane) ===')
for n in sorted(yeni, key=lambda x: x.ne)[:30]:
    print(f'  {n.ne[:40]:42} -> {str(n.properties)[:60]}')
