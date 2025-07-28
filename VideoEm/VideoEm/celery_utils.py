from celery.schedules import schedule


class ImmediateThenHourly(schedule):
    """Runs immediately on first call, then hourly."""
    def is_due(self, last_run_at):
        if last_run_at is None:
            return True, self.seconds
        return super().is_due(last_run_at)