def build(d, G, g):
    # lokal: -X uc yuzu merkezi, x 0..length
    return g.tube(d["od"] / 2, d["id"] / 2, d["length"], "x", center=False)
