import os
import orders.main
import core.logger as _logger
import orders.config as settings

orders.main.LOGGER = _logger.rotating_log(
    os.path.join(
        settings.SERVICE_ROOT_DIR, 'logs/order_tracker.log',
    ), 'order_tracker')

orders.main.main()
