# -*- coding: utf-8 -*-
"""Parquet -> JSONL donusturucu (sistem Python 3.12 ile calistir)"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pyarrow.parquet as pq

src = r'C:\Users\alipranac\.cache\huggingface\hub\datasets--hcsolakoglu--turkish-wikipedia-qa-4-million\snapshots\d979eb01bc0de4907b23ef4473f04ef13f8a9bf0\data\turkish-wiki-qa-4mil.parquet'
dst = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\turkish-wiki-qa.jsonl'

print('Okunuyor...')
table = pq.read_table(src)
print('Kolonlar:', table.column_names)
print('Satir:', table.num_rows)

# İlk 3 satırı göster
df = table.to_pandas()
for i in range(min(3, len(df))):
    print(f'--- {i} ---')
    for col in df.columns:
        print(f'  {col}: {str(df.iloc[i][col])[:200]}')

# JSONL'e yaz (ilk 5000 satır - test)
n = min(5000, len(df))
with open(dst, 'w', encoding='utf-8') as f:
    for i in range(n):
        row = {col: (df.iloc[i][col] if hasattr(df.iloc[i][col], 'item') else str(df.iloc[i][col])) for col in df.columns}
        # numpy/pandas tiplerini JSON uyumlu yap
        row2 = {}
        for k, v in row.items():
            if hasattr(v, 'item'):
                try: v = v.item()
                except: pass
            row2[k] = v
        f.write(json.dumps(row2, ensure_ascii=False) + '\n')
print(f'Ilk {n} satir -> {dst} yazildi')
