# -*- coding: utf-8 -*-
"""Wikipedia TR -> ilk cumle tanimlarindan isa cikarim v2 (genisletilmis regex)
Kalite filtresi: ZAYIF_SON + fiil bitisleri + kok_soy (unlus yumusamasi)
"""
import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import pyarrow.parquet as pq

SRC_DIR = r'C:\Users\alipranac\.cache\huggingface\hub\datasets--wikimedia--wikipedia\snapshots\b04c8d1ceb2f5cd4588862100d08de323dccfbaa\20231101.tr'
OUT = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\wiki_tr_v2.jsonl'

# ── ZAYIF SON KELIMELER (tek basina kategori degil) ──
ZAYIF_SON = {
    "özellik","sistem","model","alan","yapı","durum","işlev","dal","tür","tip",
    "çeşit","akım","yöntem","kuram","ilke","kavram","terim","süreç","olgu","nesne",
    "varlık","madde","cisim","parça","bölüm","örnek","gösterge","aralık","ölçek",
    "ölçü","sabit","hareket","canlı","araç","alet","makine","cihaz","enerji","olay",
    "iş","biçim","hal","şekil","yön","değer","sınır","bölge","katman","tabaka",
    "düzey","grup","küme","topluluk","birim","unsur","öge","eleman","prensip",
    "mekanizma","düzen","kural","kuralı","yasa","kanun","güç","kuvvet","etki",
    "sonuç","neden","sebep","amaç","hedef","sahip","hali","bakış","tanımlama",
    "kullanılmakta","yapı üzerine kurulmuş","ad","ay","gün","yıl","liste","şey",
    "durumda","şekilde","biçimde","olarak","gibi","için","üzerine","üzerinde",
    "kullanan","yapan","eden","oluşturan","sağlayan","içeren","barındıran",
    "verilen","denilen","bilinen","kullanılan","yapılan","geliştirilen",
    "yara","nadır","zorunluluk","etkisi","göstergesi","süresi","kısmı","bölümü",
}

# ── FIIL BITISLERI ──
FIIL_BITISLERI = (
    "ması","mesi","mış","miş","muş","müş","mak","mek","makta","mekte",
    "maktadır","mektedir","tır","tir","dur","dür",
)

def kok_soy(s):
    for e in ("lar","ler","sı","si","su","sü","i","ı","u","ü","nin","nın","in","ın"):
        if s.endswith(e) and len(s) > len(e) + 2:
            kok = s[:-len(e)]
            if kok.endswith("ğ") and len(kok) > 2:
                kok = kok[:-1] + "k"
            return kok
    return s

def kalite_kontrol(hedef):
    """Hedef kaliteli mi? True=iyi, False=gürültü"""
    h = hedef.strip().lower()
    if len(h) < 3 or len(h) > 60:
        return False
    kelimeler = h.split()
    if not kelimeler:
        return False
    son = kelimeler[-1].rstrip("'s")
    kok = kok_soy(son)
    # Fiil bitişi → gürültü
    if any(kok.endswith(e) for e in FIIL_BITISLERI):
        return False
    # Zayıf son kelime → gürültü
    if son in ZAYIF_SON or kok in ZAYIF_SON:
        return False
    # İlk kelime zayıf → gürültü
    if kelimeler[0].rstrip("'s") in ZAYIF_SON:
        return False
    return True

# ── REGEX KALIPLARI (öncelik sıralı) ──
KALIPLAR = [
    # 1. "X, ... bir Y'dir/dır" (en güçlü)
    re.compile(
        r'^([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?),\s*(?:[\w\sğüşıöçĞÜŞİÖÇ,]{0,80}?)\s*bir\s+'
        r'([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?)(?:\'?dir|\'?dır|tir|tır|dur|dür|tur|tür)[\s.!]'),
    # 2. "X, ... Y'dir/dır" (bir'siz — orta)
    re.compile(
        r'^([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?),?\s*(?:[\w\sğüşıöçĞÜŞİÖÇ,]{0,70}?)\s+'
        r'([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?)(?:\'?dir|\'?dır|tir|tır)[\s.!]'),
    # 3. "X, ... Y olarak bilinir/tanımlanır" (orta)
    re.compile(
        r'^([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?),?\s*(?:[\w\sğüşıöçĞÜŞİÖÇ,]{0,60}?)\s+'
        r'([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?)\s+olarak\s+(?:bilinir|tanımlanır|adlandırılır)'),
    # 4. "X'e Y denir" (zayıf ama bazen doğru)
    re.compile(
        r'^([\w\sğüşıöçĞÜŞİÖÇ\-]{2,45}?)(?:e|a|ye|ya)?\s+'
        r'([\w\sğüşıöçĞÜŞİÖÇ\-]{2,40}?)\s+denir'),
]

toplam = 0
yazilan = 0
ornekler = []

for dosya in sorted(os.listdir(SRC_DIR)):
    if not dosya.endswith('.parquet'):
        continue
    print(f'Isleniyor: {dosya}')
    table = pq.read_table(os.path.join(SRC_DIR, dosya))
    df = table.to_pandas()
    print(f'  Satir: {len(df)}')

    for i in range(len(df)):
        toplam += 1
        baslik = str(df.iloc[i].get('title', '')) if 'title' in df.columns else ''
        metin = str(df.iloc[i].get('text', '')) if 'text' in df.columns else ''
        if not metin or len(metin) < 30:
            continue
        # İlk cümle
        ilk = re.split(r'[.!?]\s', metin.strip())[0].strip()
        if len(ilk) < 25 or len(ilk) > 350:
            continue

        # Kalıpları sırayla dene
        hedef = None
        for kp in KALIPLAR:
            m = kp.search(ilk)
            if m:
                cand = m.group(2).strip().rstrip('.,;:!?')
                if kalite_kontrol(cand):
                    hedef = cand
                    break

        if hedef:
            kayit = {"konu": baslik, "tanim": ilk, "hedef": hedef}
            with open(OUT, 'a', encoding='utf-8') as f:
                f.write(json.dumps(kayit, ensure_ascii=False) + '\n')
            yazilan += 1
            if len(ornekler) < 15:
                ornekler.append((baslik, hedef, ilk[:90]))

print(f'\nToplam makale: {toplam}')
print(f'Kaliteli isa yakalanan: {yazilan} (oran: {yazilan/toplam*100:.2f}%)')
print()
for b, t, i in ornekler:
    print(f'  [{b[:25]:27}] -> {t[:35]:37} | {i[:55]}')
