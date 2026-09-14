---
name: pr-description
description: Generate a pull request description for the current branch's changes, output as copy-paste-ready markdown. Use this whenever the user asks to "write a PR description", "describe these changes for a PR", "summarize this branch", "PR summary/writeup", or wants text to paste into a pull request — even if they don't say the literal words "PR description". Writes in plain, literal technical English — no metaphor, no narrative voice.
---

# PR Description

Delegate to a fast low-cost agent like sonnet or deepseek v4 flash or similar to get the result.

Output raw markdown to copy in a fenced block.

Read the branch diff first rather than the conversation — work a later commit reverted
never happened. For a stacked change, diff against the branch below it, not master, and
say what it sits on.

Don't mention the ticket number or the branch name, and don't include any "this PR" or "these changes" phrasing. Just describe the code changes in a way that a reviewer can understand what was done and why.

-> So basically you will write in the format of the humanlayers/show-me skill.