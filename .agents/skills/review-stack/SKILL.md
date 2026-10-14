---
name: review-stack
description: Use before submitting a branch — or a whole Graphite stack — as PRs in this repository, or when asked to review the current branch's or stack's own changes for quality, architecture, naming, bugs, convention adherence, and scope, then apply the safe fixes. Covers per-branch diff scoping across a stack, parallel per-branch review, this repo's review dimensions and doc-update obligations, and the bottom-up mise verification sweep.
---

# Review and fix a branch or stack (pre-PR pass)

Self-review of **the branches' own changes**, run once implementation feels done and before any PR exists. Works on one branch or an N-branch **Graphite** stack. Report first, then fix what is safe to fix.

## 1. Pick the branches

```bash
gt log short -sr    # this stack, trunk-first (-s = ancestors+descendants of HEAD, -r = reversed)
gt log short -sr | sed -E 's/\([^)]*\)//g; s/[^A-Za-z0-9._\/-]+/ /g' | awk 'NF{print $NF}'   # names only
```

A `worktree-…` branch is untracked and `gt` errors on it — move the work onto a real branch first ([`start-work`](../start-work/SKILL.md)). Default target: every branch above `main`. If only part of the stack is this session's work, say which branches you are reviewing and confirm before sweeping the rest. A `(name)` annotation means the branch is checked out in **another worktree**: readable, not amendable.

## 2. Scope each branch

"The diff" is against the branch's **parent** (the previous entry in the trunk-first list), not `main`. No checkout needed:

```bash
git merge-base --is-ancestor "$PARENT" "$BRANCH"   # must pass; if not, wrong parent or the stack needs `gt restack`
git log --oneline "$PARENT..$BRANCH"
git diff --stat "$PARENT...$BRANCH"
git diff "$PARENT...$BRANCH"
```

The working tree sits at one branch: read other branches' files with `git show <branch>:<path>`, never from disk. Then read whatever the diff raises questions about — callers, an existing helper that makes new code redundant.

## 3. Review dimensions

Per branch:

- **Bugs and functionality** — does it do what the branch claims, including edge cases and IMAP error paths.
- **Criterion consistency** — a new or changed criterion's `imap_query` and predicate agree, and `is_efficient` is `True` only when the server query alone is exact ([`AGENTS.md`](../../../AGENTS.md) — *Architecture*).
- **Reuse and convention** — an existing criterion, action, combinator or helper already covers this.
- **Naming**, **readability**, **internal consistency**.
- **Restraint** — comments that restate the code (CI YAML especially), docs beyond what the change requires.
- **Tests** — new behaviour is covered with the `mock_account` pattern.
- **Doc obligations** — walk the *After you change the repository* table in [`AGENTS.md`](../../../AGENTS.md) row by row against the diff. It is the list; do not work from memory of it.
- **Branch ships as one unit** — if an earlier commit in this unmerged branch added something a later commit makes obsolete, fix it at the source with `gt modify`, never with a follow-up revert.
- **Branch name and commits** — `<type>/<short_name>`, snake_case, no scope segment; Conventional Commits; the type matches what the branch squashes to (it decides the release bump).
- **mise discipline** — new instructions and docs route through `mise run` / `mise exec`, never bare `uv` / `pytest` / `ruff` / `mypy`.

Across the stack (do this pass yourself, after the per-branch ones):

- **Granularity** — does the stack read as a sequence of changes each worth reviewing on its own? Where not, `gt fold` or `gt split --by-commit` / `--by-file <pathspec>`. Expect to fold more often than split.
- **Churn** — a later branch rewriting or deleting what an earlier one added. Fix at the source when both are unsubmitted; **flag instead** when the earlier branch already has an open PR.
- **Duplication** — the same helper or fixture invented in two branches.
- **Doc attribution** — the doc change lands in the branch that introduces the behaviour, not at the tip.

## 4. Parallelise the reads, serialise the writes

For a stack of three or more, dispatch **one read-only subagent per branch** in a single message: branch and parent refs, the per-branch list above, and the rule that it may only run `git diff` / `git log` / `git show` and read files — never check out, edit, or run `gt`. Do the cross-branch pass yourself. Fixes and verification stay serial: there is one working tree.

## 5. Report, then triage

Report **before** touching anything: findings grouped by branch, then cross-branch, each as `file:line` plus one line of why, by severity. Say so explicitly if there is nothing to raise. Then:

- **Easy, clearly an improvement, in scope for the owning branch** → apply it.
- **Restructuring the stack** (fold, split) → propose it, never apply it silently.
- **Needs a design decision** → stop and ask.
- **Out of scope for the stack's topic** → do not propose it.

## 6. Apply the fixes

Bottom-up, one branch at a time:

```bash
gt checkout <branch>
# apply that branch's fixes
git status --short     # nothing unrelated about to be staged
gt modify --all        # amends the branch commit; auto-restacks descendants
```

If the tree held unrelated changes, `git add` only the reviewed paths and run `gt modify` without `--all`. Never `git stash` — the stash is shared with every worktree; use a WIP commit. Finish with `gt log short -sr` to confirm nothing needs a restack.

## 7. Verify the sweep

Bottom-up, on each branch: `mise run fix`, `mise run check`, `mise run test`; add `mise run build` where `pyproject.toml` or packaging changed. Report a branch as verified only once its checks have **actually run**, and say plainly which did not.

## Never

**No `git push`, `gt submit`, `gt push`, `gh pr create`, merge, or PR comment** — this skill stops one step short of the PR, unless the user explicitly asks in that same turn. When they do, follow *Submitting* in [`AGENTS.md`](../../../AGENTS.md) — *Git / Graphite*.
