"""End-to-end test that runs the ASK agent in a loop with a real LLM."""
from openai import OpenAI
from law_compiler import compile_law
from law_enforcer import add_law
from agent_runner import run_agent

# -------- STEP 2 (RIGHT HERE) --------
LAW_TEXT = '''
LAW {
  when inventory > 0
  block refund_order
  because "Check inventory first"
}
'''
add_law(compile_law(LAW_TEXT))
# ------------------------------------

client = OpenAI()

prompt = """
You are an automation agent. 
You MUST output JSON ONLY.

Use THIS exact structure:

{
  "plan": [
    {
      "action": "<tool_name>",
      "order_id": "<string>"
    }
  ]
}

Allowed tools:
- verify_order
- check_inventory
- refund_order

DO NOT add extra fields.
DO NOT add natural language explanations.

Task: Refund order #123.
"""


print("\n=== ASKING REAL LLM ===\n")

# -------- NEW: HAND CONTROL TO AGENT RUNNER (THE LOOP) --------

print("\n=== RUNNING AGENT LOOP WITH ASK ===\n")

runtime_context = {
    "inventory": 10,
    "refund_done": False
}

final_result = run_agent(
    goal="Refund order #123",
    runtime_context=runtime_context,
    max_iterations=5
)

print("\n=== FINAL RESULT ===")
print(final_result)
