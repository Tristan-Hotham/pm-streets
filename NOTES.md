# pm-streets: working notes

Brief: /home/claude/work/new11/BRIEFS.md section 1 (+ shared rules new8/new9/new10 BRIEFS tops, /home/claude/newdata/BRIEF.md).
Format refs: studies/battle-moons, studies/sea-sunsets (release layout), studies/battle-streets (same kind of data, code layout).
Work files: /home/claude/scratch/pm-streets (delete at the end by exact path).

## Analysis plan (written before any outcome model was run)

Written after reading the raw files and counting name tokens only; no vote data had been joined to street data.

### Question
Victorian builders, landowners and councils named streets after political heroes. Do a town's Gladstone and Cobden
streets, against its Beaconsfield and Disraeli streets, follow how the town voted?

### Hypotheses
- H1 (main). Across towns, the Liberal share of a town's party-political streets rises with the Liberal share of the
  town's vote at general elections 1868 to 1900.
- H2 (timing). Within towns, Gladstone and Beaconsfield streets lie at the same distance rank as streets named after
  late Victorian battles (between the Crimean War 1854 to 1856 and the Boer War 1899 to 1902); Labour names lie farther out
  than First World War battle streets.
- H3 (Labour era, secondary). Towns with streets named after Labour figures (Keir Hardie, Lansbury, Attlee, Aneurin Bevan)
  had higher Labour vote shares 1945 to 1970.

### Name table (code/names.py), fixed before the outcome
- Main Liberal set: Gladstone, Cobden, Palmerston, John Bright (Bright only as "John Bright ..." or "Bright" + a
  traditional street word: Street, Road, Terrace, Place, Grove, Square, Avenue).
- Main Conservative set: Disraeli, Beaconsfield (Beaconsfield streets within 25 km of the town of Beaconsfield,
  Buckinghamshire, set aside as possible route names).
- Tested names (party politicians whose names are also places, estates or surnames): Peel, Rosebery, Salisbury, Balfour,
  Hartington, Granville, Chamberlain, Baldwin, Churchill, Macmillan, plain Bevan, plain Hardie. Pre-set rule: a tested
  name joins the extended set if (i) the share of its streets with a main-set street of another name within 400 m is at
  least half the same share for Gladstone streets, and (ii) fewer than 25% of its streets lie within 10 km of a
  settlement whose name contains the word. Reported for every name; the main result uses the main set only.
- Set aside without use (mostly places, royals, generals or common surnames; diagnostic reported): Derby, Melbourne,
  Aberdeen, Liverpool, Russell, Grey, Gordon, Wilson, Eden, Pitt, Canning, Thatcher, plain MacDonald, plain Powell.
- Non-party commemorative sets (for controls and placebos): royals (Victoria, Albert, Alexandra), military and imperial
  heroes (Nelson, Wellington, Roberts, Kitchener, Baden-Powell, Livingstone), reformers and radical heroes (Wilberforce,
  Shaftesbury, Plimsoll, Oastler, Cromwell, Hampden, Garibaldi, Kossuth, Chartist, Tolpuddle, Parnell, Mandela).
- Labour set: Keir Hardie, Lansbury, Attlee, Aneurin or Nye Bevan, Ramsay MacDonald.

### Data construction
- Streets: OSM features with a road highway value (trunk, primary, secondary, tertiary and links, unclassified,
  residential, living_street, pedestrian, service, road); bus stops, footways, paths, cycleways, tracks, steps and other
  features dropped. Names matched as whole words; pieces of one street (same normalised name, first points chaining
  within 150 m) merged.
- Towns: Wikidata towns and cities (present population as a size proxy). A street belongs to the nearest town within
  r = max(3, 1.5 * sqrt(pop / 10,000)) km (distance divided by r smallest wins); Greater London counted as London.
- Votes: constituencies 1868 to 1900 whose names are a town's name, or the town's name plus a division word (Leeds
  Central, East Bradford), linked to the town. Liberal share = LIB votes / (LIB + CON + LU) votes in contested elections,
  averaged over the town's contests. Liberal Unionists count with the Conservatives (they were allied from 1886).
  Northern Ireland left out (different party system). University seats left out.

