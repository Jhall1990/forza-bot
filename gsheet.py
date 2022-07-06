#!/usr/bin/python3
import gspread

AUTH = "config/auth.json"
SHEET_ID = "1mIJQIalcnsRUkwReVpmMlcaw17dYZtk-Xejwk_jSFJo"


class Events(object):
    def __init__(self):
        self.events = []

    def add_event(self, name, restrictions):
        self.events.append(Event(name, restrictions))

    def __str__(self):
        return "\n".join(str(i) for i in self.events)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __eq__(self, other):
        if not other:
            return False

        if len(self.events) != len(other.events):
            return False

        for idx, event in enumerate( self.events ):
            if event.name != other.events[idx].name:
                return False
            if event.restriction != other.events[idx].restriction:
                return False
        return True
            

class Event(object):
    def __init__(self, name, restriction):
        self.name = name
        self.restriction = restriction

    def __str__(self):
        return f"**{self.name}** - {self.restriction}"

def get_events(sheet):
    events = Events()

    for line in sheet[1:]:
        # We hit the end of the events section, that's all we care about, break
        if line[0].isupper():
            break

        if line[0]:
            events.add_event(line[0], line[1])
    return events

def get_sheet_from_google(auth, sheet_id):
    gc = gspread.service_account(filename=auth)
    sh = gc.open_by_key("1mIJQIalcnsRUkwReVpmMlcaw17dYZtk-Xejwk_jSFJo")
    return sh.sheet1.get_all_values()

def main():
    sheet_data = get_sheet_from_google(AUTH, SHEET_ID)
    return get_events(sheet_data)
