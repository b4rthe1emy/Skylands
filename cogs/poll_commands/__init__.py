import nextcord
from nextcord.ext import commands
from rich import print
import time
import dotenv

from .polls_tracker import *
from .poll_buttons import *

dotenv_file = dotenv.find_dotenv()
ADMIN_ROLE_ID = str(dotenv.get_key(dotenv_file, "ADMIN_ROLE_ID"))
ADMIN_ONLY_CHANNEL_ID = int(dotenv.get_key(dotenv_file, "ADMIN_ONLY_CHANNEL_ID"))


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

    @poll.subcommand(name="créer", description="Crée un sondage.")
    async def new(
        self,
        interaction: nextcord.Interaction,
        title=nextcord.SlashOption("titre", "Titre du sondage", True),
        options=nextcord.SlashOption(
            "options", 'Les options séparées par ";" et ENTRES GUILLEMETS', True
        ),
        multiple_votes_allowed=nextcord.SlashOption(
            "autoriser_plusieurs_votes",
            "Autoriser plusieurs votes par personne ? Les utilisateurs pourront sélectionner plusieurs réponses",
            True,
            choices={"Oui": "1", "Non": "0"},
        ),
        end: float = nextcord.SlashOption(
            "fin_automatique_en_heures",
            "Le sondage se terminera automatiquement au bout de cette durée. ex: 6.5 -> 6 heures et 30 min",
            False,
        ),
    ):
        if options[0] != '"' or options[-1] != '"':
            await interaction.response.send_message(
                "Les options doivent être entre guillemets, comme indiqué dans la description de l'argument.",
                ephemeral=True,
            )
            return

        # options = options[1:-1]
        # list_options: list[str] = options.split(";")

        # formated_options: str = ""
        # number = 0
        # custom_emojis: list[str] = []
        # for option in list_options:

        #     if option.startswith(" "):
        #         formated_options += self.number_emojis[number]
        #         formated_options += option + "\n"
        #         custom_emojis.append(self.number_emojis[number])
        #     else:
        #         formated_options += option + "\n"
        #         custom_emojis.append(option[0])

        #     number += 1

        # poll_id = self.polls_tracker.get_new_id()

        # view = get_view(len(list_options) - 1)(
        #     poll_id,
        #     self.polls_tracker,
        #     custom_emojis,
        # )
        embed, view, formated_options, list_options, poll_id = (
            get_poll_message_embed_and_view(
                self, title, options, self.polls_tracker.get_new_id()
            )
        )
        try:
            message = await interaction.channel.send(embed=embed, view=view)
        except nextcord.errors.HTTPException:

            await interaction.response.send_message(
                "Un ou plusieurs des émojis que tu as entré : "
                + ", ".join(
                    [
                        (option[0] if option[0] != " " else "<aucun>")
                        for option in list_options
                    ]
                )
                + ", ne sont pas un/des émoji(s) valide(s). Si tu veux les nombres de base (0️⃣, 1️⃣, 2️⃣...) mets un espace avant l'option.",
                ephemeral=True,
            )
            return

        if end is not None:
            end_timestamp = time.time() + (float(end) * 3600)
        else:
            end_timestamp = 0

        await self.polls_tracker.new_poll(
            Poll(
                poll_id,
                title,
                list_options,
                multiple_votes_allowed == "1",
                end_timestamp,
            ),
            interaction,
        )
        embed = get_control_panel_embed(
            title, poll_id, len(list_options), multiple_votes_allowed
        )
        await interaction.guild.get_channel(ADMIN_ONLY_CHANNEL_ID).send(
            embed=embed,
            view=PollButtonsControlPannel(
                poll_id, self.polls_tracker, message.id, message.channel.id
            ),
        )

        await interaction.response.send_message("Sondage créé.", ephemeral=True)
