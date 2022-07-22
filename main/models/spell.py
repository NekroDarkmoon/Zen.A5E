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

    def __hash__(self) -> int:
        return hash(self.name)

    def gen_embed(self, author: discord.Member) -> list[discord.Embed]:
        """ Generates embed for spell."""

        embeds: list[discord.Embed] = list()

        extras = self.extras
        e = discord.Embed(
            title=f'{self.name} {"(Rare)" if self.type == "rare" else ""}',
            color=discord.Color.random()
        )
        e.set_author(name=author.display_name, icon_url=author.display_avatar)

        # Add level and type
        def ordinal(n): return "%d%s" % (
            n, "tsnrhtdd"[(n//10 % 10 != 1)*(n % 10 < 4)*n % 10::4])

        level = ordinal(extras['level'])
        schools = ', '.join(extras['secondarySchool'])
        desc = f"*{level}-level {extras['primarySchool']}; {schools}*"
        e.description = desc

        meta = ''
        # Add Casting time
        cast_time = extras['castingTime']
        meta += f"\n**Casting Time**: {cast_time['cost']} {cast_time['type']} {cast_time['reactionTrigger'] if len(cast_time['reactionTrigger']) > 0 else ''}"
        if extras['ritual']:
            meta += f" *(Ritual)*"

        # Add Range
        spellRange = extras['range'][0]
        if spellRange in ['short', 'medium', 'long']:
            meta += f'\n**Range**: {spellRange.capitalize()} *({SpellRanges[spellRange].value}ft.)*'
        else:
            meta += f'\n**Range**: {spellRange.capitalize()}'

        # Add Area
        areaShape = extras['area']['shape']
        if areaShape != '':
            areaSize = ''

            if areaShape == 'cone':
                areaSize = f"{extras['area']['length']}ft"
            elif areaShape == 'cube':
                areaSize = f"{extras['area']['width']}ft"
            elif areaShape == 'line':
                areaSize = f"{extras['area']['length']}ft by {extras['area']['width']}ft"
            else:
                areaSize = f"{extras['area']['radius']}ft. radius"

            meta += f"\n**Area**: {areaSize} {areaShape}"

        # Add Target
        target = extras['target']
        if target['type'] != '':
            meta += f"\n**Target**: {target['quantity']} {SpellTargets[target['type']].value}"

        # Add Components
        vocal = 'V' if extras['components']['vocalized'] else ''
        seen = 'S' if extras['components']['seen'] else ''
        mat = 'M' if extras['components']['material'] else ''
        conc = 'C' if extras['concentration'] else ''
        materials = f"({extras['materials']})" if len(
            extras['materials']) > 1 else ''

        meta += f"\n**Components**: {', '.join(filter(None, [vocal, seen, mat, conc]))} {materials}"

        # Add Duration
        dur = extras['duration']
        dur = f"{dur['value']} {dur['unit'].capitalize() if dur['unit'] != 'instantaneous' else dur['unit'].capitalize()}"
        meta += f"\n**Duration**: {dur}"

        # Add Saving Throw
        meta += f"\n**Saving Throw**: {extras['savingThrow'].capitalize()}"

        # Add Meta
        e.add_field(name='Meta', value=meta, inline=False)

        # Add Description
        if len(self.description) > 1024:
            chunks = chunk_text(self.description, max_chunk_size=1000)
            e.add_field(name='Description',
                        value=chunks[0], inline=False)

            embeds.append(e)
            for chunk in chunks[1:]:
                embeds.append(
                    discord.Embed(description=chunk, color=e.color)
                )

        else:
            e.add_field(name='Description',
                        value=self.description, inline=False)
            embeds.append(e)

        return embeds
