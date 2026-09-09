# Templates

Reusable templates for HTML generation and styling.

| Directory | Purpose |
|---|---|
| `html/` | HTML page and component templates — base layouts, section blocks, composable page structures |
| `styles/` | CSS/style definitions, design tokens, theme files tied to specific HTML template families |

## HTML Generation System

Templates here are consumed by the HTML Generation Framework:
- Raw source data (from `_data/` or DuckDB) feeds into templates
- Deterministic generation scripts live in `tools/` or `src/`
- React/FastAPI interface in `ts/` + `src/` drives generation, previews results, and triggers agentic workflows
- Output pages can be grouped into dynamically composable multi-page frameworks
