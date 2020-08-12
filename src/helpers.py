from os import environ
from datetime import tzinfo, datetime
import dateutil.tz

from typing import Tuple
from enum import Enum

def get_timezone_details() -> Tuple[tzinfo, datetime]:
    timezone: tzinfo = dateutil.tz.gettz(environ.get('TIMEZONE_NAME')) or dateutil.tz.UTC
    today: datetime = datetime.now(tz=timezone)
    return timezone, today
