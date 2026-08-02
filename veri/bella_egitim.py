# -*- coding: utf-8 -*-
"""BellaTurca -> isa çıkarımı -> kalite filtresi -> gate -> kristal (eğitim hattı)
Önceki test: 2000 satır → +83 kabul (%4). Şimdi tam ölçek.
Kalite filtresi: veri/iliski_filtresi.py (iyelik ekleri + zayıf hedefler) + Feynman kuralı (kernel'de).
"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

k = ASIKernel()
BELLA_DIR = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\bella_akademik'

# ── İSA KALIBI: "X, bir Y'dir." / "X bir Y'dir" — SIKI (arada max 1-2 sıfat) ──
# GEVŞEK kalıp gürültü üretiyordu ("nun kendini hiçe saydığı...") — daraltıldı
ISA_KALIPLARI = [
    re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?),\s*(?:(?:küçük|büyük|önemli|özel|temel|genel|farklı|basit|yeni)\s+)?bir\s+([\wğüşıöçĞÜŞİÖÇ]{2,40}?)(?:dır|dir|dur|dür|tır|tir)\b', re.IGNORECASE),
    re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?)\s+(?:(?:küçük|büyük|önemli|özel|temel|genel|farklı|basit|yeni)\s+)?bir\s+([\wğüşıöçĞÜŞİÖÇ]{2,40}?)(?:dır|dir|dur|dür|tır|tir)\b', re.IGNORECASE),
]

def ilk_cumleler(metin, n=3):
    """Metnin ilk n cümlesini al (makale girişi tanım içerir)."""
    cumleler = re.split(r'(?<=[.!?])\s+', metin)
    return " ".join(cumleler[:n])

kabul = 0
ret = 0
filtre = 0
tekrar = 0
islenen_satir = 0
ornekler = []

for dosya_adi in sorted(os.listdir(BELLA_DIR)):
    if not dosya_adi.endswith('.jsonl'):
        continue
    yol = os.path.join(BELLA_DIR, dosya_adi)
    with open(yol, 'r', encoding='utf-8') as f:
        for satir in f:
            try:
                rec = json.loads(satir)
                metin = rec.get("text", "")
            except Exception:
                continue
            islenen_satir += 1
            if len(metin) < 50:
                continue
            giris = ilk_cumleler(metin)
            for kalip in ISA_KALIPLARI:
                m = kalip.search(giris)
                if not m:
                    continue
                hedef = m.group(2).strip().rstrip('.,;:!?')
                # subj burada kullanılmıyor — boş geç (hedef kalitesi kontrolü)
                if not hedef_kaliteli("", "isa", hedef):
                    filtre += 1
                    break
                sonuc = k.relations.add_relation(
                    m.group(1).strip()[:40], "isa", hedef,
                    source="bella_egitim", confidence=0.8
                )
                if sonuc["accepted"]:
                    kabul += 1
                    if len(ornekler) < 8:
                        ornekler.append((m.group(1).strip()[:35], hedef))
                elif sonuc.get("is_duplicate"):
                    tekrar += 1
                else:
                    ret += 1
                break
            if islenen_satir % 200000 == 0:
                print(f"  {islenen_satir} satır | +{kabul} kabul, {ret} ret, {filtre} filtre", flush=True)

k.save_knowledge()
print(f"\nTAMAM: {islenen_satir} satır | +{kabul} kabul, {ret} ret, {filtre} filtre, {tekrar} tekrar")
print(f"Toplam düğüm: {len(k.hooks.nodes)}")
print("\nÖrnekler:")
for s, h in ornekler:
    print(f"  {s:37} isa {h}")
