#!/usr/bin/python3

import csv
import sys
import random
import discord

"""
TODO: Some new commands
help show commands
list types - show the types
list <type> - show all cars in that type
random-car - pick a random car
random-car <type> - pick a random car from the type
"""

CAR_CSV = "cars.csv"
TRACK_CSV = "tracks.csv"
PI_CLASSES = ["D", "C", "B", "A", "S1", "S2", "X"]
RACE_TYPES = ["RALLY", "STREET", "OFFROAD"]
TRACK_IMAGE = "https://cdn.guides4gamers.com/sites/28/screenshots/2021/12/1920/{}.jpg"

with open("config/token.txt", "r") as token_file:
    TOKEN = token_file.read().strip()

if not TOKEN:
    sys.exit( "No discord token found" )


class Car(object):
    def __init__(self, year, make, model, value, rarity, speed, handle, accel, launch, brake, offroad, pi, car_type):
        self.year = year.strip()
        self.make = make.strip()
        self.model = model.strip()
        self.value = value.strip()
        self.rarity = rarity.strip()
        self.speed = speed.strip()
        self.handle = handle.strip()
        self.accel = accel.strip()
        self.launch = launch.strip()
        self.brake = brake.strip()
        self.offroad = offroad.strip()
        self.pi = pi.strip()
        self.pi_class = self.parse_pi()
        self.car_type = car_type.lower()

    def __str__(self):
        return f"{self.year} {self.make} {self.model} {self.pi} {self.value}cr"

    def parse_pi(self):
        if self.pi.startswith(("D", "C", "B", "A", "X")):
            return self.pi[0]
        elif self.pi.startswith(("S1", "S2")):
            return self.pi[0:2]
        return "X"

    @staticmethod
    def from_csv_row(row):
        return Car(*row)

class Track(object):
    def __init__(self, name, surface, type_):
        self.name = name
        self.surface = surface
        self.type = type_
        self.image_url = TRACK_IMAGE.format("-".join(self.name.split()))

    def __str__(self):
        return ("```Name:    {}\n"
                "Surface: {}\n"
                "Type:    {}\n```"
                "{}".format(self.name.title(),
                                     self.surface.title(),
                                     self.type.title(),
                                     self.image_url))

    @staticmethod
    def from_csv_row(row):
        return Track(*row)

