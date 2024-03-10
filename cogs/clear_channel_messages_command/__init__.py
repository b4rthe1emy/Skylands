import nextcord
from nextcord.ext import commands
from rich import print


class ClearChannelMessagesCommand(commands.Cog):
    @nextcord.slash_command(
        "supprimer_les_messages",
        "ATTENTION: SUPPRIME TOUS LES MESSAGES DU SALON. À UTILISER UNIQUEMENT SI TU SAIS CE QUE TU FAIS!!!",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def clear_salon(
        self,
        interaction: nextcord.Interaction,
        sure: bool = nextcord.SlashOption(
            "sûr", "T'ES VRAIMENT SÛR???", default=False, required=False
        ),
    ):
        if sure:
            await interaction.response.send_message(
                "Les 100 derniers messages de ce salon vont être supprimés. Cette opération peut prendre longtemps, merci de patienter.",
                ephemeral=True,
            )
            await interaction.channel.purge()
        else:
            await interaction.response.send_message(
                "Met l'option `sûr` à Vrai si tu es vraiment sûr.", ephemeral=True
            )
