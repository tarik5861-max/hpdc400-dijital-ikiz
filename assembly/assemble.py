"""
assemble.py - Ürün ağacına göre tüm parçaları çizer, params.json konumlarına yerleştirir.

Kullanım:
  FreeCAD dışı (test):      python3 assembly/assemble.py [--phase 1] [--step out/hpdc400.step]
  FreeCADCmd (PC'de):       FreeCADCmd assembly/assemble.py
  MCP köprüsünden:          execute_code ->  exec(open(r'<repo>/assembly/assemble.py').read())
FreeCAD içinde çalışırsa her instance ayrı Part::Feature olarak ürün ağacı gruplarıyla dokümana eklenir
ve out/hpdc400.FCStd olarak kaydedilir.
"""
import json, os, re, sys, importlib.util, traceback

# MCP execute_code ile exec() edilirken __file__ olmayabilir -> HPDC_ROOT ortam degiskeni veya global
try:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    ROOT = os.environ.get("HPDC_ROOT") or globals().get("HPDC_ROOT")
sys.path.insert(0, os.path.join(ROOT, "lib"))
import geo  # noqa: E402


def resolve_shot(P, shot=None):
    """global.shot_follow kuralini uygular (bellekte; dosya degismez). shot = alt|orta|ust (None: params'taki)."""
    G = P["global"]
    zs = G["shot_positions_z"]
    if shot is not None:
        G["shot_position"] = shot
    if G["shot_position"] not in zs:
        raise KeyError(f"shot_position gecersiz: {G['shot_position']!r} (gecerli: {list(zs)})")
    z_sel = zs[G["shot_position"]]
    dz = z_sel - zs["alt"]
    G["shot_offset_z"] = z_sel
    sf = G["shot_follow"]
    for pid in sf["instances_pos_z_eq_shot"]:
        for i in P["parts"][pid]["instances"]:
            i["pos"][2] = z_sel
            if "bbox" in i:   # params 'alt' degerini tasir; taze yuklenmis P uzerinde bir kez uygulanir
                i["bbox"][2] += dz
                i["bbox"][5] += dz
    for pid in sf.get("bbox_zmin_follow", []):   # sadece alt z siniri vurus konumuyla kayar (ust sabit)
        for i in P["parts"][pid]["instances"]:
            if "bbox" in i:
                i["bbox"][2] += dz
    for path in sf["dims_eq_shot"]:       # "A21.dims.shot_hole.center_yz[1]"
        m = re.fullmatch(r"(\w+)\.dims\.(\w+)\.(\w+)\[(\d+)\]", path)
        pid, k1, k2, idx = m.group(1), m.group(2), m.group(3), int(m.group(4))
        P["parts"][pid]["dims"][k1][k2][idx] = z_sel
    a57 = P["parts"]["A57"]
    ha = a57["dims"]["height_adjust"]["saddle_top_local_z_alt"]
    a57["dims"]["saddles"]["local_z_range"][1] = ha + dz
    for i in a57["instances"]:
        if "bbox" in i:
            i["bbox"][5] = -300 + dz   # params kurali: A57_1.bbox[5] = -300 + dz
    return P


def load_params(shot=None):
    with open(os.path.join(ROOT, "params", "params.json"), encoding="utf-8") as f:
        P = json.load(f)
    with open(os.path.join(ROOT, "params", "bom.json"), encoding="utf-8") as f:
        B = json.load(f)
    resolve_shot(P, shot)
    return P, B


def leaves(B):
    for grp in B["tree"]:
        for c in grp["children"]:
            yield grp, c


META_KEYS = {"name", "pos", "rot", "bbox", "joint", "role", "note"}


def build_part(pid, script, P, overrides=None):
    path = os.path.join(ROOT, script)
    spec = importlib.util.spec_from_file_location(pid, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = dict(P["parts"][pid]["dims"])
    if overrides:
        d.update(overrides)   # instance-bazli olcu (or. pim boyu "length")
    return mod.build(d, P["global"], geo)


def assemble(phase=None, only=None, shot=None):
    P, B = load_params(shot)
    allowed = None
    if phase:
        allowed = set()
        for ph in B["phases"]:
            if ph["phase"] <= phase:
                allowed |= set(ph["items"])
    placed, report = {}, []
    for grp, c in leaves(B):
        pid = c["id"]
        if allowed is not None and pid not in allowed: continue
        if only and pid not in only: continue
        if not os.path.exists(os.path.join(ROOT, c["script"])):
            report.append((pid, "EKSIK_SCRIPT", "")); continue
        try:
            insts = P["parts"][pid]["instances"]
            cache = {}
            def local_for(inst):
                ov = {k: v for k, v in inst.items() if k not in META_KEYS}
                key = json.dumps(ov, sort_keys=True)
                if key not in cache:
                    cache[key] = build_part(pid, c["script"], P, ov)
                    if not geo.is_valid(cache[key]):
                        report.append((pid, "GECERSIZ_GEOMETRI", key))
                return cache[key]
            local = local_for(insts[0])
            if len(insts) != c["qty"]:
                report.append((pid, "ADET_UYUSMAZ", f"bom={c['qty']} params={len(insts)}"))
            for inst in insts:
                placed[inst["name"]] = (pid, grp["id"], geo.place(local_for(inst), inst["pos"], inst.get("rot", [0, 0, 0])))
            report.append((pid, "OK", f"{len(insts)} adet, V={geo.volume(local)/1e9:.4f} m3"))
        except Exception as e:
            report.append((pid, "HATA", f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=2)}"))
    return placed, report, P, B


def to_freecad_doc(placed, B, path):
    import FreeCAD as App
    doc = App.newDocument("HPDC400")
    groups = {}
    for grp in B["tree"]:
        groups[grp["id"]] = doc.addObject("App::DocumentObjectGroup", f"{grp['id']}_{grp['name'].split()[0]}")
    for name, (pid, gid, shp) in placed.items():
        o = doc.addObject("Part::Feature", name)
        o.Shape = shp
        groups[gid].addObject(o)
    doc.recompute()
    doc.saveAs(path)
    return doc


if __name__ == "__main__" or "FreeCAD" in sys.modules:
    args = sys.argv[1:] if __name__ == "__main__" else []
    phase = int(args[args.index("--phase") + 1]) if "--phase" in args else None
    step = args[args.index("--step") + 1] if "--step" in args else os.path.join(ROOT, "out", "hpdc400.step")
    placed, report, P, B = assemble(phase)
    for r in report:
        print(f"{r[0]:5s} {r[1]:18s} {r[2]}")
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    if placed:
        geo.export_step([v[2] for v in placed.values()], step)
        print("STEP ->", step)
        if geo.BACKEND == "freecad":
            to_freecad_doc(placed, B, os.path.join(ROOT, "out", "hpdc400.FCStd"))
            print("FCStd ->", os.path.join(ROOT, "out", "hpdc400.FCStd"))
