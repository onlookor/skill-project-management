> [中文](README.md) | English

## Project Management Grounding Compilation Skill

**In one sentence**: compile general project management knowledge into rules and entries that are **decidable, traceable, and executable by a small local LLM**, so that "project management" gains composability comparable to requirements engineering and software engineering skills without depending on any particular domain skill.

### What this skill is

- A **domain-vacuum** body of statutory rules (`GRAMMAR.md`): it defines only the meta-concepts that no project can reduce away (`Project`, `Actor`, `Commitment`, `Deliverable`, `Constraint`, `Outcome`, `Assertion`), and no domain-specific object appears in its rules.
- A **governance structure** (`CHARTER.md` + `CONSTITUTION.md` + `adr/`): it defines who may change the statutory rules, how, and what counts as a legitimate change; it physically separates "intent" and "meta-rules" from the rule text.
- A **closed source ledger** (`SOURCE_LEDGER.md`): the legal values of `grounding_ref` are a closed enumeration, and every source carries a version, status (active/deprecated/superseded), authority tier, verification date, and **claim-level mapping** (which specific rule the source supports).
- A **method registry** (`knowledge/`): ontology entries and method entries are kept separate. Method entries (estimation, WBS decomposition, risk identification, earned value calculation, procurement process, ...) directly compensate for the knowledge hunger of small local models; ontology entries (core terms and relations) are the semantic basis that makes the statutory rules decidable.
- A set of **compilation and validation specifications** (`spec/` + `validation/`): they translate rules into a checklist executable by a **deterministic checker**, and define the format and verification conditions of `assumption`.
- An **interface contract specification** (`contracts/`): it defines how domain skills fill slots in the project management skill; v1 enables only **single-layer authoritative location** (a standalone contract file), while multi-layer merge semantics are defined but not enabled.

### What this skill is not

- **It is not an excerpt of PMBOK.** The processes and knowledge areas of PMBOK are products of a specific methodology; this skill anchors its ontological primitives in a domain-independent core layer (ProjectCO core concepts and the ISO 21502:2020 conceptual framework). Specific methodologies exist as method entries and do not enter the statutory rules.
- **It is not a replacement for a knowledge base.** The method registry is a **deterministically queryable** knowledge carrier, not a textbook for a model to read through.
- **It is not bound to a particular host runtime.** PACT, external domain ontologies, and any external coordination engine or ontology framework are **optional plugins**; the skill remains complete without them (see commitment C4 in `CHARTER.md`).
- **It is not a project manager that "thinks".** It provides legitimacy criteria, knowledge entries, and checklists; decision weight, approval responsibility, and human review points are non-transferable (Article 1 of `CONSTITUTION.md`, commitment C5 in `CHARTER.md`).

## File map (navigation pointers; **Article 4 of `AGENTS.md` is authoritative**)

| File | Layer | Role |
|---|---|---|
| `README.md` | Entry | Chinese version of this file: positioning, navigation, reading paths |
| `README.en.md` | Entry | This file: English version |
| `manifest.json` | Entry | Package version and contract schema version (for reference by external skills) |
| **`QUICKSTART.md`** | **Entry** | **Quick start: minimal walkthrough plus an LLM integration example** |
| `AGENTS.md` | Execution | Execution conventions: source acquisition (local first), schedule discipline, authoritative directory structure, mechanized checking |
| `CHANGELOG.md` | Scheduling | The sole register of change history (rules in Article 3.1 of `AGENTS.md`) |
| `TODO.md` | Scheduling | Ledger of individual work items (rules in Article 3.2 of `AGENTS.md`; order and exit conditions in `ROADMAP.md`) |
| **`ROADMAP.md`** | **Scheduling** | **Roadmap: goals and completion criteria, milestones and exit conditions, critical path, release points** |
| `STATE.md` | Scheduling | The sole register of the current status of each file |
| **`ERRATA.md`** | **Scheduling** | **Hallucination correction ledger: compilation errors, external review dispositions, statements pending verification** |
| `CHARTER.md` | Intent | Why the skill exists, whom it serves, testable commitments C1–C6, horizontal relations with domain skills |
| `CONSTITUTION.md` | Governance | Who may change the statutory rules and how; source closure; three levels of self-containment; optional plugin clause; compilation governance (Article 10); terminology governance and citation rules (Article 11); **grounding governance (Article 12)** |
| `GRAMMAR.md` | Legislation | Statutory rule groups A–G |
| `SOURCE_LEDGER.md` | Legislation | Closed source ledger (with version, status, authority tier, claim-level mapping) |
| **`GLOSSARY.md`** | **Legislation (support)** | **Glossary: domain-independent core concepts, framework-specific mechanism terms, compilation-domain terms, governance terms, industry abbreviations, interface contract terms; includes terminology governance and citation rules** |
| **`spec/COMPILATION_META.md`** | **Compilation meta-framework** | **What counts as legitimate compilation: P1–P6, admission conditions, selection/coexistence/replacement, failure classification, compilation governance** |
| **`spec/COMPILATION_METHODS.md`** | **Compilation method registry** | **Which compilation methods exist, which one is currently enabled, why, and replacement history** |
| **`spec/CONTEXT_ASSEMBLY.md`** | **Execution** | **Context assembly specification: four-scenario load sets, token budget, assembly manifest** |
| **`spec/GROUNDING_CRITERIA.md`** | **Execution** | **Grounding completion criteria: six criteria, status semantics, criteria record** |
| **`spec/ANCHOR_SPEC.md`** | **Specification** | **Anchor and reference specification: stable IDs, heading paths, fingerprint baseline, explicit failure on broken anchors** |
| **`spec/methods/deterministic-checker.md`** | **Concrete compilation method** | **Declaration of the deterministic-checker method: coverage, P1–P6 argument, check_id registry, translation specification** |
| `spec/ASSUMPTION_PROTOCOL.md` | Execution | Specification of the format and verification conditions of the `assumption` block (method-independent) |
| `spec/INTERFACE_CONTRACT_SPEC.md` | Execution | Slot definitions; **inter-skill information flow**; v1 single-layer resolution; declaration of items not mappable to PACT (method-independent) |
| `contracts/` | Execution | Contract schema, resolution rules, two domain examples (construction, software engineering) |
| `knowledge/` | Knowledge | Ontology entries and method registry (deterministically queryable, not for reading through) |
| `adr/` | Governance | ADR format notes and governance decision records (ADR-0001–ADR-0007) |
| **`scripts/`** | **Support** | **Auxiliary checking scripts: STATE reconciliation, source compilation landings, anchor resolution and validation, GLOSSARY/JSONL sync specification** |
| `validation/CHECKLIST.md` | Execution | Checklist generated from `COMPILATION_META.md` + `spec/methods/deterministic-checker.md` |
| **`validation/test-cases/`** | **Execution** | **Counter-example test case library (3 currently on disk)** |

