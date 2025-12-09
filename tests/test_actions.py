"""Tests for action classes."""

from unittest.mock import MagicMock

from imap_thingy.accounts import EMailAccount
from imap_thingy.filters.actions import Action, MarkAsRead, MarkAsUnread, MoveTo, Trash


class TestActionCreation:
    """Test action class creation."""

    def test_move_to_creation(self) -> None:
        """Test MoveTo action creation."""
        action = MoveTo("TestFolder")
        assert isinstance(action, Action)
        assert action.name == "move to TestFolder"

    def test_trash_creation(self) -> None:
        """Test Trash action creation."""
        action = Trash()
        assert isinstance(action, Action)
        assert action.name == "trash"

    def test_mark_as_read_creation(self) -> None:
        """Test MarkAsRead action creation."""
        action = MarkAsRead()
        assert isinstance(action, Action)
        assert action.name == "mark as read"

    def test_mark_as_unread_creation(self) -> None:
        """Test MarkAsUnread action creation."""
        action = MarkAsUnread()
        assert isinstance(action, Action)
        assert action.name == "mark as unread"


class TestActionChaining:
    """Test action chaining with & operator."""

    def test_action_chaining(self) -> None:
        """Test chaining two actions together."""
        action1 = MarkAsRead()
        action2 = MoveTo("Folder")
        chained = action1 & action2
        assert isinstance(chained, Action)
        assert "mark as read" in chained.name
        assert "move to Folder" in chained.name

    def test_action_chaining_execution(self, mock_account: EMailAccount) -> None:
        """Test that chained actions execute both functions."""
        call_order: list[str] = []

        def action1_func(account: EMailAccount, msgids: list[int]) -> None:
            call_order.append("action1")

        def action2_func(account: EMailAccount, msgids: list[int]) -> None:
            call_order.append("action2")

        action1 = Action(action1_func, "action1")
        action2 = Action(action2_func, "action2")
        chained = action1 & action2

        chained.execute(mock_account, [1, 2, 3])
        assert call_order == ["action1", "action2"]


class TestActionExecution:
    """Test action execution."""

    def test_move_to_execution(self, mock_account: EMailAccount) -> None:
        """Test MoveTo action execution."""
        mock_account.connection.move = MagicMock()
        action = MoveTo("TestFolder")
        action.execute(mock_account, [1, 2, 3])
        mock_account.connection.move.assert_called_once_with([1, 2, 3], "TestFolder")

    def test_mark_as_read_execution(self, mock_account: EMailAccount) -> None:
        """Test MarkAsRead action execution."""
        mock_account.connection.add_flags = MagicMock()
        action = MarkAsRead()
        action.execute(mock_account, [1, 2, 3])
        mock_account.connection.add_flags.assert_called_once_with([1, 2, 3], [b"\\Seen"])

    def test_mark_as_unread_execution(self, mock_account: EMailAccount) -> None:
        """Test MarkAsUnread action execution."""
        mock_account.connection.remove_flags = MagicMock()
        action = MarkAsUnread()
        action.execute(mock_account, [1, 2, 3])
        mock_account.connection.remove_flags.assert_called_once_with([1, 2, 3], [b"\\Seen"])
