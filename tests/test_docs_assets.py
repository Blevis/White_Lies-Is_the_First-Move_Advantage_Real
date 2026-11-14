"""Publication invariants: source fidelity, privacy, sparse cells and stale exports."""

from pathlib import Path
import hashlib
import json
import shutil

import pytest

from scripts.build_docs_assets import (
    FIGURES, REPORTS, ROOT, build_assets, expected_assets, research_payload, source_paths,
)


def test_export_preserves_validated_statistics_and_unavailable_cells():
    payload = research_payload(ROOT)
    assert payload["h1"]["summary"] == json.loads((ROOT / "results/h1_summary.json").read_text())
    assert payload["h2"]["summary"] == json.loads((ROOT / "results/h2_summary.json").read_text())
    assert payload["provenance"]["sampled_games"] == 836070
    assert payload["provenance"]["scanned_games"] == 97512351
    cells = payload["h2"]["cells"]
    assert len([row for row in cells if row["status"] == "tested"]) == 35
    insufficient = [row for row in cells if row["status"] != "tested"]
    assert insufficient
    assert all(row["q_score"] is None and row["q_distribution"] is None for row in insufficient)
    assert any(not row["eligible"] for row in payload["h2"]["replies"])
    assert all(type(row["eligible"]) is bool for row in payload["h2"]["replies"])
    assert payload["h1"]["summary"]["primary"]["white_win_rate"] < 0.5
    assert payload["h1"]["summary"]["primary"]["score"] > 0.5
    # Browser data has only approved aggregates, no identifiers or individual games.
    encoded = json.dumps(payload, allow_nan=False)
    for forbidden in ('"game_id"', '"white"', '"black"', '"first10"'):
        assert forbidden not in encoded
    for source, digest in payload["provenance"]["sha256"].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == digest


def test_only_final_figures_are_published_and_reports_are_synced():
    assets = expected_assets(ROOT)
    figures = [path for path in assets if path.parent == Path("docs/assets/figures")]
    assert len(figures) == 22
    assert {path.stem for path in figures} == set(FIGURES)
    for report in REPORTS:
        assert assets[Path("docs/assets/reports") / report] == (ROOT / "reports" / report).read_bytes()
    page = assets[Path("docs/research/report.md")].decode()
    body = (ROOT / "reports/FINAL_RESEARCH_REPORT.md").read_text()
    assert page.endswith(body.replace("](../figures/", "](../assets/figures/"))


@pytest.fixture
def publication_copy(tmp_path):
    for relative in source_paths():
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    return tmp_path


def test_export_is_idempotent_and_check_detects_staleness_without_writing(publication_copy):
    root = publication_copy
    originals = {path: (root / path).read_bytes() for path in source_paths()}
    assert build_assets(root)
    assert not build_assets(root)
    assert not build_assets(root, check=True)
    export = root / "docs/assets/data/research.json"
    export.write_text("stale export\n")
    assert build_assets(root, check=True) == ["docs/assets/data/research.json"]
    assert export.read_text() == "stale export\n"
    assert all((root / path).read_bytes() == content for path, content in originals.items())


def test_inconsistent_source_fails_before_any_publication_write(publication_copy):
    root = publication_copy
    path = root / "results/h2_summary.json"
    summary = json.loads(path.read_text())
    summary["score_rejections"] = 15
    path.write_text(json.dumps(summary))
    with pytest.raises(ValueError, match="score_rejections"):
        build_assets(root)
    assert not (root / "docs").exists()


def test_original_markdown_download_survives_mkdocs_without_html_conversion(tmp_path):
    pytest.importorskip("mkdocs")
    from mkdocs.structure.files import File, Files, InclusionLevel
    from scripts.docs_hook import on_files

    original = "assets/reports/FINAL_RESEARCH_REPORT.md"
    source = tmp_path / "docs" / original
    source.parent.mkdir(parents=True)
    source.write_bytes(b"# Original report\n\nPreserve these bytes.\n")
    files = Files([File(original, str(tmp_path / "docs"), str(tmp_path / "site"), True,
                        inclusion=InclusionLevel.INCLUDED)])
    on_files(files, None)
    download = files.get_file_from_path(original)
    assert not download.is_documentation_page()
    assert download.url == original
    files.copy_static_files()
    assert (tmp_path / "site" / original).read_bytes() == source.read_bytes()
