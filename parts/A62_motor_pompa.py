"""
A62_motor_pompa.py — 55 kW IEC Motor + Kampana + Eksenel Pistonlu Ana Pompa (Detaylı Endüstriyel Soğutma Kanatçıklı Tasarım).
"""
def build(d, G, g):
    bp = d["base_plate"]
    mot = d["motor"]
    bell = d["bell_housing"]
    pump = d["pump"]
    z_shaft = d["shaft_axis_height_above_origin"]

    # 1. Taban Plakası (Alt flanşlı kalın levha)
    plate = g.box(bp["len_x"], bp["width_y"], bp["thickness"])
    plate = g.move(plate, 0, 0, bp["thickness"] / 2)

    # 2. Motor Gövdesi (IEC 225M - ana silindir + soğutma kanatçığı halkaları)
    m0, m1 = mot["local_x_range"]
    motor_len = m1 - m0
    core_d = mot["d"] * 0.85
    motor_core = g.cyl(core_d / 2, motor_len, "x", center=False)

    # Soğutma kanatçıkları (radyal diskler)
    fin_list = [motor_core]
    num_fins = 12
    fin_step = motor_len / (num_fins + 1)
    for i in range(1, num_fins + 1):
        fx = m0 + i * fin_step
        fin = g.cyl(mot["d"] / 2, 8, "x", center=False)
        fin_list.append(g.move(fin, fx - 4, 0, 0))

    motor_body = g.fuse(*fin_list)

    # Üst terminal kutusu (Klemens kutusu)
    tb = mot.get("terminal_box", {"size": [240, 180, 120]})
    ts = tb["size"]
    term_box = g.box(ts[0], ts[1], ts[2])
    term_box = g.move(term_box, (m0 + m1) / 2, 0, core_d / 2 + ts[2] / 2)

    motor_full = g.fuse(motor_body, term_box)
    motor_full = g.move(motor_full, m0, 0, z_shaft)

    # 3. Kampana (Bell Housing - döküm ara flanş, kademeli çap)
    b0, b1 = bell["local_x_range"]
    bell_body = g.cyl(bell["d"] / 2, b1 - b0, "x", center=False)
    # Kampana havalandırma / bakım pencereleri (üstte hafif oyuk simülasyonu)
    window = g.box(40, bell["d"] * 0.7, bell["d"] * 0.6)
    window = g.move(window, (b0 + b1) / 2, 0, z_shaft + bell["d"] / 4)
    bell_housing = g.cut(bell_body, window)
    bell_housing = g.move(bell_housing, b0, 0, z_shaft)

    # 4. Eksenel Pistonlu Ana Pompa + Arka Regülatör / Pilot Pompa
    p0, p1 = pump["local_x_range"]
    pump_body = g.cyl(pump["d"] / 2, p1 - p0, "x", center=False)
    # Regülatör / kontrol bloğu (üstte kareimsi valf ünitesi)
    regulator = g.box(90, 100, 80)
    regulator = g.move(regulator, p0 + 70, 0, z_shaft + pump["d"] / 2 + 40)

    # Basma ve emiş flanş rakor çıkışları (üst ve yan flanşlar)
    port_top = g.cyl(25, 40, "z", center=False)
    port_top = g.move(port_top, p1 - 60, 0, z_shaft + pump["d"] / 2)

    pump_full = g.fuse(pump_body, regulator, port_top)
    pump_full = g.move(pump_full, p0, 0, z_shaft)

    # 5. Motor ayak bloğu
    feet = g.box(600, 420, 35)
    feet = g.move(feet, (m0 + m1) / 2, 0, bp["thickness"] + 17.5)

    return g.fuse(plate, motor_full, bell_housing, pump_full, feet)
