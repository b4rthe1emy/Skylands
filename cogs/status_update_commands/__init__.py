import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

STATUS_CHANNEL_ID = dotenv.get_key(dotenv.find_dotenv(), "STATUS_CHANNEL_ID")


class StatusUpdateCommands(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.status_emojis = ["🟢", "🟠", "🔴"]
        self.status_colors = [0x78B159, 0xF4900C, 0xDD2E44]
        self.status_names = ["En Ligne", "En Maintenance", "Fermé"]
        self.status_descriptions = [
            "Profitez du serveur !",
            "Le serveur est temporairement indisponnible.",
            "Le serveur est complètement fermé pour une longue durée.",
        ]

    @property
    def status_channel(self):
        return self.bot.get_channel(int(STATUS_CHANNEL_ID))

    def get_status_message(self, status: int):
        embed = nextcord.Embed(color=self.status_colors[status])
        embed.add_field(
            name="Les états possibles du serveur :",
            value=f"""

**[ {self.status_emojis[0]} ] {self.status_names[0]} :** {self.status_descriptions[0]}
**[ {self.status_emojis[1]} ] {self.status_names[1]} :** {self.status_descriptions[1]}
**[ {self.status_emojis[2]} ] {self.status_names[2]} :** {self.status_descriptions[2]}
""",
        )

        return embed

    @nextcord.slash_command(
        name="status",
        dm_permission=False,
        default_member_permissions=nextcord.Permissions(402653184),
    )
    async def status(
        self,
        interaction: nextcord.Interaction,
        status=nextcord.SlashOption(
            "status",
            "Le status du serveur.",
            required=True,
            choices={
                "online": "0",
                "maintenance": "1",
                "offline": "2",
            },
        ),
    ):
        status = int(status)

        await interaction.response.send_message(
            f"Le status du serveur va se mettre à jour. Cela peut prendre plusieurs minutes, merci de patienter.",
            ephemeral=True,
        )

        await self.status_channel.edit(name=f"『{self.status_emojis[status]}』𝐒𝐭𝐚𝐭𝐮𝐬")
        await self.status_channel.purge()
        await self.status_channel.send(
            f"## Status actuel : [ {self.status_emojis[status]} ] {self.status_names[status]} : {self.status_descriptions[status]}",
            embed=self.get_status_message(status),
        )
