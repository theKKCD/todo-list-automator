from __future__ import annotations
from typing import Dict, List
from datetime import datetime, tzinfo

import os

from todoist.api import TodoistAPI

from .semester import Semester
from .subjects import Subject, Task, read_yml_data
from .helpers  import get_timezone_details

# environment variables
TODOIST_API_TOKEN: str = os.environ['TODOIST_API_TOKEN']
TIMEZONE_NAME: str = os.environ['TIMEZONE_NAME']
DATA_LOCATION: str = os.environ['DATA_LOCATION']

api: TodoistAPI = TodoistAPI(TODOIST_API_TOKEN, cache='./tmp/todoist_cache')

def main(*args, **kwargs):
    api.sync()

    timezone: tzinfo
    today: datetime
    timezone, today = get_timezone_details()

    semester: Semester = Semester.from_yaml(os.path.join(DATA_LOCATION, 'semester.yml'), timezone)

    subjects: Dict[str, Subject]
    tasks: Dict[str, List[Task]]
    subjects, tasks = read_yml_data(os.path.join(DATA_LOCATION, 'data.yml'), semester)

    current_week: int = semester.get_current_week(today)
    if current_week == 0:
        message: str = "Not in semester. No tasks added."
        print(message)
        return { "message": message }

    added_tasks: Dict[str, List[str]] = dict( (subject.code, []) for subject in subjects.values() )

    for task in tasks[today.strftime("%A").lower()]:
        print(f'\nAttempting to add {task}...')
        if not task.is_in_week(current_week):
            print('  Skipped task, not in current week.')
            continue

        api_kwargs = {
                'project_id':   task.subject.project_id,
                'priority':     task.priority,
                'auto_parse_labels': True,
                'due': {
                    'string': task.get_due(),
                    'timezone': TIMEZONE_NAME,
                    'is_recurring': False,
                    'lang': 'en'
                }
            }

        task_name: str = task.get_name()
        task_added = api.items.add( task_name, **api_kwargs )

        added_tasks[task.subject.code].append(f"'{task_name}' due {task.get_due()}")
        print(f'  Added! ID={str(task_added.data["id"]).strip()}')
        
    response = api.commit()
    return {
        "today": today.strftime("%A"),
        "added_tasks": added_tasks,
        "api_response": response
    }

if __name__ == "__main__":
    main()
