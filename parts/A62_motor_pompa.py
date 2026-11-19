"""
A62_motor_pompa.py — 55 kW IEC Motor + Kampana + Çiftli (Tandem) Sabit Deplasmanlı Paletli Pompa Grubu.
"""
def build(d, G, g):
    bp = d["base_plate"]
    mot = d["motor"]
    bell = d["bell_housing"]
    pump = d["pump"]
    z_shaft = d["shaft_axis_height_above_origin"]

    # 1. Taban Plakası
    plate = g.box(bp["len_x"], bp["width_y"], bp["thickness"])
    plate = g.move(plate, 0, 0, bp["thickness"] / 2)

    # 2. Motor Gövdesi (IEC 225M - soğutma kanatçıklı)
    m0, m1 = mot["local_x_range"]
    motor_len = m1 - m0
    core_d = mot["d"] * 0.85
    motor_core = g.cyl(core_d / 2, motor_len, "x", center=False)

    fin_list = [motor_core]
    num_fins = 12
    fin_step = motor_len / (num_fins + 1)
    for i in range(1, num_fins + 1):
        fx = m0 + i * fin_step
        fin = g.cyl(mot["d"] / 2, 8, "x", center=False)
        fin_list.append(g.move(fin, fx - 4, 0, 0))

    motor_body = g.fuse(*fin_list)
    tb = mot.get("terminal_box", {"size": [240, 180, 120]})
    ts = tb["size"]
    term_box = g.box(ts[0], ts[1], ts[2])
    term_box = g.move(term_box, (m0 + m1) / 2, 0, core_d / 2 + ts[2] / 2)

    motor_full = g.fuse(motor_body, term_box)
    motor_full = g.move(motor_full, m0, 0, z_shaft)

    # 3. Kampana (Bell Housing)
    b0, b1 = bell["local_x_range"]
    bell_body = g.cyl(bell["d"] / 2, b1 - b0, "x", center=False)
    window = g.box(40, bell["d"] * 0.7, bell["d"] * 0.6)
    window = g.move(window, (b0 + b1) / 2, 0, z_shaft + bell["d"] / 4)
    bell_housing = g.cut(bell_body, window)
    bell_housing = g.move(bell_housing, b0, 0, z_shaft)

    # 4. Çiftli (Tandem) Paletli Pompa Grubu (Birinci Kademe Pompa + İkinci Kademe Pompa Gövdesi)
    p0, p1 = pump["local_x_range"]
    mid_x = p0 + (p1 - p0) * 0.45

    # 1. Kademe Pompa Gövdesi (Büyük)
    pump1 = g.cyl(pump["d"] / 2, mid_x - p0, "x", center=False)
    pump1 = g.move(pump1, p0, 0, z_shaft)

    # 2. Kademe Pompa Gövdesi (Tandem - biraz daha küçük çaplı ikinci paletli pompa)
    pump2_d = pump["d"] * 0.85
    pump2 = g.cyl(pump2_d / 2, p1 - mid_x, "x", center=False)
    pump2 = g.move(pump2, mid_x, 0, z_shaft)

    # Ortak emiş ve basma manifold blokları (üstte)
    manifold = g.box(120, 160, 60)
    manifold = g.move(manifold, (p0 + p1) / 2, 0, z_shaft + pump["d"] / 2 + 30)

    pump_group = g.fuse(pump1, pump2, manifold)

    # 5. Motor ayak bloğu
    feet = g.box(600, 420, 35)
    feet = g.move(feet, (m0 + m1) / 2, 0, bp["thickness"] + 17.5)

    return g.fuse(plate, motor_full, bell_housing, pump_group, feet)
