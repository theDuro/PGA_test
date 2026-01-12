from pydantic import BaseModel
from typing import Optional

class ProductionData(BaseModel):
    sheet_width: Optional[float]
    sheet_thickness: Optional[float]
    rolling_force: Optional[float]
    motor_power: Optional[float]
    line_speed: Optional[float]
    process_time: Optional[float]