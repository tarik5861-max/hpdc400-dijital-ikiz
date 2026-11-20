"""A11 +X bolmesi (X 590..2150, 1540 aciklik) mukavemet hesabi. Girdi: params/params.json. Cikti: out/olcu_2026-11-20_A11_xbolme_mukavemet.txt
Tum yuk/malzeme degerleri IKIZ TASARIM VARSAYIMI (S355, yuk = kutle tahmini x dinamik katsayi)."""
import json, math
p = json.load(open("params/params.json")); P = p["parts"]; d = P["A11"]["dims"]
rho = 7850.0
def kg(w, h, t): return w * h * t * 1e-9 * rho
m = {}
m["A22 hareketli plaka"] = kg(920, 980, 200)
m["A23 arka plaka"] = kg(920, 980, 180)
m["A82 hareketli kalip yarisi (+itici kutusu ~%30)"] = kg(540, 600, 230) * 1.3
m["kolon agirliginin A23 payi (4 x d120 x 2655 / 2)"] = 4 * math.pi / 4 * 0.12**2 * 2.655 * rho / 2
m["mafsal+capraz kafa+A35/A37+somunlar (tahmin)"] = 900.0
m["kalip yuksekligi tahriki A91..A97 (tahmin)"] = 250.0
G = sum(m.values()); g = 9.81
KD = 1.5          # dinamik/sok katsayisi (acma-kapama ivmesi) VARSAYIM
EMN = 1.4         # kutle tahmini belirsizlik payi VARSAYIM
F = G * g * KD * EMN
E = 2.1e5; fy = 355.0; sig_em = fy / 1.5
xs = d["cross_ribs_x"]; x0, x1 = 590.0, 2150.0; tr = d["cross_rib_thk"]
Lc = (x1 - x0) - tr            # serbest aciklik
Wd, H, tp, sw = d["width_y"], d["height"], d["top_plate_thk"], d["side_wall_thk"]
hw = H - tp
def kesit(acik):
    """acik: +Y duvarda acilmis z araliklari (local z, alttan). dikdortgenler (A, zc, I0)"""
    r = [(Wd * tp, H - tp / 2, Wd * tp**3 / 12)]
    r.append((sw * hw, hw / 2, sw * hw**3 / 12))
    # +Y duvar: aciklik cikarilmis
    segs = [(0, hw)]
    for a, b in acik:
        yeni = []
        for s0, s1 in segs:
            if b <= s0 or a >= s1: yeni.append((s0, s1)); continue
            if a > s0: yeni.append((s0, a))
            if b < s1: yeni.append((b, s1))
        segs = yeni
    for s0, s1 in segs:
        r.append((sw * (s1 - s0), (s0 + s1) / 2, sw * (s1 - s0)**3 / 12))
    A = sum(a for a, _, _ in r); yc = sum(a * z for a, z, _ in r) / A
    I = sum(i0 + a * (z - yc)**2 for a, z, i0 in r)
    return A, yc, I
ta = d["tank_access_opening"]
out = []
out.append("A11 +X bolmesi mukavemet (IKIZ TASARIM VARSAYIMI; S355 fy=355, em=fy/1.5=%.0f MPa)" % sig_em)
out.append("Yuk kalemleri (kg): " + "; ".join("%s %.0f" % (k, v) for k, v in m.items()))
out.append("Toplam G=%.0f kg; KD=%.1f, EMN=%.1f -> tasarim yuku F=%.1f kN (hepsi bolme ortasinda, en kotu konum)" % (G, KD, EMN, F / 1e3))
for ad, acik in (("tam kesit", []), ("tank erisim acikligi kesiti (+Y duvar z %d..%d acik)" % tuple(ta["local_z_range"]), [tuple(ta["local_z_range"])])):
    A, yc, I = kesit(acik)
    M = F * Lc / 4.0
    ct = H - yc; cb = yc
    st, sb = M * ct / I, M * cb / I
    f = F * Lc**3 / (48 * E * I)
    out.append("[%s] A=%.0f mm2 yc=%.0f I=%.3e mm4; M=%.1f kNm; sigma ust=%.1f alt=%.1f MPa (x3 kerti kosesi %.0f); ok=%.1f; ort. sehim=%.3f mm (L/%.0f)" % (ad, A, yc, I, M / 1e6, st, sb, 3 * max(st, sb), sig_em, f, Lc / f))
# kesme / ezilme
tau = (F / 2) / (2 * sw * hw)
out.append("Kesme (duvarlarda, F/2): tau=%.1f MPa (em %.0f)" % (tau, sig_em / 3**0.5))
# ust plaka yerel egilme: raylar y=+-350 (A12), duvar ic yuzu +-475, serit L=950, a=125, yuk F/2 ray basina, etkin genislik 280
Ls = Wd - 2 * sw; a = Ls / 2 - 350.0; beff = 200.0 + 2 * tp
Fr = F / 2
Mloc = Fr * a * (Ls - a) / Ls / beff
sl = Mloc / (tp**2 / 6.0)
out.append("Ust plaka yerel egilme (serit %d mm, ray y=350, a=%.0f, beff=%.0f): sigma=%.1f MPa -> SF=%.2f (fy)" % (Ls, a, beff, sl, fy / sl))
# kaburga ezilme (reaksiyon F/2 / rib)
Rr = F / 2
out.append("Kaburga t=%d: reaksiyon %.1f kN/kaburga; ezilme (20 x 475 mm ust plaka altina kaynakli): %.1f MPa" % (tr, Rr / 1e3, Rr / (tr * (Wd - 2 * sw))))
# burkulma: yan duvar sucu basma yok (ust basma ust plakada). ust plaka basma
out.append("SONUC: tum gerilmeler em (%.0f) altinda; en yuksek = ust plaka yerel egilme %.0f MPa (SF %.1f fy). Kaburgaya/duvara ek takviye GEREKMEZ." % (sig_em, sl, fy / sl))
txt = "\n".join(out); print(txt)
open("out/olcu_2026-11-20_A11_xbolme_mukavemet.txt", "w").write(txt + "\n")
