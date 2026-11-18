def build(d, G, g):
    # lokal orijin: kafa arka yuz merkezi; kafa x -t..0, govde -X
    h = d["head"]; L = d["length"]
    head = g.move(g.cyl(h["d"] / 2, h["thickness"], "x"), -h["thickness"] / 2, 0, 0)
    shank = g.move(g.cyl(d["d"] / 2, L, "x"), -L / 2, 0, 0)
    return g.fuse(head, shank)
