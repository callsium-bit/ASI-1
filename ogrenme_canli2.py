# -*- coding: utf-8 -*-
"""Araştır-öğren v2: düzeltilmiş GOLD stratejisi"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine

k = ASIKernel()
norm = k.axioms._normalize_tr

# Yanlış öğrenilen kuark düğümlerini temizle (arastirma kaynaklı)
silinen = 0
for nid, n in list(k.hooks.nodes.items()):
    if norm(n.ne) == "kuark" and "arastirma" in n.source:
        del k.hooks.nodes[nid]
        silinen += 1
print(f"Temizlenen yanlış kuark: {silinen}")

chat = ChatEngine(k)

print(f"\n=== 'klorofil' ARAŞTIR-ÖĞREN (yeni kavram) ===")
r1 = chat.sohbet("klorofil nedir?")
print(f"[1] İLK: {r1['cevap'][:120]}")

# Öğrenme durumunu kontrol et
ogrenildi = False
for n in k.hooks.nodes.values():
    if norm(n.ne) == "klorofil" and "arastirma" in n.source:
        ogrenildi = True
        print(f"    ✅ ÖĞRENDİ: klorofil isa {n.properties}")
        break
if not ogrenildi:
    print("    ⚠️ Öğrenme kaydı yok")

k.save_knowledge()

r3 = chat.sohbet("klorofil nedir?")
print(f"[2] TEKRAR: {r3['cevap'][:120]}")
