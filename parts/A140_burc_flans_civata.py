import math


def build(d, G, g):
    # lokal: burc flansi arka yuzu merkezi (x=0), vurus ekseni (y=z=0); basliklar -X yonunde (flans arkasinda)
    # saft flans/plakada gomulu: modellenmez (gomulme cakismasi uretmez)
    n, pcd = d["count"], d["pcd"]
    wh, wt = d["washer_d"], d["washer_t"]
    hd, hh = d["head_d"], d["head_h"]
    sd, sdp = d["socket_d"], d["socket_depth"]
    out = []
    for k in range(n):
        a = math.radians(d["start_angle_deg"] + 360.0 * k / n)
        y, z = pcd / 2 * math.cos(a), pcd / 2 * math.sin(a)
        w = g.move(g.cyl(wh / 2, wt, "x"), -wt / 2, y, z)
        h = g.move(g.cyl(hd / 2, hh, "x"), -wt - hh / 2, y, z)
        h = g.cut(h, g.move(g.cyl(sd / 2, sdp, "x"), -wt - hh + sdp / 2, y, z))
        out.append(g.fuse(w, h))
    return g.fuse(*out)
