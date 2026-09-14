# 06 — Generalized DDD skill (replaces taager-backend-architecture)

## Goal

Ship a topology-agnostic `ddd` skill from this repo, and stop carrying
`taager-backend-architecture` as a global skill in `~/.claude/skills/`.

The current skill hardcodes one shape: every bounded context splits into
`command/` + `query/` before anything else. That is false across the estate, so
the skill mis-advises on any context that doesn't split — and this repo is a
public personal repo, which is the wrong home for internal Taager conventions.

## Research findings

Surveyed 14 Kotlin services under `~/Projects`. Four distinct context
topologies are in production, two of them inside the *same* service:

| Topology | Shape | Real examples |
|---|---|---|
| Split (CQRS) | `command[s]/` + `quer[y\|ies]/` + `common/` | wallet, stores, cms-v2, merchant-engagement, lead, 6/7 allocation contexts |
| Command-only | `commands/` + `common/`, no read side, no controllers | `allocation/inventory` (scheduler + gateway driven), `order-fulfillment/billing`, `cmos/ordercommunication` |
| Unsplit layered | `domain/` + `application/` + `infrastructure/` directly under the context | `travolta/location`, `travolta/inventory`, `travolta/auth`, `travolta/warehouse`, `travolta/variant` |
| Flat / technical only | no bounded contexts at all | cron-service, integration-service |

Mixed within one service: `travolta` runs `picklist/command`+`query` next to an
unsplit `location/`; `allocation` uses `shipping/command` (singular) beside
`capacity/commands` (plural). `travolta/location` also puts `controller/` and
`service/` as top-level siblings of `infrastructure/` — a shape the current
skill has no vocabulary for.

Conclusion: **layering is the invariant; the command/query split is an optional
per-context overlay.** The skill must invert its current emphasis.

## Approach

Replace one 277-line monolith with a small core plus two loaded-on-demand
references (progressive disclosure — the core stays cheap in every prompt):

```
skills/ddd/
├── SKILL.md                      # invariants + topology detection + artifact map
└── references/
    ├── cqrs.md                   # the full split canon (read only when the context splits)
    └── kotlin-spring.md          # OpenAPI contract-first, JPA/DBO/DAO, testing tiers
```

`SKILL.md` leads with a **detection step** — identify the context's topology and
naming variant before writing a line — then states the invariants that hold in
all four topologies, then an artifact table keyed by *layer + role* with a
"where it lands per topology" column instead of hardcoded `command/domain/...`
paths, plus explicit rules for **choosing** whether a new context splits.

### Conform vs. improve — the balance

The skill's hardest job is not naming folders, it is deciding when the repo's
existing pattern wins over the canon. Detection alone is not enough: the model
has to sort what it finds into three buckets and act differently on each.

| What it found | Test | Action |
|---|---|---|
| **Variation** — arbitrary choice, no correctness consequence (`command` vs `commands`, `Repo` vs `Repository`, extension functions vs mapper class, controller granularity, `db/dao` vs `db/dao/pg`) | Does the choice change what the code can do, or which invariants hold? **No.** | **Conform silently.** Match the module. The only error is introducing a *third* pattern. |
| **Defect** — breaks an invariant (ORM import in domain, business rule in the use case, query importing the write aggregate, whole aggregate parked in `common`, converters in `application/`) | Same test. **Yes.** | **Don't propagate.** Write the new code correctly, name the surrounding defect once in the handoff, don't refactor uninvited. |
| **Typo / degenerate** — `infrastucture`, `...CommandsCommandsRepositoryImpl`, singular `gateway/` beside plural `controllers/` | Is it just wrong, with no argument for it? | **Don't copy.** Spell new files correctly; mention it; never mass-rename as a side effect. |

Two rules make the balance decidable rather than a judgment call:

- **Frequency decides.** One occurrence may be an accident; the same deviation
  across the whole service *is* that service's convention and is canon there.
  So the skill must instruct reading **several** sibling modules before
  concluding what the pattern is — never generalizing from the first file opened.
