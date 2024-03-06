import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

SUGESTIONS_FORUM_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SUGESTIONS_FORUM_ID"))
ADMIN_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "ADMIN_ROLE_ID"))
MEMBER_ROLE_ID = int(dotenv.get_key(dotenv.find_dotenv(), "MEMBER_ROLE_ID"))

WAITING_POST_TAG_ID = int(dotenv.get_key(dotenv.find_dotenv(), "WAITING_POST_TAG_ID"))
WIP_POST_TAG_ID = int(dotenv.get_key(dotenv.find_dotenv(), "WIP_POST_TAG_ID"))
ENDED_POST_TAG_ID = int(dotenv.get_key(dotenv.find_dotenv(), "ENDED_POST_TAG_ID"))


class PostUtilities(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot

        @bot.event
        async def on_thread_create(thread: nextcord.Thread):
            if (
                not isinstance(thread.parent, nextcord.ForumChannel)
                or thread.parent.id != SUGESTIONS_FORUM_ID
            ):
                return

            tags = thread.applied_tags.copy()
            tags.append(thread.parent.get_tag(WAITING_POST_TAG_ID))
            await thread.edit(applied_tags=tags, locked=True)

    @nextcord.slash_command(
        "post",
        dm_permission=False,
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def post(self, interaction: nextcord.Interaction):
        pass

    @post.subcommand(
        "terminer",
        'Attribue le tag terminé, réagit au message original avec "✅" et verrouille le post.',
    )
    async def terminer(self, interaction: nextcord.Interaction):
        thread: nextcord.Thread = interaction.channel

        if (
            not isinstance(thread, nextcord.Thread)
            or not isinstance(interaction.channel.parent, nextcord.ForumChannel)
            or not interaction.channel.parent.id == SUGESTIONS_FORUM_ID
        ):
            await interaction.response.send_message(
                "La commande doit être executée dans un post dans le forum Suggestions.",
                ephemeral=True,
            )
            return

        forum = interaction.channel.parent
        messages = await thread.history(oldest_first=True).flatten()
        await messages[0].add_reaction("✅")

        tags = thread.applied_tags.copy()
        tags.append(forum.get_tag(ENDED_POST_TAG_ID))
        try:
            tags.remove(forum.get_tag(WAITING_POST_TAG_ID))
        except ValueError:
            pass
        try:
            tags.remove(forum.get_tag(WIP_POST_TAG_ID))
        except ValueError:
            pass

        try:
            await thread.edit(applied_tags=tags)
        except nextcord.errors.HTTPException:
            pass
        await thread.edit(locked=True)

        await interaction.response.send_message("Ce post est terminé.")

    @post.subcommand(
        "réactiver",
        'Enlève le tag terminé, enlève la réaction du message original "✅" et déverrouille le post.',
    )
    async def réactiver(self, interaction: nextcord.Interaction):
        thread: nextcord.Thread = interaction.channel

        if (
            not isinstance(thread, nextcord.Thread)
            or not isinstance(interaction.channel.parent, nextcord.ForumChannel)
            or not interaction.channel.parent.id == SUGESTIONS_FORUM_ID
        ):
            await interaction.response.send_message(
                "La commande doit être executée dans un post dans le forum Suggestions.",
                ephemeral=True,
            )
            return

        forum = interaction.channel.parent
        messages = await thread.history(oldest_first=True).flatten()
        await messages[0].remove_reaction("✅", self.bot.user)

        tags = thread.applied_tags.copy()
        try:
            tags.remove(forum.get_tag(ENDED_POST_TAG_ID))
        except ValueError:
            pass
        tags.append(forum.get_tag(WIP_POST_TAG_ID))
        try:
            await thread.edit(applied_tags=tags)
        except nextcord.errors.HTTPException:
            pass
        await thread.edit(locked=True)

        await interaction.response.send_message("Ce post est réactivé.")
