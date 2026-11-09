"""The name table: every commemorative word searched in street names, the person or thing it is taken to mean, a party
for politicians, the years the person was prominent, and a class:
  main     unambiguous party-political name used in the main test
  test     party politician whose name is also a place, estate or common surname; enters the extended set only if it
           passes the pre-set co-location and place rule (NOTES.md)
  amb      set aside: mostly a place, a royal, a general or a common surname (diagnostic reported only)
  labour   Labour-movement politicians (H3)
  royal, hero, reform   non-party commemoration (controls and placebos)
Party codes: LIB Liberal, CON Conservative, LU Liberal Unionist, LAB Labour, PEEL Conservative (Peelite free trader),
WHIG Whig or Whig-Liberal before 1859, TORY Tory before 1834, IRN Irish Nationalist, '' not a party figure.
Regexes are applied to the lower-cased name as whole words. Order matters only for overlaps (Baden-Powell before Powell,
Lloyd George, Keir Hardie, Aneurin Bevan, Ramsay MacDonald before the bare surnames)."""

# key, label, regex, party, cls, (from, to) prominent years, note
N = [
    # main Liberal set
    ("gladstone", "Gladstone", r"gladstone", "LIB", "main", (1843, 1898), "W. E. Gladstone, Liberal prime minister 1868 to 1894"),
    ("cobden", "Cobden", r"cobden", "LIB", "main", (1838, 1865), "Richard Cobden, Anti-Corn Law League, Liberal radical"),
    ("palmerston", "Palmerston", r"palmerston", "LIB", "main", (1830, 1865), "Viscount Palmerston, Liberal prime minister 1855 to 1865"),
    ("bright", "John Bright", r"john bright|bright(?= (?:street|road|terrace|place|grove|square|avenue)\b)", "LIB", "main", (1843, 1889),
     "John Bright, Anti-Corn Law League, Liberal radical; bare Bright only with a traditional street word"),
    # main Conservative set
    ("disraeli", "Disraeli", r"disraeli", "CON", "main", (1846, 1881), "Benjamin Disraeli, Conservative prime minister 1868, 1874 to 1880"),
    ("beaconsfield", "Beaconsfield", r"beaconsfield", "CON", "main", (1876, 1881), "Disraeli's title as Earl of Beaconsfield from 1876; also a Buckinghamshire town"),
    # tested party names
    ("peel", "Peel", r"peel", "PEEL", "test", (1822, 1850), "Sir Robert Peel, Conservative prime minister; also Peel (Isle of Man), Peel Park, Peel Hall"),
    ("rosebery", "Rosebery", r"rosebery", "LIB", "test", (1885, 1896), "Earl of Rosebery, Liberal prime minister 1894 to 1895; also Rosebery estates"),
    ("salisbury", "Salisbury", r"salisbury", "CON", "test", (1868, 1902), "Marquess of Salisbury, Conservative prime minister; also the city"),
    ("balfour", "Balfour", r"balfour", "CON", "test", (1885, 1911), "A. J. Balfour, Conservative prime minister 1902 to 1905; also a Scottish surname"),
    ("hartington", "Hartington", r"hartington", "LU", "test", (1875, 1891), "Marquess of Hartington, Liberal then Liberal Unionist leader; Cavendish estate name"),
    ("granville", "Granville", r"granville", "LIB", "test", (1859, 1891), "Earl Granville, Liberal foreign secretary; also an estate name"),
    ("chamberlain", "Chamberlain", r"chamberlain", "LU", "test", (1876, 1914), "Joseph Chamberlain (Liberal, then Liberal Unionist), or Neville"),
    ("baldwin", "Baldwin", r"baldwin", "CON", "test", (1923, 1937), "Stanley Baldwin, Conservative prime minister; common surname"),
    ("churchill", "Churchill", r"churchill", "CON", "test", (1940, 1955), "Winston Churchill; also villages called Churchill"),
    ("macmillan", "Macmillan", r"macmillan", "CON", "test", (1957, 1963), "Harold Macmillan; common surname"),
    ("asquith", "Asquith", r"asquith", "LIB", "main20", (1908, 1916), "H. H. Asquith, Liberal prime minister 1908 to 1916"),
    ("bannerman", "Campbell-Bannerman", r"bannerman", "LIB", "main20", (1899, 1908), "Sir Henry Campbell-Bannerman, Liberal prime minister 1905 to 1908"),
    ("lloydgeorge", "Lloyd George", r"lloyd[- ]george", "LIB", "main20", (1908, 1922), "David Lloyd George, Liberal prime minister 1916 to 1922"),
    # Labour
    ("keirhardie", "Keir Hardie", r"keir[- ]hardie", "LAB", "labour", (1892, 1915), "Keir Hardie, first Labour leader"),
    ("lansbury", "Lansbury", r"lansbury", "LAB", "labour", (1910, 1940), "George Lansbury, Labour leader 1932 to 1935, Poplar"),
    ("attlee", "Attlee", r"attlee", "LAB", "labour", (1935, 1955), "Clement Attlee, Labour prime minister 1945 to 1951"),
    ("aneurinbevan", "Aneurin Bevan", r"(?:aneurin|nye)[- ]bevan", "LAB", "labour", (1929, 1960), "Aneurin (Nye) Bevan, minister of health 1945 to 1951"),
    ("ramsaymacdonald", "Ramsay MacDonald", r"ramsay[- ]mac ?donald", "LAB", "labour", (1911, 1935), "Ramsay MacDonald, Labour prime minister"),
    ("bevan", "Bevan", r"bevan", "LAB", "test", (1929, 1960), "bare Bevan: Aneurin Bevan or a Welsh surname"),
    ("hardie", "Hardie", r"hardie", "LAB", "test", (1892, 1915), "bare Hardie: Keir Hardie or a Scottish surname"),
    # set aside
    ("derby", "Derby", r"derby", "CON", "amb", (1846, 1868), "Earl of Derby, Conservative prime minister; mostly the city"),
    ("melbourne", "Melbourne", r"melbourne", "WHIG", "amb", (1834, 1841), "Viscount Melbourne; also Melbourne (Derbyshire, Australia)"),
    ("aberdeen", "Aberdeen", r"aberdeen", "PEEL", "amb", (1852, 1855), "Earl of Aberdeen; mostly the city"),
    ("liverpool", "Liverpool", r"liverpool", "TORY", "amb", (1812, 1827), "Earl of Liverpool; mostly the city"),
    ("russell", "Russell", r"russell", "WHIG", "amb", (1832, 1866), "Lord John Russell; common surname, Bedford estate"),
    ("grey", "Grey", r"grey", "WHIG", "amb", (1830, 1834), "Earl Grey; also a colour and surname"),
    ("gordon", "Gordon", r"gordon", "", "amb", (1884, 1885), "General Gordon, or the clan and surname"),
    ("wilson", "Wilson", r"wilson", "LAB", "amb", (1964, 1976), "Harold Wilson; common surname"),
    ("eden", "Eden", r"eden", "CON", "amb", (1955, 1957), "Anthony Eden; also the garden and rivers"),
    ("pitt", "Pitt", r"pitt", "TORY", "amb", (1783, 1806), "William Pitt; also a surname and a pit"),
    ("canning", "Canning", r"canning", "TORY", "amb", (1822, 1827), "George Canning; also canning works and towns"),
    ("thatcher", "Thatcher", r"thatcher", "CON", "amb", (1979, 1990), "Margaret Thatcher; also the trade and surname"),
    ("macdonald", "MacDonald", r"mac ?donald", "LAB", "amb", (1911, 1935), "bare MacDonald: Ramsay MacDonald or a common surname"),
    ("parnell", "Parnell", r"parnell", "IRN", "reform", (1875, 1891), "Charles Stewart Parnell, Irish Nationalist leader"),
    # royals
    ("victoria", "Victoria", r"victoria", "", "royal", (1837, 1901), "Queen Victoria (or places named after her)"),
    ("albert", "Albert", r"albert", "", "royal", (1840, 1861), "Prince Albert (or King Albert of the Belgians, or a forename)"),
    ("alexandra", "Alexandra", r"alexandra", "", "royal", (1863, 1925), "Alexandra, Princess of Wales from 1863, Queen from 1901"),
    # military and imperial heroes
    ("badenpowell", "Baden-Powell", r"baden[- ]?powell|baden", "", "hero", (1900, 1941), "Robert Baden-Powell, Mafeking 1900, the Scouts"),
    ("powell", "Powell", r"powell", "", "amb", (0, 0), "bare Powell: surname"),
    ("nelson", "Nelson", r"nelson", "", "hero", (1798, 1805), "Admiral Nelson (or a surname, or Nelson in Lancashire)"),
    ("wellington", "Wellington", r"wellington", "TORY", "hero", (1808, 1852), "Duke of Wellington (or the Shropshire and Somerset towns)"),
    ("roberts", "Roberts", r"roberts", "", "hero", (1880, 1914), "Field Marshal Roberts (or a common surname)"),
    ("kitchener", "Kitchener", r"kitchener", "", "hero", (1898, 1916), "Lord Kitchener"),
    ("livingstone", "Livingstone", r"livingstone", "", "hero", (1857, 1873), "David Livingstone (or Livingston, a surname)"),
    # reformers and radical heroes
    ("wilberforce", "Wilberforce", r"wilberforce", "", "reform", (1787, 1833), "William Wilberforce, abolition of the slave trade"),
    ("shaftesbury", "Shaftesbury", r"shaftesbury", "", "reform", (1833, 1885), "7th Earl of Shaftesbury, factory reform (also the Dorset town)"),
    ("plimsoll", "Plimsoll", r"plimsoll", "", "reform", (1868, 1880), "Samuel Plimsoll, the load line"),
    ("oastler", "Oastler", r"oastler", "", "reform", (1830, 1861), "Richard Oastler, the ten hours movement"),
    ("cromwell", "Cromwell", r"cromwell", "", "reform", (1642, 1658), "Oliver Cromwell, a Nonconformist and Liberal hero"),
    ("hampden", "Hampden", r"hampden", "", "reform", (1637, 1643), "John Hampden, ship money"),
    ("garibaldi", "Garibaldi", r"garibaldi", "", "reform", (1860, 1864), "Giuseppe Garibaldi, visited England 1864"),
    ("kossuth", "Kossuth", r"kossuth", "", "reform", (1849, 1851), "Lajos Kossuth, visited England 1851"),
    ("chartist", "Chartist", r"chartists?", "", "reform", (1838, 1848), "the Chartists"),
    ("tolpuddle", "Tolpuddle", r"tolpuddle", "", "reform", (1834, 1834), "the Tolpuddle Martyrs"),
    ("mandela", "Mandela", r"mandela", "", "reform", (1985, 2013), "Nelson Mandela"),
]
NKEY = {n[0]: n for n in N}
PARTY_NAMES = [n[0] for n in N if n[4] == "main"]
LIB_MAIN = [n[0] for n in N if n[4] == "main" and n[3] == "LIB"]
CON_MAIN = [n[0] for n in N if n[4] == "main" and n[3] == "CON"]
LABOUR = [n[0] for n in N if n[4] == "labour"]
ROYAL = [n[0] for n in N if n[4] == "royal"]
HERO = [n[0] for n in N if n[4] == "hero"]
