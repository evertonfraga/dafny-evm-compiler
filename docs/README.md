# Documentation Organization

This directory contains historical documentation, session notes, and planning documents.

## Directory Structure

### `sessions/`
Session notes and work summaries from development sessions.

**Naming Convention:** `YYYY-MM-DD-[session-name].md`

Examples:
- `2025-11-25-nested-mappings.md`
- `2025-11-26-test-reorganization.md`

**Content:** Work summaries, implementation notes, debugging sessions, feature additions.

### `planning/`
Feature planning documents, roadmaps, and gap analyses.

**Content:**
- Feature comparison matrices
- Implementation plans
- Roadmap documents
- Gap analyses
- Phase implementation plans

### `verification/`
Formal verification documentation and status reports.

**Content:**
- Verification capabilities
- Verification status
- Formal verification guides
- Verification semantics

## File Organization Rules

### Session Notes
All session summaries and work logs should follow this format:
- **Filename:** `YYYY-MM-DD-[descriptive-name].md`
- **Location:** `docs/sessions/`
- **Content:** Date, summary, changes made, issues encountered

### Planning Documents
Feature and implementation planning documents:
- **Location:** `docs/planning/`
- **Naming:** Descriptive names (e.g., `ERC20_VERIFICATION_PLAN.md`)
- **Content:** Requirements, implementation phases, success criteria

### Verification Documents
Formal verification related documentation:
- **Location:** `docs/verification/`
- **Naming:** Descriptive names (e.g., `VERIFICATION_STATUS.md`)
- **Content:** Verification capabilities, status, guides

## Project Root Documentation

Keep in project root (user-facing):
- `README.md` - Project overview and quick start
- `TUTORIAL.md` - Step-by-step usage guide
- `HARDHAT_TESTING.md` - Testing guide
- `QUICK_REFERENCE.md` - Command reference
- `LICENSE` - Project license

## Maintenance

When creating new documentation:
1. Determine category (session/planning/verification)
2. Use appropriate naming convention
3. Place in correct directory
4. Update this README if adding new categories

## Current Files

### Sessions (8 files)
Historical work summaries and session notes from development.

### Planning (11 files)
Feature planning, roadmaps, and implementation strategies.

### Verification (5 files)
Formal verification documentation and status reports.

---

**Note:** This organization was established on 2025-11-26 to maintain a clean project structure and preserve historical context.
