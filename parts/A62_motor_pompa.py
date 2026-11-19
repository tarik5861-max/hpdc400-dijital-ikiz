# A62 Motor-pompa grubu - taban plakasi, motor, kampana (ici bos), motor ayagi. Pompa ayri parcalar: A98..A119 (4520VQ).
# Lokal orijin: taban plakasi alt yuz merkezi. Mil ekseni lokal X, z = shaft_axis_height_above_origin.


def build(d, G, g):
    bp = d["base_plate"]
    mot = d["motor"]
    bell = d["bell_housing"]
    z_shaft = d["shaft_axis_height_above_origin"]

    # Taban plakasi: alt yuz orijinde, ust yuz z = thickness
    plate = g.box(bp["len_x"], bp["width_y"], bp["thickness"])
    plate = g.move(plate, 0, 0, bp["thickness"] / 2)

    # Motor: -X ucunda, local_x_range ile
    m0, m1 = mot["local_x_range"]
    motor = g.cyl(mot["d"] / 2, m1 - m0, "x", center=False)
    motor = g.move(motor, m0, 0, z_shaft)

    # Kampana (bell housing)
    b0, b1 = bell["local_x_range"]
    bh = g.tube(bell["d"] / 2, bell["d"] / 2 - bell["wall"], b1 - b0, "x", center=False)
    bh = g.move(bh, b0, 0, z_shaft)

    # Motor ayagi bloğu (optional, motor altinda): 500x360, z 30..80
    feet = g.box(500, 360, 50)
    feet = g.move(feet, (m0 + m1) / 2, 0, bp["thickness"] + 25)

    return g.fuse(plate, motor, bh, feet)
