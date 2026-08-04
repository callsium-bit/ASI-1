# -*- coding: utf-8 -*-
"""Model testi — farklı sorular (ABAP yok, mavi yok)"""
import sys, os, time
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)

sorular = [
    "Galatasaray SK nedir?",
    "Kimya nedir?",
    "Zakkum nedir?",
    "Etnomüzikoloji nedir?",
    "Türkiye'nin başkenti neresidir?",
    "Leviathan hakkında ne biliyorsun?",
    "Karbonmonoksit nedir?",
    "Pragmatizm ne demek?",
    "Su ne zaman kaynar?",
    "Ankara nerededir?",
]

print('═══ MODEL TESTİ — FARKLI SORULAR ═══\n')
toplam = 0
for s in sorular:
    basla = time.time()
    r = chat.sohbet(s)
    sure = time.time() - basla
    toplam += sure
    print(f'👤 {s}')
    print(f'🤖 {r["cevap"][:120]}')
    print(f'   ⏱ {sure:.2f}sn | kanal: {r["kanal"]}')
    print()

print(f"⏱ Ortalama: {toplam/len(sorular):.2f}sn")
