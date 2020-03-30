import os
import sys
import yaml

SERVICE_ROOT_DIR = os.path.dirname(__file__)
sys.path.append(SERVICE_ROOT_DIR)
CONFIG = yaml.safe_load(open(os.path.join(SERVICE_ROOT_DIR, 'config.yaml')))
TEMPLATES = os.path.join(SERVICE_ROOT_DIR, 'templates')
PORT = CONFIG.get('tmradio', {}).get('port', 8055)
AUTH_KEY = CONFIG.get('tmradio', {}).get('auth_key', None)
