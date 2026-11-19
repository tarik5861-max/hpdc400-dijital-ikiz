# A123 Boru tespit konsolu: zemine oturan taban sacı + dikme (lama) + boru kelepcesi (halka).
# dims: pipe_od, clamp {t, h, axis x|z}, clamp_z (boru ekseni yuksekligi, lokal), post {size_xy}, foot {size_xy, thk},
#       post_offset (lokal xy; z ekseninde kelepce yaninda, x ekseninde altinda).
# Lokal orijin: zemin, boru ekseninin dusey izdusumu. Instance anahtarlari olcuyu ezebilir.


def build(d, G, g):
    rp = d["pipe_od"] / 2
    cl, po, ft = d["clamp"], d["post"], d["foot"]
    ro = rp + cl["t"]
    zc = d["clamp_z"]
    ring = g.tube(ro, rp, cl["h"], cl["axis"], center=True)
    ring = g.move(ring, 0, 0, zc)
    ox, oy = d["post_offset"]
    px, py = po["size_xy"]
    if cl["axis"] == "z":
        ztop = zc + cl["h"] / 2
    else:
        ztop = zc - ro + cl["t"] / 2   # dikme halkanin alt etine girer
    post = g.move(g.box(px, py, ztop), ox, oy, ztop / 2)
    fx, fy = ft["size_xy"]
    foot = g.move(g.box(fx, fy, ft["thk"]), ox, oy, ft["thk"] / 2)
    return g.fuse(ring, post, foot)
