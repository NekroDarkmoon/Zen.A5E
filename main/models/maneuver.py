# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from __future__ import annotations
from enum import Enum

# Standard library imports
import asyncpg
import discord
import json
import logging

from typing import TYPE_CHECKING, Any, Optional, TypedDict
from main.cogs.utils.formats import chunk_text


# Local application imports
from main.models.base import Source


if TYPE_CHECKING:
    from typing_extensions import Self


log = logging.getLogger('__name__')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                       Spell Data
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class ManeuverExtras(TypedDict):
    activation: dict[str, Any]
    degree: int
    exertionCost: int
    tradition: str


class ManeuverTraditions(Enum):
    adamantMountain = 'Adamant Mountain'
    bitingZephyr = 'Biting Zephyr'
    mirrorsGlint = 'Mirrors Glint'
    mistAndShade = 'Mist And Shade'
    rapidCurrent = 'Rapid Current'
    razorsEdge = 'Razors Edge'
    sanguineKnot = 'Sanguine Knot'
    spiritedSteed = 'Spirited Steed'
    temperedIron = 'Tempered Iron'
    toothAndClaw = 'Tooth And Claw'
    unendingWheel = 'Unending Wheel'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                          Spell
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Maneuver(Source):
    """ Model for the spells entity type"""
    document_type = 'maneuver'

    def __init__(self, record: asyncpg.Record) -> None:
        self.name: str = record['name']
        self.description: str = record['description']
        self.extras: ManeuverExtras = json.loads(record['extra'])

    @classmethod
    def from_record(
        cls,
        name: str,
        description: str,
        extra: dict[Any]
    ) -> Self:
        pseudo = {
            'name': name,
            'description': description,
            'extra': extra
        }

        return cls(record=pseudo)

    def __hash__(self) -> int:
        return hash(self.name)

    def gen_embed(self, author: discord.Member) -> list[discord.Embed]:
        """ Generates embed for maneuver."""

        embeds: list[discord.Embed] = list()
        extras = self.extras
        e = discord.Embed(title=self.name, color=discord.Colour.random())
        e.set_author(name=author.display_name, icon_url=author.display_avatar)

        # Add degree and tradition
        level = ordinal(extras['degree'])
        tradition = ManeuverTraditions[extras['tradition']].value
        e.description = f"*{level} degree, {tradition}*"

