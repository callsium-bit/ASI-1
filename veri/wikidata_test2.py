# -*- coding: utf-8 -*-
"""Wikidata SPARQL tekrar test — rate limit açıldı mı? İlişki çeşitliliği için"""
import sys, os, urllib.request, urllib.parse, json
sys.path.insert(0, r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
os.chdir(r'C:\Users\alipranac\Desktop\projelerim\asi-prototype')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ENDPOINT = 'https://query.wikidata.org/sparql'
sparql = '''
SELECT ?xLabel ?yLabel WHERE {
  ?x wdt:P361 ?y .
  ?x rdfs:label ?xLabel . ?y rdfs:label ?yLabel .
  FILTER(LANG(?xLabel) = "tr" && LANG(?yLabel) = "tr")
} LIMIT 5
'''
url = ENDPOINT + '?format=json&query=' + urllib.parse.quote(sparql)
req = urllib.request.Request(url, headers={'User-Agent': 'ASI-1/0.1', 'Accept': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        d = json.loads(resp.read())
    satirlar = d['results']['bindings']
    print(f'Wikidata part_of: {len(satirlar)} sonuc — AÇILDI!')
    for b in satirlar[:5]:
        print(f'  {b["xLabel"]["value"][:30]} --part_of--> {b["yLabel"]["value"][:35]}')
except Exception as e:
    print(f'Wikidata hala kapali: {str(e)[:80]}')
