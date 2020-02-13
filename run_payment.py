import os
import payment.main
import core.logger as _logger
import payment.config as settings

payment.main.LOGGER = _logger.rotating_log(
    os.path.join(
        settings.SERVICE_ROOT_DIR, 'logs/payments.log',
    ), 'payments')

payment.main.main()
