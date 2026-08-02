# -*- coding: utf-8 -*-
"""Ad-hoc: ReasoningEngine kognitif döngü taslağı — kernel_v2.py'ye eklenecek"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel

k = ASIKernel()

# Kognitif döngü: OLGU → HEDEF → PLAN → OPERASYON → GERİ BİLDİRİM
def kognitif_dongu(kernel, soru):
    """NARS esinli 5 adımlı düşünme döngüsü (LLM'siz)."""
    adimlar = []

    # 1. OLGU (girdi)
    adimlar.append(("olgu", f"Soru alındı: {soru}"))

    # 2. HEDEF (ne bilmek istiyoruz?)
    norm = kernel.axioms._normalize_tr
    q = norm(soru)
    if any(t in q for t in ("nedir", "kimdir", "neymiş")):
        hedef = "kavram_tanimi"
    elif "mi" in q or "mı" in q or "mu" in q or "mü" in q:
        hedef = "dogrulama"
    elif "neden" in q or "niçin" in q:
        hedef = "nedensellik"
    elif "nerede" in q or "nereye" in q:
        hedef = "konum"
    else:
        hedef = "kavram_tanimi"
    adimlar.append(("hedef", f"Hedef: {hedef}"))

    # 3. PLAN (hangi kaynaklar?)
    plan = []
    # a) Bilgi tabanı
    kavramlar = [w for w in q.split() if len(w) > 3 and not w in
                 ("nedir", "kimdir", "neden", "nerede", "nasıl", "ne", "bir", "mi", "mı", "mu", "mü")]
    if kavramlar:
        plan.append(("bilgi_tabani", kavramlar[:3]))
    # b) Aksiyom/çıkarım
    plan.append(("aksiyom_cikarim", soru))
    # c) Araştırma (bilgi tabanında yoksa)
    plan.append(("arastirma", soru))
    adimlar.append(("plan", f"Plan: {plan}"))

    # 4. OPERASYON (adım adım çöz)
    cevap = None
    for tur, veri in plan:
        if tur == "bilgi_tabani":
            r = kernel.ask(soru)
            c = str(r.get("answer", r))
            if c and "cevaplayamıyorum" not in c and "bulunamadı" not in c:
                cevap = c
                adimlar.append(("operasyon", f"Bilgi tabanından: {c[:60]}"))
                break
        elif tur == "aksiyom_cikarim":
            # Çıkarım motorunu dene
            pass
        elif tur == "arastirma":
            # Wikipedia araştırması (sadece bilgi tabanı çözemediyse)
            pass

    # 5. GERİ BİLDİRİM
    if cevap:
        adimlar.append(("geribildirim", "Çözüldü ✅"))
    else:
        adimlar.append(("geribildirim", "Çözülemedi — araştırma gerekli"))
        cevap = "Bu soruyu şu an cevaplayamıyorum. Araştırmam gerekiyor."

    return {"cevap": cevap, "adimlar": adimlar}

# Test
for soru in ["ABAP nedir?", "Mandelbrot kümesi nedir?", "Sandalye rüya görebilir mi?"]:
    r = kognitif_dongu(k, soru)
    print(f"\n? {soru}")
    for tur, detay in r["adimlar"]:
        print(f"   [{tur}] {detay}")
    print(f"   → {r['cevap'][:80]}")
