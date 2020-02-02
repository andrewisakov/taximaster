from .config import INIT, DSN
from core.database import init

TABLES = {
    'order_events': {
        'fields': {
            'order_id': 'integer not null',
            'event': 'varchar(256) not null',
            'data': 'jsonb',
            'timestamp': 'timestamptz not null default now()',
        },
        'indexes': ('timestamp', 'order_id, timestamp',),
        'primary key': 'order_id, timestamp',
    }
}

result = init(INIT, DSN, TABLES)
