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

# Local application imports
if TYPE_CHECKING:
    from asyncpg import Record
    from main.Zen import Zen
    from main.cogs.utils.context import Context


log = logging.getLogger(__name__)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                        Lookup View
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class LookupEntry(TypedDict):
    name: str


class LookupPageEntry:
    __slots__ = ('name')

    def __init__(self, entry: LookupEntry) -> None:
        self.name: str = entry['name']

    def __str__(self) -> str:
        return f'{self.name}'


class LookupView(discord.ui.View):
    def __init__(self, interaction:  discord.Interaction, data: list[Record]):
        super().__init__()
        self.value = None

        # Display Data
        self._lookup_data = [LookupPageEntry(entry) for entry in data]
        self._interaction = interaction
        self._embed = discord.Embed(title='Multiple Matches')

        # Add SelectOptions to UI
        choices = [i.name for i in self._lookup_data]
        for c in choices:
            self.select.add_option(label=c, value=c)

    def get_suggestions(self) -> discord.Embed:
        entries = list()

        for idx, entry in enumerate(self._lookup_data):
            entries.append(f'**{idx + 1}** - {entry}')

        desc = 'Pick one of the following suggestions from the menu. \n\n'
        desc += '\n'.join(entries)
        self._embed.description = desc
        self._embed.colour = discord.Colour.random()

        return self._embed

    @discord.ui.select(
        placeholder='Select an option...',
        min_values=1,
        max_values=1,
        row=0
    )
    async def select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        await interaction.response.defer()
        self.value = select.values[0]
        self.stop()


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
        return await interaction.edit_original_message(embed=feat_model.embed, view=None)

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
            LIMIT       15
            '''

        rows: list[Record] = await conn.fetch(sql, query)

        # Return None if empty
        if rows is None or len(rows) == 0:
            return None

        ctx: Context = await commands.Context.from_interaction(interaction)

        # Present Choices
        view = LookupView(interaction, rows)
        view._embed.set_author(name=ctx.author.display_name)

        await interaction.edit_original_message(
            embed=view.get_suggestions(), view=view
        )
        await view.wait()

        value = view.value
        if value is None:
            return None

        for r in rows:
            if r['name'] == value:
                return r

        return None

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Setup
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


async def setup(bot: Zen):
    await bot.add_cog(Compendium(bot))
