"""Celery tasks for syncing data from external APIs (QuickBooks, Google Ads)."""

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.sync_tasks.sync_all_accounting")
def sync_all_accounting():
    """Sync accounting data for all active connections."""
    # TODO: Implement in Week 3
    # 1. Query all active QuickBooks/Xero connections
    # 2. For each connection, pull P&L, balance sheet, invoices, bills
    # 3. Transform and store in financial_periods + financial_transactions
    # 4. Update connection.last_synced_at
    pass


@celery_app.task(name="app.tasks.sync_tasks.sync_all_marketing")
def sync_all_marketing():
    """Sync marketing data for all active Google Ads connections."""
    # TODO: Implement in Week 4
    # 1. Query all active Google Ads connections
    # 2. For each connection, pull campaigns and daily metrics
    # 3. Upsert into ad_campaigns + campaign_metrics_daily
    # 4. Calculate derived metrics (CPC, CTR, ROAS)
    pass


@celery_app.task(name="app.tasks.sync_tasks.sync_single_connection")
def sync_single_connection(connection_id: str):
    """Sync data for a single connection (triggered after OAuth or manual refresh)."""
    # TODO: Implement
    pass
