import nextcord
from rich import print
from nextcord.ext import commands


class Miscellaneous(commands.Cog):
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
            "description",
            'La description de l\'embed. Utilise "\\n" pour aller à la ligne',
            required=False,
        ),
        preview: str = nextcord.SlashOption(
            "preview",
            "Si oui, le message sera visible que par toi",
            choices={"Oui": "Oui", "Non": "Non"},
            default="Non",
        ),
        image_url: str = nextcord.SlashOption(
            "url_image", "L'URL de l'image à mettre dans l'embed", required=False
        ),
    ):
        preview: bool = preview == "Oui"
        if description:
            description = description.replace("\\n", "\n")

        embed = nextcord.Embed()
        embed.description = "# " + title + "\n" + (description if description else "")
        if image_url:
            embed.set_image(url=image_url)

        async def add_field(interaction: nextcord.Interaction):
            async def modal_callback(modal_interaction: nextcord.Interaction):
                embed.add_field(name=name.value, value=value.value, inline=False)

                await modal_interaction.response.send_message(
                    embed=nextcord.Embed(
                        description="## Paragraphe ajouté\n\n"
                        "### Titre du paragraphe\n> "
                        + name.value
                        + "\n### Contenu du paragraphe\n"
                        + value.value
                    ),
                    ephemeral=True,
                )

            modal = nextcord.ui.Modal("Ajouter un paragraphe", timeout=None)

            modal.add_item(
                name := nextcord.ui.TextInput("Titre du paragraphe", required=True)
            )
            modal.add_item(
                value := nextcord.ui.TextInput(
                    "Contenu du paragraphe",
                    style=nextcord.TextInputStyle.paragraph,
                    required=True,
                )
            )

            modal.callback = modal_callback
            await interaction.response.send_modal(modal)

        async def send_embed(interaction: nextcord.Interaction):
            try:
                if preview:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.channel.send(embed=embed)
            except nextcord.HTTPException:
                await interaction.response.send_message(
                    embed=nextcord.Embed(
                        title="❌ URL Invalide : `" + str(image_url) + "`"
                    ),
                    ephemeral=True,
                )

        view = nextcord.ui.View(timeout=None)

        add_field_button = nextcord.ui.Button(label="Ajouter un paragraphe", emoji="📝")
        add_field_button.callback = add_field
        view.add_item(add_field_button)

        send_embed_button = nextcord.ui.Button(label="Envoyer l'embed", emoji="📨")
        send_embed_button.callback = send_embed
        view.add_item(send_embed_button)

        await interaction.response.send_message(
            embed=nextcord.Embed(title="Embed")
            .add_field(name="Titre", value=title, inline=False)
            .add_field(
                name="Description",
                value=(description if description else "> *Pas de description*"),
                inline=False,
            ),
            view=view,
            ephemeral=True,
        )
