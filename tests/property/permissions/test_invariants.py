"""Property tests for the permissions check invariants (docs/specs/user-roles-permissions.md).

Hypothesis-based tests for the check-core invariants:
- INV-001: ``has_permission`` returns ``True`` if and only if the user is active and the
  permission is granted (the ``admin`` wildcard or an explicit grant, including wildcard
  matches); otherwise ``False``.
- INV-002: an undeterminable check is never ``True`` (fail-closed): ``has_permission``
  returns ``False`` and ``require_permission`` raises ``PermissionDeniedError``.
- INV-005: a user with ``admin`` in their roles passes any catalog permission, including
  permissions declared after the user's creation.

The ``backend.permissions`` imports are deferred into the test bodies so the module
collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import contextlib
import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager

_MAX_EXAMPLES = 20

# The catalog permissions and the roles exercised by the invariants.
_PERMS = ("mail.send_email", "mail.send_password_reset_email")
_ALL_ROLES = ("admin", "user", "editor")
_WILDCARD = "mail.*"

# T-005 (INV-004): the role pool and the fixed grants for the monotonicity invariant.
_MONOTONE_ROLE_POOL = ("r1", "r2", "r3")
_MONOTONE_GRANTS = {
    "r1": ("mail.send_email",),
    "r2": ("mail.*",),
    "r3": ("mail.send_password_reset_email",),
}

# T-005 (INV-006): the catalog and the grant-key space for the valid-grant-keys invariant.
_INV006_CATALOG = {
    "mail": {
        "mail.send_email": "Send an email via the shared mail service",
        "mail.send_password_reset_email": "Send the built-in password-reset email",
    },
    "usermanagement": {
        "usermanagement.get_user": "Read a user by id",
    },
}
_INV006_VALID_KEYS = frozenset(
    {
        "mail.send_email",
        "mail.send_password_reset_email",
        "usermanagement.get_user",
        "mail.*",
        "usermanagement.*",
    }
)
_INV006_INVALID_KEYS = (
    "reports.export",  # well-formed key of an unknown feature
    "mailx.*",  # wildcard of an unknown feature
    "mail",  # no dot
    "mail.",  # trailing dot
    "MAIL.*",  # uppercase
    "mail.*.*",  # extra wildcard segment
    "mail.send_email.extra",  # three segments
)
_INV006_ALL_KEYS = tuple(sorted(_INV006_VALID_KEYS)) + _INV006_INVALID_KEYS


class _SessionRecord:
    """A structural ``SessionRecord`` (the check reads ``user_id`` / ``expires_at`` / ``revoked``)."""

    def __init__(self, user_id, expires_at, revoked):
        self.user_id = user_id
        self.expires_at = expires_at
        self.revoked = revoked


class _FakeSessionLookup:
    """A structural ``SessionLookup`` keyed by the SHA-256 hash of the token."""

    def __init__(self):
        self._records = {}

    def add(self, token, record):
        self._records[hashlib.sha256(token.encode("utf-8")).hexdigest()] = record

    def get_by_token_hash(self, token_hash):
        return self._records.get(token_hash)


class _RaisingUserManager:
    """A structural UserManager whose user lookup raises (storage failure)."""

    def get_user(self, user_id):
        raise RuntimeError("storage failure")


class _RaisingSessionLookup:
    """A structural SessionLookup whose lookup raises (storage failure)."""

    def get_by_token_hash(self, token_hash):
        raise RuntimeError("storage failure")


def _grant_matches(grant: str, perm: str) -> bool:
    """Whether a grant key matches a permission (exact, or a ``<feature>.*`` wildcard)."""
    if grant == perm:
        return True
    if grant.endswith(".*"):
        return perm.startswith(grant[:-1])  # "mail.*" -> the "mail." prefix
    return False


def _build(
    service_cls,
    role_repo_cls,
    grant_repo_cls,
    system_repo_cls,
    catalog_cls,
    *,
    user_roles=None,
    username="u1",
    grants=None,
    session_lookup=None,
    user_manager=None,
    catalog=None,
):
    """Construct a ``PermissionService`` over in-memory repositories for the invariant tests.

    Returns ``(service, manager, user, grant_repo, catalog)``. ``user_roles`` of ``None``
    creates no user; ``grants`` is a mapping ``role -> [permissions]`` applied to the grant
    repository; ``user_manager`` overrides the user manager (a structural fake); ``catalog``
    overrides the catalog (a fresh one with the mail actions is created otherwise).
    """
    if catalog is None:
        catalog = catalog_cls()
        catalog.register_feature(
            "mail",
            {
                "mail.send_email": "Send an email via the shared mail service",
                "mail.send_password_reset_email": "Send the built-in password-reset email",
            },
        )
    grant_repo = grant_repo_cls()
    for role, perms in (grants or {}).items():
        for perm in perms:
            grant_repo.grant(role, perm)
    system_repo = system_repo_cls()
    manager = UserManager(SqliteUserRepository("sqlite:///:memory:")) if user_manager is None else user_manager
    user = None
    if user_roles is not None:
        user = manager.create_user(
            UserCreate(username=username, email=f"{username}@example.com", password="correct-horse-1", roles=user_roles)
        )
    service = service_cls(
        role_repo_cls(),
        grant_repo,
        system_repo,
        manager,
        session_lookup=session_lookup,
        catalog=catalog,
    )
    return service, manager, user, grant_repo, catalog


def _session_scenario_service(scenario, perm, service_cls, *, role_repo_cls, grant_repo_cls, system_repo_cls, catalog_cls):
    """Build a service with a bound session lookup for a session-validation scenario.

    Returns ``(service, user_id, token, check_perm)``. The lookup is created after the user
    exists so the session record is bound to the real user, and the service is constructed
    with the lookup (a token-based check validates against it).
    """
    now = datetime.now(UTC)
    catalog = catalog_cls()
    catalog.register_feature(
        "mail",
        {
            "mail.send_email": "Send an email via the shared mail service",
            "mail.send_password_reset_email": "Send the built-in password-reset email",
        },
    )
    role_repo = role_repo_cls()
    grant_repo = grant_repo_cls()
    grant_repo.grant("user", perm)
    system_repo = system_repo_cls()
    manager = UserManager(SqliteUserRepository("sqlite:///:memory:"))
    user = manager.create_user(
        UserCreate(username="u1", email="u1@example.com", password="correct-horse-1", roles=["user"])
    )
    lookup = _FakeSessionLookup()
    if scenario == "revoked_session":
        lookup.add("tok", _SessionRecord(user.id, now + timedelta(hours=1), True))
    elif scenario == "expired_session":
        lookup.add("tok", _SessionRecord(user.id, now - timedelta(hours=1), False))
    else:  # mismatched_session
        other = manager.create_user(
            UserCreate(username="u2", email="u2@example.com", password="correct-horse-1", roles=["user"])
        )
        lookup.add("tok", _SessionRecord(other.id, now + timedelta(hours=1), False))
    service = service_cls(role_repo, grant_repo, system_repo, manager, session_lookup=lookup, catalog=catalog)
    return service, user.id, "tok", perm


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(
    ops=st.lists(
        st.one_of(
            st.tuples(st.just("grant"), st.sampled_from(_ALL_ROLES), st.sampled_from((*_PERMS, _WILDCARD))),
            st.tuples(st.just("revoke"), st.sampled_from(_ALL_ROLES), st.sampled_from((*_PERMS, _WILDCARD))),
            st.tuples(st.just("deactivate")),
            st.tuples(st.just("activate")),
            st.tuples(st.just("add_role"), st.sampled_from(_ALL_ROLES)),
            st.tuples(st.just("remove_role"), st.sampled_from(_ALL_ROLES)),
        ),
        min_size=1,
        max_size=15,
    )
)
def test_check_true_iff_granted_and_active(ops) -> None:
    """INV-001: ``has_permission`` is ``True`` iff the user is active and the permission is
    granted (the ``admin`` wildcard or an explicit grant, including wildcard matches).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, manager, user, grant_repo, _ = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
    )
    # The test's own model of the grant state (role -> set of grant keys).
    grants: dict[str, set[str]] = {role: set() for role in _ALL_ROLES}

    for op in ops:
        kind = op[0]
        if kind == "grant":
            role, perm = op[1], op[2]
            grant_repo.grant(role, perm)
            grants[role].add(perm)
        elif kind == "revoke":
            role, perm = op[1], op[2]
            grant_repo.revoke(role, perm)
            grants[role].discard(perm)
        elif kind == "deactivate":
            manager.deactivate_user(user.id)
        elif kind == "activate":
            manager.activate_user(user.id)
        elif kind == "add_role":
            with contextlib.suppress(Exception):
                manager.add_role(user.id, op[1])
        elif kind == "remove_role":
            with contextlib.suppress(Exception):
                manager.remove_role(user.id, op[1])

        # The invariant must hold for every catalog permission after each operation.
        current = manager.get_user(user.id)
        for perm in _PERMS:
            expected = current.is_active and (
                "admin" in current.roles
                or any(_grant_matches(g, perm) for role in current.roles for g in grants[role])
            )
            assert service.has_permission(user.id, perm) is expected


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(
    scenario=st.sampled_from(
        [
            "unknown_user",
            "lookup_raises",
            "malformed_permission",
            "unknown_permission",
            "revoked_session",
            "expired_session",
            "mismatched_session",
            "lookup_none",
            "lookup_raises_session",
        ]
    )
)
def test_undeterminable_never_true(scenario) -> None:
    """INV-002: an undeterminable check is never ``True`` (fail-closed).

    For any undeterminable state (unknown user, storage error, malformed or unknown
    permission, invalid or mismatched session, unavailable dependency): ``has_permission``
    returns ``False`` and ``require_permission`` raises ``PermissionDeniedError``.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    perm = "mail.send_email"
    if scenario in ("revoked_session", "expired_session", "mismatched_session"):
        # A session-validation scenario: the service is constructed with the bound lookup.
        service, target_id, token, check_perm = _session_scenario_service(
            scenario,
            perm,
            PermissionService,
            role_repo_cls=MemoryRoleRepository,
            grant_repo_cls=MemoryGrantRepository,
            system_repo_cls=MemorySystemPrincipalRepository,
            catalog_cls=PermissionCatalog,
        )
    else:
        if scenario == "lookup_raises":
            service, _, _, _, _ = _build(
                PermissionService,
                MemoryRoleRepository,
                MemoryGrantRepository,
                MemorySystemPrincipalRepository,
                PermissionCatalog,
                user_manager=_RaisingUserManager(),
            )
        elif scenario == "lookup_raises_session":
            service, _, _, _, _ = _build(
                PermissionService,
                MemoryRoleRepository,
                MemoryGrantRepository,
                MemorySystemPrincipalRepository,
                PermissionCatalog,
                user_roles=["user"],
                grants={"user": [perm]},
                session_lookup=_RaisingSessionLookup(),
            )
        else:
            service, _, user, _, _ = _build(
                PermissionService,
                MemoryRoleRepository,
                MemoryGrantRepository,
                MemorySystemPrincipalRepository,
                PermissionCatalog,
                user_roles=["user"],
                grants={"user": [perm]},
            )
        target_id = uuid4() if scenario in ("unknown_user", "lookup_raises") else user.id
        token = "tok" if scenario in ("lookup_none", "lookup_raises_session") else None
        check_perm = {"malformed_permission": "UPPER.case", "unknown_permission": "mail.not_in_catalog"}.get(scenario, perm)

    # has_permission returns False (never True).
    assert service.has_permission(target_id, check_perm, session_token=token) is False
    # require_permission raises PermissionDeniedError.
    with contextlib.suppress(PermissionDeniedError):
        service.require_permission(target_id, check_perm, session_token=token)
        raise AssertionError("expected PermissionDeniedError")


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(n=st.integers(min_value=1, max_value=5))
def test_admin_passes_any_catalog_permission(n) -> None:
    """INV-005: a user with ``admin`` passes any catalog permission, including permissions
    declared after the user's creation.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    catalog = PermissionCatalog()
    catalog.register_feature("base", {"read": "Read"})
    service, _, user, _, _ = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["admin"],
        catalog=catalog,
    )
    # The base permission (declared before the user's creation) passes.
    assert service.has_permission(user.id, "base.read") is True
    # Register additional catalog permissions AFTER the user's creation; the admin passes them.
    for i in range(n):
        feature = f"f{i}"
        catalog.register_feature(feature, {"act": "desc"})
        assert service.has_permission(user.id, f"{feature}.act") is True


