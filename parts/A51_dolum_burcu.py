def build(d, G, g):
    L = d["length"]; ro = d["od"] / 2; ri = d["bore_d"] / 2
    fl = d["flange"]; ph = d["pour_hole"]
    body = g.cyl(ro, L, "x")
    body = g.move(body, -L / 2, 0, 0)
    x0, x1 = fl["local_x_range"]
    flange = g.move(g.cyl(fl["od"] / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0)
    s = g.fuse(body, flange)
    s = g.cut(s, g.move(g.cyl(ri, L + 10, "x"), -L / 2, 0, 0))
    # pour hole (stadium slot through top wall)
    lx, wy = ph["length_x"], ph["width_y"]
    h = fl["od"]
    slot = g.box(lx - wy, wy, h, True)
    slot = g.fuse(slot, g.move(g.cyl(wy / 2, h, "z"), (lx - wy) / 2, 0, 0),
                  g.move(g.cyl(wy / 2, h, "z"), -(lx - wy) / 2, 0, 0))
    slot = g.move(slot, ph["center_local_x"], 0, ro)
    return g.cut(s, slot)
