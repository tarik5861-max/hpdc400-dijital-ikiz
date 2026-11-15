def build(d, G, g):
    s = g.move(g.box(d["box_x"], d["box_y"], d["box_z"]), d["box_x"] / 2, 0, 0)
    fa, fb = d["flange_local_x"]
    s = g.fuse(s, g.move(g.cyl(d["flange_d"] / 2, fb - fa, "x", center=False), fa))
    hole = g.move(g.cyl(d["output_shaft_hole_d"] / 2, d["output_hole_depth"] + 1, "x", center=False), -1)
    return g.cut(s, hole)
