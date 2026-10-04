# Image style

## When a post gets an image

Not every post needs one (owner, 2026-10-04). Use an image when it shows something the text cannot
show as well:

- a mechanism with parts and connections (a diagram);
- a number set that is easier to compare than to read (a chart or stat card);
- a real file or page the post is about (a screenshot or the file).

Reflection posts and most incident posts are text only. An image that only decorates is left out.

## House style

Diagrams use the house tokens from `templates/styles/house-tokens.json` and
`templates/styles/house.css`, so post images match the engine pages.

| Token | Light | Use in images |
|---|---|---|
| bg | `#ffffff` | Canvas |
| surface | `#f6f1ea` | Boxes, panels |
| line | `#ddd6cd` | Borders, connectors |
| text | `#141414` | Labels |
| muted | `#5a5a5a` | Secondary labels, source line |
| accent | `#c8205f` | The one element the post is about |
| accent-2 | `#0f7b6c` | A second category where one is needed |

Fonts: Bricolage Grotesque for titles and labels, Literata for running text, JetBrains Mono for
paths, commands and ids.

Rules:

1. Light theme only. X shows images on both light and dark backgrounds, and a white canvas reads on
   both.
2. 1600 × 900 pixels (16:9), PNG. X does not accept SVG; for a diagram, keep the SVG source next to the PNG.
3. One accent element per image: the thing the post is about.
4. Text in the image at 28 px or larger, so it is readable on a phone without zooming.
5. Diagrams, charts and stat cards carry a source line at the bottom in muted mono: the file or
   command the image is built from and the commit. An illustration from an AI image brief carries
   no text at all, so it has no source line; its `image.md` records where its facts come from.
6. No screenshots of the owner's desktop, terminal prompt, browser tabs or notifications.

## Production methods

| Method | When | How |
|---|---|---|
| Generated diagram | The post explains a mechanism and the repository holds the data | A script reads the repository records, writes an SVG with the house tokens, and headless Chrome renders it to PNG (`google-chrome --headless=new --screenshot`). The command and commit go in `image.md` |
| Hand-drawn diagram | A concept with no data behind it | SVG written by hand with the same tokens |
| Screenshot | An artifact post about a real page or file | A rendered engine page or file in a clean browser window, cropped to the relevant part |
| AI image brief | A post that benefits from an illustrative image, not a diagram | `image.md` holds a prompt the owner runs in an external image generator. The brief states the subject, composition, the house colours by hex value, and what must not appear (text, logos, real people) |
| Animation or short video (later stage) | A sequence: events appended, a race between sessions, a commit blocked and fixed | Options to evaluate when the first one is due: an animated SVG rendered frame by frame, a terminal recording, or a screen recording of an engine page. Short (under 30 seconds), silent, captioned |

## image.md template

Each post with an image has `image.md`:

- **Type:** generated diagram, hand-drawn diagram, screenshot, AI image brief, or animation.
- **What it shows:** one sentence.
- **Source:** the command or file it is built from, and the commit. For an AI image brief, the
  documents its facts come from, or "none".
- **Prompt:** for an AI image brief only.
- **Alt text:** as posted.
- **Files:** the image files in the post directory.

## Alt text

Every image posted has alt text (X allows up to 1,000 characters).

1. Say what the image shows and the point it makes, not what it looks like.
2. Include every number and label a reader needs. A reader using a screen reader should get the
   same information as a reader who sees the image.
3. For a diagram, describe it in reading order: what flows into what.
4. Do not start with "Image of".
