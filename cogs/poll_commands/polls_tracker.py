import nextcord
from nextcord.ext import commands
from rich import print
import json
import random
import dotenv

from utils.time_utils import to_datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Poll:
    def __init__(
        self,
        poll_id: int,
        title: str,
        options: list[str],
        multiple_votes_allowed: bool,
        end_timestamp: int,
        votes: list[int] = None,
    ) -> None:

        self.id: int = poll_id
        self.title: str = title

        self.multiple_votes_allowed: bool = multiple_votes_allowed
        self.options: list[str] = options
        self.votes = votes
        self.end_timestamp: float = end_timestamp

        if votes is None:
            self.votes: list[list[int]] = []
            for i in range(len(options)):
                self.votes.append([].copy())

    async def vote(
        self,
        user_id: int,
        option_id: int,
        interaction: nextcord.Interaction,
    ) -> None:
        option_id = int(option_id)
        if not self.multiple_votes_allowed:
            for option in self.votes:
                if user_id in option:
                    await interaction.response.send_message(
                        "Tu as déjà voté pour ce sondage. Utilise le bouton `Annuler mon/mes vote(s)` pour annuler ton vote.",
                        ephemeral=True,
                    )
                    return

        if int(user_id) in self.votes[option_id]:
            await interaction.response.send_message(
                f"Tu as déjà voté pour l'option {option_id}.", ephemeral=True
            )
            return

        self.votes[option_id].append(user_id)
        await interaction.response.send_message(
            f"Voté pour l'option {option_id}. Clique sur `Voir mon/mes vote(s)` pour voir tous tes votes sur ce sondage.",
            ephemeral=True,
        )

    def clear_all_votes_from_user(self, user_id: int) -> int:
        for option in self.votes:
            try:
                option.remove(user_id)
            except ValueError:
                pass


class PollsTracker:
    polls_file = dotenv.get_key(dotenv.find_dotenv(), "SAVED_POLLS_FILE")
    MAX_POLLS = 999_999
    active_atomatic_polls: list[Poll] = []

    def get_new_id(self) -> int:
        id_attempt = random.randint(1, self.MAX_POLLS)
        with open(self.polls_file, mode="r") as file:
            polls: list[dict] = json.loads(file.read())
            if id_attempt in [poll["id"] for poll in polls]:
                return self.get_new_id()

        return id_attempt

    async def poll_results(
        self, poll_id, interaction: nextcord.Interaction, context: nextcord.TextChannel
    ):
        polls = await self.get_polls()
        poll_index = await self.get_poll_index(poll_id, interaction)

        votes = polls[poll_index]["votes"]
        options = polls[poll_index]["options"]
        message = ""
        for option_id, option in enumerate(votes):
            message += (
                options[option_id]
                + f" : **"
                + str(len(option))
                + " vote"
                + ("s" if len(option) >= 2 else "")
                + "**"
            )
            message += "\n"

        send = interaction.response.send_message if interaction else context.send

        await send(
            embed=nextcord.Embed(
                title=f'Résultats du sondage "{polls[poll_index]["title"]}" :',
                description=message,
                colour=0x3498DB,
            )
        )

    async def delete_poll(self, poll_id, interaction: nextcord.Interaction) -> bool:
        polls = await self.get_polls()
        poll_index = await self.get_poll_index(poll_id, interaction)

        polls.pop(poll_index)

        with open(self.polls_file, mode="w") as file:
            file.write(json.dumps(polls))

        return True

    async def get_polls(self) -> list[dict]:
        with open(self.polls_file, mode="r") as file:
            polls: list[dict] = json.loads(file.read())

        return polls

    async def get_poll_index(self, poll_id, interaction: nextcord.Interaction):
        with open(self.polls_file, mode="r") as file:
            polls: list[dict] = json.loads(file.read())
            try:
                poll_index: int = [poll["id"] for poll in polls].index(int(poll_id))
                return poll_index
            except ValueError:
                await interaction.response.send_message(
                    f"Ce sondage a été supprimé.",
                    ephemeral=True,
                )

    def poll_to_dict(self, poll: Poll) -> dict:
        return {
            "id": poll.id,
            "title": poll.title,
            "options": poll.options,
            "multiple_votes_allowed": poll.multiple_votes_allowed,
            "end_timestamp": poll.end_timestamp,
            "votes": poll.votes,
        }

    def dict_to_poll(self, poll: dict) -> Poll:
        return Poll(
            poll["id"],
            poll["title"],
            poll["options"],
            poll["multiple_votes_allowed"],
            poll["end_timestamp"],
            poll["votes"],
        )

    async def edit_poll(
        self, poll_id: int, new_poll: Poll, interaction: nextcord.Interaction
    ):
        polls = await self.get_polls()
        poll_index = await self.get_poll_index(poll_id, interaction)

        poll: Poll = self.dict_to_poll(polls[poll_index])

        poll.end_timestamp = new_poll.end_timestamp
        poll.id = new_poll.id
        poll.multiple_votes_allowed = new_poll.multiple_votes_allowed
        poll.title = new_poll.title

        polls[poll_index] = self.poll_to_dict(poll)

        with open(self.polls_file, mode="w") as file:
            file.write(json.dumps(polls))

    async def clear_votes(self, poll_id, user_id, interaction: nextcord.Interaction):
        polls = await self.get_polls()
        poll_index = await self.get_poll_index(poll_id, interaction)

        if poll_index is None:
            return

        with open(self.polls_file, mode="w") as file:

            poll = self.dict_to_poll(polls[poll_index])
            poll.clear_all_votes_from_user(user_id)
            polls[poll_index] = self.poll_to_dict(poll)

            file.write(json.dumps(polls))
            del poll

        await interaction.response.send_message(
            "Tous tes votes à ce sondage ont été supprimés.", ephemeral=True
        )

    async def new_poll(self, poll: Poll, interaction: nextcord.Interaction):
        polls = await self.get_polls()

        with open(self.polls_file, mode="w") as file:
            new_poll = self.poll_to_dict(poll)
            polls.append(new_poll)
            polls = json.dumps(polls)

            file.write(polls)
            print("New poll:", new_poll)

        scheduler = AsyncIOScheduler()
        date = to_datetime(poll.end_timestamp)

        if poll.end_timestamp != 0:

            async def job():
                await self.poll_results(poll.id, None, interaction.channel)
                await self.delete_poll(poll.id, interaction)

            scheduler.add_job(job, "date", run_date=date)
            scheduler.start()

    async def vote(self, poll_id: int, option: int, interaction: nextcord.Interaction):
        polls = await self.get_polls()
        poll_index = await self.get_poll_index(poll_id, interaction)

        if poll_index is None:
            return

        with open(self.polls_file, mode="w") as file:

            poll = self.dict_to_poll(polls[poll_index])
            await poll.vote(interaction.user.id, option, interaction)
            polls[poll_index] = self.poll_to_dict(poll)

            file.write(json.dumps(polls))
            del poll
