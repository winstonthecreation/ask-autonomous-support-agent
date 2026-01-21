# api_explorer.py

import json

# -------- MOCK "UNKNOWN SYSTEM" --------
MOCK_API_CATALOG = {
    "shopify_like_system": {
        "endpoints": {
            "/orders/{order_id}": {
                "method": "GET",
                "description": "Fetch order details"
            },
            "/inventory/{sku}": {
                "method": "GET",
                "description": "Check inventory level"
            },
            "/refunds": {
                "method": "POST",
                "description": "Create a refund"
            }
        }
    }
}

def discover_api(system_name: str):
    """
    Simulate discovering an unknown API.
    In real life: this would read OpenAPI docs, hit endpoints, or inspect responses.
    """

    print(f"\n🔍 DISCOVERING API for system: {system_name}\n")

    if system_name not in MOCK_API_CATALOG:
        raise ValueError(f"Unknown system: {system_name}")

    api = MOCK_API_CATALOG[system_name]

    print("Found endpoints:")
    for path, info in api["endpoints"].items():
        print(f"- {info['method']} {path} → {info['description']}")

    return api

def call_api(_system_name: str, endpoint: str, method: str, payload: dict = None):
    """
    Simulate calling an API.
    In real life: this would use requests / httpx to make real HTTP calls.
    """

    print(f"\n📡 CALLING API: {method} {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    # --- MOCK RESPONSES ---
    if endpoint.startswith("/inventory"):
        return {"status": "success", "inventory": 10}

    if endpoint == "/refunds":
        return {"status": "success", "refund_id": "r_123"}

    return {"status": "success", "data": "mock_response"}
