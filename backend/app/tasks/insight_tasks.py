"""Celery tasks for AI insight generation."""

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.insight_tasks.generate_daily_insights")
def generate_daily_insights():
    """Generate AI insights for all organizations with active data."""
    # TODO: Implement in Week 9
    # 1. Query all organizations with at least 1 active connection
    # 2. For each org, gather latest financial + marketing data
    # 3. Run the LangGraph insight pipeline (orchestrator.py)
    # 4. Store generated insights in ai_insights table
    pass


@celery_app.task(name="app.tasks.insight_tasks.generate_org_insights")
def generate_org_insights(organization_id: str):
    """Generate insights for a specific organization."""
    # TODO: Implement
    pass