### Main specification (H1)
Street-level linear probability model: each main-set party-political street in a matched town; outcome 1 if a Liberal
name; regressor the town's Liberal vote share 1868 to 1900 (per 10 percentage points); controls log town population,
region fixed effects (nine English regions, Wales, Scotland), log(1 + royal-named streets in the town) as a proxy for the
Victorian street stock, traditional street word. Standard errors clustered by town. Effect reported per 10 points with 95% CI.

### Alternatives, robustness, placebos (planned)
- Alternative specifications: town-level binomial logit (Liberal names out of party names) with region FE, SE clustered
  by county; unweighted town OLS on the share (towns with 2+ party streets); Liberal share of seats won 1868 to 1900
  (uncontested seats included); 1868 to 1880 and 1885 to 1900 separately; no controls.
- Placebo 1 (later period): the same model with the Liberal share and the Labour share 1945 to 1970 in place of the
  Victorian vote. If the later shares predict the names as well as the Victorian share, the result reflects lasting local
  political culture rather than naming that followed contemporary politics.
- Placebo 2 (non-political commemoration): town-level Poisson models of royal-named streets and of dated battle streets
  (battle-streets data) on the Liberal vote with log population and region: expected null. A positive link would mean
  Liberal towns simply named more Victorian streets after anything.
- Randomisation inference: town vote shares shuffled within regions (2,000 draws).
- Region and outliers: leave one region out; without London; without the five towns with most party streets; Cook's
  distance check at town level.
- Measurement: merge distance 600 m; town radius x0.7 and x1.4; extended name set; Peel added as Conservative;
  traditional street words only; streets of one party within 300 m of each other in a town counted once (builders named
  groups of streets together); Gladstone streets left out (does the result rest on one name?).
- What counts against H1: a coefficient at or below zero, or a 95% CI that includes zero with a point estimate under
  1 point per 10 points of vote; or Placebo 1 as strong as the main estimate (then the timing claim fails).

### H2 and H3 methods
- H2: within-town distance percentile (distance from the town point) for party streets pooled with battle streets of
  battle-streets (traditional street words), towns with 3 or more such streets; means with town-cluster bootstrap 95% CIs.
- H3: town-level logit of having any Labour-named street on the Labour share 1945 to 1970, log population, region FE,
  Victorian stock; then adding the Liberal share 1868 to 1900 (does the Victorian vote still matter?). Correlational.

### Labelled as exploratory if added later
(listed below as they come)

## Log
- 01: 34,293 raw rows; 28,069 kept as road highway values; 28,029 matched ways -> 15,593 streets after joining pieces
  within 150 m (13,182 at 600 m). "Back X Street" normalised to "X Street" before joining (back lanes of terraces).
  40 bare "Bright" names without a traditional street word left out by rule (Bright Gardens, Bright Close, Alice Bright Lane, Jacob Bright Mews).
- 02: 86.6% of streets fall in a town. Name diagnostics (data/name_diagnostics.csv): Gladstone co-location rate (another
  main-set party street within 400 m) 17.8%; Victoria 6.5%, Liverpool 2.8%, Wilson 3.0% (the baseline for unrelated names).
  Pre-set rule: tested names passing = Peel, Rosebery, Salisbury, Balfour, Hartington, Granville, Chamberlain, Macmillan;
  failing = Baldwin, Churchill, plain Bevan, plain Hardie. The extended Victorian set therefore adds Rosebery and Granville
  (Liberal) and Salisbury, Balfour, Hartington, Chamberlain (Unionist: Hartington and Chamberlain coded with the
  Conservatives, as Liberal Unionists after 1886). Macmillan passes but is a twentieth-century name (19 streets), not used.
  Peel is used only in its own check (as Conservative).
- Samples read by eye (12 random per tested name with town, highway, nearest other party street): Salisbury includes
  route names (Salisbury Road, trunk, Fordingbridge) the 10 km place rule does not catch; Back Salisbury Street Bolton
  sits 107 m from another party street (a statesmen group). Peel includes Peel Park and Peel Hall names. Rosebery
  and Balfour look like 1880s to 1900s terraces in towns. Beaconsfield: 17 streets within 25 km of Beaconsfield, Bucks set aside.
