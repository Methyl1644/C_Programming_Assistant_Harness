"""Credential storage with keyring primary + file fallback."""
import json
import os
from pathlib import Path

_KEYRING_SERVICE = "cpa-harness"
_KEYRING_USER = "OPENAI_API_KEY"


def mask_key(key: str | None) -> str:
    if not key:
        return "(empty)"
    if len(key) < 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def _keyring_path() -> Path:
    p = os.environ.get("CPAH_KEYRING_PATH", ".keyring.json")
    return Path(p).expanduser().resolve()


def _use_keyring_lib() -> bool:
    """Return True if the system keyring is available."""
    if os.environ.get("CPAH_TEST_KEYRING_BACKEND") == "file":
        return False
    try:
        import keyring
        kr = keyring.get_keyring()
        return kr.__class__.__name__ != "Fail"
    except Exception:
        return False


def get_api_key() -> str | None:
    if _use_keyring_lib():
        try:
            import keyring
            v = keyring.get_password(_KEYRING_SERVICE, _KEYRING_USER)
            if v:
                return v
        except Exception:
            pass
    path = _keyring_path()
    if path.exists():
        data = json.loads(path.read_text())
        return data.get("OPENAI_API_KEY")
    return os.environ.get("OPENAI_API_KEY")


def store_api_key(key: str) -> None:
    if _use_keyring_lib():
        try:
            import keyring
            keyring.set_password(_KEYRING_SERVICE, _KEYRING_USER, key)
            return
        except Exception:
            pass
    path = _keyring_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"OPENAI_API_KEY": key}))


def clear_api_key() -> None:
    if _use_keyring_lib():
        try:
            import keyring
            keyring.delete_password(_KEYRING_SERVICE, _KEYRING_USER)
        except Exception:
            pass
    path = _keyring_path()
    if path.exists():
        path.unlink()
