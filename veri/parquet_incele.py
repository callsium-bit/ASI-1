# -*- coding: utf-8 -*-
"""turkish-wiki-qa-4mil parquet yapisini incele"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import pandas as pd

p = r'C:\Users\alipranac\.cache\huggingface\hub\datasets--hcsolakoglu--turkish-wikipedia-qa-4-million\snapshots\d979eb01bc0de4907b23ef4473f04ef13f8a9bf0\data\turkish-wiki-qa-4mil.parquet'

df = pd.read_parquet(p, engine='pyarrow')
print('Satir sayisi:', len(df))
print('Kolonlar:', list(df.columns))
print()
# İlk 3 satır
for i in range(min(3, len(df))):
    row = df.iloc[i]
    print(f'--- Kayit {i} ---')
    for col in df.columns:
        val = str(row[col])[:200]
        print(f'  {col}: {val}')
    print()
