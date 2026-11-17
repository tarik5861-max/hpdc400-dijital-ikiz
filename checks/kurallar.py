"""kurallar.py - params tutarlilik kurallari (check.py'den cagrilir). Geometri gerektirmez.
Hata turleri: KURAL_ITICI, KURAL_DELIK_CUBUK, KURAL_KALIP_PIM, KURAL_PIM_SAYI, KURAL_IDDIA
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _c(pts):
    return sorted((round(a, 3), round(b, 3)) for a, b in pts)


def _inst(P, pid):
    return P["parts"].get(pid, {}).get("instances", [])


def kural_kontrol(P, kararlar_text=None):
    """P = params dict; kararlar_text = KARARLAR.md metni (None ise dosyadan okunur). Hata listesi doner."""
    E = []
    def err(t, part, msg): E.append({"part": part, "type": t, "msg": msg})
    pr = P["parts"]

    # 1. sabit tarafta itici deligi yok
    for pid in ("A21", "A81"):
        for k in pr.get(pid, {}).get("dims", {}):
            if re.search(r"eject|itici", k, re.I):
                err("KURAL_ITICI", pid, f"sabit tarafta itici delik anahtari olmamali: '{k}'")

    # 2. A22 itici cubuk delikleri = A42 cubuk merkezleri
    h = pr["A22"]["dims"].get("ejector_rod_holes", {}).get("centers_yz")
    r = pr["A42"]["dims"].get("ejector_rods", {}).get("centers_yz")
    if h is None or r is None:
        err("KURAL_DELIK_CUBUK", "A22/A42", "ejector_rod_holes veya ejector_rods.centers_yz eksik")
    elif _c(h) != _c(r):
        err("KURAL_DELIK_CUBUK", "A22/A42", f"A22 delik merkezleri {h} != A42 cubuk merkezleri {r}")

    # 3. kalip pimleri kalip siniri icinde, A83 delik sayilari instance sayilariyla ayni
    d82 = pr["A82"]["dims"]
    hw, hh = d82["width_y"] / 2, d82["height_z"] / 2
    for pid, hole_key in (("A84", "pin_holes"), ("A85", "return_pin_holes")):
        ins = _inst(P, pid)
        dd = pr[pid]["dims"]
        rad = max(dd.get("d", 0), dd.get("head", {}).get("d", 0)) / 2
        for i in ins:
            y, z = i["pos"][1], i["pos"][2]
            if abs(y) + rad > hw or abs(z) + rad > hh:
                err("KURAL_KALIP_PIM", i["name"], f"kalip siniri disinda: y={y} z={z} r={rad} sinir=+-{hw}/+-{hh}")
        n_hole = len(pr["A83"]["dims"].get(hole_key, {}).get("centers_yz", []))
        if n_hole != len(ins):
            err("KURAL_PIM_SAYI", "A83", f"{hole_key} sayisi {n_hole} != {pid} instance sayisi {len(ins)}")
    for pid, n in (("A84", 24), ("A85", 4)):
        if len(_inst(P, pid)) != n:
            err("KURAL_PIM_SAYI", pid, f"instance sayisi {len(_inst(P, pid))} != {n}")

    # 4. iddia - params (sabit liste)
    if kararlar_text is None:
        try:
            kararlar_text = open(os.path.join(ROOT, "docs", "KARARLAR.md"), encoding="utf-8").read()
        except OSError:
            kararlar_text = ""
    satir = next((l for l in kararlar_text.splitlines() if l.startswith("| 20")), "")
    iddialar = [  # (KARARLAR metni, params degeri, aciklama)
        ("24 itici pimi", len(_inst(P, "A84")), 24),
        ("4 geri dönüş pimi", len(_inst(P, "A85")), 4),
        ("çift silindir", pr["A41"]["dims"].get("cylinders", {}).get("count"), 2),
        ("5 konumlu", 1 + len(pr["A22"]["dims"].get("ejector_rod_holes", {}).get("centers_yz", []))
            if pr["A22"]["dims"].get("central_hole") else None, 5),
    ]
    for metin, deger, beklenen in iddialar:
        if satir and metin in satir and deger != beklenen:
            err("KURAL_IDDIA", "KARARLAR", f"iddia '{metin}' ({beklenen}) ama params={deger}")
    return E
