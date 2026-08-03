# -*- coding: utf-8 -*-
"""Bugfix testi: durum() cakismasi + un/ut substring + atomik yazma"""
import sys, os
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from kernel_v2 import ASIKernel, ChatEngine, TaskMemory

k = ASIKernel()
chat = ChatEngine(k)
ok = 0

# 1. durum() artık akil genişletmeli
d = chat.durum()
assert "cikarim" in d, f"cikarim yok: {list(d.keys())}"
assert "log" in d, "log yok"
assert "baglam_turn" in d
print("[1] durum() akil genisletmeli:", {x: d[x] for x in ("cikarim", "log", "baglam_turn")})
ok += 1

# 2. "mutluyum ve sunum" görev silme tetiklememeli
tm = TaskMemory()
tm.ekle("süt al")
r = tm.algila("Bugün çok mutluyum ve sunum yaptım")
assert r is None, f"sahte pozitif: {r}"
print("[2] 'mutluyum ve sunum' gorev silmiyor")
ok += 1

# 3. Gerçek unut hala çalışıyor
r = tm.algila("süt görevini unut")
assert r and r["tur"] == "kapat", r
print("[3] 'süt görevini unut' kapatiyor:", r["metin"])
ok += 1

# 4. Atomik yazma çalışıyor
sonuc = k.save_knowledge()
assert sonuc["saved"] > 100000, sonuc
assert not os.path.exists("knowledge_store.json.tmp"), "tmp kaldi!"
print("[4] Atomik kayit: {} dugum, tmp temiz".format(sonuc["saved"]))
ok += 1

print("\nALL {} OK".format(ok))
