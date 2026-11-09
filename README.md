# Gladstone Road or Disraeli Street?

Partisan commemoration in the street names of Victorian Britain. Every OpenStreetMap road in the UK whose name contains a politician's or Victorian commemorative word (28,029 ways, joined into 15,593 streets), a documented name table with a tested rule for ambiguous names, and 160 British towns linked to the general election results of the seats named after them, 1868 to 1900. Do towns' Gladstone Roads and Beaconsfield Streets follow how the towns voted?

Interactive page: https://maps.tristanhotham.com/pm-streets/
Paper: https://doi.org/10.5281/zenodo.24092657
Blog post: https://blog.tristanhotham.com/2026/10/31/pm-streets/
Code and data: https://github.com/Tristan-Hotham/pm-streets

## Headline results

- Liberal names dominate: Gladstone 405, Cobden 150, Palmerston 171, John Bright 100; Beaconsfield 221, Disraeli 38. 77.3% of main-set party street names are Liberal, about 3.4 to 1, in Conservative as well as Liberal towns (Blackburn: 37% Liberal vote, 5 Liberal names, 0 Conservative). London is the exception (62 Liberal, 41 Conservative).
- Pre-specified main model (street-level linear probability model, region fixed effects, SE clustered by town; plan in NOTES.md, written before the outcome models): each 10 points of Liberal vote 1868 to 1900 goes with 5.9 (95% CI 0.4 to 11.4) points more Liberal names; p = 0.035; N = 610 streets in 160 towns.
- Survives randomisation inference (p = 0.019), leaving out any region (4.9 to 7.5), London, the five biggest towns, and most measurement choices (10 of 11 checks with intervals above zero). Placebo: the vote of 1945 to 1970 does not predict the names (Labour 0.3 (95% CI -3.7 to 4.3), Liberal -1.4 (95% CI -9.2 to 6.4)).
- Fragile: not significant at the town level unweighted (6.3 (95% CI -1.3 to 13.9)), with the share of seats won (0.4 (95% CI -1.5 to 2.3)), in 1868 boroughs only, in either half of the period, or in England and Wales only. Exploratory: carried by Beaconsfield names; with Disraeli as the only Conservative name the estimate is 0.0 (95% CI -2.3 to 2.3), too few streets to tell. A faint trace on top of a national Liberal street culture. Correlational.
- Timing: within towns, Gladstone streets rank 0.58 from centre (0) to edge (1), between Crimean (0.51) and Boer War (0.61) battle streets; Labour names (205 streets) at 0.72.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | Interactive page: MapLibre on OpenFreeMap Positron; streets coloured by party, towns ringed by Liberal vote; name filter, layers panel, search, popups, full-screen. |
| `header.png` | Social card, 1200 x 630. |
| `data/streets.csv` | Every matched street (15,593): name, key, person, party, class, highway types, position, county, region, town, co-location and place diagnostics, OSM way ids. ODbL. |
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
- Names: main set Gladstone, Cobden, Palmerston, John Bright (Liberal) and Disraeli, Beaconsfield (Conservative; 17 Beaconsfield streets within 25 km of Beaconsfield, Bucks set aside). Tested names admitted to an extended set by a pre-set rule (another party street within 400 m at half the Gladstone rate, and under 25% near a same-name place): Peel, Rosebery, Salisbury, Balfour, Hartington, Granville, Chamberlain, Macmillan pass; Baldwin, Churchill, Bevan, Hardie fail.
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

Hotham, T. (2026). Gladstone Road or Disraeli Street? Partisan Commemoration in the Street Names of Victorian Britain. Zenodo. https://doi.org/10.5281/zenodo.24092657

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
