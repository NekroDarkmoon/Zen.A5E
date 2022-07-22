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

