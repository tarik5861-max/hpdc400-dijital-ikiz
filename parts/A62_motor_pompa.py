# A62 Motor-pompa grubu - taban plakasi, motor ayak altliklari, kampana (ici bos).
# Motor ayri parca: A120 (55 kW). Pompa ayri parcalar: A98..A119 (4520VQ).
# Lokal orijin: taban plakasi alt yuzu, x=0 eski plaka merkezi (plaka merkezi base_plate.center_local_x).
# Mil ekseni lokal X, z = shaft_axis_height_above_origin.


def build(d, G, g):
    bp = d["base_plate"]
    bell = d["bell_housing"]
    feet = d["motor_feet"]
    z_shaft = d["shaft_axis_height_above_origin"]
    t = bp["thickness"]

    # Taban plakasi: alt yuz orijinde, ust yuz z = thickness
    plate = g.box(bp["len_x"], bp["width_y"], t)
    plate = g.move(plate, bp["center_local_x"], 0, t / 2)

    # Kampana (bell housing): motor on yuzu -> pompa montaj yuzu
    b0, b1 = bell["local_x_range"]
    bh = g.tube(bell["d"] / 2, bell["d"] / 2 - bell["wall"], b1 - b0, "x", center=False)
    bh = g.move(bh, b0, 0, z_shaft)

    # Motor ayak altliklari (A120 ayaklari ustune oturur)
    px, py, pz = feet["pad_size_xyz"]
    pads = [g.move(g.box(px, py, pz), feet["pad_center_local_x"], yc, t + pz / 2) for yc in feet["pad_y_centers"]]

    return g.fuse(plate, bh, *pads)
