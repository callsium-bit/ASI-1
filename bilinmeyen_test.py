# -*- coding: utf-8 -*-
"""ASI-1 bilinmeyen sorular testi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)

print('═══════ BİLİNMEYEN SORULAR TESTİ ═══════')
print()

sorular = [
    # Tamamen bilinmeyen kavramlar
    'Kuantum dolanıklık nedir?',
    'Mandelbrot kümesi nedir?',
    'Entropi nedir?',
    # Bilinen kavramların derin yönleri
    'Karın erime noktası kaç derecedir?',
    'Su ne zaman kaynar?',
    # Saçma/absürt sorular
    'Sandalye rüya görebilir mi?',
    'Elektron üzülür mü?',
    # Karmaşık ilişki sorusu
    'Yağmur toprağı ne yapar?',
    'Güneş neden parlıyor?',
]

for s in sorular:
    r = chat.sohbet(s)
    cevap = str(r.get("cevap", r))
    kaynak = r.get("kanal", "?")
    # Kısa göster
    print(f'? {s}')
    print(f'  [{kaynak}] {cevap[:110]}')
    print()
