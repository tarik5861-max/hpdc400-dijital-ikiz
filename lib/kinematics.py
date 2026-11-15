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


MOVING_PLATEN_GROUP = ("A22", "A28", "A82", "A41", "A42")
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
