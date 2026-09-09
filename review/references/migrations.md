# Migrations and recovery

Use when the scoped change moves, rewrites, or destroys persistent state. Establish the old representation, new representation, readers/writers active during transition, and the promised recovery point. Ask only questions relevant to that transition.

- Trace every transformation for lost information: truncation, collisions, precision, null handling, and many-to-one mappings. Show a concrete input that cannot survive a round trip when reversibility is claimed.
- Inspect interrupted and repeated execution. Identify which steps are atomic and which leave mixed state. A transaction keyword is not proof that all involved operations participate in the same transaction.
- Follow compatibility while old and new code coexist. Check the order of schema changes, backfills, reader changes, and retirement of old fields against the deployment plan.
- Distinguish reverting application code, restoring a snapshot, and reversing a data transformation. State which recovery mechanism preserves writes made after migration. Do not accept “rollback available” without the mechanism and its data implications.
- If a plan assumes quiescence, exclusive access, or a bounded dataset, locate that constraint. Do not invent production size or locking behavior; check the relevant database's documentation before making engine-specific claims.

A single destructive transformation may affect correctness, reliability, and delivery. Consolidate those consequences into one evidenced cause. Keep an unrelated access-control defect separate even if it occupies the same migration statement.

Read-only review never runs a migration, creates a backup, restores data, or exercises a rollback on a live system. Request an isolated orchestrator-run check when available; otherwise report static evidence and unverified runtime assumptions.

Provenance: original task-specific checklist implementing the approved review design, version 1.0.0. It contains no claim of database-specific semantics or compliance.
