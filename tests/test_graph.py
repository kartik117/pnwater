import pytest

from pnwater.services.alert_agent import llm as llm_module
from pnwater.services.alert_agent.graph import build_graph, classify_severity, format_message


@pytest.fixture(autouse=True)
def _reset_llm_client():
    llm_module.reset_for_test()
    yield
    llm_module.reset_for_test()


def _state(**overrides):
    base = {
        "river_id": "yakima",
        "parameter": "temp_c",
        "value": 35.0,
        "baseline_mean": 23.2,
        "z_score": 4.7,
        "severity": "",
        "message": "",
    }
    base.update(overrides)
    return base


def test_classify_severity_thresholds():
    assert classify_severity(_state(z_score=1.0))["severity"] == "info"
    assert classify_severity(_state(z_score=3.0))["severity"] == "warning"
    assert classify_severity(_state(z_score=5.0))["severity"] == "critical"
    assert classify_severity(_state(z_score=-5.0))["severity"] == "critical"


def test_format_message_states_direction_and_severity():
    state = classify_severity(_state(z_score=4.7))
    state = format_message(state)
    assert "above" in state["message"]
    assert "critical" in state["message"]
    assert "yakima" in state["message"]


def test_format_message_states_below_for_negative_deviation():
    state = _state(value=10.0, baseline_mean=23.2, z_score=-4.7)
    state = classify_severity(state)
    state = format_message(state)
    assert "below" in state["message"]


@pytest.mark.asyncio
async def test_full_graph_runs_without_an_api_key_configured(monkeypatch):
    monkeypatch.setattr(llm_module.settings, "google_api_key", "")
    graph = build_graph()

    result = await graph.ainvoke(_state())

    assert result["severity"] == "critical"
    assert "yakima" in result["message"]
    # No LLM key configured -- the deterministic message must stand
    # unchanged, not crash and not silently produce an empty message.
    assert result["message"].endswith("(critical).")
