#!/usr/bin/env python3
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Import
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from __future__ import annotations

# Standard library imports
import datetime
from typing import Any, Iterable, Optional, Sequence

# Third party imports
import discord
from discord import app_commands
from discord.ext import commands

# Local application imports


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Plural
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Plural:
    def __init__(self, value: int) -> None:
        self.value = value

    def __format__(self, format_spec: str) -> str:
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'

        if abs(v) != 1:
            return f'{v} {plural}'

        return f'{v} {singular}'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                       Human Join
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def human_join(seq: Sequence[str], delim: str = ', ', final: str = 'or') -> str:
    size = len(seq)
    if size == 0:
        return ''

    if size == 1:
        return seq[0]

    if size == 2:
        return f'{seq[0]} {final} {seq[1]}'

    return delim.join(seq[:-1] + f'{final} {seq[-1]}')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                       TabularData
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class TabularData:
    def __init__(self) -> None:
        self._widths: list[int] = list()
        self._columns: list[str] = list()
        self._rows: list[list[str]] = list()

    def set_columns(self, columns: list[str]) -> None:
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row: Iterable[Any]) -> None:
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for idx, elem, in enumerate(rows):
            width = len(elem) + 2
            if width > self._widths[idx]:
                self._widths[idx] = width

    def add_rows(self, rows: Iterable[Iterable[Any]]) -> None:
        for row in rows:
            self.add_row(row)

    def render(self) -> str:
        """Renders a table in rST format.
        Example:
        +-------+-----+
        | Name  | Age |
        +-------+-----+
        | Alice | 24  |
        |  Bob  | 19  |
        +-------+-----+
        """

        sep = '+'.join('-' * w for w in self._widths)
        sep = f'+{sep}+'

        to_draw = [sep]

        def get_entry(d):
            elem = '|'.join(f'{e:^{self._widths[i]}}' for i, e in enumerate(d))
            return f'|{elem}|'

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return '\n'.join(to_draw)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         format dt
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def format_dt(
        dt: datetime.datetime,
        style: Optional[str] = None,
        to_utc: bool = True
) -> str:
    if dt.tzinfo is None and to_utc:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    if style is None:
        return f'<t:{int(dt.timestamp())}>'

    return f'<t:{int(dt.timestamp())}:{style}>'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                       Color String
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def text_color(content: str, color: str = None) -> str:
    if color == 'red':
        return f'```diff\n- {content}```'
    elif color == 'orange':
        return f'```cs\n#{content}```'
    elif color == 'yellow':
        return f'```fix\n {content}```'
    elif color == 'green':
        return f'```diff\n+ {content}```'
    elif color == 'cyan':
        return f'```yaml\n{content}```'
    elif color == 'blue':
        return f'```ini\n[{content}]```'
    else:
        return f'```\n{content}```'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Chunk
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def chunk_text(
    text: str,
    max_chunk_size: int = 1024,
    chunk_on=("\n\n", "\n", ". ", ", ", " "),
    chunker_i=0
) -> list[str]:
    """
    Recursively chunks *text* into a list of str, with each element no longer than *max_chunk_size*.
    Prefers splitting on the elements of *chunk_on*, in order.
    """

    if len(text) <= max_chunk_size:
        return [text]

    if chunker_i >= len(chunk_on):  # we have no more preferred chunk_on characters
        # optimization: instead of merging a thousand characters, just use list slicing
        return [text[:max_chunk_size], *chunk_text(text[max_chunk_size:], max_chunk_size, chunk_on, chunker_i + 1)]

    # Split on the current character
    chunks = list()
    split_char = chunk_on[chunker_i]
    for chunk in text.split(split_char):
        chunk = f"{chunk}{split_char}"
        if len(chunk) > max_chunk_size:  # this chunk needs to be split more, recurse
            chunks.extend(chunk_text(
                chunk, max_chunk_size, chunk_on, chunker_i + 1))
        # this chunk can be merged
        elif chunks and len(chunk) + len(chunks[-1]) <= max_chunk_size:
            chunks[-1] += chunk
        else:
            chunks.append(chunk)

    # if the last chunk is just the split_char, yeet it
    if chunks[-1] == split_char:
        chunks.pop()

    # remove extra split_char from last chunk
    chunks[-1] = chunks[-1][: -len(split_char)]
    return chunks
