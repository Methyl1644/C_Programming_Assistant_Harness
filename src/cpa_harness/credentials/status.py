"""Status display — never prints the full key."""
from cpa_harness.credentials.storage import get_api_key, mask_key


def print_status() -> None:
    key = get_api_key()
    if key:
        print(f"API key: {mask_key(key)} (source: configured)")
    else:
        print("API key: not configured. Run `cpa-harness setup`.")
