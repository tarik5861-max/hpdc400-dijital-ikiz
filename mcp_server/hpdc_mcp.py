"""
hpdc_mcp.py - HPDC-400 dijital ikiz projesinin MCP sunucusu.

Claude Code (veya herhangi bir MCP istemcisi) bu sunucu ile projeyi tek bir arayuzden yonetir:
  * proje bilgisi: urun agaci, parca olculeri, durum
  * otomatik kontroller: statik cakisma + hareket boyunca cakisma (FreeCAD gerektirmez, OCP ile)
  * canli FreeCAD: montaji yukle, konum ver, animasyon, kalip yuksekligi ayari, ekran goruntusu
    (FreeCAD'de neka-nat/freecad-mcp eklentisinin RPC sunucusu acik olmali: MCP Addon > Start RPC Server)

Calistirma (proje kokunden; .mcp.json bunu otomatik yapar):
  uv run --no-project --python 3.12 --with "mcp[cli]" --with freecad-mcp python mcp_server/hpdc_mcp.py
Sunucu hafiftir (saniyeler icinde acilir). Kontrol araclari geometri cekirdegini (OCP) gerektirir; sunucunun
ortaminda OCP yoksa kontroller ayri bir uv ortaminda cadquery-ocp-novtk ile calisir (ilk cagri paketi indirir).
Ortam degiskenleri: FREECAD_HOST (localhost), FREECAD_PORT (9875), FREECAD_MCP_TOKEN (opsiyonel)
"""
import base64
import json
import os
import subprocess
import sys

try:                                   # mcp 2.x
    from mcp.server.mcpserver import MCPServer as FastMCP, Image
except ImportError:                    # mcp 1.x
    from mcp.server.fastmcp import FastMCP, Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mcp = FastMCP("hpdc400")


# ---------------------------------------------------------------- yardimcilar
def _load(name):
    with open(os.path.join(ROOT, "params", name), encoding="utf-8") as f:
        return json.load(f)


def _python_cmd():
    """Kontrol scriptlerini calistiracak Python: OCP varsa bu ortam, yoksa uv ile VTK'siz OCP ortami."""
    import importlib.util, shutil
    if importlib.util.find_spec("OCP") is not None:
        return [sys.executable]
    uv = shutil.which("uv") or os.path.join(os.path.expanduser("~"), ".local", "bin", "uv.exe")
    return [uv, "run", "--no-project", "--python", "3.12", "--with", "cadquery-ocp-novtk", "python"]


