"""
Tesserae v0.8 — Workbench for Structured Inquiry
==================================================
Built from:
  v0.2 — dynamic language loader, shell.json, suchness_buckets
  v0.3 — CLM gate on instance creation
  stage1 — hypothesis/domain/layers, snapshots, edit in place,
            non-linear menu, auto-save

New in v0.8:
  Candidates as first-class concept (ID 4)
  Each candidate has status: active | held | dropped | selected
  Dropped candidates require a declared reason
  The car purchase journey is a valid Tesserae instance

RM0 discipline:
  Pure functions (make_*, validate_*, take_snapshot) — no IO
  IO functions (save_, load_, list_) — no logic
  These are separated and labeled clearly

Data lives in: ./instances/ as JSON
Config lives in: concepts.json, shell.json, strings/<lang>.json
"""

import json
import os
import sys
from datetime import datetime, timezone


# ─────────────────────────────────────────────
# PURE FUNCTIONS — no IO, no side effects
# Same input → same output, always
# ─────────────────────────────────────────────

def make_instance(name, hypothesis, domain, layers, lang_id="eng"):
    """
    Create a new instance record.
    Pure — returns dict, touches nothing external.
    """
    return {
        "id":           _slug(name),
        "name":         name,
        "hypothesis":   hypothesis,
        "domain":       domain,
        "layers":       layers,       # replaces 'dimensionality' — plain language
        "lang_id":      lang_id,
        "invariants":   [],           # concept 1 — must remain true
        "constraints":  [],           # concept 2 — warning track
        "tradeoffs":    [],           # concept 3 — tensions
        "candidates":   [],           # concept 4 — named options under consideration
        "notes":        [],           # free-form observations
        "snapshots":    [],           # version history — past is never overwritten
        "created":      _now(),
        "modified":     _now(),
        "status":       "active"      # active | parked | wound_down
    }


def make_entry(kind, statement):
    """
    Create a single invariant, constraint, or tradeoff entry.
    Pure. Versioned from birth.
    """
    return {
        "id":        _slug(statement[:24]),
        "kind":      kind,
        "statement": statement,
        "version":   "1.0",
        "added":     _now()
    }


def make_candidate(name, notes=""):
    """
    Create a candidate entry.
    Pure. Candidates are named options — cars, ideas, vendors, anything.

    Status lifecycle:
      active  — in consideration
      held    — paused, not eliminated (waiting on info, etc.)
      dropped — eliminated, reason required
      selected — the chosen outcome
    """
    return {
        "id":          _slug(name),
        "kind":        "candidate",
        "name":        name,
        "notes":       notes,
        "status":      "active",
        "drop_reason": None,          # required when status → dropped
        "version":     "1.0",
        "added":       _now(),
        "updated":     _now()
    }


def update_candidate_status(candidate, new_status, reason=None):
    """
    Return updated candidate with new status.
    Pure — returns new dict, does not mutate.
    Dropped status requires a reason — enforced here.
    """
    if new_status == "dropped" and not reason:
        return None, "Drop reason is required."

    updated = dict(candidate)
    updated["status"]      = new_status
    updated["drop_reason"] = reason if new_status == "dropped" else candidate.get("drop_reason")
    updated["version"]     = _bump_version(candidate.get("version", "1.0"))
    updated["updated"]     = _now()
    return updated, None


def validate_instance(instance):
    """
    Check instance has minimum required fields.
    Returns (True, None) or (False, reason_string).
    Pure.
    """
    for field in ["name", "hypothesis", "domain", "layers"]:
        if not instance.get(field, "").strip():
            return False, f"Missing: {field}"
    return True, None


