"""kurallar.py - params tutarlilik kurallari (check.py'den cagrilir). Geometri gerektirmez.
Hata turleri: KURAL_ITICI, KURAL_DELIK_CUBUK, KURAL_KALIP_PIM, KURAL_PIM_SAYI, KURAL_IDDIA, KURAL_SHOT
Elektrik (elektrik.json yoksa atlanir): KURAL_ELEK_KANAL_ID, _REF, _BAGLI, _KAPSAM, _GUVENLIK, _LOTO, _KOKEN, _DURUM, _HESAP
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
            err("KURAL_IDDIA, KURAL_SHOT", "KARARLAR", f"iddia '{metin}' ({beklenen}) ama params={deger}")
    E += kural_shot(P)
    E += kural_elektrik()
    return E


def kural_shot(P):
    """KURAL_SHOT: shot_follow turetilmis alanlarin secili konumla tutarliligi."""
    E = []
    def err(part, msg): E.append({"part": part, "type": "KURAL_SHOT", "msg": msg})
    G, pr = P["global"], P["parts"]
    zs = G.get("shot_positions_z", {})
    pos = G.get("shot_position")
    if pos not in zs:
        err("global", f"shot_position {pos!r} gecerli anahtar degil {list(zs)}")
        return E
    if zs.get("alt") != -150.0:
        err("global", f"shot_positions_z.alt={zs.get('alt')} != -150")
    z = zs[pos]; dz = z - zs["alt"]
    if G.get("shot_offset_z") != z:
        err("global", f"shot_offset_z {G.get('shot_offset_z')} != z_sel {z}")
    for pid, k1, k2 in (("A21", "shot_hole", "center_yz"), ("A81", "sleeve_bore", "center_yz")):
        c = pr[pid]["dims"].get(k1, {}).get(k2)
        if not c or c[1] != z:
            err(pid, f"{k1}.{k2}={c} Z != z_sel {z}")
    for pid in G["shot_follow"]["instances_pos_z_eq_shot"]:
        for i in _inst(P, pid):
            if i["pos"][2] != z:
                err(i["name"], f"pos[2]={i['pos'][2]} != z_sel {z}")
    a57 = pr["A57"]["dims"]
    top = a57["saddles"]["local_z_range"][1]
    exp = a57["height_adjust"]["saddle_top_local_z_alt"] + dz
    if top != exp:
        err("A57", f"semer ustu {top} != {exp}")
    if exp != 230 + dz:
        err("A57", f"saddle_top_local_z_alt {a57['height_adjust']['saddle_top_local_z_alt']} != 230")
    for i in _inst(P, "A57"):
        if "bbox" in i and i["bbox"][5] != -300 + dz:
            err(i["name"], f"bbox[5]={i['bbox'][5]} != {-300 + dz}")
    sh = [k for k in pr["A21"]["dims"] if re.search(r"shot_hole", k)]
    if sh != ["shot_hole"]:
        err("A21", f"tek shot hole olmali, bulunan anahtarlar: {sh}")
    return E


_ELEK_REF = re.compile(r"^(?:DI|DO|AI|AO)\d+\.\d+$|^DB68\.[A-Za-z0-9_]+$")


def _elek_yaprak(x):
    """ifade agacindaki tum string yapraklari."""
    if isinstance(x, str):
        yield x
    elif isinstance(x, (list, tuple)):
        for y in x:
            yield from _elek_yaprak(y)


def _elek_dictler(x):
    if isinstance(x, dict):
        yield x
        for v in x.values():
            yield from _elek_dictler(v)
    elif isinstance(x, list):
        for v in x:
            yield from _elek_dictler(v)


def _bom_idler(n):
    out = set()
    if isinstance(n, dict):
        if "id" in n:
            out.add(n["id"])
        for v in n.values():
            out |= _bom_idler(v)
    elif isinstance(n, list):
        for v in n:
            out |= _bom_idler(v)
    return out


def kural_elektrik(el=None, bom=None):
    """KURAL_ELEK_*: params/elektrik.json tutarlilik kurallari. el/bom verilmezse dosyadan okunur;
    elektrik.json yoksa atlanir (hata degil)."""
    import json
    E = []
    def err(t, part, msg): E.append({"part": part, "type": t, "msg": msg})
    if el is None:
        yol = os.path.join(ROOT, "params", "elektrik.json")
        if not os.path.exists(yol):
            return E
        with open(yol, encoding="utf-8") as f:
            el = json.load(f)
    if bom is None:
        with open(os.path.join(ROOT, "params", "bom.json"), encoding="utf-8") as f:
            bom = json.load(f)
    bom_ids = _bom_idler(bom.get("tree", bom))
    meta = el.get("meta", {})
    kanallar = el.get("kanallar", [])

    # 1. kanal id benzersiz
    gor = {}
    for k in kanallar:
        i = k.get("id")
        if i in gor:
            err("KURAL_ELEK_KANAL_ID", str(i), "tekrar eden kanal id")
        gor[i] = k
    # 2. mantik referanslari kanal listesinde + 4. aktif kural kapsam_disi/ayrilmis kanala dayanmaz
    mantik = el.get("mantik", {})
    for sec, alanlar in (("donanim", ("id", "ifade")), ("plc", ("id", "ifade")), ("alarmlar", ("kosul",))):
        for x in mantik.get(sec, []):
            kid = x.get("id", x.get("kosul", "?"))
            if x.get("durum") in ("kapsam_disi", "ayrilmis", "istege_bagli"):
                continue  # pasif kural
            for a in alanlar:
                for t in _elek_yaprak(x.get(a)):
                    if not _ELEK_REF.match(t):
                        continue
                    if t not in gor:
                        err("KURAL_ELEK_REF", f"{sec}:{kid}", f"{t} kanal listesinde yok")
                    elif gor[t].get("durum") in ("kapsam_disi", "ayrilmis"):
                        err("KURAL_ELEK_KAPSAM", f"{sec}:{kid}", f"aktif kural {gor[t]['durum']} kanala dayaniyor: {t}")
    # 3. bagli_id bom'da
    for d in _elek_dictler(el):
        for b in d.get("bagli_id", []) or []:
            if b not in bom_ids:
                err("KURAL_ELEK_BAGLI", str(d.get("id", d.get("tag", d.get("hidrolik", "?")))), f"bagli_id {b} bom.json'da yok")
    for t in el.get("teshis_tohumu", []):
        for kn in t.get("kontrol", []):
            for b in (kn[2] if len(kn) > 2 else []):
                if b not in bom_ids:
                    err("KURAL_ELEK_BAGLI", "teshis:" + str(t.get("belirti")), f"bagli_id {b} bom.json'da yok")
    # 5. teshis guvenlik
    for t in el.get("teshis_tohumu", []):
        g = t.get("guvenlik")
        if not (isinstance(g, str) and g.strip()):
            err("KURAL_ELEK_GUVENLIK", str(t.get("belirti")), "guvenlik alani bos/yok")
    # 6. LOTO
    adimlar = el.get("loto", {}).get("adimlar", [])
    if not adimlar:
        err("KURAL_ELEK_LOTO", "loto", "adim yok")
    nolar = [a.get("no") for a in adimlar]
    if nolar != list(range(1, len(adimlar) + 1)):
        err("KURAL_ELEK_LOTO", "loto", f"adim numaralari 1..n sirali degil: {nolar}")
    for a in adimlar:
        if not str(a.get("eylem", "")).strip():
            err("KURAL_ELEK_LOTO", f"loto:{a.get('no')}", "eylem bos")
    # 7. koken / durum
    koken_ok = {"dcc630_sablon", "400t_hesap", "yeni"} | set(meta.get("koken_degerleri", {}))
    durum_ok = set(meta.get("durum_degerleri", {})) or {"aktif", "istege_bagli", "ayrilmis", "kapsam_disi"}
    for d in _elek_dictler(el):
        if "koken" in d and d["koken"] not in koken_ok:
            err("KURAL_ELEK_KOKEN", str(d.get("id", d.get("tag", d.get("slot", "?")))), f"koken {d['koken']!r} izinli degil")
    # durum: kanal/modul kayitlari (oneri kayitlarindaki serbest 'durum' alani kapsam disi)
    for d in list(kanallar) + list(el.get("moduller", [])) + [el.get("dcc630_kapsam_disi_modul", {})]:
        if "durum" in d and d["durum"] not in durum_ok:
            err("KURAL_ELEK_DURUM", str(d.get("id", d.get("slot", "?"))), f"durum {d['durum']!r} izinli degil")
    # 8. hesap sonucu
    hs = el.get("hesap_sonuclari", {})
    fr = hs.get("FR1", {})
    try:
        lo, hi = fr["aralik_A"]
        if not lo <= fr["ayar_A"] <= hi:
            err("KURAL_ELEK_HESAP", "FR1", f"ayar {fr['ayar_A']} A aralik {lo}-{hi} disinda")
    except (KeyError, TypeError, ValueError):
        err("KURAL_ELEK_HESAP", "FR1", "FR1 ayar_A/aralik_A eksik")
    hw = {x.get("id"): x.get("ifade") for x in mantik.get("donanim", [])}
    def nc(a, b):
        return ["not", b] in (hw.get(a) or [])
    if not (nc("HW.KM2", "HW.KM3") and nc("HW.KM3", "HW.KM2")):
        err("KURAL_ELEK_HESAP", "KM2/KM3", "KM2 ile KM3 karsilikli NC kilitli degil")
    return E


def kural_hidrolik(hid=None, bom=None):
    """KURAL_HIDR_*: params/hidrolik.json guvenlik/tutarlilik kurallari (CLAUDE.md kural 10).
    hid/bom verilmezse dosyadan okunur; hidrolik.json yoksa atlanir (hata degil)."""
    import json
    E = []
    def err(t, part, msg): E.append({"part": part, "type": t, "msg": msg})
    if hid is None:
        yol = os.path.join(ROOT, "params", "hidrolik.json")
        if not os.path.exists(yol):
            return E
        with open(yol, encoding="utf-8") as f:
            hid = json.load(f)
    if bom is None:
        with open(os.path.join(ROOT, "params", "bom.json"), encoding="utf-8") as f:
            bom = json.load(f)
    bom_ids = _bom_idler(bom.get("tree", bom))
    el = hid.get("elemanlar", {})
    valfler = {v.get("id"): v for v in el.get("valfler", [])}
    sensorler = {s.get("id"): s for s in el.get("sensorler", [])}

    # 1. yuksek basincli akumulator: kapama vanasi + emniyet + kilitlenebilir desarj + basinc olcumu + LOTO
    gerek = (("kapama", "kapama vanasi"), ("emniyet", "emniyet valfi"), ("desarj", "desarj valfi"),
             ("pt", "basinc sensoru"), ("loto", "LOTO adimi"))
    for a in el.get("akumulatorler", []):
        if (a.get("basinc_bar") or 999) <= 50:      # pilot/kontrol akumulatoru (dusuk basinc) muaf
            continue
        g = str(a.get("guvenlik", "")).lower()
        for anahtar, ad in gerek:
            if anahtar not in g:
                err("KURAL_HIDR_ACC_GUVENLIK", str(a.get("id")), f"guvenlik metninde {ad} yok")
    # 2. desarj valfi + akumulator basinc sensoru (esik) tanimli
    if "DV1" not in valfler:
        err("KURAL_HIDR_DESARJ", "DV1", "deşarj valfi (DV1) elemanlar.valfler'de yok")
    pt2 = sensorler.get("PT2")
    if not pt2:
        err("KURAL_HIDR_OLCUM", "PT2", "akumulator basinc sensoru PT2 yok")
    elif not any("esig" in k and isinstance(v, (int, float)) for k, v in pt2.items()):
        err("KURAL_HIDR_OLCUM", "PT2", "PT2 guvenlik esigi (bar) sayisal degil/yok")
    if "PT1" not in sensorler:
        err("KURAL_HIDR_OLCUM", "PT1", "sistem basinc sensoru PT1 yok")
    # 3. bagli_id'ler bom'da
    for grup in ("akumulatorler", "valfler", "sensorler", "silindirler"):
        for x in el.get(grup, []):
            for b in x.get("bagli_id") or []:
                if b not in bom_ids:
                    err("KURAL_HIDR_BAGLI", str(x.get("id")), f"bagli_id {b} bom.json'da yok")
    # 4. kapama vanasi arkasinda hapsolan basinc (A65 Y1.4) guvenlik on adiminda bosaltilmali
    a65 = hid.get("a65_ic_devre_tasarim")
    if a65:
        g = str(a65.get("guvenlik", "")).lower()
        for anahtar, ad in (("loto", "LOTO"), ("s121", "S121 desarj"), ("pt2", "PT2 < 2 bar dogrulama"),
                            ("hapsolmus", "Y1.4 arkasi hapsolmus basinc"), ("penj_g", "kapak basinci (PENJ_G) dogrulama")):
            if anahtar not in g:
                err("KURAL_HIDR_HAPSOLMA", "a65_ic_devre", f"guvenlik on adiminda {ad} yok")
        ic = {v.get("id") for v in a65.get("valfler", [])}
        for yid in ("Y1.4", "Y1.11"):
            if yid not in ic:
                err("KURAL_HIDR_HAPSOLMA", yid, "ic valf tanimi yok (A yolu kilidi / emniyet)")
    return E
