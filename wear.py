# this script could read dressing time data and dress data from a json file
# and return what should today, and tomorrow wear following the instructions

import json
import datetime


class Wear:
    def __init__(self, config_file='wear_config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    # json file will have flowing data structure
    # {
    #   "day": "2025-11-15",
    #   "wear": "WINS"
    # }

    
    def get_wear_for_date(self, date):
        date_str = date.strftime('%Y-%m-%d')
        wear_info = self.config.get(date_str, {})
        return wear_info.get('today'), wear_info.get('tomorrow')

    def display_wear(self, date):
        today_wear, tomorrow_wear = self.get_wear_for_date(date)
        print(f"Wear for {date.strftime('%Y-%m-%d')}:")
        print(f"  Today: {today_wear if today_wear else 'you are free to choose'}")
        print(f"  Tomorrow: {tomorrow_wear if tomorrow_wear else 'you are free to choose'}")

if __name__ == "__main__":
    wear = Wear()
    today = datetime.date.today()
    wear.display_wear(today)