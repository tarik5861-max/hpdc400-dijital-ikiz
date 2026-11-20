# A160 Generic hidrolik hat (sert boru veya hortum), tek script, hat verisi params A160.dims.hatlar[hat].
# Instance anahtari "hat" (or. "H01") hangi hattin cizilecegini secer (assemble instance override -> d["hat"]).
# Hat verisi: tools/hat_senkron.py params/hatlar.json -> params.json A160.dims.hatlar (tek yonlu senkron).
# hatlar[hat]: tip ("sert_boru"|"hortum"), od, id (ic cap), pts (LOKAL ortogonal polyline, ilk nokta ~ orijin),
#   u_halka (opsiyonel, hortum yay payi: {seg, eksen, isaret, derinlik, genislik}),
#   takip (opsiyonel, vurus konumuyla Z'de kayan uc noktalar: {idx:[..]}; hortum esnek -> uc A65 ile gider).
# Dirsek = iki dik silindirin birbirine r kadar uzatilmasi (dis) + ic bos kanal (ri kadar); uclar acik.
# Sert boru uclari flans (d = od*flans_oran, kalinlik flans_thk); hortum uclari kivrim mansonu (ferrul).
# Lokal orijin = pts[0] (baglanti agzi merkezi, hat yonune dik yuzde); eksenler global ile paralel.

AXES = "xyz"


def _axis(a, b):
    diff = [b[i] - a[i] for i in range(3)]
    k = max(range(3), key=lambda i: abs(diff[i]))
    return k, (1 if diff[k] > 0 else -1)


def _u_halka(pts, u):
    """Segment u['seg'] ortasina U-halka (iki dik bacak + alt kenar) ekler."""
    i = u["seg"]
    a, b = pts[i], pts[i + 1]
    k, s = _axis(a, b)
    mid = (a[k] + b[k]) / 2.0
    w = u["genislik"] / 2.0
    e = AXES.index(u["eksen"])
    off = u["isaret"] * u["derinlik"]
    p1 = list(a); p1[k] = mid - s * w
    p2 = list(p1); p2[e] += off
    p4 = list(a); p4[k] = mid + s * w
    p3 = list(p4); p3[e] += off
    return pts[:i + 1] + [p1, p2, p3, p4] + pts[i + 1:]


def build(d, G, g):
    h = d["hatlar"][d["hat"]]
    pts = [list(p) for p in h["pts"]]
    tk = h.get("takip")
    if tk:
        dz = G["shot_offset_z"] - G["shot_positions_z"]["alt"]
        for i in tk["idx"]:
            pts[i][2] += dz
    if h.get("u_halka"):
        pts = _u_halka(pts, h["u_halka"])
    hose = h["tip"] == "hortum"
    ro = h["od"] / 2.0
    ri = h["id"] / 2.0
    n = len(pts) - 1
    out, bore = [], []
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        k, s = _axis(a, b)
        lo, hi = sorted((a[k], b[k]))
        blo, bhi = lo, hi
        # dirsek: gecis noktasi her iki yana r kadar uzatilir (dis), ri kadar (ic kanal)
        if i > 0:
            if s > 0: lo -= ro; blo -= ri
            else: hi += ro; bhi += ri
        if i < n - 1:
            if s > 0: hi += ro; bhi += ri
            else: lo -= ro; blo -= ri
        if i == 0:
            if s > 0: blo -= d["acik_pay"]
            else: bhi += d["acik_pay"]
        if i == n - 1:
            if s > 0: bhi += d["acik_pay"]
            else: blo -= d["acik_pay"]
        c = list(a); c[k] = lo
        out.append(g.move(g.cyl(ro, hi - lo, AXES[k], center=False), *c))
        c = list(a); c[k] = blo
        bore.append(g.move(g.cyl(ri, bhi - blo, AXES[k], center=False), *c))
    # uc bilezikleri: sert boru -> flans, hortum -> kivrim mansonu (her ikisi hat icine dogru)
    if hose:
        rr, th0 = ro * d["ferrul_oran"], d["ferrul_boy"]
    else:
        rr, th0 = ro * d["flans_oran"], d["flans_thk"]
    halka = h.get("halka", [True, True])
    for p, q, on in ((pts[0], pts[1], halka[0]), (pts[-1], pts[-2], halka[1])):
        if not on:
            continue
        k, s = _axis(p, q)          # p'den q'ya yon: hat icine
        th = min(th0, d["halka_oran"] * abs(q[k] - p[k]))   # kisa bacakta bilezik dirsegi asmasin
        base = p[k] if s > 0 else p[k] - th
        c = list(p); c[k] = base
        out.append(g.move(g.cyl(rr, th, AXES[k], center=False), *c))
    return g.cut(g.fuse(*out), g.fuse(*bore))
