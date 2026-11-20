"""hortum_pose.py - hareketli hortumlar: konuma bagli ortogonal polyline (saf python, FreeCAD/OCP yok).

Girdi (params.json): A160.dims.hatlar[hat] -> pts (LOKAL, referans konum), ucler [kaynak_id, hedef_id],
  hortum_uzunluk_mm (sabit hortum boyu), rb_mm, u_halka (referans U-halka tercihi: seg/eksen/isaret/genislik);
  A160.instances[].pos (lokal orijin, global).
Uc hareketi (grup -> otelemesi, mm):
  fixed : (0,0,0)                 sert boru, braket, sabit plaka tarafi
  die   : (delta,0,0)             A35/A130/A131 ... kalip yuksekligi (kinematics.pose_full ile ayni)
  platen: (delta+dx_platen,0,0)   A22/A41 ... (kinematics.MOVING_PLATEN_GROUP)
  shot  : (0,0,dz)                A65 ... vurus konumu (shot_follow.instances_pos_z_eq_shot)
Yol: referans polyline her eksende "emici bacak" (o eksendeki en uzun bacak) ile yeniden uzatilir/kisaltilir;
bacak yon degistirebilir. Hortum boyu L sabit: artan boy U-halka (derinlik = fazlalik/2) ile yakalanir; L yetmezse
'eksik_mm' > 0 doner (hortum gerilir). Yeni yon/uc noktalari tam bagli port noktasidir.
Bukulme: ic bacak >= 2*Rb, uc bacak >= Rb (hatlar.json 'bukum_uyari' ile ayni kural).
"""
import json, os, math, sys

AX = "xyz"
EPS = 1e-6


def _axis(a, b):
    diff = [b[i] - a[i] for i in range(3)]
    k = max(range(3), key=lambda i: abs(diff[i]))
    return k, (1 if diff[k] > 0 else -1)


def _len(pts):
    return sum(abs(pts[i + 1][j] - pts[i][j]) for i in range(len(pts) - 1) for j in range(3))


def grup_of(pid, P):
    """Parca id -> hareket grubu."""
    import kinematics
    if pid in P["global"]["shot_follow"]["instances_pos_z_eq_shot"]:
        return "shot"
    if pid in kinematics.MOVING_PLATEN_GROUP:
        return "platen"
    if pid in P["parts"] and pid not in kinematics.DIE_HEIGHT_GROUP_FIXED:
        return "die"
    return "fixed"


def end_disp(grup, dx_platen, delta, dz):
    return {"fixed": (0.0, 0.0, 0.0), "die": (delta, 0.0, 0.0),
            "platen": (delta + dx_platen, 0.0, 0.0), "shot": (0.0, 0.0, dz)}[grup]


def state(P, s, die_height=None, shot=None):
    """(dx_platen, delta, dz) - mafsal konumu s, kalip yuksekligi, vurus (alt|orta|ust, None: params)."""
    import kinematics
    G = P["global"]
    dh = G["die_height_current"] if die_height is None else die_height
    dx = kinematics.pose(s, P)[1]["dx_platen"]
    zs = G["shot_positions_z"]
    z = zs[shot] if shot else G["shot_offset_z"]
    return dx, dh - G["die_height_current"], z - zs["alt"]


def ref_global(P, hid):
    h = P["parts"]["A160"]["dims"]["hatlar"][hid]
    pos = [i for i in P["parts"]["A160"]["instances"] if i["hat"] == hid][0]["pos"]
    return [[p[i] + pos[i] for i in range(3)] for p in h["pts"]], pos


def _gecerli(pts, ref):
    """Uc bacaklar (port dikmesi) referanstaki eksen+yon ve en az referans uzunlukta kalmali."""
    t = temizle(pts)
    if len(t) < 2:
        return False
    for (i, j, ri, rj) in ((0, 1, 0, 1), (-1, -2, -1, -2)):
        k0, s0 = _axis(ref[ri], ref[rj])
        k1, s1 = _axis(t[i], t[j])
        if k0 != k1 or s0 != s1:
            return False
        if abs(t[j][k1] - t[i][k1]) + 1e-6 < abs(ref[rj][k0] - ref[ri][k0]):
            return False
    return True