**On the status of domain skills**: this skill and any domain skill (requirements engineering, software engineering, construction, ...) are in a **horizontal peer relationship**; no domain skill enjoys special status. Concrete connection instances between skills (such as the artifact flow from requirements to software) are registered in `contracts/examples/` or deployment configuration, and **do not enter the statutory rules**; see the "inter-skill information flow" section of `spec/INTERFACE_CONTRACT_SPEC.md`.

**On the status of compilation methods**: a compilation method is itself an optional plugin and is not a prerequisite for the completeness of the skill (Article 10.3 of `CONSTITUTION.md`). `CM-DET-CHECKER` is currently enabled; other methods (skill cards, human checklists, PACT rules) are registered as candidates, and enabling one requires an ADR.

## Versions and releases

- There is only one package version, declared as a release point by an annotated git tag (ADR-0003); the tag message is the release note. Current release point: `v0.4.0`.
- Files carry no version number and no file-level status; for current status see `STATE.md`, and for change history see `CHANGELOG.md`.
- An external skill referring to this package reads the root `manifest.json`; `pm_contract_version` is a data field of contract files and does not follow the package version.
- Version increments: incompatible change to a normative clause or contract schema → major; new specification or file → minor; pure clarification or errata → patch.
- Whether a compiled artifact is stale is decided by the `source_commit` of its generation baseline (ADR-0004), not by comparing version numbers.

## Three reading paths

**First contact (want to know what this is)**: this file → `QUICKSTART.md` → the "testable design commitments" section of `CHARTER.md` → rule group A in `GRAMMAR.md` → consult `GLOSSARY.md` for unfamiliar terms.

**Daily use (want to integrate the skill into a project)**: Articles 6 and 6bis of `AGENTS.md` → `spec/CONTEXT_ASSEMBLY.md` → the slot definitions in `spec/INTERFACE_CONTRACT_SPEC.md` → the closest example under `contracts/examples/` → place a contract file in your own domain skill directory → `validation/CHECKLIST.md` → evaluate against `spec/GROUNDING_CRITERIA.md` before deployment.

**Governance change (want to modify statutory rules, sources, or compilation)**: the full `CONSTITUTION.md` → `adr/0001-*.md`, `adr/0002-*.md`, `adr/0003-*.md`, `adr/0004-*.md`, `adr/0005-*.md`, `adr/0006-*.md` → `adr/ADR-TEMPLATE.md` → the registration rules in `SOURCE_LEDGER.md` → if terminology is involved, read Sections 4 and 5 of `GLOSSARY.md` and Article 11 of `CONSTITUTION.md` → if compilation is involved, read `spec/COMPILATION_META.md` and `spec/COMPILATION_METHODS.md` → after the change, append a `CHANGELOG.md` batch and update statuses in `TODO.md`; register errors in `ERRATA.md`.
