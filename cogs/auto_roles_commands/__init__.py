import nextcord
from nextcord.ext import commands
from rich import print
from .auto_roles_tracker import *


class AutoRolesCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.tracker = auto_roles_tracker.AutoRolesTracker(bot)

    @nextcord.slash_command(
        "auto_rôle",
        "Groupe de commandes réservées à la gestion des auto-rôles.",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def auto_rôle(self, interaction: nextcord.Interaction):
        pass

    @auto_rôle.subcommand("supprimer", "Supprime l'auto-rôle qui a ce nom")
    async def delete(
        self,
        interaction: nextcord.Interaction,
        auto_role_name: str = nextcord.SlashOption(
            "nom_de_l_auto_role",
            "Le nom de l'auto-rôle à supprimer",
        ),
    ):
        await self.tracker.delete_auto_role(auto_role_name, interaction)

    @auto_rôle.subcommand(
        "créer",
        "Crée un auto-rôle.",
    )
    async def new(
        self,
        interaction: nextcord.Interaction,
        role_id=nextcord.SlashOption(
            "id_du_rôle",
            "L'ID du rôle à attribuer quand l'utilisateur clique sur le bouton",
        ),
        name: str = nextcord.SlashOption(
            "nom",
            "Le nom du rôle.",
        ),
        button_color: str = nextcord.SlashOption(
            "couleur_du_bouton",
            "La couleur du bouton",
            choices={"Bleu-violet": "1", "Gris": "2", "Vert": "3", "Rouge": "4"},
        ),
    ):
        if not await self.tracker.add_auto_role(
            auto_roles_tracker.AutoRole(name, button_color, int(role_id)), interaction
        ):
            await self.tracker.send_message(interaction, ephemeral=True)

    @auto_rôle.subcommand(
        "renvoyer_message",
        "Renvoie le message explicatif avec des boutons pour s'inscrire ou se désinscrire.",
    )
    async def resend_message(self, interaction: nextcord.Interaction):
        await self.tracker.send_message(interaction)
        await interaction.response.send_message(
            "Le message a été renvoyé.", ephemeral=True
        )
