import os
from datetime import date, datetime, time, tzinfo
import dateutil.tz

from enum import Enum

from todoist.api import TodoistAPI

from .semester import Semester

# environment variables
TODOIST_API_TOKEN: str = os.environ['TODOIST_API_TOKEN']
TIMEZONE_NAME: str = os.environ['TIMEZONE_NAME']
DATA_LOCATION: str = os.environ['DATA_LOCATION']

api: TodoistAPI = TodoistAPI(TODOIST_API_TOKEN, cache='./tmp/todoist_cache')

timezone: tzinfo = dateutil.tz.gettz(TIMEZONE_NAME) or dateutil.tz.UTC
today: datetime = datetime.now(tz=timezone) # Can override this for testing

class Weekday(Enum):
    Monday = 'Monday'
    Tuesday = 'Tuesday'
    Wednesday = 'Wednesday'
    Thursday = 'Thursday'
    Friday = 'Friday'
    Saturday = 'Saturday'
    Sunday = 'Sunday'

def week_array(weeks, exclude=False):
    m = lambda x: (not x+1 in weeks) if exclude else (x+1 in weeks)
    return [ m(x) for x in range(12) ]

def Subject(project_id: int, lecture_section: int=None):
    return {
        'project_id': project_id,
        'lecture_section': lecture_section
    }

def Task(subject, time, weeks=[True for _ in range(12)], task_type='Lecture', due='', priority=1, name_factory=None):
    return {
        'subject': subject,
        'time': time,
        'weeks': weeks,
        'type': task_type,
        'due': due,
        'priority': priority,
        'name_factory': name_factory
    }


def main(*args, **kwargs):
    from .name_funcs import oosd_lecture
    api.sync()

    semester: Semester = Semester.from_yaml(os.path.join(DATA_LOCATION, 'semester.yml'), timezone)

    # Input Data Here
    elen20005 = Subject(2241095310)
    swen20003 = Subject(2241095301)
    mast20026 = Subject(2241095303)
    ling20010 = Subject(2241095316)
    
    tasks_by_day = {
        Weekday.Monday: [
            Task(swen20003, '11:00am', name_factory=oosd_lecture),
            Task(mast20026, '2:15pm', task_type='Prerecorded Lecture'),
            Task(ling20010, '2:15pm', task_type='Live Lecture'),
            Task(elen20005, '3:15pm', task_type='Live Concepts/Intuition Lecture')
        ],
        Weekday.Tuesday: [
            Task(elen20005, '11:00am', task_type='Prerecorded Lecture'),
            Task(elen20005, '3:15pm', task_type='Quiz', weeks=week_array([5,7,9,10,12]))
        ],
        Weekday.Wednesday: [
            Task(mast20026, '9:00am', task_type='Prerecorded Lecture'),
            Task(elen20005, '11:00am', task_type='Prerecorded Lecture'),
            Task(ling20010, '11:00am', task_type='Tutorial'),
            Task(elen20005, '3:15pm', task_type='Workshop'),
            Task(swen20003, '2:15pm', name_factory=oosd_lecture),
        ],
        Weekday.Thursday: [
            Task(ling20010, '12:00pm', task_type='Live Lecture'),
            Task(swen20003, '1:00pm', task_type='Practical'),
        ],
        Weekday.Friday: [
            Task(mast20026, '10:00am', task_type='Prerecorded Lecture'),
            Task(elen20005, '2:15pm', task_type='Live Examples Lecture')
        ],
        Weekday.Saturday: [],
        Weekday.Sunday: []
    }

    week_number = semester.get_week_number(today)
    if week_number == 0:
        return {
            "message": "Not in semester. No tasks added."
        }

    added_tasks = []

    for task in tasks_by_day[Weekday(today.strftime("%A"))]:
        if (not task.get('weeks', (False for _ in range(12)))[week_number]):
            continue
        
        task_name = (task.get('name_factory') or (lambda _,today: f'{task.get("type", "Class")}, {today.strftime("%a %d %B")}'))(week_number, today)
        arguments = {
            'project_id': task['subject']['project_id'],
            'section_id': task['subject']['lecture_section'] if task['type'] in ['Lecture', 'Seminar'] else task.get('section_id', None),
            'priority': task.get('priority', 1),
            'auto_parse_labels': True,
            'due': {
                'string': f"{task.get('due', 'Today')} at {task.get('time', '12pm')}",
                "timezone": TIMEZONE_NAME,
                "is_recurring": False,
                "lang": "en"
            }
        }
        added_task = api.items.add(task_name, **arguments)
        api.commit()
        added_tasks.append(added_task)
        print(f"Added ID {added_task.data['id']} {added_task.data['content']}")

    return {
        "today": Weekday(today.strftime("%A")).name,
        "added_tasks": str(added_tasks)
    }

if __name__ == "__main__":
    main()
