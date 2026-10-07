"""EDGE-003: a third party reconfigures the root logger while the pipeline runs
(docs/specs/structlog-logging.md).

``migrations/env.py`` calls ``logging.config.fileConfig(alembic.ini)``, which
replaces the root handler list and disables the pre-existing non-root loggers.
The feature must keep its own handlers, touch nothing it does not own, and repair
its own logger and forwarding handler at the next logging reconfigure.
"""

from __future__ import annotations

import io
import logging
import logging.config
from pathlib import Path

from logging_test_helpers import managed_sinks, pipeline_logger, wait_for_record
from settings_test_helpers import set_value_settled

import backend.logging as feature
from backend.logging import setup_logger
from backend.settings import get_settings_registry

# The alembic shape: a root-only reconfiguration that disables existing loggers.
_FILE_CONFIG_INI = """
[loggers]
keys=root

[handlers]
keys=console

[formatters]
keys=simple

[logger_root]
level=WARNING
handlers=console

[handler_console]
class=StreamHandler
level=WARNING
formatter=simple
args=(sys.stdout,)

[formatter_simple]
format=%(levelname)s: %(message)s
"""


def test_edge_003_file_config_keeps_managed_handlers() -> None:
    """EDGE-003: the managed handlers survive fileConfig; the feature repairs itself on reconfigure."""
    setup_logger()

    feature_logger = pipeline_logger()
    managed_before = managed_sinks()

    foreign = logging.StreamHandler(io.StringIO())
    foreign.setLevel(logging.ERROR)
    foreign.setFormatter(logging.Formatter("%(message)s"))
    other_feature = logging.getLogger("edge_003_other_feature")
    other_feature.addHandler(foreign)

    logging.config.fileConfig(io.StringIO(_FILE_CONFIG_INI))

    try:
        assert managed_sinks() == managed_before, "EDGE-003: the two managed handlers must survive"
        assert foreign in other_feature.handlers, "EDGE-003: a foreign handler must not be removed"
        assert foreign.level == logging.ERROR and foreign.formatter is not None, (
            "EDGE-003: a foreign handler must not be modified"
        )
        assert feature_logger.disabled is True, "the given: fileConfig disables pre-existing non-root loggers"

        lost = "edge_003 record lost before reconfigure"
        logging.getLogger("edge_003_between").warning(lost)
        log_file = Path(feature.get_settings().log_file)
        assert lost not in log_file.read_text(encoding="utf-8", errors="replace"), (
            "EDGE-003: records emitted between the third-party call and the reconfigure are not captured"
        )

        registry = get_settings_registry()
        original_level = str(registry.get_value("logging.log_level"))
        try:
            set_value_settled(registry, "logging.log_level", "DEBUG")

            assert feature_logger.disabled is False, "EDGE-003: the feature must re-enable its own logger"
            recovered = "edge_003 recovered after reconfigure"
            logging.getLogger("edge_003_after").warning(recovered)
            assert wait_for_record(log_file, lambda record: record.get("event") == recovered) is not None, (
                "EDGE-003: the forwarding handler must be re-installed at the next logging reconfigure"
            )
        finally:
            set_value_settled(registry, "logging.log_level", original_level)
    finally:
        other_feature.removeHandler(foreign)
