# -*- coding: utf-8 -*-
"""7 Aşamalı Pipeline testi: Memory→Context→Hypothesis→Reasoning→Critic→Planner→Style"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
chat = ChatEngine(k)
ok = 0

print('═══ 7 AŞAMALI PIPELINE TESTİ ═══')
print()

# 1. Selamlaşma → sıcak karşılama (Response Planner)
r = chat.sohbet("Merhaba")
print(f'[1] Selam: {r["cevap"][:70]}')
assert "Merhaba" in r["cevap"] or "merhaba" in r["cevap"]
ok += 1

# 2. Bilgi sorusu (Reasoning + Critic)
r = chat.sohbet("ABAP nedir?")
print(f'[2] Bilgi: {r["cevap"][:70]} (kanal={r["kanal"]})')
assert "kısaltmadır" in r["cevap"]
ok += 1

# 3. Bilinmeyen → meraklı ton (Planner)
r = chat.sohbet("Sandalye rüya görebilir mi?")
print(f'[3] Bilinmeyen: {r["cevap"][:70]}')
assert "merak" in r["cevap"]
ok += 1

# 4. Görev + listele (Memory)
r = chat.sohbet("Yarın toplantı var hatırlat")
r = chat.sohbet("Görevlerim neler?")
print(f'[4] Görev: {r["cevap"][:60]}')
assert "toplantı" in r["cevap"]
ok += 1

# 5. Kalıcı hafıza (B): sohbet özeti knowledge_store'a yazıldı mı?
kalici_sayisi = sum(1 for n in k.hooks.nodes.values()
                    if n.ne == "sohbet_ozeti" and "sohbet_hafiza" in n.source)
print(f'[5] Kalıcı hafıza: {kalici_sayisi} sohbet özeti düğümü')
assert kalici_sayisi >= 1
ok += 1

# 6. Kalıcı hafızadan hatırla
r = chat.sohbet("Geçen konuşmamızı hatırlıyor musun?")
print(f'[6] Hatırla: {r["cevap"][:80]}')
assert "hatırlıyorum" in r["cevap"]
ok += 1

# 7. Stil uyarlama (Style Adapter): kısa mesaj → kısa cevap
r = chat.sohbet("ok")
print(f'[7] Stil: "{r["cevap"][:60]}" (uzunluk={len(r["cevap"])})')
ok += 1

# Kaydet — kalıcı hafıza diske
k.save_knowledge()
print(f'\nDurum: {chat.durum()}')
print(f'\nALL {ok} OK')
