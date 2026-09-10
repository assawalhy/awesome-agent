---
name: pr-description
description: Generate a concise pull request description for the current branch's changes, output as copy-paste-ready markdown. Use this whenever the user asks to "write a PR description", "describe these changes for a PR", "summarize this branch", "PR summary/writeup", or wants text to paste into a pull request — even if they don't say the literal words "PR description". Defaults to a plain-language, product-oriented recap, but switches to a technical, symbol-referencing style for internal/infra changes or when the user asks for "technical". Always writes in plain, literal technical English — no metaphor, no narrative voice.
---

# PR Description

Write a pull request description that gets a reviewer oriented fast. Two styles are available — pick based on the change and any explicit request (see "Choosing a style" below). Either way: describe what actually changed and why, and keep it short.

## Gather the facts first

Never write from memory of the conversation alone — inspect the actual branch state so the description matches what's really committed:

```bash
# base branch is usually master/main — confirm it
git diff <base>...HEAD --stat        # files touched + churn
git log <base>..HEAD --oneline       # commits on the branch
git diff <base>...HEAD               # the actual changes (skim for intent, don't quote from it)
```

Also check any project convention for PR text (a `.github/PULL_REQUEST_TEMPLATE.md` — if one exists, follow its section structure instead of the default below).

A ticket reference in the branch name, commit messages, or changelog fragments tells you the scope of the change — read it, but see "Referencing tickets and other PRs" below before putting it in the text.

When the change sits on top of another unmerged branch, get the number of that branch's pull request so you can reference it:

```bash
git remote -v                                # gitlab or github — decides the reference syntax
gh pr list --head <base-branch>              # github
glab mr list --source-branch <base-branch>   # gitlab
```

If decisions were discussed earlier in the conversation (e.g. "we chose to reject with a reason instead of silently failing because…"), fold that reasoning in — what the decision means for the feature/system, not just a restatement of the code path.

**Only describe what's in the net diff against the base branch.** The branch's commit history may contain work that was later reverted or replaced (a table added in one commit and dropped in a later one, an approach tried and then abandoned) — if it nets to no change against `<base>...HEAD`, it never happened as far as a reviewer is concerned. Leave it out entirely; mentioning it is pure noise and invites questions about something that isn't there. Use `git diff <base>...HEAD --stat` (not the commit list) as the source of truth for what to describe.

## Output format

Deliver the description as **copy-paste-ready markdown inside a single fenced block** so the user can lift it straight into the PR:

`````
<the PR description goes here>
`````

The outer fence must be longer than any fence inside it. Technical-style descriptions normally contain ```-fenced diagrams and payload blocks, so open and close the wrapper with **six** backticks in that case — a `````-fenced wrapper terminates early against them and the block renders broken.

After the block, add one short line offering to open the PR (`gh pr create`) or save it to a file — don't do either unless asked.

## Choosing a style

- **Product style** (default) — the change is user-facing or business-facing: a new feature, a behavior change a PM/support/merchant would care about. Reviewer here includes non-engineers skimming the PR list.
- **Technical style** — the change is internal/infra: consumers, event schemas, refactors, data-layer changes, enum/type additions, anything where the audience is engineers reviewing a diff and the "why" only makes sense with real symbol names attached. Also use this whenever the user explicitly asks for something "technical" or names specific classes/behavior they want called out.
- If genuinely unsure which fits, default to technical for backend/infra-only branches and product for anything touching user-visible behavior. Don't ask unless the branch is a real mix of both — in that case a short product-style summary followed by a technical paragraph works.

## Writing style — both styles

Write plain, literal technical English. The Chicago Manual of Style covers mechanics, the Microsoft Manual of Style covers software voice, and ASD-STE100 (Simplified Technical English) supplies the sentence-level discipline. Take ASD-STE100's **rules**, not its dictionary — its approved word list is scoped to aerospace maintenance and rejects ordinary engineering words like *publish*, *consumer*, and *singleton*.

The rules that carry the most weight here:

