"""render.py - FreeCAD olmadan montaj önizlemesi (OCP tessellation + matplotlib).
Kullanım: python3 checks/render.py [--phase N]  -> out/preview_iso.png, out/preview_front.png, out/preview_top.png
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "assembly")); sys.path.insert(0, os.path.join(ROOT, "lib"))
from assemble import assemble  # noqa
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location

COL = {"A10": "#7a7f87", "A20": "#3b6ea5", "A30": "#d08c2b", "A40": "#8a5aa8",
       "A50": "#c0392b", "A60": "#2e8b57", "A70": "#e3c44a", "A80": "#5f9ea0"}


def tris(shape, defl=8.0):
    BRepMesh_IncrementalMesh(shape, defl, False, 0.5, True)
    out = []
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face(ex.Current()); loc = TopLoc_Location()
        t = BRep_Tool.Triangulation_s(f, loc)
        if t is not None:
            tr = loc.Transformation()
            pts = [t.Node(i).Transformed(tr) for i in range(1, t.NbNodes() + 1)]
            P = np.array([[p.X(), p.Y(), p.Z()] for p in pts])
            for i in range(1, t.NbTriangles() + 1):
                a, b, c = t.Triangle(i).Get()
                out.append(P[[a - 1, b - 1, c - 1]])
        ex.Next()
    return out


def main():
    phase = int(sys.argv[sys.argv.index("--phase") + 1]) if "--phase" in sys.argv else None
    placed, report, P, B = assemble(phase)
    polys, cols = [], []
    hide = set(sys.argv[sys.argv.index("--hide") + 1].split(",")) if "--hide" in sys.argv else set()
    tag = "_" + "-".join(sorted(hide)) if hide else ""
    for name, (pid, gid, shp) in placed.items():
        if gid in hide: continue
        t = tris(shp); polys += t; cols += [COL.get(gid, "#999")] * len(t)
    from matplotlib.colors import to_rgb
    T = np.array(polys); n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)
    L = np.array([-0.4, -0.6, 0.7]); L /= np.linalg.norm(L)
    k = 0.35 + 0.65 * np.abs(n @ L)
    shaded = np.array([to_rgb(c) for c in cols]) * k[:, None]
    allp = np.concatenate(polys)
    mn, mx = allp.min(0), allp.max(0)
    for view, (el, az) in {"iso": (22, -55), "front": (0, -90), "top": (90, -90)}.items():
        fig = plt.figure(figsize=(14, 8), dpi=110); ax = fig.add_subplot(111, projection="3d")
        pc = Poly3DCollection(polys, edgecolors="none", linewidths=0, alpha=1.0)
        pc.set_facecolor(shaded); ax.add_collection3d(pc)
        for i, s in enumerate("xyz"):
            getattr(ax, f"set_{s}lim")(mn[i], mx[i])
        ax.set_box_aspect(tuple(mx - mn), zoom=1.0); ax.view_init(el, az); ax.set_axis_off()
        ax.set_title(f"HPDC-400 dijital ikiz - {view} ({len(placed)} instance)")
        fig.tight_layout(); fig.savefig(os.path.join(ROOT, "out", f"preview_{view}{tag}.png")); plt.close(fig)
    print("render ok", len(polys), "ucgen")


if __name__ == "__main__":
    main()
