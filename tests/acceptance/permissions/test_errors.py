"""Acceptance tests for the permissions feature's error hierarchy (docs/specs/user-roles-permissions.md).

Covers AC-026 (REQ-021): the structured exception hierarchy in
``backend.permissions.errors`` rooted at ``AuthorizationError`` — a caught
``PermissionDeniedError`` carries the context ``user_id``, ``permission``,
``reason``; a caught role error carries the context ``role``. The hierarchy
does not collide with the built-in ``PermissionError``.
"""

from __future__ import annotations

from uuid import uuid4


def test_error_context_attributes() -> None:
    """AC-026 / REQ-021: error context attributes are present when caught.

    Given a ``PermissionDeniedError``, when it is caught, then the context
    ``user_id``, ``permission``, ``reason`` is present. Given a role error,
    when it is caught, then the context ``role`` is present. The hierarchy is
    rooted at ``AuthorizationError`` (no collision with the built-in
    ``PermissionError``).
    """
    from backend.permissions.errors import (
        AuthorizationError,
        PermissionDeniedError,
        RoleAlreadyExistsError,
        RoleInUseError,
        RoleNotFoundError,
        RoleProtectedError,
        UnknownPermissionError,
    )

    user_id = uuid4()
    permission = "usermanagement.delete_user"
    reason = "unauthorized"
    role = "editor"

    # --- PermissionDeniedError carries the denial context (REQ-021). ---
    try:
        raise PermissionDeniedError(user_id=user_id, permission=permission, reason=reason)
    except PermissionDeniedError as exc:
        assert exc.user_id == user_id
        assert exc.permission == permission
        assert exc.reason == reason

    # The system principal denies with user_id=None (D1).
    try:
        raise PermissionDeniedError(user_id=None, permission=permission, reason="unknown_user")
    except PermissionDeniedError as exc:
        assert exc.user_id is None
        assert exc.reason == "unknown_user"

    # --- Role errors carry the role context (AC-026). ---
    for role_error in (
        RoleNotFoundError,
        RoleAlreadyExistsError,
        RoleInUseError,
        RoleProtectedError,
    ):
        try:
            raise role_error(role=role)
        except role_error as exc:
            assert exc.role == role

    # --- UnknownPermissionError carries the permission context (D18). ---
    try:
        raise UnknownPermissionError(permission=permission)
    except UnknownPermissionError as exc:
        assert exc.permission == permission

    # --- The hierarchy is rooted at AuthorizationError (REQ-021): raising
    #     any error in the hierarchy is caught by the root. ---
    for error_cls in (
        PermissionDeniedError,
        RoleNotFoundError,
        RoleAlreadyExistsError,
        RoleInUseError,
        RoleProtectedError,
        UnknownPermissionError,
    ):
        if error_cls is PermissionDeniedError:
            instance = PermissionDeniedError(user_id=None, permission=permission, reason=reason)
        elif error_cls is UnknownPermissionError:
            instance = UnknownPermissionError(permission=permission)
        else:
            instance = error_cls(role=role)
        try:
            raise instance
        except AuthorizationError as exc:
            assert isinstance(exc, error_cls)

    # --- No collision with the built-in PermissionError (REQ-021): the root
    #     is a distinct class and not a subclass of the built-in, so
    #     ``except PermissionError`` never catches this hierarchy. ---
    assert AuthorizationError is not PermissionError
    assert not issubclass(AuthorizationError, PermissionError)
