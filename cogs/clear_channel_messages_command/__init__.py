import nextcord
from nextcord.ext import commands
from rich import print


class ClearChannelMessagesCommand(commands.Cog):
    @nextcord.slash_command("clear_salon")
    async def clear_salon(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "Tous les messages de ce salon vont être supprimés. Cette opération peut prendre longtemps, merci de patienter.",
            ephemeral=True,
        )
        await interaction.channel.purge()
