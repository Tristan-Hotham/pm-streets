"""Step 4: the analysis plan in NOTES.md, run as written. Builds the town table and the street sample, fits the main
model, the alternatives, placebos, randomisation inference, leave-one-region-out and measurement checks, the timing
(H2) and Labour (H3) analyses. Writes WORK/model_inputs.pkl and WORK/models.json (merged into results.json by step 5)."""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, pickle
import statsmodels.api as sm, statsmodels.formula.api as smf
import geopandas as gpd
from scipy.spatial import cKDTree
from common import *
from names import N, NKEY, LIB_MAIN, CON_MAIN, LABOUR, ROYAL

S = pd.read_csv(f"{WORK}/streets.csv", keep_default_na=False, dtype={"ways": str})
S["route_flag"] = S.route_flag.astype(str) == "True"
for c_ in ("x", "y", "lon", "lat", "coloc_m", "place_km"):
    S[c_] = pd.to_numeric(S[c_], errors="coerce")
V = pd.read_csv(f"{WORK}/town_votes.csv")
T = pd.read_csv(f"{WORK}/towns_all.csv")
B = pd.read_csv(f"{WORK}/battle.csv", keep_default_na=False)
TRAD = {"street", "road", "terrace", "place", "row", "square", "grove", "crescent", "avenue", "villas", "buildings", "cottages", "parade", "mount"}
S["trad"] = S.suffix.isin(TRAD).astype(int)
EXT_LIB = LIB_MAIN + ["rosebery", "granville"]
EXT_CON = CON_MAIN + ["salisbury", "balfour", "hartington", "chamberlain"]
S["party"] = np.where(S.key.isin(LIB_MAIN), "LIB", np.where(S.key.isin(CON_MAIN), "CON", ""))
S.loc[S.route_flag, "party"] = ""
S["party_ext"] = np.where(S.key.isin(EXT_LIB), "LIB", np.where(S.key.isin(EXT_CON), "CON", ""))
S.loc[S.route_flag, "party_ext"] = ""
S["party_peel"] = np.where(S.key == "peel", "CON", S.party)

# town attributes: region and county of the town point
CNT = gpd.read_file(f"{GEO}/counties_uk.geojson").to_crs(27700)
TP = gpd.GeoDataFrame(T[["qid"]], geometry=gpd.points_from_xy(T.x, T.y), crs=27700)
J = gpd.sjoin_nearest(TP, CNT[["county", "nation", "geometry"]], how="left")
J = J[~J.index.duplicated()]
T["county"], T["nation"] = J.county.values, J.nation.values
T["region"] = [region_of(a, b) for a, b in zip(T.county, T.nation)]
TT = T.set_index("qid")
V = V[V.town.map(TT.nation).isin(["England", "Wales", "Scotland"])].copy()
V["region"] = V.town.map(TT.region); V["county"] = V.town.map(TT.county)
V["log_pop"] = np.log(V["pop"])


def town_counts(col="town", party="party", D=None):
    D = S if D is None else D
    g = D[D[col] != ""]
    out = pd.DataFrame({"n_lib": g[g[party] == "LIB"].groupby(col).size(), "n_con": g[g[party] == "CON"].groupby(col).size(),
                        "n_royal": g[g.key.isin(ROYAL)].groupby(col).size(), "n_labour": g[g.key.isin(LABOUR)].groupby(col).size()}).fillna(0)
    return out


TC = town_counts()
bc = B[(B.town != "") & (B.flag == "")].groupby("town").size()
V = V.merge(TC, left_on="town", right_index=True, how="left").fillna({"n_lib": 0, "n_con": 0, "n_royal": 0, "n_labour": 0})
V["n_battle"] = V.town.map(bc).fillna(0)
V["n_party"] = V.n_lib + V.n_con
V["lib_name_share"] = V.n_lib / V.n_party.replace(0, np.nan)
V["log_royal"] = np.log1p(V.n_royal)
V["log_battle"] = np.log1p(V.n_battle)
for c_ in ("v_lib2", "v_libwon", "v1_lib2", "v2_lib2", "p_libtot", "p_lab", "p_lib2", "i_lab"):
    V[c_ + "10"] = V[c_] * 10
R = {}


def street_sample(party="party", col="town", D=None):
    D = S if D is None else D
    P = D[(D[party] != "") & (D[col] != "")].copy()
    P["lib"] = (P[party] == "LIB").astype(int)
    P = P.merge(V.drop(columns=[c for c in V.columns if c.startswith("n_") or c == "lib_name_share"]), left_on=col, right_on="town", how="inner", suffixes=("", "_t"))
    P = P.merge(V[["town", "log_royal"]].rename(columns={"log_royal": "lr2"}), on="town")
    return P


