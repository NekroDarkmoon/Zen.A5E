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
class SpellExtras(TypedDict):
    area: dict[str, Any]
    castingTime: dict
    classes: Optional[list[str]]
    components: dict[str, bool]
    concentration: bool
    duration: dict[str, str]
    materials: str
    level: int
    primarySchool: str
    range: list[str]
    ritual: bool
    savingThrow: str
    secondarySchool: list[str]
    target: dict[str, str]


class SpellRanges(Enum):
    short = 30
    medium = 60
    long = 120


class SpellTargets(Enum):
    self = 'Self'
    creature = 'Creature'
    object = 'Object'
    creatureObject = 'Creature or Object'
    other = 'Other'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                          Spell
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Spell(Source):
    """ Model for the spells entity type"""
    document_type = 'spell'

    def __init__(self, record: asyncpg.Record) -> None:
        self.name: str = record['name']
        self.description: str = record['description']
        self.type: str = record['type']
        self.extras: SpellExtras = json.loads(record['extra'])

    @classmethod
    def from_record(
        cls,
        name: str,
        description: str,
        type: str,
        extra: dict[Any]
    ) -> Self:
        pseudo = {
            'name': name,
            'description': description,
            'type': type,
            'extra': extra
        }

        return cls(record=pseudo)

    def gen_embed(self, author: discord.Member) -> list[discord.Embed]:
        """ Generates embed for spell."""

        embeds: list[discord.Embed] = list()

        extras = self.extras
        e = discord.Embed(
            title=f'{self.name} {"(Rare)" if self.type == "rare" else ""}',
            color=discord.Color.random()
        )
        e.set_author(name=author.display_name, icon_url=author.display_avatar)

        return embeds
