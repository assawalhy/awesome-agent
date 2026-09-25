---
name: pr-description
description: Generate a pull request description for the current branch's changes, output as copy-paste-ready markdown. Use this whenever the user asks to "write a PR description", "describe these changes for a PR", "summarize this branch", "PR summary/writeup", or wants text to paste into a pull request — even if they don't say the literal words "PR description". Writes short, factual bullets with light code references, plus show-me style visuals (flows, diffs, tables, mermaid).
---

# PR Description

Delegate to a fast low-cost agent like sonnet or deepseek v4 flash or similar to get the result.
Check the draft against the diff before handing it over, and remove any attribution line
the agent adds.

Output raw markdown to copy in a fenced block. Use a four-backtick outer fence so that inner
code fences do not end the block early.

## Source of truth

Read the branch diff first rather than the conversation — work a later commit reverted
never happened. For a stacked change, diff against the branch below it, not master, and
say what it sits on.

Don't mention the ticket number or the branch name, and don't include any "this PR" or
"these changes" phrasing.

## Headings name the change

Every heading states what changed or what was fixed, not a generic section label.

- Good: `## Shopify errors are reported instead of a decoding failure`
- Bad: `## Summary`, `## What changed`, `## Details`

Open with one sentence under the title line that says what the branch does overall.

## Prose: short factual bullets

Write in this style:

```
Added validation of incoming Shopify orders in the webhook controller.
Stopped retrying Shopify errors that cannot succeed on a retry.
Returned a specific error when the Shopify authorization code is expired or already used.
Redacted secrets from outgoing request logs.
```

- One fact per bullet. Past tense verb first: Added, Removed, Changed, Fixed, Moved, Renamed.
- Refer to parts of the system by names a reader recognises and remembers: a controller,
  a use case, an endpoint, an external API operation, an error code returned to clients.
  Prefer plain wording such as "the Shopify webhook controller" or "the push product use case".
- Do not explain the change through variable names, field names, method names, helper
  classes, exception classes, or config keys. Describe what the code does instead.
- Use inline code sparingly, only for a name the reader needs to find or recognise, such as
  an endpoint path or a client-facing error code. A handful in the whole description at most.
- Do not put logic or expressions in prose.
- When the reason is not obvious from the bullet, add one short sentence stating the cause
  or the effect. Do not tell a story.
- Plain, literal English: no metaphor, no idiom, no narrative voice, no filler words,
  no emojis.

## Visuals (show-me style)

Use visuals to make the change reviewable at a glance. Pick the ones that fit, keep each small:

- A before/after flow as ASCII or a `mermaid` block, when behaviour or a request path changed.
- A short `diff` block (up to about 10 lines) for the one or two lines that carry the fix.
- A table when comparing cases, for example two error types and where each is handled.

Label diagrams and tables with plain words or recognisable component names, not class,
method, or field names. A diff block is the only place for code; keep it to the lines that
carry the fix. No full payloads, no stack traces.

## Tests

A short bullet list of the scenarios the new tests cover. Name the test class once if useful.

## Length

Roughly 25–60 lines including visuals.
