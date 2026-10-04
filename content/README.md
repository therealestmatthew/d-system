# Content: build-in-public series

Planning material for a series of posts on X about D-System and the Idea Realization Engine (IRE),
written while they are being built and leading up to the IRE's release. This directory holds the
strategy, the post queue and the drafts. It is not governed documentation: files here carry no
front matter and no document code, and nothing in `src/governance` reads them.

Related ideas: `000015` (X content series), `000016` (multi-platform presence), `000017` (content
automation pipeline). This directory is the manual first step those ideas describe. It does not
change their status.

## Files

| File | What it holds |
|---|---|
| [arc.md](arc.md) | The order of the series: eight stages from origin to the IRE release, and the later-stage formats |
| [pillars.md](pillars.md) | The five recurring post types, each mapped to the repository records that back it |
| [image-style.md](image-style.md) | When a post gets an image, the house visual style, production methods, alt text |
| [calendar.md](calendar.md) | The ordered post queue with each post's status |
| `posts/NNN-slug/` | One directory per post: `post.md`, and `image.md` plus image files when the post has an image |

## Purpose

Show, with evidence, how one person runs a software project through AI coding agents under
explicit governance, and what that taught them. The IRE is the product the series leads to; the
series earns attention for it by showing the parts as they were built and the failures that shaped
them.

## Audience

1. Developers who use AI coding agents (Claude Code, Codex, Gemini CLI) and run into the same
   problems: agents colliding, checks that pass without checking, work that drifts from what was
   asked.
2. People building agent workflows or multi-agent setups who want concrete mechanisms rather than
   general advice.
3. Technical leads deciding how much governance agent-produced work needs.

## Voice

- First person, the owner: "I built", "I learned". The agents are tools the owner directs, and the
  posts name them plainly (Claude Code, Codex, the model in use).
- Plain statement. Say what the mechanism does and what happened; no metaphor where a literal
  phrase exists. The writing-style rule in `CLAUDE.md` applies to posts as much as to documents.
- Numbers come from the repository, with the source recorded in the post's `Sources` section.
  A number that cannot be traced to a file or a command is not used.
- Failures are reported as they happened, including the owner's own wrong calls.

## Goals

1. Publish the arc in order through to the IRE release.
2. Each post explains one mechanism or one lesson, so it is useful to a reader who never sees
   another post in the series.
3. Collect the reactions and questions posts receive as input for the release (they become ideas
   through the normal capture path, not notes in this directory).

The series has no follower or engagement targets yet. Whether to set them is the owner's call.

## Cadence

Five posts a week (owner, 2026-10-04). Not every post needs an image; [image-style.md](image-style.md)
says when one is used. At five a week the eight-stage arc in [arc.md](arc.md) takes about eight
weeks; the release date itself is the owner's and is not set here.

## Confidentiality rules

These apply to every draft, every image and every shared file.

1. **No client identifiers.** No client, employer, engagement or person name from the owner's
   consulting work, and nothing from `_private/`. Examples use the fictional set in `_data/` only.
2. **Run the private-content check on every draft before it is marked `approved`.** Run
   `uv run python tools/check_no_private_content.py` from the primary checkout, where it checks the
   identifier list. In a worktree it reports `0 identifiers checked` and proves only the path rule.
3. **Screenshots and generated diagrams show the tracked tree only.** Check every screenshot for
   terminal paths, user names, branch names of private work and notification text before use.
4. **No repository link** until the owner decides the repository's visibility for the release.
5. **Shared reference files are sanitised copies**, reviewed line by line; the IRE plugin's
   templates (`plugins/idea-realization/templates/`) are the preferred starting point because a
   test forbids repository-specific instances in them.
6. **Nothing is posted by an agent.** Agents draft, cite and check. The owner publishes.

## Approval flow

| Status | Meaning | Who sets it |
|---|---|---|
| `planned` | A slot in the calendar with a topic and sources, no text yet | Agent or owner |
| `draft` | `post.md` written, sources cited, image brief written if the post has an image | Agent |
| `reviewed` | An independent review agent has checked the draft against its cited sources and the confidentiality rules, and every finding is fixed or accepted | Agent, after the review |
| `approved` | The owner has read the final text and image, and the private-content check has passed from the primary checkout | Owner |
| `posted` | Published on X; the post's URL and date are recorded in `post.md` | Owner |

A post that changes after `approved` returns to `draft`.
