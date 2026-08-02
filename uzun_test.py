# -*- coding: utf-8 -*-
"""Uzun konuşma testi: çok parçalı + bağlam + düşünme gerektiren sorular"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)

print('═══════ UZUN KONUŞMA TESTİ ═══════\n')

konusmalar = [
    # Çok parçalı soru
    ("Enflasyon nedir ve neden olur?",
     "tek soruda iki parça"),
    # Bağlam takibi: önceki cevabı referans alır
    ("ABAP hakkında ne biliyorsun?",
     "bilgi sorusu"),
    ("Peki bu nerede kullanılır?",
     "bağlam — 'bu' öncekine referans!"),
    # Düşünme zinciri
    ("Kar su mudur?",
     "aksiyom sorusu"),
    ("O zaman kar eriyince ne olur?",
     "bağlam + çıkarım"),
    # Tartışma
    ("Gökyüzü hakkında ne düşünüyorsun?",
     "görüş sorusu"),
]

for soru, etiket in konusmalar:
    r = chat.sohbet(soru)
    print(f'👤 [{etiket}] {soru}')
    print(f'🤖 {r["cevap"][:130]}')
    print()
