from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ActionStep:
    tool: str
    input_schema: Dict[str, any]
    success_condition: str


@dataclass
class ActionPlan:
    goal: str
    preconditions: List[str]
    actions: List[ActionStep]
    postconditions: List[str]
    fallback: List[ActionStep]
