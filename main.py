from __future__ import annotations
from typing import Dict, List
from datetime import datetime, tzinfo

import os
from collections import defaultdict

from todoist.api import TodoistAPI

from semester import Semester
from subjects import Subject, Task, read_yml_data
from helpers  import get_timezone_details

# environment variables
TODOIST_API_TOKEN: str = os.environ['TODOIST_API_TOKEN']
TIMEZONE_NAME: str = os.environ['TIMEZONE_NAME']
DATA_LOCATION: str = os.environ['DATA_LOCATION']

def main(*args, **kwargs):
    api: TodoistAPI = TodoistAPI(TODOIST_API_TOKEN, cache='/tmp/todoist_cache')
    api.sync()

    timezone: tzinfo
    today: datetime
    timezone, today = get_timezone_details()

    semester: Semester = Semester.from_yaml(os.path.join(DATA_LOCATION, 'semester.yml'), timezone)

    subjects: Dict[str, Subject]
    tasks: Dict[str, List[Task]]
    subjects, tasks = read_yml_data(os.path.join(DATA_LOCATION, 'data.yml'), semester)

    current_week: int = semester.get_current_week(today)
    print("Current week:", current_week)
    if current_week == 0:
        message: str = "Not in semester. No tasks added."
        print(message)
        return { "message": message }

    added_tasks: defaultdict[str, List[str]] = defaultdict(list)
    for task in tasks[today.strftime("%A").lower()]:
        if task_dict := task.api_add_task(api, current_week, TIMEZONE_NAME):
            for subject_code, tasks in task_dict.items():
                added_tasks[subject_code] += tasks
        
    response = api.commit()
    return {
        "today": today.strftime("%A"),
        "week": current_week,
        "added_tasks": added_tasks,
        # "api_response": response
    }

if __name__ == "__main__":
    main()
