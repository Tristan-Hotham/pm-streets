"""Step 8: the paper. Fills code/paper_template.tex from data/results.json, builds the tables, compiles with xelatex.
Output: release/paper/Hotham_PM_Streets.pdf and .tex beside the f_*.png figures.
https://doi.org/10.5281/zenodo.24092657 stays a placeholder unless DOI is set: DOI=10.5281/zenodo.N python3 code/08_paper.py"""
import subprocess
import pandas as pd
from common import *
from names import N

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_PM_Streets"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return "<0.001" if float(v) < 0.001 else f"{float(v):.3f}"
    if f == "pp": return "0.0" if f"{100 * float(v):.1f}" == "-0.0" else f"{100 * float(v):.1f}"
    return tex(str(v))


def pv(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def row(a, lab=None, scale=100, d=1):
    lab = tex(lab or a["label"])
    tw = a.get("towns", "")
    z = lambda v: (lambda s: "0.0" if s == "-0.0" else s)(f"{scale * v:.{d}f}")
    return f"{lab} & {z(a['b'])} & [{z(a['lo'])}, {z(a['hi'])}] & {pv(a['p'])} & {a['n']:,} & {tw}\\\\\n"


def table(rows, cap, lab, note):
    return ("\\begin{table}[tbp]\\centering\\footnotesize\\begin{threeparttable}\\caption{" + cap + "}\\label{" + lab + "}"
            "\\begin{tabular}{p{7.2cm}rcrrr}\\toprule Specification & $\\beta$ & 95\\% CI & $p$ & N & Towns\\\\\\midrule\n" + rows +
            "\\bottomrule\\end{tabular}\\begin{tablenotes}\\footnotesize\\item " + note + "\\end{tablenotes}\\end{threeparttable}\\end{table}")


NOTE = "$\\beta$: change in the probability (percentage points) that a party street is Liberal per 10 points of Liberal vote. Street-level linear probability models with log population, log(1 + royal streets), traditional street word and region fixed effects unless stated; standard errors clustered by town."
# main table: full coefficients
TERM = {"Intercept": "Constant", "v_lib210": "Liberal vote share 1868 to 1900 (per 10 points)", "log_pop": "log population", "log_royal": "log(1 + royal streets)", "trad": "Traditional street word"}
rows = ""
for t in R["main_table"]:
    lab = TERM.get(t["term"], t["term"].replace("C(region)[T.", "Region: ").replace("]", ""))
    rows += f"{tex(lab)} & {t['b']:.3f} & ({t['se']:.3f}) & {pv(t['p'])}\\\\\n"
TM = ("\\begin{table}[tbp]\\centering\\footnotesize\\begin{threeparttable}\\caption{Main model: linear probability model of a party street being Liberal (N = "
      f"{R['main']['n']:,} streets, {R['main']['towns']} towns, $R^2$ = {R['main']['r2']:.3f}).}}\\label{{tab:main}}"
      "\\begin{tabular}{p{7.5cm}rrr}\\toprule Term & Coefficient & (SE) & $p$\\\\\\midrule\n" + rows +
      "\\bottomrule\\end{tabular}\\begin{tablenotes}\\footnotesize\\item Standard errors clustered by town. Reference region: East Midlands. The outcome is 1 for a Liberal name, 0 for a Conservative one; the vote coefficient is per 10 points, on the probability scale.\\end{tablenotes}\\end{threeparttable}\\end{table}")
a0 = R["alt"][0]
rows = row(R["main"], "Main model") + f"Binomial logit, SE clustered by county (log-odds) & {a0['b']:.2f} & [{a0['lo']:.2f}, {a0['hi']:.2f}] & {pv(a0['p'])} & {a0['n']:,} & {a0['towns']}\\\\\n"
rows += f"\\quad average marginal effect (points) & {100 * a0['ame']:.1f} & [{100 * a0['ame_lo']:.1f}, {100 * a0['ame_hi']:.1f}] & & & \\\\\n"
for a in R["alt"][1:]:
    rows += row(a)
TA = table(rows, "Alternative specifications (planned).", "tab:alt", NOTE + " Town-level OLS rows: one observation per town, HC3 errors; $\\beta$ in points of the Liberal share of names. Seats-won row: per 10 points of the Liberal share of seats won.")
rows = "".join(row(a) for a in R["placebo_later"])
rows += "\\midrule\\multicolumn{6}{l}{\\textit{Town-level Poisson models of counts (incidence rate ratio per 10 points of Liberal vote)}}\\\\\n"
for a in R["placebo_count"]:
    rows += f"{tex(a['label'])} & {a['irr']:.2f} & [{a['lo']:.2f}, {a['hi']:.2f}] & {pv(a['p'])} & {a['n']} & {a['n']}\\\\\n"
TP = table(rows, "Placebo tests: the vote of 1945 to 1970 in place of the Victorian vote, and non-political commemoration.", "tab:placebo",
           NOTE + " Later-period rows use the towns with both votes. Poisson models with log population and region, SE clustered by county.")
rows = "".join(row(a) for a in R["robust"]) + f"Randomisation inference (2,000 within-region shuffles) & {100 * R['ri']['obs']:.1f} & & {R['ri']['p_two']:.3f} & {R['main']['n']} & {R['main']['towns']}\\\\\n"
rows += "\\midrule\\multicolumn{6}{l}{\\textit{Exploratory (added after the planned analysis)}}\\\\\n" + "".join(row(a) for a in R["exploratory"] + R["review"])
TR = table(rows, "Robustness: outliers, regions and measurement choices, with the exploratory checks below the line.", "tab:robust", NOTE)
rows = "".join(row(a) for a in R["loro"])
TL = table(rows, "Leaving out one region at a time.", "tab:loro", NOTE)
rows = "".join(f"{tex(k)} & {v['n']} & {v['towns']} & {v['mean']:.3f} & [{v['lo']:.3f}, {v['hi']:.3f}] & {v['median_km']:.2f}\\\\\n" for k, v in R["timing"].items())
TT = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Within-town distance rank (0 centre, 1 edge) by group, towns with 3 or more streets; town-cluster bootstrap 95\\% intervals; median distance from the town point.}\\label{tab:timing}"
      "\\begin{tabular}{lrrrcr}\\toprule Group & Streets & Towns & Mean rank & 95\\% CI & Median km\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for a in R["h3"]:
    lg = f"{a['logit_b']:.2f} ({pv(a['logit_p'])})" if "logit_b" in a else ""
    rows += f"{tex(a['label'])}: {tex({'p_lab10': 'Labour 1945 to 1970', 'v_lib210': 'Liberal 1868 to 1900', 'i_lab10': 'Labour 1918 to 1935'}[a['x']])} & {100 * a['b']:.1f} & [{100 * a['lo']:.1f}, {100 * a['hi']:.1f}] & {pv(a['p'])} & {a['n']} & {lg}\\\\\n"
