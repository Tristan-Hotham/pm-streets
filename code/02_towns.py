"""Step 2: towns, name diagnostics and the street table.
- Each street goes to the town (Wikidata town or city of 3,000 or more) with the smallest distance / radius, where the
  radius is r = max(3, 1.5 * sqrt(pop / 10,000)) km and the distance must be within r; Greater London is London.
  Radii x0.7 and x1.4 are kept for the sensitivity checks.
- Place test: distance from each street to the nearest Wikidata settlement (any type) whose name contains the word.
- Co-location test: distance from each street to the nearest main-set party street of another name.
- Battle streets (battle-streets study) get the same town assignment, as a measure of each town's Victorian street stock.
Writes WORK/streets.csv, WORK/towns_all.csv, WORK/battle.csv, data/name_diagnostics.csv."""
import pandas as pd, numpy as np
from scipy.spatial import cKDTree
from common import *
from names import N, NKEY, PARTY_NAMES

S = pd.read_csv(f"{WORK}/streets_raw.csv", keep_default_na=False, dtype={"ways": str})
T = settlements(3000)
T["x"], T["y"] = bng(T.lon.values, T.lat.values)
T["r"] = np.maximum(3000, 1500 * np.sqrt(T["pop"] / 1e4))
TREE = cKDTree(T[["x", "y"]].values)
LON = T.index[T.name == "London"][0]


def assign(x, y, county, mult=1.0):
    """index into T of each point's town (or -1): the 40 nearest towns are scored by distance / radius"""
    dist, j = TREE.query(np.c_[x, y], k=40)
    score = dist / (T.r.values[j] * mult)
    b = score.argmin(axis=1)
    out = np.where(score[np.arange(len(x)), b] <= 1, j[np.arange(len(x)), b], -1)
    out[np.asarray(county) == "Greater London"] = LON
    return out


for m, col in ((1.0, "town"), (0.7, "town_s"), (1.4, "town_l")):
    ix = assign(S.x.values, S.y.values, S.county.values, m)
    S[col] = np.where(ix >= 0, T.qid.values[np.maximum(ix, 0)], "")
ix = assign(S.x.values, S.y.values, S.county.values)
S["town_name"] = np.where(ix >= 0, T.name.values[np.maximum(ix, 0)], "")
S["town_km"] = np.where(ix >= 0, np.hypot(S.x - T.x.values[np.maximum(ix, 0)], S.y - T.y.values[np.maximum(ix, 0)]) / 1000, np.nan)
print("streets in a town", (S.town != "").mean())

# place test: nearest settlement of any type whose label contains the word
d = pd.read_csv(SETTLE, sep="\t", dtype=str, quoting=3)
d.columns = [c.lstrip("?") for c in d.columns]
d["pl"] = d.pl.str.replace(r'^"|"(@\w+)?$', "", regex=True)
xy = d.coord.str.extract(r"POINT\(([-\d.]+) ([-\d.]+)\)").astype(float)
d["lon"], d["lat"] = xy[0], xy[1]
d = d.dropna(subset=["lon"]).drop_duplicates(["pl", "lon", "lat"])
d = d[~d.pl.str.contains(r"\d|,", regex=True)]
d["x"], d["y"] = bng(d.lon.values, d.lat.values)
S["place"] = ""; S["place_km"] = np.nan
for n in N:
    k = n[0]
    rx = r"(?<![A-Za-z])(?:" + n[2] + r")(?![A-Za-z])"
    pl = d[d.pl.str.lower().str.contains(rx, regex=True)]
    m = S.key == k
    if not len(pl) or not m.any():
        continue
    dist, i = cKDTree(pl[["x", "y"]].values).query(S.loc[m, ["x", "y"]].values)
    S.loc[m, "place"] = pl.pl.values[i]
    S.loc[m, "place_km"] = dist / 1000
# co-location: nearest main-set party street of another name
P = S[S.key.isin(PARTY_NAMES)]
S["coloc_m"] = np.nan
for k in S.key.unique():
    other = P[P.key != k]
    dist, _ = cKDTree(other[["x", "y"]].values).query(S.loc[S.key == k, ["x", "y"]].values)
    S.loc[S.key == k, "coloc_m"] = dist
# Beaconsfield rule (pre-set): within 25 km of the town of Beaconsfield, Buckinghamshire, possibly a route name
b = T[T.name == "Beaconsfield"].iloc[0]
S["route_flag"] = (S.key == "beaconsfield") & (np.hypot(S.x - b.x, S.y - b.y) <= 25000)
print("Beaconsfield streets near Beaconsfield, Bucks:", int(S.route_flag.sum()))

# diagnostics for every name
G = S[(S.key == "gladstone")]
g_rate = float((G.coloc_m <= 400).mean())
rows = []
for n in N:
    s = S[S.key == n[0]]
    if not len(s):
        continue
    co = float((s.coloc_m <= 400).mean()); pl10 = float((s.place_km <= 10).mean())
    rows.append({"key": n[0], "label": n[1], "party": n[3], "class": n[4], "streets": int(len(s)), "coloc400_pc": 100 * co,
                 "coloc_ratio_to_gladstone": co / g_rate if n[0] != "gladstone" else 1.0, "near_place10_pc": 100 * pl10,
                 "traditional_pc": 100 * float(s.suffix.isin(["street", "road", "terrace", "place", "row", "square", "grove", "crescent", "avenue", "villas"]).mean()),
                 "passes": bool(co >= 0.5 * g_rate and pl10 < 0.25) if n[4] == "test" else None})
D = pd.DataFrame(rows)
D.round(3).to_csv(f"{DATA}/name_diagnostics.csv", index=False)
print("Gladstone co-location rate", round(g_rate, 3))
print(D.to_string())
S.to_csv(f"{WORK}/streets.csv", index=False)
T.to_csv(f"{WORK}/towns_all.csv", index=False)
# battle streets with the same town assignment
B = pd.read_csv(BATTLE, keep_default_na=False)
bx, by = bng(B.lon.values, B.lat.values)
ix = assign(bx, by, B.county.values)
B["town"] = np.where(ix >= 0, T.qid.values[np.maximum(ix, 0)], "")
B[["id", "battle", "year", "era", "flag", "clock", "style", "lon", "lat", "county", "town"]].to_csv(f"{WORK}/battle.csv", index=False)
print("battle streets", len(B), "in towns", (B.town != "").sum())