def _run(args, timeout=1800):
    p = subprocess.run(_python_cmd() + args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    out = (p.stdout or "") + (("\n[stderr]\n" + p.stderr[-2000:]) if p.returncode not in (0, 1) and p.stderr else "")
    return p.returncode, out.strip()


def _freecad():
    from freecad_mcp.freecad_client import FreeCADConnection
    return FreeCADConnection(host=os.environ.get("FREECAD_HOST", "localhost"),
                             port=int(os.environ.get("FREECAD_PORT", "9875")),
                             token=os.environ.get("FREECAD_MCP_TOKEN") or None)


def _fc_exec(code):
    """FreeCAD icinde kod calistir; hata metnini anlasilir dondur."""
    try:
        res = _freecad().execute_code(code)
    except Exception as e:  # baglanti yok
        return False, (f"FreeCAD'e baglanilamadi ({type(e).__name__}: {e}). FreeCAD acik mi ve "
                       "'MCP Addon' tezgahinda 'Start RPC Server' basildi mi?")
    if res.get("success"):
        return True, str(res.get("message", "")).strip()
    return False, str(res.get("error", res)) + ("\n" + res["output"] if res.get("output") else "")




def _ensure_loaded():
    ok, msg = _fc_exec("import __main__\nprint('HPDC400' in __import__('FreeCAD').listDocuments() and hasattr(__main__, 'hpdc_poz'))")
    if ok and msg.strip().endswith("True"):
        return True, "zaten yuklu"
    return freecad_montaji_yukle_impl()


def freecad_montaji_yukle_impl():
    macro = os.path.join(ROOT, "HPDC400_yukle.FCMacro").replace("\\", "/")
    root = ROOT.replace("\\", "/")
    code = (f"import os, __main__\nos.environ['HPDC_ROOT'] = r'{root}'\n"
            f"exec(open(r'{macro}', encoding='utf-8').read(), __main__.__dict__)\n")
    return _fc_exec(code)


def _main_call(expr):
    """__main__ isim alanindaki hpdc_* fonksiyonlarini cagir (makro oraya yuklenir)."""
    ok, msg = _ensure_loaded()
    if not ok:
        return ok, msg
    return _fc_exec(f"import __main__\nprint(eval({expr!r}, __main__.__dict__))")


# ---------------------------------------------------------------- proje bilgisi
def _dugumler(nodes):
    """BOM dugumleri, alt agaclar dahil (or. A62 -> pompa parcalari)."""
    for c in nodes:
        yield c
        yield from _dugumler(c.get("children", []))


@mcp.tool()
def proje_durumu() -> str:
    """Projenin ozeti: urun agaci gruplari, faz listesi, parca ve instance sayilari, son git kayitlari."""
    B, P = _load("bom.json"), _load("params.json")
    lines = [B["machine"], f"Koordinat sistemi: {B['coordinate_system']}", ""]
    for g in B["tree"]:
        lines.append(f"{g['id']} {g['name']}: " + ", ".join(f"{c['id']} x{c['qty']}" for c in _dugumler(g["children"])))
    lines.append("")
    for ph in B["phases"]:
        lines.append(f"Faz {ph['phase']}: {ph['name']} ({len(ph['items'])} parca)")
    n_inst = sum(len(p["instances"]) for p in P["parts"].values())
    lines.append(f"\nParca tipi: {len(P['parts'])}, instance: {n_inst}")
    try:
        log = subprocess.run(["git", "log", "--oneline", "-5"], cwd=ROOT, capture_output=True, text=True).stdout
        lines.append("\nSon kayitlar:\n" + log.strip())
    except Exception:
        pass
    return "\n".join(lines)


@mcp.tool()
def parca_bilgisi(parca_id: str) -> str:
    """Bir parcanin (or. 'A24', 'A91') urun agaci kaydi, olculeri, lokal orijini, montaj konumlari ve script dosyasi."""
    B, P = _load("bom.json"), _load("params.json")
    pid = parca_id.strip().upper()
    bom = next((c for g in B["tree"] for c in _dugumler(g["children"]) if c["id"] == pid), None)
    if pid not in P["parts"] or bom is None:
        return f"{pid} bulunamadi. Gecerli kimlikler: " + ", ".join(sorted(P["parts"]))
    return json.dumps({"bom": bom, "params": P["parts"][pid]}, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- otomatik kontroller (FreeCAD gerekmez)
@mcp.tool()
def statik_kontrol(faz: int = 0) -> str:
    """Kalite kapisi: geometri gecerliligi, BOM adetleri, beklenen bbox sapmasi, parca cakisma/gomulme, zemin alti.
    faz=0 tum makine; faz=N sadece N. faza kadar olan parcalar.
    Bir bilgisayardaki ILK cagri geometri cekirdegini indirir (~60 MB, birkac dakika surebilir)."""
    args = ["checks/check.py"] + (["--phase", str(faz)] if faz else [])
    code, out = _run(args)
    return ("YESIL - hata yok\n" if code == 0 else "HATA VAR\n") + out


@mcp.tool()
def hareket_kontrolu(adim: int = 10, kalip_yuksekligi_taramasi: bool = False) -> str:
    """Hareket boyunca carpisma taramasi. Varsayilan: mengene kapali->tam acik (mafsal), 'adim' esit konumda.
    kalip_yuksekligi_taramasi=True: mafsal kapali, kalip yuksekligi min->max (kaliplar sokulu)."""
    args = ["checks/motion_check.py", str(int(adim))] + (["--kalip-yuksekligi"] if kalip_yuksekligi_taramasi else [])
    code, out = _run(args, timeout=1800)
    return ("YESIL - carpisma yok\n" if code == 0 else "CARPISMA VAR\n") + out


# ---------------------------------------------------------------- canli FreeCAD
@mcp.tool()
def freecad_montaji_yukle() -> str:
    """Acik FreeCAD'de montaji bastan kurar (renkler, urun agaci gruplari) ve ac-kapa animasyonunu baslatir."""
    ok, msg = freecad_montaji_yukle_impl()
    return ("Yuklendi. " if ok else "Yuklenemedi: ") + msg[-1500:]


@mcp.tool()
def freecad_konum(mafsal: float = 0.0, kalip_yuksekligi_mm: float = 0.0) -> str:
    """Makineyi bir konumda sabitler. mafsal: 0 = kapali/kilitli, 1 = tam acik.
    kalip_yuksekligi_mm: 200-750 (0 = mevcut deger). Calisan animasyonu durdurur."""
    dh = "None" if not kalip_yuksekligi_mm else repr(float(kalip_yuksekligi_mm))
    ok, msg = _main_call(f"(hpdc_durdur(reset=False), hpdc_poz({float(mafsal)!r}, {dh}))[1]")
    return msg if ok else "Hata: " + msg


@mcp.tool()
def freecad_animasyon(baslat: bool = True) -> str:
    """Mengene ac-kapa animasyonunu baslatir (baslat=True) ya da durdurup kapali konuma getirir."""
    ok, msg = _main_call("hpdc_baslat()" if baslat else "hpdc_durdur()")
    return ("Animasyon basladi." if baslat else "Durduruldu, kapali konumda.") if ok else "Hata: " + msg


@mcp.tool()
def freecad_kalip_yuksekligi_ayarla(hedef_mm: float) -> str:
    """Redüktorlu motorla kalip yuksekligini hedefe goturur (200-750 mm, animasyonlu; kaliplar gizlenir)."""
    ok, msg = _main_call(f"hpdc_kalip_ayar({float(hedef_mm)!r})")
    return f"Kalip yuksekligi {hedef_mm:.0f} mm'ye ayarlaniyor." if ok else "Hata: " + msg


@mcp.tool()
def freecad_ekran_goruntusu(gorunum: str = "Isometric", parca: str = "") -> Image | str:
    """FreeCAD aktif gorunumunun ekran goruntusu. gorunum: Isometric, Front, Top, Right, Rear, Left, Bottom.
    parca: verilirse o nesneye odaklanir (or. 'A91_1')."""
    try:
        b64 = _freecad().get_active_screenshot(gorunum, None, None, parca or None)
    except Exception as e:
        return f"Ekran goruntusu alinamadi: {e}"
    if not b64:
        return "Ekran goruntusu alinamadi (aktif 3D gorunum yok olabilir)."
    return Image(data=base64.b64decode(b64), format="png")


if __name__ == "__main__":
    mcp.run()
