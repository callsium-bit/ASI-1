# -*- coding: utf-8 -*-
"""atlas_combined.txt isa testi: 100K satırda verim + kalite"""
import sys, os, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

k = ASIKernel()
YOL = r'C:\Users\alipranac\Desktop\Yeni klasör\atlas_combined.txt'

SON_EK = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür", "dırlar", "dirler")

def isa_cikar(satir):
    """'X, ... Y'dir.' → (subject, hedef) — ilk cümle + son-2-kelime"""
    # Liste formatlarını atla ("* 1946 - X", "|", "===", "10 Ağustos - X")
    s0 = satir.strip()
    if s0.startswith(('*', '|', '=', '#', '!')) or ' - ' in s0[:30]:
        return None
    # İlk cümleyi al
    ilk = re.split(r'(?<=[.!?])\s', satir)[0].strip()
    if ilk.count(',') < 1:
        return None
    for ek in SON_EK:
        if ilk.endswith(ek) and len(ilk) > len(ek) + 3:
            govde = ilk[:-len(ek)].strip()
            # Subject = CÜMLENİN BAŞINDAN ilk virgüle kadar (rastgele virgül değil!)
            ilk_virgul = govde.find(',')
            if ilk_virgul <= 0 or ilk_virgul > 45:
                continue
            subject = govde[:ilk_virgul].strip()
            # Özel önekleri atla (Dosya:, File:, Kategori:, Şablon:)
            if any(subject.startswith(p) for p in ("Dosya:", "File:", "Kategori:", "Şablon:", "Vikipedi:")):
                continue
            # Son 2 kelime hedef (son virgülden sonraki kısım)
            kelimeler = govde.split(',')[-1].split()
            hedef = " ".join(kelimeler[-2:]) if len(kelimeler) >= 2 else govde
            hedef = re.sub(r'^(bir|bu|o|her)\s+', '', hedef).strip()
            # "ve X" → X al ("ve senarist" → "senarist")
            if hedef.startswith("ve "):
                hedef = hedef[3:].strip()
            if 2 <= len(subject) <= 45 and 2 <= len(hedef) <= 45:
                return subject, hedef
    return None

kabul = 0
filtre = 0
islenen = 0
ornekler = []
with open(YOL, 'r', encoding='utf-8', errors='replace') as f:
    for i, satir in enumerate(f):
        if i >= 500000:
            break
        islenen += 1
        sonuc = isa_cikar(satir)
        if not sonuc:
            continue
        subject, hedef = sonuc
        if not hedef_kaliteli(subject, "isa", hedef):
            filtre += 1
            continue
        r = k.relations.add_relation(subject, "isa", hedef,
                                      source="atlas_test", confidence=0.85)
        if r["accepted"]:
            kabul += 1
            if len(ornekler) < 10:
                ornekler.append((subject, hedef))

print(f"100K satır: {islenen} | +{kabul} kabul, {filtre} filtre")
print("\nÖrnekler:")
for s, h in ornekler:
    print(f"  {s[:35]:37} isa {h[:40]}")
