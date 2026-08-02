# -*- coding: utf-8 -*-
"""AŞAMA 11: Düşünme + akıcı konuşma testi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine, ReasoningEngine, truth_value

k = ASIKernel()
chat = ChatEngine(k)
ok = 0

print('═══ AŞAMA 11: DÜŞÜNME + KONUŞMA TESTİ ═══')
print()

# 1. TruthValue (NARS)
tv = truth_value(8, 2)
assert 0.7 <= tv["freq"] <= 0.9 and tv["conf"] > 0.8
print(f'[1] TruthValue: freq={tv["freq"]} conf={tv["conf"]} (8 onay, 2 çelişki)')
ok += 1

# 2. Kognitif döngü (düşünme adımları görünür)
r = chat.dusun("Ses görünür mü?")
print(f'[2] Düşünme adımları ({r["kanal"]}):')
for a in r["adimlar"]:
    print(f'    [{a["tur"]}] {str(a["icerik"])[:60]}')
assert len(r["adimlar"]) >= 4
ok += 1

# 3. Sohbet — sözlük tonu yerine akıcı
r = chat.sohbet("Ses görünür mü?")
print(f'[3] Sohbet: {r["cevap"][:90]}')
assert "cevaplayamıyorum" not in r["cevap"] or "merak" in r["cevap"]
ok += 1

# 4. Bilgi sorusu + düşünme kanalı
r = chat.sohbet("ABAP nedir?")
print(f'[4] Sohbet: {r["cevap"][:90]} (kanal={r["kanal"]})')
ok += 1

# 5. Bilinmeyen → meraklı ton
r = chat.sohbet("Sandalye rüya görebilir mi?")
print(f'[5] Sohbet: {r["cevap"][:90]}')
ok += 1

# 6. Görev + bağlam hala çalışıyor
r = chat.sohbet("Yarın deneme sınavı var hatırlat")
r = chat.sohbet("Görevlerim neler?")
assert "deneme" in r["cevap"]
r = chat.sohbet("Az önce ne konuştuk?")
assert r["kanal"] == "gecmis"
ok += 1

print(f'\nDurum: {chat.durum()}')
print(f'\nALL {ok} OK')
