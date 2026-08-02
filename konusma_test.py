# -*- coding: utf-8 -*-
"""Canlı konuşma testi — model konuşabiliyor mu?"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)

print('═══ CANLI KONUŞMA TESTİ ═══\n')

diyalog = [
    "Merhaba",
    "Adın ne?",
    "Yarın marketten süt almayı hatırla",
    "Görevlerim neler?",
    "Ses görünür mü?",
    "ABAP nedir?",
    "Yağmur hakkında ne biliyorsun?",
    "Az önce ne konuştuk?",
    "Geçen konuşmamızı hatırlıyor musun?",
]

for soru in diyalog:
    r = chat.sohbet(soru)
    cevap = r["cevap"]
    kanal = r["kanal"]
    print(f'👤 {soru}')
    print(f'🤖 [{kanal}] {cevap[:130]}')
    print()

# Kalıcı hafızayı diske yaz
k.save_knowledge()
print("--- hafıza kaydedildi ---")
