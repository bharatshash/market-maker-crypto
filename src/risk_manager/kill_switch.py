from typing import Optional
from config import KILL_SWITCH_THRESHOLD

"""
    This module is used to immediately check for price fluctuations by a certain percentage threshold
    and then kill the bot if the fluctuation is beyond the threshold.
    
"""

class KillSwitch:
    def __init__(self, prev_price: Optional[float] = None):
        self.active: bool = False
        self.prev_price: Optional[float] = prev_price

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def is_active(self) -> bool:
        return self.active

    def check_kill(self, current_price: float) -> bool:
        if self.prev_price is None:
            self.prev_price = current_price
            return False

        price_change_pct = abs(current_price - self.prev_price) / self.prev_price * 100
        if price_change_pct > KILL_SWITCH_THRESHOLD: 
            self.prev_price = current_price
            self.activate()

        self.prev_price = current_price
        return False

# Global Kill Switch for forced shutdown
kill_switch = KillSwitch()