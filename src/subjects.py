from __future__ import annotations
from typing import Dict, List, Callable, Tuple, Union

from datetime import datetime, tzinfo

from .helpers import *
from .semester import Semester

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
                 exclude_weeks: bool = True, priority: int = 1, name_func: Callable[[int, datetime], str] = None) -> None:
        self.subject: Subject = subject
        self.__due: Tuple[str, str] = (due_day or 'Today', time)
        self.priority: int = max(min(priority, 4), 1)
        # accessed through get_name() -> str
        self.__task_name: str = name
        self.__name_func: Union[Callable[[int, datetime], str], None] = name_func
        # accessed through is_in_week() -> bool
        self.__weeks: List[int] = weeks
        self.__exclude_weeks: bool = exclude_weeks
    
    def __repr__(self):
        string: str = f'Task: {self.subject.code} \'{self.__task_name}\' due {self.get_due()}'
        if self.__weeks:
            string += f' ({"not in" if self.__exclude_weeks else "in"} weeks {self.__weeks})'
        return f'<{string}>'
    
    def get_name(self) -> str:
        today: datetime = get_timezone_details()[1]
        if self.__name_func is not None:
            current_week = self.subject.semester.get_current_week(today)
            return self.__name_func(current_week, today)
        return f'{self.__task_name or "Class"}, {today.strftime("%a %d %B")}'
    
    def get_due(self) -> str:
        return ' '.join(self.__due)

    def is_in_week(self, current_week: int) -> bool:
        if not self.__exclude_weeks:
            return current_week in self.__weeks
        return current_week not in self.__weeks
    
    @classmethod
    def from_yml_data(cls, yml_data_task: dict, subjects: Dict[str, Subject]):
        """A task has the following form:
        ```yml
        - subject:        #(string. subject code) [REQUIRED]
          name:           #(string. if empty, generator is used)
          time:           #(string. when is this due? e.g. 2:15pm)
          due_day:        #(string. human readable e.g. 'Next Monday')
          weeks:          #(List[int]. The weeks in which the task should/shoudln't be added)
          exclude_weeks:  #(bool. given weeks are excluded if true)
          priority:       #(int. 1 is lowest, 4 is highest)
        #   task_gen_list:  #(string. identifier of `name_list` used as  generator)
        ```"""
        yml_data_task['subject'] = subjects[ yml_data_task['subject'].lower() ]
        return cls(**yml_data_task)

def read_yml_data(data_yml_location: str, semester: Semester) -> Tuple[Dict[str, Subject], Dict[str, List[Task]]]:
    with open(data_yml_location, 'r') as f:
        yml_data: dict = yaml.safe_load(f)
        subject_data: list = yml_data['subjects']
        task_data: dict[str, List] = yml_data['tasks']
        subjects: Dict[str, Subject] = Subject.dict_from_yml_data(subject_data, semester)
        tasks: Dict[str, List[Task]]  = dict(
            (day_name.lower(),  [ Task.from_yml_data(task, subjects) for task in task_list ])
            for day_name, task_list in task_data.items()
        )
        return (subjects, tasks)

