# -*- coding: utf-8 -*-
"""Kendi kendini egitme: mevcut bilgi tabaninda turetim (modus ponens)"""
import sys, os, time
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
re_ = k.relations

print(f'Bilgi tabani: {len(k.hooks.nodes)} dugum ({sum(1 for n in k.hooks.nodes.values() if not n.isolated)} aktif)')
print()

# Tüm aktif kavramlar üzerinde türetim (örnekleme: ilk 300 kavram)
aktif_kavramlar = []
görülen = set()
for node in k.hooks.nodes.values():
    if node.isolated or node.ne in görülen:
        continue
    görülen.add(node.ne)
    aktif_kavramlar.append(node.ne)

print(f'Turetim icin {len(aktif_kavramlar)} benzersiz kavram taranacak')
print()

start = time.time()
toplam_hipotez = 0
toplam_kabul = 0
toplam_ret = 0
ornekler = []

# İlk 200 kavramda türetim (zaman kısıtı)
for i, kavram in enumerate(aktif_kavramlar[:200]):
    sonuc = re_.apply_hypotheses(kavram, max_depth=3)
    toplam_hipotez += sonuc["hypotheses"]
    toplam_kabul += sonuc["accepted"]
    toplam_ret += sonuc["rejected"]
    if sonuc["accepted"] > 0 and len(ornekler) < 10:
        ornekler.append((kavram, sonuc))

elapsed = time.time() - start
print(f'=== SONUÇ ({elapsed:.1f}sn) ===')
print(f'Hipotez: {toplam_hipotez} | Kabul: {toplam_kabul} | Ret: {toplam_ret}')

print('\n=== TÜRETİLEN YENİ BİLGİLER (örnekler) ===')
for kavram, s in ornekler:
    print(f'  {kavram}: +{s["accepted"]} yeni ilişki ({s["hypotheses"]} hipotezden)')

# Türetim logundan örnekler
print('\n=== TÜRETİM ZİNCİRLERİ (log) ===')
g = 0
for d in re_.get_stats()["derived_log"]:
    if g >= 8: break
    print(f'  {d["subject"]} {d["relation"]} {d["target"]}  [kural: {d["rule"]}, {d["chain"][-2:]} ->]')
    g += 1

k.save_knowledge()
print(f'\n💾 Kaydedildi: {len(k.hooks.nodes)} dugum')
