"""AC-020 / REQ-017: the composition root wires the session lookup into the shared check.

Reproduction test for issue ``session-lookup-unwired``. Every other permissions
test builds its own ``PermissionService`` and injects a lookup, so none of them
can see the missing ``session_lookup=`` argument in ``src/main.py``: the composed
service fails closed with ``storage_error`` for every token, and the specified
positive branch of AC-020 is unreachable in the composed application
(docs/specs/user-roles-permissions.md Impact Analysis: the session repository
"is used by the check").

The pattern is the established composition-root test
(``tests/acceptance/settings_coverage/test_wiring.py``): run ``import main`` in a
fresh interpreter. ``cwd`` is the test's temp directory, so the composition
root's relative SQLite URLs (``sqlite:///./data/...``) and its ``settings/``
directory are created inside the temp dir and nothing leaks into the repo.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src"

# The composed application: an admin user (the implicit wildcard, REQ-010, so the
# only thing that can deny the valid-token check is session validation) plus the
# session rows, then four checks through main._permission_service.
_CODE = f"""
import hashlib
import sys
from datetime import UTC, datetime, timedelta

sys.path.insert(0, {str(_SRC)!r})

import main
from backend.authentication import Session
from backend.usermanagement import User

now = datetime.now(UTC)
week = now + timedelta(days=7)


def add_user(username, email):
    # Direct row insert: admin skips the enforced UserManager.create_user path.
    return main._user_repository.add(
        User(
            username=username,
            email=email,
            password_hash="argon2id-placeholder",
            roles=["admin"],
            created_at=now,
            updated_at=now,
        )
    )


def add_session(user_id, token, revoked=False):
    # The same SHA-256 hash the check computes (ADR-073).
    return main._session_repository.add(
        Session(
            user_id=user_id,
            token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            created_at=now,
            expires_at=week,
            revoked=revoked,
        )
    )


alice = add_user("alice", "alice@example.com")
bob = add_user("bob", "bob@example.com")
add_session(alice.id, "valid-token")
add_session(alice.id, "revoked-token", revoked=True)
add_session(bob.id, "bob-token")

check = main._permission_service.has_permission
print(
    [
        check(alice.id, "usermanagement.get_user", session_token="valid-token"),
        check(alice.id, "usermanagement.get_user", session_token="revoked-token"),
        check(alice.id, "usermanagement.get_user", session_token="bob-token"),
        check(alice.id, "usermanagement.get_user", session_token="unknown-token"),
    ]
)
"""


def test_ac_020_composition_root_validates_session_token(tmp_path: Path) -> None:
    """AC-020 / REQ-017: the composed check validates a provided session token.

    A valid, unrevoked, unexpired session token for the user lets the check
    proceed (``True``); a revoked token, another user's token and an unknown
    token still deny (``False``).
    """
    result = subprocess.run(
        [sys.executable, "-c", _CODE],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith("[True, False, False, False]"), result.stdout
