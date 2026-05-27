# envguard

> **Type-safe env vars. One decorator, validated at startup, fails loud**

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org)
[![PyPI](https://img.shields.io/pypi/v/envguard)](https://pypi.org/project/envguard)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Install

```bash
pip install envguard
```

## The problem

Environment variables have no type safety. A missing `DATABASE_URL` doesn't fail until 3am in production. `os.environ.get("PORT")` returns a string even though you need an int.

## Usage

```python
from envguard import env, Required, Opt

@env
class Config:
    DATABASE_URL: str  = Required("Postgres connection string")
    DEBUG:        bool = Opt(False)
    PORT:         int  = Opt(8000)
    API_KEY:      str  = Required(secret=True, pattern=r"sk-[a-zA-Z0-9]+")
    ALLOWED_HOSTS:list = Opt(["localhost"])

# At import time:
# - Raises EnvError if DATABASE_URL or API_KEY is missing
# - Validates API_KEY matches the pattern
# - Converts PORT to int, DEBUG to bool, ALLOWED_HOSTS to list
# - Config.PORT is typed int, not str

print(Config.PORT)        # 8000  (int)
print(Config.DEBUG)       # False (bool)
print(Config.ALLOWED_HOSTS) # ["localhost"] (list)
```

### Fail at startup, not at 3am

```
EnvError: [envguard] Environment validation failed:
  • DATABASE_URL (str): required but not set. Postgres connection string
  • API_KEY (str): required but not set.
```

## Architecture

```
envguard/
├── envguard/
│   ├── __init__.py   # public API
│   └── *.py          # core implementation
└── tests/
    └── test_*.py     # 3 passed — no API key needed
```

## License

MIT © [bhupendra05](https://github.com/bhupendra05)

---

*Part of the [bhupendra05 developer tools collection](https://github.com/bhupendra05)*
