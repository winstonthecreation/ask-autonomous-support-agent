# ===========================
# 1) MAKE SURE PYTHON LOADS YOUR PROJECT
# ===========================
import sys
sys.path.insert(0, r"C:\Users\Admin\Desktop\Pen To Profit\ASK")

# ===========================
# 2) IMPORT YOUR SYSTEM
# ===========================
from law_compiler import compile_law
from law_enforcer import add_law, LAW_BOOK
from agent_models import ActionPlan, ActionStep
from execution_engine import execute_plan

# ===========================
# 3) DEFINE THE WORLD (RUNTIME CONTEXT)
# ===========================
runtime_context = {
    "inventory": 10   # There IS inventory available
}

print("\n🌍 === INITIAL WORLD STATE ===")
print(runtime_context)

# ===========================
# 4) ADD A HUMAN LAW (STORE OWNER RULE)
# ===========================
LAW_TEXT = '''
LAW {
  when inventory > 0
  block refund_order
  because "Check inventory first"
}
'''

law = compile_law(LAW_TEXT)
add_law(law)

print("\n📜 === HUMAN LAW ADDED ===")
for law in LAW_BOOK:
    print(f"- If {law.condition}, block {law.block_actions} because: {law.reason}")

# ===========================
# 5) CREATE A BAD PLAN (NAIVE AGENT)
# ===========================
bad_plan = ActionPlan(
    goal="Refund the customer",
    preconditions=[],
    actions=[
        ActionStep(
            tool="refund_order",
            input_schema={"order_id": "123"},
            success_condition="result['success']"
        )
    ],
    postconditions=[],
    fallback=[]
)

print("\n🚫 === RUNNING NAIVE (BAD) PLAN ===")
bad_result = execute_plan(bad_plan, runtime_context)
print("👉 RESULT:", bad_result)

# ===========================
# 6) CREATE A GOOD PLAN (TRAINED AGENT)
# ===========================
good_plan = ActionPlan(
    goal="Refund safely",
    preconditions=[],
    actions=[
        ActionStep(
            tool="check_inventory",
            input_schema={"order_id": "123"},
            success_condition="result['inventory'] > 0"
        ),
        ActionStep(
            tool="refund_order",
            input_schema={"order_id": "123"},
            success_condition="result['success']"
        )
    ],
    postconditions=[],
    fallback=[]
)

print("\n✅ === RUNNING SAFE (GOOD) PLAN ===")
good_result = execute_plan(good_plan, runtime_context)
print("👉 RESULT:", good_result)
