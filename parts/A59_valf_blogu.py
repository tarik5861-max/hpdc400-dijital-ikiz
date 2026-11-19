def build(d, G, g):
    # lokal: +X yuzu merkezi (A14 arka yuzune dayanir), sepet tabani z=0..t; govde x -depth..0, y +-w/2
    t, v, lg = d["tray"], d["valve_block"], d["legs"]
    X, W, T = t["depth_x"], t["width_y"], t["thickness"]
    parts = [g.move(g.box(X, W, T), -X / 2, 0, T / 2)]
    # sepet kenari (cevre duvari): tabla ustunde, ic bosluk tup tabanlarini tutar
    rh, rw = t["rim_height"], t["rim_wall"]
    rim = g.cut(g.box(X, W, rh), g.move(g.box(X - rw + 1, W - 2 * rw, rh + 2), (rw + 1) / 2, 0, 0))  # dikme tarafi acik
    parts.append(g.move(rim, -X / 2, 0, T + rh / 2))
    # tuplerin ARASINDA valf blogu: dikme arka yuzune dayali, uzun govde
    vx, vw, vt = v["depth_x"], v["width_y"], v["z_top_local"]
    parts.append(g.move(g.box(vx, vw, vt - T), -vx / 2, 0, T + (vt - T) / 2))
    cx, cy, cz = v["cartridges"]["size_xyz"]
    for z in v["cartridges"]["z_centers"]:
        parts.append(g.move(g.box(cx, cy, cz), -vx - cx / 2, 0, z))
    lx, ly = lg["size_xy"]
    for y in lg["centers_y"]:
        parts.append(g.move(g.box(lx, ly, lg["height"]), lg["x_local"], y, -lg["height"] / 2))
    return g.fuse(*parts)
