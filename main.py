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

bot.add_cog(PollCommands())
bot.add_cog(MiscellaneousCommands())
bot.add_cog(ModerationCommands(bot))
bot.add_cog(StatusUpdateCommands(bot))
MemberJoin(bot)
bot.add_cog(PostUtilities(bot))
bot.add_all_cog_commands()


def command_representation(command: nextcord.BaseApplicationCommand, shift: int = 0):
    command_symbol = {
        nextcord.application_command.SlashApplicationCommand: "[blue]▐[/blue][white on blue]/[/white on blue][blue]▌[/blue]",
        nextcord.application_command.SlashApplicationSubcommand: "[blue]▐[/blue][white on blue]/[/white on blue][blue]▌[/blue]",
        nextcord.application_command.UserApplicationCommand: "[bright_yellow]▐[/bright_yellow][white on bright_yellow]@[/white on bright_yellow][bright_yellow]▌[/bright_yellow]",
    }
    output: str = command_symbol[type(command)] + " " + command.name
    output += (
        " " * (85 - len(output) - shift)
        + "[black italic]"
        + command.description
        + "[/black italic]"
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
        output += "\n"

    return output


@bot.event
async def on_ready():
    commands = "\n".join(
        [command_representation(command) for command in bot.get_application_commands()]
    )
    print(">> [bold green underline]Bot ready[/bold green underline] <<")
    print(f"[bold blue]Bot Commands:[/bold blue]\n{commands}")


if __name__ == "__main__":

    dotenv.load_dotenv()
    bot.run(TOKEN)
