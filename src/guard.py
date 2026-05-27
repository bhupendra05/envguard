"""Core env validation logic."""
from __future__ import annotations
import os, re
from dataclasses import dataclass
from typing import Any, Callable, Type, TypeVar, get_type_hints

T = TypeVar("T")

class EnvError(Exception):
    """Raised when env validation fails at startup."""

@dataclass
class _Field:
    type_: type
    default: Any
    description: str
    pattern: str | None
    secret: bool

_MISSING = object()

def Required(description: str = "", pattern: str | None = None, secret: bool = False) -> Any:
    return _Field(type_=str, default=_MISSING, description=description, pattern=pattern, secret=secret)

def Optional(default: Any = None, description: str = "", pattern: str | None = None, secret: bool = False) -> Any:
    return _Field(type_=type(default) if default is not None else str, default=default, description=description, pattern=pattern, secret=secret)

_CONVERTERS: dict[type, Callable] = {
    str:   str,
    int:   int,
    float: float,
    bool:  lambda v: v.lower() in ("1", "true", "yes", "on"),
    list:  lambda v: [x.strip() for x in v.split(",")],
}

class _EnvMeta(type):
    def __new__(mcs, name, bases, ns):
        cls = super().__new__(mcs, name, bases, ns)
        if name == "_EnvBase":
            return cls
        errors = []
        for attr, field in list(ns.items()):
            if not isinstance(field, _Field):
                continue
            raw = os.environ.get(attr)
            if raw is None:
                if field.default is _MISSING:
                    errors.append(f"  • {attr}: required but not set. {field.description}")
                    continue
                else:
                    setattr(cls, attr, field.default)
                    continue
            # Type conversion
            converter = _CONVERTERS.get(field.type_, str)
            try:
                value = converter(raw)
            except (ValueError, TypeError) as e:
                errors.append(f"  • {attr}={raw!r}: cannot convert to {field.type_.__name__}: {e}")
                continue
            # Pattern check
            if field.pattern and not re.fullmatch(field.pattern, raw):
                errors.append(f"  • {attr}={raw!r}: does not match pattern {field.pattern!r}")
                continue
            setattr(cls, attr, value)

        if errors:
            raise EnvError(f"[envguard] Environment validation failed:\n" + "\n".join(errors))
        return cls

class _EnvBase(metaclass=_EnvMeta):
    pass

def env(cls: type) -> type:
    """
    Decorator that validates and type-converts environment variables at import time.

    ::

        from envguard import env, Required, Opt

        @env
        class Config:
            DATABASE_URL: str = Required("Postgres connection string")
            DEBUG:        bool = Opt(False)
            PORT:         int  = Opt(8000)
            API_KEY:      str  = Required(secret=True, pattern=r"sk-[a-zA-Z0-9]+")

        # Raises EnvError at startup if DATABASE_URL is missing
        # Otherwise: Config.DATABASE_URL, Config.PORT, Config.DEBUG are typed + validated
    """
    errors = []
    annotations = {}
    for klass in reversed(cls.__mro__):
        annotations.update(getattr(klass, "__annotations__", {}))

    for attr, type_ in annotations.items():
        field = getattr(cls, attr, None)
        if not isinstance(field, _Field):
            continue
        field.type_ = type_
        raw = os.environ.get(attr)
        if raw is None:
            if field.default is _MISSING:
                errors.append(f"  • {attr} ({type_.__name__}): required but not set. {field.description}")
                continue
            setattr(cls, attr, field.default)
            continue
        converter = _CONVERTERS.get(type_, str)
        try:
            value = converter(raw)
        except (ValueError, TypeError) as e:
            errors.append(f"  • {attr}={raw!r}: cannot convert to {type_.__name__}: {e}")
            continue
        if field.pattern and not re.fullmatch(field.pattern, raw):
            errors.append(f"  • {attr}={raw!r}: does not match pattern {field.pattern!r}")
            continue
        setattr(cls, attr, value)

    if errors:
        raise EnvError("[envguard] Environment validation failed:\n" + "\n".join(errors))
    return cls
