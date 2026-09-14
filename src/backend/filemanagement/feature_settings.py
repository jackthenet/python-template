"""Feature-owned settings registration for file-management (REQ-024).

``register_settings(registry)`` registers the feature's ``SettingDefinition``s
via ``registry.register_feature("filemanagement", [...])`` — no import side
effects: it is an explicit function called at wiring time, not at import. All
settings are read live on each operation; unregistered keys fall back to the
hardcoded defaults (the defaults registered here are the same hardcoded
fallbacks). The registration name is ``filemanagement`` (no hyphen) because
the settings key format forbids hyphens. Repository/backend injection stays
constructor args — it is not a setting. ``avatar_base_url`` is the host only
(no scheme); the avatar URL is constructed as ``https://<host>/files/<file_id>``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.logging import logged

if TYPE_CHECKING:
    from backend.settings import SettingsRegistry

# Hardcoded fallback defaults (also the registered setting defaults).
DEFAULT_STORAGE_ROOT: str = "./data/files"
DEFAULT_MAX_FILE_SIZE: int = 10485760  # 10 MB
DEFAULT_AVATAR_MAX_SIZE: int = 2097152  # 2 MB
DEFAULT_ALLOWED_TYPES: list[str] = [
    "application/octet-stream",
    "application/pdf",
    "application/zip",
    "text/plain",
    "text/csv",
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
]
DEFAULT_AVATAR_BASE_URL: str = "files.example.com"  # host only, no scheme

# Settings key prefix: the settings key format forbids hyphens.
FEATURE_NAME: str = "filemanagement"


@logged(slow_threshold_ms=5)
def register_settings(registry: SettingsRegistry) -> None:
    """Register the file-management feature's settings with ``registry`` (REQ-024)."""
    from backend.settings import SettingDefinition, SettingKind

    registry.register_feature(
        FEATURE_NAME,
        [
            SettingDefinition(
                key="filemanagement.storage_root",
                kind=SettingKind.TEXT,
                default=DEFAULT_STORAGE_ROOT,
                category="application",
                group=FEATURE_NAME,
            ),
            SettingDefinition(
                key="filemanagement.max_file_size",
                kind=SettingKind.NUMBER,
                default=DEFAULT_MAX_FILE_SIZE,
                category="application",
                group=FEATURE_NAME,
            ),
            SettingDefinition(
                key="filemanagement.avatar_max_size",
                kind=SettingKind.NUMBER,
                default=DEFAULT_AVATAR_MAX_SIZE,
                category="application",
                group=FEATURE_NAME,
            ),
            SettingDefinition(
                key="filemanagement.allowed_types",
                kind=SettingKind.LIST,
                default=DEFAULT_ALLOWED_TYPES,
                category="application",
                group=FEATURE_NAME,
            ),
            SettingDefinition(
                key="filemanagement.avatar_base_url",
                kind=SettingKind.TEXT,
                default=DEFAULT_AVATAR_BASE_URL,
                category="application",
                group=FEATURE_NAME,
            ),
        ],
    )
