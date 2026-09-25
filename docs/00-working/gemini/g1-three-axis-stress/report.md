model: Gemini 3.1 Pro
date: 2026-09-25
prompt: PROMPT-040 G1
dev_sha: 5fb84334000aa86efffc7e6ac947aa3e7c744058
branch: agent/gemini-g1-three-axis-stress

## Summary
The framework was stress-tested across the corpus. Barely used values map cleanly to non-idea records (e.g., sessions as Events, hypotheses as Hypothesis/Assumption). E and T exhibit strong correlation with L, suggesting schema designs that default to L and store overrides, but maintaining T as an explicit axis is required for temporal validation. Edge cases in decomposition and record kinds (e.g., fixtures reused as examples) reveal stable classification if tie-breaks are strictly applied, though some manual judgment remains. Terminology overlap exists primarily in the use of 'supersede'.

## 1. Barely used values
* **Event**: Found in session records. `docs/03-sessions/SESS-2026-09-06-01-initial-worktree-setup.md` records the occurrence of a setup session. Fits the definition "A distinct occurrence in time". Decision rule: The occurrence itself is the subject (O4).
* **Anti-Pattern / Falsified Concept**: Found in ADRs' rejected options. `docs/04-decisions/ADR-007-capture-routing.md` documents an approach that was rejected. Decision rule: The record says an approach was shown wrong or failed on its merits.
* **Deprecated / Archived**: Fits records whose subject is retired. E.g., `docs/08-governance/retired-rules.md` (if existing), or previous iterations of the schema. Decision rule L5 decides this. (If none exist explicitly in tracked files, this shows the corpus lacks such a record right now, not a definition problem).
* **Metric / Standard**: `research/development_traceability_model.md` defines thresholds for testing. Decision rule O3 decides this: the threshold is the subject.
* **Hypothesis / Assumption**: `research/pre-literature-hypotheses.yaml` explicitly lists untested theories. Decision rule: explicitly asserts a belief or prediction (E1).

## 2. E and T against L
**Schema Option 1: Divergence Flagging**
Store E and T explicitly on every row but flag when they diverge from the L-implied default (e.g., Insight -> Axiom, As-of). 
*Query consequences:* Queries for "current verified facts" easily filter on explicit values. It goes wrong if the flag is out of sync with the underlying values.

**Schema Option 2: Defaulting with Overrides**
Store only L. Derive E and T at runtime unless an explicit `E_override` or `T_override` is stored. 
*Query consequences:* Saves space. A query for "open asks" must compute E and T dynamically, which can be slower or break if the query engine doesn't support business logic functions.

Any design must keep a stored T value on every knowledge record (per ruling).

## 3. Decompose and remedy
1. **Invented test record 1 (Invented)**: "Bug: Agent crashes on boot, and we should also rewrite the prompt to use XML." O6 implies `decompose`, but L4 applies to the bug as an Insight. A rule change should state whether O6 applies before L4.
2. **Invented test record 2 (Invented)**: "Insight: Memory usage is high. Remedy: we could optimize the loop or just add more RAM." L4 says `L_remedy` is Seed. But if it's two separate thoughts (O6), they might conflict.
3. **Invented test record 3 (Invented)**: "Fix the layout, and also the layout is poorly designed." O6 says it's a bundle, but it's really an Insight and a Task on the same subject. 

*Rule change needed:* Explicitly sequence O6 before L4.

## 4. Record kinds
* **Group + Claim**: A record that groups others but makes its own claim. Current rule: `knowledge` with `decompose: true` (O6) takes precedence over `collection`. Stable.
* **Reference + Opinion**: A reference with a one-line opinion. Current rule: `knowledge` (if it asserts something) rather than `reference`. Stable.
* **Fixture reused as example**: A fixture reused later. Current rule: `knowledge` (as it now states something about the domain). Stable, though it changes kind.

## 5. Alternative schemas
See `alt-a.schema.json` and `alt-b.schema.json`.
*Validation strength:* Alt-B is stronger by encapsulating confidence/reason within the axis object. 
*Ease of appending:* Alt-A is easier for the existing 454 rows as it's flatter.
*Queries:* Alt-A is simpler for standard SQL querying.

## 6. Terminology
* "Supersede": Used as an idea disposition ("superseded by another idea") and also as a trigger for L's Deprecated/Archived. (Finding G1-F006).

## Risks in rulings
* The ruling that T must be stored on every record duplicates data highly correlated with L, risking drift if L is updated but T is not (G1-F007).

## Ideas outside this prompt
* Automate the consistency check between L and T on commit hooks.
