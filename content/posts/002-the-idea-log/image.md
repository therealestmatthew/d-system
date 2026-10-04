# 002 image

- **Type:** generated diagram
- **What it shows:** the idea log's 2,717 events by kind on the left, folded into 564 ideas by status
  on the right.
- **Source:** `load_events()` and `fold()` in `src/db/ideas.py`, at dev `518642d` (2026-10-04). The
  commit is printed on the image.
- **Files:** `image.png` (posted), `image.svg` (source), `image.html` (render input),
  `make_image.py` (generator).

## Regenerate

From the repository root, at the commit the post is drafted against:

```bash
uv run python content/posts/002-the-idea-log/make_image.py
google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
    --window-size=1600,900 --virtual-time-budget=5000 \
    --screenshot=content/posts/002-the-idea-log/image.png \
    content/posts/002-the-idea-log/image.html
```

The generator fails if the log contains an event kind it does not chart, so a new kind cannot drop
out of the total unnoticed. The render loads the house fonts from Google Fonts; without network
access the PNG falls back to system fonts, so check it before posting. If the numbers change,
update the post text to match.

## Alt text

> Diagram titled "2,717 events. 564 ideas. No edits." Left panel, the log, every event
> append-only: linked 839, annotated 739, created 564, status 550, amended 15, revisited 10. An
> arrow labelled fold() leads to the right panel, current state, ideas by status: triaged 494,
> open 39, promoted 13, reviewing 10, discarded 7, delivered 1. Source: src/db/ideas.py at dev
> 518642d, 2026-10-04.
