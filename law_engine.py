# ----------------------------
# LAW ENGINE = TOOL LAYER + EXCEPTIONS
# ----------------------------

class LawViolation(Exception):
    """Custom exception raised when a law is violated."""

# ---- MOCK REAL-WORLD TOOLS (v1 demo) ----

def refund_order(order_id: str):
    """Mock refund tool for demo."""
    print(f"💸 Refunding order {order_id} (mock)...")
    return {
        "status": "success",
        "order_id": order_id
    }

def check_inventory(order_id: str):
    """Mock inventory check for demo."""
    print(f"📦 Checking inventory for order {order_id} (mock)...")
    return {
        "status": "success",
        "inventory": 10
    }

def verify_order(order_id: int):
    """Mock order verification for demo."""
    print(f"🔎 Verifying order {order_id} (mock)...")
    return {
        "status": "success",
        "order_id": order_id,
        "order_status": "paid"
    }

# ---- TOOL REGISTRY (SINGLE SOURCE OF TRUTH FOR DEMO) ----
TOOL_REGISTRY = {
    "refund_order": refund_order,
    "check_inventory": check_inventory,
    "verify_order": verify_order,
}