def oosd_lecture(week_number, today):
    lectures = [
        'Subject Introduction', #1
        'Java ‐ A Quick Tour',
        'Classes and Objects 1', #2
        'Classes and Objects 2',
        'Classes and Objects 3', #3
        'Arrays and Strings',
        'Input and Output', #4
        'Software Tools/Bagel',
        'Inheritance I', #5
        'Inheritance II',
        'Interfaces', #6
        'Revision',
        'Mid-Semester Test', #7
        'Class Diagrams',
        'Generics', #8
        'Collections and Maps',
        'Exceptions', #9
        'Design Patterns 1'
        'Design Patterns 2', #10
        'Software Testing and Design',
        'Asynchronous Programing', #11
        'Advanced Java Concepts',
        'Revision', #12
        'Wrapup - Exam'
    ]
    idx: int = (week_number-1)*2
    if (int(today.strftime("%w")) not in [0,1,5,6]):
        idx += 1
    return f'Lecture {idx+1} - {lectures[idx]}'

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
