"""Shared paths, constants and helpers for the pm-streets study ("Gladstone Road or Disraeli Street?").

Raw inputs (read in place, never modified):
  STREETS  /home/claude/newdata/raw_new11/pm_streets.tsv.gz
           OpenStreetMap via QLever: UK ways and nodes with a highway tag whose name contains a politician's or a Victorian
           commemorative word (Gladstone, Beaconsfield, Victoria, Wellington...). Columns: w (OSM id), hw (highway value),
           name, p (first part of the geometry as WKT). Includes bus stops and other non-street features.
  ELEC     /home/claude/src6/elections-since-1832/data  contests.csv, candidates.csv (UK general election results
           1832 to 2024 with party families; UK Parliament and House of Commons Library, Open Parliament Licence v3.0).
  SETTLE   /home/claude/newdata/raw_new8/uk_settlements.tsv  Wikidata UK settlements with population (CC0).
  BATTLE   /home/claude/studies/battle-streets/data/streets.csv  dated battle streets (derived from OSM, ODbL).
  GEO      /home/claude/newdata/raw/geo/counties_uk.geojson (ONS boundaries, OGL v3) and Natural Earth (public domain).
Intermediates go to WORK (/home/claude/scratch/pm-streets), outside the repository.
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STREETS = os.environ.get("PM_STREETS", "/home/claude/newdata/raw_new11/pm_streets.tsv.gz")
ELEC = os.environ.get("PM_ELEC", "/home/claude/src6/elections-since-1832/data")
SETTLE = os.environ.get("PM_SETTLE", "/home/claude/newdata/raw_new8/uk_settlements.tsv")
BATTLE = os.environ.get("PM_BATTLE", "/home/claude/studies/battle-streets/data/streets.csv")
GEO = os.environ.get("PM_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("PM_FONTS", "/home/claude/ref/fonts")
INK = os.environ.get("PM_INK", "/home/claude/studies/ink-map")
INKFONTS = os.path.join(INK, "fonts", "ttf")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
WORK = os.environ.get("PM_WORK", "/home/claude/scratch/pm-streets")
for d in (DATA, IMG, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "pm-streets"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {k: nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "x": return f"{float(v):.1f}"
    raise ValueError(f)


def fill(t, R, keep=("DOI", "DOI_URL", "BLOG_URL"), tf=None):
    """replace {{path|fmt}} tokens from results.json; leave the publisher's placeholders and IMG tokens"""
    f = tf or fmt
    return re.sub(r"\{\{(?!IMG\|)([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in keep else f(get(R, m.group(1)), m.group(3)), t)


def read_tsv(path):
    """QLever TSV: header line, IRIs in <...>, literals in "..." (possibly @lang or ^^type)."""
    def lit(s):
        s = s.strip()
        if s.startswith("<") and s.endswith(">"):
            return s[1:-1]
        m = re.match(r'^"(.*)"(?:@[\w-]+|\^\^.*)?$', s, re.S)
        if m:
            return m.group(1).replace('\\"', '"').replace("\\\\", "\\")
        return s
    with gzip.open(path, "rt", encoding="utf-8") as f:
        head = [h.lstrip("?") for h in f.readline().rstrip("\n").split("\t")]
        for line in f:
            parts = line.rstrip("\n").split("\t")
            parts += [""] * (len(head) - len(parts))
            yield {h: lit(p) for h, p in zip(head, parts)}


def point(wkt):
    """first coordinate pair of a POINT or a (truncated) LINESTRING"""
    m = re.search(r"(?:POINT|LINESTRING|POLYGON)\s*\(+\s*([-\d.eE]+)\s+([-\d.eE]+)", wkt or "")
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)


def km(lat1, lon1, lat2, lon2):
    import numpy as np
    p1, p2, l1, l2 = map(np.radians, (lat1, lat2, lon1, lon2))
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin((l2 - l1) / 2) ** 2))


TOWN_TYPES = {"town", "market town", "city", "county town", "big city", "new town (UK)", "seaside resort", "town of the United Kingdom",
              "city of United Kingdom", "college town", "port city", "largest city", "railway town", "city status in the United Kingdom",
              "border city", "national capital", "cathedral city", "spa town", "post town", "port settlement", "mill town", "market municipality"}