CTRL = "log_pop + log_royal + trad + C(region)"


def lpm(P, x="v_lib210", ctrl=CTRL, label=""):
    P = P.dropna(subset=[x])
    f = f"lib ~ {x}" + (f" + {ctrl}" if ctrl else "")
    m = smf.ols(f, P).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(P.town)[0]})
    b, se = m.params[x], m.bse[x]
    lo, hi = m.conf_int().loc[x]
    return {"label": label, "x": x, "b": float(b), "se": float(se), "lo": float(lo), "hi": float(hi), "p": float(m.pvalues[x]),
            "n": int(m.nobs), "towns": int(P.town.nunique()), "mean_y": float(P.lib.mean()), "r2": float(m.rsquared)}, m


P0 = street_sample()
R["main"], M0 = lpm(P0, label="Main: street-level LPM, controls, region FE, SE clustered by town")
print("MAIN", R["main"])
# full coefficient table of the main model
R["main_table"] = [{"term": t, "b": float(M0.params[t]), "se": float(M0.bse[t]), "p": float(M0.pvalues[t])} for t in M0.params.index]
R["sample"] = {"streets": int(len(P0)), "towns": int(P0.town.nunique()), "lib": int(P0.lib.sum()), "con": int((1 - P0.lib).sum()),
               "towns_vote": int(V.v_lib2.notna().sum()), "towns_any_vote": int(len(V)), "boroughs1868": int(V.borough1868.sum()),
               "regions": int(P0.region.nunique()), "london_streets": int((P0.town_name == "London").sum()),
               "v_mean": float(V[V.town.isin(P0.town)].v_lib2.mean() * 100), "v_sd": float(V[V.town.isin(P0.town)].v_lib2.std() * 100),
               "v_min": float(V[V.town.isin(P0.town)].v_lib2.min() * 100), "v_max": float(V[V.town.isin(P0.town)].v_lib2.max() * 100)}
alt = []
# A: binomial logit (equivalent to a town-level binomial model of Liberal names out of party names), SE clustered by county
TV = V[(V.n_party > 0) & V.v_lib2.notna()].copy()
PA = P0.dropna(subset=["v_lib210"])
ma = smf.logit("lib ~ v_lib210 + log_pop + log_royal + C(region)", PA).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(PA.county_t if "county_t" in PA else PA.town.map(TT.county))[0]})
lo, hi = ma.conf_int().loc["v_lib210"]
ame = ma.get_margeff().summary_frame().loc["v_lib210"]
alt.append({"label": "Binomial logit (log-odds per 10 points), SE clustered by county", "x": "v_lib210", "b": float(ma.params["v_lib210"]),
            "se": float(ma.bse["v_lib210"]), "lo": float(lo), "hi": float(hi), "p": float(ma.pvalues["v_lib210"]), "n": int(ma.nobs), "towns": int(PA.town.nunique()),
            "or": float(np.exp(ma.params["v_lib210"])), "or_lo": float(np.exp(lo)), "or_hi": float(np.exp(hi)), "ame": float(ame.iloc[0]),
            "ame_lo": float(ame.iloc[4]), "ame_hi": float(ame.iloc[5])})
# B: unweighted town OLS, towns with 2+ party streets
TB = TV[TV.n_party >= 2]
mb = smf.ols("lib_name_share ~ v_lib210 + log_pop + log_royal + C(region)", TB).fit(cov_type="HC3")
lo, hi = mb.conf_int().loc["v_lib210"]
alt.append({"label": "Town-level OLS on the Liberal share of names, towns with 2 or more party streets, HC3", "x": "v_lib210", "b": float(mb.params["v_lib210"]),
            "se": float(mb.bse["v_lib210"]), "lo": float(lo), "hi": float(hi), "p": float(mb.pvalues["v_lib210"]), "n": int(len(TB)), "towns": int(len(TB))})
infl = mb.get_influence(); cd = infl.cooks_distance[0]
TB2 = TB[cd <= 4 / len(TB)]
mb2 = smf.ols("lib_name_share ~ v_lib210 + log_pop + log_royal + C(region)", TB2).fit(cov_type="HC3")
lo, hi = mb2.conf_int().loc["v_lib210"]
alt.append({"label": "Town-level OLS without influential towns (Cook's D > 4/n)", "x": "v_lib210", "b": float(mb2.params["v_lib210"]), "se": float(mb2.bse["v_lib210"]),
            "lo": float(lo), "hi": float(hi), "p": float(mb2.pvalues["v_lib210"]), "n": int(len(TB2)), "towns": int(len(TB2)), "dropped": int(len(TB) - len(TB2))})
