"""Optional Playwright smoke test of the built publication at a project subpath.

Install Playwright separately: pip install playwright==1.58.0
Then: python -m playwright install --with-deps chromium
Run: python scripts/smoke_site.py
The script serves site/ temporarily, writes ignored artifacts/browser screenshots,
and exits nonzero on interaction, resource, JavaScript or page-overflow failures.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "/White_Lies-Is_the_First-Move_Advantage_Real/"


@contextmanager
def serve(site, prefix=PREFIX):
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if not urlsplit(self.path).path.startswith(prefix):
                self.send_error(404)
                return
            self.path = "/" + self.path[len(prefix):]
            return super().do_GET()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}{prefix}"
    finally:
        server.shutdown()
        server.server_close()


def executable(playwright, requested):
    if requested:
        return requested
    bundled = Path(playwright.chromium.executable_path)
    if bundled.exists():
        return str(bundled)
    cached = sorted((Path.home() / ".cache/ms-playwright").glob("chromium-*/chrome-linux*/chrome"))
    return str(cached[-1]) if cached else None


def run(url, args):
    from playwright.sync_api import expect, sync_playwright

    artifacts = args.artifacts.resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    checks, errors, failed_resources = [], [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable(playwright, args.browser_executable),
                                             args=["--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        page = context.new_page()
        page.set_default_timeout(10000)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda response: failed_resources.append(f"{response.status} {response.url}")
                if response.status >= 400 and response.url.startswith(url) else None)
        page.goto(url, wait_until="networkidle")
        expect(page.locator("h1")).to_contain_text("WHITE LIES")
        if page.locator("[data-wl-preview]").count():
            expect(page.locator('[data-wl-preview][data-wl-ready="true"]')).to_be_visible()
        expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "slate")
        page.locator('label[title="Switch to light mode"]:visible').click()
        expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "default")
        page.screenshot(path=str(artifacts / "home-light-desktop.png"), full_page=True)
        page.locator('label[title="Switch to dark mode"]:visible').click()
        expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "slate")
        checks.append("Theme switching")
        search = page.get_by_role("textbox", name="Search", exact=True)
        search.click()
        search.press_sequentially("bootstrap", delay=60)
        expect(page.locator(".md-search-result__item").first).to_be_visible(timeout=15000)
        page.keyboard.press("Escape")
        checks.append("Search returns research results")
        page.locator(".wl-hero").get_by_role("link", name="Start the study", exact=True).click()
        for path, next_label in (
            ("research/question/", "2. Collect and prepare the data →"),
            ("research/approach/", "3. Does White score more? →"),
            ("research/h1/", "4. Does Black's reply matter? →"),
            ("research/h2/", "5. Checks and limits →"),
            ("research/limitations/", "6. The conclusion →"),
        ):
            expect(page).to_have_url(url + path)
            page.locator(".md-content__inner").get_by_role("link", name=next_label, exact=True).click()
        expect(page).to_have_url(url + "research/findings/")
        page.locator(".md-content__inner").get_by_role("link", name="study reference", exact=True).click()
        expect(page.locator("h1")).to_contain_text("Graphs, formulas and concepts")
        page.screenshot(path=str(artifacts / "reference-1440.png"), full_page=True)
        checks.append("Six-step study path and study reference")
        page.goto(url + "explore/", wait_until="networkidle")
        root = page.locator("[data-wl-explorer]")
        expect(root).to_have_attribute("data-wl-ready", "true")
        h1 = root.locator("[data-h1-panel]")
        expect(h1.locator("[data-kpis]")).to_contain_text("836,070")
        expect(h1.locator("[data-chart-primary]")).to_contain_text("51.776%")
        h1.get_by_role("combobox", name="Calculation", exact=True).select_option("raw")
        expect(h1.locator("[data-chart-primary]")).to_contain_text("51.900%")
        h1.get_by_role("combobox", name="Time control", exact=True).select_option("classical")
        expect(h1.get_by_role("combobox", name="Calculation", exact=True)).to_have_value("weighted")
        expect(h1.locator('option[value="raw"]')).to_have_attribute("disabled", "")
        expect(root.locator("[data-status]")).to_contain_text("Unweighted subgroup intervals are unavailable")
        h1.get_by_role("combobox", name="Average rating band", exact=True).select_option("2500")
        expect(h1.locator("[data-h1-status]")).to_contain_text("Descriptive only")
        h1.locator("[data-reset]").click()
        expect(h1.locator("[data-chart-primary]")).to_contain_text("51.776%")
        checks.append("H1 weighted/raw, unavailable raw subgroup, sparse group, reset")
        root.get_by_role("combobox", name="View results", exact=True).select_option("h2")
        expect(h1).to_be_hidden()
        opening = root.locator("[data-opening-module]")
        expect(opening.locator(".wl-square")).to_have_count(64)
        expect(opening.locator('[data-square="a1"]')).to_have_class("wl-square wl-square-dark")
        expect(opening.locator('[data-square="e4"]')).to_have_attribute("data-piece", "wP")
        opening.get_by_role("combobox", name="Black’s reply", exact=True).select_option("c5")
        expect(opening.locator('[data-square="c5"]')).to_have_attribute("data-piece", "bP")
        expect(opening.locator('[data-square="c7"]')).to_have_attribute("data-piece", "")
        opening.get_by_role("combobox", name="White’s first move", exact=True).select_option("d4")
        opening.get_by_role("combobox", name="Black’s reply", exact=True).select_option("Nf6")
        expect(opening.locator('[data-square="d4"]')).to_have_attribute("data-piece", "wP")
        expect(opening.locator('[data-square="d2"]')).to_have_attribute("data-piece", "")
        expect(opening.locator('[data-square="e2"]')).to_have_attribute("data-piece", "wP")
        expect(opening.locator('[data-square="f6"]')).to_have_attribute("data-piece", "bN")
        expect(opening.locator('[data-square="g8"]')).to_have_attribute("data-piece", "")
        opening.locator("[data-board-reset]").click()
        expect(opening.locator(".wl-board-notation")).to_have_text("Initial position")
        expect(opening.locator('[data-square="d2"]')).to_have_attribute("data-piece", "wP")
        expect(opening.locator('[data-square="g8"]')).to_have_attribute("data-piece", "bN")
        opening.locator("[data-board-show]").click()
        expect(opening.locator('[data-square="f6"]')).to_have_attribute("data-piece", "bN")
        opening.get_by_role("searchbox", name="Search replies", exact=True).fill("Nf6")
        expect(opening.locator("[data-reply-table] [data-show-reply]")).to_have_count(1)
        opening.get_by_role("searchbox", name="Search replies", exact=True).fill("")
        opening.locator('[data-sort="N"]').click()
        expect(opening.locator('[data-sort="N"]').locator("..")).to_have_attribute("aria-sort", "ascending")
        opening.get_by_role("combobox", name="Time control", exact=True).select_option("classical")
        opening.get_by_role("combobox", name="Average rating band", exact=True).select_option("2500")
        expect(opening.locator("[data-reply-chart] .wl-empty")).to_be_visible()
        expect(opening.get_by_role("combobox", name="Black’s reply", exact=True)).to_be_disabled()
        expect(opening.locator("[data-reply-table] [data-show-reply]")).to_have_count(0)
        opening.get_by_role("combobox", name="Average rating band", exact=True).select_option("0")
        expect(opening.locator("[data-reply-chart]")).to_contain_text("excludes rating bands below 1200")
        checks.append("H2 filters, both openings, legal pawn/knight moves, board reset, table search/sort, unavailable cells")
        root.get_by_role("combobox", name="View results", exact=True).focus()
        page.keyboard.press("ArrowUp")
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement !== document.body"), "Keyboard focus was lost"
        checks.append("Keyboard controls and focus")
        study_figures = set()
        study_paths = ("research/question/", "research/approach/", "research/h1/",
                       "research/h2/", "research/limitations/", "research/findings/",
                       "research/reference/")
        for width in (360, 390, 768, 1024, 1440):
            page.set_viewport_size({"width": width, "height": 960})
            for path in ("", "explore/", "research/report/", *study_paths):
                page.goto(url + path, wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                expect(page.locator(".arithmatex:not([data-rendered])")).to_have_count(0)
                expect(page.locator(".katex-error")).to_have_count(0)
                if width == 1440 and path in study_paths:
                    for graph in page.locator(".md-content img.research-figure").all():
                        graph.scroll_into_view_if_needed()
                        expect(graph).to_have_js_property("complete", True)
                        assert graph.evaluate("image => image.naturalWidth > 0"), "Study graph failed to load"
                        study_figures.add(graph.get_attribute("src").rsplit("/", 1)[-1])
                overflow = page.evaluate("({scroll:document.documentElement.scrollWidth, viewport:innerWidth})")
                assert overflow["scroll"] <= overflow["viewport"] + 1, f"Page overflow at {width}px on {path}: {overflow}"
                if width in (390, 1440) and path in ("", "explore/"):
                    page.screenshot(path=str(artifacts / f"{'home' if not path else 'explorer'}-{width}.png"), full_page=True)
                if width == 390 and path in ("research/question/", "research/reference/"):
                    page.screenshot(path=str(artifacts / f"{path.split('/')[-2]}-390.png"), full_page=True)
                targets = {"research/approach/": "step-5-prepare-the-fields-used-in-analysis",
                           "research/h1/": "step-3-calculate-the-score-and-apply-weights",
                           "research/h2/": "step-4-simulate-equal-outcomes-and-run-two-tests"}
                if width in (390, 1440) and path in targets:
                    page.locator(f"#{targets[path]}").scroll_into_view_if_needed()
                    page.screenshot(path=str(artifacts / f"{path.split('/')[-2]}-{width}.png"))
                    graph = page.locator("figure.study-figure").first
                    if graph.count():
                        graph.scroll_into_view_if_needed()
                        image = graph.locator("img.research-figure")
                        expect(image).to_have_js_property("complete", True)
                        expect(graph.locator("figcaption .study-figure__takeaway")).to_be_visible()
                        expect(graph.locator(".study-figure__notes > div")).to_have_count(2)
                        page_name = path.split("/")[-2]
                        graph.screenshot(path=str(artifacts / f"graph-{page_name}-{width}.png"))
                        if width == 1440 and path == "research/h1/":
                            page.locator('label[title="Switch to light mode"]:visible').click()
                            graph.screenshot(path=str(artifacts / "graph-h1-light-1440.png"))
                            page.locator('label[title="Switch to dark mode"]:visible').click()
        assert len(study_figures) == 11, f"Expected all eleven study graphs, found {study_figures}"
        checks.append("All eleven study graphs load; study formulas render without errors")
        checks.append("Compact graph captions render at phone/desktop widths and in both themes")
        checks.append("No document overflow at 360, 390, 768, 1024 and 1440 px on home/explorer/report and every study page")
        page.goto(url + "research/report/", wait_until="networkidle")
        expect(page.locator(".katex").first).to_be_visible()
        expect(page.locator(".katex-error")).to_have_count(0)
        checks.append("Full-report mathematics render")
        for path in ("methodology/statistics/", "methodology/uncertainty/"):
            page.goto(url + path, wait_until="networkidle")
            page.locator(".md-content details > summary").first.click()
            expect(page.locator(".katex").first).to_be_visible()
            expect(page.locator(".katex-error")).to_have_count(0)
        checks.append("Expandable method formulas render")
        assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
        animations = page.evaluate("document.getAnimations().filter(a=>a.playState==='running').length")
        assert animations == 0, "Ongoing animations despite reduced-motion preference"
        checks.append("Reduced motion respected")
        # A fresh context avoids the successful data-fetch cache from previous views.
        failure_context = browser.new_context(viewport={"width": 1024, "height": 900})
        failure_page = failure_context.new_page()
        failure_page.route("**/assets/data/research.json", lambda route: route.abort())
        failure_page.goto(url + "explore/", wait_until="networkidle")
        expect(failure_page.locator('[data-wl-explorer] [role="alert"]')).to_be_visible()
        failure_page.unroute("**/assets/data/research.json")
        failure_page.locator("[data-retry]").click()
        expect(failure_page.locator("[data-wl-explorer]")).to_have_attribute("data-wl-ready", "true")
        checks.append("Fetch failure explains unavailable data; retry recovers")
        failure_context.close()
        if args.axe_file:
            accessibility = []
            for width, paths in ((1440, ("", "explore/", "research/report/", "methodology/statistics/")),
                                 (390, ("", "explore/"))):
                page.set_viewport_size({"width": width, "height": 960})
                for scheme in ("slate", "default"):
                    for path in paths:
                        page.goto(url + path, wait_until="networkidle")
                        current = page.locator("body").get_attribute("data-md-color-scheme")
                        if current != scheme:
                            target = "light" if scheme == "default" else "dark"
                            page.locator(f'label[title="Switch to {target} mode"]:visible').click()
                        page.add_script_tag(path=str(args.axe_file.resolve()))
                        result = page.evaluate("""async () => await axe.run(document, {
                            runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21aa','wcag22aa']}
                        })""")
                        violations = [{"id": v["id"], "impact": v["impact"],
                                       "nodes": [{"target": n["target"], "summary": n["failureSummary"]}
                                                 for n in v["nodes"]]} for v in result["violations"]]
                        accessibility.append({"page": path, "width": width, "scheme": scheme,
                                              "violations": violations})
            (artifacts / "accessibility-results.json").write_text(json.dumps(accessibility, indent=2) + "\n")
            assert not any(item["violations"] for item in accessibility), "Accessibility violations; see accessibility-results.json"
            checks.append("axe WCAG A/AA checks: four desktop pages in both themes; home/explorer at 390 px in both themes")
        assert not errors, f"JavaScript errors: {errors}"
        assert not failed_resources, f"Failed local resources: {failed_resources}"
        checks.append("No JavaScript exceptions or local HTTP failures")
        browser.close()
    report = {"status": "passed", "url": url, "checks": checks, "screenshots": sorted(p.name for p in artifacts.glob("*.png"))}
    (artifacts / "smoke-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "site")
    parser.add_argument("--url", help="Use an existing server instead of the temporary subpath server")
    parser.add_argument("--base-path", default=PREFIX, help="Project subpath for the temporary server")
    parser.add_argument("--browser-executable", default=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE"))
    parser.add_argument("--axe-file", type=Path, help="Optional local axe-core JavaScript for WCAG checks")
    parser.add_argument("--artifacts", type=Path, default=ROOT / "artifacts/browser")
    args = parser.parse_args()
    if args.url:
        run(args.url.rstrip("/") + "/", args)
    else:
        prefix = "/" + args.base_path.strip("/") + "/" if args.base_path.strip("/") else "/"
        with serve(args.site.resolve(), prefix) as url:
            run(url, args)


if __name__ == "__main__":
    main()
