# -*- coding: utf-8 -*-
"""AŞAMA 10 testi: SohbetBağlamı + GörevTakibi + VektörUzayı"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine, VectorSpace, ConversationMemory, TaskMemory

ok = 0
k = ASIKernel()
chat = ChatEngine(k)

# 1. Vektör uzayı: benzerlik ölçümü
vs = VectorSpace()
s1 = vs.benzerlik("güneş sistemi", "güneş enerjisi")
s2 = vs.benzerlik("güneş sistemi", "bilgisayar programlama")
print(f"[1] Vektör: gunes-sistem vs gunes-enerji: {s1:.3f} | vs bilgisayar: {s2:.3f}")
assert s1 > s2, f"Benzerlik hatası: {s1} vs {s2}"
ok += 1

# 2. Görev ekle
r = chat.sohbet("Yarın marketten ekmek almayı hatırla")
print(f"[2] Görev ekle: {r['cevap']} (kanal={r['kanal']})")
assert r["kanal"] == "gorev" and "Hatırladım" in r["cevap"]
ok += 1

# 3. Görev listele
r = chat.sohbet("Görevlerim neler?")
print(f"[3] Görev listele: {r['cevap']}")
assert "ekmek" in r["cevap"]
ok += 1

# 4. Görev kapat
r = chat.sohbet("ekmek görevini unut")
print(f"[4] Görev kapat: {r['cevap']}")
ok += 1

# 5. Bağlam: geçmiş sorusu
r = chat.sohbet("Gökyüzü neden mavi?")
print(f"[5] Bilgi sorusu: {r['cevap'][:60]} (kanal={r['kanal']})")
r = chat.sohbet("Az önce ne konuştuk?")
print(f"    Geçmiş sorusu: {r['cevap'][:80]}")
assert r["kanal"] == "gecmis"
ok += 1

# 6. Çekirdek hala çalışıyor
r = chat.sohbet("Tas ucar mi?")
print(f"[6] Çekirdek: {r['cevap'][:60]}")
ok += 1

print(f"\nDurum: {chat.durum()}")
print(f"\nALL {ok} OK")
