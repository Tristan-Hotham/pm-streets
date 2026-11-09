"""Step 5: results.json (every number quoted anywhere) and the clean data tables in data/.
Merges WORK/models.json with descriptive counts; writes data/streets.csv, data/towns.csv, data/links.csv,
data/names.csv, data/models.csv, data/streets.json and data/towns.json for the page."""
import pandas as pd, numpy as np
from common import *
from names import N, NKEY, LIB_MAIN, CON_MAIN, LABOUR, ROYAL, HERO

R = json.load(open(f"{WORK}/models.json"))
S = pd.read_csv(f"{WORK}/streets.csv", keep_default_na=False, dtype={"ways": str})
S["route_flag"] = S.route_flag.astype(str) == "True"
for c_ in ("lon", "lat", "coloc_m", "place_km", "town_km"):
    S[c_] = pd.to_numeric(S[c_], errors="coerce")
V = pd.read_csv(f"{WORK}/towns_model.csv")
W = pd.read_csv(f"{WORK}/ways.csv", usecols=["way"])
D = pd.read_csv(f"{DATA}/name_diagnostics.csv")
raw = sum(1 for _ in gzip.open(STREETS, "rt")) - 1
S["label"] = S.key.map(lambda k: NKEY[k][1]); S["party"] = S.key.map(lambda k: NKEY[k][3]); S["class"] = S.key.map(lambda k: NKEY[k][4])
S.loc[S.route_flag, "class"] = "route"
R["n"] = {"raw": raw, "ways": int(len(W)), "streets": int(len(S)), "streets600": int(S.gid600.nunique()), "in_town_pc": 100 * float((S.town != "").mean()),
          "names": int(S.key.nunique()), "beac_route": int(S.route_flag.sum())}
cnt = S.key.value_counts()
R["count"] = {k: int(cnt.get(k, 0)) for k in NKEY}
main = S[S["class"] == "main"]
R["main_set"] = {"lib": int(main.key.isin(LIB_MAIN).sum()), "con": int(main.key.isin(CON_MAIN).sum())}
R["main_set"]["lib_pc"] = 100 * R["main_set"]["lib"] / (R["main_set"]["lib"] + R["main_set"]["con"])
R["main_set"]["ratio"] = R["main_set"]["lib"] / R["main_set"]["con"]
R["glad_vs_beac"] = R["count"]["gladstone"] / (R["count"]["beaconsfield"] + R["count"]["disraeli"] - R["n"]["beac_route"])
lab = S[S.key.isin(LABOUR)]
R["labour"] = {"n": int(len(lab)), "london": int((lab.county == "Greater London").sum()), "london_pc": 100 * float((lab.county == "Greater London").mean()),
               "lansbury_london": int(((S.key == "lansbury") & (S.county == "Greater London")).sum()), "wales": int((lab.nation == "Wales").sum()),
               "scotland": int((lab.nation == "Scotland").sum())}
R["by_nation"] = {}
for n_, g in main.groupby("nation"):
    R["by_nation"][n_] = {"lib": int(g.key.isin(LIB_MAIN).sum()), "con": int(g.key.isin(CON_MAIN).sum())}
top = lambda k: [{"town": t, "n": int(n)} for t, n in S[(S.key == k) & (S.town_name != "")].town_name.value_counts().head(6).items()]
R["top_towns"] = {k: top(k) for k in ("gladstone", "beaconsfield", "cobden", "palmerston", "bright", "attlee", "lansbury", "keirhardie")}
# diagnostics quoted
d = D.set_index("key")
R["diag"] = {k: {"coloc": float(d.loc[k, "coloc400_pc"]), "place": float(d.loc[k, "near_place10_pc"]), "n": int(d.loc[k, "streets"])}
             for k in d.index}
R["diag_pass"] = [NKEY[k][1] for k in d.index if d.loc[k, "passes"] is True or str(d.loc[k, "passes"]) == "True"]
R["diag_fail"] = [NKEY[k][1] for k in d.index if str(d.loc[k, "passes"]) == "False"]
# effects in plain terms
b = R["main"]["b"]
R["effect"] = {"pp_per10": 100 * b, "lo_pp": 100 * R["main"]["lo"], "hi_pp": 100 * R["main"]["hi"], "pp_40_60": 200 * b,
               "sd_pp": 100 * b * R["sample"]["v_sd"] / 10}
# examples
VV = V.set_index("name")
ex = {}
for t in ("Blackburn", "Leicester", "Liverpool", "Southampton", "Bolton", "Gateshead", "London", "Birmingham", "Dundee", "Widnes"):
    if t in VV.index:
        r = VV.loc[t]
        ex[t] = {"lib": int(r.n_lib), "con": int(r.n_con), "vote": 100 * float(r.v_lib2) if r.v_lib2 == r.v_lib2 else None}
R["ex"] = ex
R["region_table"] = {}
P0 = pd.read_csv(f"{WORK}/sample_main.csv")
for rg, g in P0.groupby("region"):
    R["region_table"][rg] = {"n": int(len(g)), "lib_pc": 100 * float(g.lib.mean()), "vote": 100 * float(g.drop_duplicates("town").v_lib2.mean()), "towns": int(g.town.nunique())}
