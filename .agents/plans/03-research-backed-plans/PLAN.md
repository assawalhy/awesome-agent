# Research-backed plans: resolve every decision BEFORE the approval gate

## Goal
The agent must never defer a plan decision to execution (e.g. "we'll pick the best option
during implementation"). Every non-obvious decision in PLAN.md must already be researched
(code, docs, web) and made, with alternatives considered and named, before the user is asked
to approve. The user reviews a decided plan, not a promise to plan later.

## Approach
- `skills/awesome-plan/SKILL.md`: add a **step 1.5 "Research before Decisions"** — before
  writing PLAN.md, research every open question (repo, docs, web search); each Approach/
  Decisions entry must cite its rationale/source; any item not yet decidable gets its own
  research TODO at the top of TODO.md, and the approval ask must say so explicitly instead
  of hiding it as "spike/decide later" wording.
- `agents/awesome-agent.md`: strengthen rule 2 into an explicit anti-deferral rule —
  "decisions presented for approval must already be made; alternatives considered and
  rejected options are named in PLAN.md; 'spike/decide during execution' phrasing is not
  allowed for anything the user is being asked to approve".
- No harness overlay changes needed (skill + agent are shared base files).

## Decisions
- Rule goes in BOTH files: the skill is the workflow (where the step belongs), the agent
  file is the behavior contract (where the anti-laziness rule belongs) — mirrors how rules
  1/2 are already split across the two files.
- Documentation-only change; no install.sh / MANIFEST.txt edits (both files are already
  tracked shared-base paths).

## Milestones
- M1: awesome-plan skill gains the research step + decision rules.
- M2: awesome-agent rule 2 gains the anti-deferral wording.

## Risks
- Over-researching trivial tasks → the step only applies to non-obvious decisions;
  the fast path (step 0) still skips planning entirely.
