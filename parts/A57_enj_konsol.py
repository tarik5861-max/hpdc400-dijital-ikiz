def build(d, G, g):
    b, sd = d["base_plate"], d["saddles"]
    parts = [g.move(g.box(b["len_x"], b["width_y"], b["thickness"]), 0, 0, b["thickness"] / 2)]
    z0, z1 = sd["local_z_range"]
    for cx in sd["center_local_x"]:
        parts.append(g.move(g.box(sd["len_x"], sd["width_y"], z1 - z0), cx, 0, (z0 + z1) / 2))
    return g.fuse(*parts)
