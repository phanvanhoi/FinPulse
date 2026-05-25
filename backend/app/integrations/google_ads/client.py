"""Google Ads API client for campaign and metrics sync."""

import httpx

from app.config import settings

GOOGLE_ADS_API_VERSION = "v17"
GOOGLE_ADS_BASE_URL = f"https://googleads.googleapis.com/{GOOGLE_ADS_API_VERSION}"


class GoogleAdsClient:
    def __init__(self, access_token: str, customer_id: str):
        self.access_token = access_token
        self.customer_id = customer_id.replace("-", "")
        self.developer_token = settings.GOOGLE_ADS_DEVELOPER_TOKEN

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "developer-token": self.developer_token,
            "Content-Type": "application/json",
        }

    async def search(self, query: str) -> dict:
        """Execute a GAQL query against the Google Ads API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GOOGLE_ADS_BASE_URL}/customers/{self.customer_id}/googleAds:searchStream",
                headers=self.headers,
                json={"query": query},
            )
            response.raise_for_status()
            return response.json()

    async def get_campaigns(self) -> dict:
        """Fetch all campaigns with basic info."""
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign_budget.amount_micros
            FROM campaign
            WHERE campaign.status != 'REMOVED'
            ORDER BY campaign.id
        """
        return await self.search(query)

    async def get_campaign_metrics(self, start_date: str, end_date: str) -> dict:
        """Fetch daily campaign metrics for a date range (YYYY-MM-DD format)."""
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                segments.date,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.cost_micros,
                metrics.conversions_value
            FROM campaign
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
                AND campaign.status != 'REMOVED'
            ORDER BY segments.date DESC
        """
        return await self.search(query)
