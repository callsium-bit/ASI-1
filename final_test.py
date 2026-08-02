# -*- coding: utf-8 -*-
"""Kapsamlı model testi — sonuçlar sohbet_kaydi.jsonl'e de yazılır"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine
from collections import Counter

k = ASIKernel()
chat = ChatEngine(k)

print('═══════════════════════════════════════')
print('  ASI-1 MODEL TESTİ — 3282+ DÜĞÜM')
print('═══════════════════════════════════════\n')

# ── 1. KİMLİK / KİŞİLİK ──
print('── KİŞİLİK ──')
for s in ["Merhaba", "Adın ne?", "Nasılsın?"]:
    r = chat.sohbet(s)
    print(f'  👤 {s}')
    print(f'  🤖 {r["cevap"][:95]}')
print()

# ── 2. ÇEKİRDEK AKIL (aksiyom) ──
print('── ÇEKİRDEK AKIL ──')
for s in ["Ses görünür mü?", "Taş uçar mı?"]:
    r = chat.sohbet(s)
    print(f'  👤 {s}')
    print(f'  🤖 {r["cevap"][:95]}')
print()

# ── 3. BİLGİ (yeni düğümler dahil) ──
print('── BİLGİ ──')
for s in ["ABAP nedir?", "Zakkum nedir?", "Ahali Cumhuriyet Fırkası nedir?"]:
    r = chat.sohbet(s)
    print(f'  👤 {s}')
    print(f'  🤖 {r["cevap"][:95]}')
print()

# ── 4. GÖREV + HAFIZA ──
print('── GÖREV + HAFIZA ──')
r = chat.sohbet("Yarın sunum var hatırlat")
print(f'  👤 Yarın sunum var hatırlat\n  🤖 {r["cevap"][:60]}')
r = chat.sohbet("Görevlerim neler?")
print(f'  👤 Görevlerim neler?\n  🤖 {r["cevap"][:60]}')
r = chat.sohbet("Az önce ne konuştuk?")
print(f'  👤 Az önce ne konuştuk?\n  🤖 {r["cevap"][:80]}')
print()

# ── 5. İSTATİSTİK ──
aktif = [n for n in k.hooks.nodes.values() if not n.isolated]
pc = Counter()
for n in aktif:
    for p in n.properties:
        pc[p] += 1
print('── İSTATİSTİK ──')
print(f'  Düğüm: {len(k.hooks.nodes)} | Aktif: {len(aktif)} | İzole: {len(k.hooks.nodes)-len(aktif)}')
print(f'  İlişki: {dict(pc.most_common(5))}')

k.save_knowledge()
print('\n✅ Tamamlandı — sonuçlar sohbet_kaydi.jsonl\'de de var')
