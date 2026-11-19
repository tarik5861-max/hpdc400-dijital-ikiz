def build(d, G, g):
    # lokal: -X uc yuzu merkezi, eksen +X, 0..length
    # Disli bolgeler: halka olukla goruntusel dis (helis degil); olukta cap = thread_minor
    s = g.cyl(d["d"] / 2, d["length"], "x", center=False)
    p, rmaj, rmin = d["thread_pitch"], d["thread_major"] / 2, d["thread_minor"] / 2
    zones = [(0.0, d["front_thread_len"]),
             (d["rear_thread_start_local_x"], d["rear_thread_start_local_x"] + d["rear_thread_len"])]
    cuts = []
    for x0, x1 in zones:
        x = x0 + p
        while x + p / 2 <= x1 - p:
            cuts.append(g.move(g.tube(rmaj + 1, rmin, p / 2, "x", center=False), x))
            x += p
    return g.cut(s, *cuts) if cuts else s
