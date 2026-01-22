class killSwitch:
    def __init__(self, prev_price=None):
        self.active = False
        self.prev_price = prev_price

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def is_active(self):
        return self.active

    def check_kill(self, current_price):
        if self.prev_price is None:
            self.prev_price = current_price
            return False

        price_change_pct = abs(current_price - self.prev_price) / self.prev_price * 100
        if price_change_pct > 5: 
            self.prev_price = current_price
            self.activate()

        self.prev_price = current_price

# Global Kill Switch for forced shutdown
kill_switch = killSwitch()