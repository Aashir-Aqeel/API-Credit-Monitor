from pydantic import BaseModel
from datetime import datetime
from typing import Dict

class UsageRecord(BaseModel):
    project_id: str
    date: datetime
    daily_costs: Dict[str, float]
    total_cost: float
    balance_before: float
    balance_after: float
    alerted: bool