- 03: 836 constituency-town links (data/links.csv), reviewed by eye. Fixed: North, South, Mid, North West and South East
  Durham are county divisions (were matched to Durham city); "A and B" seats split into both towns. Links with the
  source point more than 4 km from the town were all read (source points for some seats are rough). 297 towns with a
  Victorian Liberal two-party share; 197 were parliamentary boroughs in 1868 to 1880.
- 04 (planned models run once, as written): main LPM b = 0.059 per 10 points (95% CI 0.004 to 0.114), p = 0.035,
  610 streets in 160 towns, mean Liberal share of names 0.75. Weak: town-level unweighted OLS 0.063 (CI -0.013 to 0.139);
  seats-won share 0.004 (n.s.); 1868 to 1880 and 1885 to 1900 alone n.s.; 1868 boroughs only n.s.; England and Wales only
  n.s. (0.052). Placebo later vote null (Lib 1945 to 1970 -0.014, Lab 0.003). RI p = 0.019. LORO 0.049 to 0.075.
  Placebo counts: royal IRR 1.04 (n.s.), battle 0.94 (n.s.), but all party streets IRR 1.16 (p 0.03): Liberal towns had
  more party streets overall. Timing: Gladstone 0.58 between Crimea 0.51 and Boer 0.61; Labour names 0.72 beyond WWI 0.65.
  H3 Labour names: LPM 0.042 per 10 points of Labour 1945 to 1970 (CI -0.001 to 0.086), logit p 0.04; correlational.
  Bug fixed before reading results: variable name clash (C counties vs patsy C()). Binomial model run as street-level logit
  (same likelihood as the town-level binomial).

## References verified (WebSearch/WebFetch, 2026)
Each checked against a publisher, library catalogue, RePEc or institutional record (title, authors, year, venue, volume, pages, DOI).
- Azaryahu 1996 EPD 14(3) 311-330 doi 10.1068/d140311 (Haifa CRIS); Azaryahu 1997 Political Geography 16(6) 479-493 doi 10.1016/S0962-6298(96)00053-4 (Haifa CRIS)
- Alderman 2000 Professional Geographer 52(4) 672-684 doi 10.1111/0033-0124.00256; Alderman 2003 Area 35(2) 163-173 doi 10.1111/1475-4762.00250 (record pages; journal from DOI ISSN)
- Rose-Redwood, Alderman, Azaryahu 2010 PHG 34(4) 453-470 doi 10.1177/0309132509351042
- Light 2004 JHG 30(1) 154-172 doi 10.1016/S0305-7488(02)00102-0; Light and Young 2014 Annals AAG 104(3) 668-685 doi 10.1080/00045608.2014.892377
- Oto-Peralias 2018 JEG 18(1) 187-211 doi 10.1093/jeg/lbx030 (RePEc; St Andrews news: Scottish constituencies, British-themed street names)
- Gutierrez-Mora and Oto-Peralias 2022 EPB 49(6) 1792-1809 doi 10.1177/23998083211068844
- Bancilhon, Constantinides, Bogucka, Aiello, Quercia 2021 PLoS ONE 16(6) e0252869 doi 10.1371/journal.pone.0252869
- Villamil and Balcells 2021 Research & Politics 8 doi 10.1177/20531680211058550 (DOAJ)
- Biagini 1992 Liberty, Retrenchment and Reform, CUP; Joyce 1980 Work, Society and Politics (Harvester; Rutgers US ed.);
  Vincent 1966 The Formation of the Liberal Party 1857-1868, Constable; Pelling 1967 Social Geography of British Elections 1885-1910, Macmillan;
  Cox 1987 The Efficient Secret, CUP; Matthew 1986 Gladstone 1809-1874, Clarendon; Parry 1986 Democracy and Religion, CUP;
  Hinde 1987 Richard Cobden: A Victorian Outsider, Yale (last three from the JBS review title); Lawrence 1998 Speaking for the People, CUP;
  Pugh 1985 The Tories and the People 1880-1935, Blackwell; Windscheffel 2007 Popular Conservatism in Imperial London, Boydell/RHS;
  Hanham 1959 Elections and Party Management, Longmans; Howe 1997 Free Trade and Liberal England, Clarendon (CiNii);
  Trentmann 2008 Free Trade Nation, OUP; Pickering and Tyrrell (eds) 2004 Contested Sites, Ashgate; Dyos 1961 Victorian Suburb, Leicester UP;
  Wald 1983 Crosses on the Ballot, Princeton UP; Tanner 1990 Political Change and the Labour Party 1900-1918, CUP (Loughborough catalogue)
