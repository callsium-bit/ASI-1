# -*- coding: utf-8 -*-
"""BellaTurca metinlerinden isa cikarim testi"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()

# Altın regex (BellaTurca metinleri makale metni — ilk cumleler tanim olabilir)
GOLD = re.compile(
    r'^([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?),?\s*(?:[\w\sğüşıöçĞÜŞİÖÇ,]{0,90}?)\s*bir\s+'
    r'([\w\sğüşıöçĞÜŞİÖÇ]{2,45}?)(?:\'?dir|\'?dır|tir|tır|dur|dür|tur|tür)[\s.!]'
)

VERI = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\bella_akademik\dergi_.jsonl'

bulunan = 0
toplam = 0
ornekler = []
with open(VERI, 'r', encoding='utf-8') as f:
    for line in f:
        toplam += 1
        try:
            rec = json.loads(line)
        except:
            continue
        metin = rec.get('text', '')
        if not metin or len(metin) < 40:
            continue
        ilk = re.split(r'[.!?]\s', metin.strip())[0].strip()
        if len(ilk) < 25 or len(ilk) > 300:
            continue
        m = GOLD.search(ilk)
        if m:
            hedef = m.group(2).strip().rstrip('.,;:!?')
            if 2 <= len(hedef) <= 45:
                bulunan += 1
                if len(ornekler) < 8:
                    ornekler.append((m.group(1).strip()[:25], hedef, ilk[:80]))
        if toplam >= 3000:
            break

print(f'3000 satirda: {bulunan} isa kalibi')
print()
for s, t, i in ornekler:
    print(f'  [{s:27}] -> {t[:35]:37} | {i[:50]}')
