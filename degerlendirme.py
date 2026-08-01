# -*- coding: utf-8 -*-
"""ASI-1 kapsamli degerlendirme sinavi"""
import sys, os, json, time
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel
from collections import Counter

k = ASIKernel()
def norm(s):
    return s.replace("ı","i").replace("ğ","g").replace("ü","u").replace("ş","s").replace("ö","o").replace("ç","c").lower()

print('══════════════════════════════════════════')
print(' ASI-1 DEĞERLENDİRME SINAVI')
print('══════════════════════════════════════════')

# ── 1. Bilgi tabanı istatistik ──
aktif = [n for n in k.hooks.nodes.values() if not n.isolated]
izole = [n for n in k.hooks.nodes.values() if n.isolated]
pc = Counter()
for n in aktif:
    for p in n.properties: pc[p] += 1
print(f'\n[1] BİLGİ TABANI')
print(f'    Toplam: {len(k.hooks.nodes)} | Aktif: {len(aktif)} | İzole: {len(izole)}')
print(f'    İlişki dağılımı: {dict(pc.most_common(10))}')
isa_oran = pc.get('isa', 0) / max(len(aktif), 1)
print(f'    isa oranı: %{isa_oran*100:.1f} {"(SÖZLÜK TEHLİKESİ)" if isa_oran > 0.9 else "(ÇOK İLİŞKİLİ ✅)"}')

# ── 2. Çekirdek aksiyom testi ──
print(f'\n[2] ÇEKİRDEK AKSİYOMLAR')
cekirdek = [
    'Tas ucar mi?',
    'Ses gorunur mu?',
    'Kitap icilir mi?',
    'Ruzgar yutulabilir mi?',
]
for s in cekirdek:
    r = k.ask(s)
    cevap = str(r.get('answer', r))
    print(f'    ? {s}\n      → {cevap[:85]}')

# ── 3. Bilgi sorgusu (hafıza + türetim) ──
print(f'\n[3] BİLGİ SORGULARI')
bilgi = ['ABAP nedir?', 'Refrakter malzemeler nedir?', 'Enflasyon nedir?']
for s in bilgi:
    r = k.ask(s)
    cevap = str(r.get('answer', r))
    kaynak = '🛠️WIKI' if 'Wikipedia' in cevap or 'wikipedia' in cevap else '🧠HAFIZA'
    print(f'    {kaynak} ? {s}\n      → {cevap[:85]}')

# ── 4. Türetim kapasitesi ──
print(f'\n[4] TÜRETİM MOTORU')
t0 = time.time()
re_ = k.relations
# Mevcut zincirlerden türetim
test_kavramlar = ['su', 'kar', 'yagmur', 'gunes', 'mavi']
toplam_hip = 0
toplam_kab = 0
for kv in test_kavramlar:
    s = re_.apply_hypotheses(kv, max_depth=3)
    toplam_hip += s['hypotheses']
    toplam_kab += s['accepted']
print(f'    {len(test_kavramlar)} kavram → {toplam_hip} hipotez, +{toplam_kab} kabul ({time.time()-t0:.1f}sn)')
print(f'    Toplam türetim log: {re_.get_stats()["derived_count"]}')

print(f'\n══════════════════════════════════════════')
