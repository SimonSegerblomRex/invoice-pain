import calendar
import datetime

import holidays


class BankDays:

    """..."""

    def __init__(self, country):
        self.national_holidays = holidays.country_holidays(country)

    def next_bank_day(self):
        """..."""
        candidate_date = datetime.date.today()
        while True:
            candidate_date += datetime.timedelta(days=1)
            if candidate_date.weekday() > 4:
                continue
            if candidate_date in self.national_holidays:
                continue
            return candidate_date

    def last_bank_day_of_current_month(self):
        """..."""
        today = datetime.date.today()
        for day in range(*reversed(calendar.monthrange(today.year, today.month)), -1):
            candidate_date = datetime.date(today.year, today.month, day)
            if candidate_date.weekday() > 4:
                continue
            if candidate_date in self.national_holidays:
                continue
            break
        else:
            raise ValueError("No bank days left in current month")
        return candidate_date