for x, lab in (("v_libwon10", "Liberal share of seats won 1868 to 1900 (uncontested included)"), ("v1_lib210", "Vote 1868 to 1880 only"),
               ("v2_lib210", "Vote 1885 to 1900 only")):
    alt.append(lpm(P0, x, label=lab)[0])
alt.append(lpm(P0, ctrl="", label="No controls")[0])
alt.append(lpm(P0, ctrl="log_pop + log_royal + trad + C(region) + log_battle", label="Adding log(1 + battle streets)")[0])
alt.append(lpm(P0[P0.borough1868], label="Parliamentary boroughs of 1868 only")[0])
R["alt"] = alt
# placebo 1: later vote
pl = []
PP = P0.dropna(subset=["p_libtot10", "p_lab10"])
pl.append(lpm(PP, label="Main model on the placebo sample (Victorian vote)")[0])
pl.append(lpm(PP, "p_libtot10", label="Liberal share of all votes 1945 to 1970")[0])
pl.append(lpm(PP, "p_lab10", label="Labour share of all votes 1945 to 1970")[0])
r_, m_ = lpm(PP, ctrl=CTRL + " + p_lab10", label="Victorian vote, controlling for Labour share 1945 to 1970")
pl.append(r_)
R["placebo_later"] = pl
R["v_p_corr"] = {"lab": float(V[["v_lib2", "p_lab"]].corr().iloc[0, 1]), "lib": float(V[["v_lib2", "p_libtot"]].corr().iloc[0, 1]),
                 "n": int(V[["v_lib2", "p_lab"]].dropna().shape[0])}
# placebo 2: non-political commemoration
pc = []
TP2 = V[V.v_lib2.notna()].copy()
for y, lab in (("n_royal", "Royal-named streets (Victoria, Albert, Alexandra)"), ("n_battle", "Battle-named streets 1793 to 1944 (battle-streets)"), ("n_party", "All main-set party streets")):
    m = smf.glm(f"{y} ~ v_lib210 + log_pop + C(region)", TP2, family=sm.families.Poisson()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(TP2.county)[0]})
    lo, hi = m.conf_int().loc["v_lib210"]
    pc.append({"label": lab, "y": y, "b": float(m.params["v_lib210"]), "irr": float(np.exp(m.params["v_lib210"])), "lo": float(np.exp(lo)), "hi": float(np.exp(hi)),
               "p": float(m.pvalues["v_lib210"]), "n": int(m.nobs)})
R["placebo_count"] = pc
# randomisation inference: town vote shuffled within region
rng = np.random.default_rng(11)
Pr = P0.dropna(subset=["v_lib210"]).copy()
X0 = pd.get_dummies(Pr[["log_pop", "log_royal", "trad", "region"]], columns=["region"], drop_first=True).astype(float)
X0.insert(0, "const", 1.0)
tv = Pr.drop_duplicates("town")[["town", "region", "v_lib210"]]
def coef(vmap):
    X = X0.copy(); X.insert(1, "v", Pr.town.map(vmap).values)
    return np.linalg.lstsq(X.values, Pr.lib.values, rcond=None)[0][1]
obs = coef(dict(zip(tv.town, tv.v_lib210)))
null = []
for _ in range(2000):
    sh = tv.copy(); sh["v_lib210"] = sh.groupby("region").v_lib210.transform(lambda s: rng.permutation(s.values))
    null.append(coef(dict(zip(sh.town, sh.v_lib210))))
null = np.array(null)
R["ri"] = {"obs": float(obs), "draws": 2000, "p_two": float((np.sum(np.abs(null) >= abs(obs)) + 1) / 2001), "count": int(np.sum(np.abs(null) >= abs(obs)))}
# leave one region out, no London, no top five
lo_ = []
for rg in sorted(P0.region.unique()):
    r_ = lpm(P0[P0.region != rg], label=f"Without {rg}")[0]; r_["region"] = rg; lo_.append(r_)