class ForzaBotClient(discord.Client):
    def __init__(self, cars, tracks):
        super(ForzaBotClient, self).__init__()
        self.cars = cars
        self.car_types = [i for i in self.cars.keys()]
        self.all_cars = self.get_all_cars()
        self.tracks = tracks
        self.all_tracks = self.get_all_tracks()
        self.cmd_str = "!forza"
        self.cars_by_mfg = self.get_cars_by_mfg()

    async def on_ready(self):
        print(f"{self.user} has connected!")

    async def on_message(self, message):
        # The bot sent the message, send no reply.
        if message.author == client.user:
            return

        if message.content.startswith(self.cmd_str):
            response = self.message_handler(message.content)
            await message.channel.send(response)
        return

    def get_cmd(self, message):
        return list(i.lower() for i in message.lstrip(self.cmd_str).split())

    def get_all_cars(self):
        all_cars = []
        for car_list in self.cars.values():
            for car in car_list:
                all_cars.append(car)
        return all_cars

    def get_all_tracks(self):
        all_tracks = []
        for track_list in self.tracks.values():
            for track in track_list:
                all_tracks.append(track)
        return all_tracks

    def get_cars_by_mfg(self):
        cars_by_mfg = {}
        for car in self.all_cars:
            if car.make.lower() not in cars_by_mfg:
                cars_by_mfg[car.make.lower()] = []
            cars_by_mfg[car.make.lower()].append(car)
        return cars_by_mfg

    def message_handler(self, message):
        cmds = {
                    "test": self.handle_test,
                    "new-car": self.handle_new_car,
                    "list": self.handle_list,
                    "random": self.handle_random_car,
                    "track": self.handle_track,
                    "championship": self.handle_championship,
                    "champ": self.handle_championship,
                    "ship": self.handle_championship,
                    "help": self.handle_help,
                    "halp": self.handle_help,
               }

        cmd = self.get_cmd(message)

        handle = cmds.get(cmd[0])

        if handle:
            return handle(cmd)
        return "Command not supported"

    def handle_test(self, cmd):
        return "```I'm alive!```"

    def handle_new_car(self, cmd):
        random.shuffle(self.car_types)
        random.shuffle(RACE_TYPES)

        car_type = self.car_types[0]
        race_type = RACE_TYPES[0].title()

        lowest = lowest_class(self.cars[car_type])
        filtered_types = PI_CLASSES[lowest::]
        random.shuffle(filtered_types)
        perf_class = filtered_types[0]

        return "```Type: {}\nClass: {}\nRace: {}```".format(car_type, perf_class, race_type)

    def handle_list(self, cmd):
        cmds = {"types": self._list_types,
                "type": self._list_type,
                "mfg": self._list_manufacturer,
                "mfr": self._list_manufacturer}

        if len(cmd) < 2:
            return "```I need to know what thing to list```"

        handle = cmds.get(cmd[1])

        if handle:
            return handle(cmd)
        else:
            return f"```Sorry, I don't recognize command {cmd[1]}```"

    def _list_types(self, cmd):
        types = "\n".join(sorted(self.car_types))
        return f"```{types}```"

    def _list_type(self, cmd):
        if len(cmd) < 3:
            return "```I need to know what type of car to list```"

        car_type = " ".join(cmd[2::]).lower()

        if car_type in self.car_types:
            cars_of_type = "\n".join(str(i) for i in self.cars[car_type])
            return f"```{cars_of_type}```"
        else:
            return f"```Sorry I don't recognize type {car_type}```"

    def _list_manufacturer(self, cmd):
        if len(cmd) == 2:
            mfgs = "\n".join(self.cars_by_mfg)
            return f"```{mfgs}```"

        mfg = cmd[2].lower()

        if mfg not in self.cars_by_mfg:
            return "```Sorrt I don't know that manufacturer```"
        
        cars_from_mfg = "\n".join(str(i) for i in self.cars_by_mfg[mfg])
        return f"```{cars_from_mfg}```"

    def handle_random_car(self, cmd):
        if len(cmd) == 1:
            random.shuffle(self.all_cars)
            return str(self.all_cars[0])

        if len(cmd[1]) == 1:
            class_cars = [i for i in self.all_cars if i.pi_class == cmd[1].upper()]
            random.shuffle(class_cars)
            return str(class_cars[0])

        random_cmd = " ".join(cmd[1::]).lower()
        if random_cmd in self.car_types:
            rand_idx = random.randint(0, len(self.cars[random_cmd]))
            return "```" + str(self.cars[random_cmd][rand_idx]) + "````"
        return "I don't recognize that car type sorry"

    def handle_track(self, cmd):
        if len(cmd) == 1:
            random.shuffle(self.all_tracks)
            return(str(self.all_tracks[0]))

        surface = cmd[1].lower()
        if surface in self.tracks:
            rand_idx = random.randint(0, len(self.tracks[surface]))
            return str(self.tracks[surface][rand_idx])
        return "I don't recognize that surface sorry.\n\nValid surfaces: road, rally, offroad"

    def handle_championship(self, cmd):
        if len(cmd) == 1:
            num_races = 3
            surface = None
        elif len(cmd) == 2:
            if cmd[1].isdigit():
                num_races = int(cmd[1])
                surface = None
            else:
                num_races = 3
                surface = cmd[1].lower()
        elif len(cmd) == 3:
            if cmd[1].isdigit():
                num_races = int(cmd[1])
                surface = cmd[2].lower()
            elif cmd[2].isdigit():
                num_races = int(cmd[2])
                surface = cmd[1].lower()

        if num_races == 69:
            return "NICE"

        if surface and surface not in self.tracks:
            return "I don't recognize that surface sorry.\n\nValid surfaces: road, rally, offroad"

        if surface:
            random.shuffle(self.tracks[surface])
            return "\n\n".join(str(i) for i in self.tracks[surface][0:num_races])

        random.shuffle(self.all_tracks)
        return "\n\n".join(str(i) for i in self.all_tracks[0:num_races])

    def handle_help(self, cmd):
        return """```Here's all the commands I support

* new-car - Prints a random car type, class, and PI. 

* list types - List all car types.
* list type [car-type] - List all cars of the provided type.
* list mfg - List all manufacturers.
* list mfg [mfg] - List all cars made by the provided manufacturer.

* random [car-type] - Print a random car. If [car-type] is provided instead print a random car of that type.

* track [surface] - Print a random track. If [surface] is provided only tracks with that surface will be included .

* championship [num_races] [surface] - Create a championship with [num_races] with type [surface]. Default 3 races any type.

* help - Print this help text, again.
```
        """


def parse_cars(csv_path):
    cars = {}

    with open(csv_path, "r") as csv_file:
        car_reader = csv.reader(csv_file, delimiter=",")

        for index, row in enumerate(car_reader):
            if index == 0:
                continue

            car = Car.from_csv_row(row)
            if car.car_type not in cars:
                cars[car.car_type] = []
            cars[car.car_type].append(car)
    return cars


def parse_tracks(csv_path):
    tracks = {}

    with open(csv_path, "r") as csv_file:
        track_reader = csv.reader(csv_file, delimiter=",")

        for index, row in enumerate(track_reader):
            if index == 0:
                continue

            track = Track.from_csv_row(row)
            if track.surface not in tracks:
                tracks[track.surface] = []
            tracks[track.surface].append(track)
    return tracks


def lowest_class(cars):
    lowest = len(PI_CLASSES) - 1

    for car in cars:
        if PI_CLASSES.index(car.pi_class) < lowest:
            lowest = PI_CLASSES.index(car.pi_class)
        if lowest == PI_CLASSES[0]:
            return 0
    return lowest


if __name__ == "__main__":
    cars = parse_cars(CAR_CSV)
    tracks = parse_tracks(TRACK_CSV)

    client = ForzaBotClient(cars, tracks)
    client.run(TOKEN)
