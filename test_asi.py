#!/usr/bin/env python3
"""
ASI-1 — Mimari Revizyon Test Senaryoları

Test 1: Duplicate — Aynı bilgi iki kez gelirse iki ayrı node oluşmamalı
Test 2: Fast Path — Deterministic bilgi LLM çağırmamalı
Test 3: Unresolved — Fast Path çözemediği bilgiyi LLM pipeline'a göndermeli
Test 4: Contradiction — Çelişkili bilgi Crystal'a doğrudan yazılmamalı
Test 5: Persistence — Restart sonrası bilgi korunmalı
Test 6: Evidence — Aynı bilgi farklı kaynaklardan gelirse verification güncellemeli
Test 7: Regression — Mevcut çalışan kernel davranışları bozulmamalı
"""
import sys
import os
import json
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from kernel_v2 import (
    ASIKernel, CrystalNode, HookEngine, AxiomEngine,
    ContradictionEngine, FastPathValidator, StreamingIngestionPipeline,
    UnresolvedQueue, KnowledgeStore, EntityType, TurkishParser,
    LocalLLMDistiller
)

PASS = 0
FAIL = 0


def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}: {detail}")


def test_1_duplicate():
    """Ayni bilgi iki kez gelirse iki ayri node olusmamalı."""
    print("\nTEST 1: Duplicate Detection")

    kernel = ASIKernel(auto_load=False)
    initial_count = len(kernel.hooks.nodes)

    # Ayni bilgiyi iki kez gate uzerinden gonder
    r1 = kernel.contradictions.gate(
        ne="paris", properties={"baskent": "fransa"}, source="kaynak_1"
    )
    r2 = kernel.contradictions.gate(
        ne="paris", properties={"baskent": "fransa"}, source="kaynak_2"
    )

    test("Birinci bilgi kabul edilmeli", r1["accepted"])
    test("Ikinci bilgi de kabul edilmeli", r2["accepted"])
    test("Ikinci bilgi duplicate olarak isaretlenmeli", r2["is_duplicate"])
    test("Ayni node_id dondurulmeli", r1["node_id"] == r2["node_id"])

    # Sadece 1 yeni dugum olusmalı
    new_count = len(kernel.hooks.nodes) - initial_count
    test("Sadece 1 yeni dugum olusmalı (duplicate olmamalı)", new_count == 1,
         f"Beklenen 1, alinan {new_count}")

    # verification_count kontrol
    node = kernel.hooks.nodes[r1["node_id"]]
    test("verification_count 2 olmali", node.verification_count == 2,
         f"Beklenen 2, alinan {node.verification_count}")

    # Evidence iki kaynaği da icermeli
    test("Evidence her iki kaynagi icermeli",
         "kaynak_1" in node.evidence and "kaynak_2" in node.evidence,
         f"Evidence: {node.evidence}")


def test_2_fast_path_no_llm():
    """Deterministic olarak cozulebilen bilgi LLM cagirmamali."""
    print("\nTEST 2: Fast Path — LLM Gereksiz")

    kernel = ASIKernel(auto_load=False)
    fp = FastPathValidator(kernel)

    # Net kabul: mavi isa renk (zincirde mevcut)
    r1 = fp.evaluate("mavi", "isa", target="renk")
    test("'mavi isa renk' accepted olmali", r1["verdict"] == "accepted")

    # Net ret: mavi isa madde (tip cakismasi)
    r2 = fp.evaluate("mavi", "isa", target="madde")
    test("'mavi isa madde' rejected olmali", r2["verdict"] == "rejected")

    # Net ret: ses hasa agirlik
    r3 = fp.evaluate("ses", "hasa", prop="ağırlık", value="5kg")
    test("'ses hasa agirlik' rejected olmali", r3["verdict"] == "rejected")

    # Istatistik: hicbir LLM cagrisi yapilmamis olmali
    test("Unresolved 0 olmali (LLM gerekmez)",
         fp.stats["unresolved"] == 0,
         f"unresolved={fp.stats['unresolved']}")


