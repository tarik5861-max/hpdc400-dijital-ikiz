def build(d, G, g):
    # A29: Sabit plaka bos vurus ekseni dolgu takozu (kapanmis kor tapa)
    r = d["d"] / 2
    h = d["thickness"]
    c = g.cyl(r, h, "x")
    return g.move(c, -h / 2, 0, 0)
