import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

dotenv_file = dotenv.find_dotenv()
TOKEN = dotenv.get_key(dotenv_file, "DISCORD_TOKEN")

bot = commands.Bot(
    intents=nextcord.Intents.all(),
)

from cogs.polls import Poll

bot.add_cog(Poll())
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
