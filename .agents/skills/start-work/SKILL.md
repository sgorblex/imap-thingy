---
name: start-work
description: Use at the very start of a new task in this repository — before the first edit — to land in the right checkout on a correctly named Graphite branch. Covers choosing between the shared main checkout and a worktree, why `gt create` cannot open the first branch in a fresh agent worktree, the `git switch -c` + `gt track` pair that can, disposing of the scratch branch, and how much of a stack to name up front.
---

# Start work (branch and checkout setup)

Run this **before the first edit**, not after. Getting the branch right afterwards means rewriting history you have already built on.

## 1. Where am I

```bash
pwd                    # under .claude/worktrees/ ?
git branch --show-current
```

- **Inside `.claude/worktrees/<something>`** — the harness placed you there; that worktree is yours. Do **not** `git worktree remove` it when you finish, and do not `cd` out to the main checkout.
- **In the shared main checkout** — feature-sized work belongs in its own worktree, but creating one is the user's call: **ask** before `git worktree add .claude/worktrees/<short_name>`. A small self-contained edit can stay where it is.

## 2. Pick the parent

```bash
gt log short
```

Read it before creating anything, so the new branch stacks where you intend and you do not orphan, clobber, or silently restack someone else's branches. The parent is `main` for independent work, or the tip of the stack this builds on.

## 3. Open the branch

In the main checkout, `gt create <type>/<short_name> -m "<type>: …"` is all it takes. In a fresh agent worktree the harness-generated **`worktree-…`** branch is **untracked by Graphite**, and `gt` refuses every operation on it (`Cannot perform this operation on untracked branch`), so open the first branch with git:

```bash
git switch -c <type>/<short_name>
gt track --parent main            # or the branch you are stacking on
```

From there `gt create` works normally for every branch above it. The same pair also rescues work already committed onto the scratch branch.

Naming rules: [`AGENTS.md`](../../../AGENTS.md) — *Git / Graphite*.

## 4. Dispose of the scratch branch

```bash
git branch -d worktree-…
```

Self-guarding: it refuses while the branch still holds commits of its own. If it refuses, look — something is on it that you moved away from.

## 5. Name the stack you can see

If the work has an agreed plan, create the branches it calls for now, so each opens with its purpose decided. **Adding branches later, as the work reveals them, is expected**; the shape is judged at review time — see [`review-stack`](../review-stack/SKILL.md) — *Granularity*.

## Never

**No `git push`, `gt submit`, `gt push`, `gh pr create`, merge, or PR comment** unless the user explicitly asks in that same turn.
