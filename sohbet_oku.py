#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sohbet kaydını oku — tüm soru/cevap/düşünme adımları.
Kullanım: python sohbet_oku.py [son_N]"""
import sys, os, json

YOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sohbet_kaydi.jsonl")

def oku(son_n=None):
    if not os.path.exists(YOL):
        print("Kayıt yok — henüz konuşma yapılmadı.")
        return
    kayitlar = []
    with open(YOL, 'r', encoding='utf-8') as f:
        for satir in f:
            try:
                kayitlar.append(json.loads(satir))
            except Exception:
                continue
    if son_n:
        kayitlar = kayitlar[-son_n:]
    print(f"═══ SOHBET KAYDI ({len(kayitlar)} kayıt) ═══\n")
    for i, k in enumerate(kayitlar, 1):
        print(f"[{i}] {k.get('zaman', '')[:19]}")
        print(f"    👤 SORU:   {k.get('soru', '')}")
        print(f"    🤖 CEVAP:  {k.get('cevap', '')}")
        print(f"    📡 KANAL:  {k.get('kanal', '?')}")
        adimlar = k.get('adimlar') or []
        if adimlar:
            ozet = " → ".join(f"{a.get('tur','?')}" for a in adimlar)
            print(f"    🧠 DÜŞÜNME: {ozet}")
        print()

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    oku(n)
