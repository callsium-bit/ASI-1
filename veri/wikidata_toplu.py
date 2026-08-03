# -*- coding: utf-8 -*-
"""Wikidata toplu çekim: 5 ilişki türü → gate → kristal
Rate limit 1 req/min — her sorgu 3000 ilişki döndürür, 61sn bekler.
part_of(P361) located_in(P131) causes(P1542) subclass_of(P279) instance_of(P31)
"""
import sys, os, json, time, urllib.request, urllib.parse
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype\veri')
from iliski_filtresi import hedef_kaliteli
from kernel_v2 import ASIKernel

ENDPOINT = 'https://query.wikidata.org/sparql'
k = ASIKernel()

SORGULAR = [
    ("part_of", "P361"),
    ("located_in", "P131"),
    ("causes", "P1542"),
    ("subclass_of", "P279"),
    ("instance_of", "P31"),
]

def cek(pid: str, limit: int = 3000):
    sparql = f'''
SELECT ?xLabel ?yLabel WHERE {{
  ?x wdt:{pid} ?y .
  ?x rdfs:label ?xLabel . ?y rdfs:label ?yLabel .
  FILTER(LANG(?xLabel) = "tr" && LANG(?yLabel) = "tr")
}} LIMIT {limit}
'''
    url = ENDPOINT + '?format=json&query=' + urllib.parse.quote(sparql)
    req = urllib.request.Request(url, headers={'User-Agent': 'ASI-1/0.1 (egitim)', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        d = json.loads(resp.read())
    return [(b['xLabel']['value'], b['yLabel']['value']) for b in d['results']['bindings']]

kabul = 0
ret = 0
filtre = 0
toplam = 0
for rel, pid in SORGULAR:
    try:
        iliskiler = cek(pid)
    except Exception as e:
        print(f"{rel}({pid}): HATA {str(e)[:60]}", flush=True)
        time.sleep(61)
        continue
    print(f"{rel}({pid}): {len(iliskiler)} ilişki çekildi", flush=True)
    toplam += len(iliskiler)
    for x, y in iliskiler:
        if not hedef_kaliteli(x, rel, y):
            filtre += 1
            continue
        r = k.relations.add_relation(x, rel, y,
                                     source=f"wikidata|{rel}", confidence=0.9)
        if r["accepted"]:
            kabul += 1
        else:
            ret += 1
    k.save_knowledge()  # her tür sonrası atomik kayıt
    time.sleep(61)  # rate limit

print(f"\nTAMAM: {toplam} çekildi | +{kabul} kabul, {ret} ret, {filtre} filtre")
print(f"Toplam düğüm: {len(k.hooks.nodes)}")
