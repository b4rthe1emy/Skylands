import nextcord
from nextcord.ext import commands
from rich import print


class ClearChannelMessagesCommand(commands.Cog):
    @nextcord.slash_command(
        "supprimer_les_messages",
        "ATTENTION: SUPPRIME TOUS LES MESSAGES DU SALON. À UTILISER UNIQUEMENT SI TU SAIS CE QUE TU FAIS!!!",
        default_member_permissions=nextcord.Permissions(administrator=True),
        dm_permission=False,
    )
    async def clear_salon(
        self,
        interaction: nextcord.Interaction,
        sure=nextcord.SlashOption(
            "sûr",
            "T'ES VRAIMENT SÛR???",
            required=False,
            choices={"Oui": "1", "Non": "0"},
        ),
    ):
        if sure == "1":
            try:
                await interaction.channel.purge()
            except AttributeError:
                await interaction.response.send_message(
                    "Je ne peut pas effacer les messages ici.", ephemeral=True
                )
                return
            await interaction.response.send_message(
                "Les 100 derniers messages de ce salon vont être supprimés. Cette opération peut prendre longtemps, merci de patienter.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Met l'option `sûr` à Oui si tu es vraiment sûr.", ephemeral=True
            )
