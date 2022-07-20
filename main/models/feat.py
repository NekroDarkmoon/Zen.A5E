# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from __future__ import annotations

import asyncpg
import logging

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing_extensions import Self


log = logging.getLogger('__name__')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                          Feat
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Feat:
    """ Model for feats entity type"""
    document_type = 'feat'

    def __init__(self, record: asyncpg.Record) -> None:
        self.name = record['name']
        self.desc = record['desc']

    @property
    def description(self):
        return self.desc

    @classmethod
    def from_record(
        cls, name: str,
        description: str
    ) -> Self:
        pseudo = {
            'name': name,
            'desc': description,
        }

        return cls(record=pseudo)

    def __hash__(self) -> int:
        return hash(self.name)