R["alt_by"] = {a["label"]: a for a in R["alt"]}
R["rob_by"] = {a["label"]: a for a in R["robust"]}
R["pl_by"] = {a["label"]: a for a in R["placebo_later"]}
R["pc_by"] = {a["y"]: a for a in R["placebo_count"]}
R["sig"] = {"robust_pos": int(sum(a["lo"] > 0 for a in R["robust"])), "robust_n": len(R["robust"]),
            "alt_pos": int(sum(a["lo"] > 0 for a in R["alt"])), "alt_n": len(R["alt"]), "robust_b_min": min(a["b"] for a in R["robust"]),
            "robust_b_max": max(a["b"] for a in R["robust"])}
R["h3_main"] = R["h3"][0]
H = V[V.p_lab.notna()].copy(); H["any"] = H.n_labour > 0; H["q"] = pd.qcut(H.p_lab, 4, labels=False)
R["h3_quart"] = [{"lo": 100 * float(g.p_lab.min()), "hi": 100 * float(g.p_lab.max()), "pc": 100 * float(g["any"].mean()), "n": int(len(g))} for _, g in H.groupby("q")]
R["tm"] = {k.split()[0].lower().replace(",", ""): v for k, v in R["timing"].items()}

R["beac_dis"] = R["count"]["beaconsfield"] + R["count"]["disraeli"]
R["top5_list"] = ", ".join(R["top5"][:-1]) + " and " + R["top5"][-1]
R["pairs_glad_crimea_out"] = R["pairs"]["glad_crimea"]["towns"] - R["pairs"]["glad_crimea"]["a_inside"]
# ---- data tables
S["town_name"] = S.town_name.replace("", np.nan)
cols = ["gid", "name", "key", "label", "party", "class", "hws", "suffix", "lon", "lat", "county", "nation", "region", "town_name", "town", "town_km",
        "coloc_m", "place", "place_km", "n_ways", "ways"]
S[cols].rename(columns={"gid": "id", "town": "town_qid"}).round({"lon": 5, "lat": 5, "town_km": 2, "coloc_m": 0, "place_km": 2}).to_csv(f"{DATA}/streets.csv", index=False)
tc = ["town", "name", "pop", "lon", "lat", "region", "county", "borough1868", "v_lib2", "v_libwon", "v_elections", "v_seats", "v1_lib2", "v2_lib2",
      "p_libtot", "p_lab", "i_lab", "n_lib", "n_con", "n_party", "lib_name_share", "n_royal", "n_battle", "n_labour"]
V[tc].rename(columns={"town": "qid"}).round(4).to_csv(f"{DATA}/towns.csv", index=False)
import shutil
shutil.copy(f"{WORK}/links.csv", f"{DATA}/links.csv")
pd.DataFrame([{"key": n[0], "label": n[1], "regex": n[2], "party": n[3], "class": n[4], "from": n[5][0], "to": n[5][1], "note": n[6],
               "streets": R["count"][n[0]]} for n in N]).to_csv(f"{DATA}/names.csv", index=False)
rows = []
for grp in ("alt", "placebo_later", "robust", "loro", "h3"):
    for a in R[grp]:
        rows.append({"group": grp, **{k: a.get(k) for k in ("label", "x", "b", "se", "lo", "hi", "p", "n", "towns")}})
rows.insert(0, {"group": "main", **{k: R["main"].get(k) for k in ("label", "x", "b", "se", "lo", "hi", "p", "n", "towns")}})
for a in R["placebo_count"]:
    rows.append({"group": "placebo_count", "label": a["label"], "x": "v_lib210 (IRR)", "b": a["irr"], "lo": a["lo"], "hi": a["hi"], "p": a["p"], "n": a["n"]})
pd.DataFrame(rows).round(5).to_csv(f"{DATA}/models.csv", index=False)
# page data: compact streets (class codes) and towns
CL = {"main": 0, "test": 1, "main20": 2, "labour": 3, "amb": 4, "royal": 5, "hero": 6, "reform": 7, "route": 4}
keys = [n[0] for n in N]
pts = [[round(r.lon, 5), round(r.lat, 5), keys.index(r.key), r.name if r.name != NKEY[r.key][1] else "", r.town_name if isinstance(r.town_name, str) else "", r.ways.split(";")[0], int(r.route_flag)]
       for r in S.itertuples()]
jsave({"names": [{"k": n[0], "l": n[1], "p": n[3], "c": n[4], "y": f"{n[5][0]} to {n[5][1]}" if n[5][0] else "", "note": n[6]} for n in N], "s": pts}, f"{DATA}/streets.json")
tw = V[V.v_lib2.notna() | V.p_lab.notna()]
jsave([{"n": r.name, "lon": round(r.lon, 4), "lat": round(r.lat, 4), "v": None if r.v_lib2 != r.v_lib2 else round(100 * r.v_lib2, 1),
        "lab": None if r.p_lab != r.p_lab else round(100 * r.p_lab, 1), "l": int(r.n_lib), "c": int(r.n_con), "b": bool(r.borough1868), "e": int(r.v_elections) if r.v_elections == r.v_elections else 0}
       for r in tw.itertuples()], f"{DATA}/towns.json")
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("n", "main_set", "labour", "effect", "ex", "sig", "by_nation")}, indent=0)[:3000])
print(R["top_towns"])
