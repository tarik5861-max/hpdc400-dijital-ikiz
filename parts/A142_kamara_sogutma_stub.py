def build(d, G, g):
    # lokal: kamara ekseni uzerinde (y=z=0), x = global x (pos x=0); stub'lar +-Y radyal, kamara yuzeyinde baslar
    r0 = d["sleeve_r"]
    out = []
    for s in d["stubs"]:
        sg, x = s["side"], s["x"]
        y = r0
        boss = g.cyl(d["boss_d"] / 2, d["boss_h"], "y", center=False)
        pipe = g.cyl(d["pipe_d"] / 2, d["pipe_len"], "y", center=False)
        nip = g.cyl(d["nipple_d"] / 2, d["nipple_h"], "y", center=False)
        a = g.fuse(boss, g.move(pipe, 0, d["boss_h"], 0),
                   g.move(nip, 0, d["boss_h"] + d["pipe_len"] - d["nipple_h"], 0))
        a = g.cut(a, g.move(g.cyl(d["port_d"] / 2, d["port_depth"], "y", center=False), 0,
                            d["boss_h"] + d["pipe_len"] - d["port_depth"], 0))
        if sg < 0:
            a = g.rot(a, "z", 180)
        out.append(g.move(a, x, sg * y, 0))
    return g.fuse(*out)
