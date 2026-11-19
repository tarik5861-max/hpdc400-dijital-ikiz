# Kartus rotoru - A103 (45VQ) ve A109 (20VQ) ortak script. Radyal kanat yuvalari (n adet), mil deligi.
# Yuva i acisi: phase_deg + i*360/n (+Y'den +Z'ye, X ekseni etrafinda). Lokal orijin: on yuz merkezi, x 0..width.


def build(d, G, g):
    w = d["width"]
    s = g.tube(d["od"] / 2, d["bore"] / 2, w, "x", center=False)
    sl = d["slots"]
    ro = d["od"] / 2
    h = ro - sl["bottom_r"] + 1
    for i in range(sl["n"]):
        b = g.move(g.box(w + 2, h, sl["width"]), w / 2, sl["bottom_r"] + h / 2, 0)
        s = g.cut(s, g.rot(b, "x", sl["phase_deg"] + 360.0 * i / sl["n"]))
    return s
