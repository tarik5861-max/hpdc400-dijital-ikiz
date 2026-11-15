def build(d, G, g):
    # kablo rakoru opsiyonel; govde bbox'ini asmamasi icin cizilmez
    return g.cyl(d["d"] / 2, d["length"], "x", center=False)
