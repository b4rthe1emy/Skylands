import nextcord
from rich import print
from nextcord.ext import commands
import dotenv


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def send_rules(self, channel: nextcord.TextChannel, edit: bool = False):
        with open("cogs/rules_message/rules.md", "rt", encoding="utf8") as rules_file:
            rules: str = rules_file.read()

        embed = nextcord.Embed(
            title="Règlement de Skylands",
            description=rules,
        )

        if edit:
            messages = await channel.history().flatten()
            messages = [msg for msg in messages if msg.author == self.bot.user]
            try:
                last_bot_msg: nextcord.Message = messages[0]
            except IndexError:
                action = channel.send
            else:
                action = last_bot_msg.edit

        else:
            action = channel.send

        await action(embed=embed)

    @nextcord.slash_command(
        "envoyer_règles",
        "Envoie le message des règles",
        dm_permission=False,
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def send_rules_command(
        self,
        interaction: nextcord.Interaction,
        edit=nextcord.SlashOption(
            "modifier_existant",
            "Si Oui, le dernier message envoyé par le bot va être "
            "modifié, sinon, le message va être renvoyé",
            default="Oui",
            choices={"Oui": "Oui", "Non": "Non"},
        ),
    ):
        await self.send_rules(interaction.channel, edit=(edit == "Oui"))
        await interaction.response.send_message("✅ Succès", ephemeral=True)
