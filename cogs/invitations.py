import nextcord
from nextcord.ext import commands
from rich import print
import json


class Tracker:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.invites: dict[nextcord.Guild, list[nextcord.Invite]] = {}

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

        try:
            if invited_id not in invitations[str(inviter_id)]:
                invitations[str(inviter_id)].append(invited_id)

        except KeyError:
            invitations[str(inviter_id)] = [invited_id]

        self.set_stored_invitations(invitations)

        return len(invitations[str(inviter_id)])