def settlements(min_pop=10000):
    """Wikidata UK settlements whose types include a town or city type, one row per item (largest population stated),
    with population at least min_pop. Areas of London, suburbs, conurbations and built-up areas are left out; London is
    kept as one city at its Wikidata point."""
    import pandas as pd
    d = pd.read_csv(SETTLE, sep="\t", dtype=str, quoting=3)
    d.columns = [c.lstrip("?") for c in d.columns]
    d["pl"] = d.pl.str.replace(r'^"|"(@\w+)?$', "", regex=True)
    d["typel"] = d.typel.str.replace(r'^"|"(@\w+)?$', "", regex=True)
    d["pop"] = pd.to_numeric(d["pop"], errors="coerce")
    xy = d.coord.str.extract(r"POINT\(([-\d.]+) ([-\d.]+)\)").astype(float)
    d["lon"], d["lat"] = xy[0], xy[1]
    d["qid"] = d.p.str.extract(r"(Q\d+)")[0]
    g = d.groupby("qid").agg(name=("pl", "first"), lon=("lon", "median"), lat=("lat", "median"), pop=("pop", "max"),
                             types=("typel", lambda s: set(s)))
    g = g[g.types.apply(lambda s: bool(s & TOWN_TYPES)) & (g["pop"] >= min_pop)]
    g = g[~g.name.str.contains("Greater London|metropolitan|Urban Area|Built-up", regex=True)]
    g = g[(g.lat > 49.8) & (g.lat < 61) & (g.lon > -8.7) & (g.lon < 2)]
    g["types"] = g.types.apply(lambda s: "; ".join(sorted(s)))
    return g.reset_index()


def bng(lon, lat):
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 27700, always_xy=True)
    return tr.transform(lon, lat)


def merge_close(df, dist_m, key="norm"):
    """single-linkage groups of rows with the same key whose points (x, y in metres) chain within dist_m"""
    import numpy as np
    from scipy.spatial import cKDTree
    gid = np.full(len(df), -1)
    nxt = 0
    for _, idx in df.groupby(key).indices.items():
        idx = np.asarray(idx)
        if len(idx) == 1:
            gid[idx] = nxt; nxt += 1; continue
        P = df[["x", "y"]].values[idx]
        par = list(range(len(idx)))
        def f(i):
            while par[i] != i:
                par[i] = par[par[i]]; i = par[i]
            return i
        for a, b in cKDTree(P).query_pairs(dist_m):
            ra, rb = f(a), f(b)
            if ra != rb: par[ra] = rb
        roots = {}
        for i in range(len(idx)):
            r = f(i)
            if r not in roots:
                roots[r] = nxt; nxt += 1
            gid[idx[i]] = roots[r]
    return gid


REGION = {  # ceremonial county (counties_uk.geojson) -> English region; Wales and Scotland are regions of their own
    "North East": ["Durham", "Northumberland", "Tyne and Wear"],
    "North West": ["Cheshire", "Cumbria", "Greater Manchester", "Lancashire", "Merseyside"],
    "Yorkshire and the Humber": ["East Riding of Yorkshire", "North Yorkshire", "South Yorkshire", "West Yorkshire"],
    "East Midlands": ["Derbyshire", "Leicestershire", "Lincolnshire", "Northamptonshire", "Nottinghamshire", "Rutland"],
    "West Midlands": ["Herefordshire", "Shropshire", "Staffordshire", "Warwickshire", "West Midlands", "Worcestershire"],
    "East of England": ["Bedfordshire", "Cambridgeshire", "Essex", "Hertfordshire", "Norfolk", "Suffolk"],
    "London": ["Greater London"],
    "South East": ["Berkshire", "Buckinghamshire", "East Sussex", "Hampshire", "Isle of Wight", "Kent", "Oxfordshire", "Surrey", "West Sussex"],
    "South West": ["Bristol", "Cornwall", "Devon", "Dorset", "Gloucestershire", "Somerset", "Wiltshire"],
}
COUNTY_REGION = {c: r for r, cs in REGION.items() for c in cs}


def region_of(county, nation):
    if nation in ("Wales", "Scotland", "Northern Ireland"):
        return nation
    return COUNTY_REGION.get(county, "")
