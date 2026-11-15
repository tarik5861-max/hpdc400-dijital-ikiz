# A71 Operator koruma kapisi - panel (pencereli), alt ray, cam (glazing).
# Lokal orijin: panel alt kenarinin -X ucundaki orta nokta, kalinlik ortasi.
# Panel +X'te (0..len_x), +Z'de (0..height), kalinlik +-thk/2 Y'de.


def build(d, G, g):
    pn = d["panel"]
    win = d["window"]
    trk = d["bottom_track"]

    L = pn["len_x"]
    T = pn["thickness_y"]
    H = pn["height"]

    # Panel govdesi: alt-orta orijin -> merkezli kutu, sonra +L/2 X, +H/2 Z
    panel = g.box(L, T, H)
    panel = g.move(panel, L / 2, 0, H / 2)

    # Pencere boslugu (optional): kalinlik boyunca kes
    wx0, wx1 = win["local_x_range"]
    wz0, wz1 = win["local_z_range"]
    cut_box = g.box(wx1 - wx0, T + 2, wz1 - wz0)
    cut_box = g.move(cut_box, (wx0 + wx1) / 2, 0, (wz0 + wz1) / 2)
    panel = g.cut(panel, cut_box)

    # Cam (glazing): pencere boyutunda, glazing_thk kalinliginda
    glass = g.box(wx1 - wx0, win["glazing_thk"], wz1 - wz0)
    glass = g.move(glass, (wx0 + wx1) / 2, 0, (wz0 + wz1) / 2)

    # Alt ray: lokal x 0..2400, y -60..20, z -40..0
    x0, x1 = trk["local_x_range"]
    y0, y1 = trk["local_y_range"]
    z0, z1 = trk["local_z_range"]
    rail = g.box(x1 - x0, y1 - y0, z1 - z0)
    rail = g.move(rail, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)

    return g.fuse(panel, glass, rail)
