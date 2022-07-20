# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from __future__ import annotations

import logging

from abc import ABC


log = logging.getLogger(__name__)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Source
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Source(ABC):
    ...


class Trait:
    def __init__(self, name, text) -> None:
        pass
