from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime


class UsageRecord(BaseModel):
    project_id: str
    date: datetime
    daily_costs: Dict[str, float]  
    total_cost: float
    balance_before: float
    balance_after: float
    alerted: bool = Field(default=False)
