# tesserae

**Accessible structure to think, decide, or create.**

Tesserae is a language-agnostic, model-agnostic, user-owned structured inquiry workbench.

## Current Status (Stage 1)

- Persistent instances (one JSON file per inquiry)
- Hypothesis, domain, and dimensionality declaration
- Invariants 🔒, constraints 🚧, tradeoffs ⚖️
- Candidates with status lifecycle (active, held, dropped with reason, selected)
- Full snapshot history (every action preserved, no overwrite)
- Edit or remove any entry in place
- Non-linear, conversational menu (no blank prompt)
- Language skins (English, Telugu) – more can be added via `strings/` folder
- CLM gate on instance creation
- Auto‑save on every action
- Park / wind‑down status for instances

## Quick Start

1. Clone the repo
2. Run `python tesserae_v08.py`
3. Select language (english / telugu)
4. Create a new instance (name, hypothesis, domain, dimensionality)
5. Add invariants, constraints, tradeoffs, and candidates
6. Edit, remove, or park entries as your inquiry evolves
7. Snapshots are saved automatically — your history is preserved

Requires: Python 3.8+

## Documentation

- [Manifesto](MANIFESTO.md)
- [Contributing](CONTRIBUTING.md)

## License

- Core code: MIT
- Plaintext pieces and language skins: CC BY
