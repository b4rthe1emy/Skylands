from rich import print
import nextcord
from .polls_tracker import *


async def count_poll(
    interaction: nextcord.Interaction,
    poll_id: int,
    option_id: int,
    tracker: PollsTracker,
):
    if option_id == -1:
        await tracker.clear_votes(poll_id, interaction.user.id, interaction)
    else:
        await tracker.vote(poll_id, option_id, interaction)


def get_view(options):
    if options == 0:
        return PollButtons0
    if options == 1:
        return PollButtons1
    if options == 2:
        return PollButtons2
    if options == 3:
        return PollButtons3
    if options == 4:
        return PollButtons4
    if options == 5:
        return PollButtons5
    if options == 6:
        return PollButtons6
    if options == 7:
        return PollButtons7
    if options == 8:
        return PollButtons8
    if options == 9:
        return PollButtons9
    if options == 10:
        return PollButtons10


class PollButtonsClearAll(nextcord.ui.View):

    def __init__(self, poll_id: int, polls_tracker):
        super().__init__()
        self.poll_id = poll_id
        self.polls_tracker: PollsTracker = polls_tracker

    @nextcord.ui.button(
        label="Annuler mon/mes vote(s)", style=nextcord.ButtonStyle.blurple, row=0
    )
    async def buttonClear(
        self, btn: nextcord.Button, interaction: nextcord.Interaction
    ):
        await count_poll(interaction, self.poll_id, -1, self.polls_tracker)

    @nextcord.ui.button(
        label="Voir mon/mes vote(s)", style=nextcord.ButtonStyle.blurple, row=0
    )
    async def buttonViewVotes(
        self, btn: nextcord.Button, interaction: nextcord.Interaction
    ):
        polls: list[dict] = await self.polls_tracker.get_polls()
        poll_index = await self.polls_tracker.get_poll_index(self.poll_id, interaction)

        if poll_index is None:
            return

        votes = []
        for vote_index, has_voted in enumerate(
            [(interaction.user.id in vote) for vote in polls[poll_index]["votes"]]
        ):

            if has_voted:
                votes.append(str(vote_index))
        if votes:
            await interaction.response.send_message(
                f"Tu as voté pour"
                + (" les options " if len(votes) >= 2 else " l'option ")
                + (
                    votes[0]
                    if len(votes) == 1
                    else (", ".join(votes[:-1]) + " et " + votes[-1])
                )
                + ".",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Tu n'as pas voté pour ce sondage.", ephemeral=True
            )


class PollButtons0(PollButtonsClearAll):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[0]
        self.button0.emoji = self.custom_emoji

    @nextcord.ui.button(
        label="",
        style=nextcord.ButtonStyle.gray,
        row=1,
    )
    async def button0(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 0, self.polls_tracker)


class PollButtons1(PollButtons0):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[1]
        self.button1.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=1)
    async def button1(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 1, self.polls_tracker)


class PollButtons2(PollButtons1):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[2]
        self.button2.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=1)
    async def button2(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 2, self.polls_tracker)


class PollButtons3(PollButtons2):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[3]
        self.button3.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=1)
    async def button3(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 3, self.polls_tracker)


class PollButtons4(PollButtons3):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[4]
        self.button4.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=1)
    async def button4(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 4, self.polls_tracker)


class PollButtons5(PollButtons4):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[5]
        self.button5.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=2)
    async def button5(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 5, self.polls_tracker)


class PollButtons6(PollButtons5):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[6]
        self.button6.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=2)
    async def button6(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 6, self.polls_tracker)


class PollButtons7(PollButtons6):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[7]
        self.button7.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=2)
    async def button7(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 7, self.polls_tracker)


class PollButtons8(PollButtons7):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[8]
        self.button8.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=2)
    async def button8(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 8, self.polls_tracker)


class PollButtons9(PollButtons8):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[9]
        self.button9.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=2)
    async def button9(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 9, self.polls_tracker)


class PollButtons10(PollButtons9):

    def __init__(self, poll_id: int, polls_tracker, custom_emojis: list[str]):
        super().__init__(poll_id, polls_tracker, custom_emojis)
        self.poll_id = poll_id
        self.polls_tracker = polls_tracker
        self.custom_emoji = custom_emojis[10]
        self.button10.emoji = self.custom_emoji

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=3)
    async def button10(self, btn: nextcord.Button, interaction: nextcord.Interaction):
        await count_poll(interaction, self.poll_id, 10, self.polls_tracker)
