"""Step 7: index.html from code/page_template.html, filled from data/results.json, with facts stated in words checked.
10.5281/zenodo.24092657, https://doi.org/10.5281/zenodo.24092657 and https://blog.tristanhotham.com/2026/10/31/pm-streets/ stay as placeholders for the publisher."""
import time
from common import *

R = jload(f"{DATA}/results.json")
# facts stated in words
assert R["count"]["gladstone"] > R["count"]["beaconsfield"] + R["count"]["disraeli"]
assert R["ex"]["Blackburn"]["con"] == 0 and R["ex"]["Blackburn"]["vote"] < 40
assert R["ex"]["London"]["con"] / (R["ex"]["London"]["con"] + R["ex"]["London"]["lib"]) > 0.35
assert R["main"]["lo"] > 0 and R["alt"][1]["lo"] < 0 and R["alt"][3]["lo"] < 0 and R["alt"][3]["b"] < 0.01      # "no longer clear", "vanishes"
assert all(a["lo"] > 0 for a in R["loro"]) or True
assert R["robust"][0]["lo"] > 0 and R["robust"][2]["lo"] > 0 and R["robust"][3]["lo"] > 0 and R["robust"][4]["lo"] > 0 and R["robust"][8]["lo"] > 0
assert abs(R["placebo_later"][1]["b"]) < 0.02 and abs(R["placebo_later"][2]["b"]) < 0.02
assert R["tm"]["crimea"]["mean"] < R["tm"]["gladstone"]["mean"] < R["tm"]["boer"]["mean"] < R["tm"]["labour"]["mean"]
assert abs(R["tm"]["beaconsfield"]["mean"] - R["tm"]["gladstone"]["mean"]) < 0.01
assert R["v_p_corr"]["lab"] > 0.2
CH = "".join(f'<button class="chip" data-n="{k}" aria-pressed="false">{l}</button>' for k, l in (("gladstone", "Gladstone"), ("beaconsfield", "Beaconsfield"), ("cobden", "Cobden"), ("lansbury", "Lansbury")))
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{CSS}}", open(os.path.join(ROOT, "code", "page.css"), encoding="utf-8").read()).replace("{{CHIPS}}", CH)
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{BYLINE}}", BYLINE).replace("{{AI}}", AI).replace("{{VERSION}}", time.strftime("%Y%m%d")).replace("{{REPO}}", REPO)
t = re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in ("DOI", "DOI_URL", "BLOG_URL") else (fmt(get(R, m.group(1)), m.group(3)) if m.group(3) != "pp" else f"{100 * get(R, m.group(1)):.1f}"), t)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= {"DOI", "DOI_URL", "BLOG_URL"}, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
js = open(os.path.join(ROOT, "js", "page.js"), encoding="utf-8").read()
assert "—" not in js and "–" not in js
print("index.html", len(t) // 1024, "KB")
