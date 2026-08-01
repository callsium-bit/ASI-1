# -*- coding: utf-8 -*-
"""Wikipedia TR ilk cumlelerini ASI-1'e isle: gate -> kristal"""
import sys, os, json
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from kernel_v2 import ASIKernel

k = ASIKernel()
k.hooks.nodes.clear()
k.hooks.hooks.clear()
k.contradictions.isolation_zone.clear()
k._seed_knowledge()

VERI = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\wiki_tr_ilk_cumleler.jsonl'

kabul = 0
ret = 0
tekrar = 0
gurultu = 0

# Zayıf son kelimeler (tekrar kullanım)
ZAYIF_SON = {"özellik","sistem","model","alan","yapı","durum","işlev","dal","tür","tip",
             "çeşit","akım","yöntem","kuram","ilke","kavram","terim","süreç","olgu","nesne",
             "varlık","madde","cisim","parça","bölüm","örnek","gösterge","aralık","ölçek",
             "ölçü","sabit","hareket","canlı","araç","alet","makine","cihaz","enerji","olay",
             "iş","biçim","hal","şekil","yön","değer","sınır","bölge","katman","tabaka",
             "düzey","grup","küme","topluluk","birim","unsur","öge","eleman","prensip",
             "mekanizma","düzen","kural","kuralı","yasa","kanun","güç","kuvvet","etki",
             "sonuç","neden","sebep","amaç","hedef","sahip","hali","bakış","tanımlama",
             "kullanılmakta","yapı üzerine kurulmuş","ad","ay","gün","yıl","liste"}

with open(VERI, 'r', encoding='utf-8') as f:
    for line in f:
        rec = json.loads(line)
        konu = rec.get('konu', '')
        hedef = rec.get('hedef', '').strip()
        if not konu or not hedef:
            continue
        # Kalite filtresi
        son = hedef.split()[-1].lower().rstrip("'s") if hedef.split() else ""
        if len(hedef) < 3 or son in ZAYIF_SON:
            gurultu += 1
            continue

        # Gate'ten geçir
        gate = k.contradictions.gate(
            ne=konu, properties={"isa": hedef},
            source="wikipedia_tr|ilk_cumle",
            confidence=0.75
        )
        if gate["accepted"]:
            if gate.get("is_duplicate"):
                tekrar += 1
            else:
                kabul += 1
        else:
            ret += 1

print(f'Kabul: {kabul} | Ret: {ret} | Tekrar: {tekrar} | Gürültü filtresi: {gurultu}')
status = k.get_status()
print(f'Toplam düğüm: {status["total_nodes"]} | İzole: {status["isolated_nodes"]}')

k.save_knowledge()
print('💾 knowledge_store.json kaydedildi')

# Örnekler
print('\n=== YENİ DÜĞÜM ÖRNEKLERİ ===')
g = 0
for n in sorted(k.hooks.nodes.values(), key=lambda x: x.ne):
    if not n.isolated and n.source.startswith('wikipedia') and g < 20:
        print(f'  {n.ne[:35]:37} -> {str(n.properties)[:50]}')
        g += 1
