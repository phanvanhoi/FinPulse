"""LangGraph orchestrator for multi-agent insight generation.

Workflow: Orchestrator -> [CFO Agent, CMO Agent] -> Blended Agent -> Formatter
This is a deterministic workflow, not an autonomous agent.
"""

import json
from datetime import UTC, datetime
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from app.agents.schemas import BlendedAnalysis, CFOAnalysis, CMOAnalysis, FormattedInsight
from app.config import settings

# LiteLLM for LLM-agnostic API calls
import litellm


class AgentState(TypedDict):
    financial_data: dict
    marketing_data: dict
    cfo_analysis: CFOAnalysis | None
    cmo_analysis: CMOAnalysis | None
    blended_analysis: BlendedAnalysis | None
    insights: list[FormattedInsight]


async def _call_llm(prompt: str, response_model: type | None = None) -> str:
    """Call LLM via LiteLLM - supports Claude, GPT-4, etc."""
    response = await litellm.acompletion(
        model=settings.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )
    return response.choices[0].message.content


async def run_cfo_agent(state: AgentState) -> dict:
    from app.agents.prompts.cfo_weekly import CFO_WEEKLY_PROMPT

    prompt = CFO_WEEKLY_PROMPT.format(financial_data=json.dumps(state["financial_data"], default=str))
    result = await _call_llm(prompt)

    # Parse structured output (in production, use instructor or structured output API)
    return {"cfo_analysis": CFOAnalysis(
        revenue_trend=result[:200],
        margin_trend="",
        expense_anomalies=[],
        ar_concerns=[],
        key_metrics=[],
        summary=result,
    )}


async def run_cmo_agent(state: AgentState) -> dict:
    from app.agents.prompts.cmo_weekly import CMO_WEEKLY_PROMPT

    prompt = CMO_WEEKLY_PROMPT.format(marketing_data=json.dumps(state["marketing_data"], default=str))
    result = await _call_llm(prompt)

    return {"cmo_analysis": CMOAnalysis(
        best_campaigns=[],
        worst_campaigns=[],
        spend_efficiency="",
        conversion_trends="",
        budget_pacing="",
        key_metrics=[],
        summary=result,
    )}


async def run_blended_agent(state: AgentState) -> dict:
    from app.agents.prompts.blended import BLENDED_PROMPT

    prompt = BLENDED_PROMPT.format(
        cfo_analysis=state["cfo_analysis"].summary if state["cfo_analysis"] else "No financial data",
        cmo_analysis=state["cmo_analysis"].summary if state["cmo_analysis"] else "No marketing data",
    )
    result = await _call_llm(prompt)

    return {"blended_analysis": BlendedAnalysis(
        marketing_spend_pct_of_revenue=0,
        recommendations=[],
        summary=result,
    )}


async def run_formatter(state: AgentState) -> dict:
    from app.agents.prompts.formatter import FORMATTER_PROMPT

    insights = []

    # Format each analysis into user-facing insights
    for analysis, category in [
        (state.get("cfo_analysis"), "financial"),
        (state.get("cmo_analysis"), "marketing"),
        (state.get("blended_analysis"), "blended"),
    ]:
        if analysis is None:
            continue

        prompt = FORMATTER_PROMPT.format(analysis=analysis.summary)
        result = await _call_llm(prompt)

        insights.append(FormattedInsight(
            title=result.split("\n")[0][:80] if result else f"{category.title()} Weekly Summary",
            body_markdown=result,
            severity="info",
            category=category,
            insight_type="summary",
            data_context={"generated_at": datetime.now(UTC).isoformat()},
        ))

    return {"insights": insights}


def build_insight_graph() -> StateGraph:
    """Build the LangGraph workflow for insight generation."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("cfo_agent", run_cfo_agent)
    graph.add_node("cmo_agent", run_cmo_agent)
    graph.add_node("blended_agent", run_blended_agent)
    graph.add_node("formatter", run_formatter)

    # Define edges - CFO and CMO run first (could be parallel), then blended, then formatter
    graph.set_entry_point("cfo_agent")
    graph.add_edge("cfo_agent", "cmo_agent")
    graph.add_edge("cmo_agent", "blended_agent")
    graph.add_edge("blended_agent", "formatter")
    graph.add_edge("formatter", END)

    return graph.compile()
