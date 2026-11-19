"""
A62_motor_pompa.py — 55 kW Flange Motor, Bell Housing, Axial Piston Pump + Pilot Pump (SolidWorks/CAD Level Detail).
"""
def build(d, G, g):
    bp = d["base_plate"]
    mot = d["motor"]
    bell = d["bell_housing"]
    pump = d["pump"]
    z_shaft = d["shaft_axis_height_above_origin"]

    # Taban plakasi (Tank ustune oturan kalın flanşlı sac levha)
    plate = g.box(bp["len_x"], bp["width_y"], bp["thickness"])
    plate = g.move(plate, 0, 0, bp["thickness"] / 2)

    # Motor gövdesi (55 kW IEC 225M silindirik gövde + soğutma kanatçığı simülasyonu)
    m0, m1 = mot["local_x_range"]
    motor_len = m1 - m0
    motor_body = g.cyl(mot["d"] / 2, motor_len, "x", center=False)
    # Terminal kutusu üst kapak
    tb = mot.get("terminal_box", {"size": [240, 180, 120]})
    ts = tb["size"]
    term_box = g.box(ts[0], ts[1], ts[2])
    term_box = g.move(term_box, (m0 + m1) / 2, 0, z_shaft + mot["d"] / 2 + ts[2] / 2)
    motor = g.fuse(motor_body, term_box)
    motor = g.move(motor, m0, 0, z_shaft)

    # Kampana (Bell housing - motor ile pompa arası döküm ara flanş)
    b0, b1 = bell["local_x_range"]
    bell_housing = g.cyl(bell["d"] / 2, b1 - b0, "x", center=False)
    bell_housing = g.move(bell_housing, b0, 0, z_shaft)

    # Pompa grubu (Ana eksenel pistonlu pompa + ön pilot pompa flanşı)
    p0, p1 = pump["local_x_range"]
    pump_main = g.cyl(pump["d"] / 2, p1 - p0, "x", center=False)
    # Pilot pompa ek çıkıntısı (üstte veya yanda küçük silindir)
    pilot_pump = g.cyl(pump["d"] / 3, (p1 - p0) * 0.4, "z", center=False)
    pilot_pump = g.move(pilot_pump, p0 + 40, 0, z_shaft + pump["d"] / 2)
    pump_group = g.fuse(pump_main, pilot_pump)
    pump_group = g.move(pump_group, p0, 0, z_shaft)

    # Motor montaj ayakları / takozları
    feet = g.box(600, 400, 40)
    feet = g.move(feet, (m0 + m1) / 2, 0, bp["thickness"] + 20)

    return g.fuse(plate, motor, bell_housing, pump_group, feet)
