# -*- coding: utf-8 -*-
"""Yeni kavramlarla test — ABAP yok!"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)

print('═══ YENİ KAVRAMLARLA TEST ═══\n')

sorular = [
    "Zakkum nedir?",
    "Sagu nedir?",
    "Leviathan nedir?",
    "Etnomüzikoloji nedir?",
    "Fibula nedir?",
    "Karbonmonoksit nedir?",
]

for s in sorular:
    r = chat.sohbet(s)
    print(f'👤 {s}')
    print(f'🤖 {r["cevap"][:110]}')
    print()
