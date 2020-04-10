class Timer:
    current_delay = 0
    max_delay = 0

    def __init__(self, max_delay):
        self.current_delay = self.max_delay = max_delay

    def tick(self):
        self.current_delay = max(0, self.current_delay - 1)

    def is_ready(self):
        return self.current_delay <= 0

    def reset(self):
        self.current_delay = self.max_delay

    def set(self, value):
        self.current_delay = value
