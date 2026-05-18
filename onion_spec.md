RM₀ Deterministic Execution Contract

Version: 1.0.0

Status: Frozen

Scope: Logical determinism, inspectability, replayability

Non-goal: Performance, distribution, optimization, AI autonomy



0\. Purpose

RM₀ defines a deterministic execution substrate for composing logic in a way that is:

Inspectable





Replayable





Non-coercive





Free of hidden state





RM₀ governs how logic executes, not what logic means.



1\. Core Guarantees

Given:

a DAG definition,





a Frozen Snapshot,





and fixed function versions,





all decision outputs MUST be identical across runs.

This is the sole success criterion of RM₀.



2\. Execution Model Overview

An RM₀ execution consists of:

A Snapshot Builder step (impure, pre-execution)





A Frozen Snapshot (immutable input)





A Directed Acyclic Graph (DAG) of pieces





Two piece categories:





decision (pure)





io (impure)







3\. Rule 1 — Directionality (One-Way Flow)

Execution MUST form a Directed Acyclic Graph.





Upstream pieces MUST NOT depend on downstream pieces.





Cycles are forbidden.





Corollary:

Downstream execution MUST NOT alter upstream meaning within the same run.



4\. Rule 2 — One Frozen Snapshot per DAG Run

Each DAG run is evaluated against exactly one Frozen Snapshot.

All decision pieces read from the same snapshot.





No mid-run refreshes.





No mini-snapshots.





No live reads during execution.







5\. Rule 3 — Snapshot Boundary

Snapshot Builder

The Snapshot Builder is a dedicated pre-execution step and is the only place where I/O is allowed before a DAG run.

The Snapshot Builder MAY:

Call databases, APIs, filesystems





Read environment variables





Call time functions (now())





Generate random seeds





Once built, the snapshot is frozen and immutable.

Snapshot Boundary Rules

Decision pieces MUST NOT perform I/O





Decision pieces MUST NOT access ambient state





Time





Randomness





Environment variables





Filesystem





Network





If a decision requires data not present in the snapshot:





This is a modeling error





NOT a reason to perform live I/O





The correct fix is to update the Snapshot Builder and re-run







6\. Rule 4 — Purity Envelope (Decision Pieces)

A decision piece MUST:

Be functionally pure





Read only from:





the Frozen Snapshot





outputs of upstream decision pieces





Return data only





Produce no side effects





Forbidden inside decision pieces:

Database calls





Network calls





File I/O





now(), time()





random(), secrets





Environment access





Mutation of shared or global state





Purity is not a convention. It is a requirement.



7\. Rule 5 — Invariant Placement

All business invariants MUST be enforced in decision pieces.

IO pieces MUST NOT enforce invariants





Databases MAY fail, but MUST NOT be relied upon for correctness





Invariant example:

“Claimed units ≤ available units”

This MUST appear as an explicit decision piece.



8\. Rule 6 — IO Is Downstream Only

IO pieces MAY perform side effects:





Database writes





Logging





Messaging





Notifications





IO pieces MUST depend on decision outputs





Decision pieces MUST NOT depend on IO pieces





IO executes what was decided, nothing more.



9\. Replayability Requirement

The following tuple MUST be sufficient to replay a run:

DAG definition





Frozen Snapshot





Function versions





Re-execution with this tuple MUST produce identical decision outputs.



10\. Diagnostics (Q1–Q6)

RM₀ includes optional diagnostics to verify compliance.

Diagnostics MAY:

Report PASS / FAIL / WARNING





Report dependency failures





Point to violation locations





Diagnostics MUST NOT:

Infer intent





Rewrite code





Auto-fix logic





Developer agency is preserved.



11\. Failure Behavior

If a decision piece performs I/O or reads ambient state:





Execution MUST fail (lint, runtime guard, or test failure)





If required data is missing from the snapshot:





Decision MUST fail explicitly





Live fallback is forbidden







12\. Non-Goals (Explicit)

RM₀ does NOT attempt to provide:

Performance optimization





Distributed consensus





Long-running workflows





Streaming execution





Continuous monitoring





Semantic correctness





Security guarantees





AI autonomy





These belong above RM₀.



13\. Versioning

This specification is versioned.

Changes require a version bump





Existing compliant pieces remain valid under their declared version





No silent drift







14\. Minimal Examples

✅ Compliant

@decision

def validate\_amount(amount, snapshot):

&#x20;   return amount <= snapshot.balance

❌ Non-Compliant

@decision

def validate\_amount(amount):

&#x20;   return amount <= db.query\_balance()  # Forbidden I/O



15\. Compliance Statement

A DAG is RM₀-compliant if and only if all rules in this document are satisfied.

There are no partial tiers.



