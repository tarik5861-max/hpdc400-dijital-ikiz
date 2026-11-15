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


def apply(shp, tr):
    if tr[0] == "T":
        return geo.move(shp, tr[1], 0, tr[2])
    _, p0, deg, p1 = tr
    s = geo.rot(shp, "y", deg, p0[0], 0, p0[1])
    return geo.move(s, p1[0] - p0[0], 0, p1[1] - p0[1])


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    placed, _, P, _ = assemble()
    allowed = {frozenset(p) for p in P["clearances"]["allowed_contacts"]}
    worst = {}
    for i in range(n + 1):
        s = i / n
        tr, info = kinematics.pose(s, P)
        cur = {k: (v[0], apply(v[2], tr[k]) if k in tr else v[2]) for k, v in placed.items()}
        bb = {k: geo.bbox(v[1]) for k, v in cur.items()}
        for a, b in itertools.combinations(cur, 2):
            if a not in tr and b not in tr:
                continue
            if not all(bb[a][j] <= bb[b][j + 3] and bb[b][j] <= bb[a][j + 3] for j in range(3)):
                continue
            v = geo.volume(geo.common(cur[a][1], cur[b][1]))
            lim = 5000.0 if frozenset((cur[a][0], cur[b][0])) in allowed else TOL
            if v > lim:
                key = (a, b)
                if key not in worst or v > worst[key][1]:
                    worst[key] = (s, v)
        print(f"s={s:.3f}  plaka dx={info['dx_platen']:6.1f}  kafa dx={info['dx_crosshead']:6.1f}")
    print(f"\nCARPISMA cifti: {len(worst)}")
    for (a, b), (s, v) in sorted(worst.items(), key=lambda x: -x[1][1]):
        print(f"  {a:8s} x {b:8s}  en kotu s={s:.2f}  {v/1000:8.1f} cm3")
    sys.exit(1 if worst else 0)


if __name__ == "__main__":
    main()
