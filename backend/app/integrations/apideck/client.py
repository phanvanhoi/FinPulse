"""Apideck client for QuickBooks/Xero integration via unified accounting API."""

import httpx

from app.config import settings

APIDECK_BASE_URL = "https://unify.apideck.com"


class ApideckClient:
    def __init__(self, consumer_id: str | None = None):
        self.api_key = settings.APIDECK_API_KEY
        self.app_id = settings.APIDECK_APP_ID
        self.consumer_id = consumer_id or settings.APIDECK_CONSUMER_ID

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "x-apideck-app-id": self.app_id,
            "x-apideck-consumer-id": self.consumer_id,
            "Content-Type": "application/json",
        }

    async def create_session(self, redirect_uri: str, settings_config: dict | None = None) -> dict:
        """Create a Vault session for user to connect their accounting platform."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{APIDECK_BASE_URL}/vault/sessions",
                headers=self.headers,
                json={
                    "consumer_metadata": {"account_name": self.consumer_id},
                    "redirect_uri": redirect_uri,
                    "settings": settings_config or {},
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_profit_and_loss(self, start_date: str, end_date: str) -> dict:
        """Fetch P&L report from connected accounting platform."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{APIDECK_BASE_URL}/accounting/profit-and-loss",
                headers=self.headers,
                params={
                    "filter[start_date]": start_date,
                    "filter[end_date]": end_date,
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_balance_sheet(self, date: str) -> dict:
        """Fetch balance sheet from connected accounting platform."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{APIDECK_BASE_URL}/accounting/balance-sheet",
                headers=self.headers,
                params={"filter[date]": date},
            )
            response.raise_for_status()
            return response.json()

    async def list_invoices(self, cursor: str | None = None, limit: int = 100) -> dict:
        """List invoices for AR tracking."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{APIDECK_BASE_URL}/accounting/invoices",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def list_bills(self, cursor: str | None = None, limit: int = 100) -> dict:
        """List bills for AP tracking."""
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{APIDECK_BASE_URL}/accounting/bills",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()
