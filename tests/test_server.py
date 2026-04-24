"""Tests for server helpers."""

from fortimanager_mcp.server import _tool_result_success


class TestToolResultSuccess:
    """Tests for dynamic tool success normalization."""

    def test_status_error_is_failure(self) -> None:
        assert _tool_result_success({"status": "error", "message": "boom"}) is False

    def test_error_key_is_failure(self) -> None:
        assert _tool_result_success({"error": "blocked"}) is False

    def test_explicit_success_false_is_failure(self) -> None:
        assert _tool_result_success({"success": False, "result": {}}) is False

    def test_successful_result_dict_is_success(self) -> None:
        assert _tool_result_success({"success": True, "message": "ok"}) is True
