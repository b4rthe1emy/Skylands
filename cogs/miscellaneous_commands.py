import nextcord
from rich import print
from nextcord.ext import commands


class MiscellaneousCommands(commands.Cog):
    @nextcord.slash_command(name="vote", description="Lien pour voter")
    async def vote(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "Viens voter sur 👉 https://skylandsmc.fr/vote 👈 !!!", ephemeral=True
        )

    @nextcord.slash_command(name="ip", description="L'ip du serveur")
    async def ip(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "Venez jouer en 1.20.1 ou +\nsur 👉 `play.skylandsmc.fr` 👈",
            ephemeral=True,
        )

    @nextcord.slash_command(name="site", description="Lien du site de Skylands")
    async def website(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "👉 [Site de Skylands](https://skylandsmc.fr/) 👈",
            ephemeral=True,
        )

    @nextcord.slash_command(name="tiktok", description="Lien tiktok")
    async def tiktok(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "👉 [Tiktok de Skylands](https://tiktok.com/@skylands.fr) 👈 et abonne-toi !",
            ephemeral=True,
        )

    @nextcord.slash_command(name="youtube", description="Lien youtube")
    async def youtube(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "👉 [Youtube de Skylands](https://youtube.com/@skylandsmc.fr-/) 👈 et abonne-toi !",
            ephemeral=True,
        )

    @nextcord.slash_command(
        name="embed",
        description="Envoie un message sous forme d'embed, avec jusqu'à 5 pargraphes",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def embed(
        self,
        interaction: nextcord.Interaction,
        title: str = nextcord.SlashOption(
            "titre", "Le titre de l'embed", required=True
        ),
        description: str = nextcord.SlashOption(
            "description", "La description de l'embed", required=False
        ),
        preview: str = nextcord.SlashOption(
            "preview",
            "Si oui, le message sera visible que par toi",
            choices={"Oui": "Oui", "Non": "Non"},
            default="Non",
        ),
        title1: str = nextcord.SlashOption(
            "titre_1", "Le titre du paragraphe 1", False
        ),
        paragraph1: str = nextcord.SlashOption(
            "paragraphe_1", "Le paragraphe 1", False
        ),
        title2: str = nextcord.SlashOption(
            "titre_2", "Le titre du paragraphe 2", False
        ),
        paragraph2: str = nextcord.SlashOption(
            "paragraphe_2", "Le paragraphe 2", False
        ),
        title3: str = nextcord.SlashOption(
            "titre_3", "Le titre du paragraphe 3", False
        ),
        paragraph3: str = nextcord.SlashOption(
            "paragraphe_3", "Le paragraphe 3", False
        ),
        title4: str = nextcord.SlashOption(
            "titre_4", "Le titre du paragraphe 4", False
        ),
        paragraph4: str = nextcord.SlashOption(
            "paragraphe_4", "Le paragraphe 4", False
        ),
        title5: str = nextcord.SlashOption(
            "titre_5", "Le titre du paragraphe 5", False
        ),
        paragraph5: str = nextcord.SlashOption(
            "paragraphe_5", "Le paragraphe 5", False
        ),
    ):
        embed = nextcord.Embed()
        embed.description = "# " + title + "\n" + (description if description else "")

        titles = [title1, title2, title3, title4, title5]
        paragraphs = [paragraph1, paragraph2, paragraph3, paragraph4, paragraph5]

        for i in range(len(titles)):
            paragraph = paragraphs[i]
            title = titles[i]

            if title:
                if not paragraph:
                    await interaction.response.send_message(
                        f"❌ Comme tu as mis `titre_{i + 1}`, tu **dois** aussi mettre `paragraphe_{i + 1}`",
                        ephemeral=True,
                    )
                    return

                embed.add_field(name=title, value=paragraph, inline=False)
                i += 1

        if preview == "Oui":
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.channel.send(embed=embed)
