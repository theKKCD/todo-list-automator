def oosd_lecture(week_number, today):
    lectures = [
        'Subject Introduction',
        'Java ‐ A Quick Tour',
        'Classes and Objects 1',
        'Classes and Objects 2',
        'Classes and Objects 3',
        'Arrays and Strings',
        'Input and Output',
        'Software Tools/Bagel',
        'Inheritance I',
        'Inheritance II',
        'Interfaces',
        'Revision',
        'Mid-Semester Test',
        'Class Diagrams',
        'Generics',
        'Collections and Maps',
        'Exceptions',
        'Design Patterns 1'
        'Design Patterns 2',
        'Software Testing and Design',
        'Asynchronous Programing',
        'Advanced Java Concepts',
        'Revision',
        'Wrapup - Exam'
    ]
    idx: int = (week_number-1)*2
    if (int(today.strftime("%w")) not in [0,1,5,6]):
        idx += 1
    lname = lectures[idx]
    if not lname:
        return ''
    else:
        return f'Lecture {idx+1} - {lname}'

if __name__ == "__main__":
    from datetime import datetime, timezone, timedelta
    import dateutil.tz
    from main import semester_dates, get_week_number

    timezone_name = 'Australia/Melbourne'
    tz = dateutil.tz.gettz(timezone_name)
    today = datetime.now(tz=tz) # Can override this for testing
    week_number = get_week_number(today)

    print(f'Today | {today.strftime("%a %d %B %Y")}')
    print(f'OOSD  | {oosd_lecture(week_number, today)}')
