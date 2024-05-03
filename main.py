import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

TOKEN = dotenv.get_key(dotenv.find_dotenv(), "DISCORD_TOKEN")
SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))
AUTO_ROLES_CHANNEL_ID = int(
    dotenv.get_key(dotenv.find_dotenv(), "AUTO_ROLES_CHANNEL_ID")
)
RULES_CHANNEL_ID = int(dotenv.get_key(dotenv.find_dotenv(), "RULES_CHANNEL_ID"))

bot_activity = nextcord.Activity(
    name="Skylands",
    type=nextcord.ActivityType.playing,
)


bot = commands.Bot(
    intents=nextcord.Intents.all(),
    activity=bot_activity,
)

from cogs.polls import Polls
from cogs.miscellaneous import Miscellaneous
from cogs.moderation import Moderation
from cogs.status_update import StatusUpdate
from cogs.member_join import MemberJoin
from cogs.posts import Posts
from cogs.prefixes import Prefixes
from cogs.clear_channel_messages import ClearChannelMessages
from cogs.recruitment_form import RecruitmentForm
from cogs.tickets import Tickets
from cogs.rules import Rules
from cogs.giveways import Giveways
from cogs.invitations import Invitations

bot.add_cog(Polls())
bot.add_cog(Miscellaneous())
bot.add_cog(Moderation(bot))
bot.add_cog(StatusUpdate(bot))
bot.add_cog(member_join := MemberJoin(bot))
bot.add_cog(Posts(bot))
bot.add_cog(prefixes_commands := Prefixes(bot))
bot.add_cog(ClearChannelMessages())
bot.add_cog(tickets_commands := Tickets(bot))
bot.add_cog(rules_commands := Rules(bot))
bot.add_cog(Giveways(bot))
bot.add_cog(Invitations(member_join.invites_tracker))
bot.add_all_cog_commands()


@bot.event
async def on_ready():
    import utils.print_app_commands as pac

    pac.print_commands(bot)

    guild = bot.get_guild(SKYLANDS_GUILD_ID)

    await member_join.invites_tracker.setup()

    print("[bold blue]>> UPDATING TICKETS CONTROL MESSAGE[/bold blue]")
    await tickets_commands.send_control_message(None, edit=True)
    print("[italic green]Done succefully.[/italic green]\n")

    print("[bold blue]>> UPDATING RECRUITEMENT FORM MESSAGE[bold blue]")
    await RecruitmentForm.send_control_message(guild, bot, edit=True)
    print("[italic green]Done succefully.[/italic green]\n")

    print("[bold blue]>> UPDATING RULES MESSAGE[/bold blue]")
    await rules_commands.send_rules(bot.get_channel(RULES_CHANNEL_ID), edit=True)
    print("\n[italic green]Done succefully.[/italic green]\n")

    print("[bold blue]>> REFRESHING EVERYONE'S PREFIXES[/bold blue]")
    print("[italic blue]in server " + guild.name + "[/italic blue]\n")
    await prefixes_commands.refresh_everyone(guild)
    print("\n[italic green]Done succefully.[/italic green]\n")


if __name__ == "__main__":

    dotenv.load_dotenv()
    bot.run(TOKEN)
