"""motion_check.py - Kapama hareketi boyunca carpisma taramasi.
Kullanim: python3 checks/motion_check.py [adim_sayisi]
Her konumda hareketli parcalar ile tum parcalar arasinda common hacmi olculur.
"""
import os, sys, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "assembly"), os.path.join(ROOT, "lib")]
import geo, kinematics          # noqa
from assemble import assemble  # noqa

TOL = 50.0


def apply(shp, M):
    """(R, t) matrisini sekle uygula."""
    from OCP.gp import gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    R, t = M
    tr = gp_Trsf()
    tr.SetValues(R[0][0], R[0][1], R[0][2], t[0], R[1][0], R[1][1], R[1][2], t[1], R[2][0], R[2][1], R[2][2], t[2])
    return BRepBuilderAPI_Transform(shp, tr, True).Shape()


def main():
    if "--vurus-tarama" in sys.argv:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        n = int(args[0]) if args else 8
        tot = 0
        for shot in ("alt", "orta", "ust"):
            worst = run(n, False, shot, quiet=True)
            tot += len(worst)
            print(f"vurus={shot:5s} hareket CARPISMA cifti: {len(worst)}")
            for (a, b), (s, v) in sorted(worst.items(), key=lambda x: -x[1][1])[:10]:
                print(f"  {a} x {b} s={s:.2f} {v/1000:.1f} cm3")
        sys.exit(1 if tot else 0)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = int(args[0]) if args else 8
    worst = run(n, "--kalip-yuksekligi" in sys.argv, None)
    sys.exit(1 if worst else 0)


def run(n, die_sweep, shot, quiet=False):
    placed, _, P, _ = assemble(shot=shot)
    G = P["global"]
    if die_sweep:   # kalip yuksekligi ayari kalip sokulu yapilir; A83/84/85 (itici seti) kaydirma disinda
        placed = {k: v for k, v in placed.items() if v[0] not in ("A81", "A82", "A83", "A84", "A85")}
    # hortumlar (A160, tip=hortum) esnek: referans konumda cizildi, hareketli uclara (A130/A41/A65) uyum saglar -> hareket taramasindan cikarilir; sert borular taranir
    hat = P["parts"]["A160"]["dims"]["hatlar"] if "A160" in P["parts"] else {}
    inst_hat = {i["name"]: i["hat"] for i in P["parts"]["A160"]["instances"]} if "A160" in P["parts"] else {}
    placed = {k: v for k, v in placed.items() if not (v[0] == "A160" and hat[inst_hat[k]]["tip"] == "hortum")}
    allowed = {frozenset(p) for p in P["clearances"]["allowed_contacts"]}
    limits = {frozenset(p[:2]): float(p[2]) for p in P["clearances"].get("allowed_limits", [])}
    mesh = {frozenset(p) for p in P["clearances"].get("mesh_pairs", [])}
    worst = {}
    for i in range(n + 1):
        if die_sweep:
            s = 0.0; dh = G["die_height_min"] + (G["die_height_max"] - G["die_height_min"]) * i / n
        else:
            s = i / n; dh = None
        tr, info = kinematics.pose_full(s, P, dh)
        cur = {k: (v[0], apply(v[2], tr[k]) if k in tr else v[2]) for k, v in placed.items()}
        bb = {k: geo.bbox(v[1]) for k, v in cur.items()}
        for a, b in itertools.combinations(cur, 2):
            if a not in tr and b not in tr:
                continue
            if not all(bb[a][j] <= bb[b][j + 3] and bb[b][j] <= bb[a][j + 3] for j in range(3)):
                continue
            v = geo.volume(geo.common(cur[a][1], cur[b][1]))
            pr = frozenset((cur[a][0], cur[b][0]))
            lim = TOL if pr in mesh else (limits.get(pr, 5000.0) if pr in allowed else TOL)
            if v > lim:
                key = (a, b)
                if key not in worst or v > worst[key][1]:
                    worst[key] = (s if not die_sweep else info['die_height'], v)
        if not quiet: print(f"s={s:.3f} kalip_yuk={info['die_height']:6.1f} plaka dx={info['dx_platen']:6.1f} kafa dx={info['dx_crosshead']:6.1f} somun={info['nut_deg']:8.0f} deg")
    if not quiet:
        print(f"\nCARPISMA cifti: {len(worst)}")
        for (a, b), (s, v) in sorted(worst.items(), key=lambda x: -x[1][1]):
            print(f"  {a:8s} x {b:8s}  en kotu s={s:.2f}  {v/1000:8.1f} cm3")
    return worst


if __name__ == "__main__":
    main()
