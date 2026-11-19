# A121/A122 Sert hidrolik boru hatti (A64 deseni: eksene paralel dik borular, dirseklerde yaricap kadar uzatma).
# A121 = emis hatti (pompa A99 giris flansi -> tank A61), A122 = basinc hatti stub'lari (P1 A98 / P2 A100 cikisi).
# dims: od (dis cap, cizilen), id (ic cap, bilgi), path (lokal noktalar, ardisik iki nokta tek eksende farkli),
#       start_flange {size [a, b] dik eksenler, thk} (path[0]'dan ileri), end_flange {d, thk} (path[-1]'den geri).
# Lokal orijin = path[0] (baglanti agzi yuzu merkezi); eksenler global ile paralel. Instance anahtarlari olcuyu ezebilir.

AXES = "xyz"


def _axis(a, b):
    diff = [b[i] - a[i] for i in range(3)]
    k = max(range(3), key=lambda i: abs(diff[i]))
    return k, (1 if diff[k] > 0 else -1)


def build(d, G, g):
    pts = d["path"]
    r = d["od"] / 2
    n = len(pts) - 1
    segs = []
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        k, s = _axis(a, b)
        lo, hi = sorted((a[k], b[k]))
        # ic dirseklerde yaricap kadar uzat (A64 deseni)
        if (s > 0 and i > 0) or (s < 0 and i < n - 1):
            lo -= r
        if (s > 0 and i < n - 1) or (s < 0 and i > 0):
            hi += r
        c = list(a)
        c[k] = lo
        segs.append(g.move(g.cyl(r, hi - lo, AXES[k], center=False), *c))
    sf = d.get("start_flange")
    if sf:
        k, s = _axis(pts[0], pts[1])
        perp = [i for i in range(3) if i != k]
        dims = [0, 0, 0]
        dims[k] = sf["thk"]
        dims[perp[0]], dims[perp[1]] = sf["size"]
        c = list(pts[0])
        c[k] += s * sf["thk"] / 2
        segs.append(g.move(g.box(*dims), *c))
    ef = d.get("end_flange")
    if ef:
        k, s = _axis(pts[-2], pts[-1])
        c = list(pts[-1])
        c[k] -= s * ef["thk"] if s > 0 else 0
        segs.append(g.move(g.cyl(ef["d"] / 2, ef["thk"], AXES[k], center=False), *c))
    return g.fuse(*segs)
