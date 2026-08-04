#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  ASI Prototip - PySide6 Kontrol Paneli                          ║
║  Canlı izleme, başlat/durdur, boşluk takibi, damıtma            ║
╚══════════════════════════════════════════════════════════════════╝
"""
import sys
import os
import json
import threading
import queue
import time
from datetime import datetime
from typing import Optional

# Proje dizinini path'e ekle (kernel_v2.py aynı klasörde)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QListWidget, QListWidgetItem,
    QLineEdit, QGroupBox, QGridLayout, QSplitter, QFrame,
    QTabWidget, QProgressBar, QMessageBox, QStatusBar,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QSpinBox
)
from PySide6.QtCore import (
    Qt, QTimer, Signal, QThread, Slot, QSize
)
from PySide6.QtGui import (
    QFont, QColor, QPalette, QIcon, QTextCursor
)

from kernel_v2 import ASIKernel


# ═══════════════════════════════════════════════════════
# ÇALIŞAN İŞ PARÇACIĞI (Thread)
# ═══════════════════════════════════════════════════════

class KernelWorker(QThread):
    """Ağır işleri arka planda çalıştırır"""
    log_signal = Signal(str, str)        # (message, level: info/warn/error/success)
    status_signal = Signal(dict)         # kernel durumu
    progress_signal = Signal(int, int)   # (current, total)

    def __init__(self):
        super().__init__()
        self.kernel: Optional[ASIKernel] = None
        self.running = False
        self._command_queue = queue.Queue()

    def run(self):
        """Ana thread döngüsü"""
        self.running = True
        self.log_signal.emit("Kernel iş parçacığı başladı", "info")

        while self.running:
            try:
                cmd, args = self._command_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                if cmd == "init":
                    self._handle_init(*args)
                elif cmd == "ask":
                    self._handle_ask(*args)
                elif cmd == "learn":
                    self._handle_learn(*args)
                elif cmd == "distill":
                    self._handle_distill(*args)
                elif cmd == "auto_explore":
                    self._handle_auto_explore(*args)
                elif cmd == "gaps":
                    self._handle_gaps(*args)
                elif cmd == "status":
                    self._handle_status()
                elif cmd == "shutdown":
                    break
            except Exception as e:
                self.log_signal.emit(f"HATA: {e}", "error")

        self.log_signal.emit("Kernel iş parçacığı durdu", "info")

    def command(self, cmd: str, *args):
        """Ana thread'den komut gönder"""
        self._command_queue.put((cmd, args))

    # -- Komut işleyiciler --

    def _handle_init(self):
        self.log_signal.emit("Kernel başlatılıyor...", "info")
        self.kernel = ASIKernel()
        self.log_signal.emit(f"✅ Kernel hazır: {self.kernel.get_status()['total_axioms']} aksiyom", "success")
        self._handle_status()

    def _handle_ask(self, question: str):
        if not self.kernel:
            return
        self.log_signal.emit(f"🧠 Soru: {question}", "info")
        result = self.kernel.ask(question)
        self.log_signal.emit(f"   {result.get('verdict', result.get('answer', '?'))[:120]}", 
                           "error" if "KATEGORİ HATASI" in str(result.get('verdict', '')) else "success")
        self._handle_status()

    def _handle_learn(self, fact: str):
        if not self.kernel:
            return
        self.log_signal.emit(f"📚 Öğren: {fact}", "info")
        result = self.kernel.learn(fact)
        decoded = result.get("_decoded", str(result))
        level = "success" if result.get("accepted", 0) > 0 else "warn"
        self.log_signal.emit(f"   {decoded}", level)
        self._handle_status()

    def _handle_distill(self, concept: str, endpoint: str, model: str):
        """LLM damıtma KALDIRILDI — sistem saf sembolik.
        Sembolik karşılık: kavramı türetim motorundan geçir."""
        if not self.kernel:
            return
        self.log_signal.emit(f"🧠 Türetim: {concept}", "info")
        try:
            result = self.kernel.relations.apply_hypotheses(concept, max_depth=2)
            self.log_signal.emit(
                f"   {result['hypotheses']} hipotez, {result['accepted']} kabul, {result['rejected']} ret",
                "success" if result["accepted"] > 0 else "warn")
        except Exception as e:
            self.log_signal.emit(f"   ❌ Türetim hatası: {e}", "error")
        self._handle_status()

    def _handle_auto_explore(self, max_concepts: int, endpoint: str, model: str):
        """LLM damıtma KALDIRILDI — sistem saf sembolik.
        Sembolik karşılık: bilgi boşluğu analizi (az ilişkili kavramlar)."""
        if not self.kernel:
            return
        self.log_signal.emit(f"🔍 Boşluk analizi ({max_concepts} kavram)", "info")
        try:
            gaps = self.kernel.tools.call("boşlukları listele")
            if isinstance(gaps, dict):
                g = gaps.get("gaps", [])
                self.log_signal.emit(f"   {len(g)} bilgi boşluğu tespit edildi", "success")
            else:
                self.log_signal.emit(f"   {gaps}", "info")
        except Exception as e:
            self.log_signal.emit(f"   ❌ Analiz hatası: {e}", "error")
        self._handle_status()

    def _handle_gaps(self):
        if not self.kernel:
            return
        gaps = self.kernel.tools.call("boşlukları listele")
        if isinstance(gaps, dict):
            liste = gaps.get("gaps", [])
        else:
            liste = []
        self.status_signal.emit({
            "type": "gaps_update",
            "gaps": liste,
            "total": len(liste)
        })

    def _handle_status(self):
        if not self.kernel:
            return
        s = self.kernel.get_status()
        self.status_signal.emit({
            "type": "status_update",
            **s
        })


