def build(d, G, g):
    # lokal: -X yuzu merkezi, govde x 0..thickness, disli halkasi gear_x ile
    t = d["thickness"]
    gr = d["gear_ring"]
    x0, x1 = gr["local_x_range"]
    body = g.cyl(d["body_od"] / 2, t, "x", center=False)
    ring = g.gear_x(gr["teeth"], gr["module"], x0, x1, 0.0, d["gear_phase_deg"], 0, 0)
    s = g.fuse(body, ring)
    bore = g.move(g.cyl(d["bore_d"] / 2, t + 2, "x", center=False), -1)
    return g.cut(s, bore)
