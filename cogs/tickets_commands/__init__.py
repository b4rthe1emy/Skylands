import nextcord
from nextcord.ext import commands
from rich import print
import dotenv
import json

SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))
TICKETS_CATEGORY = int(dotenv.get_key(dotenv.find_dotenv(), "TICKETS_CATEGORY"))
MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MEMBER_ROLE_ID"))


class TicketsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot

    @property
    def server(self):
        return self.bot.get_guild(SKYLANDS_GUILD_ID)

    @property
    def ticket_category(self):
        return [
            category
            for category in self.server.categories
            if category.id == TICKETS_CATEGORY
        ][0]

    def is_ticket(self, channel: nextcord.TextChannel):
        with open("tickets.json", "rt") as ticket_counter_file:
            tickets: list = json.loads(ticket_counter_file.read())

        ticket_ids = [ticket["channel_id"] for ticket in tickets]

        return channel.id in ticket_ids

    @nextcord.slash_command(
        "ticket",
        "Groupe de commandes réservées à la gestion des tickets",
        guild_ids=[SKYLANDS_GUILD_ID],
        dm_permission=False,
    )
    async def tickets(self, interaction: nextcord.Interaction):
        pass

    async def create_ticket(self, interaction: nextcord.Interaction):
        author = interaction.user
        with open("tickets.json", "rt") as ticket_counter_file:
            tickets: list = json.loads(ticket_counter_file.read())

        ticket_id = len(tickets) + 1

        ticket_channel: nextcord.TextChannel = await self.server.create_text_channel(
            f"ticket-{str(ticket_id)}-{author.global_name}",
            category=self.ticket_category,
        )

        tickets.append({"channel_id": ticket_channel.id, "closed": False})

        with open("tickets.json", "wt") as ticket_counter_file:
            ticket_counter_file.write(json.dumps(tickets))

        await ticket_channel.set_permissions(
            self.server.get_role(MEMBER_ROLE_ID),
            overwrite=nextcord.PermissionOverwrite(view_channel=False),
        )

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Ticket créé : " + ticket_channel.mention,
                description="Utilise </ticket ajouter_membre:1223336538075562045> pour ajouter quelqu'un dans ton ticket",
            ),
            ephemeral=True,
        )

    @nextcord.slash_command(
        "envoyer_message_tickets",
        "Envoie le message avec le bouton pour créer un ticket",
        guild_ids=[SKYLANDS_GUILD_ID],
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def send_control_message(self, interaction: nextcord.Interaction):
        view = nextcord.ui.View()
        btn = nextcord.ui.Button(label="Créer un ticket", emoji="🎟️")

        async def callback(interaction: nextcord.Interaction):
            await self.create_ticket(interaction)

        btn.callback = callback
        view.add_item(btn)
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.send(view=view)
        await interaction.followup.send("✅ Message envoyé.", ephemeral=True)

    async def handle_ticket_error(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ) -> bool:
        if not self.is_ticket(interaction.channel):
            await interaction.response.send_message(
                "Il faut éxecuter cette commande dans un salon de ticket.",
                ephemeral=True,
            )
            return True

        if member.bot:
            await interaction.response.send_message(
                "Tu ne peux pas ajouter de bot dans un ticket.",
                ephemeral=True,
            )
            return True

        return False

    async def add_or_remove_member(
        self, add: bool, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        remove = not add
        ticket = interaction.channel
        if await self.handle_ticket_error(interaction, member):
            return

        await interaction.response.defer()
        user_in_ticket = ticket.permissions_for(member).view_channel
        if add and user_in_ticket:
            await interaction.followup.send(
                embed=nextcord.Embed(
                    title="Membre déjà dans le ticket",
                    description=f"Le membre "
                    + member.mention
                    + " est déjà dans le ticket.",
                ),
            )
            return

        if remove and not user_in_ticket:
            await interaction.followup.send(
                embed=nextcord.Embed(
                    title="Membre déjà pas dans le ticket",
                    description=f"Le membre "
                    + member.mention
                    + " n'est pas déjà dans le ticket.",
                ),
            )
            return

        await ticket.set_permissions(
            member,
            overwrite=(
                nextcord.PermissionOverwrite(view_channel=True) if add else None
            ),
        )
        await interaction.followup.send(
            embed=nextcord.Embed(
                title="Nouveau membre" if add else "Membre retiré",
                description="Membre "
                + member.mention
                + (" ajouté au" if add else " enlevé du")
                + " ticket.",
            ),
        )

    @tickets.subcommand("ajouter_membre", "Ajoute la personne au ticket")
    async def add_command(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            "utilisateur", "L'utilisateur à ajouter au ticket", required=True
        ),
    ):
        await self.add_or_remove_member(True, interaction, member)

    @tickets.subcommand("enlever_membre", "Enlève la personne du ticket")
    async def remove_command(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            "utilisateur", "L'utilisateur à enlever du ticket", required=True
        ),
    ):
        await self.add_or_remove_member(False, interaction, member)
