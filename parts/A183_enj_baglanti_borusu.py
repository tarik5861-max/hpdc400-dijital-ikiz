# A183 Enjeksiyon unitesi sert baglanti borulari (A54 B -> A65 B, A55 PA -> A65 PA); ikiz_tasarim varsayimi.
# Lokal orijin: x/y global, z vurus ekseni (pos = [0, 0, z_sel]); A54/A55/A65 ile vurus konumunda birlikte kayar.
# Instance anahtari "hat" -> d["hatlar"][hat]: od, id, pts (ortogonal polyline, lokal), flanslar [bas, son]:
#   {"t": kalinlik (hat icine dogru), "boy": [a, b] = eksene dik iki eksen (xyz sirasiyla, eksen haric)}.
# Dirsek = iki dik silindirin kosede od/2 uzatilmasi (A160 ile ayni temsil); ic kanal id/2.
AXES = "xyz"


def _axis(a, b):
    diff = [b[i] - a[i] for i in range(3)]
    k = max(range(3), key=lambda i: abs(diff[i]))
    return k, (1 if diff[k] > 0 else -1)


def build(d, G, g):
    h = d["hatlar"][d["hat"]]
    pts = h["pts"]
    ro, ri, ap = h["od"] / 2.0, h["id"] / 2.0, d["acik_pay"]
    n = len(pts) - 1
    out, bore = [], []
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        k, s = _axis(a, b)
        lo, hi = sorted((a[k], b[k]))
        blo, bhi = lo, hi
        if i > 0:
            if s > 0: lo -= ro; blo -= ri
            else: hi += ro; bhi += ri
        if i < n - 1:
            if s > 0: hi += ro; bhi += ri
            else: lo -= ro; blo -= ri
        if i == 0:
            if s > 0: blo -= ap
            else: bhi += ap
        if i == n - 1:
            if s > 0: bhi += ap
            else: blo -= ap
        c = list(a); c[k] = lo
        out.append(g.move(g.cyl(ro, hi - lo, AXES[k], center=False), *c))
        c = list(a); c[k] = blo
        bore.append(g.move(g.cyl(ri, bhi - blo, AXES[k], center=False), *c))
    for (p, q), f in zip(((pts[0], pts[1]), (pts[-1], pts[-2])), h["flanslar"]):
        k, s = _axis(p, q)
        t = f["t"]
        size = [0.0, 0.0, 0.0]
        size[k] = t
        oth = [j for j in range(3) if j != k]
        size[oth[0]], size[oth[1]] = f["boy"]
        c = list(p); c[k] = p[k] + s * t / 2.0
        out.append(g.move(g.box(*size), *c))
        cb = list(p); cb[k] = p[k] - s * ap
        bore.append(g.move(g.cyl(ri, t + 2 * ap, AXES[k], center=False), *[cb[j] if j != k else min(p[k] - s * ap, p[k] + s * (t + ap)) for j in range(3)]))
    return g.cut(g.fuse(*out), g.fuse(*bore))
