
def _t_slots(d, g, x_face, sign):
    """T kanallari: x_face = kalip yuzu, sign = govdenin yuzden itibaren yonu (-1: -X, +1: +X)."""
    ts = d.get("t_slots")
    if not ts:
        return []
    W, Hz = d["width_y"], d["height_z"]
    nw, nd, hw, hd = ts["neck_width"], ts["neck_depth"], ts["head_width"], ts["head_depth"]
    out = []
    def seg(depth0, depth1, w, along, pos):
        L = depth1 - depth0
        xc = x_face + sign * (depth0 + depth1) / 2
        if along == "y":
            return g.move(g.box(L, W + 2, w), xc, 0, pos)
        return g.move(g.box(L, w, Hz + 2), xc, pos, 0)
    for along, key in (("y", "horizontal_z_positions"), ("z", "vertical_y_positions")):
        for pos in ts.get(key, []):
            # boyun yuzden disa dogru 1 mm tasar (temiz kesim)
            out.append(seg(-1, nd, nw, along, pos))
            out.append(seg(nd, nd + hd, hw, along, pos))
    return out

def build(d, G, g):
    W, Hz, t = d["width_y"], d["height_z"], d["thickness"]
    s = g.move(g.box(t, W, Hz), t / 2, 0, 0)
    lg = d["toggle_lugs"]
    r = lg["end_radius"]
    ly = lg["y_max"] - lg["y_min"]
    yc = (lg["y_max"] + lg["y_min"]) / 2
    x0 = lg["x_extent_local"][0]
    lugs, pins = [], []
    for px, pz in lg["pin_center_local_xz"]:
        bx = px - x0
        lugs.append(g.move(g.box(bx, ly, 2 * r), x0 + bx / 2, yc, pz))
        lugs.append(g.move(g.cyl(r, ly, "y"), px, yc, pz))
        pins.append(g.move(g.cyl(lg["pin_hole_d"] / 2, ly + 2, "y"), px, yc, pz))
    s = g.fuse(s, *lugs)
    cuts = list(pins)
    tb = d["tie_bar_holes"]
    cuts += [g.move(g.cyl(tb["d"] / 2, t + 2, "x"), t / 2, y, z) for y, z in tb["centers_yz"]]
    ch = d["central_hole"]
    cuts.append(g.move(g.cyl(ch["d"] / 2, t + 2, "x"), t / 2, ch["center_yz"][0], ch["center_yz"][1]))
    ej = d["ejector_rod_holes"]
    cuts += [g.move(g.cyl(ej["d"] / 2, t + 2, "x"), t / 2, y, z) for y, z in ej["centers_yz"]]
    cuts += _t_slots(d, g, 0, 1)
    return g.cut(s, *cuts)
