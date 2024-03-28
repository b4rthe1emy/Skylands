import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

OWNER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "OWNER_ROLE_ID"))
ADMIN_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "ADMIN_ROLE_ID"))
ASSISTANT_GERANT = int(dotenv.get_key(dotenv.find_dotenv(), "ASSISTANT_GERANT"))
MODO_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MODO_ROLE_ID"))
DEV_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "DEV_ROLE_ID"))
WEB_DEV_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "WEB_DEV_ROLE_ID"))
BUILDER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "BUILDER_ROLE_ID"))
ANIMATOR_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "ANIMATOR_ROLE_ID"))
GUIDE_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "GUIDE_ROLE_ID"))
DISCORD_STAFF_ROLE_ID = int(
    dotenv.get_key(dotenv.find_dotenv(), "DISCORD_STAFF_ROLE_ID")
)
YOUTUBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "YOUTUBER_ROLE_ID"))
STREAMER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "STREAMER_ROLE_ID"))
MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MEMBER_ROLE_ID"))
MUTED_MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MUTED_MEMBER_ROLE_ID"))
SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))

ROLE_PREFIXS: dict[int, str | None] = {
    OWNER_ROLE_ID: "Gérant",
    ADMIN_ROLE_ID: "Admin",
    MODO_ROLE_ID: "Modo",
    DEV_ROLE_ID: "Dev",
    WEB_DEV_ROLE_ID: "Dev Web",
    BUILDER_ROLE_ID: "Builder",
    ANIMATOR_ROLE_ID: "Animateur",
    GUIDE_ROLE_ID: "Guide",
    DISCORD_STAFF_ROLE_ID: "Ed",
    YOUTUBER_ROLE_ID: "YT",
    STREAMER_ROLE_ID: "Streameur",
    MUTED_MEMBER_ROLE_ID: "MUET",
}


class PrefixesCommands(commands.Cog):
    @property
    def server(self):
        return self.bot.get_guild(SKYLANDS_GUILD_ID)

    @property
    def skip_role_ids(self):
        return [role_id for role_id in ROLE_PREFIXS if ROLE_PREFIXS[role_id] is None]

    @nextcord.slash_command(
        "préfixe",
        "Groupe de commandes réservées à la gestion des préfixes.",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def prefix(self, interaction: nextcord.Interaction):
        pass

    @prefix.subcommand(
        "actualiser_tout_le_monde",
        "Actualise le préfixe de tous les membres du serveur.",
    )
    async def refresh_everyone_command(self, interaction: nextcord.Interaction):
        member_count = interaction.guild.member_count
        await interaction.response.send_message(
            f'Actualisation de {member_count} membre{"s" if member_count >= 2 else ""}, cela peut prendre du temps.',
            ephemeral=True,
        )
        self.refresh_everyone(interaction.guild)

    async def refresh_everyone(self, guild: nextcord.Guild):
        for user in guild.members:
            try:
                await self.update_prefix(user)
            except nextcord.errors.Forbidden:
                pass

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot

        @bot.event
        async def on_member_update(before: nextcord.Member, after: nextcord.Member):
            if before.roles == after.roles:
                return

            await self.update_prefix(after)

        @bot.user_command(
            "préfixe actualiser",
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
        if user.bot:
            return
        if self.server.owner == user:
            return

        roles = user.roles.copy()

        if MUTED_MEMBER_ROLE_ID in [role.id for role in roles]:
            await user.edit(
                nick=f"{ROLE_PREFIXS[MUTED_MEMBER_ROLE_ID]} | {user.global_name}"
            )
            return

        roles.reverse()

        for role in roles:
            try:
                prefix = ROLE_PREFIXS[role.id]
                if prefix is not None:
                    break

            except KeyError:
                prefix = None

        if prefix is not None:
            print(
                f"Updating [on cornflower_blue] @{user.global_name or user.name} [/on cornflower_blue]'s prefix."
            )
            nick = f"{prefix} | {user.global_name or user.name}"
            await user.edit(nick=nick)
        else:
            await user.edit(nick=None)
