# A126 Pnomatik kapi tahrik silindiri (ust rayin ustunde, +X ucta) + kapi baglanti braketi + silindir dikme uzantisi.
# Lokal orijin A71 ile AYNI. Kapi kapali = piston kolu tam disari; kol kisalinca kapi +X'e acilir.


def _bx(g, x0, x1, y0, y1, z0, z1):
    s = g.box(x1 - x0, y1 - y0, z1 - z0)
    return g.move(s, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def build(d, G, g):
    cy = d["cylinder"]
    br = d["bracket"]
    post = d["post_ext"]
    zc = cy["axis_z"]
    bx0, bx1 = cy["body_x_range"]
    r = cy["bore_d"] / 2 + cy["wall"]
    cap = cy["cap_thk"]
    rod_r = cy["rod_d"] / 2

    body = g.move(g.cyl(r, bx1 - bx0, "x"), (bx0 + bx1) / 2, 0, zc)
    cap_r = r + cy["cap_over"]
    c1 = g.move(g.cyl(cap_r, cap, "x"), bx0 + cap / 2, 0, zc)
    c2 = g.move(g.cyl(cap_r, cap, "x"), bx1 - cap / 2, 0, zc)

    rx0 = br["x_range"][1]
    rod = g.move(g.cyl(rod_r, bx0 - rx0, "x"), (rx0 + bx0) / 2, 0, zc)

    out = [body, c1, c2, rod]
    for px in cy["port_x"]:
        out.append(g.move(g.cyl(cy["port_d"] / 2, cy["port_h"], "z"), px, 0, zc + r + cy["port_h"] / 2))

    # kapi baglanti braketi: kapi ustu ayagi + +Y dikme + rod ucu kolu
    ax0, ax1 = br["x_range"]
    fz0, fz1 = br["foot_z"]
    fy = br["foot_y_half"]
    out.append(_bx(g, ax0, ax1, -fy, fy, fz0, fz1))
    uy0, uy1 = br["upright_y"]
    out.append(_bx(g, ax0, ax1, uy0, uy1, fz0, br["arm_z"][1]))
    az0, az1 = br["arm_z"]
    out.append(_bx(g, ax0, ax1, -rod_r - br["arm_over"], uy1, az0, az1))

    # sag uc dikme uzantisi (A125 dikmesinin devami) + silindir arka tutucusu
    out.append(_bx(g, post["x_range"][0], post["x_range"][1], post["y_range"][0], post["y_range"][1], post["z_range"][0], post["z_range"][1]))
    return g.fuse(*out)
