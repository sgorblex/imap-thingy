from imap_thingy.filters.move_if_to import MoveIfTo
from imap_thingy.filters.move_if_from import MoveIfFrom
from imap_thingy import ACCOUNTS

velimir = ACCOUNTS["example"]

FILTERS = [
        MoveIfFrom(example, "spam@example.org", "example_folder", mark_as_read=False),
]
