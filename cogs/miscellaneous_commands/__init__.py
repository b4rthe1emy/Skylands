import nextcord
from rich import print
from nextcord.ext import commands


class MiscellaneousCommands(commands.Cog):
    @nextcord.slash_command(name="ip")
    async def ip(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "Venez jouer en 1.20.1 ou +\nsur `play.skylandsmc.fr`",
            ephemeral=True,
        )

    @nextcord.slash_command(name="site")
    async def website(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "[Site de Skylands](https://skylandsmc.fr/)",
            ephemeral=True,
        )

    @nextcord.slash_command(name="tiktok")
    async def tiktok(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "[Tiktok de Skylands](https://tiktok.com/@skylands.fr) et abonne-toi !",
            ephemeral=True,
        )

    @nextcord.slash_command(name="youtube")
    async def youtube(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "[Youtube de Skylands](https://youtube.com/@skylandsmc.fr-/) et abonne-toi !",
            ephemeral=True,
        )
