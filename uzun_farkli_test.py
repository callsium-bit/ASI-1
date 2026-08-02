# -*- coding: utf-8 -*-
"""Uzun ve farklı soru testi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)

print('═══ UZUN VE FARKLI SORU ═══\n')

# Çok parçalı + kavram ilişkisi + bağlam gerektiren soru
sorular = [
    "Enflasyon nedir, hangi ülkede ölçülür ve neye sebep olur?",
    "Zakkum bir bitki midir, yoksa başka bir şey mi? Nerede yetişir?",
    "Karbonmonoksit nedir ve insan vücuduna ne yapar?",
    "Leviathan hakkında ne biliyorsun? Kitap mı, canavar mı, başka bir şey mi?",
]

for s in sorular:
    r = chat.sohbet(s)
    print(f'👤 {s}')
    print(f'🤖 {r["cevap"][:150]}')
    print(f'   [kanal: {r["kanal"]}]')
    print()
