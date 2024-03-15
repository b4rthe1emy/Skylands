import nextcord
from nextcord.ext import commands
from rich import print
import dotenv
from utils import time_utils

WELCOME_CHANNEL_ID = int(dotenv.get_key(dotenv.find_dotenv(), "WELCOME_CHANNEL_ID"))
SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))
MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MEMBER_ROLE_ID"))


class MemberJoin(commands.Cog):
    bot: nextcord.Client

    @property
    def welcome_channel(self):
        return self.bot.get_channel(WELCOME_CHANNEL_ID)

    @property
    def skylands_guild(self):
        return self.bot.get_guild(SKYLANDS_GUILD_ID)

    async def send_welcome_message(self, member: nextcord.Member):
        embed = nextcord.Embed(
            color=0x3498DB,
            title="**Bienvenue sur Skylands**",
            url="https://skylandsmc.fr",
            timestamp=time_utils.to_datetime(),
        )
        embed.add_field(
            name=f"🛬 Bienvenue **{member.global_name}**, amuse toi bien sur 𝐒𝐤𝐲𝐥𝐚𝐧𝐝𝐬 ! *(tu es le membre #{self.skylands_guild.member_count})*",
            value="Tu peux lier ton compte Minecraft avec ton compte Discord en tapant la commande `/link` en jeu.",
        )

        await self.welcome_channel.send(
            member.mention,
            embed=embed,
            file=nextcord.File(
                open(
                    "/home/barth/Documents/GitHub/Skylands/assets/skylands_welcome.png",
                    "rb",
                ),
                "image_welcome.png",
                description="L'image de bienvenue accompagnée du message.",
            ),
        )

    @nextcord.slash_command(
        "welcome",
        "Envoie le message de bienvenue",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def welcome(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            "utilisateur", "L'utilisateur à souhaiter la bienvenue."
        ),
    ):
        await self.send_welcome_message(member)
        await interaction.response.send_message(
            f"Bienvenue souhaitée à {member.mention}.", ephemeral=True
        )

    def __init__(self, bot: nextcord.Client) -> None:
        self.bot: commands.Bot = bot

        @self.bot.event
        async def on_member_join(member: nextcord.Member):
            await self.send_welcome_message(member)
            # await member.add_roles(self.skylands_guild.get_role(MEMBER_ROLE_ID))
