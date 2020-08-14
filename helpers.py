from os import environ
from datetime import tzinfo, datetime
import dateutil.tz

from typing import Tuple

def get_timezone_details() -> Tuple[tzinfo, datetime]:
    timezone: tzinfo = dateutil.tz.gettz(environ.get('TIMEZONE_NAME')) or dateutil.tz.UTC
    today: datetime = datetime.now(tz=timezone) # datetime(2020, 8, 17, tzinfo=timezone) 
    return timezone, today
