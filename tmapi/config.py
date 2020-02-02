import os
import sys
import yaml

SERVICE_ROOT_DIR = os.path.dirname(__file__)
sys.path.append(SERVICE_ROOT_DIR)

CONFIG = yaml.safe_load(open(os.path.join(SERVICE_ROOT_DIR, 'config.yaml')))
DSN = CONFIG.get('databases', {}).get('tme_db')
REDIS = 'redis://{}'.format(CONFIG.get('redis', {}).get('host'))
