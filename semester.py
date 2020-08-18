from __future__ import annotations
from typing import Dict, Union, List

from datetime import datetime, tzinfo
import yaml

class Semester:
    """Stores details about a specific semester in the University year.
    All dates given are inclusive (i.e. Starts should be Mondays, and ends should be Sundays)."""
    def __init__(self, sem_start: datetime, sem_end: datetime, break_start: datetime, break_end: datetime) -> None:
        self.start: datetime = sem_start
        self.end: datetime = sem_end
        self.break_start: datetime = break_start
        self.break_end: datetime = break_end

    def __repr__(self) -> str:
        dtformat: str = "%b %d %Y"  
        return f'<Semester, {self.num_weeks}wks: {self.start.strftime(dtformat)} to {self.end.strftime(dtformat)} (break: {self.break_start.strftime(dtformat)} to {self.break_end.strftime(dtformat)})>'
    
    @property
    def num_weeks(self) -> int:
        return (self.end - self.start - (self.break_end - self.break_start)).days // 7

    @classmethod
    def from_yaml(cls, semester_yml_location: str, tzinfo: tzinfo) -> Semester:
        """Reads information from a YML file of the format (YYYY-MM-DD)
        ```txt
        start: 2020-08-03
        end:   2020-11-01
        break:
            start: 2020-10-05
            end:   2020-10-11
        ```
        """
        with open(semester_yml_location, 'r') as f:
            parsed: Dict[Union[str, dict]] = yaml.load(f, Loader=yaml.BaseLoader)
            timeformat: str = "%Y-%m-%d"
            dates: List[datetime] = [
                datetime.strptime(parsed['start'], timeformat),
                datetime.strptime(parsed['end'], timeformat),
                datetime.strptime(parsed['break']['start'], timeformat),
                datetime.strptime(parsed['break']['end'], timeformat),
            ]
            return cls(*[ datetime.replace(d, tzinfo=tzinfo) for d in dates ])
    
    def get_current_week(self, today: datetime) -> int:
        """Returns the current 1-indexed week number as an integer.
        If not in a semester, returns -1. If during midsem break, returns 0."""
        if (today < self.start or today > self.end):
            return -1 # Not in a teaching week.
        if (self.in_midsem_break(today)):
            return 0
        current_week: int = (today - self.start).days // 7 + 1 # 1-indexed
        if (today >= self.break_start): 
            current_week -= 1
        return current_week
    
    def in_midsem_break(self, today: datetime) -> bool:
        """Returns whether or not the given day falls in the midsem break of this semester."""
        return self.break_start <= today <= self.break_end

if __name__ == "__main__":
    from helpers import *
    timezone, today = get_timezone_details()
    print(
        Semester.from_yaml('./data/semester.yml', timezone)
    )