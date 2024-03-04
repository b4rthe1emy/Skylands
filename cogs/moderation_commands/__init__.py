import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

MUTED_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MUTED_MEMBER_ROLE_ID"))
MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MEMBER_ROLE_ID"))
ADMIN_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "ADMIN_ROLE_ID"))

SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))


class ModerationCommands(commands.Cog):

    def __init__(self, bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot

    @property
    def server(self):
        return self.bot.get_guild(SKYLANDS_GUILD_ID)

    async def handle_mute_member_errors(
        self, member: nextcord.Member, interaction: nextcord.Interaction
    ):
        member_role_ids = [role.id for role in member.roles]
        muted_role = self.server.get_role(MUTED_ROLE_ID)
        member_role = self.server.get_role(MEMBER_ROLE_ID)

        if MUTED_ROLE_ID in member_role_ids and MEMBER_ROLE_ID in member_role_ids:
            await interaction.response.send_message(
                f"# Erreur\nL'utilisateur a le rôle {muted_role.mention} **et** le rôle {member_role.mention}, ce qui n'est pas possible.\nEssaye d'en enlever un et réessaye car il peut en avoir qu'un seul à la fois.",
                ephemeral=True,
            )
            return True

        if (
            MUTED_ROLE_ID not in member_role_ids
            and MEMBER_ROLE_ID not in member_role_ids
        ):
            await interaction.response.send_message(
                f"# Erreur\nL'utilisateur n'a **ni** le rôle {muted_role.mention} **ni** le rôle {member_role.mention}, ce qui n'est pas possible.\nEssaye de lui rajouter le rôle {member_role.mention} et réessaye.",
                ephemeral=True,
            )
            return True

        if ADMIN_ROLE_ID in member_role_ids:
            await interaction.response.send_message(
                "Je ne peux pas rendre muet un administrateur car... bah je sais pas pourquoi en fait mais ça met une erreur donc je te préviens.",
                ephemeral=True,
            )
            return True

        return False

    @nextcord.user_command(
        "interdire de parler",
        dm_permission=False,
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def mute(self, interaction: nextcord.Interaction, member: nextcord.Member):
        member_role_ids = [role.id for role in member.roles]

        if self.server.owner == member:
            await interaction.response.send_message(
                "Je ne peux pas rendre muet le propriétaire du serveur ca je n'en ai pas la permission.",
                ephemeral=True,
            )
            return

        if member.bot:
            await interaction.response.send_message(
                "Je ne peux pas rendre muet un bot car ses fonctionnalités riquent de se casser.",
                ephemeral=True,
            )
            return

        error_happended = await self.handle_mute_member_errors(member, interaction)
        if error_happended:
            return

        if MUTED_ROLE_ID in member_role_ids and MEMBER_ROLE_ID not in member_role_ids:
            await interaction.response.send_message(
                f"{member.mention} est déjà muet. Utilise `laisser parler` pour l'autoriser à parler.",
                ephemeral=True,
            )
            return

        muted_role = self.server.get_role(MUTED_ROLE_ID)
        member_role = self.server.get_role(MEMBER_ROLE_ID)

        await member.remove_roles(member_role)
        await member.add_roles(muted_role)

        await member.edit(nick=("[MUET] " + member.global_name))

        await interaction.response.send_message(
            f"L'utilisateur {member.mention} ne peux maintenant plus parler.",
            ephemeral=True,
        )

    @nextcord.user_command(name="laisser parler")
    async def unmute(self, interaction: nextcord.Interaction, member: nextcord.Member):
        error_happended = await self.handle_mute_member_errors(member, interaction)
        if error_happended:
            return

        member_role_ids = [role.id for role in member.roles]

        if MUTED_ROLE_ID not in member_role_ids and MEMBER_ROLE_ID in member_role_ids:
            await interaction.response.send_message(
                f"{member.mention} est déjà non muet. Utilise `interdire de parler` pour l'interdire de parler.",
                ephemeral=True,
            )
            return

        muted_role = self.server.get_role(MUTED_ROLE_ID)
        member_role = self.server.get_role(MEMBER_ROLE_ID)

        await member.remove_roles(muted_role)
        await member.add_roles(member_role)

        await member.edit(nick=None)

        await interaction.response.send_message(
            f"L'utilisateur {member.mention} peux maintenant parler.",
            ephemeral=True,
        )
