import os
import tmradio.main
import core.logger as _logger
import settings

tmradio.main.LOGGER = _logger.rotating_log(
    os.path.join(
        settings.SERVICE_ROOT_DIR, 'logs/tmradio.log',
    ), 'tmradio')

tmradio.main.main()
