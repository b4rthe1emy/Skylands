import nextcord
from nextcord.ext import commands

from rich import print


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


def get_commands(types: tuple[type], bot: commands.Bot):
    commands = [
        command_representation(command)
        for command in bot.get_application_commands()
        if (type(command) in types)
    ]
    if not commands:
        return "[bright_black italic]None[/bright_black italic]"
    return "\n".join(commands)


def print_commands(bot: commands.Bot):
    slash_commands = get_commands(
        (nextcord.application_command.SlashApplicationCommand,), bot
    )
    user_commands = get_commands(
        (nextcord.application_command.UserApplicationCommand,), bot
    )
    message_commands = get_commands(
        (nextcord.application_command.MessageApplicationCommand,), bot
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
