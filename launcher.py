#!/usr/bin/env python3
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import os
from typing import Optional
import aiohttp
import asyncio
import asyncpg
import click
import discord
import json
import contextlib
import logging
import sys
import traceback

from logging.handlers import RotatingFileHandler

from markdownify import markdownify as md

import main.settings.config as config
from main.Zen import Zen
from main.cogs.utils.db import DB

# Try Import
try:
    import uvloop
except ImportError:
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


BULLET_STYLE = ['-', '+', '*']


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                          Main
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@click.group(invoke_without_command=True, options_metavar='[options]')
@click.pass_context
def main(ctx):
    """Starts the process of launching the bot."""
    if ctx.invoked_subcommand is None:
        with setup_logger():
            asyncio.run(run_bot())


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                      Setup Logging
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class RemoveNoise(logging.Filter):
    """Filter for logger"""

    def __init__(self):
        super().__init__(name='discord.state')

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelname == 'WARNING' and 'referencing an unknown' in record.msg:
            return False
        return True


@contextlib.contextmanager
def setup_logger():
    """Setup Logger as a Context Manager"""
    try:
        # __enter__
        max_bytes: int = 64 * 1024 * 1024
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.state').addFilter(RemoveNoise())

        logger: logging.Logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler: RotatingFileHandler = RotatingFileHandler(
            filename='.logs/Zen.log', encoding='utf_8', mode='w', maxBytes=max_bytes, backupCount=10)
        date_format = '%Y-%m-%d %H:%M:%S'
        format: logging.Formatter = logging.Formatter(
            '[{asctime}] [{levelname:<7}] {name}: {message}', date_format, style='{')
        handler.setFormatter(format)
        logger.addHandler(handler)

        yield

    finally:
        # __exit__
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Run Bot
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
async def run_bot():
    """ Starts the process of running the bot"""
    log = logging.getLogger()

    # Create DB Connection
    try:
        pool = await DB.create_pool(config.uri)
    except Exception as e:
        print(e)
        click.echo("Unable to setup/start Postgres. Exiting. ", file=sys.stderr)
        log.exception('Unable to setup/start Postgres. Exiting.')
        return

    if pool is None:
        raise RuntimeError('Unable to connect to db.')

    bot = Zen()
    bot.pool = pool
    await bot.start()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Database
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@main.group(short_help='database stuff', options_metavar='[options]')
def db():
    pass


@db.command(short_help='Update the database.')
@click.option('-q', '--quiet', help='Reduce output verbosity.', is_flag=True)
@click.pass_context
def update_db(ctx, quiet):
    """ Update the database with the latest json. """
    asyncio.run(_update_db('feats', quiet))


async def _update_db(compendium, quiet):
    # TODO: Add downloading new files

    # Open db connection
    try:
        pool = await DB.create_pool(config.uri)
    except Exception:
        click.echo(
            f'Could not create PostgreSQL connection pool.\n{traceback.format_exc()}', err=True)
        return

    # Update Feats
    feats = [file for file in os.listdir(
        f'./.packs/feats') if file.endswith('.json')]
    files = {f'./.packs/feats/{f}' for f in feats}
    sql, data = get_feat_data(files)
    await pool.executemany(sql, data)

    synergyFeats = [file for file in os.listdir(
        f'./.packs/synergyFeats') if file.endswith('.json')]
    files = {f'./.packs/synergyFeats/{f}' for f in synergyFeats}
    sql, data = get_feat_data(files, 'synergy')
    await pool.executemany(sql, data)

    spells = [file for file in os.listdir(
        f'./.packs/spells') if file.endswith('.json')]
    files = {f'./.packs/spells/{s}' for s in spells}
    sql, data = get_spell_data(files)
    await pool.executemany(sql, data)

    rareSpells = [file for file in os.listdir(
        f'./.packs/rareSpells') if file.endswith('.json')]
    files = {f'./.packs/rareSpells/{s}' for s in rareSpells}
    sql, data = get_spell_data(files, 'rare')
    await pool.executemany(sql, data)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                      Feat Readers
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_spell_data(
    files: list[str], type: Optional[str] = None
) -> tuple[str, list[tuple[str, str]]]:
    """ Generates sql for spells from files"""
    print('====================================')
    print(f'Spells - {"{type}" if type == "rare" else ""}')
    print('====================================')
    sql: str = ''' INSERT INTO spells(name, description, type, extra)
                   VALUES($1, $2, $3, $4::jsonb)
                   ON CONFLICT (name)
                   DO UPDATE SET description=$2,
                                 type=$3,
                                 extra=$4::jsonb
               '''
    sql_data: list[tuple[str, str]] = list()

    for file in files:
        with open(file, 'r', encoding='utf8') as reader:
            print(file)
            data = json.load(reader)

            # Structure for db input
            name: str = data['name']
            description: str = md(
                data['data']['description'], bullets=BULLET_STYLE)
            system = data['data']

            extras = {
                'area': system['area'],
                'castingTime': system['activation'],
                'classes': None,
                'components': system['components'],
                'concentration': system['concentration'],
                'duration': system['duration'],
                'materials': f"{system['materials']} {'which the spell consumes.' if system['materials'] else ''}",
                'level': system['level'],
                'primarySchool': system['schools']['primary'],
                'range': system['range'],
                'savingThrow': f"{system['save']['targetAbility']} {'halves' if 'half damage' in system['save']['onSave'].lower() else 'negates'}",
                'secondarySchool': system['schools']['secondary'],
            }

            sql_data.append((name, description, type, extras))

    return (sql, sql_data)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                      Feat Readers
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def get_feat_data(
    files: list[str], type: Optional[str] = None
) -> tuple[str, list[tuple[str, str]]]:
    """ Generates sql for feats from files"""
    print('====================================')
    print(f'Feats - {"{type}" if type == "synergy" else ""}')
    print('====================================')

    sql: str = ''' INSERT INTO feats(name, description, type)
                   VALUES($1, $2, $3)
                   ON CONFLICT (name)
                   DO UPDATE SET description=$2,
                                 type=$3
               '''
    sql_data: list[tuple[str, str]] = list()

    for file in files:
        with open(file, 'r', encoding='utf8') as reader:
            print(file)
            data = json.load(reader)

            # Structure for db input
            name: str = data['name']
            description: str = md(
                data['data']['description'], bullets=BULLET_STYLE)

            sql_data.append((name, description, type))

    return (sql, sql_data)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                         Imports
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#                          Init
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == '__main__':
    main()
