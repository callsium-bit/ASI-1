# -*- coding: utf-8 -*-
"""Kapsamlı model testi — 185K düğüm"""
import sys, os, time
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
print(f"📊 Düğüm: {len(k.hooks.nodes)} | Aktif: {len(aktif)}")
print(f"   İlişki: {dict(pc.most_common(5))}\n")

print('═══ MODEL TESTİ ═══\n')
sorular = [
    "Kimya nedir?",
    "Eclipse nedir?",
    "Avast Antivirus nedir?",
    "Sagu nedir?",
    "Leviathan nedir?",
    "Pragmatizm nedir?",
    "Cengiz Han kimdir?",
]
toplam = 0
for s in sorular:
    basla = time.time()
    r = chat.sohbet(s)
    sure = time.time() - basla
    toplam += sure
    print(f'👤 {s}')
    print(f'🤖 {r["cevap"][:110]}')
    print(f'   ⏱ {sure:.2f}sn | kanal: {r["kanal"]}')
    print()

print(f"⏱ Ortalama yanıt: {toplam/len(sorular):.2f}sn")
