import nextcord
from nextcord.ext import commands
from rich import print
from .tracker import GivewaysTracker
import time
import dotenv

EMOJIS = ["🥇", "🥈", "🥉"]

GIVEWAYS_CHANNEL_ID = int(dotenv.get_key(dotenv.find_dotenv(), "GIVEWAYS_CHANNEL_ID"))
EVENTS_ROLE_ID = dotenv.get_key(dotenv.find_dotenv(), "EVENTS_ROLE_ID")


class Giveways(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.tracker = GivewaysTracker(bot)
        self.bot = bot

    @property
    def server(self):
        return self.bot.get_guild(0)

    def get_participate_view(self, giveway: dict):
        view = nextcord.ui.View(timeout=None)
        button = nextcord.ui.Button(label="Participer", emoji="✋")

        async def button_callback(interaction: nextcord.Interaction):
            giveways = self.tracker.get_giveways()

            this_giveway = giveways[
                [gw["message_id"] for gw in giveways].index(giveway["message_id"])
            ]
            if interaction.user.id in this_giveway["participants"]:
                await interaction.response.send_message(
                    "❌ Tu participes déjà à ce giveway.", ephemeral=True
                )
                return

            this_giveway["participants"].append(interaction.user.id)
            self.tracker.set_giveways(giveways)

            await self.send_giveway_message(this_giveway, giveway["message_id"])

            await interaction.response.send_message("✅ Réussi", ephemeral=True)

        button.callback = button_callback
        view.add_item(button)

        return view

    async def send_giveway_message(
        self,
        giveway: dict,
        edit_message_id: int | None = None,
    ):
        embed = nextcord.Embed(description="# Giveway !\n")
        embed.description += (
            "**Nombre de participants** : " + str(len(giveway["participants"])) + "\n"
        )
        embed.description += (
            "**Nombre de gagants** : " + str(giveway["number_of_winners"]) + "\n"
        )
        if giveway["different_rewards"]:
            embed.description += "**Récompenses** : \n"
            i = 1
            for reward in giveway["rewards"]:
                embed.description += (
                    "**"
                    + (EMOJIS[i - 1] if i < 4 else "#" + str(i))
                    + "** : "
                    + reward
                    + "\n"
                )

                i += 1
        else:
            embed.description += "**Récompense** : " + giveway["reward"]

        if not edit_message_id:
            return await self.bot.get_channel(GIVEWAYS_CHANNEL_ID).send(
                "<@&" + str(EVENTS_ROLE_ID) + ">",
                embed=embed,
                view=self.get_participate_view(giveway),
            )
        else:
            return (
                await self.bot.get_channel(GIVEWAYS_CHANNEL_ID)
                .get_partial_message(edit_message_id)
                .edit(embed=embed)
            )

    @nextcord.slash_command(
        "giveway",
        "Crée un giveway",
        default_member_permissions=nextcord.Permissions(administrator=True),
    )
    async def giveways(
        self,
        interaction: nextcord.Interaction,
        title=nextcord.SlashOption("titre", "Le titre du giveway", required=True),
        number_of_winners: int = nextcord.SlashOption(
            "nombre_de_gagnants",
            "Le nombre de gagnants qui vont être sélectionnés",
            required=True,
        ),
        different_rewards=nextcord.SlashOption(
            "plusieurs_récompenses",
            "Si `Oui`, une récompense par gagnant, sinon la même pour tout le monde",
            required=True,
            choices={"Oui": "Oui", "Non": "Non"},
        ),
        rewards: str = nextcord.SlashOption(
            "récompenses", 'Les récompenses SÉPARÉES PAR DES ";"', required=True
        ),
        duration_hours: float = nextcord.SlashOption(
            "durée_heures",
            "Le giveway se termine automatiquement au bout de ce temps. A ne pas utiliser avec `durée_jours`",
            required=False,
            min_value=0,
        ),
        duration_days: float = nextcord.SlashOption(
            "durée_jours",
            "Le giveway se termine automatiquement au bout de ce temps. A ne pas utiliser avec `durée_heures`",
            required=False,
            min_value=0,
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        if duration_days and duration_hours:
            await interaction.followup.send(
                "❌ Tu ne peux pas utiliser à la fois `durée_heures` et `durée_jours`.",
                ephemeral=True,
            )
            return
        if not duration_days and not duration_hours:
            await interaction.followup.send(
                "❌ Tu n'as utilisé ni `durée_heures` ni `durée_jours`.",
                ephemeral=True,
            )
            return

        if duration_days:
            duration = duration_days * 24 * 3600
        else:
            duration = duration_hours * 3600
        end_timestamp = time.time() + duration

        different_rewards = different_rewards == "Oui"

        giveway = {
            "title": title,
            "number_of_winners": number_of_winners,
            "different_rewards": different_rewards,
            "end_timestamp": end_timestamp,
            "participants": [],
        }

        if different_rewards:
            rewards = rewards.split(";")
            if len(rewards) != number_of_winners:
                await interaction.followup.send(
                    "❌ Le nombre de récompenses ("
                    + str(len(rewards))
                    + ") n'est pas égal au nombre de gagnants ("
                    + str(number_of_winners)
                    + ")"
                )
                return

            giveway["rewards"] = rewards
        else:
            giveway["reward"] = rewards

        message = await self.send_giveway_message(giveway)
        giveway["message_id"] = message.id

        self.tracker.new_giveway(giveway, message)

        await interaction.followup.send("✅ Créé", ephemeral=True)
