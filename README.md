# ASI Prototip — Sembolik Sağduyu Motoru

**"Mavi düşmez. Renk algıdır, madde değil."**

Sıfır bağımlılıkla çalışan, aksiyom tabanlı, kendi kendine web'den öğrenebilen sembolik zeka prototipi. 4B'lik küçük bir LLM ile 175B'lik modellerden daha güvenilir bilgi tabanı oluşturur.

---

## 🧠 Mimari (6 Aşama)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ A1: Aksiyom  │───▶│ A2: 5N1K     │───▶│ A3: Çelişki  │
│    Motoru    │    │    Kanca     │    │  & Çağrışım  │
│  20 kural    │    │  27 kanca    │    │  İzole Alan  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ A4: Decoder  │◀───│ A5: LLM      │◀───│ A6: Web      │
│   Dil Motoru │    │   Distiller  │    │   Ingester   │
│  Template/LLM│    │  Qwen 4B→JSON│    │  Wikipedia   │
└─────────────┘    └─────────────┘    └─────────────┘
```

| Aşama | Ne yapar? | Bağımlılık |
|-------|-----------|------------|
| A1 | 20 değişmez dünya kuralı (yerçekimi, renk=algı, su=ıslatır) | Yok |
| A2 | 5N1K indeksli kanca motoru, kristal düğümler | Yok |
| A3 | Çelişki tespiti, izole alan, serbest çağrışım | Yok |
| A4 | İç mantığı doğal Türkçe'ye çevirme | Yok |
| A5 | Küçük LLM'den bilgi damıtma (öner → onayla) | LM Studio |
| A6 | Wikipedia → LLM → Aksiyom → Kristal Düğüm döngüsü | LM Studio |

---

## ⚡ Hızlı Başlangıç

```bash
# Tek komutla başlat
python run.py

# Testler (18 test, ~5 saniye)
python run.py test

# İnteraktif soru-cevap
python run.py ask
```

### Sorgu örnekleri (LLM'siz çalışır):

```
🧠 > Mavi düşer mi?
🤖 KATEGORİ HATASI — Renk algıdır, düşemez.

🧠 > Yağmurda mavi düşer mi?
🤖 Hayır. Yağmur sudur, mavi renktir. Yağan sudur, renk değil.

🧠 > Islanan şey mavi olur mu?
🤖 Olmaz. Su ıslatır, renklendirmez.

🧠 > Ses düşer mi?
🤖 KATEGORİ HATASI — Ses de algısaldır, düşemez.
```

---

## 🌐 Web'den Öğrenme (LM Studio gerekir)

```bash
# Tek kavram: Wikipedia → Qwen 4B → Aksiyom → Kristal
python run.py web deprem

# Kesintisiz döngü (gap kalmayana kadar)
python run.py web-loop 10

# Sınırsız döngü (gece boyu çalıştır)
python run.py web-loop 0
```

### Pipeline:
```
Wikipedia API → Ham metin → Qwen 4B (JSON çıkar) → Aksiyom kontrolü → Kristal/İzole
                    ↑                                                      ↓
                    └──── LLM yoksa regex fallback ────────────────────────┘
```

---

## 🖥️ GUI Kontrol Paneli

```bash
python run.py gui
```

PySide6 ile karanlık tema, canlı durum takibi, boşluk listesi, damıtma paneli.

---

## 📁 Dosya Yapısı

```
asi-prototype/
├── kernel.py          # v1: Aşama 1-2 (1114 satır)
├── kernel_v2.py       # v2: Tüm aşamalar (~2600 satır) ★ ANA MOTOR
├── gui.py             # PySide6 kontrol paneli
├── run.py             # Tek tıkla başlatıcı
└── README.md
```

---

## 🔧 Gereksinimler

| Bileşen | Zorunlu? | Not |
|---------|----------|-----|
| Python 3.11+ | ✅ Evet | |
| PySide6 | ❌ Sadece GUI | `pip install PySide6` |
| LM Studio | ❌ Sadece A5-A6 | Yerel LLM, localhost:1234 |
| İnternet | ❌ Sadece A6 | Wikipedia API |

**Çekirdek sistem (A1-A4) sıfır bağımlılıkla çalışır.**

---

## 🎯 Neden Farklı?

- **LLM'lerin aksine**: "Mavi düşer mi?" sorusuna ezberden değil, **akıl yürüterek** cevap verir
- **Açıklanabilir**: Hangi aksiyom zincirinden geçtiğini adım adım gösterir
- **Sıfır halüsinasyon**: Sembolik mantık, olasılıksal değil
- **Çelişki korumalı**: Yanlış bilgi ana hafızaya sızmaz, izole edilir
- **Küçük modelle büyük iş**: 4B'lik LLM, arkasındaki mantık motoruyla 175B'lik modellerden daha güvenilir

---

## 📜 Lisans

MIT
