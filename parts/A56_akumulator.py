def build(d, G, g):
    L = d["length"]; v = d["top_valve"]; fr = d["foot_ring"]
    body_h = L - v["height"]
    body = g.move(g.cyl(d["od"] / 2, body_h, "z"), 0, 0, body_h / 2)
    valve = g.move(g.cyl(v["d"] / 2, v["height"], "z"), 0, 0, body_h + v["height"] / 2)
    return g.fuse(body, valve)
