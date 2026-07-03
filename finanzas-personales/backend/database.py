import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Windows-only: fix SSL certificate verification with corporate/system CA store
if sys.platform == "win32":
    import truststore
    truststore.inject_into_ssl()

load_dotenv()

_url: str | None = None
_key: str | None = None


def get_client() -> Client:
    global _url, _key
    if _url is None:
        _url = os.environ["SUPABASE_URL"]
        # service_role bypasses RLS — safe for server-side use only
        _key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(_url, _key)
