from discord import ButtonStyle, Emoji, PartialEmoji
import nextcord
from nextcord.ext import commands
from rich import print
import dotenv
import json

NOTIFS_CHANNEL_ID = int(dotenv.get_key(dotenv.find_dotenv(), "NOTIFS_CHANNEL_ID"))
AUTO_ROLES_FILE_PATH = dotenv.get_key(dotenv.find_dotenv(), "AUTO_ROLES_FILE_PATH")


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

                if not has_role:
                    await interaction.user.add_roles(
                        interaction.guild.get_role(role_id)
                    )
                else:
                    await interaction.user.remove_roles(
                        interaction.guild.get_role(role_id)
                    )

                print(auto_role)

            button = nextcord.ui.Button(
                label=auto_role["name"],
                custom_id=(
                    "auto_role_button_"
                    + str(auto_role["name"])
                    + "_"
                    + str(auto_role["role_id"])
                ),
            )
            button.callback = lambda interaction: callback(interaction, auto_role)
            self.add_item(button)


class AutoRolesTracker:
    def __init__(self) -> None:
        self.auto_roles_file: str = AUTO_ROLES_FILE_PATH

    @property
    def auto_roles(self) -> list[dict]:
        with open(self.auto_roles_file, mode="r") as file:
            auto_roles = json.loads(file.read())
        return auto_roles

    async def add_category(
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

        guild = interaction.guild
        channel = guild.get_channel(NOTIFS_CHANNEL_ID)

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
            await interaction.response.send_message(
                "Voici un apercu des auto-rôles. Utilise </auto_rôle renvoyer_message:1216310345673478246> pour renvoyer le message.",
                embed=embed,
                ephemeral=True,
            )
        else:
            await channel.send(embed=embed, view=view)
