import os
import sys
import yaml
import xmltodict
from threading import BoundedSemaphore

SERVICE_ROOT_DIR = os.path.dirname(__file__)
sys.path.append(SERVICE_ROOT_DIR)

CONFIG = yaml.safe_load(open(os.path.join(SERVICE_ROOT_DIR, 'config.yaml')))
REDIS = CONFIG.get('redis', {})
CHANNELS = REDIS.get('channels', [])
REDIS = REDIS.get('host')
DSN = CONFIG.get('dsn')
TME_DB = CONFIG.get('tme_db')

DSN = (DSN.get('minsize'), DSN.get('maxsize'), 'postgres://{}:{}@{}/{}'.format(
    DSN.get('user'), DSN.get('password'), DSN.get('host'), DSN.get('database')
))
TME_DB = (
    TME_DB.get('minsize', 1),
    TME_DB.get('maxsize', 10), 
    'postgres://{}:{}@{}/{}'.format(
        TME_DB.get('user', 'postgres'), 
        TME_DB.get('password', 'postgres'), 
        TME_DB.get('host', 'localhost'), 
        TME_DB.get('database', 'tme_db')
    )
)
