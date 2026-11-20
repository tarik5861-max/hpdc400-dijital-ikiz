
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
    s = g.move(g.box(t, W, Hz), -t / 2, 0, 0)
    tb = d["tie_bar_holes"]
    cuts = [g.move(g.cyl(tb["d"] / 2, t + 2, "x"), -t / 2, y, z) for y, z in tb["centers_yz"]]

    sh = d["shot_hole"]
    d_sh = sh["d"]

    # 3 vuruş ekseninin (alt, orta, ust) TAMAMI sabit plaka üzerinde delik/yatak olarak açılır.
    for z_pos in [-150.0, -75.0, 0.0]:
        cuts.append(g.move(g.cyl(d_sh / 2, t + 2, "x"), -t / 2, 0, z_pos))

    if "ejector_return_holes" in d:
        erh = d["ejector_return_holes"]
        for y, z in erh["centers_yz"]:
            cuts.append(g.move(g.cyl(erh["d"] / 2, t + 2, "x"), -t / 2, y, z))

    cuts += _t_slots(d, g, 0, -1)
    return g.cut(s, *cuts)
