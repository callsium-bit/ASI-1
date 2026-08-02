# -*- coding: utf-8 -*-
"""BellaTurca küçük test: 50K satırda kaç kabul (bugfix sonrası)"""
import sys, os, json
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel
import re as _re

k = ASIKernel()
ISA_KALIPLARI = [
    _re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?),\s*(?:(?:küçük|büyük|önemli|özel|temel|genel|farklı|basit|yeni)\s+)?bir\s+([\wğüşıöçĞÜŞİÖÇ]{2,40}?)(?:dır|dir|dur|dür|tır|tir)\b', _re.IGNORECASE),
    _re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?)\s+(?:(?:küçük|büyük|önemli|özel|temel|genel|farklı|basit|yeni)\s+)?bir\s+([\wğüşıöçĞÜŞİÖÇ]{2,40}?)(?:dır|dir|dur|dür|tır|tir)\b', _re.IGNORECASE),
]

yol = r'veri\bella_akademik\dergi_.jsonl'
kabul = ret = filtre = 0
ornekler = []
with open(yol, 'r', encoding='utf-8') as f:
    for i, satir in enumerate(f):
        if i >= 50000:
            break
        try:
            metin = json.loads(satir).get("text", "")
        except Exception:
            continue
        giris = " ".join(_re.split(r'(?<=[.!?])\s+', metin)[:3])
        for kalip in ISA_KALIPLARI:
            m = kalip.search(giris)
            if not m:
                continue
            hedef = m.group(2).strip().rstrip('.,;:!?')
            if not hedef_kaliteli("", "isa", hedef):
                filtre += 1
                break
            sonuc = k.relations.add_relation(
                m.group(1).strip()[:40], "isa", hedef,
                source="bella_test", confidence=0.8)
            if sonuc["accepted"]:
                kabul += 1
                if len(ornekler) < 8:
                    ornekler.append((m.group(1).strip()[:35], hedef))
            else:
                ret += 1
            break

print(f"50K satır: +{kabul} kabul, {ret} ret, {filtre} filtre")
for s, h in ornekler:
    print(f"  {s:37} isa {h}")
