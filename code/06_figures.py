"""Step 6: figures for the page (img/*.jpg), the blog (release/blog/b_*.png, 1800 px) and the paper (release/paper/f_*.png, 300 dpi)."""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd
import matplotlib.patheffects as pe
from PIL import Image
from figstyle import *
from names import N, NKEY, LIB_MAIN, CON_MAIN, LABOUR

R = jload(f"{DATA}/results.json")
S = pd.read_csv(f"{DATA}/streets.csv", keep_default_na=False)
V = pd.read_csv(f"{DATA}/towns.csv")
BLOG, PAPERD = f"{ROOT}/release/blog", f"{ROOT}/release/paper"
HALO = [pe.withStroke(linewidth=3, foreground=PAPER)]


def out(fig, name, dpi=300):
    fig.savefig(f"{WORK}/{name}.png", dpi=dpi, facecolor=PAPER)
    plt.close(fig)
    im = Image.open(f"{WORK}/{name}.png").convert("RGB")
    im.resize((1600, round(im.size[1] * 1600 / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=84, optimize=True)
    im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    im.save(f"{PAPERD}/f_{name}.png", optimize=True)
    os.remove(f"{WORK}/{name}.png")


S["X"], S["Y"] = proj(S.lon.values, S.lat.values)
# ---------- 1. map: Liberal and Conservative names
fig = plt.figure(figsize=(10, 8.6), facecolor=PAPER)
for i, (keys, col, title) in enumerate(((LIB_MAIN, LIB, "Liberal heroes: Gladstone, Cobden, Bright, Palmerston"), (CON_MAIN, CON, "Conservative: Beaconsfield and Disraeli"))):
    ax = fig.add_axes([0.01 + 0.495 * i, 0.045, 0.48, 0.84])
    uk_base(ax)
    g = S[S.key.isin(keys) & (S["class"] == "main") & (S.nation != "Northern Ireland")]
    ax.scatter(g.X, g.Y, s=9, c=col, edgecolors="white", linewidths=0.35, zorder=3)
    ax.set_xlim(-10000, 660000); ax.set_ylim(0, 1000000)
    ax.text(0.03, 0.985, title, transform=ax.transAxes, fontsize=12.5, weight="semibold", color=col, va="top")
    ax.text(0.03, 0.95, f"{len(g):,} streets", transform=ax.transAxes, fontsize=11, family=MONO, color=MUT, va="top")
fig.text(0.02, 0.965, "Political street names in Great Britain", fontsize=17, weight="semibold", color=INKC)
fig.text(0.02, 0.012, "OpenStreetMap streets, pieces within 150 m joined. Beaconsfield streets within 25 km of Beaconsfield, Bucks left out.", fontsize=9, color=MUT)
out(fig, "map")

# ---------- 2. names: counts and the co-location test
D = pd.read_csv(f"{DATA}/name_diagnostics.csv")
show = ["gladstone", "cobden", "palmerston", "bright", "beaconsfield", "disraeli", "peel", "rosebery", "salisbury", "balfour", "hartington", "granville",
        "chamberlain", "churchill", "baldwin", "derby", "melbourne", "russell", "liverpool", "wilson", "victoria", "nelson"]
D = D.set_index("key").loc[show].reset_index()
colr = lambda r: LIB if (r["class"] == "main" and r.party == "LIB") else CON if (r["class"] == "main") else ("#B9A06B" if r["class"] == "test" else NEU)
fig = plt.figure(figsize=(11, 7.4), facecolor=PAPER)
ax = fig.add_axes([0.17, 0.1, 0.36, 0.78]); ax2 = fig.add_axes([0.6, 0.1, 0.37, 0.78])
y = np.arange(len(D))[::-1]
ax.barh(y, D.streets, color=[colr(r) for _, r in D.iterrows()], height=0.7)
ax.set_yticks(y); ax.set_yticklabels(D.label, fontsize=10.5)
for yy, v in zip(y, D.streets):
    ax.text(v + 15, yy, f"{v:,}", va="center", fontsize=8.5, family=MONO, color=MUT)
ax.set_xlabel("streets"); ax.set_title("How many streets", loc="left", fontsize=12.5, weight="semibold")
ax2.barh(y, D.coloc400_pc, color=[colr(r) for _, r in D.iterrows()], height=0.7)
g = float(D.loc[D.key == "gladstone", "coloc400_pc"].iloc[0])
ax2.axvline(g / 2, color=INKC, lw=1, ls=(0, (3, 2)))
ax2.text(g / 2 + 0.6, 2.0, "half the Gladstone\nrate: the pass mark\nfor tested names", fontsize=8.5, color=INKC, va="center")
ax2.set_yticks(y); ax2.set_yticklabels([])
ax2.set_xlabel("% with another party street within 400 m")
ax2.set_title("Do they sit with other statesmen?", loc="left", fontsize=12.5, weight="semibold")
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=LIB, label="Liberal (main set)"), Patch(color=CON, label="Conservative (main set)"), Patch(color="#B9A06B", label="tested name"),
                    Patch(color=NEU, label="set aside or non-party")], loc="upper left", ncol=4, frameon=False, fontsize=10, bbox_to_anchor=(0.02, 0.995))