# ═══════════════════════════════════════════════════════════════
# ANA PENCERE
# ═══════════════════════════════════════════════════════════════

class ASIPanel(QMainWindow):
    """ASI Prototip kontrol paneli"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASI Prototip - Kontrol Paneli")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Stil
        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QGroupBox {
                color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; margin-top: 12px; padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 10px; padding: 0 5px;
            }
            QLabel { color: #c9d1d9; }
            QPushButton {
                background-color: #21262d; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 6px;
                padding: 6px 16px; font-size: 13px;
            }
            QPushButton:hover { background-color: #30363d; }
            QPushButton:pressed { background-color: #484f58; }
            QPushButton#startBtn { background-color: #238636; color: white; }
            QPushButton#startBtn:hover { background-color: #2ea043; }
            QPushButton#stopBtn { background-color: #da3633; color: white; }
            QPushButton#stopBtn:hover { background-color: #f85149; }
            QPushButton#distillBtn { background-color: #1f6feb; color: white; }
            QPushButton#distillBtn:hover { background-color: #388bfd; }
            QPushButton#exploreBtn { background-color: #8957e5; color: white; }
            QPushButton#exploreBtn:hover { background-color: #a371f7; }

            QLineEdit, QSpinBox {
                background-color: #0d1117; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 4px;
                padding: 5px;
            }
            QTextEdit {
                background-color: #0d1117; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 4px;
                font-family: 'Consolas', 'Cascadia Code', monospace;
                font-size: 12px;
            }
            QListWidget {
                background-color: #0d1117; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 4px;
            }
            QTreeWidget {
                background-color: #0d1117; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 4px;
            }
            QTreeWidget::item { padding: 4px; }
            QHeaderView::section {
                background-color: #161b22; color: #c9d1d9;
                border: 1px solid #30363d; padding: 4px;
            }
            QProgressBar {
                border: 1px solid #30363d; border-radius: 4px;
                text-align: center; color: #c9d1d9;
            }
            QProgressBar::chunk { background-color: #1f6feb; border-radius: 3px; }
            QStatusBar { color: #8b949e; }
            QTabWidget::pane { border: 1px solid #30363d; }
            QTabBar::tab {
                background: #21262d; color: #8b949e;
                padding: 8px 16px; border: 1px solid #30363d;
            }
            QTabBar::tab:selected { background: #0d1117; color: #f0f6fc; }
        """)

        # İş parçacığı
        self.worker = KernelWorker()
        self.worker.log_signal.connect(self.on_log)
        self.worker.status_signal.connect(self.on_status)
        self.worker.progress_signal.connect(self.on_progress)
        self.worker.start()

        # UI
        self._build_ui()

        # Kernel'i başlat
        self.worker.command("init")

        # Otomatik yenileme timer'ı
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(5000)  # 5 saniyede bir gap kontrolü

        # Log
        self.log("ASI Prototip Kontrol Paneli başlatıldı", "info")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # == ÜST ÇUBUK: Durum & Kontrol ==
        top_bar = QHBoxLayout()

        # Durum göstergesi
        self.status_indicator = QLabel("⚫ Başlatılıyor...")
        self.status_indicator.setStyleSheet("font-size: 16px; font-weight: bold; padding: 4px;")
        top_bar.addWidget(self.status_indicator)
        top_bar.addStretch()

        # İstatistik etiketleri
        self.lbl_axioms = QLabel("Aksiyom: 0")
        self.lbl_nodes = QLabel("Düğüm: 0")
        self.lbl_hooks = QLabel("Kanca: 0")
        self.lbl_isolated = QLabel("İzole: 0")
        for lbl in [self.lbl_axioms, self.lbl_nodes, self.lbl_hooks, self.lbl_isolated]:
            lbl.setStyleSheet("font-size: 13px; padding: 4px 8px; background: #161b22; "
                             "border-radius: 4px; border: 1px solid #30363d;")
            top_bar.addWidget(lbl)

        main_layout.addLayout(top_bar)

        # == İLERLEME ÇUBUĞU ==
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(4)
        self.progress.setTextVisible(False)
        self.progress.hide()
        main_layout.addWidget(self.progress)

        # == ANA BÖLÜM: Splitter ==
        splitter = QSplitter(Qt.Horizontal)

        # -- SOL PANEL: Kontroller --
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 4, 0)
        left_layout.setSpacing(8)

        # Kontrol butonları
        ctrl_group = QGroupBox("⚙️ Sistem Kontrol")
        ctrl_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ Başlat")
        self.btn_start.setObjectName("startBtn")
        self.btn_stop = QPushButton("⏹ Durdur")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_reset = QPushButton("↺ Sıfırla")
        self.btn_start.clicked.connect(self._start_kernel)
        self.btn_stop.clicked.connect(self._stop_kernel)
        self.btn_reset.clicked.connect(self._reset_kernel)
        ctrl_layout.addWidget(self.btn_start)
        ctrl_layout.addWidget(self.btn_stop)
        ctrl_layout.addWidget(self.btn_reset)
        ctrl_group.setLayout(ctrl_layout)
        left_layout.addWidget(ctrl_group)

        # Soru-cevap grubu
        ask_group = QGroupBox("🧠 Sorgu")
        ask_layout = QVBoxLayout()
        ask_input_layout = QHBoxLayout()
        self.ask_input = QLineEdit()
        self.ask_input.setPlaceholderText("Soru sor: Mavi düşer mi?...")
        self.ask_input.returnPressed.connect(self._ask_question)
        self.btn_ask = QPushButton("Sor")
        self.btn_ask.clicked.connect(self._ask_question)
        ask_input_layout.addWidget(self.ask_input)
        ask_input_layout.addWidget(self.btn_ask)
        ask_layout.addLayout(ask_input_layout)

        # Hızlı soru butonları
        quick_layout = QHBoxLayout()
        quick_questions = [
            ("Mavi düşer mi?", "mavi"),
            ("Ses düşer mi?", "ses"),
            ("Gökyüzü neden mavi?", "gokyuzu"),
        ]
        for text, _ in quick_questions:
            btn = QPushButton(text)
            btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
            btn.clicked.connect(lambda checked, t=text: self._quick_ask(t))
            quick_layout.addWidget(btn)
        ask_layout.addLayout(quick_layout)
        ask_group.setLayout(ask_layout)
        left_layout.addWidget(ask_group)

        # Öğrenme grubu
        learn_group = QGroupBox("📚 Öğrenme")
        learn_layout = QHBoxLayout()
        self.learn_input = QLineEdit()
        self.learn_input.setPlaceholderText("limon sarıdır, kar beyazdır...")
        self.learn_input.returnPressed.connect(self._learn_fact)
        self.btn_learn = QPushButton("Öğren")
        self.btn_learn.clicked.connect(self._learn_fact)
        learn_layout.addWidget(self.learn_input)
        learn_layout.addWidget(self.btn_learn)
        learn_group.setLayout(learn_layout)
        left_layout.addWidget(learn_group)

        # Damıtma grubu
        distill_group = QGroupBox("🔬 LLM Damıtma")
        distill_layout = QVBoxLayout()
        distill_input_layout = QHBoxLayout()
        self.distill_input = QLineEdit()
        self.distill_input.setPlaceholderText("Kavram: yıldırım, şimşek, dolu...")
        self.distill_input.returnPressed.connect(self._distill_concept)
        self.btn_distill = QPushButton("Damıt")
        self.btn_distill.setObjectName("distillBtn")
        self.btn_distill.clicked.connect(self._distill_concept)
        distill_input_layout.addWidget(self.distill_input)
        distill_input_layout.addWidget(self.btn_distill)
        distill_layout.addLayout(distill_input_layout)

        # Endpoint ve model ayarları
        settings_layout = QHBoxLayout()
        self.endpoint_input = QLineEdit("http://localhost:PORT/v1/chat/completions")
        self.endpoint_input.setPlaceholderText("Yerel LLM endpoint")
        self.model_input = QLineEdit("local-model")
        self.model_input.setPlaceholderText("Model adı")
        self.model_input.setMaximumWidth(130)
        settings_layout.addWidget(QLabel("Endpoint:"))
        settings_layout.addWidget(self.endpoint_input)
        settings_layout.addWidget(QLabel("Model:"))
        settings_layout.addWidget(self.model_input)
        distill_layout.addLayout(settings_layout)

        # Otomatik keşif
        explore_layout = QHBoxLayout()
        self.explore_spin = QSpinBox()
        self.explore_spin.setRange(1, 20)
        self.explore_spin.setValue(5)
        self.btn_explore = QPushButton("🔍 Otomatik Keşif")
        self.btn_explore.setObjectName("exploreBtn")
        self.btn_explore.clicked.connect(self._auto_explore)
        explore_layout.addWidget(QLabel("Max kavram:"))
        explore_layout.addWidget(self.explore_spin)
        explore_layout.addWidget(self.btn_explore)
        distill_layout.addLayout(explore_layout)

        distill_group.setLayout(distill_layout)
        left_layout.addWidget(distill_group)

        # Boşluk listesi
        gaps_group = QGroupBox("📊 Boşluklar (Gaps)")
        gaps_layout = QVBoxLayout()
        self.gaps_list = QTreeWidget()
        self.gaps_list.setHeaderLabels(["Kavram", "Tür", "Öncelik"])
        self.gaps_list.setAlternatingRowColors(True)
        self.gaps_list.header().setStretchLastSection(True)
        gaps_layout.addWidget(self.gaps_list)
        self.btn_refresh_gaps = QPushButton("🔄 Boşlukları Tazele")
        self.btn_refresh_gaps.clicked.connect(lambda: self.worker.command("gaps"))
        gaps_layout.addWidget(self.btn_refresh_gaps)
        gaps_group.setLayout(gaps_layout)
        left_layout.addWidget(gaps_group)

        # -- SAĞ PANEL: Log ve Detay --
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(8)

        # Tab widget
        self.tabs = QTabWidget()

        # Log sekmesi
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(4, 4, 4, 4)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_view)
        clear_btn = QPushButton("Temizle")
        clear_btn.clicked.connect(self.log_view.clear)
        log_layout.addWidget(clear_btn)
        self.tabs.addTab(log_tab, "📝 Log")

        # Aksiyomlar sekmesi
        axioms_tab = QWidget()
        axioms_layout = QVBoxLayout(axioms_tab)
        self.axioms_view = QTextEdit()
        self.axioms_view.setReadOnly(True)
        self.axioms_view.setFont(QFont("Consolas", 10))
        axioms_layout.addWidget(self.axioms_view)
        self.tabs.addTab(axioms_tab, "📜 Aksiyomlar")

        # Kristal Düğümler sekmesi
        nodes_tab = QWidget()
        nodes_layout = QVBoxLayout(nodes_tab)
        self.nodes_view = QTreeWidget()
        self.nodes_view.setHeaderLabels(["ID", "Ne", "Özellikler", "Güven"])
        self.nodes_view.setAlternatingRowColors(True)
        nodes_layout.addWidget(self.nodes_view)
        self.tabs.addTab(nodes_tab, "💎 Düğümler")

        # İzole sekmesi
        isolated_tab = QWidget()
        isolated_layout = QVBoxLayout(isolated_tab)
        self.isolated_view = QTreeWidget()
        self.isolated_view.setHeaderLabels(["ID", "Kavram", "Özellikler", "Sebep"])
        self.isolated_view.setAlternatingRowColors(True)
        isolated_layout.addWidget(self.isolated_view)
        self.tabs.addTab(isolated_tab, "🔒 İzole")

        right_layout.addWidget(self.tabs)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # Durum çubuğu
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")

    # ── Log yönetimi ──────────────────────────────────────────

    def log(self, message: str, level: str = "info"):
        """Renkli log mesajı ekle"""
        colors = {
            "info": "#8b949e",
            "success": "#3fb950",
            "warn": "#d29922",
            "error": "#f85149",
        }
        color = colors.get(level, "#c9d1d9")
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = f'<span style="color:#484f58">[{timestamp}]</span> '
        html += f'<span style="color:{color}">{message}</span>'
        self.log_view.append(html)
        # Otomatik kaydır
        self.log_view.moveCursor(QTextCursor.MoveOperation.End)

    @Slot(str, str)
    def on_log(self, message: str, level: str):
        self.log(message, level)

    @Slot(dict)
    def on_status(self, data: dict):
        msg_type = data.get("type", "")

        if msg_type == "status_update":
            self.lbl_axioms.setText(f"Aksiyom: {data.get('total_axioms', 0)}")
            self.lbl_nodes.setText(f"Düğüm: {data.get('total_nodes', 0)}")
            self.lbl_hooks.setText(f"Kanca: {data.get('total_hooks', 0)}")
            self.lbl_isolated.setText(f"İzole: {data.get('isolated_nodes', 0)}")
            self.status_indicator.setText("🟢 Çalışıyor")
            self._update_detail_tabs(data)

        elif msg_type == "gaps_update":
            gaps = data.get("gaps", [])
            self.gaps_list.clear()
            for g in gaps:
                item = QTreeWidgetItem([
                    g["concept"], g["type"],
                    str(g.get("priority", "?"))
                ])
                self.gaps_list.addTopLevelItem(item)

    @Slot(int, int)
    def on_progress(self, current: int, total: int):
        if total > 0:
            self.progress.setMaximum(total)
            self.progress.setValue(current)
            self.progress.show()
        else:
            self.progress.hide()

    def _auto_refresh(self):
        """Periyodik durum güncellemesi"""
        self.worker.command("gaps")
        self.worker.command("status")

    # ── Buton aksiyonları ────────────────────────────────────

    def _start_kernel(self):
        self.worker.command("init")
        self.log("Kernel başlatılıyor...", "info")

    def _stop_kernel(self):
        self.log("⚠️ Kernel duraklatıldı (iş parçacığı devam ediyor)", "warn")
        self.status_indicator.setText("🔴 Duraklatıldı")
        self._refresh_timer.stop()

    def _reset_kernel(self):
        reply = QMessageBox.question(
            self, "Sıfırla", "Tüm bilgi tabanını sıfırlamak istediğine emin misin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.worker.command("init")
            self.log("🔄 Sistem sıfırlandı", "warn")
            self._refresh_timer.start()

    def _ask_question(self):
        question = self.ask_input.text().strip()
        if not question:
            return
        self.worker.command("ask", question)
        self.ask_input.clear()

    def _quick_ask(self, question: str):
        self.ask_input.setText(question)
        self._ask_question()

    def _learn_fact(self):
        fact = self.learn_input.text().strip()
        if not fact:
            return
        self.worker.command("learn", fact)
        self.learn_input.clear()

    def _distill_concept(self):
        concept = self.distill_input.text().strip()
        if not concept:
            return
        endpoint = self.endpoint_input.text().strip()
        model = self.model_input.text().strip()
        self.worker.command("distill", concept, endpoint, model)
        self.distill_input.clear()

    def _auto_explore(self):
        max_concepts = self.explore_spin.value()
        endpoint = self.endpoint_input.text().strip()
        model = self.model_input.text().strip()
        self.worker.command("auto_explore", max_concepts, endpoint, model)

    # ── Detay sekmeleri güncelleme ───────────────────────────

    def _update_detail_tabs(self, data: dict):
        """Aksiyom, düğüm ve izole sekmelerini güncelle"""
        # Aksiyomlar
        if "entity_types" in data:
            axioms_text = "📜 YÜKLÜ AKSİYOMLAR:\n\n"
            # Worker üzerinden kernel'e erişip aksiyomları al
            if self.worker.kernel:
                for ax in self.worker.kernel.axioms.axioms.values():
                    axioms_text += f"  [{ax.priority}] {ax.statement}\n"
            self.axioms_view.setPlainText(axioms_text)

        # Kristal Düğümler
        if self.worker.kernel:
            self.nodes_view.clear()
            for node in self.worker.kernel.hooks.nodes.values():
                if node.isolated:
                    continue
                props_str = ", ".join(f"{k}={v}" for k, v in node.properties.items())
                item = QTreeWidgetItem([
                    node.id, node.ne, props_str,
                    f"{node.confidence:.2f}"
                ])
                self.nodes_view.addTopLevelItem(item)

            # İzole düğümler
            self.isolated_view.clear()
            for node in self.worker.kernel.contradictions.isolation_zone:
                props_str = ", ".join(f"{k}={v}" for k, v in node.properties.items())
                item = QTreeWidgetItem([
                    node.id, node.ne, props_str,
                    node.source[:80]
                ])
                self.isolated_view.addTopLevelItem(item)


# ═══════════════════════════════════════════════════════════════
# ANA PROGRAM
# ═══════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ASI Prototip Panel")
    app.setStyle("Fusion")

    # Karanlık palet
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1f6feb"))
    app.setPalette(palette)

    panel = ASIPanel()
    # Geçici olarak en üstte göster (bulunabilmesi için)
    panel.setWindowFlags(panel.windowFlags() | Qt.WindowStaysOnTopHint)
    panel.show()
    panel.raise_()
    panel.activateWindow()
    # 3 saniye sonra normal seviyeye indir
    QTimer.singleShot(3000, lambda: panel.setWindowFlags(
        panel.windowFlags() & ~Qt.WindowStaysOnTopHint
    ) or panel.show())
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
