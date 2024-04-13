import nextcord
from nextcord.ext import commands
from rich import print
import dotenv
import json

SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))
TICKETS_CATEGORY = int(dotenv.get_key(dotenv.find_dotenv(), "TICKETS_CATEGORY"))
MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MEMBER_ROLE_ID"))
TICKETS_CHANNEL_ID = int(dotenv.get_key(dotenv.find_dotenv(), "TICKETS_CHANNEL_ID"))

ADMIN_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "ADMIN_ROLE_ID"))
OWNER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "OWNER_ROLE_ID"))
SYS_STAFF_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SYS_STAFF_ROLE_ID"))
JM_OWNER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "JM_OWNER_ROLE_ID"))


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
        dm_permission=False,
        # default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def tickets(self, interaction: nextcord.Interaction):
        pass

    @property
    def default_permissions(self):
        return nextcord.PermissionOverwrite(view_channel=False)

    async def create_ticket(self, interaction: nextcord.Interaction):
        author = interaction.user
        with open("tickets.json", "rt") as ticket_counter_file:
            tickets: list = json.loads(ticket_counter_file.read())

        ticket_id = len(tickets) + 1

        ticket_channel: nextcord.TextChannel = await self.server.create_text_channel(
            f"ticket-{str(ticket_id)}-{author.global_name}",
            category=self.ticket_category,
        )
        new_ticket = {
            "channel_id": ticket_channel.id,
            "owner_id": author.id,
            "closed": False,
            "id": ticket_id,
        }
        tickets.append(new_ticket)

        with open("tickets.json", "wt") as ticket_counter_file:
            ticket_counter_file.write(json.dumps(tickets))

        await ticket_channel.set_permissions(
            self.server.get_role(MEMBER_ROLE_ID),
            overwrite=self.default_permissions,
        )

        owner_perm = nextcord.PermissionOverwrite()
        owner_perm.view_channel = True

        await ticket_channel.set_permissions(
            interaction.user,
            overwrite=owner_perm,
        )

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Ticket créé : " + ticket_channel.mention,
                description="Utilise </ticket ajouter_membre:1224104262808768512> pour ajouter quelqu'un dans ton ticket",
            ),
            ephemeral=True,
        )

        return ticket_channel

    @nextcord.slash_command(
        "envoyer_message_tickets",
        "Envoie le message avec le bouton pour créer un ticket",
        dm_permission=False,
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def send_control_message(
        self,
        interaction: nextcord.Interaction,
        edit=nextcord.SlashOption(
            "modifier_existant",
            "Si Oui, le dernier message envoyé par le bot va être "
            "modifié, sinon, le message va être renvoyé",
            default="Non",
            choices={"Oui": "Oui", "Non": "Non"},
        ),
    ):
        edit = True if edit == "Oui" or edit == True else False
        view = nextcord.ui.View(timeout=None)
        btn = nextcord.ui.Button(label="Créer un ticket", emoji="🎟️")

        async def callback(interaction: nextcord.Interaction):
            await self.create_ticket(interaction)

        btn.callback = callback
        view.add_item(btn)

        if edit:
            messages = (
                await self.bot.get_channel(TICKETS_CHANNEL_ID).history().flatten()
            )
            messages = [msg for msg in messages if msg.author == self.bot.user]
            try:
                last_bot_msg: nextcord.Message = messages[0]
            except IndexError:
                action = self.bot.get_channel(TICKETS_CHANNEL_ID).send
            else:
                action = last_bot_msg.edit

        else:
            action = self.bot.get_channel(TICKETS_CHANNEL_ID).send

        await action(
            embeds=[
                nextcord.Embed(
                    title="Règles des tickets",
                    description="Voici les règles à lire avant de créer un ticket :",
                )
                .add_field(
                    name="Règle 1",
                    value="Merci de créer un ticket uniquement pour les raison "
                    "listées dans le menu déroulant en dessous de ce message",
                    inline=False,
                )
                .add_field(
                    name="Règle 2",
                    value="Merci de ne pas ouvrir un ticket pour un recrutement.",
                    inline=False,
                )
                .add_field(
                    name="Règle 3",
                    value="Merci de ne pas créer un ticket uniquement dans le but "
                    "de déranger le staff.",
                    inline=False,
                )
                .add_field(
                    name="Règle 4",
                    value="Merci de ne pas ouvrir un ticket dans le seul but de "
                    "poser une question.",
                    inline=False,
                ),
                nextcord.Embed(
                    title="Qu'est-ce qu'un ticket ?",
                    description="> Un ticket te permet d'échanger avec le staff "
                    "dans un salon privé. Si tu as un problème, tu peux ouvrir "
                    "un ticket pour qu'on t'aide !",
                ).add_field(
                    name="Comment créer un ticket ?",
                    value="> Choisis parmi les options du menu déroulant situé "
                    "en dessous de ce message pour créer ton ticket !",
                ),
            ],
            view=view,
        )
        if interaction is not None:
            await interaction.response.send_message(
                "✅ Message renvoyé.", ephemeral=True
            )

    async def handle_ticket_error(self, interaction: nextcord.Interaction) -> bool:
        if not self.is_ticket(interaction.channel):
            await interaction.response.send_message(
                "Il faut éxecuter cette commande dans un salon de ticket.",
                ephemeral=True,
            )
            return True

        return False

    async def add_or_remove_member(
        self, add: bool, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        remove = not add
        ticket = interaction.channel

        if await self.handle_ticket_error(interaction):
            return

        if not self.is_member_an_admin(
            interaction.user
        ) and not self.is_member_the_ticket_owner(interaction.user, ticket):
            self.send_error_message(
                interaction,
                "Tu ne peux pas ajouter/enlever de membre dans ce ticket "
                "car tu n'es ni un administrateur ni le propriétaire du ticket.",
            )
            return

        if member.bot:
            self.send_error_message(
                interaction, "Tu ne peux pas ajouter/enlever de bot dans un ticket."
            )
            return

        await interaction.response.defer()
        user_in_ticket = ticket.permissions_for(member).view_channel

        if add and user_in_ticket:
            await self.send_error_message(
                interaction,
                f"Le membre " + member.mention + " est déjà dans le ticket.",
                followup=True,
            )
            return
        if remove and not user_in_ticket:
            await self.send_error_message(
                interaction,
                f"Le membre " + member.mention + " n'est pas déjà dans le ticket.",
                followup=True,
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

    async def send_error_message(
        self, interaction: nextcord.Interaction, message: str, followup: bool = False
    ):
        if followup:
            send = interaction.followup.send
        else:
            send = interaction.response.send_message

        await send(
            embed=nextcord.Embed(
                title="🚫 Refusé",
                description=message,
            ),
            ephemeral=True,
        )

    def is_member_the_ticket_owner(
        self, member: nextcord.Member, ticket: nextcord.TextChannel
    ):
        with open("tickets.json", "rt") as ticket_counter_file:
            tickets: list = json.loads(ticket_counter_file.read())

        ticket_info = tickets[
            [ticket["channel_id"] for ticket in tickets].index(ticket.id)
        ]

        return member.id == ticket_info["owner_id"]

    def is_member_an_admin(self, member: nextcord.Member):
        return (
            member.get_role(ADMIN_ROLE_ID) is not None
            or member.get_role(OWNER_ROLE_ID) is not None
            or member.get_role(SYS_STAFF_ROLE_ID) is not None
            or member.get_role(JM_OWNER_ROLE_ID) is not None
        )

    @tickets.subcommand("fermer", "Ferme le ticket")
    async def close_ticket_command(
        self,
        interaction: nextcord.Interaction,
        reason: str = nextcord.SlashOption(
            "raison",
            "Pourquoi veux-tu fermer ce ticket ?",
            required=False,
            default="Aucune raison spécifiée",
        ),
    ):

        if await self.handle_ticket_error(interaction):
            return

        if not self.is_member_the_ticket_owner(
            interaction.user, interaction.channel
        ) and not self.is_member_an_admin(interaction.user):
            await self.send_error_message(
                interaction,
                "Tu dois être le propriétaire du ticket ou un administrateur pour pouvoir demander de fermer le ticket.",
            )

        await interaction.response.defer()

        button = nextcord.ui.Button(label="Confirmer", emoji="✅")

        async def button_callback(button_interaction: nextcord.Interaction):
            requester = interaction.user
            closer = button_interaction.user

            if self.is_member_an_admin(requester):
                if self.is_member_an_admin(closer) or self.is_member_the_ticket_owner(
                    closer, interaction.channel
                ):
                    await self.close_ticket(button_interaction, reason)
                else:
                    await self.send_error_message(
                        button_interaction,
                        "Pour confirmer la fermeture de ce ticket, tu dois être le propriétaire "
                        "de ce ticket car c'est un administrateur qui a demandé de le fermer.\n"
                        "*PS: Les administrateurs peuvent contourner ce message.*",
                    )

            elif self.is_member_the_ticket_owner(requester, interaction.channel):
                if self.is_member_an_admin(closer):
                    await self.close_ticket(button_interaction, reason)

                else:
                    await self.send_error_message(
                        button_interaction,
                        "Pour confirmer la fermeture de ce ticket, tu dois être un administrateur "
                        "car c'est le propriétaire de ce ticket qui a demandé de le fermer.",
                    )

            else:
                await self.send_error_message(
                    button_interaction,
                    "Tu ne peux pas confirmer la fermeture de ce ticket.",
                )

        button.callback = button_callback

        view = nextcord.ui.View()
        view.add_item(button)

        await interaction.followup.send(
            embed=nextcord.Embed(
                title="Demande de fermeture du ticket",
                description="Clique sur le bouton pour accepter la fermeture de ce ticket.",
            )
            .add_field(
                name="Demande de :",
                value=(
                    (
                        "L'administrateur : "
                        if self.is_member_an_admin(interaction.user)
                        else "Le propriétaire du ticket : "
                    )
                    + interaction.user.mention
                ),
            )
            .add_field(name="Raison :", value="> " + reason, inline=False),
            view=view,
        )

    async def close_ticket(self, interaction: nextcord.Interaction, reason: str):
        await interaction.response.send_message(
            embed=nextcord.Embed(title="Fermeture du ticket en cours..."),
            ephemeral=True,
        )

        with open("tickets.json", "rt") as tickets_file:
            tickets: list = json.loads(tickets_file.read())

        ticket_ids = [ticket["channel_id"] for ticket in tickets]
        ticket_index = ticket_ids.index(interaction.channel_id)

        tickets[ticket_index]["closed"] = True

        with open("tickets.json", "wt") as tickets_file:
            tickets_file.write(json.dumps(tickets))

        ticket_channel: nextcord.TextChannel = self.server.get_channel(
            interaction.channel_id
        )
        for user in ticket_channel.members:
            if user.bot:
                continue
            await user.send(
                embed=nextcord.Embed(
                    title="Ticket fermé",
                )
                .add_field(
                    name="Fermé par :", value=interaction.user.mention, inline=False
                )
                .add_field(name="Raison :", value="> " + reason, inline=False),
            )

        # new_perms = self.default_permissions
        # new_perms.send_messages = False

        # await ticket_channel.set_permissions(
        #     self.server.get_role(MEMBER_ROLE_ID),
        #     overwrite=new_perms,
        # )

        await ticket_channel.delete()
