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

