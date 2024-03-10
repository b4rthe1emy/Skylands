import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

import blagues_api

BLAGUES_API_TOKEN = dotenv.get_key(dotenv.find_dotenv(), "BLAGUES_API_TOKEN")


class BlaguesCommands(commands.Cog):
    def __init__(self) -> None:
        super().__init__()
        self.blague_api = blagues_api.BlaguesAPI(BLAGUES_API_TOKEN)

    @nextcord.slash_command(
        "blague", "Envoie une blague grâce à la librairie Blague-API."
    )
    async def joke(
        self,
        interaction: nextcord.Interaction,
        filters: str = nextcord.SlashOption(
            "filtres",
            "Types de blagues à ne pas dire. Ne peut pas être mélangé avec `catégorie`",
            required=False,
        ),
        category: str = nextcord.SlashOption(
            "catégorie",
            "Type de blagues à dire. Ne peut pas être mélangé avec `filtres`",
            required=False,
        ),
    ):
        if filters and category:
            await interaction.response.send_message(
                "Tu ne peut pas mélanger `filtres` avec `catégories`. Choisis-en un seul."
            )
            return

        if filters:
            filters: list[str] = filters.split(";")
            print(filters)
            joke = await self.blague_api.random(disallow=filters)
            print(joke)

        if category:
            print(category)
            joke = await self.blague_api.random_categorized(category)
            print(joke)