out(fig, "names")

# ---------- 3. towns: vote and names
T = V[(V.n_party > 0) & V.v_lib2.notna()].copy()
fig = plt.figure(figsize=(10, 7), facecolor=PAPER)
ax = fig.add_axes([0.09, 0.11, 0.86, 0.76])
ax.scatter(100 * T.v_lib2, 100 * T.lib_name_share, s=12 + 9 * T.n_party, c=LIB, alpha=0.45, edgecolors=INKC, linewidths=0.4)
# binned means (streets pooled), and the main model's slope through the mean
P = T.copy(); P["bin"] = pd.cut(100 * P.v_lib2, [0, 40, 45, 50, 55, 60, 65, 101])
bm = P.groupby("bin").apply(lambda g: pd.Series({"x": 100 * np.average(g.v_lib2, weights=g.n_party), "y": 100 * g.n_lib.sum() / g.n_party.sum(), "n": g.n_party.sum()}))
ax.plot(bm.x, bm.y, "o-", color=INKC, ms=7, lw=1.2, label="streets pooled in bins of vote share")
b = R["main"]["b"] * 10
xm = 100 * np.average(T.v_lib2, weights=T.n_party); ym = 100 * T.n_lib.sum() / T.n_party.sum()
xx = np.array([25, 85]); ax.plot(xx, ym + b * (xx - xm), color=LIB, lw=2.2, label=f"main model: +{R['effect']['pp_per10']:.1f} points per 10 points of vote")
for t in ("Blackburn", "Leicester", "Liverpool", "London", "Gateshead", "Dundee", "Bolton", "Birmingham"):
    r = T[T.name == t]
    if len(r):
        ax.annotate(t, (100 * r.v_lib2.iloc[0], 100 * r.lib_name_share.iloc[0]), xytext=(6, -12 if t in ("London", "Gateshead") else 5), textcoords="offset points", fontsize=9.5, color=INKC, path_effects=HALO)
ax.set_xlim(18, 102); ax.set_ylim(-4, 104)
ax.set_xlabel("Liberal share of the two-party vote, general elections 1868 to 1900 (%)")
ax.set_ylabel("Liberal share of the town's party street names (%)")
ax.legend(loc="lower right", frameon=False, fontsize=10)
fig.text(0.02, 0.95, f"{R['sample']['towns']} towns, {R['sample']['streets']} party streets: bubbles sized by streets", fontsize=13.5, weight="semibold", color=INKC)
out(fig, "towns")

# ---------- 4. coefficient plot
rows = [("Main model", R["main"])]
rows += [(a["label"], a) for a in R["alt"] if "logit" not in a["label"] and "seats" not in a["label"] and "Town-level OLS" not in a["label"]]
rows += [("[seats won share]", R["alt_by"]["Liberal share of seats won 1868 to 1900 (uncontested included)"])]
rows += [(a["label"], a) for a in R["robust"]]
rows += [("Placebo: " + a["label"], a) for a in R["placebo_later"][1:3]]
short = {"Vote 1868 to 1880 only": "Vote 1868 to 1880 only", "Extended name set (Rosebery, Granville; Salisbury, Balfour, Hartington, Chamberlain)": "Extended name set"}
fig = plt.figure(figsize=(10, 9.5), facecolor=PAPER)
ax = fig.add_axes([0.45, 0.08, 0.51, 0.85])
y = np.arange(len(rows))[::-1]
for yy, (lab, a) in zip(y, rows):
    c = LIB if lab == "Main model" else (NEU if lab.startswith("Placebo") else INKC)
    ax.plot([100 * a["lo"], 100 * a["hi"]], [yy, yy], color=c, lw=1.6)
    ax.plot(100 * a["b"], yy, "o", color=c, ms=6.5)
