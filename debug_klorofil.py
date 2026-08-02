# -*- coding: utf-8 -*-
"""klorofil tanımı + SON_EK kontrolü debug"""
import sys, os, re
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
data = k.web_ingester.fetch_concept_text("klorofil", strategy="tr")
metin = data.get("text", "") if data else ""
print(f"Metin uzunluk: {len(metin)}")
ilk = re.split(r'[.!?]\s', metin)[0]
print(f"İlk cümle ({len(ilk)}): ...{ilk[-100:]}")
print()
SON_EK = ("dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür",
          "dırlar", "dirler", "durler", "türüdür", "türüdir", "türüdür")
t = ilk.strip().rstrip('.').strip()
print(f"Son 20 karakter: ...{t[-20:]}")
for ek in SON_EK:
    if t.endswith(ek):
        print(f"✅ '{ek}' ile bitiyor")
        break
else:
    print("❌ Hiçbir ek ile bitmiyor")
