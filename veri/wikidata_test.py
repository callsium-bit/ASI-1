# -*- coding: utf-8 -*-
"""Wikidata SPARQL: Türkçe etiketli kavramlar için ilişki çeşitliliği (part_of, located_in)
Test: 30 kavram için ilişki çek, kaliteyi gör."""
import sys, os, json, urllib.request, urllib.parse
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ENDPOINT = "https://query.wikidata.org/sparql"
UA = {"User-Agent": "ASI-1/0.1 (educational research bot)", "Accept": "application/json"}

def sorgula(sparql, timeout=20):
    url = ENDPOINT + "?format=json&query=" + urllib.parse.quote(sparql)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())

# 1. part_of örnekleri (Türkçe etiketli): "X, Y'nin parçasıdır"
sparql_part_of = """
SELECT ?xLabel ?yLabel WHERE {
  ?x wdt:P361 ?y .
  ?x rdfs:label ?xLabel . ?y rdfs:label ?yLabel .
  FILTER(LANG(?xLabel) = "tr" && LANG(?yLabel) = "tr")
  FILTER(?x != ?y)
} LIMIT 15
"""
# 2. located_in örnekleri
sparql_located = """
SELECT ?xLabel ?yLabel WHERE {
  ?x wdt:P131 ?y .
  ?x rdfs:label ?xLabel . ?y rdfs:label ?yLabel .
  FILTER(LANG(?xLabel) = "tr" && LANG(?yLabel) = "tr")
} LIMIT 15
"""
# 3. causes örnekleri
sparql_causes = """
SELECT ?xLabel ?yLabel WHERE {
  ?x wdt:P1542 ?y .
  ?x rdfs:label ?xLabel . ?y rdfs:label ?yLabel .
  FILTER(LANG(?xLabel) = "tr" && LANG(?yLabel) = "tr")
} LIMIT 15
"""

print("=== WIKIDATA SPARQL TESTİ ===")
for isim, sorgu in [("part_of", sparql_part_of), ("located_in", sparql_located), ("causes", sparql_causes)]:
    try:
        sonuc = sorgula(sorgu)
        satirlar = sonuc.get("results", {}).get("bindings", [])
        print(f"\n[{isim}] {len(satirlar)} sonuç:")
        for b in satirlar[:5]:
            x = b.get("xLabel", {}).get("value", "?")
            y = b.get("yLabel", {}).get("value", "?")
            print(f"  {x[:35]} --{isim}--> {y[:40]}")
    except Exception as e:
        print(f"\n[{isim}] HATA: {e}")
