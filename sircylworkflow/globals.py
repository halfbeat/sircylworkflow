from __future__ import annotations

import typing as t
from contextvars import ContextVar

from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:  # pragma: no cover
    from .di.infra.security import MyUsuario

_current_user_context_var: ContextVar[MyUsuario] = ContextVar('current_user')
current_user: MyUsuario = LocalProxy(  # type: ignore[assignment]
    _current_user_context_var, unbound_message="No existe un usuario en este contexto"
)