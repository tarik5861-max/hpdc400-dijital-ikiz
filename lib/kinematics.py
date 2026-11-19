"""
kinematics.py - 5 noktali cift mafsal (toggle) kapama kinematigi.

s = 0  -> kalip kapali, mafsal kilitli (montajin cizildigi konum)
s = 1  -> tam acik (big link acisi = toggle.open_big_link_deg)

pose(s, P) -> {instance_adi: transform}
  transform = ("T", dx, dz)                       sadece oteleme (XZ)
            = ("R", (px0, pz0), deg, (px1, pz1))   Y ekseni etrafinda donme: once pivot0 etrafinda deg, sonra pivot0->pivot1 oteleme
Parca gruplari: hareketli plaka grubu (T), capraz kafa grubu A31+A37 (T), pimler A34 ("joint" alanina gore T;
bolunmus diz pimleri dahil), A32 (A etrafinda R), A33 (C etrafinda R), A36 (E etrafinda R).
Arka uctan bagimsiz: FreeCAD Placement'a da OCP gp_Trsf'e de cevrilir.
"""
import math


def _ang_y(v0, v1):
    """v0 -> v1 (XZ duzlemi) icin +Y ekseni etrafinda sag el kurali acisi (derece)."""
    return math.degrees(math.atan2(v0[1] * v1[0] - v0[0] * v1[1], v0[0] * v1[0] + v0[1] * v1[1]))


def joints(theta_deg, sz, T):
    """Bir yarim (sz=+1 ust, -1 alt) icin eklem konumlari (x, z)."""
    th = math.radians(theta_deg)
    Ax, Az = T["A_xz"][0], sz * T["A_xz"][1]
    Cz = sz * T["C_xz"][1]
    Dz = sz * T["D_xz"][1]
    L1, L2 = T["L1_big_link"], T["L2_front_link"]
    u = (-math.cos(th), -sz * math.sin(th))            # A'dan B'ye birim vektor (diz eksene dogru katlanir)
    B = (Ax + L1 * u[0], Az + L1 * u[1])
    C = (B[0] - math.sqrt(L2 ** 2 - (B[1] - Cz) ** 2), Cz)
    E = (Ax + T["E_from_A"] * u[0], Az + T["E_from_A"] * u[1])
    D = (E[0] + math.sqrt(T["crosshead_link"] ** 2 - (E[1] - Dz) ** 2), Dz)
    return {"A": (Ax, Az), "B": B, "C": C, "E": E, "D": D}


MOVING_PLATEN_GROUP = ("A22", "A28", "A82", "A41", "A42", "A83", "A84", "A85")
CROSSHEAD_GROUP = ("A31", "A37")          # capraz kafa + kapama piston kolu (A35 govdesi sabit)


def pose(s, P):
    T = P["global"]["toggle"]
    th = max(0.0, min(1.0, s)) * T["open_big_link_deg"]
    J = {sz: (joints(0.0, sz, T), joints(th, sz, T)) for sz in (+1, -1)}
    dx_platen = J[1][1]["C"][0] - J[1][0]["C"][0]
    dx_cross = J[1][1]["D"][0] - J[1][0]["D"][0]
    out = {}
    for pid, part in P["parts"].items():
        for inst in part["instances"]:
            n = inst["name"]; z = inst["pos"][2]; sz = 1 if z >= 0 else -1
            j0, j1 = J[sz]
            if pid in MOVING_PLATEN_GROUP:
                out[n] = ("T", dx_platen, 0.0)
            elif pid in CROSSHEAD_GROUP:
                out[n] = ("T", dx_cross, 0.0)
            elif pid == "A36":
                # capraz kafa kolu: lokal orijin = E deligi; E etrafinda doner, E ile birlikte tasinir.
                # aci = kilitli (E->D) vektoru ile anlik (E->D) vektoru arasi (D, E'nin +X tarafinda/eksene yakin)
                a = _ang_y((j0["D"][0] - j0["E"][0], j0["D"][1] - j0["E"][1]),
                           (j1["D"][0] - j1["E"][0], j1["D"][1] - j1["E"][1]))
                out[n] = ("R", j0["E"], a, j1["E"])
            elif pid == "A34":
                k = inst["joint"]
                out[n] = ("T", j1[k][0] - j0[k][0], j1[k][1] - j0[k][1])
            elif pid == "A32":
                a = _ang_y((j0["B"][0] - j0["A"][0], j0["B"][1] - j0["A"][1]),
                           (j1["B"][0] - j1["A"][0], j1["B"][1] - j1["A"][1]))
                out[n] = ("R", j0["A"], a, j1["A"])
            elif pid == "A33":
                a = _ang_y((j0["B"][0] - j0["C"][0], j0["B"][1] - j0["C"][1]),
                           (j1["B"][0] - j1["C"][0], j1["B"][1] - j1["C"][1]))
                out[n] = ("R", j0["C"], a, j1["C"])
    return out, {"dx_platen": dx_platen, "dx_crosshead": dx_cross, "theta": th}


