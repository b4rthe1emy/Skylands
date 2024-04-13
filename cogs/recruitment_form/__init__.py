import nextcord
from rich import print
import dotenv
from nextcord.ext import commands

RECRUITEMENT_CHANNEL_ID = int(
    dotenv.get_key(dotenv.find_dotenv(), "RECRUITEMENT_CHANNEL_ID")
)

from cogs.tickets_commands import TicketsCommands


class RecruitmentForm(nextcord.ui.Modal):
    async def send_control_message(
        guild: nextcord.Guild, bot: commands.Bot, edit=False
    ):
        async def button_callback(interaction: nextcord.Interaction):
            confirm_button = nextcord.ui.Button(label="C'est parti !", emoji="📝")

            async def confirm_button_callback(interaction: nextcord.Interaction):
                await interaction.response.send_modal(RecruitmentForm(bot))

            confirm_button.callback = confirm_button_callback
            confirm_view = nextcord.ui.View()
            confirm_view.add_item(confirm_button)
            await interaction.response.send_message(
                embeds=[
                    nextcord.Embed(title="Formulaire recrutement"),
                    nextcord.Embed(
                        title="Attention",
                        description="> Le formulaire que nous utilisons pour recruter du personnel "
                        "sur le serveur Discord Skylands n'a pas pour but de collecter des données "
                        "à des fins de revente ou d'arnaque. Son objectif est de nous assurer que "
                        "tu souhaites véritablement nous aider et que ta participation est motivée "
                        "par un réel intérêt pour notre communauté.",
                    ),
                    nextcord.Embed(
                        title="Tes réponses aux questions seront communiquées au staff",
                        description="> Un ticket sera automatiquement créé lorsque tu finira le formulaire "
                        "et tes réponses aux questions y seront envoyés.\n"
                        "> Merci de répondre correctement aux questions et de rester poli tout au "
                        "long de ta démarche. On compte sur toi!",
                    ),
                ],
                view=confirm_view,
                ephemeral=True,
            )

        button = nextcord.ui.Button(
            label="Remplir le formulaire",
            emoji="📝",
        )

        button.callback = button_callback
        confirm_view = nextcord.ui.View(timeout=None)
        confirm_view.add_item(button)

        if edit:
            messages = (
                await guild.get_channel(RECRUITEMENT_CHANNEL_ID).history().flatten()
            )
            messages = [msg for msg in messages if msg.author == bot.user]
            try:
                last_bot_msg: nextcord.Message = messages[0]
            except IndexError:
                action = guild.get_channel(RECRUITEMENT_CHANNEL_ID).send
            else:
                action = last_bot_msg.edit

        else:
            action = guild.get_channel(RECRUITEMENT_CHANNEL_ID).send

        await action(
            embed=nextcord.Embed(
                title="Formulaire recrutement",
                description="Cliquez sur le bouton pour remplir le formulaire.",
            ),
            view=confirm_view,
        )

    async def callback(self, interaction: nextcord.Interaction):
        values = {item.label: item.value for item in self.items}

        ticket = await TicketsCommands(self.bot).create_ticket(interaction)
        embed = nextcord.Embed(
            title=f"{interaction.user.global_name} veut faire parti du staff!",
            description=f"{interaction.user.mention} a rempli le formulaire de recrutement !\n"
            "Voici ce qu'il a marqué :",
        )
        for value in values:
            embed.add_field(name=value, value=values[value], inline=False)

        await ticket.send(embed=embed)
        # description="**"
        # + str({item.label: item.value for item in self.items})[1:-1]
        # .replace(",", "\n**")
        # .replace("'", "")
        # .replace(":", "** :"),

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(title="Recrutement", timeout=None)
        self.bot: commands.Bot = bot

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