- **Priority order: correctness of new code > local consistency > canon.**
  If staying correct means deviating from the surrounding module, do it and say
  so in one line. Improvements are *proposed*, never bundled into a feature change.

Taager-only content (observed-drift catalogue, `...ViewPolicy` / `...Authorities`
auth model, sharedkernel-Feign centralization, internal blog citation) is
preserved as a project-local skill in `allocation-service/.claude/skills/`, not
shipped in this public repo.

## Decisions

- **Core is layering, not CQRS** — four topologies observed in production; the split is the exception, not the frame.
- **Progressive disclosure over one big file** — the split canon and the Kotlin/Spring mechanics are each irrelevant to most invocations; keeping them out of SKILL.md keeps the always-loaded cost low.
- **Respecting the repo outranks the canon, but only for variations** — the skill classifies every difference as variation / defect / typo and acts differently on each, so "follow the repo" never degrades into propagating broken layering.
- **Frequency, not first sighting, defines the pattern** — the detection step reads several sibling modules; a one-off is an accident, a service-wide deviation is that service's standard.
- **Improvements are proposed, not performed** — flagging a defect is in scope; refactoring it as a side effect of a feature is not.
- **Skill named `ddd`** — as requested; description carries the trigger surface so it fires on "where should this go", aggregate/use-case/repository naming, and layering questions without needing the word "DDD".
- **Taager specifics → `allocation-service/.claude/skills/`** (user decision) — keeps the drift catalogue usable at work, out of a public repo. Not committed to the Taager repo unless asked.
- **No installer changes** — `src_for`/`target_file` already map `skills/**` to `$skill_root/**` and `mkdir -p` the nesting, so `skills/ddd/references/*.md` install as-is. Only MANIFEST entries are needed.
- **Back up before deleting** `~/.claude/skills/taager-backend-architecture/` — it is git-untracked and that path is its only copy.
- **Manual removal, not an installer prune** — the old skill was never installer-managed, so it isn't in the registry that `do_uninstall` walks; a phantom MANIFEST entry would not clean it.
- **VERSION 0.4.0 → 0.5.0** — new shipped files, additive.

## Rejected alternatives

- *Keep `taager-backend-architecture` and add a sibling `ddd` skill* — two overlapping skills competing for the same triggers; the Taager one would keep winning and keep giving CQRS-only advice.
- *Genericize in place (edit the existing skill, same name)* — leaves internal conventions in the public repo and keeps a name that only fires for one employer's code.
- *One flat generic SKILL.md, no references* — 277+ lines loaded on every backend prompt, and the Kotlin/Spring half is dead weight for non-JVM work.
- *Ship `references/taager.md` in this repo* — rejected by the user; public repo.

## Milestones

1. Write `skills/ddd/SKILL.md` + the two references.
2. Register: MANIFEST entries, VERSION bump, README skill table + counts.
3. Land the Taager overlay in `allocation-service/.claude/skills/`.
4. Back up and remove `~/.claude/skills/taager-backend-architecture/`.
5. Verify: fake-HOME install/update/uninstall places and prunes all three new files.

## Risks

- **Trigger over-reach** — a skill called `ddd` can fire on any backend prompt. Mitigate with a description scoped to code-organization/layering/naming questions, not "backend work" generally.
- **Reference files never get read** — progressive disclosure fails if SKILL.md doesn't say to load them. Mitigate with an explicit, unmissable "if the context splits, read `references/cqrs.md` first" instruction.
- **Copy drift across Taager repos** — the overlay lands in allocation-service only; other repos keep no copy until someone copies it. Called out as an optional follow-up rather than done silently for 14 repos.
- **"Respect the repo" collapsing into "copy the repo"** — the likeliest failure of the conform-vs-improve section is the model treating every deviation as a variation and cementing drift. Mitigate by listing the invariants that can *never* be overridden by local precedent, explicitly, next to the classifier.
- **Unsolicited refactors** — the opposite failure: the model "improves" surrounding code during a feature change. Mitigate with the propose-don't-perform rule stated in both the classifier and the review checklist.
- **`.awesome-agent/` mirror is already stale** (missing `pr-description`) — refreshing it is in scope but is install output, not source.
