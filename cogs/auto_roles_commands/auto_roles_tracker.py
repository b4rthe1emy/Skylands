from discord import ButtonStyle, Emoji, PartialEmoji
import nextcord
from nextcord.ext import commands
from rich import print
import dotenv
import json

AUTO_ROLES_CHANNEL_ID = int(
    dotenv.get_key(dotenv.find_dotenv(), "AUTO_ROLES_CHANNEL_ID")
)
AUTO_ROLES_FILE_PATH = dotenv.get_key(dotenv.find_dotenv(), "AUTO_ROLES_FILE_PATH")
SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))


class AutoRole:
    def __init__(self, name: str, button_color: int, role_id: int) -> None:
        self.name: str = name
        self.button_color: int = button_color
        self.role_id: int = role_id

    @property
    def to_dict(self):
        return {
            "name": self.name,
            "button_color": self.button_color,
            "role_id": self.role_id,
        }


class AutoRolesButtons(nextcord.ui.View):
    def __init__(self, auto_roles: list[dict]) -> None:
        super().__init__(timeout=None, auto_defer=False)
        self.auto_roles: list[dict] = auto_roles

        for auto_role in self.auto_roles:

            async def callback(interaction: nextcord.Interaction, auto_role):
                role_id = auto_role["role_id"]
                has_role = bool(interaction.user.get_role(role_id))

                if has_role:
                    await interaction.user.remove_roles(
                        interaction.guild.get_role(role_id)
                    )
                    await interaction.response.send_message(
                        'Le rôle "' + str(auto_role["name"]) + '" vous a été enlevé.',
                        ephemeral=True,
                    )

                else:
                    try:
                        await interaction.user.add_roles(
                            interaction.guild.get_role(role_id)
                        )
                        await interaction.response.send_message(
                            'Le rôle "'
                            + str(auto_role["name"])
                            + '" vous a été attribué.',
                            ephemeral=True,
                        )
                    except AttributeError:
                        await interaction.response.send_message(
                            "Le rôle n'a pas pu être attribué. Contactez les administrateurs et développeurs dans le salon <#1201270746983440385>.",
                            ephemeral=True,
                        )

            style = int(auto_role["button_color"])

            button = nextcord.ui.Button(
                label=auto_role["name"],
                custom_id=(
                    "auto_role_button_"
                    + str(auto_role["name"])
                    + "_"
                    + str(auto_role["role_id"])
                ),
                style=style,
            )

            async def btn_callback(interaction: nextcord.Interaction):
                await callback(interaction, auto_role)

            button.callback = btn_callback
            self.add_item(button)


class AutoRolesTracker:
    def __init__(self, bot: commands.Bot) -> None:
        self.auto_roles_file: str = AUTO_ROLES_FILE_PATH
        self.bot: commands.Bot = bot

    @property
    def auto_roles(self) -> list[dict]:
        with open(self.auto_roles_file, mode="r") as file:
            auto_roles = json.loads(file.read())
        return auto_roles

    async def add_auto_role(
        self, auto_role: AutoRole, interaction: nextcord.Interaction
    ):
        auto_roles = self.auto_roles
        auto_roles.append(auto_role.to_dict)

        with open(self.auto_roles_file, mode="w") as file:
            file.write(json.dumps(auto_roles))

    async def send_message(
        self, interaction: nextcord.Interaction, ephemeral: bool = False
    ):
        embed = nextcord.Embed(
            title="Notifications", color=0x3498DB, url="https://skylandsmc.fr/"
        )

        channel = self.bot.get_guild(SKYLANDS_GUILD_ID).get_channel(
            AUTO_ROLES_CHANNEL_ID
        )

        embed.add_field(
            name="Choisissez un rôle en cliquant sur les boutons ci-dessous pour recevoir des **notifications** de :",
            value=", ".join([n["name"] for n in self.auto_roles]),
            inline=False,
        )

        embed.add_field(
            name="❓ Pour supprimer votre rôle, il suffit de cliquer à nouveau.",
            value="",
            inline=False,
        )

        view = AutoRolesButtons(self.auto_roles)

        if ephemeral:
            if interaction is not None:
                await interaction.response.send_message(
                    "Voici un apercu des auto-rôles. Utilise </auto_rôle renvoyer_message:1216344424670298283> pour renvoyer le message.",
                    embed=embed,
                    ephemeral=True,
                )
        else:
            return await channel.send(embed=embed, view=view)
