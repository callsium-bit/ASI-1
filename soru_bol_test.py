# -*- coding: utf-8 -*-
"""Soru Bölme Katmanı testi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)
ok = 0

print('═══ SORU BÖLME TESTİ ═══\n')

testler = [
    # Çok parçalı → bölünmeli
    ("Enflasyon nedir ve neye sebep olur?", True),
    ("Zakkum nedir ve nerede yetişir?", True),
    # Tek parçalı → bölünmemeli (normal akış)
    ("Sagu nedir?", False),
    ("Gökyüzü neden mavidir?", False),
]

for soru, beklenen_bol in testler:
    r = chat.sohbet(soru)
    kanal = r["kanal"]
    bolundu = (kanal == "soru_bol")
    durum = "✅" if bolundu == beklenen_bol else "❌"
    print(f'{durum} {soru}')
    print(f'   → [{kanal}] {r["cevap"][:130]}')
    print()
    if bolundu == beklenen_bol:
        ok += 1

print(f'\n{ok}/4 OK')
