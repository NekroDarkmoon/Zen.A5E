# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from __future__ import annotations

# Standard library imports
import logging
import re

from typing import TYPE_CHECKING, Optional

# Third party imports
import discord  # noqa
from async_lru import alru_cache
from discord import app_commands
from discord.ext import commands

# Local application imports
from main.models.feat import Feat

# Local application imports
if TYPE_CHECKING:
    from asyncpg import Record
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
        record = await self.lookup_entity('feats', query)

        feat_model = Feat(record)
        return await interaction.edit_original_message(embed=feat_model.embed)

    # ====================================================
    # Lookup Utils
    async def lookup_entity(self, entity: str, query: str) -> Record:
        conn = self.bot.pool
        query = query.lower()

        sql = f'''SELECT * FROM {entity} WHERE LOWER(name)=$1'''
        row: Record = await conn.fetchrow(sql, query)

        if row is None:
            sql = f'''
                SELECT      * 
                FROM        {entity}
                WHERE       name % $1
                ORDER BY    similarity(name, $1) DESC
                LIMIT       5
            '''

            rows: list[Record] = await conn.fetch(sql, query)
            row = await self.disambiguate(rows, query)
        else:
            return row

    async def disambiguate(self, rows, query):
        choices = [r['name'] for r in rows]

        if choices is None or len(choices) == 0:
            raise RuntimeError('Query not Found.')

        names = '\n'.join(r['name'] for r in rows)
        raise RuntimeError(f'Tag not found. Did you mean...\n{names}')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Setup
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


async def setup(bot: Zen):
    await bot.add_cog(Compendium(bot))
