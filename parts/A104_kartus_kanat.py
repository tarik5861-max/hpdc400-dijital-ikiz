# Kartus kanadi (vane) - A104 (45VQ) ve A110 (20VQ) ortak script. Instance basina 'tip_r' override:
# kanat ucu kam profiline (halka) yaslanir, kanat rotor yuvasinda kayar. Lokal: +Y radyal, x 0..width;
# instance rot [aci,0,0] = rotor yuva acisi.


def build(d, G, g):
    w, h, t = d["width"], d["height"], d["thk"]
    tip = d["tip_r"]
    return g.move(g.box(w, h, t), w / 2, tip - h / 2, 0)