- Parry 2000 Disraeli and England, Historical Journal 43(3) 699-728 (journal index)
- Matthew, McKibbin and Kay 1976 EHR 91, 723-752 (catalogue)
- Craig 1974 British Parliamentary Election Results 1885-1918, Macmillan doi 10.1007/978-1-349-02298-4; Craig 1989 BPER 1832-1885 2nd ed, Parliamentary Research Services
- Haklay 2010 EPB 37(4) 682-703 doi 10.1068/b35097; Bast and Buchhold 2017 CIKM 647-656 doi 10.1145/3132847.3132921
- Whitehand 1972 Trans IBG 56, 39-55; Cameron and Miller 2015 JHR 50(2) 317-372; Abadie, Athey, Imbens, Wooldridge 2023 QJE 138(1) 1-35
- Not used: Conzen 1960 (not re-verified), Arregui Alegria 2026 working paper (unrefereed). Crossref API and some publisher pages were blocked.
- Journals: Political Geography (Elsevier, hybrid, 11,000 words max), Urban History (CUP, 10,000 incl. notes and tables),
  Social Science History (CUP, 12,000 incl. notes and references, abstract 250). All publish subscription articles without an APC.

## Exploratory (added after the planned models)
- Name-by-name comparison against Beaconsfield and Disraeli: Gladstone 6.2 (-1.4 to 13.8), Cobden and Bright 9.9 (1.1 to 18.6), Palmerston 6.5 (-1.0 to 14.1). Labelled exploratory in the paper.

