# -*- coding: utf-8 -*-
"""5N1K veri yapısı inceleme"""
import sys, os, json
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

YOL = os.path.join(os.path.expanduser("~"), "Desktop", "5n1k_temiz_59k.jsonl")
with open(YOL, 'r', encoding='utf-8') as f:
    for i, satir in enumerate(f):
        rec = json.loads(satir)
        print(f"Kayıt {i}:")
        print(f"  keys: {list(rec.keys())}")
        if "5n1k" in rec:
            print(f"  5n1k keys: {list(rec['5n1k'].keys()) if isinstance(rec['5n1k'], dict) else type(rec['5n1k'])}")
            print(f"  5n1k: {str(rec['5n1k'])[:150]}")
        print(f"  tam: {str(rec)[:200]}")
        if i >= 2:
            break
