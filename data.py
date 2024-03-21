import csv
import sqlite3
import argparse
import contextlib


data = {
    "motorsport": {
        "cars": "fm-cars.csv",
        "tracks": "fm-tracks.csv",
    },
#     "horizon5": {
#         "cars": "fh5-cars.csv",
#         "tracks": "fh5-tracks.csv",
#     },
}


def cars_from_db(db_file):
    cars = {}
    query = "SELECT * FROM cars"

    with contextlib.closing(sqlite3.connect(db_file)) as conn:
        with conn as cur:
            result = cur.execute(query).fetchall()

    for row in result:
        if row[0] not in cars:
            cars[row[0]] = []
        cars[row[0]].append(Car(*row[1:]))
    return cars


def tracks_from_db(db_file):
    tracks = {}
    query = "SELECT * FROM tracks"

    with contextlib.closing(sqlite3.connect(db_file)) as conn:
        with conn as cur:
            result = cur.execute(query).fetchall()

    for row in result:
        if row[0] not in tracks:
            tracks[row[0]] = []
        tracks[row[0]].append(Track(*row[1:]))
    return tracks


def divisions_from_db(db_file):
    divisions = []
    query = "SELECT DISTINCT(division) FROM cars"

    with contextlib.closing(sqlite3.connect(db_file)) as conn:
        with conn as cur:
            result = cur.execute(query).fetchall()

    for row in result:
        divisions.append(row[0])
    return divisions


def to_db(cars, tracks, output):
    con = sqlite3.connect(output)
    cur = con.cursor()

    # Create the track table
    query = "CREATE TABLE tracks(game, name, surface, type)"
    cur.execute(query)

    # Create the car table
    query = "CREATE TABLE cars(game, year, make, model, division, class)"
    cur.execute(query)

    cars_to_db(con, game, cars)
    tracks_to_db(con, game, tracks)

    con.commit()


def cars_to_db(cursor, game, cars):
    insert_query = "INSERT INTO cars VALUES"
    
    for game in cars:
        for car in cars[game]:
            query = f"{insert_query} {car.to_db(game)}"
            cursor.execute(query)


def tracks_to_db(cursor, game, tracks):
    insert_query = "INSERT INTO tracks VALUES"

    for game in tracks:
        for track in tracks[game]:
            query = f"{insert_query} {track.to_db(game)}"
            cursor.execute(query)


def parse_cars(path):
    cars = []

    with open(path, "r") as f:
        reader = csv.reader(f)

        for i, row in enumerate(reader):
            if i == 0:
                continue
            cars.append(Car.from_csv(row))
    return cars


def parse_tracks(path):
    tracks = []

    with open(path, "r") as f:
        reader = csv.reader(f)

        for i, row in enumerate(reader):
            if i == 0:
                continue
            tracks.append(Track.from_csv(row))
    return tracks


class Car():
    def __init__(self, year, make, model, division, perfClass):
        self.year = year.strip().replace('"', "'")
        self.make = make.strip().replace('"', "'")
        self.model = model.strip().replace('"', "'")
        self.division = division.strip().replace('"', "'")
        self.perfClass = perfClass.strip().strip("1234567890").replace('"', "'")

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

    def to_db(self, game):
        return f'("{game}", "{self.year}", "{self.make}", "{self.model}", "{self.division}", "{self.perfClass}")'

    @staticmethod
    def from_csv(line):
        return Car(*line)


class Track():
    def __init__(self, name, surface, type_):
        self.name = name.strip()
        self.surface = surface.strip()
        self.type = type_.strip()

    def to_db(self, game):
        return f'("{game}", "{self.name}", "{self.surface}", "{self.type}")'

    @staticmethod
    def from_csv(line):
        return Track(*line)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", help="output db file", required=True)
    args = ap.parse_args()

    cars = {}
    tracks = {}

    for game in data:
        cars[game] = parse_cars(data[game]["cars"])
        tracks[game] = parse_tracks(data[game]["tracks"])

    to_db(cars, tracks, args.output)

    db_cars = cars_from_db(args.output)
    db_tracks = tracks_from_db(args.output)
    print("done")