def reroute(pts, a, b, ride=None):
    """Referans polyline (U'suz, global) -> uclari a / b kadar oteli, ortogonal.
    Her eksende (a_k != b_k) bir ic kose noktasinda 'atlama' bacagi eklenir (ortak dogrultulu bacaklarla birlesir = emilir);
    uc bacaklar (port dikmesi) yon/uzunluk korur; aday secimi: en kisa yol. Doner (pts, basarisiz_eksenler)."""
    ref = [list(p) for p in pts]
    cur = [list(p) for p in pts]
    bad = []
    for k in range(3):
        d = b[k] - a[k]
        if abs(d) < EPS:
            for p in cur:
                p[k] += a[k]
            continue
        best = None
        n = len(cur) - 1
        t2 = [j for j, p in enumerate(cur) if len(p) > 3 and p[3] == 2]
        for pas in (0, 1):      # pas 0: U-halka 'ride' ucuyla birlikte gider (atlama U'nun diger yaninda); pas 1: serbest
            if pas == 1 and best is not None:
                break
            for i in range(1, n):
                if len(cur[i]) > 3 and cur[i][3]:
                    continue          # U-halka koseleri (etiketli): atlama yeri olamaz
                if pas == 0 and t2 and ride is not None and not ((ride == 1 and i < t2[0]) or (ride == 0 and i > t2[-1])):
                    continue
                cand = [list(p) for p in cur[:i + 1]]
                for p in cand:
                    p[k] += a[k]
                q = list(cur[i]); q[k] += b[k]
                cand.append(q)
                for p in cur[i + 1:]:
                    p2 = list(p); p2[k] += b[k]
                    cand.append(p2)
                # ref kontrolu: onceki eksenlerin kaymasi ref'e de dahil edilmeli -> uc bacak kontrolu cur uzerinden
                if not _gecerli_ref(cand, cur):
                    continue
                c = _len(temizle(cand))
                if best is None or c < best[0] - 1e-6:
                    best = (c, cand)
        if best is None:
            bad.append(AX[k])
            for idx, p in enumerate(cur):
                p[k] += a[k] if idx < len(cur) - 1 else b[k]
        else:
            cur = best[1]
    return cur, bad


def _gecerli_ref(cand, cur):
    """cand'in uc bacaklari cur'unkiyle (eksen, yon, uzunluk>=) uyumlu mu (cur zaten otelenmis, bacaklar ayni)."""
    return _gecerli(cand, cur)


def _u_ekle(pts, seg, e, isg, W, D):
    p, q = pts[seg], pts[seg + 1]
    k, s = _axis(p, q)
    mid = (p[k] + q[k]) / 2.0
    w = W / 2.0
    p1 = list(p); p1[k] = mid - s * w
    p2 = list(p1); p2[e] += isg * D
    p4 = list(p); p4[k] = mid + s * w
    p3 = list(p4); p3[e] += isg * D
    return pts[:seg + 1] + [p1, p2, p3, p4] + pts[seg + 1:]


def temizle(pts):
    """Tekrarlayan noktalari at; es dogrultulu ardisik bacaklari birlestir."""
    out = []
    for p in pts:
        if not out or max(abs(p[i] - out[-1][i]) for i in range(3)) > 1e-4:
            out.append(list(p))
    ch = True
    while ch and len(out) > 2:
        ch = False
        for i in range(1, len(out) - 1):
            a, b, c = out[i - 1], out[i], out[i + 1]
            ax1, ax2 = _axis(a, b)[0], _axis(b, c)[0]
            if ax1 == ax2:
                del out[i]; ch = True; break
    return out


def bukulme(pts, rb):
    """[(bacak_no, uzunluk, gerekli)] ihlal listesi (ic >= 2Rb, uc >= Rb)."""
    n = len(pts) - 1
    v = []
    for i in range(n):
        l = sum(abs(pts[i + 1][j] - pts[i][j]) for j in range(3))
        need = rb if (i == 0 or i == n - 1) else 2 * rb
        if n == 1:
            need = 0
        if l + 1e-6 < need:
            v.append((i + 1, round(l, 1), need))
    return v


