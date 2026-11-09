"""Step 3: constituencies -> towns, and each town's vote.
A constituency is linked to a town when its name, after removing direction and division words (North, East, Central,
Burghs, Boroughs, District, Town, City of), is the town's name, or begins with the town's name followed by a ward name
(Birmingham Bordesley, Liverpool Everton, Glasgow Govan); a few names need an alias (code/aliases below). Where two
towns share a name, the one nearest the constituency's point is used (within 30 km). London: every constituency whose
point lies in Greater London. Northern Ireland, Ireland and university seats left out.
Votes: Liberal share = LIB / (LIB + CON + LU) of votes cast in the town's contested seats at an election, then averaged
over elections. Seats won: LIB seats / all seats returned (contested or not).
Writes WORK/links.csv (for review), WORK/town_votes.csv."""
import pandas as pd, numpy as np
import geopandas as gpd
from common import *

ALIAS = {"The Hartlepools": ["Hartlepool"], "Great Grimsby": ["Grimsby"], "Wycombe": ["High Wycombe"], "Burton": ["Burton upon Trent"],
         "Penryn and Falmouth": ["Falmouth"], "Tynemouth and North Shields": ["Tynemouth"], "Warwick and Leamington": ["Warwick", "Leamington Spa"],
         "Pembroke and Haverfordwest": ["Haverfordwest", "Pembroke"], "Weymouth and Melcombe Regis": ["Weymouth"], "Tunbridge": ["Royal Tunbridge Wells"],
         "New Shoreham": ["Shoreham-by-Sea"], "City of Chester": ["Chester"], "Aston Manor": ["Birmingham"], "Barrow in Furness": ["Barrow-in-Furness"],
         "Swansea Town": ["Swansea"], "Swansea District": ["Swansea"], "Newport (Monmouthshire)": ["Newport"], "Hull": ["Kingston upon Hull"],
         "Stockton": ["Stockton-on-Tees"], "Stratford-on-Avon": ["Stratford-upon-Avon"], "Leamington": ["Leamington Spa"],
         "Thirsk and Malton": [], "Peebles and Selkirk": [], "Ross and Cromarty": [], "Orkney and Shetland": [], "Elginshire and Nairnshire": [],
         "Clackmannanshire and Kinross-shire": [], "Radcliffe-cum-Farnworth": ["Radcliffe", "Farnworth"],
         "North Durham": [], "South Durham": [], "Mid Durham": [], "North West Durham": [], "South East Durham": []}  # county divisions, not the city
DIR = r"(north|south|east|west|central|mid|north east|north west|south east|south west|northern|southern|eastern|western)"
DROP = r"shire\b|riding|universit|county|division|valley|forest|isle of|lonsdale|hallamshire|middlesex|cleveland"
NORM = lambda s: re.sub(r"[^a-z ]", " ", s.lower().replace("-", " ").replace("'", "")).split()

c = pd.read_csv(f"{ELEC}/contests.csv", dtype={"election": str})
k = pd.read_csv(f"{ELEC}/candidates.csv", dtype={"election": str})
VIC = ["1868", "1874", "1880", "1885", "1886", "1892", "1895", "1900"]
LATE = ["1945", "1950", "1951", "1955", "1959", "1964", "1966", "1970"]
INTER = ["1918", "1922", "1923", "1924", "1929", "1931", "1935"]
c = c[c.election.isin(VIC + INTER + LATE) & c.nation.isin(["England", "Wales", "Scotland"])].copy()
c = c[~c.constituency.str.contains("Universit")]
T = pd.read_csv(f"{WORK}/towns_all.csv")
T["key"] = T.name.map(lambda s: " ".join(NORM(s)))
byname = {kk: g for kk, g in T.groupby("key")}
cx, cy = bng(c.lon.values, c.lat.values)
c["x"], c["y"] = cx, cy
GL = gpd.read_file(f"{GEO}/counties_uk.geojson")
GL = GL[GL.county == "Greater London"].to_crs(27700).geometry.iloc[0]
from shapely.geometry import Point
LONQ = T[T.name == "London"].qid.iloc[0]


