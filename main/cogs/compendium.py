# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from __future__ import annotations

# Standard library imports
import logging
import re

from typing import TYPE_CHECKING, Optional
from unicodedata import category

# Third party imports
import discord  # noqa
from async_lru import alru_cache
from discord import app_commands
from discord.ext import commands

# Local application imports
if TYPE_CHECKING:
    from main.Zen import Zen
    from main.cogs.utils.context import Context


log = logging.getLogger(__name__)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Compendium
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Compendium(commands.Cog):
    def __init__(self, bot: Zen) -> None:
        self.bot: Zen = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{VIDEO GAME}')

    # ====================================================
    # Commands
    @app_commands.command(name='feat')
    @app_commands.describe(query='Feat')
    async def feat(
        self,
        interaction: discord.Interaction,
        query: str
    ):
        """ Looks up a feat. """
        await interaction.response.defer()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Setup
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
async def setup(bot: Zen):
    await bot.add_cog(Compendium(bot))
