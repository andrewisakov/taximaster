import os
import sms.main
import core.logger as _logger
import sms.config as settings

sms.main.LOGGER = _logger.rotating_log(
    os.path.join(
        settings.SERVICE_ROOT_DIR, 'logs/sms.log',
    ), 'sms')

sms.main.main()
