"""Build image.svg and image.html for post 002 from the idea log at the current commit.

Run from the repository root:

    uv run python content/posts/002-the-idea-log/make_image.py
    google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
        --window-size=1600,900 --virtual-time-budget=5000 \
        --screenshot=content/posts/002-the-idea-log/image.png \
        content/posts/002-the-idea-log/image.html
"""

import collections
import subprocess
from html import escape
from pathlib import Path

from src.db import ideas

HERE = Path(__file__).parent
W, H = 1600, 900
C = {
    "bg": "#ffffff",
    "surface": "#f6f1ea",
    "line": "#ddd6cd",
    "text": "#141414",
    "muted": "#5a5a5a",
    "accent": "#c8205f",
}
DISPLAY = "'Bricolage Grotesque', ui-sans-serif, sans-serif"
BODY = "'Literata', Georgia, serif"
MONO = "'JetBrains Mono', ui-monospace, monospace"
FONTS = (
    "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800"
    "&family=JetBrains+Mono:wght@400;600&family=Literata:opsz,wght@7..72,400&display=swap"
)


def text(x: float, y: float, value: str, size: int, family: str, fill: str, **extra: str) -> str:
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in extra.items())
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-family="{family}" fill="{fill}" {attrs}>'
        f"{escape(value)}</text>"
    )


def bars(x: float, y: float, rows: list[tuple[str, int]], scale: float, fill: str) -> list[str]:
    out = []
    for i, (label, count) in enumerate(rows):
        top = y + i * 74
        width = max(count * scale, 4)
        out.append(text(x, top + 30, label, 28, MONO, C["text"]))
        out.append(
            f'<rect x="{x + 240}" y="{top + 4}" width="{width:.1f}" height="34" fill="{fill}"/>'
        )
        out.append(
            text(x + 252 + width, top + 32, f"{count:,}", 28, DISPLAY, C["text"], font_weight="700")
        )
    return out


def panel(x: float) -> str:
    return (
        f'<rect x="{x}" y="230" width="650" height="560" rx="14" '
        f'fill="{C["surface"]}" stroke="{C["line"]}"/>'
    )


def main() -> None:
    events = ideas.load_events()
    state = ideas.fold(events)
    kinds = collections.Counter(event["event"] for event in events)
    statuses = collections.Counter(item["status"] for item in state.values())
    commit = subprocess.run(
        ["git", "log", "-1", "--format=%h %ad", "--date=short"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    log_rows = [
        ("linked", kinds["linked"]),
        ("annotated", kinds["annotated"]),
        ("created", kinds["created"]),
        ("status", kinds["status"]),
        ("amended", kinds["amended"]),
        ("revisited", kinds["revisited"]),
    ]
    other = len(events) - sum(count for _, count in log_rows)
    assert other == 0, f"{other} events of an unlisted kind; add a row"
    state_rows = sorted(statuses.items(), key=lambda row: -row[1])
    scale = 260 / max(count for _, count in log_rows + state_rows)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>',
        text(80, 120, f"{len(events):,} events. {len(state):,} ideas. No edits.", 64, DISPLAY,
             C["text"], font_weight="800", letter_spacing="-1.5"),
        text(80, 178, "The log holds only events. An idea's state is computed by folding them.",
             30, BODY, C["muted"]),
        panel(60),
        text(90, 282, "The log: every event, append-only", 30, DISPLAY, C["text"],
             font_weight="700"),
        *bars(90, 320, log_rows, scale, C["muted"]),
        panel(890),
        text(920, 282, "Current state: ideas by status", 30, DISPLAY, C["text"], font_weight="700"),
        *bars(920, 320, state_rows, scale, C["text"]),
        f'<line x1="712" y1="520" x2="878" y2="520" stroke="{C["accent"]}" stroke-width="5"/>',
        f'<path d="M872 506 L890 520 L872 534 Z" fill="{C["accent"]}"/>',
        f'<rect x="728" y="492" width="134" height="56" rx="28" fill="{C["accent"]}"/>',
        text(795, 530, "fold()", 30, MONO, "#ffffff", font_weight="600", text_anchor="middle"),
        text(80, 850, f"Source: src/db/ideas.py load_events() and fold() · dev {commit}", 24, MONO,
             C["muted"]),
        "</svg>",
    ]
    svg = "\n".join(parts) + "\n"
    (HERE / "image.svg").write_text(svg, encoding="utf-8")
    (HERE / "image.html").write_text(
        f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{FONTS}">'
        f"<style>html,body{{margin:0;background:#fff}}</style></head><body>{svg}</body></html>\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
