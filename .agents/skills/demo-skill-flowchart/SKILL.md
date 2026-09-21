---
name: demo-skill-flowchart
description: "Turn a process described in sequence into a rendered diagram. Fires when the input describes steps in order, hand-offs between parties, or conditional branches — \"first X, then Y\", \"it goes to legal for sign-off\", \"if the amount is over the threshold\", \"walk through how the close works\". Must not fire on a list with no ordering or hand-off between its items, on a single step, or when the person asks for prose, a checklist or a written procedure rather than a diagram."
---

# demo-skill-flowchart

Takes a process someone has described and draws it. The value is that a diagram makes gaps visible
that prose hides — an unassigned step, a branch with no rejoin, a loop nobody mentioned.

**First line of every run, before anything else:**

> **demo-skill-flowchart** — drawing the process you described.

## What it needs, and how it gets it

Call `demo-skill-ask-me` for anything undetermined. Do not write questioning of your own.

**Say that you are calling it**, in the line after your own announcement — `calling demo-skill-ask-me
to gather what I need`. One component visibly using another is the thing being demonstrated, and it
is invisible unless the hand-off is stated.

Typically undetermined: where the process starts and ends, who owns the steps that were described
without an owner, what happens on the failure side of a branch that only stated the success side,
and whether a step named twice is one step or two.

Ask only the ones that would change the diagram. A process described completely needs no interview.

## Draw what was described, including where it is incoherent

- **A gap stays a gap.** A step with no owner is drawn with no owner. A branch with one exit is
  drawn with one exit. A diagram that silently completes the process hides the finding the person
  most needs.
- **Mark each gap on the diagram itself** — a visually distinct node or edge — and list the gaps
  beneath it in the conversation, so they are readable without studying the picture.
- **Never infer a step that was not described.** If the sequence cannot work as stated, draw it as
  stated and say why it cannot work.

## Two outputs

**1. The standalone file — this is the component.**

Write one self-contained HTML file that opens by double-clicking it in any browser, on a machine
with no repository, no server and no network.

- Location: the directory the person names. When they name none, `~/demo-kit-output/`, created if
  it does not exist. Never the current directory, so running this inside a repository does not drop
  a file into someone's working tree.
- Filename: `<short-slug-of-the-process>-flowchart.html`.
- The diagram is **inline SVG written into the file**. No `<script src>`, no stylesheet link, no
  web font, no diagram library loaded at run time, no image URL. A file that needs the network is
  not self-contained, and the machine it is opened on may have none.
- Inline the CSS in a `<style>` block. Give the page an explicit background and text colour rather
  than inheriting the browser's.
- Report the absolute path back, and say it can be emailed or copied to any machine as one file.

**2. The repository publish — a convenience, not the component.**

When the current directory is inside a repository that has a `_public/` directory, also write the
same diagram to `_public/demo-kit/<same-filename>`, creating `_public/demo-kit/` if needed. That is
where this repository's HTML Viewer can browse and render it.

When there is no such repository, skip this silently — say the standalone file is the output and
move on. The standalone file is what makes this component general; the publish is one repository's
convenience.

## What it must never do

- **Never write outside those two locations.** Not `docs/`, not `.Codex/`, not `_data/`, not
  `sql/`, not `schemas/`, not any governed document path, and not the repository root.
- **Never overwrite a file it did not just create** without saying so and being told to proceed.
- **Never fix the process while drawing it.** Report the incoherence; the person decides.
- **Never name an industry, company or role of its own.** Everything it draws comes from the input.
