# IMAP Thingy
An IMAP scripting library, primarily to make email filters.

Ever complained about receiving the same emails on multiple inboxes? Or wanted to auto-archive receipts that you've already opened? Or wanted your emails to get sorted automatically in some other way?

Well, complain no more!
(or at least not for this reason)

IMAP Thingy is a library that lets its users create advanced IMAP filters. Possibly on multiple emails, possibly even on multiple accounts.


## Installation
```
pip install imap-thingy
```
or, for the unreleased state of `main`:
```
pip install git+https://github.com/sgorblex/imap-thingy.git
```


## Usage and examples
Here is a simple example which loads credentials from an accounts.json file that looks something like this:
```
[
  {
    "name": "beautiful gmail account",
    "type": "gmail",
    "username": "myaddress@gmail.com",
    "password": "ana ppp asw ord"
  },
  {
    "name": "beautiful custom account",
    "host": "mydomain.com",
    "port": 993,
    "username": "its.a.me@mydomain.com",
    "password": "my_super_secret_pw"
  }
]
```
At the moment we do not support OAUTH (PRs welcome :), so if you're using something like GMail you will have to generate an [app-password](https://support.google.com/accounts/answer/185833?hl=en).

As for the main script, which simply applies some filters (probably the most useful):
```python
# my_beautiful_script.py

from imap_thingy.accounts import Path, accounts_from_json
from imap_thingy.filters import Filter, If, FromIs, SubjectMatches, ToIs, MoveTo, MarkAsRead

from dmarc import dmarc_pairs

import argparse

def main():
    parser = argparse.ArgumentParser(description="imap_filters: my personal IMAP filters")
    parser.add_argument("--dry-run", action="store_true", help="Print actions instead of executing them")
    args = parser.parse_args()

    accounts = accounts_from_json("accounts.json")
    gmail = accounts["beautiful gmail account"]
    custom = accounts["beautiful custom account"]

    pairs = [
        # In account "beautiful gmail account", move all mail directed to "members@boringassociation.org" to "Boring Association" folder (marking as read first)
        (gmail / "INBOX", Filter(ToIs("members@boringassociation.org"), MarkAsRead() + MoveTo(Path("Boring Association")))),
        # In account "beautiful custom account", move all mail from "googledev-noreply@google.com" to "Dev Stuff.Google Developer Program" folder. Note that folder delimiter may differ between servers
        (custom / "INBOX", Filter(FromIs("googledev-noreply@google.com"), MarkAsRead() + MoveTo(Path("Dev Stuff.Google Developer Program")))),
        # A filter based on a complex criterion and a series of actions
        (gmail / "INBOX", If(FromIs("list4nerds@nerduniversity.edu") & SubjectMatches(r"List Digest, Vol \d+")).then(MarkAsRead() + MoveTo(Path("List For Nerds")))),
    ]
    pairs.extend(dmarc_pairs(custom, "dmarcreport@microsoft.com", "Postmaster.DMARC Reports"))

    for folder, f in pairs:
        folder.run(f, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
```
The important parts are `accounts_from_json`, `pairs` (folder + filter), and looping over pairs and calling `folder.run(f, ...)`. Folders are obtained from an account (e.g. `account / "INBOX"`, `account.inbox`). For type hints or direct use, import `Folder` from `imap_thingy.accounts`. `Account(..., ssl_context=ctx)` connects with your own `ssl.SSLContext` (e.g. one trusting a private CA), `Account(..., timeout=30)` (or `"timeout": 30` in `accounts.json`) bounds the connection and each socket read or write to that many seconds instead of waiting forever, and `account.list_folders()` returns the `Path` of every folder that can hold mail. Criteria that can be expressed purely in IMAP (e.g. `FromIs`, `SubjectContains`, `BodyContains`) use server-side search only; criteria that need body parsing (e.g. `SubjectMatches` with regex, or `BodyMatches` which searches decoded plain/HTML body text with `re.search`) use a per-run fetch cache to minimize redundant fetches within a `run()`, but messages that have had actions applied may be evicted from the cache and fetched again if they are re-selected later in the same `run()`.

**Note:** The library no longer configures logging automatically. The previously documented `imap_thingy.logging.setup_logging()` helper is kept only as a deprecated compatibility shim and should not be used in new code. Instead, configure logging explicitly in your application near the entry point (for example with `logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")`) so that loggers under `imap_thingy` emit to your handlers.

Arbitrarily complex filters can be implemented in Python, likely via `imapclient` and/or `mailparser`, if not directly via our bindings. For example, here is a custom helper that returns (folder, filter) pairs to automatically move DMARC reports, while first trashing the previews:
```python
# dmarc.py

from imap_thingy.accounts import Account, Path
from imap_thingy.filters import If, FromIs, SubjectMatches, MoveTo, Trash

def dmarc_pairs(account: Account, sender: str, folder: str, delete_preview: bool = True, base_folder: str = "INBOX"):
    f = account / base_folder
    pairs = []
    if delete_preview:
        pairs.append((f, If(FromIs(sender) & SubjectMatches("[Preview] .*")).then(Trash())))
    pairs.append((f, If(FromIs(sender)).then(MoveTo(Path(folder)))))
    return pairs
```

