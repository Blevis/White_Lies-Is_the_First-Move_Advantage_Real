"""Offline end-to-end check: mock the two network calls, run every notebook code cell."""
import os, sys, shutil, tempfile, glob
src = os.path.abspath(".")
tmp = tempfile.mkdtemp()
for f in glob.glob(src + "/*.py") + [src + "/main.ipynb"]:
    shutil.copy(f, tmp)
os.chdir(tmp); os.makedirs("data"); os.makedirs("figures")
sys.path.insert(0, tmp)
print("running in", tmp)
os.environ["LICHESS_TOKEN"] = "test"
import matplotlib; matplotlib.use("Agg")
import nbformat
import src.explorer as explorer, src.wiki_scrape as wiki_scrape

SPEED_DRAW = dict(bullet=.04, blitz=.05, rapid=.06, classical=.09)
SPEED_SC = dict(bullet=.512, blitz=.516, rapid=.522, classical=.530)
SHARE = {"": 1, "e2e4": .50, "e2e4,e7e5": .22, "d2d4": .33, "d2d4,d7d5": .13}

def mock_get(self, play="", speeds="blitz", ratings="1600", variant="standard"):
    band = int(ratings); n = int(2e6 * (1 + band / 1500)) + 5000
    N = int(n * SHARE[play]); D = int(N * SPEED_DRAW[speeds])
    s = SPEED_SC[speeds] + 0.00001 * band + (.003 if play.endswith("e5") else 0)
    W = int(N * s - D / 2)
    return dict(white=W, draws=D, black=N - W - D)
explorer.Explorer.get = mock_get

html = """<html><body><table><tr><th>ECO</th><th>Name</th></tr>
<tr><td>A00</td><td>Polish</td></tr><tr><td>B20</td><td>Sicilian</td></tr><tr><td>C00</td><td>French</td></tr>
<tr><td>C60</td><td>Ruy Lopez</td></tr><tr><td>D06</td><td>QGD</td></tr><tr><td>E60</td><td>KID</td></tr></table></body></html>"""
wiki_scrape.fetch_html = lambda *a, **k: html

nb = nbformat.read("main.ipynb", as_version=4)
ns = {}
for i, c in enumerate(nb.cells):
    if c.cell_type != "code":
        continue
    try:
        exec(compile(c.source, f"cell{i}", "exec"), ns)
    except Exception as e:
        print(f"FAIL cell {i}: {type(e).__name__}: {e}"); raise
print("ALL CELLS OK")
print(ns["q1"].head(3).to_string())
print(ns["ranges"].head(4).to_string())
