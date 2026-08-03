# -*- coding: utf-8 -*-
"""5n1k_cot haber → olay ilişkisi testi: 1000 haberde verim + kalite"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

YOL = r'C:\Users\alipranac\5n1k-synthetic-data\5n1k_cot_train.jsonl'
k = ASIKernel()
norm = k.axioms._normalize_tr

# KALIPLAR: "X'te gerçekleşti/düzenlendi/yapıldı" → konum
KONUM_KALIP = re.compile(r"([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?)(?:'?da|'?de|'?ta|'?te)\s+(?:gerçekleşti|gerçekleştirildi|düzenlendi|düzenlenen|yapıldı|yapılan|toplandı|açıldı)", re.IGNORECASE)
# "X'te bulunan Y" → Y located_in X (zaten wiki'den var, atla)
# NEDEN: "X ... neden oldu" → causes
NEDEN_KALIP = re.compile(r"([\wğüşıöçĞÜŞİÖÇ\s\-]{3,40}?)\s+(?:neden oldu|yol açtı|sebep oldu)", re.IGNORECASE)

kabul = 0
filtre = 0
konum_sayisi = 0
neden_sayisi = 0
ornekler = []

with open(YOL, 'r', encoding='utf-8') as f:
    for i, satir in enumerate(f):
        if i >= 1000:
            break
        try:
            rec = json.loads(satir)
        except Exception:
            continue
        metin = rec.get("metin", "")
        # Konum: ilk cümlede ara
        m = KONUM_KALIP.search(metin[:300])
        if m:
            olay = m.group(1).strip()
            # "Kahramanmaraş İl, Dönüşüm Merkezi bünyesinde" gibi kesikler — kalite kontrol
            if len(olay) >= 3 and not olay.lower().startswith(("a", "ve", "bu", "bir")):
                konum_sayisi += 1
                # Konum hedefini bul: kalıptan önceki son kelime grubu
                konum = metin[:m.start()].split()[-1].strip("',.;:!?()") if metin[:m.start()].split() else ""
                if konum and hedef_kaliteli(olay, "located_in", konum):
                    r = k.relations.add_relation(olay, "located_in", konum,
                                                 source="cot_haber", confidence=0.8)
                    if r["accepted"]:
                        kabul += 1
                        if len(ornekler) < 8:
                            ornekler.append((olay, konum, "located_in"))
                else:
                    filtre += 1
        # Neden
        m2 = NEDEN_KALIP.search(metin[:300])
        if m2:
            olay = m2.group(1).strip()
            neden_sayisi += 1

print(f"1000 haber: konum kalibi {konum_sayisi}, neden kalibi {neden_sayisi}")
print(f"Kabul: {kabul} | Filtre: {filtre}")
print("\nÖrnekler:")
for o, kn, il in ornekler:
    print(f"  {o[:35]:37} --{il}--> {kn[:30]}")
