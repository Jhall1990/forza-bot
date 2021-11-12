import csv
import sys
import random
import discord

CAR_CSV = "cars.csv"
PI_CLASSES = ["D", "C", "B", "A", "S1", "S2", "X"]

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
        self.car_type = car_type

    def __lt__(self, other):
        return PI_CLASSES.index(self.pi_class) < PI_CLASSES.index(other.pi_class)

    def __gt__(self, other):
        return PI_CLASSES.index(self.pi_class) > PI_CLASSES.index(other.pi_class)

    def __str__(self):
        return " ".join([self.year, self.vehicle, self.car_type])

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
        return message.lstrip(self.cmd_str).split()

    def message_handler(self, message):
        cmds = {"test": self.handle_test,
                "new-car": self.handle_new_car}

        cmd = self.get_cmd(message)

        handle = cmds.get(cmd[0])

        if handle:
            return handle(cmd)
        return "Command not supported"

    def handle_test(self, cmd):
        return "Test command worked!"

    def handle_new_car(self, cmd):
        random.shuffle(self.car_types)
        car_type = self.car_types[0]
        perf_class = lowest_class(self.cars[car_type])
        return "Type: {}\nClass: {}".format(car_type, perf_class)

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
            return PI_CLASSES[0]
    return PI_CLASSES[lowest]


if __name__ == "__main__":
    cars = parse_csv(CAR_CSV)
    print(type(cars))

    for car_type, car_list in cars.items():
        print("Type: {}".format(car_type))
        for car in car_list:
            print("   {}".format(str(car)))

    client = ForzaBotClient(cars)
    client.run(TOKEN)
