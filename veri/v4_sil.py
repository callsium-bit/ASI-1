# -*- coding: utf-8 -*-
"""wiki_tr_v4 (2. cümle) düğümlerini tamamen sil — kalite felaketi, modeli bozuyor"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
once = len(k.hooks.nodes)
silinen = 0
for nid, n in list(k.hooks.nodes.items()):
    if n.source.startswith("wiki_tr_v4"):
        del k.hooks.nodes[nid]
        silinen += 1
k.save_knowledge()
print(f"Silinen v4: {silinen} | Once: {once} | Sonra: {len(k.hooks.nodes)}")
