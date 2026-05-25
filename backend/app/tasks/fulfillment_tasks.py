"""Celery tasks for BurgerPrints order fulfillment."""

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.fulfillment_tasks.submit_order_to_burgerprints")
def submit_order_to_burgerprints(order_id: str):
    from app.services.fulfillment_service import submit_order_to_burgerprints_sync

    return submit_order_to_burgerprints_sync(order_id)


@celery_app.task(name="app.tasks.fulfillment_tasks.retry_failed_fulfillment")
def retry_failed_fulfillment(order_id: str):
    from app.services.fulfillment_service import submit_order_to_burgerprints_sync

    return submit_order_to_burgerprints_sync(order_id)
