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
class Condition(Source):
    """ Model for feats entity type"""
    document_type = 'condition'

    def __init__(self, record: asyncpg.Record) -> None:
        self.name: str = record['name']
        self.description: str = record['description']

    @classmethod
    def from_record(
        cls,
        name: str,
        description: str,
    ) -> Self:
        pseudo = {
            'name': name,
            'description': description,
        }

        return cls(record=pseudo)

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def embed(self) -> discord.Embed:
        e = discord.Embed(
            title=(self.name).capitalize(),
            description=self.description,
            color=discord.Color.random()
        )

        return e
