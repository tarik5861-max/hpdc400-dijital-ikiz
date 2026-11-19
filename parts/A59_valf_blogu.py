def build(d, G, g):
    # lokal: +X yuzu merkezi (A14 arka yuzune civatali), govde x -depth..0, y +-w/2, z 0..h
    b, sb, ct = d["body"], d["seat_bosses"], d["cartridges"]
    X, W, H = b["depth_x"], b["width_y"], b["height_z"]
    parts = [g.move(g.box(X, W, H), -X / 2, 0, H / 2)]
    for y in sb["centers_y"]:
        parts.append(g.move(g.cyl(sb["d"] / 2, sb["height"], "z"), sb["x_local"], y, H + sb["height"] / 2))
    cx, cy, cz = ct["size_xyz"]
    for y in ct["centers_y"]:
        parts.append(g.move(g.box(cx, cy, cz), -X - cx / 2, y, ct["z_center"]))
    return g.fuse(*parts)
