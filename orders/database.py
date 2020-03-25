import csv
from functools import lru_cache
from .config import INIT, DSN, ASTERISK_SOUNDS_FILE
from core.database import init

TABLES = {
    'order_events': {
        'fields': {
            'order_id': 'integer not null',
            'event': 'varchar(256) not null',
            'data': 'jsonb',
            'timestamp': 'timestamptz not null default now()',
        },
        'indexes': ('timestamp',
                    # 'order_id, timestamp',
                    ),
        'primary key': 'order_id, timestamp',
    }
}


class AsteriskSounds:
    MARK_TYPE = 0
    COLOR_TYPE = 1
    DIGIT_TYPE = 2
    MESSAGE_TYPE = 4

    def __init__(self, csv_file=ASTERISK_SOUNDS_FILE):
        self.csv_file = csv_file
        self._csv_data = {}
        self._load()

    def _load(self):
        with open(self.csv_file) as f:
            reader = csv.reader(f, delimiter=';')
            self._csv_data = [(r[1].upper(), r[2], int(r[3])) for r in reader]

    @lru_cache(maxsize=100)
    def get(self, name, type=None):
        r = [r for r in self._csv_data if (
            r[0] == name.upper()) and(r[2] is not None and r[2] == type)]
        return r[0][1] if r else ''
