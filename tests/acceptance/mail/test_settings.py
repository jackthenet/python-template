"""Acceptance tests for mail settings registration and live reads (AC-001..AC-003)."""

from __future__ import annotations

from backend.mail import register_settings
from mail_test_helpers import ensure_mail_settings, resolve_mail_config

from backend.settings import get_settings_registry


def test_ac_001_register_settings() -> None:
    """AC-001: register_settings(registry) registers the mail SMTP settings."""
    registry = get_settings_registry()
    register_settings(registry)

    expected_defaults = {
        "mail.smtp_host": "localhost",
        "mail.smtp_port": 587,
        "mail.smtp_username": "",
        "mail.smtp_password": "",
        "mail.smtp_from": "no-reply@example.com",
        "mail.smtp_tls": True,
        "mail.smtp_timeout": 30,
        "mail.from_name": "Python Template",
    }
    for key, default in expected_defaults.items():
        assert registry.get_value(key) == default


def test_ac_002_live_read_modified_host() -> None:
    """AC-002: a modified mail.smtp_host is used (live read on each send)."""
    ensure_mail_settings().set_value("mail.smtp_host", "live.example.com")

    config = resolve_mail_config()
    assert config.host == "live.example.com"


def test_ac_003_fallback_unregistered_host() -> None:
    """AC-003: an unregistered mail.smtp_host falls back to the hardcoded default."""
    get_settings_registry()  # the registry exists; the mail settings are unregistered

    config = resolve_mail_config()
    assert config.host == "localhost"
