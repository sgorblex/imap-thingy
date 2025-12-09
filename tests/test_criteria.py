"""Tests for criteria classes."""

from datetime import date, datetime

from imap_thingy.filters.criteria import (
    BccIs,
    CcIs,
    Criterion,
    FromIs,
    FromMatches,
    OlderThan,
    SelectAll,
    SubjectContains,
    SubjectIs,
    SubjectMatches,
    ToIs,
)


class TestCriteriaCombination:
    """Test criteria boolean operations."""

    def test_criteria_and_combination(self) -> None:
        """Test combining criteria with AND operator."""
        criterion1 = FromIs("sender@example.com")
        criterion2 = SubjectContains("Important")
        combined = criterion1 & criterion2
        assert isinstance(combined, Criterion)

    def test_criteria_or_combination(self) -> None:
        """Test combining criteria with OR operator."""
        criterion1 = FromIs("sender1@example.com")
        criterion2 = FromIs("sender2@example.com")
        combined = criterion1 | criterion2
        assert isinstance(combined, Criterion)

    def test_criteria_negation(self) -> None:
        """Test negating a criterion."""
        criterion = FromIs("sender@example.com")
        negated = ~criterion
        assert isinstance(negated, Criterion)


class TestAddressCriteria:
    """Test address-based criteria."""

    def test_from_is_creation(self) -> None:
        """Test FromIs criterion creation."""
        criterion = FromIs("test@example.com")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["FROM", "test@example.com"]

    def test_to_is_creation(self) -> None:
        """Test ToIs criterion creation."""
        criterion = ToIs("test@example.com")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["TO", "test@example.com"]

    def test_cc_is_creation(self) -> None:
        """Test CcIs criterion creation."""
        criterion = CcIs("test@example.com")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["CC", "test@example.com"]

    def test_bcc_is_creation(self) -> None:
        """Test BccIs criterion creation."""
        criterion = BccIs("test@example.com")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["BCC", "test@example.com"]

    def test_from_matches_creation(self) -> None:
        """Test FromMatches criterion creation."""
        criterion = FromMatches(r".*@example\.com")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query is None


class TestSubjectCriteria:
    """Test subject-based criteria."""

    def test_subject_contains_creation(self) -> None:
        """Test SubjectContains criterion creation."""
        criterion = SubjectContains("Important")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["SUBJECT", "Important"]

    def test_subject_is_creation(self) -> None:
        """Test SubjectIs criterion creation."""
        criterion = SubjectIs("Exact Subject")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["SUBJECT", "Exact Subject"]

    def test_subject_matches_creation(self) -> None:
        """Test SubjectMatches criterion creation."""
        criterion = SubjectMatches(r"^\[.*\]")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query is None


class TestDateCriteria:
    """Test date-based criteria."""

    def test_older_than_with_date(self) -> None:
        """Test OlderThan with date object."""
        cutoff = date(2025, 1, 1)
        criterion = OlderThan(cutoff)
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["SENTBEFORE", "01-Jan-2025"]

    def test_older_than_with_datetime(self) -> None:
        """Test OlderThan with datetime object."""
        cutoff = datetime(2025, 1, 1, 12, 0, 0)
        criterion = OlderThan(cutoff)
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["SENTBEFORE", "01-Jan-2025"]

    def test_older_than_with_string(self) -> None:
        """Test OlderThan with string date."""
        criterion = OlderThan("01-Jan-2025")
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["SENTBEFORE", "01-Jan-2025"]


class TestSpecialCriteria:
    """Test special criteria."""

    def test_select_all_creation(self) -> None:
        """Test SelectAll criterion creation."""
        criterion = SelectAll()
        assert isinstance(criterion, Criterion)
        assert criterion.imap_query == ["ALL"]
