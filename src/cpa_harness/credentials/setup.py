"""Interactive setup: prompt for API key, store in keyring."""
import getpass
from cpa_harness.credentials.storage import store_api_key, mask_key


def run_setup() -> None:
    print("CP-AH: First-time setup")
    print("Your API key will be stored in the system keyring.")
    key = getpass.getpass("Enter your OpenAI-compatible API key: ")
    if not key.strip():
        print("Empty key, aborting.")
        return
    store_api_key(key.strip())
    print(f"Stored. Masked: {mask_key(key)}")
