"""
Smoke tests for LangGraph tools with mocked DB and LLM.
These verify tool signatures and return shapes without real DB/Groq calls.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def make_mock_hcp(id="hcp-001", first="Priya", last="Sharma", specialty="Cardiology", hospital="Apollo", city="Hyderabad"):
    h = MagicMock()
    h.id = id
    h.first_name = first
    h.last_name = last
    h.specialty = specialty
    h.hospital = hospital
    h.city = city
    h.email = f"{first.lower()}@test.com"
    return h


def make_mock_interaction(id="int-001", hcp_id="hcp-001"):
    i = MagicMock()
    i.id = id
    i.hcp_id = hcp_id
    i.summary = "Test summary"
    i.sentiment = "positive"
    i.key_entities = {"drugs_mentioned": ["Atorvastatin"]}
    i.raw_notes = "Great meeting with Dr. Sharma"
    i.interaction_date = None
    i.interaction_type = "in_person"
    i.products_discussed = ["Atorvastatin"]
    i.outcome = "Positive"
    i.source = "chat"
    return i


class TestSearchHCP:
    def test_returns_list(self):
        """search_hcp tool returns a list."""
        mock_hcp = make_mock_hcp()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_hcp]

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("app.tools.search_hcp.AsyncSessionLocal", return_value=mock_session):
            import asyncio
            from app.tools.search_hcp import _search_hcp_async
            result = asyncio.get_event_loop().run_until_complete(_search_hcp_async("Sharma", 5))

        assert isinstance(result, list)
        assert result[0]["name"] == "Priya Sharma"
        assert result[0]["id"] == "hcp-001"


class TestGetInteractionHistory:
    def test_returns_list_with_uuid(self):
        """get_interaction_history returns list when given UUID."""
        mock_interaction = make_mock_interaction()
        mock_hcp = make_mock_hcp()

        mock_result_int = MagicMock()
        mock_result_int.scalars.return_value.all.return_value = [mock_interaction]

        mock_result_hcp = MagicMock()
        mock_result_hcp.scalar_one_or_none.return_value = mock_hcp

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=[mock_result_int, mock_result_hcp])
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("app.tools.get_interaction_history.AsyncSessionLocal", return_value=mock_session):
            import asyncio
            from app.tools.get_interaction_history import _get_history_async
            result = asyncio.get_event_loop().run_until_complete(
                _get_history_async("hcp-001", 10)
            )

        assert isinstance(result, list)
        assert result[0]["interaction_id"] == "int-001"


class TestScheduleFollowup:
    def test_invalid_date_returns_error(self):
        """schedule_followup returns error dict on invalid date."""
        mock_interaction = make_mock_interaction()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_interaction

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("app.tools.schedule_followup.AsyncSessionLocal", return_value=mock_session):
            import asyncio
            from app.tools.schedule_followup import _schedule_followup_async
            result = asyncio.get_event_loop().run_until_complete(
                _schedule_followup_async("int-001", "not-a-date", "Deliver samples")
            )

        assert "error" in result
        assert "Invalid date" in result["error"]
