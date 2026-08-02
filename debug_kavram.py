# -*- coding: utf-8 -*-
"""klorofil/kuark düğüm durumu debug"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
norm = k.axioms._normalize_tr
for hedef_kelime in ["klorofil", "kuark"]:
    print(f"--- {hedef_kelime} ---")
    var = False
    for n in k.hooks.nodes.values():
        if norm(n.ne) == hedef_kelime:
            var = True
            print(f"  {n.ne} | props: {n.properties} | src: {n.source[:50]} | izole: {n.isolated}")
    if not var:
        print("  DÜĞÜM YOK — bilinmiyor")
