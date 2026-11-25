"""acik_kalip_tarama.py - Acik kalipta plunger (A52+A186) ve itici (A42 + kalip itici seti A83/84/85) taramasi.
(a) plunger px=0..plunger_stroke x s in {1.0, s(300 mm)} ej=0; (b) itici ej=0..-die_ejection_stroke x s in {s300, 1.0}.
s(300) = plaka acikligi (kinematics dx_platen) 300 mm'ye esit olan mafsal s. Yontem: itici_tarama/motion_check (pose_full + apply).
Kullanim: python3 checks/acik_kalip_tarama.py  -> out/acik_kalip_tarama.txt
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "assembly"), os.path.join(ROOT, "lib"), os.path.dirname(os.path.abspath(__file__))):
    if p not in sys.path:
        sys.path.insert(0, p)
import geo, kinematics   # noqa
from motion_check import apply   # noqa
from assemble import assemble    # noqa

TOL = 50.0
ACIKLIK = 300.0
PLUNGER = ("A52", "A186")
ITICI = ("A42", "A83", "A84", "A85")


def s_of(P, opening):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        if kinematics.pose(m, P)[1]["dx_platen"] < opening:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def scan(placed, P, s, mov_ids, shifts, label, out):
    hat = P["parts"]["A160"]["dims"]["hatlar"]; ih = {i["name"]: i["hat"] for i in P["parts"]["A160"]["instances"]}
    pl = {k: v for k, v in placed.items() if not (v[0] == "A160" and hat[ih[k]]["tip"] == "hortum")}
    allowed = {frozenset(p) for p in P["clearances"]["allowed_contacts"]}
    limits = {frozenset(p[:2]): float(p[2]) for p in P["clearances"].get("allowed_limits", [])}
    tr, info = kinematics.pose_full(s, P, None)
    mov = {k for k, v in pl.items() if v[0] in mov_ids}
    res = {}
    for sh_x in shifts:
        cur = {}
        for k, v in pl.items():
            sh = apply(v[2], tr[k]) if k in tr else v[2]
            if k in mov:
                sh = apply(sh, (kinematics.I3, (sh_x, 0.0, 0.0)))
            cur[k] = (v[0], sh)
        bb = {k: geo.bbox(v[1]) for k, v in cur.items()}
        for a in mov:
            for b in cur:
                if a == b or (b in mov and b < a):
                    continue
                if not all(bb[a][j] <= bb[b][j + 3] and bb[b][j] <= bb[a][j + 3] for j in range(3)):
                    continue
                v = geo.volume(geo.common(cur[a][1], cur[b][1]))
                pr = frozenset((cur[a][0], cur[b][0]))
                if v > (limits.get(pr, 5000.0) if pr in allowed else TOL):
                    if (a, b) not in res or v > res[(a, b)][1]:
                        res[(a, b)] = (sh_x, v)
    out.append(f"{label} s={s:.4f} (acik {info['dx_platen']:.1f} mm): " + ("TEMIZ" if not res else f"CAKISMA {len(res)} cift"))
    for (a, b), (x, v) in res.items():
        out.append(f"   {a}({cur[a][0]}) x {b}({cur[b][0]}) kayma_x={x:.0f} {v/1000:.1f} cm3")
    return len(res)


def main():
    placed, _, P, _ = assemble()
    G = P["global"]
    s300 = s_of(P, ACIKLIK)
    stroke = float(G["plunger_stroke"])
    lim = float(P["parts"]["A82"]["dims"]["ejector_box"]["die_ejection_stroke"]) if "ejector_box" in P["parts"]["A82"].get("dims", {}) else float(G.get("die_ejection_stroke", 65.0))
    n = int(round(stroke / 25.0))
    px = [stroke * i / n for i in range(n + 1)]
    ej = [0.0, -lim / 2, -lim]
    out = [f"s(300 mm)={s300:.4f}; plunger px 0..{stroke:g} adim {stroke/n:.1f}; itici ej 0..-{lim:g}"]
    tot = 0
    for s, nm in ((1.0, "a1 plunger s=1"), (s300, "a2 plunger s=300")):
        tot += scan(placed, P, s, PLUNGER, px, nm, out)
    for s, nm in ((s300, "b1 itici s=300"), (1.0, "b2 itici s=1")):
        tot += scan(placed, P, s, ITICI, ej, nm, out)
    open(os.path.join(ROOT, "out", "acik_kalip_tarama.txt"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))
    sys.exit(1 if tot else 0)


if __name__ == "__main__":
    main()
