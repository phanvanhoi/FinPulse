"""Celery tasks for alert evaluation and notification."""

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.alert_tasks.evaluate_all_alerts")
def evaluate_all_alerts():
    """Evaluate all active alert configs against current data."""
    # TODO: Implement in Week 10
    # 1. Query all active AlertConfig records
    # 2. For each alert, fetch the relevant metric value
    # 3. Compare against threshold using operator
    # 4. If triggered, create an AIInsight with severity=warning/critical
    # 5. Send notification via configured channels (in_app, email)
    pass
