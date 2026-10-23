# Agent notes — imap-thingy

The shared guide for AI-assisted work in this repository. **`CLAUDE.md`** redirects here; change policy here only.

## Project

`imap-thingy` is a Python (>=3.14) library for scripting IMAP email filters across one or more accounts. It is a library, not an app: there is no entry point — users write their own scripts (see `README.md`) that build `(folder, filter)` pairs and call `folder.run(filter, dry_run=...)`. Built on `imapclient` (protocol) and `mail-parser` (message parsing).

## Architecture

**Accounts and folders** (`accounts/`): `Account` holds credentials and the server's folder `delimiter` (`.` by default, `/` for `GMailAccount`). `account / "INBOX"` yields a `Folder` (account + `core.Path`). `Path` is delimiter-agnostic segments; it is only rendered to a string with the account's delimiter at run time, which is why actions like `MoveTo(Path(...))` receive `delimiter=` in `execute()`. An optional `ssl_context` and socket `timeout` go to `IMAPClient`; `list_folders()` returns selectable folders as `Path`s, split on the account's `delimiter` so they round-trip through `account / path` (a different server delimiter is logged). `accounts_from_json` builds accounts from a JSON config.

**Filters** = `Criterion` + `Action` (`filters/filter.py`), built either as `Filter(crit, action)` or `If(crit).then(action)`.

- **Criterion** (`filters/criteria/criterion.py`) has two halves that must agree: an `imap_query` (`core.IMAPQuery`, server-side SEARCH) and a Python predicate `func(Message) -> bool` (client-side). `is_efficient=True` means the IMAP query alone is exact and no fetch is needed. If the IMAP query is only a prefilter (e.g. `SubjectIs` uses `SUBJECT`, which is substring-match on the server; regex criteria use `ALL` or a looser query), set `is_efficient=False` so the predicate is applied after fetching. `&`, `|`, `~` combine both halves; the result is efficient only if all operands are. User regexes go through `core.pattern.Pattern`: compiled at construction (`ValueError`, hence `SpecError` on load) and matched with the `regex` package under the process-wide match timeout (`MatchTimeoutError`), never with `re`.
- **Action** (`filters/actions/action.py`) wraps `func(conn, msgids, *, delimiter)`; `+` / `.then()` chains actions.
- **Specs** (`core/spec.py`, `spec/`): a class declaring `spec_type` records its constructor arguments as a data node (`to_spec()`, loaded by `imap_thingy.spec`); non-JSON arguments need `spec_codecs`. `__eq__`, `__hash__` and `__repr__` derive from the spec. A new exported criterion or action needs a `spec_type`, an entry in `spec/schema.json`, and a case in `tests/test_spec.py` (its coverage test fails otherwise).

