"""BurgerPrints API v2 client for POD fulfillment."""

import httpx

from app.config import settings
from app.integrations.burgerprints.exceptions import BurgerPrintsAPIError, BurgerPrintsAuthError
from app.integrations.burgerprints.schemas import BurgerPrintsCreateOrderRequest, BurgerPrintsOrderResult


class BurgerPrintsClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.BURGERPRINTS_API_KEY
        self.base_url = (base_url or settings.BURGERPRINTS_API_BASE_URL).rstrip("/")

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if "burgerprints.com" in self.base_url:
            headers["Host"] = "api.burgerprints.com"
        return headers

    def _parse_response(self, response: httpx.Response) -> dict:
        try:
            payload = response.json()
        except ValueError as exc:
            raise BurgerPrintsAPIError(
                f"Invalid JSON response from BurgerPrints (HTTP {response.status_code})",
                status_code=response.status_code,
            ) from exc

        if response.status_code in (401, 403) or payload.get("message") == "Failed to authenticate.":
            raise BurgerPrintsAuthError(payload.get("message", "Failed to authenticate."))

        if payload.get("is_success") is False:
            raise BurgerPrintsAPIError(
                payload.get("message", "BurgerPrints request failed"),
                status_code=response.status_code,
                errors=payload.get("errors") or [],
            )

        if response.status_code >= 400:
            message = payload.get("message") or response.text or "BurgerPrints request failed"
            raise BurgerPrintsAPIError(message, status_code=response.status_code)

        return payload

    async def verify_api_key(self) -> bool:
        """Validate API key. Auth errors raise BurgerPrintsAuthError."""
        if not self.api_key:
            raise BurgerPrintsAuthError("BurgerPrints API key is not configured")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/order/0", headers=self.headers)
        except httpx.HTTPError as exc:
            raise BurgerPrintsAPIError(f"Could not reach BurgerPrints API: {exc}") from exc

        if response.status_code in (401, 403):
            raise BurgerPrintsAuthError("Invalid BurgerPrints API key")

        try:
            payload = response.json()
        except ValueError as exc:
            raise BurgerPrintsAPIError("Invalid response while verifying API key") from exc

        if payload.get("message") == "Failed to authenticate.":
            raise BurgerPrintsAuthError(payload.get("message", "Invalid BurgerPrints API key"))

        if payload.get("is_success") is False and response.status_code not in (404,):
            raise BurgerPrintsAPIError(
                payload.get("message", "BurgerPrints API verification failed"),
                status_code=response.status_code,
            )

        return True

    async def get_order(self, order_id: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/order/{order_id}", headers=self.headers)
        payload = self._parse_response(response)
        return payload.get("result") or payload

    async def create_order(self, request: BurgerPrintsCreateOrderRequest) -> BurgerPrintsOrderResult:
        body = request.model_dump(exclude_none=True)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{self.base_url}/order", headers=self.headers, json=body)

        payload = self._parse_response(response)
        result = payload.get("result") or payload
        order_id = str(result.get("id") or result.get("order_id") or "")
        if not order_id:
            raise BurgerPrintsAPIError("BurgerPrints did not return an order ID", status_code=response.status_code)

        return BurgerPrintsOrderResult(
            order_id=order_id,
            status=result.get("status"),
            raw=result if isinstance(result, dict) else None,
        )
