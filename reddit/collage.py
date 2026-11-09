"""Reddit collage (2400 px wide, light paper), the social card header.png (1200 x 630) and a looping GIF of the names
appearing one by one. Every number comes from data/results.json. Run from the study folder: python3 reddit/collage.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import pandas as pd
import matplotlib.patheffects as pe
from PIL import Image
from figstyle import *
from names import LIB_MAIN, CON_MAIN, LABOUR

R = jload(f"{DATA}/results.json")
S = pd.read_csv(f"{DATA}/streets.csv", keep_default_na=False)
S = S[S.nation != "Northern Ireland"]
S["X"], S["Y"] = proj(S.lon.values, S.lat.values)
V = pd.read_csv(f"{DATA}/towns.csv")
OUT = os.path.join(ROOT, "reddit")
HALO = [pe.withStroke(linewidth=4, foreground=PAPER)]
lib = S[S.key.isin(LIB_MAIN) & (S["class"] == "main")]; con = S[S.key.isin(CON_MAIN) & (S["class"] == "main")]; lab = S[S.key.isin(LABOUR)]

def gb(ax):
    uk_base(ax, lw=0.3); ax.set_xlim(-10000, 660000); ax.set_ylim(0, 990000)

# ---------------- collage
fig = plt.figure(figsize=(16, 11.5), facecolor=PAPER)
fig.text(0.03, 0.955, "Gladstone Road or Disraeli Street?", fontsize=34, weight="semibold", color=INKC)
fig.text(0.03, 0.918, f"Every UK street named after a Victorian statesman: {R['count']['gladstone']:,} Gladstones, {R['count']['beaconsfield']:,} Beaconsfields, {R['count']['disraeli']} Disraelis. "
         f"{R['main_set']['lib_pc']:.0f}% of party street names are Liberal.", fontsize=15.5, color=MUT)
ax = fig.add_axes([0.0, 0.07, 0.3, 0.72]); gb(ax)
ax.scatter(lib.X, lib.Y, s=10, c=LIB, edgecolors="white", linewidths=0.3, zorder=3)
fig.text(0.04, 0.86, f"Orange: Liberal heroes, {len(lib):,} streets in GB", fontsize=15, color=LIB, weight="semibold", va="top")
fig.text(0.04, 0.83, "Gladstone, Cobden, John Bright, Palmerston", fontsize=11.5, color=MUT, va="top")
ax = fig.add_axes([0.27, 0.07, 0.3, 0.72]); gb(ax)
ax.scatter(con.X, con.Y, s=10, c=CON, edgecolors="white", linewidths=0.3, zorder=3)
fig.text(0.31, 0.86, f"Blue: Conservative, {len(con):,} streets in GB", fontsize=15, color=CON, weight="semibold", va="top")
fig.text(0.31, 0.83, "Beaconsfield (Disraeli's title) and Disraeli", fontsize=11.5, color=MUT, va="top")
# scatter of towns
T = V[(V.n_party > 0) & V.v_lib2.notna()]
ax = fig.add_axes([0.62, 0.55, 0.35, 0.3])
ax.scatter(100 * T.v_lib2, 100 * T.lib_name_share, s=8 + 6 * T.n_party, c=LIB, alpha=0.45, edgecolors=INKC, linewidths=0.3)
b = R["main"]["b"] * 10; xm = 100 * np.average(T.v_lib2, weights=T.n_party); ym = 100 * T.n_lib.sum() / T.n_party.sum()
xx = np.array([25, 85]); ax.plot(xx, ym + b * (xx - xm), color=INKC, lw=2)
ax.text(86, ym + b * (86 - xm), "model\nslope", fontsize=10, color=INKC, va="center")
ax.text(99, 8, "bubble = a town,\nsized by its party streets", fontsize=10, color=MUT, ha="right")
ax.set_xlabel("Liberal share of the vote 1868 to 1900 (%)", fontsize=11); ax.set_ylabel("Liberal share of\nparty street names (%)", fontsize=11)
ax.set_title(f"Liberal towns named a little more after Liberals:\n+{R['effect']['pp_per10']:.1f} points per 10 points of vote (95% CI {R['effect']['lo_pp']:.1f} to {R['effect']['hi_pp']:.1f}), {R['sample']['towns']} towns",
             loc="left", fontsize=12.5, color=INKC)
# clock
TM = R["timing"]; order = [("Crimea 1854 to 1856", "Crimean battles", NEU), ("Gladstone", "Gladstone", LIB), ("Beaconsfield and Disraeli", "Beaconsfield, Disraeli", CON),
                            ("Boer War 1899 to 1902", "Boer War battles", NEU), ("First World War", "First World War battles", NEU), ("Labour names", "Labour leaders", LAB)]
ax = fig.add_axes([0.75, 0.12, 0.22, 0.3])
for yy, (k, l, c) in zip(range(len(order))[::-1], order):
    t = TM[k]; ax.plot([t["lo"], t["hi"]], [yy, yy], color=c, lw=2.5); ax.plot(t["mean"], yy, "o", color=c, ms=9)
ax.set_yticks(range(len(order))[::-1]); ax.set_yticklabels([o[1] for o in order], fontsize=11.5)
ax.set_xlabel("rank of distance within town\n(0 centre, 1 edge)", fontsize=11)
ax.set_title("When: Gladstone streets sit between\nCrimean and Boer War battle streets", loc="left", fontsize=12.5, color=INKC, x=-0.55)
fig.text(0.03, 0.025, f"Data: OpenStreetMap contributors (ODbL); UK Parliament election results (Open Parliament Licence); Wikidata. Streets within 150 m joined; models compare towns within regions. "
         "Correlational.  maps.tristanhotham.com/pm-streets", fontsize=10.5, color=MUT)
fig.savefig(f"{OUT}/pm_streets_collage.png", dpi=170, facecolor=PAPER); plt.close(fig)

# ---------------- header 1200 x 630
fig = plt.figure(figsize=(12, 6.3), facecolor=PAPER)
fig.text(0.05, 0.74, "Gladstone Road", fontsize=46, weight="semibold", color=LIB)
fig.text(0.05, 0.6, "or Disraeli Street?", fontsize=46, weight="semibold", color=CON)
fig.text(0.05, 0.47, "Victorian street names and the party\nthe town voted for", fontsize=19, color=INKC, va="top")
fig.text(0.05, 0.22, f"{R['count']['gladstone']:,} Gladstones   {R['count']['beaconsfield']:,} Beaconsfields   {R['count']['disraeli']} Disraelis", fontsize=15, family=MONO, color=MUT)
fig.text(0.05, 0.08, "Dr Tristan Hotham · Independent researcher · 2026", fontsize=12, color=MUT)
ax = fig.add_axes([0.6, 0.02, 0.38, 0.96]); gb(ax)
ax.scatter(lib.X, lib.Y, s=5, c=LIB, edgecolors="none", zorder=3); ax.scatter(con.X, con.Y, s=6, c=CON, edgecolors="none", zorder=4)
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=PAPER); plt.close(fig)

# ---------------- GIF: the names arrive one by one
frames = []
steps = [("gladstone", "Gladstone", LIB), ("cobden", "Cobden", LIB), ("palmerston", "Palmerston", LIB), ("bright", "John Bright", LIB),
         ("beaconsfield", "Beaconsfield", CON), ("disraeli", "Disraeli", CON), ("lab", "Keir Hardie, Lansbury, Attlee, Bevan", LAB)]
shown = []
for k, l, c in steps:
    g = lab if k == "lab" else S[(S.key == k) & (S["class"] == "main")]
    shown.append((g, c))
    fig = plt.figure(figsize=(6, 8), facecolor=PAPER); ax = fig.add_axes([0.0, 0.0, 1, 0.86]); gb(ax)
    for gg, cc in shown[:-1]:
        ax.scatter(gg.X, gg.Y, s=6, c=cc, alpha=0.35, edgecolors="none", zorder=3)
    ax.scatter(g.X, g.Y, s=12, c=c, edgecolors="white", linewidths=0.3, zorder=4)
    fig.text(0.05, 0.95, "Streets in Great Britain named after", fontsize=15, color=MUT)
    fig.text(0.05, 0.9, f"{l}: {len(g):,}", fontsize=19, color=c, weight="semibold")
    fig.savefig(f"{WORK}/gif.png", dpi=90, facecolor=PAPER); plt.close(fig)
    frames.append(Image.open(f"{WORK}/gif.png").convert("P", palette=Image.ADAPTIVE))
# clean final frame: all three groups at full strength with a full key, nothing faded
fig = plt.figure(figsize=(6, 8), facecolor=PAPER); ax = fig.add_axes([0.0, 0.0, 1, 0.86]); gb(ax)
for gg, cc, zz in ((lib, LIB, 3), (con, CON, 4), (lab, LAB, 5)):
    ax.scatter(gg.X, gg.Y, s=10, c=cc, edgecolors="white", linewidths=0.25, zorder=zz)
fig.text(0.05, 0.955, "Streets in Great Britain named after", fontsize=15, color=MUT)
fig.text(0.05, 0.915, f"Liberal heroes: {len(lib):,}", fontsize=14, color=LIB, weight="semibold")
fig.text(0.05, 0.88, f"Beaconsfield, Disraeli: {len(con):,}", fontsize=14, color=CON, weight="semibold")
fig.text(0.55, 0.915, f"Labour leaders: {len(lab):,}", fontsize=14, color=LAB, weight="semibold")
fig.savefig(f"{WORK}/gif.png", dpi=90, facecolor=PAPER); plt.close(fig)
frames.append(Image.open(f"{WORK}/gif.png").convert("P", palette=Image.ADAPTIVE))
frames[0].save(f"{OUT}/pm_streets.gif", save_all=True, append_images=frames[1:], duration=[1400] * (len(frames) - 1) + [2600], loop=0, optimize=True)
os.remove(f"{WORK}/gif.png")
for f in ("pm_streets_collage.png", "pm_streets.gif"):
    print(f, Image.open(f"{OUT}/{f}").size, os.path.getsize(f"{OUT}/{f}") // 1024, "KB")
print("header", Image.open(f"{ROOT}/header.png").size)
