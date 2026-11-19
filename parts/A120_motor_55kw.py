# A120 Elektrik motoru M1 55 kW 4 kutup, IEC 280S/M, B3 ayakli (ikiz_tasarim varsayimi olculer, params A120).
# Lokal orijin: on (DE) kalkan yuzu merkezi, mil ekseni uzerinde; mil +X, govde -X; ayak alti z = -shaft_height_H.
import math


def build(d, G, g):
    def seg(dia, xr):
        a, b = xr
        return g.move(g.cyl(dia / 2, b - a, "x", center=False), a)

    H = d["shaft_height_H"]
    fr = d["frame"]
    parts = [seg(d["de_shield"]["d"], d["de_shield"]["local_x_range"]),
             seg(d["de_hub"]["d"], d["de_hub"]["local_x_range"]),
             seg(fr["d"], fr["local_x_range"]),
             seg(d["nde_shield"]["d"], d["nde_shield"]["local_x_range"])]

    # Mil + kama kanali
    sh = d["shaft"]
    shaft = seg(sh["d"], sh["local_x_range"])
    k = sh["key"]
    k0, k1 = k["local_x_range"]
    key = g.move(g.box(k1 - k0, k["width"], 2 * k["depth"]), (k0 + k1) / 2, 0, sh["d"] / 2)
    parts.append(g.cut(shaft, key))

    # Sogutma kanatciklari (radyal, eksenel)
    fn = d["fins"]
    f0, f1 = fn["local_x_range"]
    r_in = fr["d"] / 2 - fn["thk"]          # govdeye gomulu baslar (fuse icin bindirme)
    h = fn["r_out"] - r_in
    for i in range(fn["count"]):
        ang = 360.0 * (i + 0.5) / fn["count"]
        fin = g.move(g.box(f1 - f0, fn["thk"], h), (f0 + f1) / 2, 0, r_in + h / 2)
        parts.append(g.rot(fin, "x", ang))

    # Fan kapagi (arka): ince cidarli kabuk + izgara delikli alin
    fc = d["fan_cover"]
    c0, c1 = fc["local_x_range"]
    ro = fc["d"] / 2
    shell = g.move(g.tube(ro, ro - fc["wall"], c1 - c0, "x", center=False), c0)
    end = seg(fc["d"], (c0, c0 + fc["end_thk"]))
    gh = fc["grille_holes"]
    holes = []
    for i in range(gh["count"]):
        a = 2 * math.pi * i / gh["count"]
        holes.append(g.move(g.cyl(gh["d"] / 2, fc["end_thk"] * 3, "x"), c0 + fc["end_thk"] / 2,
                            gh["pcd"] / 2 * math.cos(a), gh["pcd"] / 2 * math.sin(a)))
    parts += [shell, g.cut(end, *holes)]

    # Ayaklar (B3): 2 ayak ray, her birinde 2 delik; ray -> govde baglanti nervuru
    ft = d["feet"]
    x_mid = -ft["hole_C_x"] - ft["hole_B_x"] / 2
    zb = -H
    for s in (1, -1):
        y_h = s * ft["hole_A_y"] / 2
        pad = g.move(g.box(ft["pad_len_x"], ft["pad_width_y"], ft["pad_height"]), x_mid, y_h, zb + ft["pad_height"] / 2)
        hs = [g.move(g.cyl(ft["hole_d"] / 2, ft["pad_height"] * 3, "z"), xh, y_h, zb + ft["pad_height"] / 2)
              for xh in (-ft["hole_C_x"], -ft["hole_C_x"] - ft["hole_B_x"])]
        web_h = ft["web_top_z"] - (zb + ft["pad_height"])
        web = g.move(g.box(ft["pad_len_x"], ft["web_width_y"], web_h), x_mid, s * ft["web_center_y"],
                     zb + ft["pad_height"] + web_h / 2)
        parts += [g.cut(pad, *hs), web]

    # Klemens kutusu (ust) + kaide + kablo rakoru
    tb = d["terminal_box"]
    sx, sy, sz = tb["size_xyz"]
    qx, qy, qz = tb["pedestal_xyz"]
    xc = tb["local_center_x"]
    parts.append(g.move(g.box(qx, qy, qz), xc, 0, tb["base_z"] - qz / 2))
    parts.append(g.move(g.box(sx, sy, sz), xc, 0, tb["base_z"] + sz / 2))
    gl = tb["gland"]
    sgn = 1 if gl["side"] == "+Y" else -1
    gland = g.move(g.cyl(gl["d"] / 2, gl["length"], "y", center=False), xc, 0, gl["local_z"])
    if sgn < 0:
        gland = g.rot(gland, "z", 180, xc, 0, 0)
    parts.append(g.move(gland, 0, sgn * sy / 2, 0))
    return g.fuse(*parts)