- **One topic per sentence**, under about 25 words. Split a long sentence rather than bolting on another clause.
- **Active voice, present tense.** "`cancelAfterSalesRequest` publishes the event", not "the event will be published".
- **No figurative language.** No metaphor, personification, understatement, or rhetorical build-up. A method does not *announce*, *tell nobody*, *know about*, *hear about*, or *care*. It publishes, raises, sends, returns, or throws. This is the single easiest way to make a description worse, and the one to guard hardest against.
- **State the fact, not your assessment of it.** Cut "the interesting part is", "worth pausing on", "surprisingly", "elegantly", "the beauty here". Say what the thing is and why it matters; the reader decides whether it is interesting.
- **One term per concept, every time.** Do not alternate between "reason", "failure reason", and "cause" for the same field.
- **Serial comma. Closed-up em dashes** (CMOS). Spell out one through nine, use numerals for 10 and above (Microsoft).
- **No Latin abbreviations** — "for example", not "e.g."; "that is", not "i.e."

Same facts, both voices:

| Don't | Do |
| --- | --- |
| Cancelling a request used to be the one terminal transition that told nobody. | `Order.cancelAfterSalesRequest` reversed cash and profit but published no event. |
| The interesting part is how little this needed. | `raiseRequestFailedEvent` already exists, so this adds no event class and no producer. |
| Those two renames are the part worth pausing on. | **Breaking change.** Two `failureReason` values change on a live topic. |
| Consumers never heard about it, so balances went stale. | Consumers of `after-sales.failed` did not learn that the request ended, so a derived balance became incorrect. |

## Structure — product style

No title/header line (no `TICKET-ID — summary` line) and no forced section headers (no "What" / "Why" / "Things to know" labels splitting the content). Write **1-3 short paragraphs, or a flat list of bullets** — whichever reads better for the change — plain-language and product-oriented throughout.

- What this PR does from a feature/behavior standpoint (e.g. "admins can now approve or reject a withdrawal request"). Skip class names, method names, and code snippets entirely.
- The reasoning behind the feature or any non-obvious behavior choice, explained in terms of what it means for users or the business, not how it's implemented (e.g. "rejections require a reason so support can explain the decision to the merchant" rather than naming the field that stores it).
- Scope cuts, follow-ups deferred, or behavior edge cases worth flagging, kept at the same plain-language level — only if there's something real to say.

**Principles:** product-oriented, not technical (no function/class/file names or code); a few short sentences or bullets total; lead with why; don't pad with boilerplate; don't label the bullets/paragraphs by category.

**Example (abridged)** — admin approve/reject on withdrawals:

- Admins can now approve or reject a merchant's withdrawal request from the admin panel, instead of it being auto-approved.
- Rejections require a reason so the merchant gets a clear explanation, and a rejected withdrawal automatically returns the funds to the merchant's wallet.
- Only pending withdrawals can be approved or rejected — once a decision is made it can't be changed.

## Structure — technical style

