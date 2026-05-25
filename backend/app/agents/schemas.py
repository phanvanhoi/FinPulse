"""Structured output schemas for AI agents - ensures deterministic, citation-backed insights."""

from pydantic import BaseModel


class MetricDataPoint(BaseModel):
    metric_name: str
    current_value: float
    previous_value: float | None = None
    change_pct: float | None = None
    period: str


class CFOAnalysis(BaseModel):
    revenue_trend: str
    margin_trend: str
    cash_runway_days: int | None = None
    expense_anomalies: list[str]
    ar_concerns: list[str]
    key_metrics: list[MetricDataPoint]
    summary: str


class CMOAnalysis(BaseModel):
    best_campaigns: list[str]
    worst_campaigns: list[str]
    spend_efficiency: str
    conversion_trends: str
    budget_pacing: str
    key_metrics: list[MetricDataPoint]
    summary: str


class BlendedAnalysis(BaseModel):
    marketing_spend_pct_of_revenue: float
    estimated_cac: float | None = None
    revenue_per_ad_dollar: float | None = None
    recommendations: list[str]
    summary: str


class FormattedInsight(BaseModel):
    title: str
    body_markdown: str
    severity: str  # info, warning, critical
    category: str  # financial, marketing, blended
    insight_type: str  # summary, recommendation, alert, anomaly
    data_context: dict
