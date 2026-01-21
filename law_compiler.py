from law_language import parse_law_script
from law_models import Law
import hashlib


def compile_law(text: str) -> Law:
    # 1) Parse the human LawScript
    parsed = parse_law_script(text)

    # 2) Create a short unique id for this law
    law_id = hashlib.sha256(text.encode()).hexdigest()[:8]

    # 3) Build and return a Law object
    return Law(
        id=law_id,
        condition=f"{parsed['field']} {parsed['operator']} {parsed['value']}",
        block_actions=[parsed["tool"]],
        reason=parsed["reason"]
    )
