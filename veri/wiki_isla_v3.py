# -*- coding: utf-8 -*-
"""Wikipedia TR -> ilişki genişletme (part_of, causes, located_in)
Konsey kararı: isa tekeli ölümcül. Makale gövdelerinden ilişki kalıpları çıkar.
subject = makale başlığı, target = kalıp öncesi öbek.
Örn: "Asya'nın bir parçasıdır" → title part_of Asya
Çıktı: veri/wiki_iliskiler.jsonl
"""
import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import pyarrow.parquet as pq

SRC_DIR = r'C:\Users\alipranac\.cache\huggingface\hub\datasets--wikimedia--wikipedia\snapshots\b04c8d1ceb2f5cd4588862100d08de323dccfbaa\20231101.tr'
OUT = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\wiki_iliskiler.jsonl'

# ── İLİŞKİ KALIPLARI: target'ı yakala (subject = title) ──
# (regex, relation) — target = grup(1), sonra temizlik
AP = r"'?"  # apostrophe opsiyonel (Anadolu'da)
ILISKI_KALIPLARI = [
    # part_of: "Y'nin bir parçasıdır" / "Y'nin parçasıdır"
    (re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?)(?:\'nın|\'in|\'nin|\'nin|\'nun)?\s*(?:bir\s+)?parçası(?:dır|dır|dır)', re.IGNORECASE), "part_of"),
    # located_in: "Y'de bulunur" / "Y'de yer alır" / "Y'de yaşar"
    (re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?)' + AP + r'(?:de|da|te|ta)\s+(?:bulunur|yer alır|yaşar|görülür)', re.IGNORECASE), "located_in"),
    # causes: "Y'ye neden olur" / "Y'ye yol açar"
    (re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?)' + AP + r'(?:ye|ya|e|a)\s+(?:neden olur|yol açar|sebep olur)', re.IGNORECASE), "causes"),
    # causes: "Y'den kaynaklanır" → title causes Y
    (re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?)' + AP + r'(?:den|dan|ten|tan)\s+kaynaklanır', re.IGNORECASE), "causes"),
    # part_of: "Y'nin bir bölümüdür"
    (re.compile(r'([\wğüşıöçĞÜŞİÖÇ\s\-]{2,40}?)(?:\'nın|\'in|\'nin|\'nun)?\s*(?:bir\s+)?bölümü(?:dür|dür|dür)', re.IGNORECASE), "part_of"),
]

def temizle(s):
    """Kalıp sonucunu temizle: bağlaçları, iyelik kalıntılarını at."""
    s = s.strip().strip('.,;:!?()[]"\'')
    s = re.sub(r"('nın|'in|'nin|'nun|'ının|'sinin)$", "", s).strip()
    # Çok kelimeli çıktıysa SON kelimeyi al (ilişki hedefi genelde tek kelime)
    kelimeler = s.split()
    if len(kelimeler) > 1:
        s = kelimeler[-1]
    if len(s) < 3 or len(s) > 50:
        return ""
    return s

toplam = 0
yazilan = 0
ornekler = []

with open(OUT, 'w', encoding='utf-8') as out:
    for dosya in sorted(os.listdir(SRC_DIR)):
        if not dosya.endswith('.parquet'):
            continue
        p = os.path.join(SRC_DIR, dosya)
        table = pq.read_table(p, columns=['title', 'text'])
        for title, text in zip(table.column('title').to_pylist(),
                               table.column('text').to_pylist()):
            toplam += 1
            if toplam % 100000 == 0:
                print(f"  {toplam} makale | {yazilan} ilişki", flush=True)
            if not text or len(text) < 100:
                continue
            giris = text[:800]
            ilk_3 = " ".join(giris.split()[:60])
            for kalip, rel in ILISKI_KALIPLARI:
                m = kalip.search(ilk_3)
                if not m:
                    continue
                hedef = temizle(m.group(1))
                if not hedef:
                    continue
                # title'ın kendisiyle eşleşmesin (döngü)
                if hedef.lower() == title.lower():
                    continue
                rec = {"subject": title, "relation": rel, "target": hedef}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                yazilan += 1
                if len(ornekler) < 10:
                    ornekler.append(rec)
                break

print(f"\nTAMAM: {toplam} makale, {yazilan} ilişki")
for o in ornekler:
    print(f"  {o['subject'][:35]:37} --{o['relation']}--> {o['target'][:40]}")
