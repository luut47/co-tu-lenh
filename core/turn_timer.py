class TurnTimer:
    def __init__(self, duration_seconds=60):
        self.duration_seconds = duration_seconds
        self.remaining_time = duration_seconds
        self.is_running = False

    def reset(self):
        self.remaining_time = self.duration_seconds

    def update(self, delta_time):
        """
        delta_time is the time elapsed in seconds.
        """
        if self.is_running:
            self.remaining_time -= delta_time
            if self.remaining_time < 0:
                self.remaining_time = 0

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def is_time_out(self):
        return self.remaining_time <= 0

    def get_time_string(self):
        # Format as "00:SS" where SS is 00 to 60
        seconds = int(self.remaining_time)
        return f"00:{seconds:02d}"
