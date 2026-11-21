# A182 Kamara (A51) arka destegi: eyer + dikme + taban plakasi; A11 ust yuzune dayanir (ikiz_tasarim varsayimi)
# Lokal orijin: vurus ekseni (y=0, z=z_sel), x global. bottom_local_z TURETILMIS (assemble.resolve_shot): frame_top_z - z_sel.
def build(d, G, g):
    x0, x1 = d["cradle_x"]
    px0, px1 = d["pillar_x"]
    fx0, fx1 = d["foot_x"]
    zb = d["bottom_local_z"]
    cz0, cz1 = d["cradle_z"]
    cy, py, fy, ft = d["cradle_half_y"], d["pillar_half_y"], d["foot_half_y"], d["foot_t"]
    rs = d["sleeve_r"] + d["seat_gap"]
    cradle = g.move(g.box(x1 - x0, 2 * cy, cz1 - cz0), (x0 + x1) / 2, 0, (cz0 + cz1) / 2)
    cradle = g.cut(cradle, g.move(g.cyl(rs, (x1 - x0) + 2, "x"), (x0 + x1) / 2, 0, 0))
    pillar = g.move(g.box(px1 - px0, 2 * py, cz0 - (zb + ft) + 2), (px0 + px1) / 2, 0, ((zb + ft) + cz0) / 2 - 1)
    foot = g.move(g.box(fx1 - fx0, 2 * fy, ft), (fx0 + fx1) / 2, 0, zb + ft / 2)
    return g.fuse(cradle, pillar, foot)
