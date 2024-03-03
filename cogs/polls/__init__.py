import nextcord
from nextcord.ext import commands
from rich import print
import datetime
import dotenv

from .polls_tracker import *
from .poll_buttons import *

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

    @poll.subcommand(
        name="résultats",
        description="Affiche le nombre de votes pour chaque option du sondage qui a cette ID.",
    )
    async def results(
        self,
        interaction: nextcord.Interaction,
        poll_id=nextcord.SlashOption(
            "id_du_sondage", "L'ID du sondage à voir les résultats", True
        ),
    ):
        await self.polls_tracker.poll_results(poll_id, interaction)

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

        list_options: list[str] = options.split(";")

        formated_options: str = ""
        number = 0
        custom_emojis: list[str] = []
        for option in list_options:

            if option.startswith(" "):
                formated_options += self.number_emojis[number]
                formated_options += option + "\n"
                custom_emojis.append(self.number_emojis[number])
            else:
                formated_options += option + "\n"
                custom_emojis.append(option[0])

            number += 1

        poll_id = self.polls_tracker.get_new_id()

        view = get_view(len(list_options) - 1)(
            poll_id,
            self.polls_tracker,
            custom_emojis,
        )

        poll_message: nextcord.Message = await interaction.response.send_message(
            embed=nextcord.Embed(
                title=title,
                description=formated_options,
                colour=0x3498DB,
            ),
            view=view,
        )

        await self.polls_tracker.new_poll(
            Poll(
                poll_id,
                title,
                list_options,
                multiple_votes_allowed == "1",
            )
        )
