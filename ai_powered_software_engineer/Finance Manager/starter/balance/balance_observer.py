# balance_observer.py


class IBalanceObserver:
    def update(self, balance, transaction):
        """Handle balance updates."""
        raise NotImplementedError("Subclasses must implement update method.")


class PrintBalance(IBalanceObserver):
    def update(self, balance, transaction):
        """Print balance update message."""
        print(f"{transaction} -> new balance: ${balance}")


class LowBalanceAlertObserver(IBalanceObserver):
    def __init__(self, threshold):
        self.threshold = threshold
        self.alert_triggered = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        if balance < self.threshold:
            self.alert_triggered = True
            print(
                f"Low balance alert: ${balance} "
                f"is below threshold of ${self.threshold}"
            )
        else:
            self.alert_triggered = False
