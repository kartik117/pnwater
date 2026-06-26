from __future__ import annotations

import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from pnwater.config import settings
from pnwater.models.schemas import Severity
from pnwater.services.alert_agent.llm import get_llm_client

logger = logging.getLogger(__name__)


class AlertState(TypedDict):
    river_id: str
    parameter: str
    value: float
    baseline_mean: float
    z_score: float
    severity: str
    message: str


def classify_severity(state: AlertState) -> AlertState:
    magnitude = abs(state["z_score"])
    if magnitude >= settings.anomaly_z_score_critical:
        severity = Severity.CRITICAL
    elif magnitude >= settings.anomaly_z_score_warning:
        severity = Severity.WARNING
    else:
        severity = Severity.INFO
    return {**state, "severity": severity.value}


def format_message(state: AlertState) -> AlertState:
    direction = "above" if state["value"] > state["baseline_mean"] else "below"
    message = (
        f"{state['river_id']}: {state['parameter']} reading of {state['value']:.2f} is "
        f"{abs(state['z_score']):.1f} std devs {direction} the {state['baseline_mean']:.2f} "
        f"baseline ({state['severity']})."
    )
    return {**state, "message": message}


def llm_explain(state: AlertState) -> AlertState:
    """Appends a plain-language explanation from Gemini when an API key
    is configured; otherwise the deterministic message from
    format_message stands unchanged. A failed or slow LLM call must
    never block an alert from being recorded, so any exception here is
    swallowed and logged, not raised.
    """
    client = get_llm_client()
    if client is None:
        return state

    try:
        response = client.invoke(
            "In one short sentence for a water-quality operator, explain this alert in plain "
            f"language without restating the numbers verbatim: {state['message']}"
        )
        explanation = (response.content or "").strip()
        if explanation:
            return {**state, "message": f"{state['message']} {explanation}"}
    except Exception:
        logger.exception("LLM explanation failed; keeping the deterministic message")
    return state


def build_graph():
    graph = StateGraph(AlertState)
    graph.add_node("classify_severity", classify_severity)
    graph.add_node("format_message", format_message)
    graph.add_node("llm_explain", llm_explain)
    graph.set_entry_point("classify_severity")
    graph.add_edge("classify_severity", "format_message")
    graph.add_edge("format_message", "llm_explain")
    graph.add_edge("llm_explain", END)
    return graph.compile()
