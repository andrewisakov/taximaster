import os
import sys
import yaml

SERVICE_ROOT_DIR = os.path.dirname(__file__)
sys.path.append(SERVICE_ROOT_DIR)

CONFIG = yaml.safe_load(open(os.path.join(SERVICE_ROOT_DIR, 'config.yaml')))
DSN = CONFIG.get('databases', {}).get('order_tracker')
INIT = CONFIG.get('databases', {}).get('init_tracker')
REDIS = 'redis://{}'.format(CONFIG.get('redis', {}).get('host'))
CALLBACK_STOP = CONFIG.get('callback_stop', [])
CALLBACK_START = CONFIG.get('callback_start', [])
TMTAPI = CONFIG.get('tmtapi', {})
TME_DB = CONFIG.get('databases', {}).get('tme_db', {})
ASTERISK_SOUNDS = CONFIG.get('asterisk_sounds', {}).get('csv', '')
ASTERISK_SOUNDS_FILE = None if not ASTERISK_SOUNDS else os.path.join(SERVICE_ROOT_DIR, ASTERISK_SOUNDS)