### Running rules
`imap_thingy.runner` runs filters grouped by folder (`Rules`, a list of `(folder, [filters])`), either once or continuously through IMAP IDLE:
```python
from imap_thingy.runner import monitor, run_rules, starred_only

rules = [(gmail / "INBOX", [f1, f2]), (custom / "INBOX", [f3])]
run_rules(rules, dry_run=False)                 # one folder after the other
run_rules(rules, dry_run=False, parallel=True)  # one thread per folder; failures raised together at the end
monitor(rules, dry_run=False)                   # run each folder's filters on new mail, until SIGTERM/SIGINT
```
`monitor` installs SIGTERM/SIGINT handlers, so call it from the main thread; to run it in another thread (e.g. inside a worker), pass `install_signal_handlers=False` and a `threading.Event` to stop it: `monitor(rules, dry_run=False, stop=stop, install_signal_handlers=False)` returns about a second after `stop.set()`, once any filters already running finish. Handlers it installs are restored on return. `starred_only(rules)` restricts every filter to starred messages and unstars them before the action, so you can sort mail by starring it.

`folder.run(...)` and `run_rules(...)` return reports (`imap_thingy.report`), plain JSON-compatible dicts: per folder its `account`, `folder` (path segments), `dry_run` and `error` and, per filter, its `spec` (`null` for filters with no data form), `action`, the `matched` messages (`uid`, `from`, `subject`, `date` in UTC) and whether the action was `executed`. A dry run selects the folder read-only and executes nothing:
```python
report = (gmail / "INBOX").run([f1, f2], dry_run=True)
for f in report["filters"]:
    print(f["spec"], [m["subject"] for m in f["matched"]])
```
With `parallel=True`, a failure raises `RunRulesError` (a `RuntimeError`) once every folder has run; its `reports` hold every folder's report, the failed ones with `error` set and the filters that finished before it.

### Rules as data
Filters built from the library's criteria and actions can be turned into JSON-compatible data and back, e.g. to keep rules in a file or edit them from another program:
```python
import json
from imap_thingy.spec import load_filter

f = If(FromIs("list4nerds@nerduniversity.edu") & ~IsRead()).then(MarkAsRead() + MoveTo(Path(["Lists", "Nerds"])))
data = json.dumps(f.to_spec())
assert load_filter(json.loads(data)) == f
```
```json
{
  "criterion": {"and": [{"type": "from_is", "args": {"addr": "list4nerds@nerduniversity.edu"}}, {"not": {"type": "is_read"}}]},
  "action": {"seq": [{"type": "mark_as_read"}, {"type": "move_to", "args": {"folder": ["Lists", "Nerds"]}}]}
}
```
A leaf is `{"type": ..., "args": {...}}`: the class name in `snake_case` and its constructor arguments by name. Folder paths are lists of segments, flags are `Flag` names (`"SEEN"`), dates are ISO 8601. `OlderThan(date)` takes a fixed date; `OlderThanDays(n)` (`{"type": "older_than_days", "args": {"days": 30}}`) counts back from the day the rule runs. `&`, `|`, `~` become `and`, `or`, `not`, and `+` becomes `seq`. `load_criterion` and `load_action` load the parts, and `imap_thingy.spec.json_schema()` returns the JSON Schema of the format (shipped as `imap_thingy/spec/schema.json`). Criteria and actions built from your own functions have no data form: `to_spec()` raises `NotSerializableError`. Equality and `repr()` follow the data form, so `FromIs("a") == FromIs("a")`.

## Development
Tooling is pinned with [mise](https://mise.jdx.dev/); run everything through `mise run <task>`:

| Task | What it does |
| --- | --- |
| `setup` | Install Python dependencies into `.venv` |
| `fix` | Ruff auto-fix and format, then mypy |
| `check` | Ruff lint and format check, then mypy |
| `test` | Run the test suite; extra args go to pytest (`mise run test -- tests/test_criteria.py`) |
| `build` | Build sdist and wheel |
| `clean` / `clean-all` | Remove caches and build outputs (`clean-all` also removes `.venv`) |

Releases and `CHANGELOG.md` are automated by Release Please from Conventional Commit squash titles; dependency updates come from Renovate.


## Contributing
Feel free to raise issues or open pull requests! Branch, commit and PR conventions are in [`AGENTS.md`](https://github.com/sgorblex/imap-thingy/blob/main/AGENTS.md).


## License
[GPL v.3](https://www.gnu.org/licenses/gpl-3.0.en.html) or later
