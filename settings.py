import os
import sys

SERVICE_ROOT_DIR = os.path.dirname(__file__)
sys.path.append(SERVICE_ROOT_DIR)
REDIS_HOST = 'redis://192.168.222.21'

TM_HOST = '192.168.222.211'
TM_PORT = 8089

SAULT = '1292'

DSN = 'dbname=tme_db user=postgres password=postgres host=192.168.222.179'
