"""Product CI's ruff: pinned to the control repository's version, and clean on the template.

Product CI runs ``uvx ruff@<version> check .`` at the product root as soon as the product adds a
``pyproject.toml``. With no ruff configuration of the product's own, ruff applies its defaults to
every file the template ships, so the template must pass under those defaults at the pinned
version.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tomllib
from pathlib import Path

IRR = Path(__file__).resolve().parent.parent
PRODUCT_TEMPLATE = IRR / "templates" / "product-repo"
PRODUCT_CI = PRODUCT_TEMPLATE / ".github" / "workflows" / "product-ci.yml"


def locked_ruff() -> str:
    lock = tomllib.loads((IRR / "uv.lock").read_text(encoding="utf-8"))
    return next(package["version"] for package in lock["package"] if package["name"] == "ruff")


def test_product_ci_pins_the_control_repositorys_ruff() -> None:
    pins = re.findall(r"uvx ruff@(\S+) check", PRODUCT_CI.read_text(encoding="utf-8"))
    assert re.findall(r"uvx ruff(?:@\S+)? ", PRODUCT_CI.read_text(encoding="utf-8")) == [
        f"uvx ruff@{pin} " for pin in pins
    ], "every ruff call in product CI names an exact version"
    project = tomllib.loads((IRR / "pyproject.toml").read_text(encoding="utf-8"))
    dev = project["project"]["optional-dependencies"]["dev"]
    assert pins == [locked_ruff()]
    assert f"ruff=={locked_ruff()}" in dev


def test_the_template_is_clean_under_the_pinned_ruffs_defaults(tmp_path: Path) -> None:
    uvx = shutil.which("uvx")
    assert uvx, "uvx (from uv) is needed to run the pinned ruff"
    product = tmp_path / "product"
    shutil.copytree(PRODUCT_TEMPLATE, product)
    result = subprocess.run([uvx, f"ruff@{locked_ruff()}", "check", "--isolated", "--no-cache",
                             "."], cwd=product, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
