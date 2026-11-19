def build(d, G, g):
    # lokal: +X yuzu merkezi, govde x -thickness..0
    t = d["thickness"]
    body = g.cyl(d["od"] / 2, t, "x", center=False)
    body = g.move(body, -t)
    bore = g.move(g.cyl(d["bore_d"] / 2, t + 2, "x", center=False), -t - 1)
    s = g.cut(body, bore)
    # Klavuz: bore ustune halka olukla goruntusel ic dis (carpisma uretmez: oluk bore'dan DISA acilir)
    p, rmaj, rmin = d["thread_pitch"], d["thread_major"] / 2, d["thread_minor"] / 2
    depth = rmaj - rmin
    cuts, x = [], -t + p
    while x + p / 2 <= -p:
        cuts.append(g.move(g.tube(d["bore_d"] / 2 + depth, d["bore_d"] / 2 - 0.5, p / 2, "x", center=False), x))
        x += p
    return g.cut(s, *cuts) if cuts else s
