#!/usr/bin/env python3
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Import
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from __future__ import annotations

# Standard library imports
import datetime
import logging
import inspect
import itertools
import os
import sys
import traceback

from collections import Counter
from typing import TYPE_CHECKING, Any, Optional, Union
import asyncpg

# Third party imports
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import menus


# Local application imports
from main.cogs.utils import formats, time
from main.cogs.utils.context import Context, GuildContext
from main.cogs.utils.paginator import ZenPages


if TYPE_CHECKING:
    from main.Zen import Zen
    from utils.context import Context

GuildChannel = discord.TextChannel | discord.VoiceChannel | discord.StageChannel | discord.CategoryChannel | discord.Thread

log = logging.getLogger('__name__')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                        Meta Cog
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Meta(commands.Cog):
    def __init__(self, bot: Zen) -> None:
        self.bot: Zen = bot

    def cog_unload(self) -> None:
        self.bot.help_command = self.old_help_command

    async def cog_command_error(self, ctx: Context, error: commands.CommandError):
        if isinstance(error, commands.BadArgument):
            await ctx.send(str(error))

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Ping commands are stupid."""
        await interaction.response.send_message("Pong!")

    @app_commands.command()
    async def info(self, interaction: discord.Interaction) -> None:
        """ Helpful Information """
        e = discord.Embed(title='Help', color=discord.Colour.random())
        e.description = 'For detailed information about the bot please view the github page linked below.\n\n'
        e.description += 'Use the invite command to invite the bot to your server.'
        e.timestamp = discord.utils.utcnow()
        e.add_field(
            name='Discord Server',
            value='https://discord.com/invite/r6ufkcpSvU',
            inline=False
        )
        e.add_field(
            name='Github',
            value='https://github.com/NekroDarkmoon/Zen.A5E',
            inline=False
        )
        e.add_field(
            name='Support The Bot',
            value='[Ko-fi](https://ko-fi.com/nekrodarkmoon)',
            inline=False
        )

        await interaction.response.send_message(embed=e)

    @app_commands.command()
    async def invite(self, interaction: discord.Interaction) -> None:
        """ Joins a server. """
        perms = discord.Permissions.none()
        perms.read_messages = True
        perms.change_nickname = True
        perms.send_messages = True
        perms.send_messages_in_threads = True
        perms.create_public_threads = True
        perms.create_private_threads = True
        perms.manage_messages = True
        perms.manage_threads = True
        perms.embed_links = True
        perms.attach_files = True
        perms.read_message_history = True
        perms.use_external_emojis = True
        perms.use_external_stickers = True
        perms.use_application_commands = True

        await interaction.response.send_message(
            f'<{discord.utils.oauth_url(self.bot.client_id, permissions=perms)}>'
        )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Import
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Import
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Import
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Setup
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


async def setup(bot: Zen) -> None:
    await bot.add_cog(Meta(bot))
