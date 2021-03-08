from os import environ
from datetime import tzinfo, datetime
import dateutil.tz

from typing import Tuple

def get_timezone_details() -> Tuple[tzinfo, datetime]:
    timezone: tzinfo = dateutil.tz.gettz(environ.get('TIMEZONE_NAME')) or dateutil.tz.UTC
    today: datetime = datetime.now(tz=timezone) 
    # today: datetime = datetime(2021, 3, 9, tzinfo=timezone) 
    return timezone, today
