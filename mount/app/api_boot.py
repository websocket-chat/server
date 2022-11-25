import atexit

from app.api import init_api
from app.common import logger
from app.common import settings

logger.configure_logging(
    app_env=settings.APP_ENV,
    log_level=settings.APP_LOG_LEVEL,
)
logger.overwrite_exception_hook()
atexit.register(logger.restore_exception_hook)

app = init_api()
