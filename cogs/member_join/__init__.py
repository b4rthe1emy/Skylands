import nextcord
from nextcord.ext import commands
from rich import print
import dotenv
from utils import time_utils
import cogs.member_join.image_generator as img_gen
import cogs.invitations as invitations

from captcha.image import ImageCaptcha
import random


WELCOME_CHANNEL_ID = int(dotenv.get_key(dotenv.find_dotenv(), "WELCOME_CHANNEL_ID"))
SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))
NON_VERIFIED_MEMBER_ROLE_ID = int(
    dotenv.get_key(dotenv.find_dotenv(), "NON_VERIFIED_MEMBER_ROLE_ID")
)
MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MEMBER_ROLE_ID"))
CAPTCHA_CHANNEL_ID = int(dotenv.get_key(dotenv.find_dotenv(), "CAPTCHA_CHANNEL_ID"))
WELCOME_IMAGE_FILE_PATH = dotenv.get_key(
    dotenv.find_dotenv(), "WELCOME_IMAGE_FILE_PATH"
)


class MemberJoin(commands.Cog):
    def __init__(self, bot: nextcord.Client) -> None:
        self.bot: commands.Bot = bot

        @bot.event
        async def on_member_join(member: nextcord.Member):
            await self.send_welcome_message(member)
            await member.add_roles(
                self.skylands_guild.get_role(NON_VERIFIED_MEMBER_ROLE_ID)
            )

        @bot.event
        async def on_member_remove(member: nextcord.Member):
            await self.invites_tracker.update_invites(member)

        self.invites_tracker = invitations.Tracker(self.bot)

    @property
    def welcome_channel(self):
        return self.bot.get_channel(WELCOME_CHANNEL_ID)

    @property
    def skylands_guild(self):
        return self.bot.get_guild(SKYLANDS_GUILD_ID)

    async def send_welcome_message(self, member: nextcord.Member):
        try:
            invite = await self.invites_tracker.get_invite_of_member(member)
        except Exception as e:
            invite = None
            from types import TracebackType

            print(
                f"[red bold]Error while getting @{member.name}'s join method[/red bold]: "
                + str(e)
            )

        msg_content = "Tu peux lier ton compte Minecraft avec ton compte Discord en tapant la commande `/link` en jeu."

        if invite is not None:
            msg_content += "\n\nTu as été invité par " + (
                invite.inviter.global_name or invite.inviter.name
            )

        embed = nextcord.Embed(
            color=0x3498DB,
            title="**Bienvenue sur Skylands**",
            url="https://skylandsmc.fr",
            timestamp=time_utils.to_datetime(),
        )
        embed.add_field(
            name=(
                f"🛬 Bienvenue **{member.global_name}**, amuse toi bien sur 𝐒𝐤𝐲𝐥𝐚𝐧𝐝𝐬 ! *(tu es le membre #"
                + str(self.skylands_guild.member_count)
                + ")*"
            ),
            value=msg_content,
        )

        await img_gen.generate_welcome_image(member)

        await self.welcome_channel.send(
            member.mention,
            embed=embed,
            file=nextcord.File(
                open(
                    WELCOME_IMAGE_FILE_PATH,
                    "rb",
                ),
                "image.png",
            ),
        )

        text = ""
        for i in range(5):
            text += random.choice(
                "abcdefghijklmnopqrstuvwxyz"  # ABCDEFGHIJKLMNOPQRSTUVWXYZ
            )
        image = ImageCaptcha(250, 100).generate(text)

        view = nextcord.ui.View(timeout=None)

        button = nextcord.ui.Button(label="Clique ICI pour faire le captcha")
        modal = nextcord.ui.Modal("CAPTCHA")

        modal.text_input = nextcord.ui.TextInput("CAPTCHA", required=True)

        modal.add_item(modal.text_input)

        async def modal_callback(interaction: nextcord.Interaction):
            if modal.text_input.value == text:
                await interaction.message.delete()
                await interaction.user.remove_roles(
                    self.skylands_guild.get_role(NON_VERIFIED_MEMBER_ROLE_ID)
                )
                await interaction.user.add_roles(
                    self.skylands_guild.get_role(MEMBER_ROLE_ID)
                )
            else:
                await interaction.response.send_message(
                    "CAPTCHA incorrect.", ephemeral=True
                )

        modal.callback = modal_callback

        async def button_callback(interaction: nextcord.Interaction):
            if interaction.user.id != member.id:
                await interaction.response.send_message(
                    f"Y'a que {member.mention} qui peut faire le CAPTCHA.",
                    ephemeral=True,
                )
                return
            await interaction.response.send_modal(modal)

        button.callback = button_callback

        view.add_item(button)

        await self.bot.get_channel(CAPTCHA_CHANNEL_ID).send(
            member.mention + " Complète ce CAPTCHA pour avoir accès au serveur.",
            file=nextcord.File(image, "captcha.png"),
            view=view,
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
