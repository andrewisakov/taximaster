import psycopg2
from copy import deepcopy
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import DuplicateDatabase, DuplicateTable


def create_tables(TABLES):
    commands = []
    for tbl, tbl_data in TABLES.items():
        commands.append(f'create table {tbl} ' '({});'.format(
            ','.join(
                [f'{fname} {ftype}' for fname,
                 ftype in tbl_data.get('fields').items()]
            )
        )
        )
        for idx in tbl_data.get('indexes'):
            commands.append(f'create index on {tbl} ({idx});')
        primary_key = tbl_data.get('primary key')
        if primary_key:
            commands.append(
                f'alter table {tbl} add primary key ({primary_key});')
    return commands


def init(INIT, DSN, TABLES):
    errors = []
    try:
        with psycopg2.connect(**INIT) as pgcon:
            pgcon.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with pgcon.cursor() as c:
                dbname = DSN.get('database')
                c.execute(f'create database {dbname};')
    except DuplicateDatabase as e:
        pgcon.rollback()
        errors.append(e)

    dsn = deepcopy(DSN)
    del dsn['minsize']
    del dsn['maxsize']
    with psycopg2.connect(**dsn) as pgcon:
        pgcon.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with pgcon.cursor() as c:
            for cmd in create_tables(TABLES):
                try:
                    c.execute(cmd)
                except DuplicateTable as e:
                    errors.append(e)
                    pgcon.rollback()
    return errors
