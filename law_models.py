from dataclasses import dataclass
from typing import List

@dataclass
class Law:
    id: str
    condition: str
    block_actions: List[str]
    reason: str
