import os
import sys
import yaml
import core.logger as _logger


SERVICE_ROOT_DIR = os.path.dirname(__file__)
sys.path.append(SERVICE_ROOT_DIR)

CONFIG = yaml.safe_load(open(os.path.join(SERVICE_ROOT_DIR, 'config.yaml')))
REDIS = 'redis://{}'.format(CONFIG.get('redis', {}).get('host'))

TME_DB = CONFIG.get('databases', {}).get('tme_db', {})
IMAP = CONFIG.get('imap', {})
LEGAL_SENDERS = CONFIG.get('senders', {})
MAIL_SCHEMA = CONFIG.get('mail')
LOGGER = _logger.rotating_log(
    os.path.join(
        SERVICE_ROOT_DIR, 'logs/payment.log',
    ), 'mayment')
