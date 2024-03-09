import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

TOKEN = dotenv.get_key(dotenv.find_dotenv(), "DISCORD_TOKEN")

bot = commands.Bot(
    intents=nextcord.Intents.all(),
)

from cogs.poll_commands import PollCommands
from cogs.miscellaneous_commands import MiscellaneousCommands
from cogs.moderation_commands import ModerationCommands
from cogs.status_update_commands import StatusUpdateCommands
from cogs.member_join import MemberJoin
from cogs.posts_utilities import PostUtilities
from cogs.prefixes_comands import PrefixesCommands

bot.add_cog(PollCommands())
bot.add_cog(MiscellaneousCommands())
bot.add_cog(ModerationCommands(bot))
bot.add_cog(StatusUpdateCommands(bot))
MemberJoin(bot)
bot.add_cog(PostUtilities(bot))
bot.add_cog(PrefixesCommands(bot))
bot.add_all_cog_commands()


def command_representation(command: nextcord.BaseApplicationCommand, shift: int = 0):
    command_symbol = {
        nextcord.application_command.SlashApplicationCommand: "[blue]▐[/blue][white on blue]/[/white on blue][blue]▌[/blue]",
        nextcord.application_command.SlashApplicationSubcommand: "[blue]▐[/blue][white on blue]/[/white on blue][blue]▌[/blue]",
        nextcord.application_command.UserApplicationCommand: "[green]▐[/green][on green]@[/on green][green]▌[/green]",
        nextcord.application_command.MessageApplicationCommand: "[yellow]▐[/yellow][on yellow]“[/on yellow][yellow]▌[/yellow]",
    }
    output: str = command_symbol[type(command)] + " " + command.name

    number_of_spaces = 85 - len(output) - shift
    if isinstance(
        command,
        (
            nextcord.application_command.SlashApplicationCommand,
            nextcord.application_command.SlashApplicationSubcommand,
        ),
    ):
        output += (
            "[bright_black italic]"
            + (" " if int(number_of_spaces / 2) != number_of_spaces / 2 else "")
            + (
                " ." * int(number_of_spaces / 2)
                + " "
                + command.description
                + "[/bright_black italic]"
            )
        )
    if (
        isinstance(command, nextcord.SlashApplicationCommand)
        and list(command.children.values()) != []
    ):

        children = list(command.children.values())
        for i, command in enumerate(children):
            if i != len(children) - 1:
                output += "\n ├── " + command_representation(command, shift=5)
            else:
                output += "\n ╰── " + command_representation(command, shift=5)

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
        """
[cyan] ______   __  __   __  __   __       ______   __   __   _____   ______      ______   ______   ______  
/\  ___\ /\ \/ /  /\ \_\ \ /\ \     /\  __ \ /\ '-.\ \ /\  __-./\  ___\    /\  == \ /\  __ \ /\__  _\ 
\ \___  \\\ \  _'-.\ \____ \\\ \ \____\ \  __ \\\ \ \-.  \\\ \ \/\ \ \___  \   \ \  __< \ \ \/\ \\\/_/\ \/ 
 \/\_____\\\ \_\ \_\\\/\_____\\\ \_____\\\ \_\ \_\\\ \_\\\\'\_\\\ \____-\/\_____\   \ \_____\\\ \_____\  \ \_\ 
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


if __name__ == "__main__":

    dotenv.load_dotenv()
    bot.run(TOKEN)