**Execution** (`Folder.run` / `_run_one` in `accounts/account.py`): one IMAP connection per `run()` call, shared by all filters passed to it, executed sequentially (earlier filters' actions affect later ones). Per filter: `search_mail` → if not efficient, fetch uncached ids into a per-run `fetched` cache and apply `criterion.select` → execute action (or log in dry-run). Messages acted on are evicted from the cache. Each filter's matches are summarised from one `ENVELOPE` fetch into the returned report (`report.py`, JSON-compatible `TypedDict`s); a dry run selects the folder read-only. `run_into` fills a caller's report as filters finish, so a partial report survives a failure.

**IMAP search encoding** (`get_mail.py`): `search_mail` bypasses `imapclient.search()` and sends a raw `SEARCH CHARSET UTF-8` with a custom `_normalise_search_criteria_utf8`, because upstream drops the charset on nested criteria and breaks non-ASCII values. `IMAPQuery.build()` produces lists for AND, `("OR", a, b)` / `("NOT", a)` tuples, and `(key, value)` pairs for base criteria; the normaliser flattens simple pairs and parenthesises OR/NOT groups. `IMAPQuery.Deferred` builds its query at search time, for criteria relative to the run (`OlderThanDays`). Changes to `IMAPQuery` structure must stay compatible with this normaliser (see `tests/test_imap_query.py`).

**IDLE** (`idle_monitor.py`): `IdleMonitor` watches a folder on a background thread with a read-only connection, calling an `IdleHandler` on each IDLE response, with exponential-backoff reconnect. `IdleFilterer` runs `folder.run(filters)` (on a separate connection) when an `IdleTrigger` (`on_new_mail`, `on_read`, `on_any_event`) fires. Monitors are one-shot. IDLE waits in `IDLE_POLL` slices so `stop()` only sets an event; the watcher thread itself ends IDLE and logs out, so no connection is shared between threads.

**Runner** (`runner.py`): `Rules` is a list of `(Folder, list[Filter])` groups. `run_rules` runs them sequentially, or with `parallel=True` one thread per folder, where every folder still runs and the failures are raised together as one `RunRulesError` (a `RuntimeError` carrying every folder's report). `monitor` starts an `IdleMonitor` per folder that runs its filters on new mail, until its `stop` event is set or (with `install_signal_handlers`, main thread only) SIGTERM/SIGINT. `starred_only` wraps rules to act only on starred messages, unstarring them first.

**Logging**: the library never configures logging; loggers are hierarchical under `imap_thingy` (account → folder children). `imap_thingy.logging.setup_logging()` is a deprecated shim.

**Tests** are pure unit tests with no real IMAP server: `conftest.py`'s `mock_account` fixture replaces `Account.connect` with a `MagicMock`, so tests assert on calls made to the mock connection.

## Git / Graphite

- Branches are managed with **Graphite** (`gt create` / `gt modify` / `gt restack` / `gt submit`), not raw `git branch` / `git commit --amend` / `gh pr create`. Check the current stack (`gt log short`) before adding branches, so new work stacks on the right parent.
- **Branch names**: `<type>/<short_name>` — one slash, `<type>` the Conventional Commit type the branch squashes to, `<short_name>` lowercase `snake_case`, two to four words, no scope segment (`feat/body_criteria`, `fix/idle_backoff`). Always pass the name to `gt create` (`gt create feat/x -m "feat: …"`); without one it slugifies the message.
- Reserved prefixes, never used for hand-made branches: `release-please--`, `renovate/`, `graphite-base/`, `worktree-`.
- **Conventional Commits** on every commit. PRs merge into `main` by **squash** — the squash title is the changelog entry Release Please reads, so it decides the version bump. Merging the Release Please PR tags the release and publishes it to PyPI (`.github/workflows/release-please.yml`, trusted publishing via the `pypi` environment). Put the **why** in the commit body: a later review reads the branch, not the conversation.
- **A branch ships as one unit.** If an earlier commit in an unmerged branch added something a later one makes obsolete, fix it at the source (`gt modify`) instead of adding a revert commit.
- A stacked PR that cannot pass until the branch below merges gets the `ci:pause` label: Woodpecker then starts no run, so the required check stays pending. Resuming needs the label removed *and* a new push.
- **Submitting** (only when asked, see below): `gt s -pns --ai` — submit the current branch and those below it, plus (`-s`) those above it; publish (not draft); no interactive editing; AI-written title and description. Then read every PR it created or updated and fix it with `gh pr edit`: the **title** becomes the squash commit and changelog entry, so its type must match the branch and it must name the user-visible change; the **description** must be accurate (generated text guesses — e.g. it may ask to verify something already verified) and say what the reviewer must know (manual steps, merge order).
- **Never run remote-mutating commands — `git push`, `gt submit`, `gt push`, `gh pr create`, merging, closing or commenting on a PR — unless the user explicitly asks in the current request.** Local commits, stack edits and read-only inspection need no asking.

**Worktrees**: feature-sized agent work goes in its own worktree under `.claude/worktrees/<short_name>` (gitignored); from the shared main checkout, **ask before creating one**. A harness-generated `worktree-…` branch is untracked scratch that `gt` refuses to operate on: open the real branch with `git switch -c <type>/<short_name>` then `gt track --parent <parent>`, and delete the scratch branch (`git branch -d worktree-…`; a `SessionEnd` hook in `.claude/settings.json` sweeps merged leftovers). Hand the worktree back in place, committed and clean, nothing submitted. Skills: `.agents/skills/start-work`, `.agents/skills/review-stack`.

## Shell commands (mise)

`mise.toml` pins Python and uv and creates `.venv`. Run tools through **`mise run <task>`** (list: `mise tasks`, or the task table in the README's *Development* section) or **`mise exec -- …`** for one-offs, e.g. a single test:

```bash
mise run test -- tests/test_criteria.py::TestCriteriaCombination::test_criteria_and_combination
```

Do **not** invoke `uv`, `pytest`, `ruff` or `mypy` directly without `mise run` / `mise exec`. CI is the exception: it calls `uv` directly, and its uv/Python pins are kept in step with `mise.toml` by Renovate groups.

## Local quality checks

After each implementation pass run `mise run fix`, which leaves `mise run check` clean; add `mise run test` before handing work over; `mise run build` once before a PR. CI (Woodpecker, `.woodpecker/checks.yaml`) runs format check, lint, mypy, tests and build on PRs and pushes to `main`; `main`'s ruleset requires it as `ci/woodpecker/pr/checks`, so never put a path filter on that pipeline's top-level `when`. GitHub Actions only hosts release automation (Release Please, PyPI publish) and PR assignment. Report work as done only once the relevant check has **actually run**, and say plainly which ones did not.

## After you change the repository

**Write as little as the rule needs** — no comments restating the code (CI YAML especially), no docs beyond what the change requires.

| You change… | Update… |
| --- | --- |
| Public criteria / actions | Package `__init__.py` exports and `filters/__init__.py` `__all__`; `README.md` if user-facing |
| mise tasks | `README.md` *Development* task table |
| CI, Release Please, Renovate | This file, where a rule changes |
| Versions or `CHANGELOG.md` | **Nothing by hand** — Release Please owns them (`release-please-config.json`) |
| A convention agreed with the user in conversation | This file or a skill — in the same change |
