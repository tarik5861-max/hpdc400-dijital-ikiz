"""
geo.py - Arka uçtan bağımsız ince geometri katmanı.

Aynı parça scripti iki yerde çalışır:
  * FreeCAD içinde (MCP köprüsü / FreeCADCmd)  -> backend = "freecad"  (Part modülü)
  * FreeCAD olmayan ortamda (CI / bulut test)  -> backend = "ocp"      (OpenCascade, pip cadquery-ocp)
İkisi de aynı OCC çekirdeğini kullanır, sonuç hacimler aynıdır.

Parça scriptleri SADECE bu fonksiyonları kullanır:
  box, cyl, tube, cut, fuse, common, move, rot, hole_x/y/z (kısayol), volume, bbox
"""
import math

BACKEND = None
try:
    import FreeCAD as App  # noqa
    import Part            # noqa
    BACKEND = "freecad"
except Exception:
    BACKEND = "ocp"

AX = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}

# ---------------------------------------------------------------- FreeCAD
if BACKEND == "freecad":
    V = App.Vector

    def box(dx, dy, dz, center=True):
        s = Part.makeBox(dx, dy, dz)
        if center:
            s.translate(V(-dx / 2, -dy / 2, -dz / 2))
        return s

    def cyl(r, h, axis="x", center=True):
        d = V(*AX[axis])
        s = Part.makeCylinder(r, h, V(0, 0, 0), d)
        if center:
            s.translate(d * (-h / 2))
        return s

    def cut(a, *bs):
        for b in bs:
            a = a.cut(b)
        return a

    def fuse(a, *bs):
        for b in bs:
            a = a.fuse(b)
        return a.removeSplitter() if hasattr(a, "removeSplitter") else a

    def common(a, b):
        return a.common(b)

    def move(s, x=0, y=0, z=0):
        s = s.copy()
        s.translate(V(x, y, z))
        return s

    def rot(s, axis, deg, cx=0, cy=0, cz=0):
        s = s.copy()
        s.rotate(V(cx, cy, cz), V(*AX[axis]), deg)
        return s

    def volume(s):
        return s.Volume

    def bbox(s):
        b = s.BoundBox
        return (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)

    def is_valid(s):
        return s.isValid()

    def export_step(shapes, path):
        Part.Compound(list(shapes)).exportStep(path)

    def polyprism(pts_yz, x0, x1):
        """YZ duzleminde kapali poligon (x=x0), +X yonunde x1'e kadar ekstrude."""
        vs = [V(x0, y, z) for y, z in pts_yz] + [V(x0, pts_yz[0][0], pts_yz[0][1])]
        f = Part.Face(Part.makePolygon(vs))
        return f.extrude(V(x1 - x0, 0, 0))

# ---------------------------------------------------------------- OCP
else:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Ax1, gp_Trsf, gp_Vec
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.TopoDS import TopoDS_Compound
    from OCP.BRep import BRep_Builder
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

    def _tr(s, t):
        return BRepBuilderAPI_Transform(s, t, True).Shape()

    def move(s, x=0, y=0, z=0):
        t = gp_Trsf(); t.SetTranslation(gp_Vec(x, y, z))
        return _tr(s, t)

    def rot(s, axis, deg, cx=0, cy=0, cz=0):
        t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(cx, cy, cz), gp_Dir(*AX[axis])), math.radians(deg))
        return _tr(s, t)

    def box(dx, dy, dz, center=True):
        s = BRepPrimAPI_MakeBox(dx, dy, dz).Shape()
        return move(s, -dx / 2, -dy / 2, -dz / 2) if center else s

    def cyl(r, h, axis="x", center=True):
        d = AX[axis]
        s = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*d)), r, h).Shape()
        return move(s, *[-c * h / 2 for c in d]) if center else s

    def cut(a, *bs):
        for b in bs:
            a = BRepAlgoAPI_Cut(a, b).Shape()
        return a

    def fuse(a, *bs):
        for b in bs:
            a = BRepAlgoAPI_Fuse(a, b).Shape()
        u = ShapeUpgrade_UnifySameDomain(a); u.Build()
        return u.Shape()

    def common(a, b):
        return BRepAlgoAPI_Common(a, b).Shape()

    def volume(s):
        p = GProp_GProps(); BRepGProp.VolumeProperties_s(s, p)
        return p.Mass()

    def bbox(s):
        b = Bnd_Box(); BRepBndLib.Add_s(s, b, False)
        b.SetGap(0.0)
        p, q = b.CornerMin(), b.CornerMax()
        return (p.X(), p.Y(), p.Z(), q.X(), q.Y(), q.Z())

    def is_valid(s):
        return BRepCheck_Analyzer(s).IsValid()

    def polyprism(pts_yz, x0, x1):
        """YZ duzleminde kapali poligon (x=x0), +X yonunde x1'e kadar ekstrude."""
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
        from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
        mp = BRepBuilderAPI_MakePolygon()
        for y, z in pts_yz:
            mp.Add(gp_Pnt(x0, y, z))
        mp.Close()
        face = BRepBuilderAPI_MakeFace(mp.Wire()).Face()
        return BRepPrimAPI_MakePrism(face, gp_Vec(x1 - x0, 0, 0)).Shape()

    def export_step(shapes, path):
        c = TopoDS_Compound(); bld = BRep_Builder(); bld.MakeCompound(c)
        for s in shapes:
            bld.Add(c, s)
        w = STEPControl_Writer(); w.Transfer(c, STEPControl_AsIs); w.Write(path)


# ---------------------------------------------------------------- ortak yardımcılar
def tube(ro, ri, h, axis="x", center=True):
    """İçi boş silindir (silindir gövdesi, burç, somun)."""
    return cut(cyl(ro, h, axis, center), cyl(ri, h + 2, axis, center))


def place(s, pos, rot_deg):
    """params.json instance yerleşimi: önce X, sonra Y, sonra Z dönüşü (lokal orijin etrafında), sonra öteleme."""
    rx, ry, rz = rot_deg
    if rx: s = rot(s, "x", rx)
    if ry: s = rot(s, "y", ry)
    if rz: s = rot(s, "z", rz)
    return move(s, *pos)


def gear_x(teeth, module, x0, x1, bore_d=0.0, phase_deg=0.0, cy=0.0, cz=0.0):
    """Duz disli (basitlestirilmis trapez dis), ekseni X, merkezi (cy, cz), x0..x1 genislik.
    phase_deg: bir disin ortasinin YZ duzleminde atan2(z, y) acisi.
    Pitch R = m*z/2, dis basi R+m, dis dibi R-1.25m. Ayni modullu iki disli, faz dogru verilirse
    (kinematics.gear_phase) birbirine girmeden kavrar."""
    R = module * teeth / 2.0
    ra, rf = R + module, R - 1.25 * module
    p = 2 * math.pi / teeth
    ph = math.radians(phase_deg)
    pts = []
    for k in range(teeth):
        t = ph + k * p
        for a, r in ((-0.30, rf), (-0.12, ra), (0.12, ra), (0.30, rf)):
            pts.append((cy + r * math.cos(t + a * p), cz + r * math.sin(t + a * p)))
    s = polyprism(pts, x0, x1)
    if bore_d > 0:
        b = move(cyl(bore_d / 2.0, (x1 - x0) + 2, "x", center=False), x0 - 1, cy, cz)
        s = cut(s, b)
    return s
