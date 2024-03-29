import nextcord
from rich import print


class RecruitmentForm(nextcord.ui.Modal):
    async def callback(self, interaction: nextcord.Interaction):
        print([item.value for item in self.items])
        await interaction.response.send_message(
            "Ça fait rien pour l'instant...", ephemeral=True
        )

    def __init__(self) -> None:
        super().__init__(title="Recrutement")

        # Pseudo Minecraft
        # Prénom
        # Âge
        # Disponibilité (beaucoup/pas beaucoup...)
        # Depuis combien de temps environ joues-tu à Minecraft ?
        # En quoi peux-tu nous aider (modération, build, développeur...) ?
        # Pourquoi Skylands ?

        first_name = nextcord.ui.TextInput(
            "Prénom",
            style=nextcord.TextInputStyle.short,
            required=True,
            placeholder="Le nom de famille n'est pas demandé",
        )
        mc_username = nextcord.ui.TextInput(
            "Pseudo Minecraft",
            style=nextcord.TextInputStyle.short,
            required=True,
        )
        age: int = nextcord.ui.TextInput(
            "Âge",
            style=nextcord.TextInputStyle.short,
            required=True,
            placeholder="Nombre entier compris entre 1 et 99",
            max_length=2,
        )
        availability_time_in_mc = nextcord.ui.TextInput(
            "Disponibilité et depuis quand sur Minecraft ?",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            placeholder="Disponibilité: ex : beaucoup, moyen, pas beaucoup...\nDepuis quand sur Minecraft: ex : 1 an, 4 ans...",
        )
        how_help_why_skylands = nextcord.ui.TextInput(
            "En quoi nous aider et pourquoi Skylands ?",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            placeholder="En quoi ? : ex : modération, build, développeur...\nPourquoi ? : ex : Je veux vous aider car...",
        )

        self.items: list[nextcord.ui.TextInput] = [
            first_name,
            mc_username,
            age,
            availability_time_in_mc,
            how_help_why_skylands,
        ]
        [self.add_item(item) for item in self.items]
