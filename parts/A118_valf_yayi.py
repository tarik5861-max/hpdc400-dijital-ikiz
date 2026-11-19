# A118 Emniyet valfi yayi 239766 (basitlestirilmis: helis yerine bosluklu silindir, sarim araliklari kanal).
# Lokal orijin: valf tarafi uc merkezi, eksen +X.


def build(d, G, g):
    L = d["length"]
    s = g.tube(d["od"] / 2, d["id"] / 2, L, "x", center=False)
    c = d["coils"]
    p = L / c["n"]
    for i in range(1, c["n"]):
        s = g.cut(s, g.move(g.tube(d["od"] / 2 + 1, d["od"] / 2 - c["groove_depth"], c["groove_w"], "x"), i * p, 0, 0))
    return s
