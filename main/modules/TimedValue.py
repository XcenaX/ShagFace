import datetime

class TimedValue:
    def __init__(self, time):
        self._started_at = datetime.datetime.utcnow()
        self.time = time

    def has_time_passed(self):
        time_passed = datetime.datetime.utcnow() - self._started_at
        if time_passed.total_seconds() > self.time:
            return True
        return False