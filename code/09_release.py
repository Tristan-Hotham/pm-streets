"""Step 9: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24092657, https://doi.org/10.5281/zenodo.24092657 and https://blog.tristanhotham.com/2026/10/31/pm-streets/ stay as placeholders for the publisher."""
import shutil, zipfile, importlib.util
from PIL import Image
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "07_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks (and rebuilds index.html)
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_PM_Streets"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else
              (f"{100 * get(R, m.group(1)):.1f}" if m.group(3) == "pp" else fmt(get(R, m.group(1)), m.group(3))), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP, set(re.findall(r"\{\{([^|}]+)\}\}", post))
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
assert AI in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
C = R["count"]
meta = {"title": "Gladstone Road or Disraeli Street? Victorian street names and the party the town voted for",
        "slug": "pm-streets",
        "excerpt": f"Victorian builders named thousands of streets after statesmen. I mapped them all: {C['gladstone']} Gladstones against {C['beaconsfield'] + C['disraeli']} Beaconsfields and Disraelis. Liberal names won almost everywhere, and Liberal towns chose them only a little more often.",
        "seo_description": f"Every UK street named after a Victorian statesman, mapped: {C['gladstone']} Gladstones, {C['beaconsfield'] + C['disraeli']} Beaconsfields and Disraelis. Did names follow the vote?",
        "tags": ["maps", "street names", "history", "Gladstone", "Disraeli", "Victorian", "elections", "political memory", "OpenStreetMap", "data visualisation"],
        "header_alt": f"Title card reading 'Gladstone Road or Disraeli Street?' in orange and blue beside a map of Great Britain with orange dots for Liberal street names and blue dots for Conservative ones, and the line {C['gladstone']} Gladstones, {C['beaconsfield']} Beaconsfields, {C['disraeli']} Disraelis."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith((".pyc", ".png")) or fn == "__pycache__":
            continue
        z.write(os.path.join(ROOT, "code", fn), f"{SLUG}/code/{fn}")
    for fn in sorted(os.listdir(DATA)):
        if fn.endswith(".json") and fn != "results.json":
            continue
        z.write(os.path.join(DATA, fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "NOTES.md"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
    z.write(os.path.join(REL, "paper", "cover_note.md"), f"{SLUG}/release/paper/cover_note.md")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("$", "")
assert "\\" not in ab, ab
zmeta = {"title": "Gladstone Road or Disraeli Street? Partisan Commemoration in the Street Names of Victorian Britain",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/pm-streets/}}.</p><p>Sources: OpenStreetMap contributors (ODbL) via QLever; UK Parliament and House of Commons Library election results (Open Parliament Licence v3.0); Wikidata (CC0); ONS boundaries (OGL v3.0). Derived street data under the ODbL; text and figures CC BY 4.0; code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["street names", "commemoration", "political memory", "Gladstone", "Disraeli", "Victorian elections", "electoral geography", "OpenStreetMap"],
         "license": "cc-by-4.0", "language": "eng",
         "notes": "Text and figures CC BY 4.0; code MIT; street tables derived from OpenStreetMap, ODbL; election-derived tables contain Parliamentary information under the Open Parliament Licence v3.0.",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.openstreetmap.org/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = json.dumps(zmeta, ensure_ascii=False) + json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
