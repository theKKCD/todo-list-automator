from __future__ import annotations
from typing import Dict, List, Callable, Tuple, Union

from datetime import datetime, tzinfo
from collections import defaultdict

from helpers import *
from semester import Semester

import yaml

class Subject:
    def __init__(self, code: str, name: str, project_id: int, semester: Semester) -> None:
        self.code: str = code
        self.name: str = name.lower()
        self.project_id: int = project_id
        self.semester: Semester = semester
    
    def __repr__(self) -> str:
        return f'<Subject: {self.code} ({self.name}); ID: {self.project_id}>'

    @classmethod
    def dict_from_yml(cls, data_yml_location: str, semester: Semester) -> Dict[str, Subject]:
        """Reads information from a YML file of the format (YYYY-MM-DD)
        ```
        subjects:
          - code: (string) // unique id used to match tasks with projects
            name: (string) // human-readable string, used in logs
            project_id: (int) // from Todoist API
        ```
        """
        with open(data_yml_location, 'r') as f:
            yml_data: dict = yaml.safe_load(f)
            return cls.dict_from_yml_data(yml_data['subjects'], semester)
    
    @classmethod
    def dict_from_yml_data(cls, yml_data_subjects: list, semester: Semester) -> Dict[str, Subject]:
        return dict((subject_dict['code'].lower(), cls(**subject_dict, semester=semester)) 
                    for subject_dict in yml_data_subjects)

class Task:  
    def __init__(self, subject: Subject, time: str, due_day: str ='', name: str = '', weeks: List[int] = [],
                 exclude_weeks: bool = False, priority: int = 1, name_func: Callable[[int, datetime, str], str] = None,
                 subtasks: List[Task] = [], section_id: int = 0) -> None:
        self.subject: Subject = subject
        self.__due: Tuple[str, str] = (due_day or 'Today', time)
        self.priority: int = max(min(priority, 4), 1)
        # accessed through get_name() -> str
        self.__task_name: str = name
        self.__name_func: Union[Callable[[int, datetime, str], str], None] = name_func
        # accessed through is_in_week() -> bool
        self.__weeks: List[int] = weeks
        self.__exclude_weeks: bool = exclude_weeks
        # subtasks
        self.parent: Task = None
        self.subtasks: List[Task] = subtasks
        for subtask in subtasks:
            assert not subtask.parent
            subtask.parent = self
        self.api_id: str = ''
        self.__section_id: str = section_id
    
    def __repr__(self):
        string: str = f'Task: {self.subject.code} \'{self.get_name()}\' due {self.get_due()}'
        if self.__weeks:
            string += f' ({"not in" if self.__exclude_weeks else "in"} weeks {self.__weeks})'
        return f'<{string}>'
    
    @property
    def is_subtask(self) -> bool:
        return (self.parent is not None)

    def get_name(self) -> str:
        today: datetime = get_timezone_details()[1]
        if self.__name_func is not None:
            current_week = self.subject.semester.get_current_week(today)
            return self.__name_func(current_week, today, self.__due[0].replace('Today', ''))
        name: str = self.__task_name or "Class"
        if self.__due[0] == 'Today':
            name += f', {today.strftime("%a %d %B")}'
        return name
    
    def get_due(self) -> str:
        return ' '.join(self.__due)

    def is_in_week(self, current_week: int) -> bool:
        if not self.__weeks:
            return True
        in_weeks = int(current_week) in self.__weeks
        if self.__exclude_weeks:
            return not in_weeks
        return in_weeks
    
    def add_subtask(self, subtask: Task) -> None:
        assert not subtask.parent
        subtask.parent = self
        self.subtasks.append(subtask)

    @classmethod
    def from_yml_data(cls, yml_data_task: dict, subjects: Dict[str, Subject], generators: Dict[str, Callable[[int, datetime], str]]):
        """A task has the following form:
        ```yml
        - subject:        #(string. subject code) [REQUIRED]
          name:           #(string. if empty, generator is used)
          time:           #(string. when is this due? e.g. 2:15pm)
          due_day:        #(string. human readable e.g. 'Next Monday')
          weeks:          #(List[int]. The weeks in which the task should/shoudln't be added)
          exclude_weeks:  #(bool. given weeks are excluded if true)
          priority:       #(int. 1 is lowest, 4 is highest)
          name_generator: #(string. identifier of  generator)
          subtasks:       #(list of tasks, subject not required)
            - name: ...
              ...
        ```"""
        if not isinstance(yml_data_task['subject'], Subject):
            yml_data_task['subject'] = subjects[ yml_data_task['subject'].lower() ]
        # name_generator: str
        if name_generator := yml_data_task.get('name_generator'):
            yml_data_task['name_func'] = generators[name_generator]
            del yml_data_task['name_generator']
        # subtasks: List[dict]
        if subtasks := yml_data_task.get('subtasks'):
            yml_data_task['subtasks'] = []
            for subtask in subtasks:
                subtask['subject'] = yml_data_task['subject']
                yml_data_task['subtasks'].append(cls.from_yml_data(subtask, subjects, generators))
            # yml_data_task['subtasks'] = [ cls.from_yml_data(subtask.update({'subject': yml_data_task['subject']}), subjects, generators) for subtask in subtasks ] # List[Task]
        return cls(**yml_data_task)

    def api_add_task(self: Task, api: TodoistAPI, current_week: int, timezone_name: str) -> defaultdict[str, List[str]]:
        """Adds tasks to the API, and recursively adds the subtasks of a given task."""
        added_tasks: defaultdict[str, List[str]] = defaultdict(list)
        task_name: str = self.get_name()

        if not self.is_in_week(current_week) or not task_name:
            return

        api_kwargs: Dict = {
            'priority': self.priority,
            'auto_parse_labels': True,
            'due': {
                'string': self.get_due(),
                'timezone': timezone_name,
                'is_recurring': False,
                'lang': 'en'
            }
        }
        # Note, we only add subtasks to existing tasks
        if self.is_subtask:
            api_kwargs['parent_id'] = self.parent.api_id
        else:
            api_kwargs['project_id'] = self.subject.project_id
        
        if self.__section_id > 0:
            api_kwargs['section_id'] = self.__section_id

        task_added = api.items.add( task_name, **api_kwargs )
        self.api_id = str(task_added.data["id"])
        added_tasks[self.subject.code].append(f"'{task_name}' due {self.get_due()}")

        # if self.subtasks != []
        for subtask in self.subtasks:
            subtasks: defaultdict[str, List[str]] = subtask.api_add_task(api, current_week, timezone_name)
            for subject_code, tasks in subtasks.items():
                added_tasks[subject_code] += tasks

        return added_tasks

