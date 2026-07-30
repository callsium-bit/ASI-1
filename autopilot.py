#!/usr/bin/env python3
"""
ASI-1 Oto-Pilot — Kendi kendini yöneten bakım döngüsü.
Her çalıştığında: test → web-ingest → gap analizi → rapor → hata düzelt
"""
import sys, os, json, time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from kernel_v2 import ASIKernel, WebKnowledgeIngester, FastPathValidator, AttentionRouter

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
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "initial_state": kernel.get_status(),
        "concepts_processed": [],
        "errors": [],
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
            
            # Fast-Path doğrulama
            accepted = 0
            rejected = 0
            for rel in relations:
                rel_type = rel.get("type", "")
                fp_result = fp.evaluate(
                    concept, rel_type,
                    target=rel.get("target", ""),
                    prop=rel.get("property", ""),
                    value=str(rel.get("value", ""))
                )
                if fp_result["verdict"] == "accepted":
                    kernel.hooks.create_node(
                        ne=concept,
                        properties={rel.get("property", "nitelik"): rel.get("value", rel.get("target", ""))},
                        source="autopilot"
                    )
                    accepted += 1
                elif fp_result["verdict"] == "rejected":
                    rejected += 1

            total_accepted += accepted
            total_rejected += rejected
            
            report["concepts_processed"].append({
                "concept": concept,
                "source": web_data["title"],
                "relations": len(relations),
                "accepted": accepted,
                "rejected": rejected
            })
            
            log(f"   ✅ +{accepted} | ❌ -{rejected} | 📖 {web_data['title']}")
            
        except Exception as e:
            report["errors"].append(f"{concept}: {str(e)[:100]}")
            log(f"   ⚠️ Hata: {e}")

    # 3. Son durum
    report["final_state"] = kernel.get_status()
    
    # 4. Raporu kaydet
    try:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    except:
        pass

    status = report["final_state"]
    log(f"📊 Döngü tamam: {status['total_nodes']} düğüm, "
        f"+{total_accepted} yeni, -{total_rejected} ret")
    
    return report

if __name__ == "__main__":
    run_cycle()
