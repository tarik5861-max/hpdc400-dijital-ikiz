# A71 Operator koruma kapisi - profil cerceve (kenar + pencere ayirici), sac dolgu, alt ray.
# Lokal orijin: panel alt kenarinin -X ucundaki orta nokta, kalinlik ortasi.
# Panel +X'te (0..len_x), +Z'de (0..height), kalinlik +-thk/2 Y'de.
# Cam paneller A124, ust ray+makara A125, tahrik A126, guvenlik anahtari A127, kol+kenar A128.


def _bx(g, x0, x1, y0, y1, z0, z1):
    s = g.box(x1 - x0, y1 - y0, z1 - z0)
    return g.move(s, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def build(d, G, g):
    pn = d["panel"]
    win = d["window"]
    trk = d["bottom_track"]

    L = pn["len_x"]
    T = pn["thickness_y"]
    H = pn["height"]
    fp = pn["frame_profile"]
    t = d["infill_thk"]
    h = T / 2

    wx0, wx1 = win["local_x_range"]
    wz0, wz1 = win["local_z_range"]
    wxm = (wx0 + wx1) / 2

    # dis cerceve: 4 profil
    parts = [
        _bx(g, 0, fp, -h, h, 0, H),
        _bx(g, L - fp, L, -h, h, 0, H),
        _bx(g, fp, L - fp, -h, h, 0, fp),
        _bx(g, fp, L - fp, -h, h, H - fp, H),
    ]
    # pencere cercevesi (cam bosluguna komsu) + orta ayirici
    parts += [
        _bx(g, wx0 - fp, wx1 + fp, -h, h, wz0 - fp, wz0),
        _bx(g, wx0 - fp, wx1 + fp, -h, h, wz1, wz1 + fp),
        _bx(g, wx0 - fp, wx0, -h, h, wz0, wz1),
        _bx(g, wx1, wx1 + fp, -h, h, wz0, wz1),
        _bx(g, wxm - fp / 2, wxm + fp / 2, -h, h, wz0, wz1),
    ]
    # sac dolgu: ic dikdortgen - pencere cercevesi dis siniri
    infill = _bx(g, fp, L - fp, -t / 2, t / 2, fp, H - fp)
    hole = _bx(g, wx0 - fp, wx1 + fp, -T, T, wz0 - fp, wz1 + fp)
    infill = g.cut(infill, hole)

    # alt ray
    x0, x1 = trk["local_x_range"]
    y0, y1 = trk["local_y_range"]
    z0, z1 = trk["local_z_range"]
    rail = _bx(g, x0, x1, y0, y1, z0, z1)

    return g.fuse(parts[0], *parts[1:], infill, rail)
