"""House style for the static figures: light paper, Source Serif text, IBM Plex Mono numbers, party colours."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as stransform
from common import *

for f in ("SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
import dataclasses                          # the Semibold file reports weight 400; mark it so weight="semibold" finds it
fm.fontManager.ttflist = [dataclasses.replace(e, weight=600) if e.fname.endswith("SourceSerif4-Semibold.ttf") else
                          dataclasses.replace(e, style="italic") if e.fname.endswith("SourceSerif4-It.ttf") else e for e in fm.fontManager.ttflist]
fm.fontManager._findfont_cached.cache_clear() if hasattr(fm.fontManager._findfont_cached, "cache_clear") else None
SERIF = "Source Serif 4"
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": SERIF, "font.size": 12, "axes.edgecolor": "#8A8170", "axes.labelcolor": "#2A2620", "xtick.color": "#5E574B",
                     "ytick.color": "#5E574B", "axes.facecolor": "none", "axes.unicode_minus": False, "axes.spines.top": False, "axes.spines.right": False})
PAPER, INKC, MUT, GRID, LAND, SEA = "#FBF8F1", "#2A2620", "#6E665A", "#E6DFD0", "#F1ECE1", "#FBF8F1"
LIB, CON, LAB, NEU, ROY = "#E08A1E", "#2D5C9E", "#C2332B", "#9A9283", "#7A5C8E"
COUNTIES = jload(f"{GEO}/counties_uk.geojson")["features"]
TR = Transformer.from_crs(4326, 27700, always_xy=True)
proj = lambda lon, lat: TR.transform(lon, lat)


def uk_base(ax, lw=0.35):
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    for ft in COUNTIES:
        g = stransform(lambda x, y, z=None: TR.transform(x, y), shape(ft["geometry"]))
        polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
        for p in polys:
            verts, codes = [], []
            for ring in [p.exterior] + list(p.interiors):
                cs = np.asarray(ring.coords)
                verts += cs.tolist(); codes += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), fc=LAND, ec="#CFC6B4", lw=lw, zorder=1))
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
