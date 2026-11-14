"""Check a built MkDocs publication without third-party packages or network calls.

Checks every local HTML href/src/srcset, inline/CSS url, target anchor, the
publication's headline figures, raw report downloads, and aggregate-only assets.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREFIX = "/White_Lies-Is_the_First-Move_Advantage_Real/"
CSS_URL = re.compile(r"url\(\s*['\"]?([^)'\"\s]+)['\"]?\s*\)", re.I)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.text = set(), [], []
        self.canonical = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append(attrs[key])
        if attrs.get("srcset") and not attrs["srcset"].startswith("data:"):
            self.refs.extend(part.strip().split()[0] for part in attrs["srcset"].split(",") if part.strip())
        self.refs.extend(CSS_URL.findall(attrs.get("style", "")))

    def handle_data(self, data):
        self.text.append(data)


def check_site(site: Path, prefix: str | None = None) -> tuple[list[str], dict]:
    site = site.resolve()
    if prefix is None:
        homepage_path = site / "index.html"
        canonical = Document(homepage_path.read_text(encoding="utf-8")).canonical if homepage_path.exists() else None
        prefix = urlsplit(canonical).path if canonical else "/"
    prefix = "/" + prefix.strip("/") + "/" if prefix.strip("/") else "/"
    errors = []
    documents = {path: Document(path.read_text(encoding="utf-8")) for path in site.rglob("*.html")}
    references = 0

    def check_reference(source: Path, reference: str, css=False):
        nonlocal references
        if not reference or reference.startswith(("data:", "blob:", "mailto:", "tel:")):
            return
        if css and reference.startswith("#"):
            return  # SVG paint/filter references resolve in the consuming document.
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc:
            return
        references += 1
        source_url = "https://publication.invalid" + prefix + source.relative_to(site).as_posix()
        target_url = urlsplit(urljoin(source_url, reference))
        target_path = unquote(target_url.path)
        if not target_path.startswith(prefix):
            errors.append(f"{source.relative_to(site)}: URL escapes project subpath: {reference}")
            return
        target = (site / target_path[len(prefix):]).resolve()
        if not target.is_relative_to(site):
            errors.append(f"{source.relative_to(site)}: URL escapes site directory: {reference}")
            return
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            errors.append(f"{source.relative_to(site)}: missing target {reference}")
            return
        anchor = unquote(target_url.fragment).split(":~:text=", 1)[0]
        if anchor and target in documents and anchor not in documents[target].ids:
            # Material's client-side overlay links are intentionally dynamic.
            if anchor not in {"__search", "__drawer", "__toc"}:
                errors.append(f"{source.relative_to(site)}: missing anchor {reference}")

    for source, document in documents.items():
        for reference in document.refs:
            check_reference(source, reference)
    css_files = list(site.rglob("*.css"))
    for source in css_files:
        content = re.sub(r"/\*.*?\*/", "", source.read_text(encoding="utf-8"), flags=re.S)
        for reference in CSS_URL.findall(content):
            check_reference(source, reference, css=True)

    homepage = documents.get(site / "index.html")
    if not homepage:
        errors.append("Missing homepage index.html")
    else:
        text = re.sub(r"\s+", "", "".join(homepage.text))
        for required in ("836,070", "51.776", "1.776", "14", "35", "March2025"):
            if required not in text:
                errors.append(f"Homepage missing published research value: {required}")
    for path in site.rglob("*"):
        if path.is_file() and (path.suffix.lower() in {".parquet", ".pgn", ".zst", ".ipynb"}
                               or re.match(r"games_.*\.csv$", path.name)):
            errors.append(f"Game-level or unnecessary large research input in site: {path.relative_to(site)}")
    data_file = site / "assets/data/research.json"
    if not data_file.exists():
        errors.append("Missing aggregate research.json")
    else:
        payload = json.loads(data_file.read_text())
        if payload.get("schema_version") != 1:
            errors.append("Unexpected aggregate data schema")
        forbidden = {"game_id", "white", "black", "first10", "white_player", "black_player"}

        def inspect(value):
            if isinstance(value, dict):
                if forbidden & value.keys():
                    errors.append("Individual-game identifiers found in aggregate payload")
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)
        inspect(payload)
        if payload["provenance"]["sampled_games"] != 836070:
            errors.append("Aggregate sample count differs from publication")
    for original in (ROOT / "reports").glob("*.md"):
        if original.name not in {"FINAL_RESEARCH_REPORT.md", "FINAL_CONCLUSION.md", "implementation_audit.md", "COMPLETION_CHECKLIST.md"}:
            continue
        downloaded = site / "assets/reports" / original.name
        if not downloaded.exists() or downloaded.read_bytes() != original.read_bytes():
            errors.append(f"Original Markdown download absent or altered: {original.name}")
    return sorted(set(errors)), {"html_pages": len(documents), "css_files": len(css_files), "local_references": references}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", "--site-dir", type=Path, default=ROOT / "site")
    parser.add_argument("--base-path", help="Override canonical URL path; defaults to canonical path or / for local builds")
    args = parser.parse_args()
    if not args.site.is_dir():
        parser.error("Build the website first: python -m mkdocs build --strict")
    errors, statistics = check_site(args.site, args.base_path)
    print(json.dumps(statistics, indent=2))
    if errors:
        print("\n".join(errors))
        return 1
    print("Static site checks passed: local links, anchors, assets, downloads and publication data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
