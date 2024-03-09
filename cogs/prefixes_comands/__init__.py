import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

OWNER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "OWNER_ROLE_ID"))
SYS_STAFF_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SYS_STAFF_ROLE_ID"))
ADMIN_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "ADMIN_ROLE_ID"))
MODO_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MODO_ROLE_ID"))
DEV_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "DEV_ROLE_ID"))
WEB_DEV_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "WEB_DEV_ROLE_ID"))
BUILDER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "BUILDER_ROLE_ID"))
ANIMATOR_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "ANIMATOR_ROLE_ID"))
GUIDE_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "GUIDE_ROLE_ID"))
DISCORD_STAFF_ROLE_ID = int(
    dotenv.get_key(dotenv.find_dotenv(), "DISCORD_STAFF_ROLE_ID")
)
STAFF_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "STAFF_ROLE_ID"))
YOUTUBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "YOUTUBER_ROLE_ID"))
STREAMER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "STREAMER_ROLE_ID"))
BOOSTER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "BOOSTER_ROLE_ID"))
FRIEND_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "FRIEND_ROLE_ID"))
MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MEMBER_ROLE_ID"))
MUTED_MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MUTED_MEMBER_ROLE_ID"))
NON_VERIFIED_MEMBER_ROLE_ID = int(
    dotenv.get_key(dotenv.find_dotenv(), "NON_VERIFIED_MEMBER_ROLE_ID")
)

SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))

ROLE_PREFIXS: dict[int, str | None] = {
    OWNER_ROLE_ID: "Gérant",
    SYS_STAFF_ROLE_ID: None,
    ADMIN_ROLE_ID: "Admin",
    MODO_ROLE_ID: "Modo",
    DEV_ROLE_ID: "Dev",
    WEB_DEV_ROLE_ID: "Dev Web",
    BUILDER_ROLE_ID: "Builder",
    ANIMATOR_ROLE_ID: "Animateur",
    GUIDE_ROLE_ID: "Guide",
    DISCORD_STAFF_ROLE_ID: "Ed",
    STAFF_ROLE_ID: None,
    YOUTUBER_ROLE_ID: "YT",
    STREAMER_ROLE_ID: "Streameur",
    BOOSTER_ROLE_ID: None,
    FRIEND_ROLE_ID: None,
    MEMBER_ROLE_ID: None,
    MUTED_MEMBER_ROLE_ID: "MUET",
    NON_VERIFIED_MEMBER_ROLE_ID: None,
}


class PrefixesCommands(commands.Cog):
    @property
    def server(self):
        return self.bot.get_guild(SKYLANDS_GUILD_ID)

    @property
    def skip_role_ids(self):
        return [role_id for role_id in ROLE_PREFIXS if ROLE_PREFIXS[role_id] is None]

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot

        @bot.event
        async def on_member_update(before: nextcord.Member, after: nextcord.Member):
            if before.roles == after.roles:
                return

            await self.update_prefix(after)

        @bot.user_command(
            "actualiser le préfixe",
            default_member_permissions=nextcord.Permissions(134217728),
        )
        async def refresh(
            interaction: nextcord.Interaction,
            user: nextcord.Member = nextcord.SlashOption(
                "utilisateur", "L'utilisateur à actualiser le préfixe."
            ),
        ):

            if self.server.owner == user:
                await interaction.response.send_message(
                    "Je ne peux pas changer le pseudo du propriétaire du serveur ca je n'en ai pas la permission.",
                    ephemeral=True,
                )
                return

            if ADMIN_ROLE_ID in [role.id for role in user.roles]:
                await interaction.response.send_message(
                    "Je ne peux pas changer le pseudo d'un administrateur car... bah je sais pas pourquoi en fait mais ça met une erreur donc je te préviens.",
                    ephemeral=True,
                )
                return

            if user.bot:
                await interaction.response.send_message(
                    "Je ne peux pas changer le pseudo d'un bot car ses fonctionnalités pourraient se casser. Change son pseudo manuellement si tu en as vraiment envie.",
                    ephemeral=True,
                )
                return

            await self.update_prefix(user)

            await interaction.response.send_message(
                f"Le préfixe de l'utilisateur {user.mention} a été actualisé.",
                ephemeral=True,
            )

    async def update_prefix(self, user: nextcord.Member):
        role_ids = [role.id for role in user.roles.copy()]
        role_ids.pop(0)

        for skip_role_id in self.skip_role_ids:
            if skip_role_id in role_ids:
                role_ids.remove(skip_role_id)

        if len(role_ids):
            biggest_role = self.server.get_role(role_ids[-1])
            try:
                prefix = ROLE_PREFIXS[biggest_role.id]
            except AttributeError:
                return

            await user.edit(nick=f"{prefix} | {user.global_name}")

            if MUTED_MEMBER_ROLE_ID in role_ids:
                await user.edit(
                    nick=f"{ROLE_PREFIXS[MUTED_MEMBER_ROLE_ID]} | {user.global_name}"
                )

        else:
            await user.edit(nick=None)
