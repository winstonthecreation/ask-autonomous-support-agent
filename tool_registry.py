"""Simple tool registry for demo and testing purposes."""
TOOL_REGISTRY = {}

def register_tool(name, func):
    """Register a tool in the global TOOL_REGISTRY."""
    TOOL_REGISTRY[name] = func
    
def refund_order(order_id, _amount=None):
    """Mock refund tool for demo."""
    print(f"Refunding order {order_id}")
    return {"status": "success"}

def check_inventory(order_id):
    """Mock inventory check for demo."""
    print(f"Checking inventory for order {order_id}")
    return {"status":"success", "inventory": 10}

# register_tool("refund_order", refund_order)
# register_tool("check_inventory", check_inventory)
