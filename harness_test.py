# -*- coding: utf-8 -*-
"""ChatGPT harness senaryosu bizim RelationEngine'de (çapraz kompozisyon + oracle)"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()
re_ = k.relations

print('=== CHATGPT HARNESS SENARYOSU (bizim engine) ===')
print()

# Gözlemlenen olgular
gorulen = [
    ("serçe", "isa", "kuş"),
    ("kuş", "isa", "hayvan"),
    ("kanat", "part_of", "kuş"),
    ("kuş", "located_in", "ağaç"),
    ("ağaç", "located_in", "orman"),
    ("orman", "located_in", "Türkiye"),
    ("bıçak", "used_for", "kesme"),
    ("bıçak", "part_of", "mutfak_aleti"),
    ("mutfak_aleti", "used_for", "yemek_hazırlama"),
    ("yağmur", "causes", "sel"),
    ("sel", "causes", "hasar"),
]
for s, r, t in gorulen:
    re_.add_relation(s, r, t, source="harness_gorulen", confidence=1.0)
print(f"[1] Gözlemlenen olgu: {len(gorulen)}")

# Çapraz kompozisyon türetimi
turetilen = re_.derive_composition("serçe", max_depth=3)
print(f"\n[2] serçe çapraz türetim: {len(turetilen)}")
for d in turetilen:
    print(f"    {d['subject']} --{d['relation']}--> {d['target']}  [{d['rule']}]")

# Tüm hipotezler
hip = re_.derive_hypotheses("serçe", max_depth=3)
print(f"\n[3] serçe tüm hipotezler: {len(hip)}")
for h in hip:
    print(f"    {h['subject']} --{h['relation']}--> {h['target']}  [{h['rule']}]")

# Oracle gate testi
print(f"\n[4] Oracle gate (türetilmiş → UNCERTAIN, store'a girmez):")
o = re_.oracle
for h in hip[:5]:
    resp = o.check_derived(h)
    print(f"    {h['subject']} --{h['relation']}--> {h['target']}: {resp['verdict']} ({resp['source']})")

# Manuel onay sonrası
print(f"\n[5] Manuel onay sonrası:")
if hip:
    h0 = hip[0]
    o.approve(h0["subject"], h0["relation"], h0["target"])
    resp = o.check_derived(h0)
    print(f"    {h0['subject']} --{h0['relation']}--> {h0['target']}: {resp['verdict']} ✅")
    print(f"    Oracle istatistik: {o.get_stats()}")

# Konsey koşulu: sıfır türetim = kuralları düzelt
print(f"\n[6] Konsey koşulu: {re_.get_stats()['derived_count']} türetim — motor {'ÇALIŞIYOR' if re_.get_stats()['derived_count'] > 0 else 'SIFIR!'}")
