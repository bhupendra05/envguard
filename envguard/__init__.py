"""envguard — Type-safe environment variables. One decorator, validated at startup."""
from .guard import env, EnvError, Required, Optional as Opt
__version__ = "0.1.0"
__all__ = ["env", "EnvError", "Required", "Opt"]
