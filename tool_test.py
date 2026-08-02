# -*- coding: utf-8 -*-
"""ToolRegistry bugfix testi v2"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
ok = 0

# BUG'lar: araçlara gitmemeli
r = k.ask("Karın erime noktası kaç derecedir?")
cevap = str(r.get("answer", r))
assert "hesap" not in cevap and "Güvensiz" not in cevap, f"BUG: {cevap}"
ok += 1
print("[1] Erime noktasi: {}".format(cevap[:60]))

r = k.ask("Su ne zaman kaynar?")
cevap = str(r.get("answer", r))
assert "Bugün" not in cevap, f"BUG: {cevap}"
ok += 1
print("[2] Su ne zaman: {}".format(cevap[:60]))

# Gerçek araçlar hala çalışıyor
r = k.ask("7 çarpı 8 kaç eder?")
cevap = str(r.get("answer", r))
assert "56" in cevap, f"BUG: {cevap}"
ok += 1
print("[3] 7x8: {}".format(cevap[:40]))

r = k.ask("Saat kaç?")
cevap = str(r.get("answer", r))
assert "Bugün" in cevap or "saat" in cevap.lower(), f"BUG: {cevap}"
ok += 1
print("[4] Saat kac: {}".format(cevap[:60]))

# Bilgi sorusu normal
r = k.ask("ABAP nedir?")
cevap = str(r.get("answer", r))
assert "kısaltmadır" in cevap or "Wikipedia" in cevap, f"BUG: {cevap}"
ok += 1
print("[5] ABAP: {}".format(cevap[:60]))

print("\nALL {} OK".format(ok))
