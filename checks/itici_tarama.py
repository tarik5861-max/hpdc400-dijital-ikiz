"""itici_tarama.py - Itici (A42) strok taramasi: mafsal s=0 (ej=0) ve s=1 (ej=0 ve ej=-EJ_LIMIT; cikarma yalniz kalip acikken).
A161 strok sinirlama mansonu A42'nin ileri konumunu sinirlar (A83/A84/A85 kalip itici seti A42 ile gider);
bu yuzden ej=-145 (tam makine stroku) senaryosu mansonla cakisir ve taranmaz: sinir = global.ejector_box.die_ejection_stroke (65).
Kullanim: python3 checks/itici_tarama.py   (check.py da run() ile cagirir)
"""
import os, sys, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "assembly"), os.path.join(ROOT, "lib"), os.path.dirname(os.path.abspath(__file__))):
    if p not in sys.path:
        sys.path.insert(0, p)
import geo, kinematics   # noqa

TOL = 50.0


def _limit(P):
    return float(P["parts"]["A82"]["dims"].get("ejector_box", {}).get("die_ejection_stroke", 65.0)) \
        if "ejector_box" in P["parts"]["A82"].get("dims", {}) else float(P["global"].get("die_ejection_stroke", 65.0))


def tara(placed, P, limit=None):
    """-> [(a, b, s, ej, cm3)] izinsiz cakisma listesi."""
    from motion_check import apply
    lim = limit if limit is not None else _limit(P)
    hat = P["parts"]["A160"]["dims"]["hatlar"]; ih = {i["name"]: i["hat"] for i in P["parts"]["A160"]["instances"]}
    pl = {k: v for k, v in placed.items() if not (v[0] == "A160" and hat[ih[k]]["tip"] == "hortum")}
    allowed = {frozenset(p) for p in P["clearances"]["allowed_contacts"]}
    limits = {frozenset(p[:2]): float(p[2]) for p in P["clearances"].get("allowed_limits", [])}
    mov = {k for k, v in pl.items() if v[0] == "A42"}
    dieset = {k for k, v in pl.items() if v[0] in ("A83", "A84", "A85")}
    res = {}
    for s in (0.0, 1.0):
        tr, _ = kinematics.pose_full(s, P, None)
        for ej in ((0.0,) if s == 0.0 else (0.0, -lim)):   # itici cikarma yalniz kalip ACIKKEN (s=1); kapaliyken pimler sabit yariya girer (fiziksel olmayan senaryo)
            cur = {}
            for k, v in pl.items():
                sh = v[2]
                if k in tr:
                    sh = apply(sh, tr[k])
                if k in mov | dieset:
                    sh = apply(sh, (kinematics.I3, (ej, 0.0, 0.0)))   # kalip itici seti A42 ucu ile itilir, kalip strok limiti = lim
                cur[k] = (v[0], sh)
            bb = {k: geo.bbox(v[1]) for k, v in cur.items()}
            for a in mov | dieset:
                for b in cur:
                    if a == b or (b in mov | dieset and b < a):
                        continue
                    if not all(bb[a][j] <= bb[b][j + 3] and bb[b][j] <= bb[a][j + 3] for j in range(3)):
                        continue
                    v = geo.volume(geo.common(cur[a][1], cur[b][1]))
                    pr = frozenset((cur[a][0], cur[b][0]))
                    if v > (limits.get(pr, 5000.0) if pr in allowed else TOL):
                        res.setdefault((a, b), (s, ej, v))
    return [(a, b, s, ej, v / 1000) for (a, b), (s, ej, v) in res.items()]


def main():
    from assemble import assemble
    placed, _, P, _ = assemble()
    r = tara(placed, P)
    for a, b, s, ej, v in r:
        print(f"  ITICI CAKISMA {a} x {b} s={s} ej={ej} {v:.1f} cm3")
    print(f"itici_tarama (ej 0 ve -{_limit(P):g}): cakisma cifti {len(r)}")
    sys.exit(1 if r else 0)


if __name__ == "__main__":
    main()
