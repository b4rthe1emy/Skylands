import nextcord
from nextcord.ext import commands
from rich import print
import json
import random
import dotenv


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
                        "Vous avez déjà voté pour ce sondage. Utilisez */[NOT_IMPLEMENTD_COMMAND]* pour annuler votre vote",
                        ephemeral=True,
                    )
                    return

        if [vote.user_id for vote in self.votes[option_id]] == user_id:
            interaction.response.send_message(
                f"Vous avez déjà voté pour l'option n°{option_id}.", ephemeral=True
            )
            return

        self.votes[option_id].append(PollVote(user_id))

    def clear_all_votes_from_user(self, user_id: int) -> int:
        for option in self.votes:
            [vote.user_id for vote in option].remove(user_id)


class PollsTracker:
    polls_file = dotenv.get_key(dotenv.find_dotenv(), "SAVED_POLLS_FILE")
    MAX_POLLS = 999_999

    def get_new_id(self) -> int:
        id_attempt = random.randint(1, self.MAX_POLLS)
        with open(self.polls_file, mode="r") as file:
            polls: list[dict] = json.loads(file.read())
            if id_attempt in [poll["id"] for poll in polls]:
                return self.get_new_id()

        return id_attempt

    async def delete_poll(self, poll_id, interaction: nextcord.Interaction) -> bool:
        with open(self.polls_file, mode="r") as file:
            polls: list[dict] = json.loads(file.read())
            try:
                poll_index = [poll["id"] for poll in polls].index(poll_id)
            except ValueError:
                await interaction.response.send_message(
                    f"Le sondage {poll_id} n'existe pas.", ephemeral=True
                )
                return False

            polls.pop(poll_index)

        with open(self.polls_file, mode="w") as file:
            file.write(json.dumps(polls))

        return True

    def new_poll(self, poll: Poll):
        with open(self.polls_file, mode="r") as file:
            polls: list[dict] = json.loads(file.read())

        with open(self.polls_file, mode="w") as file:
            new_poll = {
                "id": poll.id,
                "title": poll.title,
                "multiple_votes_allowed": poll.multiple_votes_allowed,
                "votes": poll.votes,
                "options": poll.options,
            }
            polls.append(new_poll)
            polls = json.dumps(polls)

            file.write(polls)
            print("New poll:", new_poll)

    def vote(self, poll_id: int, option: int, interaction: nextcord.Interaction):
        with open(self.polls_file, mode="r") as file:
            polls: list[dict] = json.loads(file.read())

        with open(self.polls_file, mode="w") as file:
            poll_index = [poll["id"] for poll in polls].index(poll_id)

            polls[poll_index]["votes"][option].append(PollVote(interaction.user.id))

        interaction.response.send_message("g pas fini de le coder")
        raise NotImplementedError("g pas fini")
