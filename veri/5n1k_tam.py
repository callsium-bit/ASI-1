# -*- coding: utf-8 -*-
"""5N1K 59K tam ölçek v2: konu→subject, ne'den isa, nerede/neden/kim→ilişki"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
re_ = k.relations
YOL = os.path.join(os.path.expanduser("~"), "Desktop", "5n1k_temiz_59k.jsonl")

def temizle(s):
    s = str(s).strip().strip('.,;:!?()[]"\' ')
    s = re.sub(r'\s+', ' ', s)
    return s

def isa_cikar(tanim):
    """Tanım sonundan isa hedefi çıkar: '... felsefi akımdır' → 'felsefi akım'"""
    SON_EK = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür", "dırlar", "dirler")
    t = str(tanim).strip().rstrip('.').strip()
    for ek in SON_EK:
        if t.endswith(ek) and len(t) > len(ek) + 2:
            govde = t[:-len(ek)].strip()
            kelimeler = govde.split()
            son = " ".join(kelimeler[-2:]) if len(kelimeler) >= 2 else govde
            son = re.sub(r'^(bir|bu|o|her)\s+', '', son).strip()
            if 2 <= len(son) <= 45:
                return son
    return None

kabul = 0
ret = 0
tekrar = 0
boş = 0
ornekler = []

with open(YOL, 'r', encoding='utf-8') as f:
    for satir in f:
        try:
            rec = json.loads(satir)
        except Exception:
            continue
        konu = temizle(rec.get("konu", ""))
        if not konu or len(konu) > 50:
            boş += 1
            continue
        five = rec.get("5n1k", {})
        islenen = False

        # 1. "ne" tanımından isa
        ne = temizle(five.get("ne", ""))
        hedef = isa_cikar(ne) if ne else None
        if hedef:
            islenen = True
            sonuc = re_.add_relation(konu, "isa", hedef,
                                     source="5n1k_tam|ne", confidence=0.85)
            if sonuc["accepted"]:
                kabul += 1
                if len(ornekler) < 10:
                    ornekler.append((konu, "isa", hedef))
            elif sonuc.get("is_duplicate"):
                tekrar += 1
            else:
                ret += 1

        # 2. nerede/neden/kim → ilişki
        for alan, rel in [("nerede", "located_in"), ("neden", "causes"), ("kim", "invented_by")]:
            deger = temizle(five.get(alan, ""))
            if not deger or deger.lower() in ("yok", "bilinmiyor", "belirsiz", "bilinmemektedir", "none"):
                continue
            if len(deger) < 2 or len(deger) > 60:
                continue
            islenen = True
            sonuc = re_.add_relation(konu, rel, deger,
                                     source=f"5n1k_tam|{alan}", confidence=0.85)
            if sonuc["accepted"]:
                kabul += 1
                if len(ornekler) < 10:
                    ornekler.append((konu, rel, deger))
            elif sonuc.get("is_duplicate"):
                tekrar += 1
            else:
                ret += 1

        if not islenen:
            boş += 1

k.save_knowledge()
print(f"TAMAM: +{kabul} kabul, {ret} ret, {tekrar} tekrar, {boş} boş")
print(f"Toplam düğüm: {len(k.hooks.nodes)}")
print("\nÖrnekler:")
for s, r, t in ornekler:
    print(f"  {s[:32]:34} --{r}--> {t[:38]}")