def test_3_unresolved_to_queue():
    """Fast Path cozemedigi bilgiyi queue'ya gondermeli."""
    print("\nTEST 3: Unresolved -> Queue")

    kernel = ASIKernel(auto_load=False)
    fp = FastPathValidator(kernel)

    # Aksiyomlarda karsiligi olmayan bilgi
    r = fp.evaluate("deprem", "isa", target="jeolojik_olay")
    test("'deprem isa jeolojik_olay' unresolved olmali",
         r["verdict"] == "unresolved")

    # Pipeline uzerinden test
    pipeline = StreamingIngestionPipeline(kernel)
    pr = pipeline.process_relation("volkan", "isa", target="dag_tipi")
    test("Pipeline unresolved'i queue'ya eklemeli",
         pr["path"] in ("queued", "batch"))
    test("Queue'da bekleyen oge olmali",
         pipeline.queue.pending() >= 1,
         f"pending={pipeline.queue.pending()}")


def test_4_contradiction_blocks_crystal():
    """Celiskili bilgi Crystal'a dogrudan yazilmamali."""
    print("\nTEST 4: Contradiction -> Crystal Engellenir")

    kernel = ASIKernel(auto_load=False)

    # Gokyuzu'nun rengi zaten 'mavi' olarak kayitli
    # 'yesil' bilgisi celismeli
    r = kernel.contradictions.gate(
        ne="gokyuzu", properties={"gorunur_renk": "yesil"}, source="test"
    )
    test("Celiskili bilgi reddedilmeli", not r["accepted"])
    test("Node izolasyonda olmali",
         any(n.ne == "gokyuzu" and n.isolated
             for n in kernel.contradictions.isolation_zone))

    # Crystal'daki orijinal deger degismemis olmali
    original_nodes = kernel.hooks.search_5n1k(ne="gokyuzu")
    original_colors = [n.properties.get("gorunur_renk") for n in original_nodes
                       if not n.isolated and "gorunur_renk" in n.properties]
    test("Crystal'daki orijinal renk 'mavi' olarak kalmali",
         "mavi" in original_colors,
         f"Bulunan renkler: {original_colors}")


def test_5_persistence():
    """Program kapatilip tekrar acildiginda bilgi korunmali."""
    print("\nTEST 5: Persistence — Bilgi Kaliciligi")

    # Gecici dosya kullan
    tmp_path = os.path.join(SCRIPT_DIR, "_test_knowledge_store.json")

    try:
        # 1. Kernel olustur ve bilgi ogret
        k1 = ASIKernel(auto_load=False)
        k1.contradictions.gate(
            ne="ankara", properties={"baskent": "turkiye"},
            source="test_persist", confidence=0.85
        )
        k1.contradictions.gate(
            ne="istanbul", properties={"nufus": "buyuk"},
            source="test_persist", confidence=0.9
        )
        initial_nodes = len(k1.hooks.nodes)

        # 2. Kaydet
        save_result = k1.save_knowledge(path=tmp_path)
        test("Kaydetme basarili olmali", save_result["saved"] > 0,
             f"saved={save_result.get('saved', 0)}")
        test("Dosya olusturulmali", os.path.exists(tmp_path))

        # 3. Yeni kernel ile yukle
        k2 = ASIKernel(knowledge_path=tmp_path, auto_load=True)
        test("Dugum sayisi korunmali",
             len(k2.hooks.nodes) == initial_nodes,
             f"Beklenen {initial_nodes}, alinan {len(k2.hooks.nodes)}")

        # 4. Ogrenilen bilgi mevcut mu?
        ankara_nodes = k2.hooks.search_5n1k(ne="ankara")
        test("'ankara' bilgisi yuklenmeli", len(ankara_nodes) > 0)
        if ankara_nodes:
            node = ankara_nodes[0]
            test("Confidence korunmali", node.confidence == 0.85,
                 f"confidence={node.confidence}")
            test("Source korunmali", "test_persist" in node.source,
                 f"source={node.source}")

    finally:
        # Temizlik
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_6_evidence_update():
    """Ayni bilginin farkli kaynaklardan tekrar gelmesi verification guncellemeli."""
    print("\nTEST 6: Evidence — Verification Metadata")

    kernel = ASIKernel(auto_load=False)

    # Ayni bilgi 3 farkli kaynaktan
    sources = ["wikipedia", "textbook", "encyclopedia"]
    for src in sources:
        kernel.contradictions.gate(
            ne="su", properties={"kimyasal_formul": "H2O"},
            source=src
        )

    # Dugum kontrolu
    nodes = [n for n in kernel.hooks.nodes.values()
             if AxiomEngine._normalize_tr(n.ne) == "su"
             and "kimyasal_formul" in n.properties
             and not n.isolated]
    test("Tek bir dugum olmali (3 degil)", len(nodes) == 1,
         f"Bulunan dugum sayisi: {len(nodes)}")

    if nodes:
        node = nodes[0]
        test("verification_count 3 olmali", node.verification_count == 3,
             f"verification_count={node.verification_count}")
        test("Evidence 3 kaynak icermeli", len(node.evidence) == 3,
             f"evidence={node.evidence}")
        test("Confidence 1.0'a ulasmamali (diminishing)",
             node.confidence < 1.0,
             f"confidence={node.confidence}")
        test("Confidence baslangictan yuksek olmali",
             node.confidence > 0.5,
             f"confidence={node.confidence}")


