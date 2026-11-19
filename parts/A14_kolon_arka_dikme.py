"""
A14_kolon_arka_dikme.py — Şase arka ucundaki ana dikme ve destek yapısı (Modern Endüstriyel Tasarım).
Optimize edilmiş kütle, pahlanmış köşeler, estetik hafifletme ceppleri ve sağlam mesnet yapısı.
"""
def build(d, G, g):
    def rbox(xr, yr, zr):
        (x0, x1), (y0, y1), (z0, z1) = xr, yr, zr
        return g.move(g.box(x1 - x0, y1 - y0, z1 - z0), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)

    p, gu, ur, lr = d["plate"], d["gussets"], d["upper_ribs"], d["lower_ribs"]
    c = p.get("top_corner_chamfer", 0)
    if c:
        (y0, y1), (z0, z1) = p["y_range"], p["z_range"]
        pts = [(y0, z0), (y1, z0), (y1, z1 - c), (y1 - c, z1), (y0 + c, z1), (y0, z1 - c)]
        parts = [g.polyprism(pts, p["local_x_range"][0], p["local_x_range"][1])]
    else:
        parts = [rbox(p["local_x_range"], p["y_range"], p["z_range"])]

    for y0, y1 in gu["y_ranges"]:
        pr = g.polyprism([(-x, z) for x, z in gu["profile_xz"]], 0, y1 - y0)
        parts.append(g.move(g.rot(pr, "z", 90), 0, y0, 0))
    for i, zr in enumerate(ur["z_ranges"]):
        yr = ur["y_ranges"][i] if "y_ranges" in ur else ur["y_range"]
        parts.append(rbox(ur["local_x_range"], yr, zr))

    for yr in lr["y_ranges"]:
        parts.append(rbox(lr["local_x_range"], yr, lr["z_range"]))

    # Modern dokunuş: Orta kısımdan estetik dikey hafifletme/kanal oluğu çıkarma (Görsel hafiflik)
    main_shape = g.fuse(*parts)

    # Hafifletme kanalları (Ön ve arka yüzde estetik yuvalar)
    pocket_left = g.move(g.box(15, 180, 400), p["local_x_range"][0] + 15, -180, 0)
    pocket_right = g.move(g.box(15, 180, 400), p["local_x_range"][0] + 15, 180, 0)
    final_shape = g.cut(main_shape, pocket_left, pocket_right)
    return final_shape
