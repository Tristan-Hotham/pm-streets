"""Step 10: README.md, LICENSE, the Reddit post (reddit/post.md) and the journal cover note (release/paper/cover_note.md),
filled from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
N, M, E, C = R["n"], R["main"], R["effect"], R["count"]
z1 = lambda v: (lambda s: "0.0" if s == "-0.0" else s)(f"{100 * v:.1f}")
pp = lambda a: f"{z1(a['b'])} (95% CI {z1(a['lo'])} to {z1(a['hi'])})"
readme = f"""# Gladstone Road or Disraeli Street?

Partisan commemoration in the street names of Victorian Britain. Every OpenStreetMap road in the UK whose name contains a politician's or Victorian commemorative word ({N['ways']:,} ways, joined into {N['streets']:,} streets), a documented name table with a tested rule for ambiguous names, and {R['sample']['towns']} British towns linked to the general election results of the seats named after them, 1868 to 1900. Do towns' Gladstone Roads and Beaconsfield Streets follow how the towns voted?

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24092657}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/pm-streets/}}
Code and data: {REPO}

## Headline results

- Liberal names dominate: Gladstone {C['gladstone']}, Cobden {C['cobden']}, Palmerston {C['palmerston']}, John Bright {C['bright']}; Beaconsfield {C['beaconsfield']}, Disraeli {C['disraeli']}. {R['main_set']['lib_pc']:.1f}% of main-set party street names are Liberal, about {R['main_set']['ratio']:.1f} to 1, in Conservative as well as Liberal towns (Blackburn: {R['ex']['Blackburn']['vote']:.0f}% Liberal vote, {R['ex']['Blackburn']['lib']} Liberal names, 0 Conservative). London is the exception ({R['ex']['London']['lib']} Liberal, {R['ex']['London']['con']} Conservative).
- Pre-specified main model (street-level linear probability model, region fixed effects, SE clustered by town; plan in NOTES.md, written before the outcome models): each 10 points of Liberal vote 1868 to 1900 goes with {pp(M)} points more Liberal names; p = {M['p']:.3f}; N = {M['n']} streets in {M['towns']} towns.
- Survives randomisation inference (p = {R['ri']['p_two']:.3f}), leaving out any region ({100 * R['loro_range']['min']:.1f} to {100 * R['loro_range']['max']:.1f}), London, the five biggest towns, and most measurement choices ({R['sig']['robust_pos']} of {R['sig']['robust_n']} checks with intervals above zero). Placebo: the vote of 1945 to 1970 does not predict the names (Labour {pp(R['placebo_later'][2])}, Liberal {pp(R['placebo_later'][1])}).
- Fragile: not significant at the town level unweighted ({pp(R['alt'][1])}), with the share of seats won ({pp(R['alt'][3])}), in 1868 boroughs only, in either half of the period, or in England and Wales only. Exploratory: carried by Beaconsfield names; with Disraeli as the only Conservative name the estimate is {pp(R['review'][2])}, too few streets to tell. A faint trace on top of a national Liberal street culture. Correlational.
- Timing: within towns, Gladstone streets rank {R['tm']['gladstone']['mean']:.2f} from centre (0) to edge (1), between Crimean ({R['tm']['crimea']['mean']:.2f}) and Boer War ({R['tm']['boer']['mean']:.2f}) battle streets; Labour names ({R['labour']['n']} streets) at {R['tm']['labour']['mean']:.2f}.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | Interactive page: MapLibre on OpenFreeMap Positron; streets coloured by party, towns ringed by Liberal vote; name filter, layers panel, search, popups, full-screen. |
| `header.png` | Social card, 1200 x 630. |
| `data/streets.csv` | Every matched street ({N['streets']:,}): name, key, person, party, class, highway types, position, county, region, town, co-location and place diagnostics, OSM way ids. ODbL. |
| `data/names.csv` | The name table: regex, person, party, class, years, note, streets. |
| `data/name_diagnostics.csv` | Co-location and place tests for every name, with the pass or fail of tested names. |
| `data/towns.csv` | Towns with votes (1868 to 1900, 1918 to 1935, 1945 to 1970), seats, party, royal, battle and Labour street counts. |
| `data/links.csv` | Every constituency to town link, with how it was made. |
| `data/models.csv` | Every model estimate (main, alternatives, placebos, robustness, leave-one-region-out, H3). |
| `data/results.json` | Every number quoted on the page, in the paper, blog, collage and post. |
| `data/streets.json`, `data/towns.json` | Page data. |
| `code/` | Numbered pipeline, `names.py` (the name table), templates, `qa.js`. |
| `release/` | Paper (`paper/`, with `cover_note.md`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage, looping GIF, `collage.py` and post text. |
| `NOTES.md` | The analysis plan (written before the outcome models), the log, and the reference verification list. |

## Method in brief

- Streets: road highway values only; whole-word name matching; pieces with the same normalised name chaining within 150 m joined ("Back X Street" joined to X Street).
- Names: main set Gladstone, Cobden, Palmerston, John Bright (Liberal) and Disraeli, Beaconsfield (Conservative; {N['beac_route']} Beaconsfield streets within 25 km of Beaconsfield, Bucks set aside). Tested names admitted to an extended set by a pre-set rule (another party street within 400 m at half the Gladstone rate, and under 25% near a same-name place): {", ".join(R['diag_pass'])} pass; {", ".join(R['diag_fail'])} fail.
- Towns: Wikidata towns and cities of 3,000 or more; nearest by distance over a population-based radius; Greater London as one.
- Votes: seats named after the town (with divisions, two-town seats and a short alias list); Liberal share of Liberal plus Conservative and Liberal Unionist votes in contested seats, averaged over elections 1868 to 1900.
- Models: as in the analysis plan in `NOTES.md` (statsmodels).

## How to rerun

Python 3 with pandas, numpy, scipy, geopandas, pyproj, shapely, statsmodels, matplotlib, Pillow; xelatex, pdftotext; node with Playwright for `code/qa.js`. Raw inputs are listed in `code/common.py`; intermediates go to `PM_WORK`.

```
python3 code/01_streets.py     # match names, join pieces
python3 code/02_towns.py       # towns, name diagnostics, battle streets
python3 code/03_votes.py       # constituency to town links, vote shares
python3 code/04_models.py      # the planned models
python3 code/05_results.py     # results.json and data tables
python3 code/06_figures.py     # figures
python3 code/07_build_site.py  # index.html
python3 code/08_paper.py       # paper PDF (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py      # collage, header, GIF
python3 code/10_readme.py      # README, LICENSE, post, cover note
python3 code/09_release.py     # blog post and Zenodo files
node code/qa.js                # screenshots
```

## Sources and licences

- Streets: © OpenStreetMap contributors, Open Database Licence; queried with QLever. Derived street tables are released under the ODbL.
- Elections: UK Parliament results and House of Commons Library (Open Parliament Licence v3.0), as compiled in the elections-since-1832 study.
- Settlements: Wikidata (CC0). Counties: ONS (Open Government Licence v3.0).
- Base map: OpenFreeMap, OpenStreetMap data (ODbL). MapLibre GL JS (BSD 3-Clause).
- Text and figures CC BY 4.0; code MIT (see `LICENSE`).

## Citation

Hotham, T. (2026). Gladstone Road or Disraeli Street? Partisan Commemoration in the Street Names of Victorian Britain. Zenodo. {{https://doi.org/10.5281/zenodo.24092657}}

{AI}
"""
open(f"{ROOT}/README.md", "w").write(readme)
open(f"{ROOT}/LICENSE", "w").write("""MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text and figures: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), Tristan Hotham, 2026.
Street data (data/streets.csv, data/streets.json, data/name_diagnostics.csv): derived from OpenStreetMap, © OpenStreetMap contributors, Open Database Licence 1.0 (https://opendatacommons.org/licenses/odbl/1-0/).
Election-derived tables (data/towns.csv, data/towns.json, data/links.csv): contain Parliamentary information licensed under the Open Parliament Licence v3.0. Settlement names and points from Wikidata (CC0).
data/names.csv, data/models.csv and data/results.json: CC BY 4.0.
""")
post = f"""**Title:** [OC] Every UK street named after a Victorian statesman: {C['gladstone']} Gladstones vs {C['beaconsfield'] + C['disraeli']} Beaconsfields and Disraelis. {R['main_set']['lib_pc']:.0f}% of party street names are Liberal, even in Tory towns

**Body:**

Victorian builders named new streets after the statesmen of the day. I matched every OpenStreetMap road in the UK against a table of politicians, sorted out the false friends (a Derby Road usually goes to Derby), and linked {R['sample']['towns']} towns to how they voted from 1868 to 1900.

- Gladstone {C['gladstone']}, Cobden {C['cobden']}, Palmerston {C['palmerston']}, John Bright {C['bright']}; Beaconsfield (Disraeli's title) {C['beaconsfield']}, Disraeli {C['disraeli']}.
- Tory Blackburn ({R['ex']['Blackburn']['vote']:.0f}% Liberal vote) has {R['ex']['Blackburn']['lib']} Liberal party names and no Conservative ones. London has the most Conservative names ({R['ex']['London']['con']} of {R['ex']['London']['con'] + R['ex']['London']['lib']}).
- Liberal towns did name a little more after Liberals: +{E['pp_per10']:.1f} points per 10 points of vote (95% CI {E['lo_pp']:.1f} to {E['hi_pp']:.1f}), comparing towns in the same region. The 1945 to 1970 vote does not predict the names, but the link is fragile under some alternative measures.
- Gladstone streets sit between Crimean and Boer War battle streets in their towns, so probably mostly late Victorian. Labour names ({R['labour']['n']}: Keir Hardie, Lansbury, Attlee, Bevan) sit farther out.

Interactive map: {PAGE}

**Source comment:**

Data: OpenStreetMap contributors (ODbL) via QLever; UK Parliament election results (Open Parliament Licence); Wikidata (CC0). Tools: Python (pandas, geopandas, statsmodels, matplotlib), MapLibre with OpenFreeMap tiles. Name table, tests and code: {REPO}
"""
open(f"{ROOT}/reddit/post.md", "w").write(post)
words_note = "about 7,700 words before references, plus tables and figures"
cover = f"""# Cover note: Gladstone Road or Disraeli Street?

## Suitable journals (checked 2026)

All publish subscription articles without an article processing charge; open access is optional and paid. Word limits below were checked against the publishers' author pages where those could be reached; recheck the Elsevier guides before submitting.

1. **Journal of Historical Geography** (Elsevier). Commemorative toponymy and historical political geography are core topics (it published Light 2004 on Bucharest street names). The best fit for the historical framing. Its length guidance could not be reconfirmed at review (the guide for authors page was unreachable); the main text is {words_note}.
2. **Urban History** (Cambridge University Press). Articles "normally no longer than 10,000 words, inclusive of footnotes and tables" (author instructions, checked at review). The text fits, but the appendix tables count, so they would need to move to online supplementary material.
3. **Political Geography** (Elsevier). Published Azaryahu (1997) on Berlin street names; the framing would lead with commemoration and political memory. An earlier check found an 11,000-word limit for full-length papers; this could not be reconfirmed at review.

Also possible: **Social Science History** (Cambridge University Press), if the framing leads with the quantitative method; an earlier check found a 12,000-word limit including notes and references, not reconfirmed at review.

## Summary of the contribution (for a cover letter)

Commemorative street names are a classic object of political geography, but most work studies renaming by states at moments of rupture, and recent quantitative work relates present-day names to present-day outcomes. This paper asks whether the dispersed, mostly private naming of Victorian streets carried partisan content. Using a national OpenStreetMap table of {N['streets']:,} commemorative streets, a name table with a pre-set test for ambiguous names, and {R['sample']['towns']} towns linked to general election results from 1868 to 1900, it finds that party street names were overwhelmingly Liberal everywhere, and that more Liberal towns had a modestly more Liberal mix ({E['pp_per10']:.1f} points per 10 points of vote, 95% CI {E['lo_pp']:.1f} to {E['hi_pp']:.1f}) in a model specified in a written plan before the outcome was examined. A later-period placebo is null, but the association is fragile (it is carried by Beaconsfield names and is not significant in several planned alternatives), which the paper reports in full. The design is correlational. Data, code and the name table are openly released.
"""
open(f"{ROOT}/release/paper/cover_note.md", "w").write(cover)
for f in (f"{ROOT}/README.md", f"{ROOT}/reddit/post.md", f"{ROOT}/release/paper/cover_note.md"):
    t = "\n".join(l for l in open(f).read().splitlines() if not l.startswith("|---"))
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in t, (f, bad)
print("readme", len(readme.split()), "words; cover", len(cover.split()))
