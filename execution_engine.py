"""Executes ActionPlans while enforcing laws and updating world state."""
from agent_models import ActionPlan
from law_enforcer import check_plan_legality, check_step_legality
from law_engine import TOOL_REGISTRY, LawViolation

def run_fallback(plan: ActionPlan):
    """Run fallback actions when a law is violated or a step fails."""
    for step in plan.fallback:
        tool_func = TOOL_REGISTRY[step.tool]
        tool_func(**step.input_schema)


def execute_plan(plan: ActionPlan, runtime_context: dict):
    """Execute an ActionPlan while enforcing laws and updating state."""
    try:
        # Check if plan is legal
        check_plan_legality(plan, runtime_context)

        # Run each legal action
        for step in plan.actions:
            check_step_legality(step, runtime_context)
            tool_func = TOOL_REGISTRY[step.tool]
            result = tool_func(**step.input_schema)

            # ---- WORLD UPDATE (keep this) ----
            if step.tool == "refund_order" and result.get("status") == "success":
                runtime_context["refund_done"] = True

            # Verify success
            if not result.get("status") == "success":
                raise RuntimeError("Step failed")

        return {
            "status": "SUCCESS",
            "context": runtime_context
        }

    except LawViolation as lv:
        run_fallback(plan)
        return {
            "status": "BLOCKED",
            "reason": str(lv),
            "context": runtime_context
        }

    except RuntimeError:
        run_fallback(plan)
        return {
            "status": "FAILED",
            "context": runtime_context
        }
