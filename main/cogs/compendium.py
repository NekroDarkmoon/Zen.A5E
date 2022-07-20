# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from __future__ import annotations
import asyncio

# Standard library imports
import logging
import re

from typing import TYPE_CHECKING, Optional, TypedDict

# Third party imports
import discord  # noqa
from async_lru import alru_cache
from discord import app_commands
from discord.ext import commands

# Local application imports
from main.models.feat import Feat
from main.cogs.utils.paginator import SimplePages

# Local application imports
if TYPE_CHECKING:
    from asyncpg import Record
    from main.Zen import Zen
    from main.cogs.utils.context import Context


log = logging.getLogger(__name__)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         LookUp Pages
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class LookupEntry(TypedDict):
    name: str


class LookupPageEntry:
    __slots__ = ('name')

    def __init__(self, entry: LookupEntry) -> None:
        self.name: str = entry['name']

    def __str__(self) -> str:
        return f'{self.name}'


class LookupPages(SimplePages):
    def __init__(self, entries: list[LookupEntry], *, ctx: Context, per_page: int = 15):
        converted = [LookupPageEntry(entry) for entry in entries]
        super().__init__(converted, ctx=ctx, per_page=per_page)


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
        record = await self.lookup_entity(interaction, 'feats', query)

        if record is None:
            return await interaction.edit_original_message(
                content='No results Founds.')

        feat_model = Feat(record)
        return await interaction.edit_original_message(embed=feat_model.embed)

    # ====================================================
    # Lookup Utils
    async def lookup_entity(
        self, interaction: discord.Interaction, entity: str, query: str
    ) -> Optional[Record]:
        """ Looks up an entity in the database. """

        conn = self.bot.pool
        query = query.lower()

        sql = f'''SELECT * FROM {entity} WHERE LOWER(name)=$1'''
        row: Record = await conn.fetchrow(sql, query)

        if row is not None:
            return row

        # Perform Fuzzy Search
        sql = f'''
            SELECT      * 
            FROM        {entity}
            WHERE       name % $1
            ORDER BY    similarity(name, $1) DESC
            LIMIT       5
            '''

        rows: list[Record] = await conn.fetch(sql, query)

        # Return None if empty
        if rows is None or len(rows) == 0:
            return None

        choices: list[str] = [r['name'] for r in rows]
        ctx: Context = await commands.Context.from_interaction(interaction)

        # Present Choices
        p = LookupPages(entries=rows, ctx=ctx)
        p.embed.set_author(name=ctx.author.display_name)
        await p.start()

        await asyncio.sleep(10)
        return rows[1]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Setup
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
async def setup(bot: Zen):
    await bot.add_cog(Compendium(bot))