R["loro"] = lo_
R["loro_range"] = {"min": min(x["b"] for x in lo_), "max": max(x["b"] for x in lo_)}
rb = []
rb.append(lpm(P0[P0.town_name != "London"], label="Without London")[0])
top5 = P0.town.value_counts().head(5).index
R["top5"] = list(P0[P0.town.isin(top5)].drop_duplicates("town").town_name)
rb.append(lpm(P0[~P0.town.isin(top5)], label="Without the five towns with most party streets")[0])
# measurement
D600 = S.sort_values("n_ways", ascending=False).drop_duplicates(["gid600", "key"])
rb.append(lpm(street_sample(D=D600), label="Pieces joined within 600 m")[0])
Ps = street_sample(col="town_s"); rb.append(lpm(Ps, label="Town radius x0.7")[0])
Pl = street_sample(col="town_l"); rb.append(lpm(Pl, label="Town radius x1.4")[0])
Pe = street_sample(party="party_ext"); rb.append(lpm(Pe, label="Extended name set (Rosebery, Granville; Salisbury, Balfour, Hartington, Chamberlain)")[0])
Pp = street_sample(party="party_peel"); rb.append(lpm(Pp, label="Peel added as Conservative")[0])
rb.append(lpm(P0[P0.trad == 1], ctrl="log_pop + log_royal + C(region)", label="Traditional street words only")[0])
Pc = P0.copy(); Pc["k"] = Pc.town + "|" + Pc[ "party"]
Pc["g"] = merge_close(Pc, 300, key="k")
Pc1 = Pc.drop_duplicates("g")
rb.append(lpm(Pc1, label="Same-party streets within 300 m counted once")[0])
rb.append(lpm(P0[P0.key != "gladstone"], label="Without Gladstone streets")[0])
rb.append(lpm(P0[P0.region != "Scotland"], label="England and Wales only")[0])
R["robust"] = rb
R["clusters300"] = {"streets": int(len(P0)), "units": int(len(Pc1))}
print(pd.DataFrame(alt + pl + rb)[["label", "b", "lo", "hi", "p", "n", "towns"]].to_string())
print(pd.DataFrame(pc).to_string()); print(R["ri"]); print(R["loro_range"])

# ---- exploratory (added after the planned models): which Liberal names carry the association
ex = []
for keys, lab in ((["gladstone"], "Gladstone against Beaconsfield and Disraeli"), (["cobden", "bright"], "Cobden and Bright against Beaconsfield and Disraeli"),
                  (["palmerston"], "Palmerston against Beaconsfield and Disraeli")):
    Pe_ = P0[P0.key.isin(keys + ["beaconsfield", "disraeli"])]
    ex.append(lpm(Pe_, label=lab)[0])
R["exploratory"] = ex
print(pd.DataFrame(ex)[["label", "b", "lo", "hi", "p", "n", "towns"]])
# ---- exploratory, added at independent review: does the result rest on one contestable name?
rv = []
rv.append(lpm(P0[P0.key != "palmerston"], label="Without Palmerston")[0])
rv.append(lpm(P0[P0.key != "bright"], label="Without John Bright")[0])
rv.append(lpm(P0[P0.key != "beaconsfield"], label="Without Beaconsfield (Disraeli only)")[0])
STD = (r"^(back |upper |lower |little |great |north |south |east |west |old |new |higher )?(john )?(gladstone|cobden|palmerston|bright|disraeli|beaconsfield) "
       r"(street|road|terrace|place|grove|square|avenue|crescent|close|gardens|way|drive|lane|villas|row|mews|court|walk|parade|mount|buildings|cottages|rise|hill|park)( east| west| north| south)?$")
rv.append(lpm(P0[P0.name.str.lower().str.match(STD)], label="Plain street forms only")[0])
R["review"] = rv
# pieces of one street left unjoined by the 150 m first-point rule: same name, same town, nearest twin within 600 m
_tw = 0
for _, g_ in P0.groupby(["town", "norm"]):
    if len(g_) > 1:
        xy_ = g_[["x", "y"]].values
        dm_ = np.sqrt(((xy_[:, None] - xy_[None]) ** 2).sum(-1)); np.fill_diagonal(dm_, 1e12)
        _tw += int((dm_.min(axis=1) <= 600).sum())
R["review_twins"] = {"streets": _tw, "of": int(len(P0))}
print(pd.DataFrame(rv)[["label", "b", "lo", "hi", "p", "n", "towns", "mean_y"]])

# ---- H2 timing: within-town distance percentile, party and Labour streets pooled with battle streets
T2 = T.set_index("qid")
Q = S[(S.town != "") & ((S.party != "") | S.key.isin(LABOUR))].copy()
Q["grp"] = np.where(S.loc[Q.index, "key"] == "gladstone", "Gladstone", np.where(Q.key.isin(["beaconsfield", "disraeli"]), "Beaconsfield and Disraeli",
            np.where(Q.key.isin(["cobden", "bright", "palmerston"]), "Cobden, Bright, Palmerston", "Labour names")))