TH = ("\\begin{table}[tbp]\\centering\\footnotesize\\begin{threeparttable}\\caption{H3: town has a Labour-named street (linear probability, points per 10 points of vote, HC3 errors; logit coefficient and $p$ alongside).}\\label{tab:h3}"
      "\\begin{tabular}{p{6.8cm}rcrrr}\\toprule Model: variable & $\\beta$ & 95\\% CI & $p$ & Towns & Logit\\\\\\midrule\n" + rows +
      "\\bottomrule\\end{tabular}\\begin{tablenotes}\\footnotesize\\item Controls: log population, log(1 + royal streets), region fixed effects.\\end{tablenotes}\\end{threeparttable}\\end{table}")
rows = "".join(f"{tex(k)} & {v['towns']} & {v['n']} & {v['lib_pc']:.1f} & {v['vote']:.1f}\\\\\n" for k, v in sorted(R["region_table"].items()))
TG = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{The main sample by region: towns, party streets, Liberal share of names (\\%) and mean town Liberal vote share 1868 to 1900 (\\%).}\\label{tab:region}"
      "\\begin{tabular}{lrrrr}\\toprule Region & Towns & Streets & Liberal names & Liberal vote\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
D = pd.read_csv(f"{DATA}/name_diagnostics.csv", keep_default_na=False)
rows = "".join(f"{tex(r.label)} & {tex(r.party)} & {r['class']} & {r.streets:,} & {r.coloc400_pc:.1f} & {r.near_place10_pc:.1f} & {r.traditional_pc:.0f} & {'' if r.passes == '' else ('pass' if str(r.passes) == 'True' else 'fail')}\\\\\n" for _, r in D.iterrows())
TD = ("\\begin{small}\\begin{longtable}{llllrrrr}\\caption{Name diagnostics: streets, \\% with a main-set party street of another name within 400 m, \\% within 10 km of a same-name settlement, \\% with a traditional street word, and the pre-set test result.}\\label{tab:diag}\\\\"
      "\\toprule Name & Party & Class & Streets & Co-loc. & Place & Trad. & Test\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}\\end{small}")
rows = "".join(f"{tex(n[1])} & {tex(n[3])} & {n[4]} & {str(n[5][0]) + ' to ' + str(n[5][1]) if n[5][0] else ''} & {tex(n[6])}\\\\\n" for n in N)
TN = ("\\begin{small}\\begin{longtable}{llllp{7.4cm}}\\caption{The name table: party (LIB Liberal, CON Conservative, LU Liberal Unionist, LAB Labour, PEEL Peelite, WHIG, TORY, IRN Irish Nationalist), class and years of prominence.}\\label{tab:names}\\\\"
      "\\toprule Name & Party & Class & Years & Note\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}\\end{small}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{PAGE}}", PAGE).replace("{{REPO}}", REPO)
for k, v in (("TABLE_MAIN", TM), ("TABLE_ALT", TA), ("TABLE_PLACEBO", TP), ("TABLE_ROBUST", TR), ("TABLE_LORO", TL), ("TABLE_TIMING", TT), ("TABLE_H3", TH),
             ("TABLE_REGION", TG), ("TABLE_DIAG", TD), ("TABLE_NAMES", TN)):
    t = t.replace("{{" + k + "}}", v)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24092657", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t, [l for l in t.splitlines() if "{{" in l or "--" in l][:5]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l or l.startswith("!")][:15])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
body = txt.split("References")[0] if "References" in txt else txt
print("paper", r.returncode, len(txt.split()), "words in all;", len(body.split()), "before references;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–"))
