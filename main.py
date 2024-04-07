import nextcord
from nextcord.ext import commands
from rich import print
import dotenv

TOKEN = dotenv.get_key(dotenv.find_dotenv(), "DISCORD_TOKEN")
SKYLANDS_GUILD_ID = int(dotenv.get_key(dotenv.find_dotenv(), "SKYLANDS_GUILD_ID"))
AUTO_ROLES_CHANNEL_ID = int(
    dotenv.get_key(dotenv.find_dotenv(), "AUTO_ROLES_CHANNEL_ID")
)


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
from cogs.clear_channel_messages_command import ClearChannelMessagesCommand
from cogs.auto_roles_commands import AutoRolesCommands

from cogs.recruitment_form import RecruitmentForm
from cogs.tickets_commands import TicketsCommands

bot.add_cog(PollCommands())
bot.add_cog(MiscellaneousCommands())
bot.add_cog(ModerationCommands(bot))
bot.add_cog(StatusUpdateCommands(bot))
bot.add_cog(MemberJoin(bot))
bot.add_cog(PostUtilities(bot))
bot.add_cog(prefixes_commands := PrefixesCommands(bot))
bot.add_cog(ClearChannelMessagesCommand())
bot.add_cog(auto_roles_commands := AutoRolesCommands(bot))
bot.add_cog(tickets_commands := TicketsCommands(bot))
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

    print("[bold blue]>> REFRESHING EVERYONE'S PREFIXES[/bold blue]")
    print("[italic blue]in server " + guild.name + "[/italic blue]\n")
    await prefixes_commands.refresh_everyone(guild)
    print("\n[italic green]Done succefully.[/italic green]\n")

    print("[bold blue]>> UPDATING TICKETS CONTROL MESSAGE[/bold blue]")
    await tickets_commands.send_control_message(None, edit=True)
    print("[italic green]Done succefully.[/italic green]\n")

    print("[bold blue]>> SENDING RECRUITEMENT FORM MESSAGE[bold blue]")

    btn = nextcord.ui.Button(label="Formulaire", emoji="📝")

    async def btn_callback(interaction: nextcord.Interaction):
        await interaction.response.send_modal(RecruitmentForm())

    btn.callback = btn_callback
    view = nextcord.ui.View()
    view.add_item(btn)
    await guild.get_channel(AUTO_ROLES_CHANNEL_ID).send(
        embed=nextcord.Embed(
            title="Formulaire recrutement",
            description="Cliquez sur le bouton pour remplir le formulaire.",
        ),
        view=view,
    )
    print("[italic green]Done succefully.[/italic green]\n")
    # print("[italic bright_black]Disabled.[/italic bright_black]\n")


if __name__ == "__main__":

    dotenv.load_dotenv()
    bot.run(TOKEN)
