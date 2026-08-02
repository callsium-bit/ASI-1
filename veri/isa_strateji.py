# -*- coding: utf-8 -*-
"""5N1K isa çıkarım stratejisi testi: son-2-kelime + dır/dir sıyırma"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli

SON_EK = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür", "dırlar", "dirler")

def isa_cikar(tanim):
    """Tanım sonundan isa hedefi çıkar: '... felsefi akımdır' → 'felsefi akım'"""
    t = tanim.strip().rstrip('.').strip()
    for ek in SON_EK:
        if t.endswith(ek) and len(t) > len(ek) + 2:
            govde = t[:-len(ek)].strip()
            kelimeler = govde.split()
            # Son 2 kelimeyi al (sıfat+isim kombinasyonu)
            son = " ".join(kelimeler[-2:]) if len(kelimeler) >= 2 else govde
            son = re.sub(r'^(bir|bu|o|her)\s+', '', son).strip()
            if 2 <= len(son) <= 45:
                return son
    return None

# Test cümleleri
ornekler = [
    "Varoluşçuluk, 20. yüzyılda gelişen, insanın önce var olduğunu savunan felsefi akımdır.",
    "Kuantum bilgisayarlar, klasik bitler yerine kübitleri kullanarak hesaplama yapan yeni nesil bilgisayarlardır.",
    "Büyük İskender İmparatorluğu, Makedonya Kralı İskender'in kurduğu dev imparatorluktur.",
    "Enflasyon, para biriminin satın alma gücünün düşmesidir.",
    "ABAP, SAP sistemlerinde kullanılan bir programlama dilidir.",
    "Anadolu, tarihi zengin bir coğrafi bölgedir.",
]
ok = 0
for c in ornekler:
    h = isa_cikar(c)
    kalite = hedef_kaliteli("", "isa", h) if h else False
    print(f"  '{c[:60]}...' → isa: {h} (kalite: {kalite})")
    if h and kalite:
        ok += 1

print(f"\n{ok}/{len(ornekler)} kaliteli isa")
