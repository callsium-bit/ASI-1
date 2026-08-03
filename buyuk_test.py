# -*- coding: utf-8 -*-
"""175K düğüm model testi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine
from collections import Counter

k = ASIKernel()
chat = ChatEngine(k)

aktif = [n for n in k.hooks.nodes.values() if not n.isolated]
pc = Counter()
for n in aktif:
    for p in n.properties:
        pc[p] += 1
print(f"Düğüm: {len(k.hooks.nodes)} | Aktif: {len(aktif)} | İlişki: {dict(pc.most_common(4))}\n")

print('═══ 175K MODEL TESTİ ═══\n')
sorular = [
    "Beşiktaş JK nedir?",
    "Bilgisayar nedir?",
    "Kimya nedir?",
    "Pragmatizm nedir?",
    "Galatasaray SK nedir?",
    "Cengiz Han kimdir?",
]
for s in sorular:
    r = chat.sohbet(s)
    print(f'👤 {s}')
    print(f'🤖 {r["cevap"][:110]}')
    print()
