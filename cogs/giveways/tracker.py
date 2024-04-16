import nextcord
from nextcord.ext import commands
from rich import print
import json

import dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.time_utils import to_datetime
import random

EVENTS_ROLE_ID = dotenv.get_key(dotenv.find_dotenv(), "EVENTS_ROLE_ID")


class GivewaysTracker:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def get_winners(self, giveway: dict) -> list[int]:
        participants: list[int] = giveway["participants"]
        users = participants.copy()

        winners = set()
        while users:
            winner = random.choice(users)
            if winner in winners:
                continue
            winners.add(winner)
            users.remove(winner)

        return winners

    def get_giveways(self) -> list[dict]:
        with open("giveways.json", "rt") as giveways_file:
            return json.loads(giveways_file.read())

    def set_giveways(self, giveways: list[dict]):
        with open("giveways.json", "wt") as giveways_file:
            giveways_file.write(json.dumps(giveways))

    def new_giveway(self, giveway: dict, message: nextcord.Message):
        giveways = self.get_giveways()
        giveways.append(giveway)
        self.set_giveways(giveways)

        async def job():
            this_giveway = self.get_giveways()[
                [gy["message_id"] for gy in self.get_giveways()].index(
                    giveway["message_id"]
                )
            ]
            if (
                not len(this_giveway["participants"])
                < this_giveway["number_of_winners"]
            ):

                winners = self.get_winners(this_giveway)

                content: str = "# Fin du giveway\n\n"

                i = 1
                for winner in winners:
                    content += "#" + str(i) + " <@" + str(winner) + ">"
                    if giveway["different_rewards"]:
                        content += " : " + giveway["rewards"][i - 1]
                    content += "\n"
                    i += 1

                content += "\n\n"

                content += (
                    "Bravo à <@"
                    + ">, <@".join([str(win) for win in winners])
                    + ">"
                    + (
                        (
                            (" qui ont gagné " if len(winners) > 1 else " qui a gagné ")
                            + giveway["reward"]
                        )
                        if not giveway["different_rewards"]
                        else ""
                    )
                    + " !"
                )

                await message.channel.send(
                    "<@&" + str(EVENTS_ROLE_ID) + ">",
                    embed=nextcord.Embed(description=content),
                    # reference=message.channel.get_partial_message(giveway["message_id"]),
                )
                message.embeds[0].title = "Giveway terminé"

            else:
                await message.channel.send(
                    embed=nextcord.Embed(
                        description="# Giveway annulé\nPas assez de participants"
                    )
                )
                message.embeds[0].title = "Giveway annulé"

            await message.edit(view=None, embed=message.embeds[0], content="")

        date = to_datetime(giveway["end_timestamp"])

        scheduler = AsyncIOScheduler()
        scheduler.add_job(job, "date", run_date=date)
        scheduler.start()
