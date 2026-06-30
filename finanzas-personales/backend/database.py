import os
import truststore
from supabase import create_client, Client
from dotenv import load_dotenv

# Use Windows certificate store to fix SSL on corporate/Windows environments
truststore.inject_into_ssl()

load_dotenv()

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        # service_role bypasses RLS — safe for server-side use only
        key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        _client = create_client(url, key)
    return _client