def candidates(name):
    if name in ALIAS:
        return [" ".join(NORM(a)) for a in ALIAS[name]], "alias"
    if re.search(DROP, name.lower()):
        return [], ""
    if " and " in name:                          # two-town seats: Penryn and Falmouth, Nelson and Colne
        out = []
        for part in name.split(" and "):
            cc, _ = candidates(part)
            out += cc
        return out, "and"
    w = NORM(re.sub(r"\(.*?\)", "", name))
    w = [x for x in w if x not in ("burghs", "boroughs", "district", "town", "city", "of")]
    s = " ".join(w)
    s = re.sub(r"^" + DIR + r" ", "", s)
    s = re.sub(r" " + DIR + r"$", "", s)
    if s in byname:
        return [s], "name"
    for n in range(len(w) - 1, 0, -1):          # Birmingham Bordesley, Liverpool West Toxteth, Glasgow St Rollox
        p = " ".join(w[:n])
        if p in byname and p not in ("st", "new", "great", "east", "west", "north", "south"):
            return [p], "prefix"
    return [], ""


rows = []
for (name, xx, yy, el) in c[["constituency", "x", "y", "election"]].drop_duplicates(["constituency", "election"]).itertuples(index=False):
    if GL.contains(Point(xx, yy)):
        rows.append({"constituency": name, "election": el, "town": LONQ, "town_name": "London", "how": "Greater London", "km": 0.0}); continue
    cand, how = candidates(name)
    for ck in cand:
        if ck not in byname:
            continue
        g = byname[ck]
        dd = np.hypot(g.x - xx, g.y - yy) / 1000
        j = dd.idxmin()
        if dd[j] <= 30:
            rows.append({"constituency": name, "election": el, "town": g.qid[j], "town_name": g.name[j], "how": how, "km": round(float(dd[j]), 1)})
L = pd.DataFrame(rows)
L.drop_duplicates(["constituency", "town"]).sort_values("constituency").to_csv(f"{WORK}/links.csv", index=False)
# borough flag: a town counts as a parliamentary borough in 1868 to 1880 if it was linked to a seat then
bor = set(L[L.election.isin(["1868", "1874", "1880"])].town)


def votes(els, tag):
    LL = L[L.election.isin(els)]
    m = LL.merge(k[["election", "constituency", "family", "votes", "elected"]], on=["election", "constituency"])
    m["fam"] = m.family.replace({"LU": "CON", "PEEL": "CON"})
    out = []
    for t, g in m.groupby("town"):
        rec = {"town": t}
        sh, shl, shlab = [], [], []
        for e, ge in g.groupby("election"):
            v = ge.dropna(subset=["votes"])
            two = v[v.fam.isin(["LIB", "CON"])].votes.sum()
            tot = v.votes.sum()
            if two > 0:
                sh.append(v[v.fam == "LIB"].votes.sum() / two)
            if tot > 0:
                shl.append(v[v.fam == "LIB"].votes.sum() / tot); shlab.append(v[v.fam == "LAB"].votes.sum() / tot)
        won = g[g.elected == True]
        rec.update({f"{tag}_lib2": np.mean(sh) if sh else np.nan, f"{tag}_libtot": np.mean(shl) if shl else np.nan,
                    f"{tag}_lab": np.mean(shlab) if shlab else np.nan, f"{tag}_elections": len(sh),
                    f"{tag}_seats": len(won), f"{tag}_libwon": float((won.fam == "LIB").mean()) if len(won) else np.nan,
                    f"{tag}_labwon": float((won.fam == "LAB").mean()) if len(won) else np.nan})
        out.append(rec)
    return pd.DataFrame(out)


V = votes(VIC, "v").merge(votes(["1868", "1874", "1880"], "v1"), on="town", how="left").merge(votes(["1885", "1886", "1892", "1895", "1900"], "v2"), on="town", how="left")
V = V.merge(votes(INTER, "i"), on="town", how="left").merge(votes(LATE, "p"), on="town", how="left")
V["borough1868"] = V.town.isin(bor)
V = V.merge(T[["qid", "name", "pop", "lon", "lat"]].rename(columns={"qid": "town"}), on="town")
V.to_csv(f"{WORK}/town_votes.csv", index=False)
print("links", L.drop_duplicates(["constituency", "town"]).shape[0], "towns with Victorian vote", V.v_lib2.notna().sum(), "boroughs 1868", len(bor))
print(L[L.election.isin(VIC)].how.value_counts())
