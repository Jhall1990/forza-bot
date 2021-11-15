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
PI_CLASSES = ["D", "C", "B", "A", "S1", "S2", "X"]
RACE_TYPES = ["RALLY", "STREET", "OFFROAD"]

with open("token.txt", "r") as token_file:
    TOKEN = token_file.read().strip()

if not TOKEN:
    sys.exit( "No discord token found" )

class Car(object):
    def __init__(self, year, vehicle, value, rarity, speed, handle, accel, launch, brake, offroad, pi, car_type):
        self.year = year
        self.vehicle = vehicle
        self.value = value
        self.rarity = rarity
        self.speed = speed
        self.handle = handle
        self.accel = accel
        self.launch = launch
        self.brake = brake
        self.offroad = offroad
        self.pi = pi
        self.pi_class = self.parse_pi()
        self.car_type = car_type.lower()

    def __str__(self):
        return " ".join([self.year, self.vehicle])

    def parse_pi(self):
        if self.pi.startswith(("D", "C", "B", "A", "X")):
            return self.pi[0]
        elif self.pi.startswith(("S1", "S2")):
            return self.pi[0:2]
        return "X"

    @staticmethod
    def from_csv_row(row):
        return Car(*row)

class ForzaBotClient(discord.Client):
    def __init__(self, cars):
        super(ForzaBotClient, self).__init__()
        self.cars = cars
        self.car_types = [i for i in self.cars.keys()]
        self.all_cars = self.get_all_cars()
        self.cmd_str = "/forza"

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

    def message_handler(self, message):
        cmds = {
                    "test": self.handle_test,
                    "new-car": self.handle_new_car,
                    "list": self.handle_list,
                    "random": self.handle_random_car,
                    "help": self.handle_help,
                    "halp": self.handle_help,
               }

        cmd = self.get_cmd(message)

        handle = cmds.get(cmd[0])

        if handle:
            return "```{}```".format(handle(cmd))
        return "Command not supported"

    def handle_test(self, cmd):
        return "Test command worked!"

    def handle_new_car(self, cmd):
        random.shuffle(self.car_types)
        random.shuffle(RACE_TYPES)

        car_type = self.car_types[0]
        race_type = RACE_TYPES[0].title()

        lowest = lowest_class(self.cars[car_type])
        filtered_types = PI_CLASSES[lowest::]
        random.shuffle(filtered_types)
        perf_class = filtered_types[0]

        return "Type: {}\nClass: {}\nRace: {}".format(car_type, perf_class, race_type)

    def handle_list(self, cmd):
        if len(cmd) == 1:
            return "I need either 'types' or <type>"

        list_cmd = " ".join(cmd[1::]).lower()

        if cmd[1] == "types":
            return "\n".join(sorted(self.car_types))
        if list_cmd in self.car_types:
            return "\n".join([str(i) for i in self.cars[list_cmd]])
        return "I don't recognize that car type sorry"

    def handle_random_car(self, cmd):
        if len(cmd) == 1:
            random.shuffle(self.all_cars)
            return str(self.all_cars[0])

        random_cmd = " ".join(cmd[1::]).lower()
        if random_cmd in self.car_types:
            rand_idx = random.randint(0, len(self.cars[random_cmd]))
            return str(self.cars[random_cmd][rand_idx])
        return "I don't recognize that car type sorry"

    def handle_help(self, cmd):
        return """Here's all the commands I support

* new-car - Prints a random car type, class, and PI. 

* list [car-type] - Lists all the car types. If [car-type] is provided list all the cars of that type.

* random [car-type] - Print a random car. If [car-type] is provided instead print a random car of that type.

* help - Print this help text, again.
        """


def parse_csv(csv_path):
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


def lowest_class(cars):
    lowest = len(PI_CLASSES) - 1

    for car in cars:
        if PI_CLASSES.index(car.pi_class) < lowest:
            lowest = PI_CLASSES.index(car.pi_class)
        if lowest == PI_CLASSES[0]:
            return 0
    return lowest


if __name__ == "__main__":
    cars = parse_csv(CAR_CSV)
    print(type(cars))

    for car_type, car_list in cars.items():
        print("Type: {}".format(car_type))
        for car in car_list:
            print("   {}".format(str(car)))

    client = ForzaBotClient(cars)
    client.run(TOKEN)
