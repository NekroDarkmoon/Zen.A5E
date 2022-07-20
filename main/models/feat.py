# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from __future__ import annotations

# Standard library imports
import asyncpg
import discord
import logging

from typing import TYPE_CHECKING


# Local application imports
from main.models.base import Source


if TYPE_CHECKING:
    from typing_extensions import Self


log = logging.getLogger('__name__')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                          Feat
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Feat(Source):
    """ Model for feats entity type"""
    document_type = 'feat'

    def __init__(self, record: asyncpg.Record) -> None:
        self.name = record['name']
        self.description = record['description']
        self.type = record['type']

    @classmethod
    def from_record(
        cls,
        name: str,
        description: str,
        type: str,
    ) -> Self:
        pseudo = {
            'name': name,
            'description': description,
            'type': type,
        }

        return cls(record=pseudo)

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def embed(self):
        return discord.Embed(
            title=self.name,
            description=self.description,
            color=discord.Color.random()
        )
