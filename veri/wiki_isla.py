# -*- coding: utf-8 -*-
"""Wikipedia TR dump -> ilk cumle tanimlarindan isa cikarim + JSONL kayit"""
import sys, os, json, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import pyarrow.parquet as pq

SRC_DIR = r'C:\Users\alipranac\.cache\huggingface\hub\datasets--wikimedia--wikipedia\snapshots\b04c8d1ceb2f5cd4588862100d08de323dccfbaa\20231101.tr'
OUT = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\wiki_tr_ilk_cumleler.jsonl'

# Altın regex: "X, ... bir Y'dir/dır" ve "X, ... Y'dir"
GOLD = re.compile(
    r'^([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?),?\s*(?:[\w\sğüşıöçĞÜŞİÖÇ,]{0,90}?)\s*bir\s+'
    r'([\w\sğüşıöçĞÜŞİÖÇ]{2,45}?)(?:\'?dir|\'?dır|tir|tır|dur|dür|tur|tür)[\s.!]'
)

toplam = 0
yazilan = 0
ornekler = []

for dosya in sorted(os.listdir(SRC_DIR)):
    if not dosya.endswith('.parquet'):
        continue
    print(f'Isleniyor: {dosya}')
    table = pq.read_table(os.path.join(SRC_DIR, dosya))
    df = table.to_pandas()
    print(f'  Satir: {len(df)}')

    for i in range(len(df)):
        toplam += 1
        baslik = str(df.iloc[i].get('title', '')) if 'title' in df.columns else ''
        metin = str(df.iloc[i].get('text', '')) if 'text' in df.columns else ''
        if not metin or len(metin) < 30:
            continue
        # İlk cümle
        ilk = re.split(r'[.!?]\s', metin.strip())[0].strip()
        if len(ilk) < 25 or len(ilk) > 300:
            continue
        m = GOLD.search(ilk)
        if m:
            target = m.group(2).strip().rstrip('.,;:!?')
            if 2 <= len(target) <= 45:
                kayit = {"konu": baslik, "tanim": ilk, "hedef": target}
                with open(OUT, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(kayit, ensure_ascii=False) + '\n')
                yazilan += 1
                if len(ornekler) < 10:
                    ornekler.append((baslik, target, ilk[:100]))

print(f'\nToplam makale: {toplam}')
print(f'Isa kalibi yakalanan: {yazilan}')
print()
for b, t, i in ornekler:
    print(f'  [{b[:25]:27}] -> {t[:35]:37} | {i[:60]}')
