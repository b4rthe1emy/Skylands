import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

dotenv_file = dotenv.find_dotenv()

bot = commands.Bot(
    intents=nextcord.Intents.all(),
)


@bot.event
async def on_ready():
    print(">> [bold green underline]Bot ready[/bold green underline] <<")
    print(
        f"[bold blue]Bot Commands:[/bold blue] [bright_black]{bot.get_application_commands()[0].name}[/bright_black]"
    )


if __name__ == "__main__":

    dotenv.load_dotenv()
    TOKEN = dotenv.get_key(dotenv_file, "DISCORD_TOKEN")
    bot.run(TOKEN)
