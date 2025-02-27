import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import AsyncGenerator

load_dotenv()

# Supabase connection
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

async def get_supabase_client() -> AsyncGenerator[Client, None]:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    yield supabase