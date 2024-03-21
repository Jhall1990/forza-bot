import random
import discord
import argparse
from discord import app_commands

import data


# TODO: Upper case class
# TODO: Don't pick division that's lower than the selected car (race only?)
# TODO: Figure out what the lowest class per division is
# TODO: Game based class, division
# TODO: Clean up select stuff?


#############
# Constants #
#############
SELECT_TRACK = "track"
SELECT_CAR = "car"
SELECT_CLASS = "class"
SELECT_DIVISION = "division"
SELECT_RACE = "race"


CLASS_E = "e"
CLASS_D = "d"
CLASS_C = "c"
CLASS_B = "b"
CLASS_A = "a"
CLASS_S = "s"
CLASS_R = "r"
CLASS_P = "p"
CLASS_X = "x"
ALL_CLASSES = [
    CLASS_E,
    CLASS_D,
    CLASS_C,
    CLASS_B,
    CLASS_A,
    CLASS_S,
    CLASS_R,
    CLASS_P,
    CLASS_X,
]


###########
# Helpers #
###########
def get_token(path):
    with open(path, "r") as f:
        return f.read().strip()


def select_choices():
    choices = [
        SELECT_TRACK,
        SELECT_CAR,
        SELECT_CLASS,
        SELECT_DIVISION,
        SELECT_RACE,
    ]
    return [app_commands.Choice(name=c, value=c) for c in choices]


##########
# Client #
##########
class ForzaBot(discord.Client):
    def __init__(self, guild, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild = discord.Object(id=guild)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=self.guild)
        await self.tree.sync(guild=self.guild)

    async def on_ready(self):
        print("ready!")


class ForzaCommand(app_commands.Group):
    def __init__(self, db_file, *args, **kwargs):
        super().__init__(name="forza", *args, **kwargs)
        self.cars = data.cars_from_db(db_file)
        self.tracks = data.tracks_from_db(db_file)
        self.divisions = data.divisions_from_db(db_file)
        self.game = "motorsport"

    ################
    # Ping Command #
    ################
    @app_commands.command(name="ping")
    async def ping_command(self, interaction):
        await interaction.response.send_message("pong")

    ##################
    # Select Command #
    ##################
    @app_commands.command(name="select")
    @app_commands.choices(command=select_choices())
    async def select_command(self, interaction, command: app_commands.Choice[str]):
        embed = None
        if command.value == SELECT_TRACK:
            embed = self.select_track()
        elif command.value == SELECT_CAR:
            embed = self.select_car()
        elif command.value == SELECT_CLASS:
            embed = self.select_class()
        elif command.value == SELECT_DIVISION:
            embed = self.select_division()
        elif command.value == SELECT_RACE:
            embed = self.select_race()
        else:
            await interaction.response.send_message(f"Unrecognized selection: {command}")
            return
        await interaction.response.send_message(embed=embed)

    def select_track(self):
        track = self.select_random(self.tracks[self.game])
        return self.create_embed("Track", ["Name"], [track.name])

    def select_car(self):
        car = self.select_random(self.cars[self.game])
        return self.create_embed("Car", 
                                 ["Year", "Make", "Model", "Division", "Class"], 
                                 [car.year, car.make, car.model, car.division, car.perfClass])

    def select_class(self, car=None):
        start = 0
        if car:
            start = ALL_CLASSES.index(car.perfClass.lower())
        randClass = self.select_random(ALL_CLASSES, start)
        return self.create_embed("Class", ["Class"], [randClass])

    def select_division(self):
        division = self.select_random(self.divisions).upper()
        return self.create_embed("Division", ["Division"], [division])

    def select_race(self):
        car = self.select_random(self.cars[self.game])
        division = self.select_random(self.divisions)
        track = self.select_random(self.tracks[self.game])

        if random.randint(0, 4) == 0:
            perfClass = self.select_random(ALL_CLASSES, start=ALL_CLASSES.index(car.perfClass.lower())).upper()
            return self.create_embed("Race", ["Track", "Class", "Car"], [track.name, perfClass, str(car)])

        perfClass = self.select_random(ALL_CLASSES).upper()
        return self.create_embed("Race", ["Track", "Class", "Division"], [track.name, perfClass, division])

    def select_random(self, collection, start=0):
        return collection[random.randint(start, len(collection)-1)]

    def create_embed(self, title, headers, values):
        embed = discord.Embed(title=title)
        for header, value in zip(headers, values):
            embed.add_field(name=header, value=value, inline=False)
        embed.set_thumbnail(url="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/117bfc2d-044f-4583-8dc7-ed4e0e146692/dd6sbxv-6f66db4b-d0df-47bc-8615-a095aecceb78.png/v1/fill/w_850,h_850,q_80,strp/forza_horizon_4_logo_icon_by_20sy_dd6sbxv-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9ODUwIiwicGF0aCI6IlwvZlwvMTE3YmZjMmQtMDQ0Zi00NTgzLThkYzctZWQ0ZTBlMTQ2NjkyXC9kZDZzYnh2LTZmNjZkYjRiLWQwZGYtNDdiYy04NjE1LWEwOTVhZWNjZWI3OC5wbmciLCJ3aWR0aCI6Ijw9ODUwIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.JzeW4CclkWBFl9hfmAupkb-opy1L7Qm4ONNL-iMsCG4")
        return embed


##############
# Arg Parser #
##############
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--token", help="path to file with discord bot token", required=True)
ap.add_argument("-g", "--guild", help="discord guild id", required=True)
ap.add_argument("-d", "--db", help="path to db file with tracks and cars", required=True)
args = ap.parse_args()

########
# Main #
########
client = ForzaBot(args.guild, intents=discord.Intents.default())
client.tree.add_command(ForzaCommand(args.db))
client.run(get_token(args.token))
