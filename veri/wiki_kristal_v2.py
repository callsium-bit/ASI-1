# -*- coding: utf-8 -*-
"""wiki_tr_v2.jsonl -> gate -> kristal dugum"""
import sys, os, json
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from kernel_v2 import ASIKernel

k = ASIKernel()
VERI = r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri\wiki_tr_v2.jsonl'

kabul = 0
ret = 0
tekrar = 0

with open(VERI, 'r', encoding='utf-8') as f:
    for line in f:
        rec = json.loads(line)
        konu = rec.get('konu', '')
        hedef = rec.get('hedef', '').strip()
        if not konu or not hedef or len(hedef) < 3:
            continue
        gate = k.contradictions.gate(
            ne=konu, properties={"isa": hedef},
            source="wikipedia_tr_v2|ilk_cumle",
            confidence=0.75
        )
        if gate["accepted"]:
            if gate.get("is_duplicate"):
                tekrar += 1
            else:
                kabul += 1
        else:
            ret += 1

print(f'Kabul: {kabul} | Ret: {ret} | Tekrar: {tekrar}')
status = k.get_status()
print(f'Toplam dugum: {status["total_nodes"]} | Izole: {status["isolated_nodes"]}')
k.save_knowledge()
print('💾 kaydedildi')
