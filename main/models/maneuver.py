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
    document_type = 'spell'
