"""PayPal Checkout Orders API v2 client."""

from decimal import Decimal

import httpx

from app.config import settings
from app.integrations.paypal.exceptions import PayPalAPIError, PayPalAuthError


class PayPalClient:
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        mode: str | None = None,
    ):
        self.client_id = client_id or settings.PAYPAL_CLIENT_ID
        self.client_secret = client_secret or settings.PAYPAL_CLIENT_SECRET
        self.mode = (mode or settings.PAYPAL_MODE or "sandbox").lower()
        self.base_url = (
            "https://api-m.sandbox.paypal.com"
            if self.mode == "sandbox"
            else "https://api-m.paypal.com"
        )

    async def _get_access_token(self) -> str:
        if not self.client_id or not self.client_secret:
            raise PayPalAuthError("PayPal credentials not configured")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                headers={"Accept": "application/json"},
            )

        if response.status_code == 401:
            raise PayPalAuthError("Invalid PayPal client credentials")
        if response.status_code >= 400:
            raise PayPalAPIError(f"PayPal auth failed: {response.text}", response.status_code)

        return response.json()["access_token"]

    async def create_checkout_order(
        self,
        *,
        amount: Decimal,
        currency: str,
        return_url: str,
        cancel_url: str,
        reference_id: str,
        description: str,
    ) -> tuple[str, str]:
        """Returns (paypal_order_id, approve_url)."""
        token = await self._get_access_token()
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": reference_id,
                    "description": description[:127],
                    "amount": {
                        "currency_code": currency.upper(),
                        "value": f"{amount:.2f}",
                    },
                }
            ],
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
                "brand_name": settings.APP_NAME,
                "user_action": "PAY_NOW",
            },
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )

        if response.status_code >= 400:
            raise PayPalAPIError(f"PayPal create order failed: {response.text}", response.status_code)

        data = response.json()
        paypal_order_id = data["id"]
        approve_url = next(
            (link["href"] for link in data.get("links", []) if link.get("rel") == "approve"),
            "",
        )
        if not approve_url:
            raise PayPalAPIError("PayPal did not return an approval URL")

        return paypal_order_id, approve_url

    async def capture_order(self, paypal_order_id: str) -> dict:
        token = await self._get_access_token()

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders/{paypal_order_id}/capture",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )

        if response.status_code >= 400:
            raise PayPalAPIError(f"PayPal capture failed: {response.text}", response.status_code)

        return response.json()
