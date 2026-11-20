"""hat_senkron.py - params/hatlar.json -> params/params.json A160.dims.hatlar + A160 instance'lari (TEK YONLU).

Kaynak: params/hatlar.json (hat tanimi, global koordinat). Hedef: params.json parts.A160 (hat verisi LOKAL).
Her hat bir instance (A160_<n>, override hat=<ID>). bbox cizilen geometriden hesaplanir (BBOX_SAPMA olmasin).
T-tee dugumlerinde dal hat, ana hattin dis yuzeyinde baslar (ana boruya girmez).
Hortum yay payi U-halkasi: --u-ara ile (cakisma taramali) secilir, yoksa mevcut secim korunur.
Kullanim: python3 tools/hat_senkron.py [--u-ara]
"""
import json, os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "assembly"), os.path.join(ROOT, "lib")]
import geo  # noqa
import assemble as asm  # noqa

PARAMS = os.path.join(ROOT, "params", "params.json")
HATLAR = os.path.join(ROOT, "params", "hatlar.json")
AX = "xyz"
ORTAK = {"acik_pay": 1.0, "halka_oran": 0.8, "flans_oran": 1.6, "flans_thk": 14.0, "ferrul_oran": 1.1, "ferrul_boy": 70.0}


def axis(a, b):
    diff = [b[i] - a[i] for i in range(3)]
    k = max(range(3), key=lambda i: abs(diff[i]))
    return k, (1 if diff[k] > 0 else -1)


def pts_of(h):
    g = h["guzergah"]
    pts = [list(g["baslangic"])] + [list(p) for p in g["ara_noktalar"]] + [list(g["bitis"])]
    out = [pts[0]]
    for p in pts[1:]:
        if p != out[-1]:
            out.append(p)
    return out


def host_trim(hid, pts, hats, nodes, end):
    """Hat ucu bir T-tee dugumundeyse ve ana hattin duz (ic) segmentindeyse, ucu ana boru dis yuzeyine ceker."""
    p = pts[0] if end == 0 else pts[-1]
    q = pts[1] if end == 0 else pts[-2]
    if not any(n["nokta"] == p for n in nodes):
        return pts
    kb, sb = axis(p, q)
    for oid, ob in hats.items():
        if oid == hid or ob["tip"] != "sert_boru":
            continue
        op = ob["pts"]
        for i in range(len(op) - 1):
            a, b = op[i], op[i + 1]
            k, _ = axis(a, b)
            if k == kb:
                continue
            others = [j for j in range(3) if j != k]
            if any(a[j] != p[j] for j in others):
                continue
            lo, hi = sorted((a[k], b[k]))
            if lo < p[k] < hi:   # kesin ic nokta
                np_ = list(p)
                np_[kb] += sb * ob["od"] / 2.0
                res = [list(x) for x in pts]
                res[0 if end == 0 else -1] = np_
                return res
    return pts


def build_hats(H, P, old=None):
    hats = {}
    for h in H["hatlar"]:
        sert = h["tip"] == "sert_boru"
        hats[h["id"]] = {
            "tip": h["tip"], "od": float(h["dis_cap_mm"]),
            "id": float(h["ic_cap_mm"] if sert else h["hortum"]["ic_cap_mm"]),
            "pts": pts_of(h), "kaynak": h["kaynak"]["id"], "hedef": h["hedef"]["id"],
            "yay_payi_mm": h.get("yay_payi_mm", 0),
            "hortum_uzunluk_mm": h.get("hortum_uzunluk_mm"),
            "rb_mm": h["min_bukum_yaricap_mm"] if sert else h["hortum"]["min_bukulme_yaricap_mm"],
        }
    # tee trim (sirayla; ana hatlar sert_boru ve kendileri degismez)
    nodes = H["dugumler"]
    for hid, h in hats.items():
        h["pts"] = host_trim(hid, h["pts"], hats, nodes, 0)
        h["pts"] = host_trim(hid, h["pts"], hats, nodes, 1)
    # blok yuzune bitisik stub: kirp (mm, --kirp ile cizilen geometriden bulunur, params'ta saklanir) uclari hat icine ceker
    for hid, h in hats.items():
        kp = (old or {}).get(hid, {}).get("kirp")
        if kp:
            h["kirp"] = kp
            for end, t in ((0, kp[0]), (-1, kp[1])):
                if t:
                    p, q = (h["pts"][0], h["pts"][1]) if end == 0 else (h["pts"][-1], h["pts"][-2])
                    k, sg = axis(p, q)
                    p[k] += sg * t
    # ortak uc: iki hattin ucu ayni noktadaysa sonraki hat o ucta halka (flans/ferrul) cizmez
    seen = set()
    for hid, h in hats.items():
        h["halka"] = [True, True]
        for j, end in enumerate((0, -1)):
            key = tuple(round(x) for x in h["pts"][end])
            if key in seen:
                h["halka"][j] = False
            seen.add(key)
    follow = set(P["global"]["shot_follow"]["instances_pos_z_eq_shot"])
    for hid, h in hats.items():
        n = len(h["pts"])
        if h["kaynak"] in follow:
            h["takip"] = {"idx": [0, 1]}
        elif h["hedef"] in follow:
            h["takip"] = {"idx": [n - 2, n - 1]}
    return hats


