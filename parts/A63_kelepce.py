def build(d, G, g):
    # lokal: tup sirasi ekseni X=0,Y=0; band alt yuzu z=0. Halkalar her tupu sarar; arka barlar valf blogunu atlar
    h, t, ro = d["band_height"], d["band_thickness"], d["tube_od"] / 2
    parts = [g.move(g.tube(ro + t, ro, h, "z", center=False), 0, y, 0) for y in d["centers_y"]]
    rb = d["rear_bars"]
    x0, x1 = rb["x_local_range"]
    for ya, yb in rb["y_ranges"]:
        parts.append(g.move(g.box(x1 - x0, yb - ya, h), (x0 + x1) / 2, (ya + yb) / 2, h / 2))
    return g.fuse(*parts)
