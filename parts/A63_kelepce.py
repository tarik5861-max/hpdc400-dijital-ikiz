def build(d, G, g):
    # lokal: tup sirasi ekseni X=0,Y=0; band alt yuzu z=0. Halkalar her tupu sarar + A14 arka yuzune dayanan duz bar
    h, t, ro = d["band_height"], d["band_thickness"], d["tube_od"] / 2
    parts = [g.move(g.tube(ro + t, ro, h, "z", center=False), 0, y, 0) for y in d["centers_y"]]
    rb = d["rear_bar"]
    x0, x1 = rb["x_local_range"]
    w = rb["half_width_y"]
    parts.append(g.move(g.box(x1 - x0, 2 * w, h), (x0 + x1) / 2, 0, h / 2))
    return g.fuse(*parts)