## Status
- All files built: index.html (QA desktop 1280 and phone 390, 0 console errors), header.png, paper PDF (25 pages, about 7,100 words
  before references, https://doi.org/10.5281/zenodo.24092657 placeholder filled by 08_paper.py from env DOI), cover_note.md, blog post (6 figures), Zenodo zip and
  metadata, collage, looping GIF (reddit/pm_streets.gif), README, LICENSE.
- Fixed in QA: map legend wrapping; name chips hidden on phones so the Layers button shows.
- Claim checked by web: the MBW (from 1857) and LCC renamed many London streets, last large round in the late 1930s.

## Independent review (2026)
Referee and fact-check pass. Scratch in /home/claude/scratch/review-pm-streets (deleted afterwards).

Reproduction
- Re-ran 01 to 05 from the raw inputs into a fresh work folder: results.json, models.csv, towns.csv and names.csv identical to the built versions (every value). Main: 5.9 points per 10 (0.4 to 11.4), p 0.035, 610 streets, 160 towns; RI p 0.019.
- H3 logit gave a convergence warning; refitted with BFGS it converges to the same estimate (0.685, p 0.041), so the reported logit p stands.

Name table and merging (sampled by eye)
- Gladstone, Cobden, Disraeli: almost all ordinary street forms. Bright: concentrated in Lancashire, Greater Manchester and West Yorkshire (fits John Bright); 8 in Northern Ireland (Bright is also a County Down place; NI is outside the models). Odd forms in the main sample: 22 of 610 (business parks, bridges, "View" names, bare names, Main Bright Road, Steel Bright Road); dropping them gives 6.3 (0.8 to 11.8).
- Palmerston: London 30, Hampshire 12 (Fareham and Portsmouth, near the Palmerston forts); still a commemoration of the man, but a referee may question coding him as a party Liberal. Without Palmerston 6.5 (0.2 to 12.8).
- Beaconsfield: route rule works (bypass and interchange names flagged); 8 bare "Beaconsfield" residential names remain (probably house or estate names). KEY: without Beaconsfield (Disraeli the only Conservative name) the estimate is 0.0 (-2.3 to 2.3, 481 streets, 95% Liberal). Too few Disraeli streets to rule out a proportional effect (about 1 point), but the association is carried by Beaconsfield names. Added as exploratory (results.json "review").
- Merging: the 150 m rule chains first points only, so long multi-piece streets stay split: 145 of 610 main-sample streets have a same-named twin in the same town within 600 m. The planned 600 m check (5.8, 529 streets) covers it; noted in the paper.
- Town assignment: London's population radius is about 44 km; 26 streets outside Greater London are assigned to London, only 1 in the main sample. Region FE use the street's county, not the town's; differs for 1 street (estimate unchanged, 5.9).
- Town to seat matching: links read by eye. From 1885 many towns are represented by county divisions named after them (Accrington, Barnsley, Sevenoaks, Woodbridge, Biggleswade, Epsom and others), not boroughs; their vote includes the countryside. The planned 1868-boroughs check (3.8, -2.4 to 10.0) is the cleanest test of the town hypothesis and is not significant. Now said explicitly in the paper.

Errors fixed (paper, blog, page, README, Reddit post, cover note, Zenodo text)
- "Pre-registered" was wrong (no public registration): now "pre-specified in a written plan".
- Author line now "Dr Tristan Hotham".
- "London ... the most Conservative mix of any large town" and "London is the most Conservative" were false (Bolton and Gateshead 3 of 6 and 4 of 8 Conservative): now "more Conservative names than any other town".
- "Lansbury names are concentrated in East London" false (14 of 85): reworded.
- "disappears at the town level without weights" wrong (same size, 6.3, wider CI): reworded.
- Placebo overclaimed ("names follow the vote of their own time"): the later Liberal CI includes the main estimate; now "consistent with", in paper, blog and page.
- Timing overclaimed ("built in the 1870s to 1890s", "exactly the same place"): softened everywhere.
- LPM described as "equivalent" to the weighted town regression (not exact, street-level control): fixed; added why the street weighting was planned and that the unweighted town model answers H1 with towns equal.
- Misattributions: Tanner (1990) cited for the franchise factor (he qualified it): fixed. Haklay (2010) cited for "close to complete" OSM coverage (he found it incomplete then): fixed. Whitehand (1972) cited for battle-street clock: citation removed there. Dyos and Vincent claims about who named streets and freehold land society names softened.
- Clearance-bias sentence was wrong (losses bias a share only if they differ by party): fixed.
- Empty "Timing and Labour" subsection heading with its text misplaced under Threats: fixed. Section roadmap numbering wrong: fixed. "Scotland's ten towns" now filled from results.json. Abstract trimmed to 248 words; -0.0 shown as 0.0.
- GIF: frame counts were GB-only while captions implied UK (Gladstone 404 vs 405): captions now say Great Britain; added a clean final frame with all groups at full strength and a full key. Collage legends now say "in GB".
- Cover note: Urban History limit reconfirmed (10,000 words inclusive of footnotes and tables); Elsevier guide pages (JHG, Political Geography) and the SSH page could not be reached at review, so those limits are marked as not reconfirmed. Word count updated (about 7,700 before references).

References re-verified at review (WebSearch/WebFetch): Parry 2000 HJ DOI 10.1017/S0018246X99001326; Villamil and Balcells 2021 Research & Politics 8(4) (issue added); Whitehand 1972 Trans IBG 56, 39-55 (Birmingham publication list); Gutierrez-Mora and Oto-Peralias 2022 EPB 49(6) 1792-1809 (RePEc); Bancilhon et al. 2021 PLoS ONE e0252869 (DOAJ, ITU); Craig 1974 Macmillan DOI 10.1007/978-1-349-02298-4 (Springer); Oto-Peralias 2018 JEG 18(1) 187-211 and its Scottish identity finding (RePEc, St Andrews). Others rely on the builder's verification above (standard records, consistent with my knowledge); none found wrong.

Remaining referee concerns (not fixable with these data)
- Unit: H1 is about towns, but the main model weights towns by party streets (London 103 of 610); the unweighted town model is not significant. A referee may ask for the town-level model as primary.
- The result rests on Beaconsfield, the most ambiguous Conservative name (also a town and a house name).
- Constituency to town matching mixes boroughs with post-1885 county divisions; a borough flag from Craig would allow a clean borough-only sample with both periods.
- No Victorian population, Nonconformity, or date of building; present-day OSM names only (survivorship after clearance and renaming).
- Names are not dated: the battle-street clock is coarse; a referee would want a sample dated from Ordnance Survey 1:2500 editions or local street-naming minutes.
- Multiple alternative specifications without correction; the main p (0.035) is modest.
