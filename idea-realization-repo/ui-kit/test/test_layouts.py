"""The shell layouts, their schema, the extra rules and the generated `dist/layouts.css`.

Valid layouts build byte-identically and match the committed file; `--check` catches a stale or
missing output (on tmp copies only: the real dist is never written); every rule rejects a crafted
bad layout with exit 1 and a message naming the file; the generated sheet has a rule per layout
and per region.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "tools"))

import build_layouts as gen  # noqa: E402

LAYOUTS = KIT / "layouts"
SCHEMA = LAYOUTS / "layout.schema.json"
DIST = KIT / "dist" / "layouts.css"
SCRIPT = KIT / "tools" / "build_layouts.py"
SHIPPED = {"ide", "dashboard", "focus", "examiner"}


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )


def _ide() -> dict[str, Any]:
    data: dict[str, Any] = json.loads((LAYOUTS / "ide.json").read_text(encoding="utf-8"))
    return data


@pytest.fixture
def tmp_layouts(tmp_path: Path) -> Path:
    """A copy of the real layouts folder (schema included)."""
    target = tmp_path / "layouts"
    shutil.copytree(LAYOUTS, target)
    return target


def _write(folder: Path, name: str, data: Any) -> None:
    (folder / f"{name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def _dist_hash() -> str:
    return hashlib.sha256(DIST.read_bytes()).hexdigest()


# ---- valid layouts ----


def test_shipped_layouts_are_present_and_valid() -> None:
    layouts = gen.load_layouts(LAYOUTS, SCHEMA)
    assert {lay.id for lay in layouts} == SHIPPED


def test_schema_is_valid_draft_2020_12() -> None:
    schema = gen.load_schema(SCHEMA)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"


def test_render_is_byte_identical_and_matches_committed() -> None:
    first = gen.render(gen.load_layouts(LAYOUTS, SCHEMA), gen.schema_regions(SCHEMA))
    second = gen.render(gen.load_layouts(LAYOUTS, SCHEMA), gen.schema_regions(SCHEMA))
    assert first == second
    assert DIST.read_bytes() == first.encode("utf-8")
    assert b"\r" not in DIST.read_bytes()
    assert first.endswith("}\n") and not first.endswith("\n\n")


def test_two_cli_builds_are_byte_identical(tmp_path: Path) -> None:
    a, b = tmp_path / "a.css", tmp_path / "b.css"
    assert _run("--out", str(a)).returncode == 0
    assert _run("--out", str(b)).returncode == 0
    assert a.read_bytes() == b.read_bytes() == DIST.read_bytes()


def test_check_passes_on_committed() -> None:
    before = _dist_hash()
    result = _run("--check")
    assert result.returncode == 0, result.stderr
    assert _dist_hash() == before


# ---- --check staleness, on tmp copies ----


def test_check_fails_on_stale_output(tmp_path: Path) -> None:
    before = _dist_hash()
    out = tmp_path / "layouts.css"
    out.write_text(DIST.read_text(encoding="utf-8") + "/* edited */\n", encoding="utf-8")
    result = _run("--check", "--out", str(out))
    assert result.returncode == 1
    assert "stale" in result.stderr
    assert _dist_hash() == before


def test_check_fails_on_missing_output(tmp_path: Path) -> None:
    result = _run("--check", "--out", str(tmp_path / "absent.css"))
    assert result.returncode == 1


def test_check_fails_when_a_layout_changes(tmp_layouts: Path, tmp_path: Path) -> None:
    before = _dist_hash()
    out = tmp_path / "layouts.css"
    shutil.copy(DIST, out)
    data = _ide()
    data["grid"]["columns"][1] = "minmax(0, 5fr)"
    _write(tmp_layouts, "ide", data)
    result = _run("--check", "--layouts", str(tmp_layouts), "--out", str(out))
    assert result.returncode == 1
    assert "stale" in result.stderr
    assert _dist_hash() == before


def test_check_fails_when_a_layout_is_added(tmp_layouts: Path, tmp_path: Path) -> None:
    out = tmp_path / "layouts.css"
    shutil.copy(DIST, out)
    data = _ide()
    data["id"] = "extra"
    _write(tmp_layouts, "extra", data)
    assert _run("--check", "--layouts", str(tmp_layouts), "--out", str(out)).returncode == 1


# ---- every rule rejects a crafted bad layout ----


def _mutate_track_px(d: dict[str, Any]) -> None:
    d["grid"]["columns"][0] = "240px"


def _mutate_track_minmax_px(d: dict[str, Any]) -> None:
    d["grid"]["columns"][0] = "minmax(200px, 1fr)"


def _mutate_track_minmax_auto(d: dict[str, Any]) -> None:
    d["grid"]["rows"][1] = "minmax(0, auto)"


def _mutate_region_missing_from_areas(d: dict[str, Any]) -> None:
    d["grid"]["areas"][2] = "nav main inspector"


def _mutate_area_name_not_in_regions(d: dict[str, Any]) -> None:
    d["regions"].remove("inspector")


def _mutate_ragged_areas(d: dict[str, Any]) -> None:
    d["grid"]["areas"][1] = "nav main"


def _mutate_areas_wider_than_columns(d: dict[str, Any]) -> None:
    d["grid"]["areas"] = [
        "header header header header",
        "nav main inspector inspector",
        "nav dock inspector inspector",
        "strip strip strip strip",
    ]


def _mutate_rows_mismatch(d: dict[str, Any]) -> None:
    d["grid"]["rows"] = d["grid"]["rows"][:3]


def _mutate_non_rectangular_region(d: dict[str, Any]) -> None:
    d["grid"]["areas"][2] = "nav dock main"


def _mutate_split_region(d: dict[str, Any]) -> None:
    d["grid"]["areas"][3] = "strip header strip"


def _mutate_unknown_region(d: dict[str, Any]) -> None:
    d["regions"][0] = "toolbar"
    d["grid"]["areas"][0] = "toolbar toolbar toolbar"


def _mutate_id_not_file_name(d: dict[str, Any]) -> None:
    d["id"] = "workbench"


def _mutate_extra_key(d: dict[str, Any]) -> None:
    d["theme"] = "dark"


def _mutate_missing_label(d: dict[str, Any]) -> None:
    del d["label"]


def _mutate_duplicate_region(d: dict[str, Any]) -> None:
    d["regions"].append("main")


def _mutate_empty_cell(d: dict[str, Any]) -> None:
    d["grid"]["areas"][2] = "nav . inspector"


CASES = {
    "track-px": (_mutate_track_px, "240px"),
    "track-minmax-px": (_mutate_track_minmax_px, "minmax(200px, 1fr)"),
    "track-minmax-auto": (_mutate_track_minmax_auto, "minmax(0, auto)"),
    "region-missing-from-areas": (_mutate_region_missing_from_areas, "not placed in areas"),
    "area-name-not-in-regions": (_mutate_area_name_not_in_regions, "not in regions"),
    "ragged-areas": (_mutate_ragged_areas, "has 2 cells but columns has 3"),
    "areas-wider-than-columns": (_mutate_areas_wider_than_columns, "has 4 cells"),
    "rows-mismatch": (_mutate_rows_mismatch, "areas has 4 rows but rows has 3"),
    "non-rectangular-region": (_mutate_non_rectangular_region, "one rectangle"),
    "split-region": (_mutate_split_region, "one rectangle"),
    "unknown-region": (_mutate_unknown_region, "toolbar"),
    "id-not-file-name": (_mutate_id_not_file_name, "does not match the file name"),
    "extra-key": (_mutate_extra_key, "theme"),
    "missing-label": (_mutate_missing_label, "label"),
    "duplicate-region": (_mutate_duplicate_region, "non-unique"),
    "empty-cell": (_mutate_empty_cell, "nav . inspector"),
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_rule_rejects_bad_layout(case: str, tmp_layouts: Path, tmp_path: Path) -> None:
    before = _dist_hash()
    mutate, expected = CASES[case]
    data = copy.deepcopy(_ide())
    mutate(data)
    _write(tmp_layouts, "ide", data)
    out = tmp_path / "layouts.css"
    result = _run("--layouts", str(tmp_layouts), "--out", str(out))
    assert result.returncode == 1
    assert "invalid layout" in result.stderr
    assert "ide.json" in result.stderr
    assert expected in result.stderr, result.stderr
    assert not out.exists()
    # --check also exits 1 on an invalid layout
    assert _run("--check", "--layouts", str(tmp_layouts), "--out", str(DIST)).returncode == 1
    assert _dist_hash() == before


def test_rule_errors_direct() -> None:
    data = _ide()
    assert gen.rule_errors(data, "ide") == []
    data["grid"]["areas"][2] = "nav dock main"
    assert any("one rectangle" in e for e in gen.rule_errors(data, "ide"))


def test_invalid_json_is_reported(tmp_layouts: Path, tmp_path: Path) -> None:
    (tmp_layouts / "ide.json").write_text("{ not json", encoding="utf-8")
    result = _run("--layouts", str(tmp_layouts), "--out", str(tmp_path / "x.css"))
    assert result.returncode == 1
    assert "ide.json: not valid JSON" in result.stderr


def test_empty_layouts_folder_is_an_error(tmp_path: Path) -> None:
    folder = tmp_path / "layouts"
    folder.mkdir()
    shutil.copy(SCHEMA, folder / SCHEMA.name)
    result = _run("--layouts", str(folder), "--out", str(tmp_path / "x.css"))
    assert result.returncode == 1
    assert "no layout files" in result.stderr


# ---- generated CSS shape ----


def test_generated_css_has_rule_per_layout_and_region() -> None:
    css = DIST.read_text(encoding="utf-8")
    for lay in gen.load_layouts(LAYOUTS, SCHEMA):
        shell = re.escape(f'.ui-shell[data-layout="{lay.id}"]')
        block = re.search(shell + r" \{([^}]*)\}", css)
        assert block, lay.id
        body = block.group(1)
        assert f"grid-template-columns: {' '.join(lay.columns)};" in body
        assert f"grid-template-rows: {' '.join(lay.rows)};" in body
        for row in lay.areas:
            assert f'"{row}"' in body
        for region in lay.regions:
            rule = f'.ui-shell[data-layout="{lay.id}"] > [data-region="{region}"] '
            assert rule + f"{{ grid-area: {region}; }}" in css


def test_unused_regions_are_hidden_per_layout() -> None:
    css = DIST.read_text(encoding="utf-8")
    all_regions = set(gen.schema_regions(SCHEMA))
    for lay in gen.load_layouts(LAYOUTS, SCHEMA):
        prefix = f'.ui-shell[data-layout="{lay.id}"] > [data-region]:not('
        if set(lay.regions) == all_regions:
            assert prefix not in css
            continue
        used = ", ".join(f'[data-region="{r}"]' for r in lay.regions)
        assert prefix + used + ") { display: none; }" in css


def test_generated_css_is_wide_only_and_has_no_px() -> None:
    css = DIST.read_text(encoding="utf-8")
    assert "@media (width >= 64em) {" in css
    rules = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    assert not re.search(r"\d+px", rules)


def test_generated_css_layout_order_is_sorted() -> None:
    css = DIST.read_text(encoding="utf-8")
    ids = re.findall(r'\.ui-shell\[data-layout="([^"]+)"\] \{', css)
    assert ids == sorted(SHIPPED)
