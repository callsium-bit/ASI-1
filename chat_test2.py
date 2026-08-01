# -*- coding: utf-8 -*-
"""AŞAMA 10 testi v2: görev kapatma düzeltmesi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)
ok = 0

# Görev ekle
r = chat.sohbet("Yarın marketten ekmek almayı hatırla")
print(f"[1] Ekle: {r['cevap'][:50]}")
assert "Hatırladım" in r["cevap"]
ok += 1

# Listele
r = chat.sohbet("Görevlerim neler?")
print(f"[2] Listele: {r['cevap'][:50]}")
assert "ekmek" in r["cevap"]
ok += 1

# Kapat (düzeltme: "ekmek görevini unut" → kapat)
r = chat.sohbet("ekmek görevini unut")
print(f"[3] Kapat: {r['cevap'][:50]}")
assert "kapatıldı" in r["cevap"], r["cevap"]
ok += 1

# Kapatıldı mı?
r = chat.sohbet("Görevlerim neler?")
print(f"[4] Son liste: {r['cevap'][:50]}")
assert "ekmek" not in r["cevap"], "Hala listede!"
ok += 1

# Bağlam + çekirdek
r = chat.sohbet("Az önce ne konuştuk?")
print(f"[5] Bağlam: {r['cevap'][:60]}")
assert r["kanal"] == "gecmis"
ok += 1

r = chat.sohbet("Ses gorunur mu?")
print(f"[6] Çekirdek: {r['cevap'][:50]}")
assert "algisal" in str(r["cevap"]).replace("ı","i")
ok += 1

print(f"\nALL {ok} OK")
