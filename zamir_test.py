# -*- coding: utf-8 -*-
"""Zamir çözümleme testi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)
ok = 0

print('═══ ZAMİR ÇÖZÜMLEME TESTİ ═══\n')

# Diyalog 1: ABAP bağlamı
r = chat.sohbet("ABAP nedir?")
print(f'[1] ABAP nedir? → {r["cevap"][:60]}')
assert "kısaltma" in r["cevap"] or "programlama" in r["cevap"]
ok += 1

r = chat.sohbet("Peki bu nerede kullanılır?")
print(f'[2] Peki BU nerede kullanılır? → {r["cevap"][:70]} (kanal={r["kanal"]})')
assert r["kanal"] == "zamir", f"zamir kanali bekleniyor: {r['kanal']}"
assert "ABAP" not in r["cevap"].lower() or len(r["cevap"]) > 10
ok += 1

# Diyalog 2: Enflasyon bağlamı
r = chat.sohbet("Enflasyon nedir?")
print(f'[3] Enflasyon nedir? → {r["cevap"][:60]}')
ok += 1

r = chat.sohbet("Bu neden olur?")
print(f'[4] BU neden olur? → {r["cevap"][:70]} (kanal={r["kanal"]})')
assert r["kanal"] == "zamir"
ok += 1

print(f'\nALL {ok} OK')