Bq = B[(B.town != "") & (B.clock.astype(str) == "True") & (B["style"] == "traditional")].copy()
Bq["grp"] = Bq.era
bx, by = bng(Bq.lon.values, Bq.lat.values); Bq["x"], Bq["y"] = bx, by
A = pd.concat([Q[["town", "grp", "x", "y"]], Bq[["town", "grp", "x", "y"]]])
A["dist"] = np.hypot(A.x - A.town.map(T2.x), A.y - A.town.map(T2.y)) / 1000
A = A[A.town != T2.index[T2.name == "London"][0]] if False else A
A["n"] = A.groupby("town").grp.transform("size")
A = A[A.n >= 3].copy()
A["pct"] = A.groupby("town").dist.rank(pct=True)
rng = np.random.default_rng(5)
towns = A.town.unique()
by_t = {t: g for t, g in A.groupby("town")}
GR = ["Napoleonic 1793 to 1815", "1816 to 1853", "Crimea 1854 to 1856", "Cobden, Bright, Palmerston", "1857 to 1898", "Gladstone",
      "Beaconsfield and Disraeli", "Boer War 1899 to 1902", "First World War", "Labour names", "Second World War"]
boots = {g: [] for g in GR}
for _ in range(1000):
    smp = pd.concat([by_t[t] for t in rng.choice(towns, len(towns))])
    mm = smp.groupby("grp").pct.mean()
    for g in GR:
        if g in mm: boots[g].append(mm[g])
R["timing"] = {}
for g in GR:
    v = A[A.grp == g]
    if len(v) >= 5:
        R["timing"][g] = {"n": int(len(v)), "towns": int(v.town.nunique()), "mean": float(v.pct.mean()), "lo": float(np.percentile(boots[g], 2.5)),
                          "hi": float(np.percentile(boots[g], 97.5)), "median_km": float(v.dist.median())}
R["timing_n"] = {"streets": int(len(A)), "towns": int(A.town.nunique())}
print(pd.DataFrame(R["timing"]).T.round(3))
# paired within-town comparison: towns with both Gladstone and Crimean / Boer streets
def paired(a, b):
    m = A[A.grp.isin([a, b])].groupby(["town", "grp"]).pct.mean().unstack().dropna()
    return {"towns": int(len(m)), "a_inside": int((m[a] < m[b]).sum()), "diff": float((m[a] - m[b]).mean())}
R["pairs"] = {"glad_crimea": paired("Gladstone", "Crimea 1854 to 1856"), "glad_boer": paired("Gladstone", "Boer War 1899 to 1902"),
              "glad_beac": paired("Gladstone", "Beaconsfield and Disraeli"), "lab_wwi": paired("Labour names", "First World War")}
print(R["pairs"])

# ---- H3 Labour names
H = V[V.p_lab.notna()].copy()
H["any_lab"] = (H.n_labour > 0).astype(int)
h = []
for f, lab in (("any_lab ~ p_lab10 + log_pop + log_royal + C(region)", "Labour share 1945 to 1970"),
               ("any_lab ~ p_lab10 + v_lib210 + log_pop + log_royal + C(region)", "plus Liberal share 1868 to 1900"),
               ("any_lab ~ i_lab10 + log_pop + log_royal + C(region)", "Labour share 1918 to 1935")):
    d_ = H.dropna(subset=[w for w in ("p_lab10", "v_lib210", "i_lab10") if w in f])
    m = smf.ols(f, d_).fit(cov_type="HC3")
    for x in [w for w in ("p_lab10", "v_lib210", "i_lab10") if w in f]:
        lo, hi = m.conf_int().loc[x]
        h.append({"label": lab, "x": x, "b": float(m.params[x]), "lo": float(lo), "hi": float(hi), "p": float(m.pvalues[x]), "n": int(m.nobs)})
    try:
        ml = smf.logit(f, d_).fit(disp=0, cov_type="HC1")
        x0 = f.split("~")[1].split("+")[0].strip()
        h[-1 if x0 == h[-1]["x"] else -2]["logit_b"] = float(ml.params[x0])
        h[[i for i, r in enumerate(h) if r["x"] == x0][-1]]["logit_p"] = float(ml.pvalues[x0])
    except Exception as e:
        print("logit failed", e)
R["h3"] = h
R["h3_n"] = {"towns": int(len(H)), "with_labour": int(H.any_lab.sum()), "labour_streets": int(S[S.key.isin(LABOUR)].shape[0]),
             "labour_in_towns": int(H.n_labour.sum())}
print(pd.DataFrame(h).to_string())
V.to_csv(f"{WORK}/towns_model.csv", index=False)
P0.to_csv(f"{WORK}/sample_main.csv", index=False)
json.dump(nonan(R), open(f"{WORK}/models.json", "w"), indent=1)