def to_local(hats, old):
    out, pos = {}, {}
    for hid, h in hats.items():
        o = h["pts"][0]
        e = {"tip": h["tip"], "od": h["od"], "id": h["id"],
             "pts": [[round(p[i] - o[i], 3) for i in range(3)] for p in h["pts"]],
             "yay_payi_mm": h["yay_payi_mm"], "rb_mm": h["rb_mm"], "ucler": [h["kaynak"], h["hedef"]]}
        if h["tip"] == "hortum" and h.get("hortum_uzunluk_mm"):
            e["hortum_uzunluk_mm"] = h["hortum_uzunluk_mm"]   # sabit hortum boyu: lib/hortum_pose.py konuma bagli yol icin
        if "takip" in h:
            e["takip"] = h["takip"]
        if not all(h["halka"]):
            e["halka"] = h["halka"]
        if h.get("kirp"):
            e["kirp"] = h["kirp"]
        if old and old.get(hid, {}).get("u_halka"):
            e["u_halka"] = old[hid]["u_halka"]
        out[hid] = e
        pos[hid] = [float(x) for x in o]
    return out, pos


def replace_block(raw, key, obj):
    """parts altindaki ust duzey '"<key>": {...}' blogunu metin duzeyinde degistirir/ekler (biçim bozulmaz)."""
    txt = json.dumps(obj, ensure_ascii=False)
    m = re.search(r'\n ?"parts": \{', raw)
    start = m.end()
    pat = re.compile(r'\n  ?"%s": ' % key)
    mm = pat.search(raw, start)
    if mm:
        _, end = json.JSONDecoder().raw_decode(raw, mm.end())
        return raw[:mm.end()] + txt + raw[end:]
    # ekle: parts blogunun sonuna
    _, pend = json.JSONDecoder().raw_decode(raw, m.end() - 1)
    k = raw.rfind("}", 0, pend)
    k2 = raw.rfind("\n", 0, k)
    prefix = raw[:k2].rstrip()
    return prefix + ',\n  "%s": %s' % (key, txt) + raw[k2:]


def kirp_hesapla(hats, placed):
    """Her hat ucu icin: uc noktasina degen blok (A160 disi) ile ortusen kisim kadar ucu hat icine cek (stub blok yuzunde biter)."""
    res = {}
    boxes = {n: geo.bbox(v[2]) for n, v in placed.items() if v[0] != "A160"}
    for hid, h in hats.items():
        r = h["od"] / 2.0
        kp = [0.0, 0.0]
        for j, (p, q) in enumerate(((h["pts"][0], h["pts"][1]), (h["pts"][-1], h["pts"][-2]))):
            k, sg = axis(p, q)
            L = abs(q[k] - p[k])
            lo = min(p[k], q[k]) if sg > 0 else min(p[k], q[k])
            c = list(p); c[k] = min(p[k], q[k])
            cy = geo.move(geo.cyl(r, L, AX[k], center=False), *c)
            bb = geo.bbox(cy)
            worst = 0.0
            for n, b in boxes.items():
                if not all(bb[i] <= b[i + 3] and b[i] <= bb[i + 3] for i in range(3)):
                    continue
                cm = geo.common(cy, placed[n][2])
                if geo.volume(cm) < 50.0:
                    continue
                cb = geo.bbox(cm)
                # ortusme diger ucu (q) iceriyorsa gercek cakisma: atla; degilse hat ucunu blogun hatta bakan yuzune cek
                if cb[k] - 1.5 <= q[k] <= cb[k + 3] + 1.5:
                    continue
                dist = lambda x: max(cb[k] - x, x - cb[k + 3], 0.0)
                if dist(p[k]) > dist(q[k]):
                    continue   # blok diger uca daha yakin: o uc kirpilir
                t = (cb[k + 3] - p[k]) if sg > 0 else (p[k] - cb[k])
                worst = max(worst, t)
            kp[j] = round(worst, 1) if worst > 0 else 0.0
        if any(kp):
            res[hid] = kp
            print("kirp", hid, kp)
    return res