def test_7_regression():
    """Mevcut calisan kernel davranislari bozulmamali."""
    print("\nTEST 7: Regression — Mevcut Davranislar")

    kernel = ASIKernel(auto_load=False)

    # 7a: Aksiyom yukleme
    status = kernel.get_status()
    test("20+ aksiyom yuklenmeli", status["total_axioms"] >= 20)
    test("7+ tohum dugum olusmalı", status["total_nodes"] >= 7)

    # 7b: Mavi duser mi?
    result = kernel.ask("Mavi duser mi?")
    test("'Mavi duser mi?' -> KATEGORI HATASI",
         "KATEGORİ HATASI" in result.get("verdict", ""))

    # 7c: Yagmurda mavi duser mi?
    result = kernel.ask("Yagmurda mavi duser mi?")
    test("Yagmur aksiyomu kullanilmali",
         "ax_yagmur_sudur" in result.get("axioms_used", []))

    # 7d: Islanan sey mavi olur mu?
    result = kernel.ask("Islanan sey mavi olur mu?")
    test("'Islanan sey' sorusu cevaplanmali", "verdict" in result)

    # 7e: Ses duser mi?
    result = kernel.ask("Ses duser mi?")
    test("'Ses duser mi?' -> KATEGORI HATASI",
         "KATEGORİ HATASI" in result.get("verdict", ""))

    # 7f: Turkce Parser
    parsed = TurkishParser.parse_statement("limon sarıdır")
    test("Parser 'limon saridır' cozebilmeli",
         parsed and parsed["ne"] == "limon" and parsed["properties"].get("renk") == "sarı",
         f"Parsed: {parsed}")

    # 7g: Celiski motoru
    result = kernel.learn("gokyuzu yesildir")
    rejected_count = sum(1 for d in result.get("details", []) if not d.get("accepted", True))
    test("Gokyuzu yesildir celiski olarak tespit edilmeli", rejected_count > 0)

    # 7h: isa zinciri
    chain = kernel.axioms.resolve_isa_chain("mavi")
    test("mavi -> renk -> algisal_ozellik zinciri calismali",
         "renk" in chain and "algisal_ozellik" in chain,
         f"chain={chain}")

    # 7i: Varlik tipleri
    test("'mavi' algisal olmali",
         kernel.axioms.get_entity_type("mavi") == EntityType.ALGISAL)
    test("'su' fiziksel olmali",
         kernel.axioms.get_entity_type("su") == EntityType.FIZIKSEL)

    # 7j: Normalize
    test("Turkce normalize calismali",
         AxiomEngine._normalize_tr("Gokyuzu") == "gokyuzu")


def main():
    global PASS, FAIL

    print("=" * 60)
    print("  ASI-1 MIMARI REVIZYON — TEST SENARYOLARI")
    print("=" * 60)

    test_1_duplicate()
    test_2_fast_path_no_llm()
    test_3_unresolved_to_queue()
    test_4_contradiction_blocks_crystal()
    test_5_persistence()
    test_6_evidence_update()
    test_7_regression()

    print("\n" + "=" * 60)
    total = PASS + FAIL
    if FAIL == 0:
        print(f"  TUM TESTLER BASARILI: {PASS}/{total}")
    else:
        print(f"  SONUC: {PASS}/{total} gecti, {FAIL} basarisiz")
    print("=" * 60)

    return FAIL == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
