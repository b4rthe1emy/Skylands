import nextcord
from nextcord.ext import commands
from rich import print
import json

import time


class Tracker:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.invites: dict[int, list[nextcord.Invite]] = {}

    async def setup(self):
        await self.set_all_invites()

    async def set_all_invites(self):
        for guild in self.bot.guilds:
            self.invites[guild.id] = await guild.invites()

    def get_invite_from_code(
        self, invite_list: list[nextcord.Invite], code: str
    ) -> nextcord.Invite:
        for invite in invite_list:
            if invite.code == code:
                return invite

    async def get_invite_of_member(self, member: nextcord.Member) -> nextcord.Invite:
        invites_before_join = self.invites[member.guild.id]
        invites_after_join = await member.guild.invites()

        for invite in invites_after_join:
            if (
                invite.uses
                > self.get_invite_from_code(invites_before_join, invite.code).uses
            ):
                await self.set_all_invites()
                return invite

    async def update_invites(self, member: nextcord.Member):
        self.invites[member.guild.id] = await member.guild.invites()

    def get_stored_invitations(self) -> dict[int, list[int]]:
        with open("invites.json", "rt") as file:
            return json.load(file)

    def set_stored_invitations(self, inviters: dict[int, list[int]]):
        with open("invites.json", "wt") as file:
            file.write(json.dumps(inviters))

    def add_user_to_inviter(self, inviter_id: int, invited_id: int) -> int:
        invitations = self.get_stored_invitations()

        new = {
            "invited_id": invited_id,
            "time": int(time.time()),
        }

        try:
            if invited_id not in [
                inv["invited_id"] for inv in invitations[str(inviter_id)]
            ]:
                invitations[str(inviter_id)].append(new)

        except KeyError:
            invitations[str(inviter_id)] = [new]

        self.set_stored_invitations(invitations)

        return len(invitations[str(inviter_id)])


class Invitations(commands.Cog):
    def __init__(self, tracker: Tracker) -> None:
        self.tracker: Tracker = tracker

    @nextcord.slash_command(
        "top_invitations",
        "Affiche les X membres qui ont invités le plus de gens à partir de la date sélectionnée.",
        dm_permission=False,
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def top_invitations(
        self,
        interaction: nextcord.Interaction,
        nb_members: int = nextcord.SlashOption(
            "nombre_de_membres", "Contrôle le nombre de membres qui vont être affichés"
        ),
        days: float = nextcord.SlashOption(
            "jours",
            "Contrôle à partir de combien de temps les invitations vont êtres comptés",
        ),
    ):
        days = int(days) if days.is_integer() else days
        invs: dict[str, dict[str, int | float]] = self.tracker.get_stored_invitations()

        invitations: dict[int, int] = {}
        for inviter in invs:
            for i in range(len(invs[inviter])):

                if invs[inviter][i]["time"] > time.time() - days * 86400:
                    try:
                        invitations[int(inviter)] += 1
                    except KeyError:
                        invitations[int(inviter)] = 1

        inv_list = list(invitations.keys())
        inv_list.sort()

        inv_list = inv_list[0:nb_members]

        await interaction.response.send_message(
            f"Les {nb_members} membres qui ont invité le plus de membres dans les {days} derniers jours sont :\n"
            + "\n".join(
                [
                    f"- <@{inviter_id}> : {invitations[inviter_id]} invitation(s)"
                    for inviter_id in inv_list
                ],
            ),
            ephemeral=True,
        )
