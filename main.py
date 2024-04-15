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
from cogs.auto_roles import AutoRoles
from cogs.recruitment_form import RecruitmentForm
from cogs.tickets import Tickets
from cogs.rules import Rules

bot.add_cog(Polls())
bot.add_cog(Miscellaneous())
bot.add_cog(Moderation(bot))
bot.add_cog(StatusUpdate(bot))
bot.add_cog(MemberJoin(bot))
bot.add_cog(Posts(bot))
bot.add_cog(prefixes_commands := Prefixes(bot))
bot.add_cog(ClearChannelMessages())
bot.add_cog(auto_roles_commands := AutoRoles(bot))
bot.add_cog(tickets_commands := Tickets(bot))
bot.add_cog(rules_commands := Rules)
bot.add_all_cog_commands()


def command_representation(command: nextcord.BaseApplicationCommand, shift: int = 0):
    command_symbol = {
        nextcord.SlashApplicationCommand: "[blue]▐[/blue][white on blue]/[/white on blue][blue]▌[/blue]",
        nextcord.SlashApplicationSubcommand: "[blue]▐[/blue][white on blue]/[/white on blue][blue]▌[/blue]",
        nextcord.UserApplicationCommand: "[green]▐[/green][on green]@[/on green][green]▌[/green]",
        nextcord.MessageApplicationCommand: "[yellow]▐[/yellow][on yellow]“[/on yellow][yellow]▌[/yellow]",
    }
    output: str = command_symbol[type(command)]
    if isinstance(command, nextcord.SlashApplicationCommand) and command.children:
        output = "[blue]▐[/blue][white on blue]⤷[/white on blue][blue]▌[/blue]"
    output += " " + command.name

    number_of_spaces = 90 - len(output) - shift
    if isinstance(
        command,
        (
            nextcord.application_command.SlashApplicationCommand,
            nextcord.application_command.SlashApplicationSubcommand,
        ),
    ):
        output += (
            "[bright_black italic] "
            + ("╌" * number_of_spaces)
            + " "
            + command.description
            + "[/bright_black italic]"
        )

    if (
        isinstance(command, nextcord.SlashApplicationCommand)
        and list(command.children.values()) != []
    ):

        children = list(command.children.values())
        for i, command in enumerate(children):
            if i == len(children) - 1:
                output += "\n ┖──࢈"
            else:
                output += "\n ┠──࢈"

            output += command_representation(command, shift=shift + 5)

    return output


def get_commands(types: tuple[type]):
    commands = [
        command_representation(command)
        for command in bot.get_application_commands()
        if (type(command) in types)
    ]
    if not commands:
        return "[bright_black italic]None[/bright_black italic]"
    return "\n".join(commands)


@bot.event
async def on_ready():
    slash_commands = get_commands(
        (nextcord.application_command.SlashApplicationCommand,)
    )
    user_commands = get_commands((nextcord.application_command.UserApplicationCommand,))
    message_commands = get_commands(
        (nextcord.application_command.MessageApplicationCommand,)
    )
    print(
        r"""[cyan]
 ______   __  __   __  __   __       ______   __   __   _____   ______      ______   ______   ______  
/\  ___\ /\ \/ /  /\ \_\ \ /\ \     /\  __ \ /\ '-.\ \ /\  __-./\  ___\    /\  == \ /\  __ \ /\__  _\ 
\ \___  \\ \  _'-.\ \____ \\ \ \____\ \  __ \\ \ \-.  \\ \ \/\ \ \___  \   \ \  __< \ \ \/\ \\/_/\ \/ 
 \/\_____\\ \_\ \_\\/\_____\\ \_____\\ \_\ \_\\ \_\\'\_\\ \____-\/\_____\   \ \_____\\ \_____\  \ \_\ 
  \/_____/ \/_/\/_/ \/_____/ \/_____/ \/_/\/_/ \/_/ \/_/ \/____/ \/_____/    \/_____/ \/_____/   \/_/[/cyan]
""",
    )
    print(
        f"[blue]▐[/blue][bold on blue]/[/bold on blue][blue]▌ [/blue][bold blue]Slash Commands:[/bold blue]\n\n{slash_commands}\n"
    )
    print(
        f"[green]▐[/green][bold on green]@[/bold on green][green]▌ [/green][bold green]User Commands:[/bold green]\n\n{user_commands}\n"
    )
    print(
        f"[yellow]▐[/yellow][bold on yellow]“[/bold on yellow][yellow]▌ [/yellow][bold yellow]Message Commands:[/bold yellow]\n\n{message_commands}\n"
    )
    guild = bot.get_guild(SKYLANDS_GUILD_ID)

    print("[bold blue]>> UPDATING AUTO-ROLE MESSAGE[bold blue]")

    last_message = [
        msg
        async for msg in bot.get_guild(SKYLANDS_GUILD_ID)
        .get_channel(AUTO_ROLES_CHANNEL_ID)
        .history()
        if msg.author == bot.user
    ][0]
    await auto_roles_commands.tracker.send_message(None, edit_message=last_message)

    print("[italic green]Done succefully.[/italic green]\n")

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