# --- INV-004: the effective permission set is monotone in the role set ---


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(
    roles_a=st.frozensets(st.sampled_from(_MONOTONE_ROLE_POOL), min_size=1),
    roles_b=st.frozensets(st.sampled_from(_MONOTONE_ROLE_POOL), min_size=1),
)
def test_effective_set_monotone(roles_a, roles_b) -> None:
    """INV-004: the effective permission set is monotone in the role set.

    For any role sets R ⊆ R', effective(R) ⊆ effective(R').
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    from backend.usermanagement import StaticRoleStore

    # R = roles_a and R' = roles_a | roles_b, so R ⊆ R' holds by construction.
    r = roles_a
    r_prime = roles_a | roles_b

    catalog = PermissionCatalog()
    catalog.register_feature(
        "mail",
        {
            "mail.send_email": "Send an email via the shared mail service",
            "mail.send_password_reset_email": "Send the built-in password-reset email",
        },
    )
    grant_repo = MemoryGrantRepository()
    for role, perms in _MONOTONE_GRANTS.items():
        for perm in perms:
            grant_repo.grant(role, perm)

    manager = UserManager(
        SqliteUserRepository("sqlite:///:memory:"),
        role_store=StaticRoleStore(("admin", "user", *_MONOTONE_ROLE_POOL)),
    )
    user_r = manager.create_user(
        UserCreate(username="ur", email="ur@example.com", password="correct-horse-1", roles=sorted(r))
    )
    user_r_prime = manager.create_user(
        UserCreate(username="urp", email="urp@example.com", password="correct-horse-1", roles=sorted(r_prime))
    )
    service = PermissionService(
        MemoryRoleRepository(), grant_repo, MemorySystemPrincipalRepository(), manager, catalog=catalog
    )

    def effective(user_id):
        return {perm for perm in _PERMS if service.has_permission(user_id, perm)}

    # Monotonicity: R ⊆ R' implies effective(R) ⊆ effective(R').
    assert effective(user_r.id) <= effective(user_r_prime.id)


# --- INV-006: the valid grant keys are exactly the catalog actions union feature wildcards ---


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(key=st.sampled_from(_INV006_ALL_KEYS))
def test_valid_grant_keys_exactly_catalog_plus_wildcards(key) -> None:
    """INV-006: the set of valid grant keys is exactly the catalog actions union the feature
    wildcards; a grant of any other key raises.
    """
    from backend.permissions import (
        AuthorizationError,
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    catalog = PermissionCatalog()
    for feature, actions in _INV006_CATALOG.items():
        catalog.register_feature(feature, actions)
    role_repo = MemoryRoleRepository()
    role_repo.add("user", None, True)
    grant_repo = MemoryGrantRepository()
    service = PermissionService(
        role_repo,
        grant_repo,
        MemorySystemPrincipalRepository(),
        _RaisingUserManager(),  # no user lookup is exercised by this invariant
        catalog=catalog,
    )

    if key in _INV006_VALID_KEYS:
        # A catalog action or a feature wildcard is accepted and stored.
        service.grant_permission("user", key)
        assert key in service.get_role_permissions("user")
    else:
        # Any other key raises and is not stored.
        try:
            service.grant_permission("user", key)
            raise AssertionError(f"expected a grant of {key!r} to raise")
        except (AuthorizationError, ValueError):
            pass
        assert key not in service.get_role_permissions("user")
