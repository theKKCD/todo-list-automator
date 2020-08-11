from datetime import date, datetime, time, tzinfo
import yaml

class Semester:
    """Stores details about a specific semester in the University year.
    All dates given are inclusive (i.e. Starts should be Mondays, and ends should be Sundays).
    """
    def __init__(self, sem_start: datetime, sem_end: datetime, break_start: datetime, break_end: datetime):
        self.start: datetime = sem_start
        self.end: datetime = sem_end
        self.break_start: datetime = break_start
        self.break_end: datetime = break_end
    
    @classmethod
    def from_yaml(cls, semester_yml_location: str, tzinfo: tzinfo):
        """Reads information from a YML file of the format (YYYY-MM-DD)
        ```
        start: 2020-08-03
        end:   2020-11-01
        break:
            start: 2020-10-05
            end:   2020-10-11
        ```
        """
        with open(semester_yml_location, 'r') as f:
            parsed = yaml.safe_load(f)
            return cls( datetime.combine(parsed['start'], time(), tzinfo=tzinfo),
                        datetime.combine(parsed['end'], time(), tzinfo=tzinfo),
                        datetime.combine(parsed['break']['start'], time(), tzinfo=tzinfo),
                        datetime.combine(parsed['break']['end'], time(), tzinfo=tzinfo) )
    
    def get_week_number(self, today: datetime) -> int:
        """Returns the current 1-indexed week number as an integer.
        If not in a semester, returns -1.
        If during midsem break, returns 0.
        """
        if (today < self.start or today > self.end):
            return -1 # Not in a teaching week.
        if (self.in_midsem_break(today)):
            return 0
        week_number: int = (today - self.start).days // 7 + 1 # 1-indexed
        if (today >= self.break_start): week_number -= 1
        return week_number
    
    def in_midsem_break(self, today: datetime) -> bool:
        """Returns whether or not the given day is in the midsem break"""
        return self.break_start <= today <= self.break_end
        