def _u_kur(ref, L, rb, u):
    """Referans polyline'a (a=b=0) fazla boy icin U-halka ekle: p1..p4 koseleri etiketli (p2,p3 -> tag=1; p1,p4 -> tag=2).
    Doner (pts, (e, isg) | None)."""
    lp = _len(ref)
    D = (L - lp) / 2.0
    if D < 30.0 or not u:      # u_halka yok = yerlestirilebilecek bos hacim bulunamadi (hat_senkron --u-ara): U yok, fazla boy raporlanir
        return [list(p) + [0] for p in ref], None
    n = len(ref) - 1
    legs = [(i, sum(abs(ref[i + 1][j] - ref[i][j]) for j in range(3)), _axis(ref[i], ref[i + 1])[0]) for i in range(n)]
    order = sorted(legs, key=lambda t: -t[1])
    if u and u["seg"] < n:
        order = [legs[u["seg"]]] + [t for t in order if t[0] != u["seg"]]
    W0 = max(u["genislik"] if u else 0.0, 2 * rb)
    for strict in (True, False, None):
        for (i, l, k) in order:
            ml = ((rb if i == 0 else 2 * rb) + (rb if i == n - 1 else 2 * rb)) if strict else 0.4 * l
            W = min(W0, l - ml)
            if strict is None:
                W = 0.5 * l
            if W < (2 * rb if strict is not None else 60.0):
                continue
            e = AX.index(u["eksen"]) if u["eksen"] != AX[k] else next(j for j in range(3) if j != k)
            isg = u["isaret"]
            pts = _u_ekle([list(p) for p in ref], i, e, isg, W, D)
            out = [list(p) + [0] for p in pts]
            out[i + 1][3] = 2; out[i + 2][3] = 1; out[i + 3][3] = 1; out[i + 4][3] = 2
            return out, (e, isg)
    return [list(p) + [0] for p in ref], None


def _u_ayarla(pts, e_isg, L):
    """Etiketli U-halkanin derinligini, yol boyu L olacak sekilde ayarla (<= 0 ise U kalkar)."""
    if not e_isg:
        return pts
    e, isg = e_isg
    idx = [i for i, p in enumerate(pts) if len(p) > 3 and p[3] == 1]
    if len(idx) != 2:
        return pts
    i2, i3 = idx
    p1 = pts[i2 - 1]
    D = isg * (pts[i2][e] - p1[e]) + (L - _len(pts)) / 2.0
    D = max(D, 0.0)
    for i in (i2, i3):
        pts[i][e] = pts[i2 - 1][e] + isg * D
    return pts


def hose_path(P, hid, dx_platen, delta, dz, L=None):
    """Hortum yolu (global ortogonal polyline). Doner (pts, info).
    info: dogrusal (U'suz yol boyu), fazla (L - U'suz yol), eksik_mm (>0: hortum yetmiyor), bukulme (ihlaller), rigid, u, yol, L."""
    h = P["parts"]["A160"]["dims"]["hatlar"][hid]
    ref, pos = ref_global(P, hid)
    L = float(L if L is not None else h["hortum_uzunluk_mm"])
    g0, g1 = (grup_of(x, P) for x in h["ucler"])
    a, b = end_disp(g0, dx_platen, delta, dz), end_disp(g1, dx_platen, delta, dz)
    rb = h["rb_mm"]
    upts, e_isg = _u_kur(ref, L, rb, h.get("u_halka"))
    rank = {"fixed": 0, "shot": 1, "platen": 1, "die": 2}
    ride = 0 if rank[g0] >= rank[g1] else 1
    pts, bad = reroute(upts, a, b, ride)
    pts = temizle(pts)
    pts = _u_ayarla(pts, e_isg, L)
    pts = temizle(pts)
    yol = _len(pts)
    rigid = all(abs(a[i] - b[i]) < EPS for i in range(3))
    # U'suz yol boyu: U derinligi cikarilarak
    dep = 0.0
    idx = [i for i, p in enumerate(pts) if len(p) > 3 and p[3] == 1]
    if e_isg and len(idx) == 2:
        dep = e_isg[1] * (pts[idx[0]][e_isg[0]] - pts[idx[0] - 1][e_isg[0]])
    lp = yol - 2 * dep
    info = {"dogrusal": lp, "fazla": L - lp, "eksik_mm": max(0.0, yol - L - 1e-3), "bukulme": bukulme(pts, rb),
            "rigid": rigid, "u": bool(e_isg), "eksenyok": bad, "yol": yol, "L": L, "u_derinlik": dep}
    return [p[:3] for p in pts], info


