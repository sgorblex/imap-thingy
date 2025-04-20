# IMAP Thingy
An IMAP scripting library, primarily to make email filters.

Ever complained about receiving the same emails on multiple inboxes? Or wanted to auto-archive receipts that you've already opened? Or wanted your emails to get sorted automatically in some other way?

Well, complain no more!
(or at least not for this reason)

IMAP Thingy is a library that lets its users create advanced IMAP filters. Possibly on multiple emails, possibly even on multiple accounts.


## Installation
The quickest way is probably
```
git clone github.com/sgorblex/imap_thingy
cd imap_thingy
pip install -e .
imap-thingy --help
```


## Usage and examples
First, populate `accounts.json` with your email credentials.

At the moment we do not support OAUTH (PRs welcome :), so if you're using something like GMail you will have to generate an [app-password](https://support.google.com/accounts/answer/185833?hl=en)

Instantiation of simple filters (probably the most useful):
```python
# custom_filters/__init__.py

from imap_thingy.filters.basic_filters import MoveIfToFilter, MoveIfFromFilter
from imap_thingy.filters.criterion_filter import CriterionFilter, from_is, move_to, subject_matches, mark_as_read
from .dmarc import DmarcFilter

from imap_thingy import ACCOUNTS
xmpl = ACCOUNTS["example"]
sgor = ACCOUNTS["Sgorblex"]

FILTERS = [
        # In account example, move all mail directed to "members@boringassociation.org" to "Boring Association" folder
        MoveIfToFilter(xmpl, "members@boringassociation.org", "Boring Association"),
        # In account Sgorblex, move all mail from "googledev-noreply@google.com" to "Dev Stuff.Google Developer Program" folder. Note that folder delimiter may differ between servers
        MoveIfFromFilter(sgor, "googledev-noreply@google.com", "Dev Stuff.Google Developer Program"),
        # An instantiation of a more general filter based on a complex criterion and a series of actions
        CriterionFilter(xmpl, from_is("list4nerds@nerduniversity.edu") & subject_matches(r"List Digest, Vol \d\+"), mark_as_read() & move_to("List For Nerds")),
        # Custom filter, see below
        DmarcFilter(sgor, "dmarcreport@microsoft.com", "Postmaster.DMARC Reports"),
]
```

Arbitrarily complex filters can be implemented in Python, likely via `imapclient` and/or `pyzmail`, if not directly via our bindings. For example, here is a custom filter that I wrote to automatically move DMARC reports, while first trashing the previews:
```python
# custom_filters/dmarc.py

from imap_thingy.account import EMailAccount
from imap_thingy.filters.criterion_filter import CriterionFilter, from_is, move_to, subject_matches
from imap_thingy.filters.filter_interfaces import OneAccountOneFolderFilter

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
