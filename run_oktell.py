import os
import oktell.main
import core.logger as _logger
import settings

oktell.main.LOGGER = _logger.rotating_log(
    os.path.join(
        settings.SERVICE_ROOT_DIR, 'logs/oktell.log',
    ), 'oktell')

oktell.main.main()
