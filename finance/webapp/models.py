from uuid import uuid4
from dataclasses import dataclass, field


@dataclass
class ChangeStoreModel:

    budget_idx: int = None
    correlation: str = field(default_factory=lambda: str(uuid4()))
