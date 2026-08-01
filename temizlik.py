# -*- coding: utf-8 -*-
"""Mevcut bilgi tabanını kalite filtrele: zayıf düğümleri izole et"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
from kernel_v2 import ASIKernel

k = ASIKernel()

# Zayıf son kelimeler (tek başına kategori değil)
ZAYIF_SON = {
    "özellik","sistem","model","alan","yapı","durum","işlev",
    "dal","tür","tip","çeşit","akım","yöntem","kuram","ilke",
    "kavram","terim","süreç","olgu","nesne","varlık","madde",
    "cisim","parça","bölüm","örnek","gösterge","aralık","ölçek",
    "ölçü","sabit","hareket","canlı","araç","alet","makine",
    "cihaz","enerji","olay","iş","biçim","hal","şekil","yön",
    "değer","sınır","bölge","katman","tabaka","düzey","grup",
    "küme","topluluk","birim","unsur","öge","eleman","prensip",
    "mekanizma","düzen","kural","kuralı","yasa","kanun","güç",
    "kuvvet","etki","sonuç","neden","sebep","amaç","hedef",
    "reddi","gölgesi","canavar","tartışma","alanı","yaradır",
    "paketidir","paketi","göstergesi","sınırı","değeri",
    "sahip","hali","süresi","olmuşlar","olmuş","kavuşturmuş",
    "sürmekte","yapısına","üzerinden","için","olarak","gibi",
    "yara","nadır","zorunluluk","zorunluluğu","etkisi","göstergesi",
    "kullanan","başarmış","başlamış","geliştirilmiş","oluşturulmuş",
    "na","ne","dan","den","tan","ten",
}

# Fiil bitişleri: son kelime fiil eki taşıyorsa kategori değildir
# "yaşaması", "ilerlemesi", "getirmiş", "sürmek", "kavuşturmuş"
FIIL_BITISLERI = (
    "ması", "mesi", "mış", "miş", "muş", "müş",
    "mak", "mek", "makta", "mekte", "maktadır", "mektedir",
    "tır", "tir", "dur", "dür",
)

def kok_soy(s):
    """Çoğul/iyelik eklerini sıyır: olmuşlar→olmuş, yöntemi→yöntem"""
    for e in ("lar", "ler", "sı", "si", "su", "sü", "i", "ı", "u", "ü", "nin", "nın", "in", "ın"):
        if s.endswith(e) and len(s) > len(e) + 2:
            kok = s[:-len(e)]
            # Türkçe ünsüz yumuşaması: k→ğ ("özelliği" → "özelliğ" → "özellik")
            if kok.endswith("ğ") and len(kok) > 2:
                kok = kok[:-1] + "k"
            return kok
    return s

tum = list(k.hooks.nodes.values())
aktif_oncesi = sum(1 for n in tum if not n.isolated)
izole_edilen = 0
kaliteli = 0

for node in tum:
    if node.isolated:
        continue
    props = node.properties
    if not props:
        continue
    # Her property değerini kontrol et
    zayif_mi = False
    for key, val in props.items():
        if key == 'isa':
            val_str = str(val).strip().lower()
            kelimeler = val_str.split()
            son = kelimeler[-1].rstrip("'s") if kelimeler else ""
            # Tek kelime zayıf son → izole
            if len(kelimeler) == 1 and son in ZAYIF_SON:
                zayif_mi = True
                break
            # Fiil bitişli son kelime → izole (kategori değil)
            kok = kok_soy(son)
            if any(kok.endswith(e) for e in FIIL_BITISLERI):
                zayif_mi = True
                break
            # Zayıf son kelime (iyelik eki sıyrılmış haliyle de kontrol)
            if son in ZAYIF_SON or kok in ZAYIF_SON:
                zayif_mi = True
                break
            # Anlamsız kısa hedef (5 karakterden az anlamlı kelime yok)
            if len(val_str) < 6:
                zayif_mi = True
                break
        elif isinstance(val, str) and len(val) > 120:
            # Çok uzun değerler gürültü (nerede/neden alanlarından kalma)
            zayif_mi = True
            break

    if zayif_mi:
        node.isolated = True
        node.status = "isolated"
        node.source = f"{node.source} | kalite_filtre"
        k.contradictions.isolation_zone.append(node)
        izole_edilen += 1
    else:
        kaliteli += 1

print('=== KALİTE FİLTRESİ ===')
print(f'Aktif (önce): {aktif_oncesi}')
print(f'İzole edilen: {izole_edilen}')
print(f'Kaliteli kalan: {kaliteli}')

# Kaydet
k.save_knowledge()
print(f'\n💾 Kaydedildi: {len(k.hooks.nodes)} düğüm')

# Kaliteli örnekler
print('\n=== KALİTELİ ÖRNEKLER ===')
goster = 0
for n in sorted(k.hooks.nodes.values(), key=lambda x: x.ne):
    if not n.isolated and 'isa' in n.properties and goster < 25:
        print(f'  {n.ne[:40]:42} -> {str(n.properties)[:60]}')
        goster += 1
