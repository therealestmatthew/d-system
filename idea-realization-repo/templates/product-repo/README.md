# REPLACE-WITH-PRODUCT-NAME

REPLACE-WITH-ONE-PARAGRAPH: what the product does and who it is for.

Work on this repository is planned, claimed and reviewed in the control repository. See
`CLAUDE.md` for the branch rules.

## Stack

Delete the rows that do not apply.

| Part | Directory | Stack | Manifest |
|---|---|---|---|
| Web front end | `web/` | REPLACE-WITH (for example TypeScript, React, Vite) | `package.json` |
| API / back end | `api/` | REPLACE-WITH (for example Python, FastAPI) | `pyproject.toml` |
| Infrastructure | `infra/` | AWS CDK (REPLACE-WITH language) | `infra/cdk.json` |

CI runs a stack's steps only when its manifest exists (`.github/workflows/product-ci.yml`). If a
part lives in a subdirectory, update the manifest paths and `working-directory` in that workflow.

## First-time setup

```bash
git clone REPLACE-WITH-THE-PRODUCT-REPOSITORY-GIT-URL
cd REPLACE-WITH-REPOSITORY-DIRECTORY
git switch dev
tools/install-hooks.sh          # pre-commit hook: the confidential check
```

Put the deny-list (from the repository owner, never committed) at `.private/deny-list.txt`, or
export `PRIVATE_DENY_LIST=<path>` to point at the control repository's copy.

REPLACE-WITH the stack's install commands, for example:

```bash
npm ci                          # Node
uv sync                         # Python
```

## Run

REPLACE-WITH the commands that start the product locally, for example:

```bash
npm run dev                     # web front end, http://localhost:5173
uv run uvicorn api.main:app --reload   # API, http://localhost:8000
```

## Test

The same commands CI runs in the `verify` job:

```bash
npm run lint && npm test        # Node
uv run pytest                   # Python
(cd infra && npx cdk synth)     # infrastructure: synthesizes only, deploys nothing
python3 tools/check_confidential.py
```

## Deploy

Deploying is done from a developer machine by the control repository's `aws-deploy` agent,
through `tools/aws-sandbox` there. CI never deploys and never calls AWS.
