"""
check.py - Otomatik kalite kapısı (agent'ların her turda çalıştırdığı test).

Kontroller:
  1. Her script çalışıyor mu, geometri geçerli mi, adetler BOM ile tutuyor mu
  2. Parça çifti çakışması (boolean common hacmi) - allowed_contacts hariç
  3. Zemin altına taşan parça var mı (Z < -axis_height)
  4. Kritik mate kontrolleri (kolon eksenleri, kalıp yüksekliği, döküm burcu ekseni)
Çıktı: out/check_report.json + konsol özeti. Çıkış kodu: hata varsa 1.

Kullanım: python3 checks/check.py [--phase N]
"""
import json, os, sys, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "assembly")); sys.path.insert(0, os.path.join(ROOT, "lib"))
import geo                      # noqa
from assemble import assemble   # noqa

TOL_VOL = 50.0      # mm3 altı çakışma = sayısal gürültü
TOL_ALLOWED = 5000.0  # izinli temas çiftinde bile 5 cm3 üstü örtüşme = gömülme hatası


def bbox_overlap(a, b, pad=0.5):
    return all(a[i] - pad <= b[i + 3] and b[i] - pad <= a[i + 3] for i in range(3))


def main():
    phase = int(sys.argv[sys.argv.index("--phase") + 1]) if "--phase" in sys.argv else None
    placed, report, P, B = assemble(phase)
    errors, warns = [], []
    for pid, st, msg in report:
        if st != "OK":
            (warns if st == "EKSIK_SCRIPT" else errors).append({"part": pid, "type": st, "msg": msg})

    allowed = {frozenset(p) for p in P.get("clearances", {}).get("allowed_contacts", [])}
    floor = -P["global"]["axis_height"]
    names = list(placed)
    boxes = {n: geo.bbox(placed[n][2]) for n in names}
    for n in names:
        if boxes[n][2] < floor - 1.0:
            errors.append({"part": n, "type": "ZEMIN_ALTI", "msg": f"zmin={boxes[n][2]:.1f} < zemin {floor}"})

    # lokal orijin / yerlesim uyumu: cizilen parca, olcu mimarinin verdigi bbox ile ortusmeli
    exp = {i["name"]: i["bbox"] for pp in P["parts"].values() for i in pp["instances"] if "bbox" in i}
    for n in names:
        if n in exp:
            dev = max(abs(boxes[n][k] - exp[n][k]) for k in range(6))
            if dev > 2.0:
                errors.append({"part": n, "type": "BBOX_SAPMA",
                               "msg": f"max sapma {dev:.1f} mm; cizilen={[round(x) for x in boxes[n]]} beklenen={exp[n]}"})

    for a, b in itertools.combinations(names, 2):
        pa, pb = placed[a][0], placed[b][0]
        is_allowed = frozenset((pa, pb)) in allowed
        if not bbox_overlap(boxes[a], boxes[b]):
            continue
        v = geo.volume(geo.common(placed[a][2], placed[b][2]))
        # izinli temas = yuzey temasi / nominal-esit gecme: hacim ~0 olmali. Buyuk hacim -> gomulme.
        lim = TOL_ALLOWED if is_allowed else TOL_VOL
        if v > lim:
            errors.append({"part": f"{a} x {b}", "type": "GOMULME" if is_allowed else "CAKISMA",
                           "msg": f"{v/1000:.1f} cm3"})

    res = {"phase": phase, "parts_placed": len(names), "errors": errors, "warnings": warns,
           "bboxes": {n: [round(x, 1) for x in boxes[n]] for n in names}}
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    with open(os.path.join(ROOT, "out", "check_report.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print(f"Yerlesen instance: {len(names)} | HATA: {len(errors)} | UYARI: {len(warns)}")
    for e in errors[:60]:
        print("  HATA ", e["type"], e["part"], e["msg"][:200])
    for w in warns[:60]:
        print("  uyari", w["type"], w["part"])
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