def read_yml_data(data_yml_location: str, semester: Semester) -> Tuple[Dict[str, Subject], Dict[str, List[Task]]]:
    with open(data_yml_location, 'r') as f:
        yml_data: dict = yaml.safe_load(f)
        subject_data: list = yml_data['subjects']
        task_data: Dict[str, List] = yml_data['tasks']
        
        generator_data: Union[Dict[str, Dict], None] = yml_data.get('task_name_generators')
        generators: Dict[str, Callable[[int, datetime, str], str]] = {}
        if generator_data:
            for (generator_name, info) in generator_data.items():
                generators[generator_name] = name_factory_factory(info)

        subjects: Dict[str, Subject] = Subject.dict_from_yml_data(subject_data, semester)
        tasks: Dict[str, List[Task]]  = dict(
            (day_name.lower(),  [ Task.from_yml_data(task, subjects, generators) for task in task_list ])
            for day_name, task_list in task_data.items()
        )
        print(tasks['tuesday'])
        return (subjects, tasks)

def name_factory_factory(info: Dict) -> Callable[[int, datetime, str], str]:
    def func(current_week: int, today: datetime, due_day: str = '') -> str:
        new_due_day: str = (due_day or today.strftime("%A")).lower().replace('next', '').strip()
        due_next_week: bool = \
            'next' in due_day.lower() \
            or int(today.strftime('%w').lower()) >= int(datetime.strptime(new_due_day.title(), '%A').strftime('%w'))
        incr: int
        try:
            incr = [day.lower() for day in info.get('days_of_week')].index(new_due_day)
        except ValueError:
            incr = 0
        idx: int = (current_week - 1 + int(due_next_week)) \
                * (len(info.get('days_of_week', '1'))) \
                + incr
        class_number: int = idx + 1 - info['list'][:idx].count('');
        return f"{info.get('prefix','').strip()}{' '+str(class_number) if info.get('num_after_prefix') else ''} - {info['list'][idx]}{today.strftime(', %a %d %B') if info.get('use_date') else ''}" \
            if info['list'][idx] else ''
    return func
