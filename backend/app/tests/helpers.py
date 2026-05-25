"""Shared test fixtures for checkout payloads."""

TEST_SHIPPING = {
    "street_address": "123 Main St",
    "apt_suite_other": "",
    "city": "Austin",
    "state": "TX",
    "zipcode": "78701",
    "country": "US",
    "phone_number": "+15551234567",
}


def checkout_payload(session_id: str, email: str = "buyer@example.com", **extra) -> dict:
    return {
        "session_id": session_id,
        "customer_email": email,
        "customer_name": "Test Buyer",
        "shipping": TEST_SHIPPING,
        **extra,
    }
