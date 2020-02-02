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
