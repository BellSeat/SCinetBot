# Schedule module for provide students help desk shift 
# it is sub module of tg.py

import json
import datetime
from zoneinfo import ZoneInfo
class Shift:
    def __init__(self,today=None,start_time=None, end_time=None, student1=None, student2=None):
        self.today = today
        self.start_time = start_time
        self.end_time = end_time
        self.student1 = student1
        self.student2 = student2
    
    def set_values(self, today, start_time, end_time, student1, student2):
        self.today = today
        self.start_time = start_time
        self.end_time = end_time
        self.student1 = student1
        self.student2 = student2
    
    def get_value(self):
        return {
            'today': self.today,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'student1': self.student1,
            'student2': self.student2
        }
    def valid_shift(self):
        return all([self.today, self.start_time])

class Schedule:
    def __init__(self, config_file='schedule_config.json', timezone='America/Chicago'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.timezone = ZoneInfo(timezone)

   # json file will have flowing data structure
   # {
   #   "day": "2025-11-14",
    #   "shifts": {
    #       "08:00-10:00":{"student1": "Alice", "student2": "Bob"},
    #       "10:00-12:00":{"student1": "Charlie", "student2": "David"}
    #   }
    # }
    def get_schedule_for_date(self, date):
        date_str = date.strftime('%Y-%m-%d')
        return self.config.get(date_str, {}).get('shifts', {})
    
    # get current shift based on current time return student1 and student2
    def get_current_shift(self):
        # initial shift class
        
        now = datetime.datetime.now(self.timezone)
        current_time_str = now.strftime('%H:%M')
        shifts = self.get_schedule_for_date(now.date())

        for time_range, students in shifts.items():
            start_time, end_time = time_range.split('-')
            # Current shift: start_time <= current < end_time (exclusive end)
            if start_time <= current_time_str < end_time:
                shift = Shift(today=now.date(), start_time=start_time, end_time=end_time, student1=students['student1'], student2=students['student2'])
                return shift
        return None
    
    # get last shift based on current time return a Shift class instance
    def get_last_shift(self):
        now = datetime.datetime.now(self.timezone)
        current_time_str = now.strftime('%H:%M')
        shifts = self.get_schedule_for_date(now.date())

        last_shift_end = None
        last_shift_start = None
        last_students = None

        for time_range, students in shifts.items():
            start_time, end_time = time_range.split('-')
            # Last shift: end_time <= current (completed shifts)
            if end_time <= current_time_str:
                if last_shift_end is None or end_time > last_shift_end:
                    last_shift_end = end_time
                    last_shift_start = start_time
                    last_students = students

        if last_shift_end:
            return Shift(today=now.date(), start_time=last_shift_start, end_time=last_shift_end, student1=last_students['student1'], student2=last_students['student2'])
        return None
    # get next shift based on current time return a Shift class instance
    def get_next_shift(self):
        now = datetime.datetime.now(self.timezone)
        date_str = now.strftime('%Y-%m-%d')
        current_time_str = now.strftime('%H:%M')
        shifts = self.get_schedule_for_date(now.date())
        
        for time_range, students in shifts.items():
            start_time, end_time = time_range.split('-')
            if start_time >= current_time_str:
                return Shift(today=now.date(), start_time=start_time, end_time=end_time, student1=students['student1'], student2=students['student2'])
        return None
    
    def display_schedule(self, date):
        shifts = self.get_schedule_for_date(date)
        print(f"Schedule for {date.strftime('%Y-%m-%d')}:")
        for time_range, students in shifts.items():
            print(f"  {time_range}: Student1 - {students['student1']}, Student2 - {students['student2']}")
    