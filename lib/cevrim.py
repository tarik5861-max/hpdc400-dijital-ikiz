"""cevrim.py - tam dokum cevrimi (Kademe 1b): zaman tabanli faz tablosu, saf python (FreeCAD gerekmez).
durum(t, P, H) -> {"faz", "s", "ej", "px", "not"}:
  s  mafsal konumu (0 kapali/kilitli .. 1 acik)      ej  itici ilerleme (mm, -X yonu: negatif = ileri)
  px plunger (A52) +X ilerlemesi (mm)       ma maca (A184) cekili orani (0 ileri/kavitede .. 1 cekili, x A167 strok 80 mm)
Sureler animasyon suresidir (gercek cevrim ~60 s, hidrolik.json sarj.cevrim_s); sayisal degerler params'tan, kalanlar VARSAYIM (ikiz tasarim).
Kural (dogrulanmis uzaylar): plunger yalniz s=0'da hareket eder (kapali kalip, kamara tarama 0..500 temiz); itici yalniz s=1'de (itici_tarama).
Maca (A184) Y ekseninde A167 stroku (80 mm) kadar ileri/geri gider; yaglama geometri hareketi yapmaz (yalniz faz adi/durum cubugu). Maca yalniz kalip acikken ileri girer, kapaliyken geri cekilir (ayrim yuzu x=170'e hic girmez).
"""
import math


def _cos(u):
    u = min(max(u, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * u)


def ayarlar(P, H):
    a82 = P["parts"]["A82"]["dims"]
    ej = float(a82.get("ejector_box", {}).get("die_ejection_stroke", P["global"].get("die_ejection_stroke", 65.0)))
    stroke = float(P["parts"]["A52"]["dims"]["stroke"])
    f3 = float(H.get("hizli_vurus_tasarim", {}).get("faz3_strok_mm", 10.0))
    ma = float(P["parts"]["A167"]["dims"]["stroke"])
    return {"stroke": stroke, "f3": f3, "slow": 150.0, "ej": ej, "ma": ma}   # slow: yavas faz stroku = VARSAYIM (dolum agzi kapanana kadar)


def faz_tablosu(c):
    """(ad, sure_s, fn(u)->(s, ej, px), not). u 0..1."""
    S, F3, SL, EJ = c["stroke"], c["f3"], c["slow"], c["ej"]
    k = lambda s=0.0, ej=0.0, px=0.0, ma=0.0: (s, ej, px, ma)
    return [
        ("1 Kalip acik, bekle", 0.5, lambda u: k(1.0, ma=1.0), "kalip acik, parca alindi, maca cekili"),
        ("2 Yaglama / sprey", 0.8, lambda u: k(1.0, ma=1.0), "kalip spreyi + plunger yaglama A143 (geometri hareketi yok)"),
        ("3 Maca gir (A167)", 0.8, lambda u: k(1.0, ma=1.0 - _cos(u)), "maca pimleri kaviteye ilerler (A184, 80 mm)"),
        ("4 Kalip kapanir", 2.0, lambda u: k(1.0 - _cos(u)), "mafsal acik -> kapali"),
        ("5 Kilitle", 0.6, lambda u: k(0.0), "mafsal kilitli, kapama kuvveti"),
        ("6 Dokum dolumu", 0.6, lambda u: k(0.0), "metal kamaraya; plunger geride"),
        ("7 Yavas vurus", 1.2, lambda u: k(0.0, 0.0, SL * _cos(u)), "faz 1: hava tahliyesi, plunger ilerler"),
        ("8 Hizli vurus", 0.5, lambda u: k(0.0, 0.0, SL + (S - F3 - SL) * u), "faz 2: 3,0 m/s (ACC1), kalip dolumu"),
        ("9 Basinc artirma", 0.6, lambda u: k(0.0, 0.0, S - F3 + F3 * _cos(u)), "faz 3: carpan A55, metal cekme"),
        ("10 Katilasma", 1.5, lambda u: k(0.0, 0.0, S), "tutma/sogutma"),
        ("11 Plunger geri", 1.2, lambda u: k(0.0, 0.0, S * (1.0 - _cos(u))), "plunger baslangica doner (kalip hala kapali)"),
        ("12 Maca cek (A167)", 0.8, lambda u: k(0.0, ma=_cos(u)), "maca pimleri geri (kalip kapali), parca serbest"),
        ("13 Kalip acilir", 2.0, lambda u: k(_cos(u), ma=1.0), "mafsal kapali -> acik, plaka 420 mm"),
        ("14 Itici ileri", 0.8, lambda u: k(1.0, -EJ * _cos(u), ma=1.0), "A42/A83/A84/A85 -X yonu, parca cikarilir"),
        ("15 Parca alma", 0.8, lambda u: k(1.0, -EJ, ma=1.0), "parca disari (robot/cikarma)"),
        ("16 Itici geri", 0.8, lambda u: k(1.0, -EJ * (1.0 - _cos(u)), ma=1.0), "itici baslangica"),
    ]


def toplam(c):
    return sum(f[1] for f in faz_tablosu(c))


def durum(t, c):
    tab = faz_tablosu(c)
    T = sum(f[1] for f in tab)
    t = t % T
    for i, (ad, d, fn, nt) in enumerate(tab):
        if t < d or i == len(tab) - 1:
            s, ej, px, ma = fn(t / d)
            return {"i": i, "faz": ad, "s": s, "ej": ej, "px": px, "ma": ma, "not": nt}
        t -= d


if __name__ == "__main__":
    import json, os
    R = os.path.join(os.path.dirname(__file__), "..", "params")
    P = json.load(open(os.path.join(R, "params.json"), encoding="utf-8"))
    H = json.load(open(os.path.join(R, "hidrolik.json"), encoding="utf-8"))
    c = ayarlar(P, H)
    T = toplam(c)
    n = int(T / 0.02)
    bad = 0
    for j in range(n + 1):
        d = durum(j * 0.02, c)
        if d["px"] > 1e-9 and d["s"] > 1e-9: bad += 1
        if abs(d["ej"]) > 1e-9 and d["s"] < 1 - 1e-9: bad += 1
        if d["ma"] < 1 - 1e-9 and 0.02 < d["s"] < 0.98 and abs(d["s"] - 1.0) > 1e-9 and d["s"] > 1e-9 and d["ma"] > 1e-9: bad += 1   # maca kavitedeyken (ma<1) kalip yalniz tam acik/kapali olmali
        if not (-1e-9 <= d["ma"] <= 1 + 1e-9): bad += 1
        if not (-1e-9 <= d["s"] <= 1 + 1e-9 and 0 <= d["px"] <= c["stroke"] + 1e-9 and -c["ej"] - 1e-9 <= d["ej"] <= 1e-9): bad += 1
    print(f"cevrim {T:.1f} s, {n + 1} ornek, kural ihlali {bad}; ayar {c}")
    raise SystemExit(1 if bad else 0)
