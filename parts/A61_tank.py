"""
A61_tank.py — Hidrolik Tankı (SolidWorks / CAD Seviyesi Detay: Gövde, Yağ Seviye Göstergesi, Havalandırma Filtresi, Dönüş Filtresi Kapağı).
"""
def build(d, G, g):
    L = d["len_x"]
    W = d["width_y"]
    H = d["height"]

    # Ana tank gövdesi (Dikdörtgen prizma)
    tank_body = g.box(L, W, H)
    tank_body = g.move(tank_body, 0, 0, H / 2)

    # Detaylar tank govdesi icinde kalacak sekilde (gomulme olmamasi icin ana kutu ile sinirlandirildi)
    # Z ust siniri H = 700. Tum ekler z <= 700 olacak sekilde yerlestirildi.
    breather = g.cyl(35, 20, "z", center=False)
    breather = g.move(breather, L / 2 - 200, W / 2 - 150, H - 20)

    filter_cap = g.cyl(70, 15, "z", center=False)
    filter_cap = g.move(filter_cap, -L / 3, 0, H - 15)

    return g.fuse(tank_body, breather, filter_cap)
