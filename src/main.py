"""Application entrypoint.

Registers every feature's settings in the shared settings registry at startup,
then calls ``setup_logger`` exactly once (spec section 3.3, REQ-011). The call
is idempotent and thread-safe, so a second call (e.g. from a test or a
re-import) is a no-op.
"""

from backend.authentication import register_settings as register_authentication_settings
from backend.eventbus import register_settings as register_eventbus_settings
from backend.logging import register_settings as register_logging_settings
from backend.logging import setup_logger
from backend.settings import get_settings_registry
from backend.usermanagement import register_settings as register_usermanagement_settings

_registry = get_settings_registry()
register_logging_settings(_registry)
register_authentication_settings(_registry)
register_usermanagement_settings(_registry)
register_eventbus_settings(_registry)

setup_logger()