def hose_dims_local(P, hid, pts):
    """A160.build icin d['hatlar'][hid] kopyasi: pts (lokal), takip/u_halka yok."""
    h = dict(P["parts"]["A160"]["dims"]["hatlar"][hid])
    pos = [i for i in P["parts"]["A160"]["instances"] if i["hat"] == hid][0]["pos"]
    h["pts"] = [[p[i] - pos[i] for i in range(3)] for p in pts]
    h.pop("takip", None); h.pop("u_halka", None)
    return h, pos


def cyl_specs(P, hid, pts):
    """FreeCAD/baska arka uc icin: [('cyl', (x,y,z) taban, 'x'|'y'|'z', uzunluk, yaricap), ('sph', merkez, yaricap)]."""
    d = P["parts"]["A160"]["dims"]
    h = d["hatlar"][hid]
    ro = h["od"] / 2.0
    out = []
    n = len(pts) - 1
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        k, s = _axis(a, b)
        lo, hi = sorted((a[k], b[k]))
        c = list(a); c[k] = lo
        out.append(("cyl", tuple(c), AX[k], hi - lo, ro))
        if i > 0:
            out.append(("sph", tuple(a), ro))
    rr, th0 = ro * d["ferrul_oran"], d["ferrul_boy"]
    halka = h.get("halka", [True, True])
    for p, q, on in ((pts[0], pts[1], halka[0]), (pts[-1], pts[-2], halka[1])):
        if not on:
            continue
        k, s = _axis(p, q)
        th = min(th0, d["halka_oran"] * abs(q[k] - p[k]))
        c = list(p); c[k] = p[k] if s > 0 else p[k] - th
        out.append(("cyl", tuple(c), AX[k], th, rr))
    return out


def hortum_idler(P):
    return [hid for hid, h in P["parts"]["A160"]["dims"]["hatlar"].items() if h["tip"] == "hortum"]


def tarama(P, n_s=8, dhs=None, shots=("alt", "orta", "ust")):
    """Kalip yuksekligi x mafsal x vurus taramasi: hortum basina en kotu durumlar. Doner {hid: dict}."""
    G = P["global"]
    dhs = dhs or [G["die_height_min"], G["die_height_current"], G["die_height_max"]]
    res = {}
    for hid in hortum_idler(P):
        r0 = hose_path(P, hid, *state(P, 0.0, G["die_height_current"], "alt"))[1]
        r = {"max_yol": 0.0, "eksik": 0.0, "bukum_ihlal": 0, "min_fazla": 1e9, "max_fazla": -1e9, "ref": len(r0["bukulme"])}
        h = P["parts"]["A160"]["dims"]["hatlar"][hid]
        for dh in dhs:
            for shot in shots:
                for i in range(n_s + 1):
                    st = state(P, i / n_s, dh, shot)
                    pts, inf = hose_path(P, hid, *st)
                    r["max_yol"] = max(r["max_yol"], inf["dogrusal"])
                    r["eksik"] = max(r["eksik"], inf["eksik_mm"])
                    r["min_fazla"] = min(r["min_fazla"], inf["fazla"]); r["max_fazla"] = max(r["max_fazla"], inf["fazla"]); r["u_yok"] = r.get("u_yok", 0) + (0 if inf["rigid"] or inf["u"] else 1)
                    r["bukum_ihlal"] = max(r["bukum_ihlal"], len(inf["bukulme"]))
                    if inf["eksenyok"]:
                        r["eksenyok"] = inf["eksenyok"]
        r["L"] = h["hortum_uzunluk_mm"]
        res[hid] = r
    return res


if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(ROOT, "lib"))
    P = json.load(open(os.path.join(ROOT, "params", "params.json"), encoding="utf-8"))
    print("hat   L_mm  max_yol  eksik  fazla[min..max]  bukum_ihlal(max/ref0)")
    for hid, r in tarama(P).items():
        print(f"{hid:5s} {r['L']:6.0f} {r['max_yol']:7.0f} {r['eksik']:6.0f}  {r['min_fazla']:6.0f}..{r['max_fazla']:6.0f}   {r['bukum_ihlal']}/{r['ref']}"
              + (f" EKSENYOK={r.get('eksenyok')}" if r.get("eksenyok") else ""))
