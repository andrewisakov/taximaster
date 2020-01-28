import os
import tmapi.main
import core.logger as _logger
import settings

tmapi.main.LOGGER = _logger.rotating_log(
    os.path.join(
        settings.SERVICE_ROOT_DIR, 'logs/tmapi.log',
    ), 'tmapi')

tmapi.main.main()