ax.axvline(0, color=MUT, lw=0.8)
ax.set_yticks(y); ax.set_yticklabels([short.get(l, l).replace("Liberal share of all votes", "Liberal vote").replace("Labour share of all votes", "Labour vote").replace("[seats won share]", "Share of seats the Liberals won") for l, _ in rows], fontsize=9.5)
ax.set_xlabel("points of Liberal names per 10 points of Liberal vote (95% CI)")
ax.grid(axis="x", color=GRID, lw=0.6)
fig.text(0.02, 0.965, "One modest association, many checks", fontsize=15, weight="semibold", color=INKC)
out(fig, "checks")

# ---------- 5. the clock: within-town distance rank
TM = R["timing"]
order = ["Napoleonic 1793 to 1815", "Crimea 1854 to 1856", "Cobden, Bright, Palmerston", "Gladstone", "Beaconsfield and Disraeli", "Boer War 1899 to 1902", "First World War", "Labour names", "Second World War"]
lab = {"Napoleonic 1793 to 1815": "Napoleonic battles (1793 to 1815)", "Crimea 1854 to 1856": "Crimean battles (1854 to 1856)", "Boer War 1899 to 1902": "Boer War battles (1899 to 1902)",
       "First World War": "First World War battles", "Second World War": "Second World War battles", "Labour names": "Labour: Keir Hardie, Lansbury, Attlee, Bevan"}
fig = plt.figure(figsize=(10, 6.4), facecolor=PAPER)
ax = fig.add_axes([0.36, 0.12, 0.6, 0.74])
order = [o for o in order if o in TM]
y = np.arange(len(order))[::-1]
for yy, o in zip(y, order):
    t = TM[o]; c = LIB if o in ("Gladstone", "Cobden, Bright, Palmerston") else CON if o.startswith("Beac") else LAB if o.startswith("Labour") else NEU
    ax.plot([t["lo"], t["hi"]], [yy, yy], color=c, lw=2); ax.plot(t["mean"], yy, "o", color=c, ms=8)
    ax.text(0.79, yy, f"n = {t['n']}", fontsize=9, family=MONO, color=MUT, va="center")
ax.set_yticks(y); ax.set_yticklabels([lab.get(o, o) for o in order], fontsize=10.5)
ax.axvline(0.5, color=MUT, lw=0.8, ls=(0, (3, 2)))
ax.set_xlim(0.38, 0.84); ax.set_xlabel("mean rank of distance from the town centre within each town (0 centre, 1 edge), 95% CI")
fig.text(0.02, 0.93, "Gladstone streets sit where late Victorian towns were growing", fontsize=14.5, weight="semibold", color=INKC)
out(fig, "clock")

# ---------- 6. Labour names
lab = S[S.key.isin(LABOUR) & (S.nation != "Northern Ireland")]
fig = plt.figure(figsize=(10, 8.5), facecolor=PAPER)
ax = fig.add_axes([0.0, 0.03, 0.5, 0.88]); uk_base(ax)
ax.scatter(lab.X, lab.Y, s=12, c=LAB, edgecolors="white", linewidths=0.4, zorder=3)
ax.set_xlim(-10000, 660000); ax.set_ylim(0, 1000000)
ax.text(0.03, 0.98, f"{len(lab)} streets named after\nLabour leaders", transform=ax.transAxes, fontsize=12, color=LAB, va="top", weight="semibold")
ax2 = fig.add_axes([0.6, 0.14, 0.36, 0.66])
H = V[V.p_lab.notna()].copy(); H["any"] = H.n_labour > 0
H["bin"] = pd.qcut(100 * H.p_lab, 4)
bm = H.groupby("bin").agg(x=("p_lab", lambda s: 100 * s.mean()), y=("any", lambda s: 100 * s.mean()), n=("any", "size"))
ax2.bar(range(len(bm)), bm.y, color=LAB, alpha=0.85)
ax2.set_xticks(range(len(bm))); ax2.set_xticklabels([f"{max(0, iv.left):.0f} to {iv.right:.0f}%" for iv in bm.index], fontsize=9.5)
ax2.set_xlabel("Labour share of the vote 1945 to 1970 (quarters of towns)")
ax2.set_ylabel("% of towns with a Labour-named street")
for i, (v, n) in enumerate(zip(bm.y, bm.n)):
    ax2.text(i, v + 0.6, f"{v:.0f}%", ha="center", fontsize=9.5, family=MONO)
fig.text(0.02, 0.95, "Keir Hardie, Lansbury, Attlee, Bevan: names of the Labour era", fontsize=14, weight="semibold", color=INKC)
out(fig, "labour")
print(sorted(os.listdir(BLOG)), sorted(os.listdir(PAPERD)))
