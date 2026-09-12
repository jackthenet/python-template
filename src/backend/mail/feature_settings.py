"""Feature-owned settings registration and live config resolution for mail.

REQ-001: ``register_settings(registry)`` registers the mail SMTP
``SettingDefinition``s (no import side effects). REQ-002: ``resolve_mail_config``
reads the settings live on each call, falling back to the hardcoded defaults
when the registry does not exist or a key is unregistered.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from backend.logging import logged

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry


@dataclass(frozen=True)
class MailConfig:
    """The resolved SMTP configuration (read live on each send)."""

    host: str
    port: int
    username: str
    password: str
    use_tls: bool
    timeout: float
    from_name: str
    from_address: str


def _read_setting(registry: SettingsRegistry | None, key: str, fallback: Any) -> Any:
    """Read ``key`` live from ``registry``; return ``fallback`` when absent."""
    if registry is None or not registry.has(key):
        return fallback
    return registry.get_value(key)


def resolve_mail_config() -> MailConfig:
    """Resolve the SMTP configuration live (REQ-002).

    Reads from the shared registry (``required=False``) on each call; when the
    registry does not exist or a key is unregistered, the hardcoded default is
    used.
    """
    from backend.settings import get_settings_registry

    registry = get_settings_registry(required=False)
    return MailConfig(
        host=_read_setting(registry, "mail.smtp_host", "localhost"),
        port=_read_setting(registry, "mail.smtp_port", 587),
        username=_read_setting(registry, "mail.smtp_username", ""),
        password=_read_setting(registry, "mail.smtp_password", ""),
        from_address=_read_setting(registry, "mail.smtp_from", "no-reply@example.com"),
        use_tls=_read_setting(registry, "mail.smtp_tls", True),
        timeout=_read_setting(registry, "mail.smtp_timeout", 30),
        from_name=_read_setting(registry, "mail.from_name", "Python Template"),
    )


@logged(slow_threshold_ms=5)
def register_settings(registry: SettingsRegistry) -> None:
    """Register the mail feature's SMTP settings with ``registry`` (REQ-001)."""
    from backend.settings import SettingDefinition, SettingKind

    registry.register(
        SettingDefinition(
            key="mail.smtp_host",
            kind=SettingKind.TEXT,
            default="localhost",
            category="application",
            group="mail",
        )
    )
    registry.register(
        SettingDefinition(
            key="mail.smtp_port",
            kind=SettingKind.NUMBER,
            default=587,
            min_value=1,
            max_value=65535,
            category="application",
            group="mail",
        )
    )
    registry.register(
        SettingDefinition(
            key="mail.smtp_username",
            kind=SettingKind.TEXT,
            default="",
            category="application",
            group="mail",
        )
    )
    registry.register(
        SettingDefinition(
            key="mail.smtp_password",
            kind=SettingKind.TEXT,
            default="",
            category="application",
            group="mail",
        )
    )
    registry.register(
        SettingDefinition(
            key="mail.smtp_from",
            kind=SettingKind.EMAIL,
            default="no-reply@example.com",
            category="application",
            group="mail",
        )
    )
    registry.register(
        SettingDefinition(
            key="mail.smtp_tls",
            kind=SettingKind.BOOLEAN,
            default=True,
            category="application",
            group="mail",
        )
    )
    registry.register(
        SettingDefinition(
            key="mail.smtp_timeout",
            kind=SettingKind.NUMBER,
            default=30,
            min_value=1,
            category="application",
            group="mail",
        )
    )
    registry.register(
        SettingDefinition(
            key="mail.from_name",
            kind=SettingKind.TEXT,
            default="Python Template",
            category="application",
            group="mail",
        )
    )
