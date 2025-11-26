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

from imap_thingy.filters.basic_filters import MoveIfToFilter, MoveIfFromFilter
from imap_thingy.filters.criterion_filter import CriterionFilter, from_is, move_to, subject_matches, mark_as_read
from imap_thingy.accounts import logout_all
from imap_thingy.filters import apply_filters
from imap_thingy.accounts import accounts_from_json

from dmarc import DmarcFilter

import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description="imap_filters: my personal IMAP filters")
    parser.add_argument("--dry-run", action="store_true", help="Print actions instead of executing them")
    parser.add_argument("--log", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log.upper(), None), format='%(asctime)s [%(levelname)s] %(message)s')

    accounts = accounts_from_json("accounts.json")
    gmail = accounts["beautiful gmail account"]
    custom = accounts["beautiful custom account"]

    filters = [
        # In account "beautiful gmail account", move all mail directed to "members@boringassociation.org" to "Boring Association" folder (marking as read first)
        MoveIfToFilter(gmail, "members@boringassociation.org", "Boring Association"),
        # In account "beautiful custom account", move all mail from "googledev-noreply@google.com" to "Dev Stuff.Google Developer Program" folder. Note that folder delimiter may differ between servers
        MoveIfFromFilter(custom, "googledev-noreply@google.com", "Dev Stuff.Google Developer Program"),
        # An instantiation of a more general filter based on a complex criterion and a series of actions
        CriterionFilter(gmail, from_is("list4nerds@nerduniversity.edu") & subject_matches(r"List Digest, Vol \d\+"), mark_as_read() & move_to("List For Nerds")),
        # Custom filter, see below
        DmarcFilter(custom, "dmarcreport@microsoft.com", "Postmaster.DMARC Reports"),
    ]

    apply_filters(filters, dry_run=args.dry_run)
    logout_all(accounts)


if __name__ == "__main__":
    main()
```
The important parts are `accounts_from_json`, `filters`, `apply_filters` and `logout_all`.

Arbitrarily complex filters can be implemented in Python, likely via `imapclient` and/or `mailparser`, if not directly via our bindings. For example, here is a custom filter that I wrote to automatically move DMARC reports, while first trashing the previews:
```python
# dmarc.py

from imap_thingy.accounts import EMailAccount
from imap_thingy.filters.criterion_filter import CriterionFilter, from_is, move_to, subject_matches

from imap_thingy.filters.interfaces import OneAccountOneFolderFilter

class DmarcFilter(OneAccountOneFolderFilter):
    def __init__(self, account: EMailAccount, sender, folder, delete_preview=True, base_folder="INBOX"):
        super().__init__(account, base_folder=base_folder)
        self.filters = [CriterionFilter(account, from_is(sender), move_to(folder), base_folder=base_folder)]
        if delete_preview: self.filters = [CriterionFilter(account, from_is(sender) & subject_matches("[Preview] .*"), move_to("Trash"), base_folder=base_folder)] + self.filters

    def apply(self, dry_run=False):
        for filter in self.filters:
            filter.apply(dry_run=dry_run)

```

## Contributing
Feel free to raise issues or open pull requests!


## License
[GPL v.3](https://www.gnu.org/licenses/gpl-3.0.en.html)
