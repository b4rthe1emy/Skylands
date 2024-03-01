import nextcord
from nextcord.ext import commands
from rich import print

import dotenv

from .polls_tracker import *


dotenv_file = dotenv.find_dotenv()
ADMIN_ROLE_ID = str(dotenv.get_key(dotenv_file, "ADMIN_ROLE_ID"))


class PollCommands(commands.Cog):
    """
    Poll commands cog.
    """

    def __init__(self) -> None:
        super().__init__()

        self.polls_tracker = PollsTracker()
        self.number_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    @nextcord.slash_command(
        name="sondage",
        dm_permission=False,
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def poll(self, interaction: nextcord.Interaction):
        """
        Groupe de commandes réservées aux sondages
        """
        pass

    @poll.subcommand(name="temp_vote")
    async def temp_vote(
        self,
        interaction: nextcord.Interaction,
        poll_id=nextcord.SlashOption("id_du_sondage", required=True),
        option=nextcord.SlashOption("option", required=True),
    ):
        self.polls_tracker.vote(poll_id, option, interaction)
        interaction.response.send_message(f"ok, voted for {option}")

    @poll.subcommand(
        name="supprimer", description="Supprime le sondage qui a cette ID."
    )
    async def delete(
        self,
        interaction: nextcord.Interaction,
        poll_id=nextcord.SlashOption(
            "id_du_sondage", "L'ID du sondage à supprimer", True
        ),
    ):
        if await self.polls_tracker.delete_poll(int(poll_id), interaction):
            await interaction.response.send_message(
                f"Supprimé avec succès le sondage {poll_id}.", ephemeral=True
            )

    @poll.subcommand(name="créer", description="Créer un sondage.")
    async def new(
        self,
        interaction: nextcord.Interaction,
        title=nextcord.SlashOption("titre", "Titre du sondage", True),
        options=nextcord.SlashOption(
            "options", 'Toutes les réponses séparées par ";"', True
        ),
        multiple_votes_allowed=nextcord.SlashOption(
            "autoriser_plusieurs_votes",
            "Autoriser plusieurs votes par personne ? Les utilisateurs pourront sélectionner plusieurs réponses",
            True,
            choices={"Oui": "1", "Non": "0"},
        ),
    ):

        list_options = options.split(";")

        formated_options: str = ""
        number = 0
        for option in list_options:
            formated_options += self.number_emojis[number] + " "
            formated_options += option + "\n"
            number += 1

        # view = polls_buttons.get_view(len(list_options))

        poll_message: nextcord.Message = await interaction.response.send_message(
            embed=nextcord.Embed(
                title=title,
                description=formated_options,
                colour=0x3498DB,
            ),
        )

        self.polls_tracker.new_poll(
            Poll(
                self.polls_tracker.get_new_id(),
                title,
                list_options,
                poll_message,
                multiple_votes_allowed == 1,
            )
        )
