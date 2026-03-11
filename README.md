# IMAP Thingy
An IMAP scripting library, primarily to make email filters.

Ever complained about receiving the same emails on multiple inboxes? Or wanted to auto-archive receipts that you've already opened? Or wanted your emails to get sorted automatically in some other way?

Well, complain no more!
(or at least not for this reason)

IMAP Thingy is a library that lets its users create advanced IMAP filters. Possibly on multiple emails, possibly even on multiple accounts.


## Installation
The quickest way is probably
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
The important parts are `accounts_from_json`, `pairs` (folder + filter), and looping over pairs and calling `folder.run(f, ...)`. Folders are obtained from an account (e.g. `account / "INBOX"`, `account.inbox`). For type hints or direct use, import `Folder` from `imap_thingy.accounts`. Criteria that can be expressed purely in IMAP (e.g. `FromIs`, `SubjectContains`) use server-side search only; criteria that need body parsing (e.g. `SubjectMatches` with regex) use a per-run fetch cache to minimize redundant fetches within a `run()`, but messages that have had actions applied may be evicted from the cache and fetched again if they are re-selected later in the same `run()`.

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

## Contributing
Feel free to raise issues or open pull requests!


## License
[GPL v.3](https://www.gnu.org/licenses/gpl-3.0.en.html)