if __name__ == "__main__":
    import json, os
    P = json.load(open(os.path.join(os.path.dirname(__file__), "..", "params", "params.json")))
    for s in (0, 0.25, 0.5, 0.75, 1.0):
        print(s, {k: round(v, 1) for k, v in pose(s, P)[1].items()})


# ---------------------------------------------------------------- genel dönüşüm (matris) + kalıp yüksekliği ayarı
# M = (R, t): R 3x3 satır listesi, t = (tx, ty, tz).  p' = R p + t
I3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
DIE_HEIGHT_GROUP_FIXED = ("A11", "A12", "A21", "A24", "A25", "A81",   # kolonlar, sabit plaka, şase: hareket etmez
                          "A13", "A14", "A51", "A52", "A54", "A55", "A56", "A57", "A58", "A61", "A62", "A71", "A72",
                          "A98", "A99", "A100", "A101", "A102", "A103", "A104", "A105", "A106", "A107", "A108", "A109", "A110", "A111", "A112", "A113", "A114", "A115", "A116", "A117", "A118", "A119", "A120",
                          "A121", "A122", "A123")   # A98..A119: A62 pompa agaci, A120: M1 motor, A121..A123 emis/basinc borulari + tespit (2026-11-19 makine arkasi, sabit); A61 tank sase icinde (sabit)


def _mat_ry(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return ((c, 0, s), (0, 1, 0), (-s, 0, c))


def _mat_rx(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return ((1, 0, 0), (0, c, -s), (0, s, c))


def _mv(R, p):
    return tuple(sum(R[i][j] * p[j] for j in range(3)) for i in range(3))


def _compose(A, B):
    """A ∘ B : önce B, sonra A."""
    Ra, ta = A; Rb, tb = B
    R = tuple(tuple(sum(Ra[i][k] * Rb[k][j] for k in range(3)) for j in range(3)) for i in range(3))
    t = tuple(_mv(Ra, tb)[i] + ta[i] for i in range(3))
    return (R, t)


def to_matrix(tr):
    """pose() çıktısındaki ('T'/'R') dönüşümü matrise çevir."""
    if tr[0] == "T":
        return (I3, (tr[1], 0.0, tr[2]))
    _, p0, deg, p1 = tr
    R = _mat_ry(deg)
    q = _mv(R, (p0[0], 0.0, p0[1]))
    return (R, (p1[0] - q[0], 0.0, p1[1] - q[2]))


def _rot_x_about(deg, cy, cz):
    R = _mat_rx(deg)
    q = _mv(R, (0.0, cy, cz))
    return (R, (0.0, cy - q[1], cz - q[2]))


def die_height_angles(delta, P):
    """Kalıp yüksekliği değişimi delta (mm, + = büyür) -> dişli açıları (derece, +X ekseni etrafında)."""
    D = P["global"]["die_height_drive"]
    nut = delta / D["thread_pitch_mm"] * 360.0
    central = -nut * D["z_nut"] / D["z_central"]
    pinion = -central * D["z_central"] / D["z_pinion"]
    motor_rev = pinion / 360.0 * D["gearbox_ratio"]
    return {"nut_deg": nut, "central_deg": central, "pinion_deg": pinion, "motor_rev": motor_rev}


def pose_full(s, P, die_height=None):
    """Mafsal konumu s + kalıp yüksekliği -> {instance: (R, t)}.
    Kalıp yüksekliği değişince arka plaka ve ona bağlı her şey (mafsal, hareketli plaka, tahrik) +X'te delta kadar kayar;
    somunlar ve dişliler kendi eksenlerinde döner. Kolonlar, sabit plaka, şase, enjeksiyon sabit."""
    G = P["global"]
    dh = G["die_height_current"] if die_height is None else die_height
    delta = dh - G["die_height_current"]
    tog, info = pose(s, P)
    ang = die_height_angles(delta, P)
    shift = (I3, (delta, 0.0, 0.0))
    out = {}
    for pid, part in P["parts"].items():
        if pid in DIE_HEIGHT_GROUP_FIXED:
            continue
        for inst in part["instances"]:
            n = inst["name"]
            M = to_matrix(tog[n]) if n in tog else (I3, (0.0, 0.0, 0.0))
            if pid == "A26":
                _, y, z = inst["pos"]
                M = _compose(_rot_x_about(ang["nut_deg"], y, z), M)
            elif pid == "A91":
                M = _compose(_rot_x_about(ang["central_deg"], 0.0, 0.0), M)
            elif pid == "A93":
                _, y, z = inst["pos"]
                M = _compose(_rot_x_about(ang["pinion_deg"], y, z), M)
            out[n] = _compose(shift, M)
    info = dict(info); info.update(ang); info["die_height"] = dh; info["delta"] = delta
    return out, info
