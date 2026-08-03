# -*- coding: utf-8 -*-
"""ne-index hız testi: mahalle gibi yoğun kavramda search"""
import sys, os, time
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
norm = k.axioms._normalize_tr

# Yoğun kavram: mahalle
basla = time.time()
for _ in range(1000):
    d = k.hooks.search_5n1k(ne="mahalle")
sure = time.time() - basla
print(f"1000x search_5n1k('mahalle'): {sure:.2f}sn ({len(d)} dugum)")

# find_duplicate
basla = time.time()
for _ in range(1000):
    d2 = k.hooks.find_duplicate("mahalle", {"isa": "yerel topluluk"})
sure2 = time.time() - basla
print(f"1000x find_duplicate: {sure2:.2f}sn")

# Ne-index boyutu
print(f"_ne_index: {len(k.hooks._ne_index)} kavram")
