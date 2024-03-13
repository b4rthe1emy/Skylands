from nextcord.utils import MISSING
from rich import print
import nextcord
from .polls_tracker import *
from utils.time_utils import to_datetime

NUMBER_EMOJIS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def get_control_panel_embed(title, poll_id, len_list_options, multiple_votes_allowed):
    embed = nextcord.Embed(
        title='Control panel pour le sondage : "' + title + '"',
        description=f"**Ceci est le panneau de configuration du sondage que vous venez de créer.**",
        colour=0x3498DB,
        timestamp=to_datetime(),
    )
    embed.add_field(
        name="❓ Pour plus d'informations, merci de regarder le message original.",
        value="",
    )
    embed.add_field(name="`int` ID", value="```" + str(poll_id) + "```", inline=False)
    embed.add_field(
        name="`int` Nombre de réponses possibles",
        value=str(len_list_options),
        inline=False,
    )
    embed.add_field(
        name="`bool` Autoriser plusieurs votes",
        value=("Oui" if multiple_votes_allowed == "1" else "Non"),
        inline=False,
    )
    return embed


def get_poll_message_embed_and_view(self, title, options):

    options = options[1:-1]
    list_options: list[str] = options.split(";")

    formated_options: str = ""
    number = 0
    custom_emojis: list[str] = []
    for option in list_options:

        if option.startswith(" "):
            formated_options += NUMBER_EMOJIS[number]
            formated_options += option + "\n"
            custom_emojis.append(NUMBER_EMOJIS[number])
        else:
            formated_options += option + "\n"
            custom_emojis.append(option[0])

        number += 1

    poll_id = self.polls_tracker.get_new_id()

    view: nextcord.ui.View = get_view(len(list_options) - 1)(
        poll_id,
        self.polls_tracker,
        custom_emojis,
    )
    embed = nextcord.Embed(
        title=title,
        description=formated_options,
        colour=0x3498DB,
        timestamp=to_datetime(),
    )
    return (embed, view, formated_options, list_options, poll_id)


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


def get_view(options) -> nextcord.ui.View:
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


class ControlPanelModal(nextcord.ui.Modal):
    def __init__(self, polls_tracker: PollsTracker, buttons_control_pannel) -> None:
        self.polls_tracker: PollsTracker = polls_tracker
        self.buttons_control_pannel = buttons_control_pannel

    async def setup(self, interaction: nextcord.Interaction, poll_id: int):
        self.poll_id: int = poll_id

        super().__init__(timeout=None, title=f"Renommer le sondage {self.poll_id}")

        polls = await self.polls_tracker.get_polls()
        poll_index = await self.polls_tracker.get_poll_index(self.poll_id, interaction)

        self.poll: Poll = self.polls_tracker.dict_to_poll(polls[poll_index])

        self.new_name = nextcord.ui.TextInput(
            "Nouveau nom",
            default_value=self.poll.title,
            placeholder="Nouveau nom",
            required=True,
        )
        self.add_item(self.new_name)

        self.new_mva = nextcord.ui.TextInput(
            "Autoriser plusieurs votes (1 : Oui, 0 : Non)",
            default_value=("1" if self.poll.multiple_votes_allowed else "0"),
            placeholder="Autoriser plusieurs votes",
            required=True,
            max_length=1,
        )
        self.add_item(self.new_mva)

    async def callback(self, callback_interaction: nextcord.Interaction):

        await self.polls_tracker.edit_poll(
            self.poll_id,
            Poll(
                self.poll.id,
                self.new_name.value,
                self.poll.options,
                bool(self.new_mva.value == "1"),
                self.poll.end_timestamp,
                self.poll.votes,
            ),
            callback_interaction,
        )
        await callback_interaction.guild.get_channel_or_thread(
            self.buttons_control_pannel.message_channel_id
        ).get_partial_message(self.buttons_control_pannel.message_id).edit(
            embed=get_poll_message_embed_and_view()
        )

        await callback_interaction.message.edit(
            embed=get_control_panel_embed(
                self.new_name.value,
                self.poll_id,
                len(self.poll.options),
                (self.new_mva.value == "1"),
            ),
        )


class PollButtonsControlPannel(nextcord.ui.View):
    def __init__(
        self, poll_id: int, polls_tracker, message_id: int, message_channel_id: int
    ):
        super().__init__(timeout=None)  # , prevent_update=False)
        self.poll_id = poll_id
        self.polls_tracker: PollsTracker = polls_tracker
        self.message_id: int = message_id
        self.message_channel_id: int = message_channel_id

    @nextcord.ui.button(label="Supprimer", emoji="🗑️", style=nextcord.ButtonStyle.red)
    async def delete_poll(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        await self.polls_tracker.delete_poll(self.poll_id, interaction)
        await interaction.response.send_message("Sondage supprimé", ephemeral=True)
        await interaction.message.edit(
            content=None,
            embed=nextcord.Embed(
                title="Control panel : Ce sondage a été supprimé.",
                timestamp=to_datetime(),
            ),
            view=None,
        )
        await interaction.guild.get_channel_or_thread(
            self.message_channel_id
        ).get_partial_message(self.message_id).edit(
            content=None,
            embed=nextcord.Embed(
                title="Ce sondage est terminé.", timestamp=to_datetime()
            ),
            view=None,
        )

    @nextcord.ui.button(
        label="Modifier",
        emoji="🖊️",
        custom_id=("poll_edit_" + str(random.randint(0, 999_999_999))),
    )
    async def edit_poll(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        modal = ControlPanelModal(self.polls_tracker, self)
        await modal.setup(interaction, self.poll_id)
        await interaction.response.send_modal(modal)


class PollButtonsClearAll(nextcord.ui.View):

    def __init__(self, poll_id: int, polls_tracker):
        super().__init__(timeout=None)
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

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, row=1)
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