def take_snapshot(instance):
    """
    Freeze current state into version history.
    Pure — returns updated instance, does not write to disk.
    The past is never overwritten. Only versioned forward.
    """
    snapshot = {
        "timestamp":  _now(),
        "hypothesis": instance["hypothesis"],
        "domain":     instance["domain"],
        "layers":     instance["layers"],
        "invariants": list(instance["invariants"]),
        "constraints":list(instance["constraints"]),
        "tradeoffs":  list(instance["tradeoffs"]),
        "candidates": list(instance["candidates"]),
        "notes":      list(instance["notes"])
    }
    updated            = dict(instance)
    updated["snapshots"] = instance["snapshots"] + [snapshot]
    updated["modified"]  = _now()
    return updated


# ─────────────────────────────────────────────
# PURE UTILITIES
# ─────────────────────────────────────────────

def _now():
    return datetime.now(timezone.utc).isoformat()

def _slug(text):
    # Readable, filesystem-safe ID from text
    return text.lower().strip().replace(" ", "_")[:32]

def _bump_version(v):
    try:
        major, minor = v.split(".")
        return f"{major}.{int(minor)+1}"
    except Exception:
        return "1.1"


# ─────────────────────────────────────────────
# CONFIG LOADER — reads your existing JSON files
# From v0.2: dynamic language scan, shell.json
# ─────────────────────────────────────────────

def load_shell(path="shell.json"):
    """
    Load shell.json — concepts, suchness, icons.
    Fallback if file missing.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "version": "0.2",
            "suchness_buckets": {
                "western_analytic": ["eng"],
                "dravidian":        ["tel"]
            },
            "concepts": {
                "1": {"suchness": "that which must remain true",        "default_icon": "🔒"},
                "2": {"suchness": "a boundary that can bend",           "default_icon": "🚧"},
                "3": {"suchness": "a relationship between choices",     "default_icon": "⚖️"},
                "4": {"suchness": "a named option under consideration", "default_icon": "🎯"}
            }
        }


def load_concepts(path="concepts.json"):
    """
    Load concepts.json — IDs, suchness, language mappings.
    This is the English-agnostic foundation.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["concepts"]
    except FileNotFoundError:
        return {}


