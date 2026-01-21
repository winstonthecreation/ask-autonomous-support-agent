from law_models import Law
from agent_models import ActionPlan
from law_engine import LawViolation

# Simple in-memory law book
LAW_BOOK = []


def add_law(law: Law):
    LAW_BOOK.append(law)


def check_plan_legality(plan: ActionPlan, runtime_context: dict):
    for law in LAW_BOOK:
        field, op, value = law.condition.split()

        actual = runtime_context.get(field)

        if actual is None:
            continue

        violated = False

        if op == ">" and actual > int(value):
            violated = True
        elif op == "<" and actual < int(value):
            violated = True
        elif op == "==" and str(actual) == value:
            violated = True
        elif op == "!=" and str(actual) != value:
            violated = True

        if violated:
            # ONLY block if the FIRST step is illegal (naked refund)
            first_tool = plan.actions[0].tool
            if first_tool in law.block_actions:
                raise LawViolation(law.reason)

    return True

def check_step_legality(step, runtime_context: dict):
    for law in LAW_BOOK:
        field, op, value = law.condition.split()

        actual = runtime_context.get(field) or step.input_schema.get(field)

        if actual is None:
            continue

        violated = False

        if op == ">" and actual > int(value):
            violated = True
        elif op == "<" and actual < int(value):
            violated = True
        elif op == "==" and str(actual) == value:
            violated = True
        elif op == "!=" and str(actual) != value:
            violated = True

        # THIS is the key difference from check_plan_legality:
        if violated and step.tool in law.block_actions:
            raise LawViolation(law.reason)

    return True
