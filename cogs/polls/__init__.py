import nextcord
from nextcord.ext import commands
from rich import print

import dotenv

from .polls_tracker import *


dotenv_file = dotenv.find_dotenv()
ADMIN_ROLE_ID = str(dotenv.get_key(dotenv_file, "ADMIN_ROLE_ID"))


class Poll(commands.Cog):
    """
    Poll commands cog.
    """

    number_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

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
        name="supprimer", description="Supprime le sondage qui a cette ID."
    )
    async def delete(
        self,
        interaction: nextcord.Interaction,
        poll_id=nextcord.SlashOption(
            "id_du_sondage", "L'ID du sondage à supprimer", True
        ),
    ):
        await interaction.response.send_message("`NotImplementedError`")
        raise NotImplementedError()

    @poll.subcommand(name="créer", description="Créer un sondage avec une ID.")
    async def new(
        self,
        interaction: nextcord.Interaction,
        title=nextcord.SlashOption("titre", "Titre du sondage", True),
        poll_id=nextcord.SlashOption(
            "id_du_sondage",
            "Nombre entier UNIQUE, l'ID du sondage sert à l'identifier",
            True,
        ),
        options=nextcord.SlashOption(
            "options", 'Toutes les réponses séparées par ";"', True
        ),
        multiple_votes_allowed=nextcord.SlashOption(
            "autoriser_plusieurs_votes",
            "Autoriser plusieurs votes par personne ? Les utilisateurs pourront sélectionner plusieurs réponses",
            True,
            choices={"Oui": "1", "Non": "0"},
            # default="1",
        ),
    ):

        try:
            if ADMIN_ROLE_ID in interaction.message.author.roles:
                await interaction.response.send_message(
                    f"Uniquement les admistraturs peuvent envoyer des sondages.",
                    silent=True,
                    reference=interaction.message,
                    ephemeral=True,
                )
                return
        except Exception as e:
            print(
                f"[red][bold]Error during admin role checking:[/bold] {type(e).__name__}: {e}[/red]"
            )

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
            # view=view(int(poll_id)),
        )

        polls_tracker.create_poll(poll_message, int(poll_id), len(list_options))
