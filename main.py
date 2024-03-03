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

bot.add_cog(PollCommands())
bot.add_cog(MiscellaneousCommands())
bot.add_cog(ModerationCommands(bot))
bot.add_all_cog_commands()


@bot.event
async def on_ready():
    print(">> [bold green underline]Bot ready[/bold green underline] <<")
    print(
        f"[bold blue]Bot Commands:[/bold blue] [bright_black]{[command.name for command in bot.get_application_commands()]}[/bright_black]"
    )


if __name__ == "__main__":

    dotenv.load_dotenv()
    bot.run(TOKEN)
