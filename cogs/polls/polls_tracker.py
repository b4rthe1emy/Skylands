import nextcord
from nextcord.ext import commands
from rich import print


class PollVote:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id


class Poll:
    def __init__(
        self,
        poll_id: int,
        title: str,
        options: list[str],
        message: nextcord.Message,
        multiple_votes_allowed: bool,
    ) -> None:

        self.id: int = poll_id
        self.message: nextcord.Message = message
        self.title: str = title

        self.multiple_votes_allowed: bool = multiple_votes_allowed
        self.options: list[str] = options
        self.votes: list[list[PollVote]] = [[]] * len(options)

    def vote(
        self,
        user_id: int,
        option_id: int,
        interaction: nextcord.Interaction,
    ) -> None:

        if not self.multiple_votes_allowed:
            for option in self.votes:
                if user_id in [vote.user_id for vote in option]:
                    interaction.response.send_message(
                        "Vous avez déjà voté.", ephemeral=True
                    )
                    return

        if [vote.user_id for vote in self.votes[option_id]] == user_id:
            interaction.response.send_message(
                f"Vous avez déjà voté pour l'option {option_id}.", ephemeral=True
            )
            return

        self.votes[option_id].append(PollVote(user_id))

    def clear_all_votes_from_user(self, user_id: int) -> int:
        for option in self.votes:
            [vote.user_id for vote in option].remove(user_id)
