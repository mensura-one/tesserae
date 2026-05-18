Plain Text — Minimal Spec (v0.1)

Purpose

Provide a versioned, inspectable representation of meaning between human input and constraint evaluation—without adding authority, inference, or optimization.



Position in Stack

Human Input

→ Mapping (interpretation; explicit \& contestable)

→ Plain Text (representation)

→ CLM (PASS / FAIL)

→ Onion (deterministic execution)

→ APIs (actions)



Core Definition

A piece is a:

named, versioned, single-responsibility unit of normalized meaning

Plain Text is a set of pieces + composition rules that form a structured representation.



Invariants (Non-Negotiable)

Non-Authority





Plain Text does not decide, rank, or optimize.





It cannot affect CLM outcomes.





Explicitness





All inputs, outputs, and rules are declared.





No hidden dependencies.





Versioning





Every piece and mapping is versioned.





No silent changes.





Inspectability





Raw input → mapping → pieces is visible and reviewable.





Contestability





Pieces and mappings can be rejected, replaced, or forked.







Piece Grammar (Required)

PIECE\_ID:

VERSION:

TYPE: (intent | entity | constraint | context | transform)



INPUT:

&#x20; - primitives only (string, number, bool, list, iso\_datetime)



OUTPUT:

&#x20; - normalized primitive or structured dict



PURPOSE:

&#x20; - one sentence, single responsibility



RULES:

&#x20; - explicit mapping / transformation logic



CONTEXT:

&#x20; - declared dependencies (no implicit context)



Composition Rules

Representation = set of pieces (order does not imply authority)





Composition is additive





No piece alters another piece





No implicit constraints introduced







Mapping Layer (Required Boundary)

Mapping performs interpretation





Must be:





explicit





versioned





inspectable





contestable





Plain Text does not interpret; it represents mapping outputs.



Relationship to CLM

CLM evaluates only the Plain Text representation





Plain Text cannot:





override constraints





soften refusal





influence PASS/FAIL







Relationship to Onion

Plain Text does not execute





Onion consumes only CLM-approved artifacts







Prohibited

Hidden context





Implicit invariants





Mixed responsibility (representation + decision)





Optimization, learning, ranking





Claims of semantic correctness or completeness







Acceptance Threshold (Stage Gate)

Plain Text is valid for CLM reference if:

One normalization example exists





CLM can fully reject the representation





Versioning is explicit





No semantic authority is claimed







One-Line Summary

Plain Text encodes meaning as versioned, inspectable pieces so constraints can be applied deterministically without introducing interpretation or authority.





