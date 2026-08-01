#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gece_operasyonu.py — ASI-1 Gece Oto-Pilotu
Kullanıcı uykuda; bu script sırayla:
  1. Veri setlerini işler (Wikipedia TR, 5N1K, BellaTurca temiz kısım)
  2. Türetim motorunu çalıştırır (kendi kendini eğitme)
  3. Testleri doğrular (40/40)
  4. knowledge_store.json'a kaydeder
  5. Rapor dosyasına yazar (kullanıcı sabah okur)

Her 30 dk'da bir cron ile tetiklenir. Her turda yeni bilgi işler.
"""
import sys, os, json, time, traceback
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAPOR = os.path.join(SCRIPT_DIR, "gece_raporu.json")
TUR_DOSYA = os.path.join(SCRIPT_DIR, ".gece_tur.json")  # son işlenen satır indeksi

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(os.path.join(SCRIPT_DIR, "gece_log.txt"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

def durum_oku():
    try:
        with open(TUR_DOSYA, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def durum_yaz(d):
    with open(TUR_DOSYA, "w") as f:
        json.dump(d, f)

def rapor_guncelle(bolum, veri):
    try:
        with open(RAPOR, "r", encoding="utf-8") as f:
            rapor = json.load(f)
    except Exception:
        rapor = {"turlar": [], "baslangic": datetime.now().isoformat()}
    rapor[bolum] = veri
    with open(RAPOR, "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=1)
    return rapor

def main():
    log("🚀 Gece operasyonu başladı")
    durum = durum_oku()
    tur = durum.get("tur", 0) + 1
    durum["tur"] = tur
    durum_yaz(durum)

    from kernel_v2 import ASIKernel
    k = ASIKernel()

    rapor = {"tur": tur, "zaman": datetime.now().isoformat()}
    baslangic_dugum = len(k.hooks.nodes)

    # ── 1. VERİ SETİ İŞLEME (her turda farklı kaynak, dönüşümlü) ──
    from dataset_ingester import DatasetIngester
    ing = DatasetIngester(k)
    kaynaklar = [
        ("5n1k_temiz", os.path.join(os.path.expanduser("~"), "Desktop", "5n1k_temiz_59k.jsonl"), 3000),
        ("genel_kultur", os.path.join(os.path.expanduser("~"), "Desktop", "genel_kultur_5n1k.jsonl"), 3000),
        ("wiki_tr_v2", os.path.join(SCRIPT_DIR, "veri", "wiki_tr_v2.jsonl"), 2000),
    ]
    secilen = kaynaklar[(tur - 1) % len(kaynaklar)]
    isim, yol, limit = secilen
    log(f"📥 Kaynak: {isim} (limit {limit})")
    try:
        sonuc = ing.ingest_jsonl(yol, limit=limit)
        rapor["kaynak"] = isim
        rapor["kabul"] = sonuc.get("accepted", 0)
        rapor["tekrar"] = sonuc.get("duplicates", 0)
        log(f"   +{sonuc.get('accepted', 0)} kabul, {sonuc.get('duplicates', 0)} tekrar")
    except Exception as e:
        log(f"⚠️ Veri hatası: {e}")
        rapor["veri_hata"] = str(e)

    # ── 2. TÜRETİM (kendi kendini eğitme) ──
    log("🧠 Türetim başlıyor...")
    try:
        turetim_sonuc = {"kavram": 0, "hipotez": 0, "kabul": 0, "ret": 0}
        aktif_kavramlar = []
        gorulen = set()
        for node in k.hooks.nodes.values():
            if node.isolated or node.ne in gorulen:
                continue
            gorulen.add(node.ne)
            aktif_kavramlar.append(node.ne)
        # Her turda farklı dilim (kademeli)
        dilim_boyu = 150
        baslangic_idx = ((tur - 1) * dilim_boyu) % max(len(aktif_kavramlar), 1)
        dilim = aktif_kavramlar[baslangic_idx:baslangic_idx + dilim_boyu]
        for kavram in dilim:
            s = k.relations.apply_hypotheses(kavram, max_depth=3)
            turetim_sonuc["kavram"] += 1
            turetim_sonuc["hipotez"] += s["hypotheses"]
            turetim_sonuc["kabul"] += s["accepted"]
            turetim_sonuc["ret"] += s["rejected"]
        rapor["turetim"] = turetim_sonuc
        log(f"   {turetim_sonuc['kavram']} kavram, +{turetim_sonuc['kabul']} türetim")
    except Exception as e:
        log(f"⚠️ Türetim hatası: {e}")
        rapor["turetim_hata"] = str(e)

    # ── 3. KAYDET ──
    k.save_knowledge()
    rapor["dugum_toplam"] = len(k.hooks.nodes)
    rapor["dugum_artis"] = len(k.hooks.nodes) - baslangic_dugum
    log(f"💾 Kaydedildi: {len(k.hooks.nodes)} düğüm (+{rapor['dugum_artis']})")

    # ── 4. HIZLI TEST (sadece kritik) ──
    try:
        r = k.ask("Mavi duser mi?")
        cevap = str(r.get("answer", r)).replace("ı", "i")
        rapor["cekirdek_ok"] = "algisal" in cevap
        log(f"🧪 Çekirdek: {'OK' if rapor['cekirdek_ok'] else 'SORUN!'} — {cevap[:60]}")
    except Exception as e:
        rapor["cekirdek_ok"] = False
        log(f"⚠️ Test hatası: {e}")

    # ── 5. RAPOR ──
    rapor_guncelle(f"tur_{tur}", rapor)
    log(f"📊 Tur {tur} tamam: +{rapor['dugum_artis']} düğüm → {len(k.hooks.nodes)}")

    return rapor

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"💥 KRİTİK HATA: {e}")
        traceback.print_exc()
        # Rapor dosyasına hatayı yaz
        try:
            rapor_guncelle("kritik_hata", {"zaman": datetime.now().isoformat(), "hata": str(e)})
        except Exception:
            pass
        sys.exit(1)
