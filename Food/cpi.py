# Food/cpi.py
from typing import Dict, Any
from Food.cpi_model import blended_food_cpi
from Food.estimator import expected_monthly_food_cost  

def expected_food_inflation(eat_out_ratio: float = 0.2) -> float:
    """Return blended CPI decimal (e.g., 0.0143 = 1.43%)."""
    return blended_food_cpi(eat_out_ratio)

def expected_food_monthly_from_json(payload: Dict[str, Any]) -> float:
    """Return a single CAD monthly cost for the planner."""
    return expected_monthly_food_cost(payload)