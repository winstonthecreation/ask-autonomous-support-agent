import json
import re
from agent_models import ActionPlan, ActionStep

def validate_canonical_schema(plan_dict: dict) -> bool:
    """
    Returns True if the JSON matches our STRICT expected format:
    {
      "plan": [
        {"action": "...", "order_id": "..."}
      ]
    }
    """

    # Must have top-level "plan"
    if "plan" not in plan_dict:
        return False

    # plan must be a list
    if not isinstance(plan_dict["plan"], list):
        return False

    # Must contain at least one step
    if len(plan_dict["plan"]) == 0:
        return False

    first_step = plan_dict["plan"][0]

    # Each step must be a dict
    if not isinstance(first_step, dict):
        return False

    # Must contain "action" and "order_id"
    if "action" not in first_step or "order_id" not in first_step:
        return False

    return True

def normalize_tool_name(raw: str) -> str:
    if not raw:
        return "unknown_action"

    name = raw.lower()

    # REFUNDS
    if "refund" in name:
        return "refund_order"

    # INVENTORY
    if "inventory" in name or "stock" in name:
        return "check_inventory"

    # ORDER VERIFICATION
    if "verify" in name or "check_order" in name or "check order" in name:
        return "verify_order"

    # FALLBACK: make it a valid python-style name but keep meaning
    return name.replace(" ", "_")

def collect_inputs(step_dict: dict) -> dict:
    """
    Take EVERYTHING the LLM gave us that looks like an input,
    EXCEPT:
      - 'action' / 'Action'
      - 'description' / 'Description'
      - 'next_step' / variants
      - 'step' / 'Step' / 'StepNumber'
    """
    banned_keys = {
        "action", "Action",
        "description", "Description",
        "next_step", "next_steps", "NextStep", "Next_steps",
        "step", "Step", "StepNumber"
    }

    inputs = {}

    for k, v in step_dict.items():
        if k not in banned_keys:
            inputs[k] = v

    return inputs

def extract_json_from_text(text: str) -> str:
    match = re.search(r"```json(.*?)```", text, re.S)
    if match:
        return match.group(1).strip()
    return text.strip()

def llm_to_action_plan(raw_text: str) -> ActionPlan:
    """
    Convert messy LLM JSON output into your strict ASK ActionPlan.
    This function intentionally supports multiple possible LLM formats.
    """

    json_text = extract_json_from_text(raw_text)

    plan_dict = json.loads(json_text)
    # ---- STEP 5.1: STRICT SCHEMA CHECK FIRST ----
    if validate_canonical_schema(plan_dict):
        actions = []
        for step in plan_dict["plan"]:
            raw_tool = step["action"]
            tool_name = normalize_tool_name(raw_tool)

            inputs = {"order_id": step["order_id"]}

            actions.append(
                ActionStep(
                    tool=tool_name,
                    input_schema=inputs,
                    success_condition="result.get('status') == 'success'"
                )
            )

        order_id = plan_dict["plan"][0]["order_id"]

        return ActionPlan(
            goal=f"Execute plan for order {order_id}",
            preconditions=[],
            actions=actions,
            postconditions=[],
            fallback=[]
        )

    # ---- END STEP 5.1 ----


    if "ActionPlan" in plan_dict:
        ap = plan_dict["ActionPlan"]

        order_id = (
            ap.get("order_id")
            or ap.get("orderID")
            or ap.get("OrderID")
            or ap.get("orderId")
        )

        step_list = (
           ap.get("actions")
           or ap.get("Actions")
           or ap.get("steps")
           or ap.get("Steps")
           or []
        )


        actions = []

        for step in step_list:
            tool_name = (
                step.get("action")
                or step.get("Action")
                or step.get("description")
                or step.get("Description")
                or step.get("task")
                or step.get("Task")
                or ""
            )

            tool_name = normalize_tool_name(tool_name)
            
            inputs = {}
            if order_id is not None:
                inputs["order_id"] = order_id

            actions.append(
                ActionStep(
                    tool=tool_name,
                    input_schema=inputs,
                    success_condition="result.get('status') == 'success'"
                )
            )


        return ActionPlan(
            goal=f"Process workflow for order {order_id}",
            preconditions=[],
            actions=actions,
            postconditions=[],
            fallback=[]
        )

    if "actionPlan" in plan_dict:
        ap = plan_dict["actionPlan"]

        order_id = ap.get("order_id") or ap.get("orderID") or ap.get("orderId")

        actions = [
            ActionStep(
                tool=ap.get("action", "unknown_action"),
                input_schema={"order_id": order_id},
                success_condition="result.get('status') == 'success'"
            )
        ]

        return ActionPlan(
            goal=f"Execute {ap.get('action', 'unknown_action')} for order {order_id}",
            preconditions=[],
            actions=actions,
            postconditions=[],
            fallback=[]
        )

    if "actions" in plan_dict:
        actions = []
        for a in plan_dict["actions"]:
            actions.append(
                ActionStep(
                    tool=a["tool"],
                    input_schema=a["inputs"],
                    success_condition=a["success_condition"]
                )
            )

        return ActionPlan(
            goal=plan_dict["goal"],
            preconditions=[],
            actions=actions,
            postconditions=[],
            fallback=[]
        )

    if "plan" in plan_dict and isinstance(plan_dict["plan"], list):
        actions = []
         # NEW: start with known order_id from runtime_context IF AVAILABLE
        order_id = plan_dict.get("order_id")  # may be None

        for step in plan_dict["plan"]:

            raw_tool = step.get("action", "")
            tool_name = normalize_tool_name(raw_tool)

            inputs = collect_inputs(step)

            if tool_name in {"check_inventory", "refund_order", "verify_order"}:
                if "order_id" not in inputs:
                    if order_id is None:
                        raise ValueError("order_id required but missing")
                    inputs["order_id"] = order_id
            
            if "order_id" in inputs:
                order_id = inputs["order_id"]

            if order_id is not None and "order_id" not in inputs:
                inputs["order_id"] = order_id


            actions.append(
                ActionStep(
                    tool=tool_name,
                    input_schema=inputs,
                    success_condition="result.get('status') == 'success'"
                )
            )

    # 4) Safer goal (works even if order_id is None)
        goal_text = (
            f"Execute plan for order {order_id}"
            if order_id is not None
            else "Execute plan"
        )

        return ActionPlan(
            goal=goal_text,
            preconditions=[],
            actions=actions,
            postconditions=[],
            fallback=[]
        )

    raise ValueError(f"Unrecognized LLM plan format: {plan_dict}")
