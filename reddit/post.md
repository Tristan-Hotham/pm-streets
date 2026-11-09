**Title:** [OC] Every UK street named after a Victorian statesman: 405 Gladstones vs 259 Beaconsfields and Disraelis. 77% of party street names are Liberal, even in Tory towns

**Body:**

Victorian builders named new streets after the statesmen of the day. I matched every OpenStreetMap road in the UK against a table of politicians, sorted out the false friends (a Derby Road usually goes to Derby), and linked 160 towns to how they voted from 1868 to 1900.

- Gladstone 405, Cobden 150, Palmerston 171, John Bright 100; Beaconsfield (Disraeli's title) 221, Disraeli 38.
- Tory Blackburn (37% Liberal vote) has 5 Liberal party names and no Conservative ones. London has the most Conservative names (41 of 103).
- Liberal towns did name a little more after Liberals: +5.9 points per 10 points of vote (95% CI 0.4 to 11.4), comparing towns in the same region. The 1945 to 1970 vote does not predict the names, but the link is fragile under some alternative measures.
- Gladstone streets sit between Crimean and Boer War battle streets in their towns, so probably mostly late Victorian. Labour names (205: Keir Hardie, Lansbury, Attlee, Bevan) sit farther out.

Interactive map: https://maps.tristanhotham.com/pm-streets/

**Source comment:**

Data: OpenStreetMap contributors (ODbL) via QLever; UK Parliament election results (Open Parliament Licence); Wikidata (CC0). Tools: Python (pandas, geopandas, statsmodels, matplotlib), MapLibre with OpenFreeMap tiles. Name table, tests and code: https://github.com/Tristan-Hotham/pm-streets
