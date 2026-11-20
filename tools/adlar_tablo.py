#!/usr/bin/env python3
"""bom.json -> docs/PARCA_ADLARI.md (grup başlıklı ad tablosu). Eksik alanlı düğümleri uyarır."""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bom = json.load(open(os.path.join(R, "params/bom.json"), encoding="utf-8"))
out, warn, n = ["# Parça Adları", "", "Kaynak: params/bom.json (tools/adlar_tablo.py ile üretilir; elle düzenleme).", ""], [], 0
HDR = ["| ID | Türkçe ad | İngilizce ad | Adet | İşlev |", "|---|---|---|---|---|"]
def esc(s): return str(s).replace("|", "\\|")
def walk(nodes, rows):
    global n
    for x in nodes:
        if "script" in x:
            miss = [k for k in ("ad_tr", "ad_en", "islev") if not x.get(k)]
            if miss: warn.append(f"UYARI: {x.get('id')} eksik alan: {miss}")
            else: n += 1
            rows.append(f"| {x.get('id')} | {esc(x.get('ad_tr',''))} | {esc(x.get('ad_en',''))} | {x.get('qty','')} | {esc(x.get('islev',''))} |")
        if x.get("children"): walk(x["children"], rows)
for g in bom["tree"]:
    rows = []
    if "script" in g: walk([g], rows)
    else: walk(g.get("children", []), rows)
    out += [f"## {g.get('id')} {g.get('name')}", ""] + HDR + rows + [""]
open(os.path.join(R, "docs/PARCA_ADLARI.md"), "w", encoding="utf-8").write("\n".join(out))
print(f"{n} düğüm adlı -> docs/PARCA_ADLARI.md")
for w in warn: print(w)