Reference real class/enum/field/topic names when they help a reviewer orient (this is the point of this style — unlike product style, don't paraphrase them away). Order roughly from "what changed" to "why non-obvious choices were made" to "what to watch for while reviewing."

That order is a default, not a template. Let the change decide the shape: some PRs need a diagram, a table, and three labelled sections; others are four plain paragraphs with no headings at all. Do not manufacture a **Before**/**After** pair, a payload block, or a "Notes for review" heading when the change does not have one. Structure that the content did not ask for reads as filler.

**Prefer showing over describing.** Reviewers skim. A sentence explaining a shape is almost always worse than the shape itself, so reach for a scannable device whenever one fits, and keep prose for the reasoning that can't be tabulated:

- **Text diagram** for flows, before/after, or dispatch — cheaper to read than a paragraph tracing the same path:
  ```
  Order.failAfterSalesRequest ──> AfterSalesRequestFailedEvent ──> after-sales.failed  (new)
          ▲
          └── single choke point for all 5 failure paths, so no handler needed touching
  ```
- **Before/after pair** whenever the change is "X used to happen, now Y does" — two labelled 2-3 line blocks beat a paragraph of contrast.
- **Fenced code block** for a payload, schema, DTO, config key, or new enum. Show the actual field list; don't describe it in sentences.
- **Table** for any mapping with more than two rows — status → reason, input → output, flag → behavior.
- **Short bolded labels** (`**Payload**`, `**Breaking change.**`, `**Before deploy**`) where a section genuinely starts. Unlike product style, structural labels are welcome here — they make a dense change skimmable. Earn each one; a description that reads well as plain paragraphs needs none.
- **A marker** on the one or two things a reviewer or consumer could actually get wrong. An emoji (⚠️, 🔴), a bolded `**Breaking change.**`, or nothing at all — pick what suits the change and stay consistent within the description. At most one or two per PR: if everything is flagged, nothing is.

**Principles:**
- One idea per bullet/paragraph: the change and its reasoning together, not split into a "what" list and a separate "why" list.
- Name the actual symbols (class, enum value, topic, config key) when doing so is what makes the reasoning legible — e.g. "added `OperationType.X` instead of reusing `Y` because…" is the point, not something to avoid.
- Still concise — a sentence or two per bullet, not a code walkthrough. Let the diff carry line-level detail; this carries intent and decisions. A diagram or table replaces prose, it doesn't get added on top of it.
- Only mention things that exist in the final diff (see "Gather the facts" above) — don't narrate the implementation's history.
- Close with a deploy/rollout note only when there's a real prerequisite (topic must exist, migration must run, flag must be flipped).
- No test/verification commentary, no "This PR aims to leverage…" boilerplate.

**Example (abridged)** — publishing after-sales failures to a new topic. Note how the flow, the payload, and the status→reason mapping are all *shown*; prose is reserved for the decisions a diagram can't carry:

---

After-sales published successes only. A consumer of `after-sales.succeeded` could not learn that the request later failed. This change adds the matching failure topic.

**Before**
```
after-sales request succeeds ──> after-sales.succeeded
after-sales request fails    ──> (nothing)
```

**After**
```
Order.successAfterSalesRequest ──> AfterSalesRequestSucceededEvent ──> after-sales.succeeded
Order.failAfterSalesRequest    ──> AfterSalesRequestFailedEvent    ──> after-sales.failed  (new)
```

**Payload** (`after-sales.failed`, namespace `order-management`)
```ts
{
  orderBusinessId: string;
  afterSalesId: number;
  requestType: string;        // refund | replacement | addition | compensation
  changeInMerchantProfit: number;
  failureReason: string;      // new — see table
}
```

**The 5 failure paths and their reason**

| shipment status | `failureReason` |
| --- | --- |
| `returned` | `shipment_returned` |
| `warehouse_cancelled` | `shipment_warehouse_canceled` |
| `return_in_progress` *(additions only)* | `shipment_return_in_progress` |

**Notes for review**

- New `AfterSalesFailureReason` enum instead of reusing `OrderEventType`. Only five of that enum's 24 values are reachable here, so the narrower type turns an invalid reason into a compile error. The wire strings do not change, so the payload contract is unaffected.
- The guard is per-transition, not per-request. This is intentional: a request can move `SUCCEEDED → FAILED` and back, and both events in order let a consumer reverse an earlier success.
- ⚠️ The event is a notification, not a ledger entry. The balance stays derived from the order document on each recalculation, so a consumer that treats accumulated `changeInMerchantProfit` as authoritative drifts from the aggregation.

**Before deploy:** confirm `after-sales.failed` exists on the cluster, or that auto-topic-creation is on for `taager/order-management`.

---

## Both styles

### Notes for review

End the description with a short list of **two or three notes** — the things a reviewer or whoever deploys the change could get wrong, and nothing else. Write them so a reader can act on each one without opening the diff: state the risk or the decision, then what it means for them.

Keep the list to three items. A note that only restates a line of the diff is not a note. Mark at most one item, and only when getting it wrong breaks something.

Good notes name a real consequence:

- Keep the feature flag off until the deduction branch merges. Nothing decrements the stored quantity yet, so every run would allocate the same stock again.
- The refresh job must not read through the allocation gateway. A same-day re-run would otherwise refresh the snapshot from itself.

### Referencing tickets and other PRs

**Do not write the Jira ticket key in the description** (`ENG-1234`, `PROJ-99`). Automation reacts to the key and moves the ticket to "code review", which is wrong for a ticket that has already moved past that — for example one deployed to dev. Name the ticket in the PR title or the branch name, where the automation expects it, and keep the body free of it.

Reference other pull requests by their number in the target platform's own syntax, so the link resolves and no ticket automation fires:

| Platform | Syntax | Example |
| --- | --- | --- |
| GitLab | `!<number>` | Stacked on !412. |
| GitHub | `#<number>` | Stacked on #412. |

Check the remote to pick the syntax; do not guess from habit. For a stacked change, say what it is stacked on in one line at the top, and describe only the diff against that branch.

Do not include a testing/local-verification section, and don't mention how tests were run locally or any environment quirks — that's not part of this description.
