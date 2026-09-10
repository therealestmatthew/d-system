# Architecture

System architecture diagrams, data flow documentation, and schema design rationale. Use Mermaid for diagrams where possible (renders natively in GitHub).

- [HTML generation adversarial audit](ARCH-003-html-adversarial-audit.md): findings and
  proposed plan amendments before implementation.
- [Skills and agents diagram library](diagrams/demo/index.html): six standalone SVGs for the
  training session, indexed by a contact sheet opened straight from the filesystem. These are SVG
  rather than Mermaid deliberately — they are presented at a fixed projector size with no dev server
  and no GitHub renderer available, which is the one case the Mermaid preference above does not
  cover. Their labels come from `brain/concepts/terms-skills-and-agents-demo.md`.
