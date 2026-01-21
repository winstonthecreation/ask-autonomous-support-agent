"""Main agent loop that coordinates LLM, ASK, execution, and observation."""
from openai import OpenAI
from ask_bridge import llm_to_action_plan
from execution_engine import execute_plan
from agent_models import ActionStep

client = OpenAI()

def call_llm(goal: str, runtime_context: dict) -> str:
    """
    Ask the real LLM for a plan given the goal + current world state.
    Returns raw text (JSON-ish) from the model.
    """

    prompt = f"""
    You are an autonomous agent operating inside an ASK (Assured Safe Kernel) system.

    GOAL:
    {goal}

    CURRENT WORLD STATE:
    {runtime_context}

    YOU MUST OUTPUT ONLY JSON IN THIS EXACT FORMAT:

    {{
      "plan": [
        {{
          "action": "<one action name>",
          "order_id": 123,
          "... any other useful parameters ..."
        }}
      ]
    }}

    RULES:
    1) ALWAYS use top-level key "plan"
    2) "plan" MUST be a list
    3) Every step MUST include "action"
    4) Include "order_id" whenever relevant
    5) Do NOT add explanations, markdown, or code blocks — ONLY raw JSON
    """


    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def default_fallback(_plan):
    """
    Default safety fallback for now.
    Later we can make this smarter.
    """
    return [
        ActionStep(
            tool="check_inventory",
            input_schema={"order_id": "123"},
            success_condition="result.get('status') == 'success'"
        )
    ]


def observe_world(runtime_context: dict) -> dict:
    """
    DEMO VERSION: The agent 'perceives' what happened after execution.
    This simulates reading from real systems (DB, APIs, logs, etc.)
    """

    print("\n👁️ OBSERVING WORLD...")

    # Simulate reading from systems
    if runtime_context.get("refund_done"):
        runtime_context["last_observation"] = "Refund appears completed in payment system."
    else:
        runtime_context["last_observation"] = "No refund detected yet."

    # Simulate inventory observation
    if runtime_context.get("inventory", 0) <= 0:
        runtime_context["inventory_status"] = "OUT OF STOCK"
    else:
        runtime_context["inventory_status"] = f"{runtime_context['inventory']} units available"

    print("Observed world:", runtime_context)
    return runtime_context



def goal_satisfied(_goal: str, runtime_context: dict) -> bool:
    """
    Simple stopping rule for now.
    You can change this later.
    """

    # Example: if refund was successful, we stop.
    return runtime_context.get("refund_done", False)


def run_agent(goal: str, runtime_context: dict, max_iterations: int = 5):
    """
    FULL OUTER LOOP:
    propose → ASK enforces → act → observe → repeat
    """

    print("\n=== STARTING AGENT LOOP ===")
    print(f"🎯 Goal: {goal}")
    print(f"🌍 Initial world: {runtime_context}\n")


    for i in range(max_iterations):
        print(f"\n🚀 === ITERATION {i+1} ===")
        raw = call_llm(goal, runtime_context)
        print("\n🤖 LLM PROPOSED PLAN:\n", raw)


# -------- STEP 5.4: MULTI-RETRY SAFE PARSING (3 ATTEMPTS) --------
        max_retries = 3
        attempt = 0

        if "order_id" not in runtime_context:
            runtime_context["order_id"] = 123

        while True:
            try:
                plan = llm_to_action_plan(raw)
                break   # SUCCESS → exit loop

            except RuntimeError as e:
                attempt += 1

                if attempt > max_retries:
                    print("\n🚨 FATAL: LLM failed 3 times — giving up.")
                    raise e  # let it crash intentionally

                print(f"\n❌ PARSE ERROR (attempt {attempt}/{max_retries}) — repairing LLM output...\n")

                repair_prompt = f"""
                Your previous output was invalid JSON.

                ERROR:
                {e}

                CURRENT WORLD STATE:
                {runtime_context}

                Respond ONLY with JSON in exactly this format:

                {{
                    "plan": [
                        {{
                            "action": "check_inventory",
                            "order_id": 123
                        }}
                    ]
                }}
                """


                raw = client.responses.create(
                    model="gpt-4.1-mini",
                    input=repair_prompt
                ).output_text

                print("\nREPAIRED RAW OUTPUT:\n", raw)
# -------- END STEP 5.4 --------

        result = execute_plan(plan, runtime_context)
        runtime_context = observe_world(runtime_context)

        if result["status"] == "BLOCKED":
            print(f"\n❌ ASK BLOCKED THE PLAN: {result.get('reason')}")
        elif result["status"] == "FAILED":
            print("\n⚠️ PLAN FAILED — Agent will try again")
        elif result["status"] == "SUCCESS":
            print("\n✅ PLAN EXECUTED SUCCESSFULLY")


        # STOP if goal achieved
        if result["status"] == "SUCCESS" and goal_satisfied(goal, runtime_context):
            return result

        # ---- STEP 4B: FEEDBACK TO LLM ----
        if result["status"] == "BLOCKED":
            goal = f"""
            Your last plan was blocked because: {result.get('reason')}.
            You MUST perform check_inventory FIRST before attempting any refund.
            Now propose a new plan.
            """
            print("\n🔁 ASK BLOCKED THE PLAN — telling LLM to try again...\n")

        if result["status"] == "FAILED":
            goal = f"Your last plan failed during execution. Try a different approach to achieve: {goal}"
            print("\n🔁 PLAN FAILED — asking LLM to try a different strategy...\n")



    print("\n⚠️ MAX ITERATIONS REACHED — STOPPING")
    return {"status": "STOPPED", "reason": "max_iterations"}
