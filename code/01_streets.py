"""Step 1: OSM features -> commemorative streets. Keeps road highway values only, matches each name against the name table
(whole words, specific multi-word names first), joins the pieces of one street (same normalised name, first points chaining
within 150 m; 600 m kept as a sensitivity grouping), and adds county, nation and region.
Writes WORK/ways.csv and WORK/streets_raw.csv."""
import pandas as pd, numpy as np
import geopandas as gpd
from common import *
from names import N, NKEY

ROADS = {"trunk", "primary", "secondary", "tertiary", "trunk_link", "primary_link", "secondary_link", "tertiary_link", "unclassified",
         "residential", "living_street", "pedestrian", "service", "road", "busway"}
rows, hwc = [], {}
for r in read_tsv(STREETS):
    hwc[r["hw"]] = hwc.get(r["hw"], 0) + 1
    lon, lat = point(r["p"])
    if lon is None or not r["name"] or r["hw"] not in ROADS:
        continue
    rows.append({"way": r["w"].rsplit("/", 1)[-1], "kind": r["w"].split("/")[-2], "hw": r["hw"], "name": r["name"].strip(), "lon": lon, "lat": lat})
W = pd.DataFrame(rows)
print("rows", sum(hwc.values()), "kept as roads", len(W), "kinds", W.kind.value_counts().to_dict())
FIRST = ["mandela", "badenpowell", "keirhardie", "aneurinbevan", "ramsaymacdonald", "lloydgeorge"]
ORDER = FIRST + [n[0] for n in N if n[0] not in FIRST]
RX = [(k, re.compile(r"(?<![a-z])(?:" + NKEY[k][2] + r")(?![a-z])")) for k in ORDER]


def match(name):
    s = name.lower().replace("’", "'")
    for k, rx in RX:
        if rx.search(s):
            return k
    return ""


W["key"] = W.name.apply(match)
print("not matched", (W.key == "").sum(), W[W.key == ""].name.value_counts().head(15).to_dict())
W = W[W.key != ""].copy()
x, y = bng(W.lon.values, W.lat.values)
W["x"], W["y"] = x, y
C = gpd.read_file(f"{GEO}/counties_uk.geojson").to_crs(27700)
P = gpd.GeoDataFrame(W[["way"]], geometry=gpd.points_from_xy(W.x, W.y), crs=27700)
J = gpd.sjoin_nearest(P, C[["county", "nation", "geometry"]], how="left", max_distance=3000)
J = J[~J.index.duplicated()]
W["county"], W["nation"] = J["county"].values, J["nation"].values
W = W[W.nation.notna()].copy()
W["region"] = [region_of(c, n) for c, n in zip(W.county, W.nation)]
W["norm"] = (W.name.str.lower().str.replace(r"\(.*?\)", "", regex=True).str.replace(r"[^a-z ]", " ", regex=True)
             .str.replace(r"\bst\b", "street", regex=True).str.replace(r"\brd\b", "road", regex=True)
             .str.replace(r"\bave\b", "avenue", regex=True).str.replace(r"^back ", "", regex=True).str.split().str.join(" "))
# "Back Gladstone Street" (the back lane of a terrace) is joined with Gladstone Street when within 150 m
W["gid"] = merge_close(W, 150)
W["gid600"] = merge_close(W, 600)
W.to_csv(f"{WORK}/ways.csv", index=False)
S = W.groupby("gid").agg(name=("name", lambda s: s.value_counts().index[0]), norm=("norm", "first"), key=("key", "first"),
                         lon=("lon", "mean"), lat=("lat", "mean"), x=("x", "mean"), y=("y", "mean"), n_ways=("way", "size"),
                         ways=("way", lambda s: ";".join(s)), hws=("hw", lambda s: ";".join(sorted(set(s)))),
                         county=("county", "first"), nation=("nation", "first"), region=("region", "first"),
                         gid600=("gid600", "first")).reset_index()
S["suffix"] = S.norm.str.split().str[-1]
S.to_csv(f"{WORK}/streets_raw.csv", index=False)
print("ways", len(W), "streets (150 m)", len(S), "streets (600 m)", S.gid600.nunique())
print(S.key.value_counts().to_string())
