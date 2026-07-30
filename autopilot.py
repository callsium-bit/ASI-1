#!/usr/bin/env python3
"""
ASI-1 Oto-Pilot — Kendi kendini yöneten bakım döngüsü.
Her çalıştığında: test → web-ingest → gap analizi → rapor → hata düzelt

Revizyon: FastPath → Contradiction Gate akışı.
Hiçbir bilgi doğrudan Crystal'a yazılmaz — gate zorunludur.
"""
import sys, os, json, time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from kernel_v2 import (ASIKernel, WebKnowledgeIngester, FastPathValidator,
                        AttentionRouter, UnresolvedQueue, CrystalNode)

ENDPOINT = "http://localhost:1234/v1/chat/completions"
MODEL = "google/gemma-4-e4b"
MAX_CONCEPTS = 3  # Her turda işlenecek kavram
REPORT_FILE = os.path.join(SCRIPT_DIR, "autopilot_report.json")

def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def run_cycle():
    log("🚀 Oto-Pilot döngüsü başladı")
    kernel = ASIKernel()
    ingester = WebKnowledgeIngester(kernel, language="tr", timeout=10)
    fp = FastPathValidator(kernel)
    queue = UnresolvedQueue(kernel, batch_size=5,
                            endpoint=ENDPOINT, model=MODEL)

    # İstatistik sayaçları
    stats = {
        "total_items": 0,
        "accepted_by_fast_path": 0,
        "rejected_by_fast_path": 0,
        "unresolved": 0,
        "llm_calls": 0,
        "duplicate_items": 0,
        "new_knowledge": 0,
        "contradictions": 0,
    }

    report = {
        "timestamp": datetime.now().isoformat(),
        "initial_state": kernel.get_status(),
        "concepts_processed": [],
        "errors": [],
        "stats": stats,
        "final_state": {}
    }

    # 1. Boşluk tespiti
    from kernel_v2 import LocalLLMDistiller
    distiller = LocalLLMDistiller(kernel)
    gaps = distiller.detect_gaps(limit=10)
    log(f"🔍 {len(gaps)} boşluk bulundu")

    if not gaps:
        log("✅ Boşluk yok, sistem temiz")
        report["final_state"] = kernel.get_status()
        return report

    # 2. Web'den kavramları işle
    total_accepted = 0
    total_rejected = 0

    for gap in gaps[:MAX_CONCEPTS]:
        concept = gap["concept"]
        log(f"🎯 İşleniyor: {concept} [{gap['type']}]")

        try:
            web_data = ingester.fetch_concept_text(concept, strategy="tr")
            if not web_data:
                report["errors"].append(f"{concept}: Wikipedia'da bulunamadı")
                continue

            # Regex ile çıkar (LLM'siz, hızlı)
            relations_data = ingester.extract_relations_rule_based(concept, web_data["text"])
            relations = relations_data.get("relations", [])

            # Fast-Path doğrulama → Contradiction Gate
            accepted = 0
            rejected = 0
            unresolved_count = 0
            duplicates = 0

            for rel in relations:
                rel_type = rel.get("type", "")
                stats["total_items"] += 1

                fp_result = fp.evaluate(
                    concept, rel_type,
                    target=rel.get("target", ""),
                    prop=rel.get("property", ""),
                    value=str(rel.get("value", ""))
                )

                if fp_result["verdict"] == "accepted":
                    # ✅ DÜZELTME: Doğrudan create_node yerine gate üzerinden geç
                    props = {rel.get("property", "nitelik"): rel.get("value", rel.get("target", ""))}
                    gate_result = kernel.contradictions.gate(
                        ne=concept, properties=props,
                        source=f"autopilot|{web_data['title']}",
                        confidence=float(rel.get("confidence", 0.75))
                    )
                    if gate_result["accepted"]:
                        accepted += 1
                        stats["accepted_by_fast_path"] += 1
                        if gate_result["is_duplicate"]:
                            duplicates += 1
                            stats["duplicate_items"] += 1
                        else:
                            stats["new_knowledge"] += 1
                    else:
                        # gate reddetti (contradiction)
                        rejected += 1
                        stats["contradictions"] += 1

                elif fp_result["verdict"] == "rejected":
                    # ✅ DÜZELTME: Reddedilen bilgiyi izolasyona gönder
                    props = {rel.get("property", "nitelik"): rel.get("value", rel.get("target", ""))}
                    iso_node = CrystalNode(
                        id=kernel.hooks._next_id(), ne=concept,
                        properties=props,
                        source=f"autopilot_rejected|{fp_result['reason'][:60]}",
                        isolated=True, confidence=0.2,
                        status="isolated"
                    )
                    kernel.hooks.nodes[iso_node.id] = iso_node
                    kernel.contradictions.isolation_zone.append(iso_node)
                    rejected += 1
                    stats["rejected_by_fast_path"] += 1

                else:
                    # ✅ DÜZELTME: unresolved → Queue'ya ekle
                    queue.add(
                        concept=concept, rel_type=rel_type,
                        target=rel.get("target", ""),
                        prop=rel.get("property", ""),
                        value=str(rel.get("value", "")),
                        reason=fp_result["reason"]
                    )
                    unresolved_count += 1
                    stats["unresolved"] += 1

            total_accepted += accepted
            total_rejected += rejected

            report["concepts_processed"].append({
                "concept": concept,
                "source": web_data["title"],
                "relations": len(relations),
                "accepted": accepted,
                "rejected": rejected,
                "unresolved": unresolved_count,
                "duplicates": duplicates
            })

            log(f"   ✅ +{accepted} | ❌ -{rejected} | ❓ ?{unresolved_count} | 📖 {web_data['title']}")

        except Exception as e:
            report["errors"].append(f"{concept}: {str(e)[:100]}")
            log(f"   ⚠️ Hata: {e}")

    # 2.5. Queue'da birikenleri flush et
    pending = queue.pending()
    if pending > 0:
        log(f"📬 Queue'da {pending} unresolved öğe var, batch çözülüyor...")
        resolved = queue.resolve_batch()
        stats["llm_calls"] += 1
        total_accepted += resolved
        stats["new_knowledge"] += resolved
        log(f"   ✅ Batch: {resolved}/{pending} çözüldü")

    # 3. Son durum ve istatistik
    report["final_state"] = kernel.get_status()

    # LLM bağımlılık oranı
    total = stats["total_items"]
    if total > 0:
        stats["llm_dependency_ratio"] = round(
            stats["unresolved"] / total, 4
        )
    else:
        stats["llm_dependency_ratio"] = 0.0

    report["stats"] = stats

    # 4. Raporu kaydet
    try:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except:
        pass

    status = report["final_state"]
    log(f"📊 Döngü tamam: {status['total_nodes']} düğüm, "
        f"+{total_accepted} yeni, -{total_rejected} ret")

    # İstatistik özeti
    log(f"📈 İstatistik:")
    log(f"   Total: {stats['total_items']} | "
        f"FastPath Accept: {stats['accepted_by_fast_path']} | "
        f"FastPath Reject: {stats['rejected_by_fast_path']}")
    log(f"   Unresolved→LLM: {stats['unresolved']} | "
        f"Duplicates: {stats['duplicate_items']} | "
        f"New: {stats['new_knowledge']}")
    log(f"   LLM Dependency: {stats['llm_dependency_ratio']:.1%}")

    return report

if __name__ == "__main__":
    run_cycle()
