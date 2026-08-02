#!/usr/bin/env python3
"""
DatasetIngester — Yerel veri setlerinden (JSONL) bilgi damıtma.
5N1K 59K verisi → Altın regex → FastPath/Gate → Kristal Düğüm

LLM KULLANMAZ. 59K örnek saniyeler içinde işlenir.
"""
import sys, os, json, re, time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from kernel_v2 import ASIKernel, FastPathValidator

# Varsayılan veri yolları (masaüstü)
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
DATA_FILES = {
    "5n1k_temiz": os.path.join(DESKTOP, "5n1k_temiz_59k.jsonl"),
    "genel_kultur": os.path.join(DESKTOP, "genel_kultur_5n1k.jsonl"),
}


class DatasetIngester:
    """JSONL veri setlerinden ilişkisel bilgi çıkarıp kristal hafızaya yazar."""

    # İlk cümleden "X, ... bir Y'dir/dır" → isa ilişkisi
    GOLD_ISA = re.compile(
        r'^(?P<subject>[\w\sğüşıöçĞÜŞİÖÇ]{2,40}?),?\s*(?:[\w\sğüşıöçĞÜŞİÖÇ,]{0,80}?)\s*bir\s+'
        r'(?P<target>[\w\sğüşıöçĞÜŞİÖÇ]{2,50}?)'
        r'(?:\'?dir|\'?dır|tir|tır|tur|tür)[\s.!]',
        re.I
    )
    # "X, ... Y'dir" (bir'siz)
    GOLD_ISA2 = re.compile(
        r'^(?P<subject>[\w\sğüşıöçĞÜŞİÖÇ]{2,40}?),?\s*(?:[\w\sğüşıöçĞÜŞİÖÇ,]{0,80}?)\s*'
        r'(?P<target>[\w\sğüşıöçĞÜŞİÖÇ]{2,50}?)'
        r'(?:\'?dir|\'?dır|tir|tır)[\s.!]',
        re.I
    )
    # "X'in Y'si Z'dir" → hasa ilişkisi (SADECE bilinen property'ler)
    GOLD_HASA = re.compile(
        r'^(?P<subject>[\w\sğüşıöçĞÜŞİÖÇ]{2,40}?)(?:nin|nın|in|ın|un|ün)\s+'
        r'(?P<prop>sıcaklığı|büyüklüğü|ağırlığı|hızı|yapısı|şekli|türü|cinsi|maddesi|rengi|'
        r'nüfusu|başkenti|merkezi|yüzölçümü|uzunluğu|yüksekliği|derinliği|'
        r'amacı|görevi|işlevi|nedeni|sonucu)\s+'
        r'(?P<value>[\w\sğüşıöçĞÜŞİÖÇ\-\d.,%°]{2,60}?)(?:\'?dir|\'?dır|\.|,|;)',
        re.I
    )

    def __init__(self, kernel: ASIKernel = None):
        self.kernel = kernel or ASIKernel()
        self.fast_path = FastPathValidator(self.kernel)
        self.stats = {
            "lines_read": 0, "isa_extracted": 0, "hasa_extracted": 0,
            "accepted": 0, "rejected": 0, "unresolved": 0, "duplicates": 0,
            "skipped": 0
        }

    def _extract_relations(self, text: str, subject_hint: str = "") -> list:
        """Metinden isa/hasa ilişkilerini çıkar (LLM'siz)."""
        relations = []
        text = text.strip()
        if not text:
            return relations

        subject = subject_hint

        # ── STRATEJİ 1: "X, <açıklama>, Y'dir" — son virgülden sonraki öbek ──
        # Çoğu 5N1K tanımı bu formattadır:
        # "Varoluşçuluk, 20. yüzyılda gelişen, ..., felsefi akımdır."
        # → subject=Varoluşçuluk, target=felsefi akım
        # SADECE İLK CÜMLE kullanılır (açıklayıcı paragraflar gürültü üretir)
        if not subject:
            # İlk virgüle kadar subject
            first_comma = text.find(',')
            if first_comma > 0:
                subject = text[:first_comma].strip()

        if subject:
            # İlk cümleyi al (nokta ile biten kısım)
            ilk_cumle = re.split(r'[.!?]\s', text)[0] if text else ""
            if not ilk_cumle:
                ilk_cumle = text
            parts = [p.strip() for p in ilk_cumle.split(',')]
            if len(parts) >= 2:
                last_part = parts[-1]
                # "Y'dir" ekini temizle — TÜM Türkçe varyantları
                m = re.match(
                    r'^([\w\sğüşıöçĞÜŞİÖÇ\-]{2,50}?)(?:'
                    r'leridir|larıdır|lerdir|lardır|leridir|larıdır|'
                    r'sidir|sıdır|sidir|sıdır|sudur|südür|'
                    r'idir|ıdır|udur|üdür|tir|tır|tur|tür|'
                    r'\'?dir|\'?dır|dur|dür|dir|dır|'
                    r'ler|lar|si|sı|su|sü)(?:\.|,|;)?$',
                    last_part, re.I
                )
                if m:
                    target = m.group(1).strip()
                    # Kalite: 2-50 karakter, subject değil
                    if 2 <= len(target) <= 50 and target.lower() != subject.lower():
                        # Genel kelimeleri at
                        generic = {"bir", "bu", "şu", "o", "her", "çok", "bazı"}
                        if target.split()[0].lower() not in generic:
                            # Gerçek kategori: 2-6 kelime (uzun öbekler gürültü)
                            kelime_sayisi = len(target.split())
                            # SON KELİME KARA LİSTESİ: tek başına kategori DEĞİL
                            # "Determinant özelliktir" → ANLAMSIZ (hangi özellik?)
                            # "matematiksel özellik" → OK (niteleyen var)
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
                            }
                            son_kelime = target.split()[-1].lower().rstrip("'s")
                            # Tek kelimelik zayıf hedef → reddet
                            if kelime_sayisi == 1 and son_kelime in ZAYIF_SON:
                                pass  # kabul etme
                            elif kelime_sayisi >= 2 and son_kelime in ZAYIF_SON:
                                # Niteleyen var → kabul (örn: "matematiksel özellik")
                                relations.append(("isa", subject, target))
                            else:
                                # Son kelime kara listede değil → kategori kontrolü
                                kategori_sonlari = (
                                    "dalı","türü","tipi","çeşidi","akımı","sistemi","yöntemi",
                                    "tepkime","kavram","süreç","olgu","kuram","teori","yasa",
                                    "ilke","model","yapı","bilim","sanat","hareket","dönem",
                                    "devlet","imparatorluk","kent","ülke","iklim","bitki",
                                    "hayvan","element","bileşik","alan","bölge","molekül",
                                    "enerji","araç","alet","makine","cihaz","canlı","nesne",
                                    "madde","olay","durum","özellik","işlev","dal","tür",
                                    "tip","çeşit","akım","sistem","yöntem","kuram","ilke",
                                    "denklem","fonksiyon","teorem","aksiyom","hipotez",
                                    "yasası","kanunu","kuramı","teorisi","modeli","sistemi",
                                )
                                son_uygun = any(son_kelime.endswith(s) for s in kategori_sonlari)
                                if 1 <= kelime_sayisi <= 6 and son_uygun:
                                    relations.append(("isa", subject, target))

        # ── STRATEJİ 2: Fallback "X ... bir Y'dir" ──
        if not relations:
            m = self.GOLD_ISA.search(text)
            if m:
                if not subject:
                    subject = m.group("subject").strip()
                target = m.group("target").strip().rstrip('.,;:!?')
                if 2 <= len(target) <= 50 and target.lower() != subject.lower():
                    relations.append(("isa", subject, target))

        # ── hasa: "X'in Y'si Z'dir" ──
        m = self.GOLD_HASA.search(text)
        if m:
            s = m.group("subject").strip()
            prop = m.group("prop").strip()
            value = m.group("value").strip().rstrip('.,;:!?')
            if s and prop and value:
                relations.append(("hasa", s, prop, value))

        return relations

    def ingest_jsonl(self, path: str, limit: int = 0, field: str = "ne") -> dict:
        """
        JSONL dosyasından bilgi işle.
        field="ne" → 5N1K tanım alanı, "assistant" → sohbet cevapları
        """
        if not os.path.exists(path):
            return {"error": f"Dosya yok: {path}"}

        start = time.time()
        processed = 0

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if limit and processed >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    self.stats["skipped"] += 1
                    continue

                self.stats["lines_read"] += 1
                processed += 1

                # Metni seç
                text = None
                subject_hint = ""
                if field == "ne" and "5n1k" in record:
                    five = record["5n1k"]
                    text = five.get("ne", "")
                    subject_hint = record.get("konu", "")
                    # İLİŞKİ GENİŞLETME (konsey kararı): 5N1K alanları → ilişki türleri
                    # nerede → located_in, neden → causes, kim → invented_by
                    # Kısa değerler (<80 karakter) güvenli; uzunlar varyasyon yaratıyor
                    if subject_hint:
                        from kernel_v2 import FIELD_TO_RELATION
                        for alan, rel in FIELD_TO_RELATION.items():
                            deger = five.get(alan, "").strip()
                            if deger and 3 < len(deger) <= 80:
                                self._process_relation(subject_hint, rel, deger)
                elif "messages" in record:
                    # Chat formatı: son assistant cevabı
                    for msg in record["messages"]:
                        if msg.get("role") == "assistant" and msg.get("content"):
                            text = msg["content"]
                    if not text:
                        self.stats["skipped"] += 1
                        continue
                elif "content" in record:
                    text = record["content"]
                elif "text" in record:
                    text = record["text"]
                else:
                    self.stats["skipped"] += 1
                    continue

                if not text or len(text) < 15:
                    self.stats["skipped"] += 1
                    continue

                # İlişkileri çıkar ve işle
                relations = self._extract_relations(text, subject_hint)
                for rel in relations:
                    if rel[0] == "isa":
                        _, subj, target = rel
                        self.stats["isa_extracted"] += 1
                        self._process_relation(subj, "isa", target)
                    elif rel[0] == "hasa":
                        _, subj, prop, value = rel
                        self.stats["hasa_extracted"] += 1
                        self._process_relation(subj, "hasa", value, prop)

        elapsed = time.time() - start
        self.stats["elapsed_sec"] = round(elapsed, 2)
        self.stats["rate_per_sec"] = round(self.stats["lines_read"] / max(elapsed, 0.01), 1)
        return self.stats

    def _process_relation(self, subject: str, rel_type: str, target: str,
                          prop: str = ""):
        """
        Gate üzerinden geçir (LLM'siz).
        Dataset bilgisi temiz kaynaktan geldiği için FastPath'e gerek yok:
        gate dedup + contradiction kontrolü yapar, çelişkisiz olanı kabul eder.
        """
        props = {rel_type if rel_type in ("isa", "instance_of", "subclass_of",
                                          "part_of", "used_for", "causes",
                                          "located_in", "invented_by",
                                          "has_property") else (prop or "isa"): target}
        gate = self.kernel.contradictions.gate(
            ne=subject, properties=props,
            source=f"dataset|{rel_type}",
            confidence=0.8
        )
        if gate["accepted"]:
            if gate.get("is_duplicate"):
                self.stats["duplicates"] += 1
            else:
                self.stats["accepted"] += 1
        else:
            self.stats["rejected"] += 1

    def ingest_all(self, limit_per_file: int = 0) -> dict:
        """Tüm masaüstü veri setlerini işle."""
        summary = {}
        for name, path in DATA_FILES.items():
            print(f"📥 {name}: {path}")
            result = self.ingest_jsonl(path, limit=limit_per_file)
            summary[name] = result
            print(f"   ✅ {result.get('accepted', 0)} kabul, "
                  f"{result.get('rejected', 0)} ret, "
                  f"{result.get('unresolved', 0)} unresolved, "
                  f"{result.get('rate_per_sec', 0)}/sn")
        return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ASI-1 DatasetIngester")
    parser.add_argument("--file", help="JSONL dosyası")
    parser.add_argument("--limit", type=int, default=0, help="Max satır (0=sınırsız)")
    parser.add_argument("--field", default="ne", help="Alan adı (ne/assistant)")
    parser.add_argument("--save", action="store_true", help="Sonunda kaydet")
    args = parser.parse_args()

    ingester = DatasetIngester()

    if args.file:
        result = ingester.ingest_jsonl(args.file, limit=args.limit, field=args.field)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        summary = ingester.ingest_all(limit_per_file=args.limit)
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    status = ingester.kernel.get_status()
    print(f"\n📊 Sistem: {status['total_nodes']} düğüm, {status['isolated_nodes']} izole")

    if args.save:
        ingester.kernel.save_knowledge()
        print("💾 Kaydedildi: knowledge_store.json")
