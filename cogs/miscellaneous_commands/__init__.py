import nextcord
from rich import print
from nextcord.ext import commands


class MiscellaneousCommands(commands.Cog):
    @nextcord.slash_command(name="vote", description="Lien pour voter")
    async def vote(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "Viens voter sur 👉 https://skylandsmc.fr/vote 👈 !!!", ephemeral=True
        )

    @nextcord.slash_command(name="ip", description="L'ip du serveur")
    async def ip(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "Venez jouer en 1.20.1 ou +\nsur 👉 `play.skylandsmc.fr` 👈",
            ephemeral=True,
        )

    @nextcord.slash_command(name="site", description="Lien du site de Skylands")
    async def website(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "👉 [Site de Skylands](https://skylandsmc.fr/) 👈",
            ephemeral=True,
        )

    @nextcord.slash_command(name="tiktok", description="Lien tiktok")
    async def tiktok(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "👉 [Tiktok de Skylands](https://tiktok.com/@skylands.fr) 👈 et abonne-toi !",
            ephemeral=True,
        )

    @nextcord.slash_command(name="youtube", description="Lien youtube")
    async def youtube(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "👉 [Youtube de Skylands](https://youtube.com/@skylandsmc.fr-/) 👈 et abonne-toi !",
            ephemeral=True,
        )
