def build(d, G, g):
    # lokal orijin = A35 ekseni uzerinde, A35 flans montaj yuzu (x=0), +X arkaya. 2 mesnet bileziği + dikme + yatak plakasi (blok altinda degil, ustunde: blok bileziklere asili)
    c = d["collar"]
    ro, ri, ln = c["od"] / 2, c["id"] / 2, c["len"]
    s = []
    for x0 in c["x_starts"]:
        s.append(g.move(g.tube(ro, ri, ln, "x", center=False), x0, 0, 0))
        s.append(g.move(g.box(ln, c["web_y"], c["web_z1"] - c["web_z0"]), x0 + ln / 2, 0, (c["web_z0"] + c["web_z1"]) / 2))
    return g.fuse(*s)