def scan_languages(strings_dir="strings"):
    """
    From v0.2: scan strings/ and strings/community/ for all language skins.
    Returns dict: lang_id → filepath
    """
    found = {}

    def _scan(folder):
        if not os.path.exists(folder):
            return
        for fname in os.listdir(folder):
            if fname.endswith(".json"):
                fpath = os.path.join(folder, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    lid = data.get("language_id")
                    if lid:
                        found[lid] = fpath
                except Exception:
                    pass

    _scan(strings_dir)
    _scan(os.path.join(strings_dir, "community"))
    return found


def load_language(lang_id, lang_paths):
    """Load a language skin by ID. Returns skin dict or None."""
    path = lang_paths.get(lang_id)
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ─────────────────────────────────────────────
# IO LAYER — all disk reads/writes live here
# ─────────────────────────────────────────────

INSTANCES_DIR = "instances"


def _ensure_dir():
    os.makedirs(INSTANCES_DIR, exist_ok=True)


def save_instance(instance):
    """Write instance to disk. Returns filepath."""
    _ensure_dir()
    path = os.path.join(INSTANCES_DIR, f"{instance['id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(instance, f, indent=2, ensure_ascii=False)
    return path


def load_instance(instance_id):
    """Load instance from disk. Returns dict or None."""
    path = os.path.join(INSTANCES_DIR, f"{instance_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_instances():
    """
    Return all instances sorted by most recently modified.
    Returns list of summary dicts.
    """
    _ensure_dir()
    results = []
    for fname in os.listdir(INSTANCES_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(INSTANCES_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            # Count active candidates separately — useful signal
            active_c = sum(
                1 for c in d.get("candidates", [])
                if c.get("status") == "active"
            )
            results.append({
                "id":       d["id"],
                "name":     d["name"],
                "status":   d.get("status", "active"),
                "modified": d.get("modified", ""),
                "counts": {
                    "invariants":  len(d.get("invariants",  [])),
                    "constraints": len(d.get("constraints", [])),
                    "tradeoffs":   len(d.get("tradeoffs",   [])),
                    "candidates":  len(d.get("candidates",  [])),
                    "active_candidates": active_c
                }
            })
        except Exception:
            pass
    results.sort(key=lambda x: x["modified"], reverse=True)
    return results


# ─────────────────────────────────────────────
# CLI HELPERS
# ─────────────────────────────────────────────

def ui(skin, key):
    """Get UI string from skin. Falls back to key name."""
    return skin.get("ui", {}).get(key, key)


def ask(prompt_text):
    """Single prompt. Strips whitespace."""
    return input(f"{prompt_text} ").strip()


def show_status(instance, skin, concepts):
    """
    Always-visible header inside an instance.
    User always knows where they are.
    """
    c = instance
    # Candidate summary: show active vs total
    total_c  = len(c.get("candidates", []))
    active_c = sum(1 for x in c.get("candidates", []) if x.get("status") == "active")
    held_c   = sum(1 for x in c.get("candidates", []) if x.get("status") == "held")
    sel_c    = sum(1 for x in c.get("candidates", []) if x.get("status") == "selected")

    print(f"\n── {c['name']} ──")
    print(
        f"  🔒 {len(c['invariants'])}  "
        f"🚧 {len(c['constraints'])}  "
        f"⚖️  {len(c['tradeoffs'])}  "
        f"🎯 {active_c} active"
        + (f" / {held_c} held" if held_c else "")
        + (f" / {sel_c} selected" if sel_c else "")
        + (f"  [{total_c} total]" if total_c else "")
    )
    print(f"  Hypothesis: {c['hypothesis']}")
    print(f"  Domain: {c['domain']}  |  Layers: {c['layers']}")
    print()


def show_all_entries(instance, skin):
    """Display all entries grouped by concept."""
    sections = [
        ("invariants",  "🔒", "invariant"),
        ("constraints", "🚧", "constraint"),
        ("tradeoffs",   "⚖️ ", "tradeoff"),
        ("notes",       "📝", "note"),
    ]
    for key, icon, label in sections:
        items = instance.get(key, [])
        print(f"\n  {icon} {label}s:")
        if not items:
            print(f"    {ui(skin, 'empty')}")
        else:
            for i, item in enumerate(items, 1):
                text = item["statement"] if isinstance(item, dict) else item
                print(f"    {i}. {text}")

    # Candidates grouped by status — most useful for real inquiry
    candidates = instance.get("candidates", [])
    print(f"\n  🎯 candidates:")
    if not candidates:
        print(f"    {ui(skin, 'empty')}")
    else:
        for status in ["active", "held", "selected", "dropped"]:
            group = [c for c in candidates if c.get("status") == status]
            if group:
                print(f"\n    [{status}]")
                for i, c in enumerate(group, 1):
                    line = f"      {i}. {c['name']}"
                    if c.get("notes"):
                        line += f" — {c['notes']}"
                    if status == "dropped" and c.get("drop_reason"):
                        line += f"\n         ↳ dropped: {c['drop_reason']}"
                    print(line)


# ─────────────────────────────────────────────
# FLOW FUNCTIONS — user interaction sequences
# ─────────────────────────────────────────────

def flow_new_instance(skin, lang_id):
    """
    Guide user through creating a new instance.
    Confirm step lets user revise before committing.
    Not linear — user can redo until satisfied.
    """
    print(f"\n── New Instance ──")
    print("You can revise anything before confirming.\n")

    while True:
        name        = ask(ui(skin, "prompt_instance_name"))
        if not name:
            print("Name cannot be empty.")
            continue
        hypothesis  = ask(ui(skin, "prompt_hypothesis"))
        domain      = ask(ui(skin, "prompt_domain"))
        layers      = ask(ui(skin, "prompt_layers"))

        print(f"\n{ui(skin, 'confirm_title')}")
        print(f"  Name:       {name}")
        print(f"  Hypothesis: {hypothesis}")
        print(f"  Domain:     {domain}")
        print(f"  Layers:     {layers}")
        print()
        print(ui(skin, "confirm_create"))
        print(ui(skin, "confirm_revise"))
        print(ui(skin, "confirm_cancel"))

        choice = ask(ui(skin, "prompt_choice"))
        if choice == "1":
            instance = make_instance(name, hypothesis, domain, layers, lang_id)
            valid, reason = validate_instance(instance)
            if not valid:
                print(f"Cannot create: {reason}")
                continue
            instance = take_snapshot(instance)  # snapshot at birth
            save_instance(instance)
            print(f"\n{ui(skin, 'saved')} '{name}' created.")
            return instance
        elif choice == "2":
            continue
        else:
            return None


def flow_open_instance(skin):
    """Pick from existing instances."""
    instances = list_instances()
    if not instances:
        print(f"\n{ui(skin, 'no_instances')}")
        return None

    print("\n── Open Instance ──")
    for i, inst in enumerate(instances, 1):
        c = inst["counts"]
        print(
            f"  {i}. {inst['name']}  "
            f"[🔒{c['invariants']} 🚧{c['constraints']} "
            f"⚖️ {c['tradeoffs']} 🎯{c['active_candidates']}/{c['candidates']}]  "
            f"({inst['status']})"
        )

    choice = ask("Choice (number) or 0 to cancel:")
    if choice == "0" or not choice.isdigit():
        return None
    idx = int(choice) - 1
    if 0 <= idx < len(instances):
        inst = load_instance(instances[idx]["id"])
        if inst:
            print(f"\n{ui(skin, 'loaded')} '{inst['name']}'")
            return inst
    print(ui(skin, "not_found"))
    return None


def flow_add_entry(instance, kind, skin):
    """
    Add invariant, constraint, or tradeoff.
    Multiple in one sitting. Conversational, not one-shot.
    Auto-saves after additions.
    """
    icons   = {"invariant": "🔒", "constraint": "🚧", "tradeoff": "⚖️"}
    icon    = icons.get(kind, "")
    print(f"\n── Add {icon} {kind} ──")
    print("Type each statement, Enter to add.")
    print("'done' to finish, 'cancel' to abort.\n")

    added = 0
    while True:
        statement = ask(ui(skin, "prompt_statement"))
        if statement.lower() == "done":
            break
        if statement.lower() == "cancel":
            return instance
        if not statement:
            continue
        entry = make_entry(kind, statement)
        instance[f"{kind}s"].append(entry)
        instance["modified"] = _now()
        added += 1
        print(f"  Added {icon}")

    if added:
        instance = take_snapshot(instance)
        save_instance(instance)
        print(f"\n{ui(skin, 'saved')} {added} {kind}(s) added.")
    return instance


def flow_add_candidate(instance, skin):
    """
    Add a named candidate.
    Name + optional notes. Status starts as active.
    This is how you track the CX-5, the RAV4, any option.
    """
    print(f"\n── Add 🎯 candidate ──")
    name = ask(ui(skin, "prompt_candidate_name"))
    if not name:
        return instance
    notes = ask(ui(skin, "prompt_candidate_note"))
    candidate = make_candidate(name, notes)
    instance["candidates"].append(candidate)
    instance["modified"] = _now()
    instance = take_snapshot(instance)
    save_instance(instance)
    print(f"\n{ui(skin, 'saved')} '{name}' added as active candidate.")
    return instance


def flow_candidate_status(instance, skin):
    """
    Update a candidate's status.
    Dropped requires a reason — enforced, not optional.
    This is where the narrowing path is recorded honestly.
    """
    candidates = instance.get("candidates", [])
    if not candidates:
        print(f"\n  {ui(skin, 'empty')}")
        return instance

    print(f"\n── Update Candidate Status ──")
    for i, c in enumerate(candidates, 1):
        print(f"  {i}. [{c['status']}] {c['name']}")

    idx_input = ask("Which candidate? (0 to cancel):")
    if not idx_input.isdigit() or idx_input == "0":
        return instance
    idx = int(idx_input) - 1
    if not (0 <= idx < len(candidates)):
        print("Invalid choice.")
        return instance

    candidate = candidates[idx]
    print(f"\n  Current: [{candidate['status']}] {candidate['name']}")
    print(ui(skin, "candidate_status_menu"))
    status_map = {"1": "active", "2": "held", "3": "dropped", "4": "selected"}
    s_choice = ask(ui(skin, "prompt_choice"))
    new_status = status_map.get(s_choice)
    if not new_status:
        return instance

    reason = None
    if new_status == "dropped":
        # Reason is required — declared, not silent
        reason = ask(ui(skin, "prompt_drop_reason"))
        if not reason:
            print("Drop reason required. Cancelling.")
            return instance

    updated, error = update_candidate_status(candidate, new_status, reason)
    if error:
        print(f"Error: {error}")
        return instance

    instance["candidates"][idx] = updated
    instance["modified"] = _now()
    instance = take_snapshot(instance)
    save_instance(instance)
    print(f"\n{ui(skin, 'saved')} '{candidate['name']}' → {new_status}.")
    return instance


def flow_add_note(instance, skin):
    """Add a free-form note."""
    note = ask(ui(skin, "prompt_statement"))
    if note:
        instance["notes"].append(note)
        instance["modified"] = _now()
        instance = take_snapshot(instance)
        save_instance(instance)
        print(f"\n{ui(skin, 'saved')}")
    return instance


def flow_edit_entry(instance, skin):
    """
    Edit any entry in place.
    Old state preserved in snapshot before change.
    This is the 'correct yourself in conversation' feel.
    """
    print(f"\n── Edit Entry ──")
    print("  1. Invariants 🔒")
    print("  2. Constraints 🚧")
    print("  3. Tradeoffs ⚖️")
    print("  4. Notes 📝")
    print("  0. Cancel")
    section_map = {"1": "invariants", "2": "constraints",
                   "3": "tradeoffs",  "4": "notes"}
    key = section_map.get(ask(ui(skin, "prompt_choice")))
    if not key:
        return instance

    items = instance.get(key, [])
    if not items:
        print(f"  {ui(skin, 'empty')}")
        return instance

    for i, item in enumerate(items, 1):
        text = item["statement"] if isinstance(item, dict) else item
        print(f"  {i}. {text}")

    idx_input = ask("Which number? (0 to cancel):")
    if not idx_input.isdigit() or idx_input == "0":
        return instance
    idx = int(idx_input) - 1
    if not (0 <= idx < len(items)):
        return instance

    current  = items[idx]
    cur_text = current["statement"] if isinstance(current, dict) else current
    print(f"  Current: {cur_text}")
    new_text = ask("New statement (Enter to keep):")

    if new_text:
        if isinstance(current, dict):
            items[idx]["statement"] = new_text
            items[idx]["version"]   = _bump_version(current.get("version", "1.0"))
        else:
            items[idx] = new_text
        instance[key]      = items
        instance["modified"] = _now()
        instance = take_snapshot(instance)
        save_instance(instance)
        print(f"\n{ui(skin, 'saved')} Updated.")
    return instance


def flow_remove_entry(instance, skin):
    """
    Remove an entry. Snapshot taken first — past preserved.
    """
    print(f"\n── Remove Entry ──")
    print("  1. Invariants 🔒")
    print("  2. Constraints 🚧")
    print("  3. Tradeoffs ⚖️")
    print("  4. Notes 📝")
    print("  0. Cancel")
    section_map = {"1": "invariants", "2": "constraints",
                   "3": "tradeoffs",  "4": "notes"}
    key = section_map.get(ask(ui(skin, "prompt_choice")))
    if not key:
        return instance

    items = instance.get(key, [])
    if not items:
        print(f"  {ui(skin, 'empty')}")
        return instance

    for i, item in enumerate(items, 1):
        text = item["statement"] if isinstance(item, dict) else item
        print(f"  {i}. {text}")

    idx_input = ask("Which number to remove? (0 to cancel):")
    if not idx_input.isdigit() or idx_input == "0":
        return instance
    idx = int(idx_input) - 1
    if not (0 <= idx < len(items)):
        return instance

    removed_text = items[idx]["statement"] if isinstance(items[idx], dict) else items[idx]
    print(f"  Remove '{removed_text}'?  1. Yes  0. No")
    if ask(ui(skin, "prompt_choice")) == "1":
        instance[key].pop(idx)
        instance["modified"] = _now()
        instance = take_snapshot(instance)
        save_instance(instance)
        print(f"\n{ui(skin, 'saved')} Removed.")
    return instance


def flow_update_instance(instance, skin):
    """Update hypothesis, domain, or layers. Snapshots before change."""
    print(f"\n── Update Instance ──")
    print("  1. Hypothesis")
    print("  2. Domain")
    print("  3. Layers")
    print("  0. Cancel")
    field_map = {"1": "hypothesis", "2": "domain", "3": "layers"}
    field = field_map.get(ask(ui(skin, "prompt_choice")))
    if not field:
        return instance

    print(f"  Current: {instance[field]}")
    new_val = ask("New value (Enter to keep):")
    if new_val:
        instance[field]      = new_val
        instance["modified"] = _now()
        instance = take_snapshot(instance)
        save_instance(instance)
        print(f"\n{ui(skin, 'saved')} {field.capitalize()} updated.")
    return instance


def flow_view_history(instance):
    """Show snapshot history. The past is always visible."""
    snapshots = instance.get("snapshots", [])
    if not snapshots:
        print("\n  No snapshots yet.")
        return
    print(f"\n── Snapshot History ({len(snapshots)} versions) ──")
    for i, snap in enumerate(snapshots, 1):
        active_c = sum(
            1 for c in snap.get("candidates", [])
            if c.get("status") == "active"
        )
        print(
            f"\n  v{i} — {snap['timestamp'][:19].replace('T',' ')}"
            f"\n    Hypothesis: {snap['hypothesis']}"
            f"\n    🔒{len(snap['invariants'])}  "
            f"🚧{len(snap['constraints'])}  "
            f"⚖️ {len(snap['tradeoffs'])}  "
            f"🎯{active_c} active candidates"
        )


def flow_park(instance, skin):
    """Park instance — preserved, set aside, not deleted."""
    print(f"\n  Park '{instance['name']}'?")
    print("  It is preserved. Reopen anytime.")
    print("  1. Yes   0. No")
    if ask(ui(skin, "prompt_choice")) == "1":
        instance["status"]   = "parked"
        instance["modified"] = _now()
        save_instance(instance)
        print(f"\n{ui(skin, 'parked')}")
        return instance, True    # True = exit to main menu
    return instance, False


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

def run():
    # Load config from your existing files
    shell    = load_shell("shell.json")
    concepts = load_concepts("concepts.json")

    # Scan for available languages dynamically (from v0.2)
    lang_paths = scan_languages("strings")
    if not lang_paths:
        print("No language skins found in strings/. Exiting.")
        sys.exit(1)

    # Language selection
    print("\n=== Tesserae v0.8 ===")
    lang_list = list(lang_paths.items())
    print("Select language:")
    for i, (lid, fpath) in enumerate(lang_list, 1):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                lname = json.load(f).get("language_name", lid)
        except Exception:
            lname = lid
        print(f"  {i}. {lname} ({lid})")

    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(lang_list):
            lang_id = lang_list[int(choice)-1][0]
            break
        elif choice in lang_paths:
            lang_id = choice
            break
        print("Invalid. Try again.")

    skin = load_language(lang_id, lang_paths)
    if not skin:
        print(f"Could not load language {lang_id}. Exiting.")
        sys.exit(1)

    print(f"\n{ui(skin, 'welcome')}\n")

    current = None   # currently open instance

    while True:
        if current:
            # ── Inside an instance ──
            show_status(current, skin, concepts)
            print(ui(skin, "instance_menu_title"))
            for key in [
                "opt_add_invariant", "opt_add_constraint",
                "opt_add_tradeoff",  "opt_add_candidate",
                "opt_add_note",      "opt_view_all",
                "opt_edit",          "opt_remove",
                "opt_candidate_action", "opt_update_instance",
                "opt_snapshot",      "opt_park",
                "opt_history",       "opt_back"
            ]:
                print(ui(skin, key))

            choice = ask(ui(skin, "prompt_choice"))

            if choice == "1":
                current = flow_add_entry(current, "invariant", skin)
            elif choice == "2":
                current = flow_add_entry(current, "constraint", skin)
            elif choice == "3":
                current = flow_add_entry(current, "tradeoff", skin)
            elif choice == "4":
                current = flow_add_candidate(current, skin)
            elif choice == "5":
                current = flow_add_note(current, skin)
            elif choice == "6":
                show_all_entries(current, skin)
            elif choice == "7":
                current = flow_edit_entry(current, skin)
            elif choice == "8":
                current = flow_remove_entry(current, skin)
            elif choice == "9":
                current = flow_candidate_status(current, skin)
            elif choice == "10":
                current = flow_update_instance(current, skin)
            elif choice == "11":
                current = take_snapshot(current)
                save_instance(current)
                print(f"\n{ui(skin, 'snapshot_taken')}")
            elif choice == "12":
                current, go_back = flow_park(current, skin)
                if go_back:
                    current = None
            elif choice == "13":
                flow_view_history(current)
            elif choice == "0":
                save_instance(current)
                print(f"\n{ui(skin, 'saved')}")
                current = None

        else:
            # ── Main menu ──
            print(f"\n{ui(skin, 'menu_title')}")
            for key in [
                "menu_new_instance", "menu_open_instance",
                "menu_list_instances", "menu_switch_language",
                "menu_exit"
            ]:
                print(ui(skin, key))

            choice = ask(ui(skin, "prompt_choice"))

            if choice == "1":
                new_inst = flow_new_instance(skin, lang_id)
                if new_inst:
                    current = new_inst

            elif choice == "2":
                opened = flow_open_instance(skin)
                if opened:
                    current = opened

            elif choice == "3":
                instances = list_instances()
                if not instances:
                    print(f"\n{ui(skin, 'no_instances')}")
                else:
                    print("\n── All Instances ──")
                    for inst in instances:
                        c = inst["counts"]
                        print(
                            f"  {inst['name']}  "
                            f"[🔒{c['invariants']} 🚧{c['constraints']} "
                            f"⚖️ {c['tradeoffs']} 🎯{c['active_candidates']}/{c['candidates']}]"
                            f"  ({inst['status']})"
                        )

            elif choice == "4":
                # Switch language without restarting
                print("\nAvailable languages:")
                for i, (lid, fpath) in enumerate(lang_list, 1):
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            lname = json.load(f).get("language_name", lid)
                    except Exception:
                        lname = lid
                    print(f"  {i}. {lname} ({lid})")
                lc = input("> ").strip()
                if lc.isdigit() and 1 <= int(lc) <= len(lang_list):
                    new_lid  = lang_list[int(lc)-1][0]
                    new_skin = load_language(new_lid, lang_paths)
                    if new_skin:
                        skin    = new_skin
                        lang_id = new_lid
                        print(f"\n{ui(skin, 'welcome')}")

            elif choice == "0":
                print(f"\n{ui(skin, 'goodbye')}\n")
                sys.exit(0)


if __name__ == "__main__":
    run()
