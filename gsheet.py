#!/usr/bin/python3
import hashlib
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

    def checksum(self):
        return hashlib.sha256("".join(i.checksum() for i in self.events).encode("utf-8")).hexdigest()
            

class Event(object):
    def __init__(self, name, restriction):
        self.name = name
        self.restriction = restriction

    def checksum(self):
        return hashlib.sha256(f"{self.name}{self.restriction}".encode("utf-8")).hexdigest()

    def __str__(self):
        return f"**{self.name}** - {self.restriction}"


def get_events(sheet):
    events = Events()

    for line in sheet[1:]:
        # Skip lines that start with ( they are basically just comments
        if line[0] and line[0][0] == "(":
            continue

        # Skip header lines
        if line[0] and line[0].isupper():
            continue

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
