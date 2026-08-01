# -*- coding: utf-8 -*-
"""ASI-1 final sınav"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
from kernel_v2 import ASIKernel
k = ASIKernel()

print('=== FINAL SINAV (220 kaliteli dugum) ===')
print()
sorular = [
    'Mavi duser mi?',
    'Eylemsizlik nedir?',
    'Kara delik nedir?',
    'Epistemoloji nedir?',
    'Determinant nedir?',
    'Ronesans nedir?',
    'Sahra Colu nedir?',
    'Yapay zeka nedir?',
    'Enflasyon nedir?',
    'Gotik mimari nedir?',
    'Minotor nedir?',
    'Andromeda nedir?',
]
iyi = 0
for s in sorular:
    r = k.ask(s)
    cevap = str(r.get('answer', r)) if isinstance(r, dict) else str(r)
    gurultu = any(z in cevap for z in ['yaradır','özelliğidir','sistemidir','zorunluluktır','bölünmedir','nadır'])
    kaynak = 'WIKI' if '[Wikipedia]' in cevap else 'Hafiza'
    durum = 'GURULTU' if gurultu else ('OK' if 'cevaplayam' not in cevap else 'BOS')
    iyi += (durum == 'OK')
    print('[{:6}] {:25} -> {}'.format(kaynak, s[:24], cevap[:90]))
    if gurultu:
        print('        ⚠️ GURULTU DETECTED')
    print()
print('SONUC: {}/{} temiz cevap'.format(iyi, len(sorular)))
