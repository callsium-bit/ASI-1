# -*- coding: utf-8 -*-
"""ASI-1 kapsamli canli sinav (2587 dugum)"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel
k = ASIKernel()

def norm(s):
    return s.replace("ı","i").replace("ğ","g").replace("ü","u").replace("ş","s").replace("ö","o").replace("ç","c").lower()

print('=== ASI-1 KAPSAMLI SINAV (2587 dugum) ===')
print()

# Farkli kategorilerde sorular
sorular = [
    # Çekirdek aksiyomlar
    ('Temel', 'Mavi duser mi?'),
    ('Temel', 'Yagmurda mavi duser mi?'),
    ('Temel', 'Islanan sey mavi olur mu?'),
    # Wikipedia v1 (927 donemi)
    ('Bilgi', 'ABAP nedir?'),
    ('Bilgi', 'Andromeda nedir?'),
    ('Bilgi', 'Minotor nedir?'),
    # Wikipedia v2 (yeni 1012)
    ('Bilgi', 'Refrakter malzemeler nedir?'),
    ('Bilgi', 'Tabakhane nedir?'),
    ('Bilgi', 'Uzunluk birimi nedir?'),
    ('Bilgi', 'Etnomuzikoloji nedir?'),
    # Önceki zayıf noktalar
    ('Zayif', 'Enflasyon nedir?'),
    ('Zayif', 'Yapay zeka nedir?'),
    ('Zayif', 'Kara delik nedir?'),
    ('Zayif', 'Determinant nedir?'),
    ('Zayif', 'Gotik mimari nedir?'),
    ('Zayif', 'Sahra Colu nedir?'),
    # Farkli soru formati
    ('Format', 'Ronesans nedir?'),
    ('Format', 'Epistemoloji nedir?'),
]

iyi = 0
gurultu_sayisi = 0
bos = 0
for kat, s in sorular:
    r = k.ask(s)
    cevap = str(r.get('answer', r)) if isinstance(r, dict) else str(r)
    n = norm(cevap)
    gurultu = any(z in n for z in ['yarad','ozelligidir','sistemidir','zorunluluktir',
                                   'bolunmedir','nadir','kullanan','etki yara'])
    kaynak = 'WIKI' if '[wikipedia' in n else 'HAFIZA'
    if gurultu:
        durum = 'GURULTU'
        gurultu_sayisi += 1
    elif 'cevaplayam' in n or 'bulunamad' in n:
        durum = 'BOS'
        bos += 1
    else:
        durum = 'OK'
        iyi += 1
    print('[{:6}] [{:6}] {} -> {}'.format(kaynak, durum, s[:28], cevap[:95]))
    print()

print('='*60)
print('SONUC: {}/{} OK | {} gurultu | {} bos'.format(iyi, len(sorular), gurultu_sayisi, bos))