def u_ara(hats, placed):
    """Yay payi olan hortumlara, cakismasiz ilk uygun U-halka (seg, eksen, isaret, derinlik, genislik) secer."""
    res = {}
    obst = [(geo.bbox(v[2]), v[2]) for n, v in placed.items()]
    for hid, h in hats.items():
        if h["tip"] != "hortum" or not h["yay_payi_mm"]:
            continue
        ro, rb, pts = h["od"] / 2.0, h["rb_mm"], h["pts"]
        segs = sorted(range(len(pts) - 1), key=lambda i: -abs(sum(pts[i + 1][j] - pts[i][j] for j in range(3))))
        D0 = h["yay_payi_mm"] / 2.0   # tam fazla boy (hortum_pose U derinligi = fazla/2); eskiden min(yay/2, 1.2*Rb)
        found = None
        for dm in (1.0, 0.75, 0.5, 0.3):
            for wm in (2.0, 1.4, 1.0):
                W, D = wm * rb, D0 * dm
                for i in segs:
                    a, b = pts[i], pts[i + 1]
                    k, sg = axis(a, b)
                    if abs(b[k] - a[k]) < W + 4 * ro + 20:
                        continue
                    for e in range(3):
                        if e == k:
                            continue
                        for isg in (1, -1):
                            mid = (a[k] + b[k]) / 2.0
                            c1, c2 = list(a), list(a)
                            c1[k], c2[k] = mid - W / 2, mid + W / 2
                            shapes = []
                            for (x0, x1, base) in ((0, D, c1), (0, D, c2)):
                                c = list(base)
                                if isg < 0:
                                    c[e] -= D
                                shapes.append(geo.move(geo.cyl(ro + 6, D, AX[e], center=False), *c))
                            cb = list(a); cb[k] = mid - W / 2 - ro; cb[e] += isg * D
                            if isg < 0:
                                pass
                            shapes.append(geo.move(geo.cyl(ro + 6, W + 2 * ro, AX[k], center=False), *cb))
                            loop = geo.fuse(*shapes)
                            lb = geo.bbox(loop)
                            ok = True
                            for ob, sh in obst:
                                if all(lb[q] <= ob[q + 3] and ob[q] <= lb[q + 3] for q in range(3)):
                                    if geo.volume(geo.common(loop, sh)) > 50.0:
                                        ok = False
                                        break
                            if ok:
                                found = {"seg": i, "eksen": AX[e], "isaret": isg, "derinlik": round(D, 1), "genislik": round(W, 1)}
                                break
                        if found: break
                    if found: break
                if found: break
            if found: break
        print("u_halka", hid, found)
        if found:
            res[hid] = found
    return res


def main():
    H = json.load(open(HATLAR, encoding="utf-8"))
    raw = open(PARAMS, encoding="utf-8").read()
    P = json.loads(raw)
    old = P["parts"].get("A160", {}).get("dims", {}).get("hatlar")
    if "--kirp" in sys.argv:
        placed, _, _, _ = asm.assemble()
        k0 = kirp_hesapla(build_hats(H, P, None), placed)
        old = {hid: dict((old or {}).get(hid, {}), kirp=k0.get(hid)) for hid in [h["id"] for h in H["hatlar"]]}
    hats = build_hats(H, P, old)
    if "--u-ara" in sys.argv:
        placed, _, _, _ = asm.assemble()
        # A160 haric tum parcalar + diger hatlar (kendisi dahil, halka hat uzerinde basladigi icin esik 50 mm3'te cakisma olusabilir)
        uh = u_ara(hats, {n: v for n, v in placed.items() if v[0] != "A160"})
        old = {hid: dict((old or {}).get(hid, {}), u_halka=uh.get(hid) or (old or {}).get(hid, {}).get('u_halka')) for hid in hats}   # bulunamazsa eski secim korunur
    loc, pos = to_local(hats, old)
    dims = dict(ORTAK)
    dims["hatlar"] = loc
    blk = {"name": "Hidrolik hatlar (sert boru + hortum, generic)", "dims": dims,
           "local_origin": "hattin ilk noktasi (baglanti agzi merkezi); eksenler global ile paralel; hat verisi params/hatlar.json'dan tools/hat_senkron.py ile uretilir (elle degistirme)",
           "note": "hortum = esnek, referans konumda (kalip yuksekligi 400, vurus alt, mafsal kapali) cizilir; A65 uclari vurus ile Z'de kayar (takip). ikiz_tasarim varsayimi.",
           "instances": []}
    for i, hid in enumerate(hats, 1):
        blk["instances"].append({"name": f"A160_{i}", "pos": pos[hid], "rot": [0, 0, 0], "hat": hid})
    P["parts"]["A160"] = blk
    # bbox'lari cizilen geometriden al
    for inst in blk["instances"]:
        d = dict(dims); d["hat"] = inst["hat"]
        G = dict(P["global"]); G["shot_offset_z"] = G["shot_positions_z"]["alt"]
        s = geo.place(asm.build_part("A160", "parts/A160_hat_boru.py", {"parts": {"A160": {"dims": dims}}, "global": G}, {"hat": inst["hat"]}), inst["pos"], [0, 0, 0])
        if "takip" not in loc[inst["hat"]]:
            inst["bbox"] = [round(x, 1) for x in geo.bbox(s)]
        print(inst["name"], inst["hat"], loc[inst["hat"]]["tip"], "bbox" in inst and inst["bbox"])
    open(PARAMS, "w", encoding="utf-8").write(replace_block(raw, "A160", blk))


if __name__ == "__main__":
    main()
