from __future__ import annotations
import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: Optional[AsyncIOMotorClient] = None
_client_uri: Optional[str] = None  # Track which URI the client was created with


def get_client() -> Optional[AsyncIOMotorClient]:
    global _client, _client_uri

    uri = os.getenv("MONGODB_URI")

    print("MONGODB_URI =", uri)   

    if not uri:
        return None
    # Re-create client if URI changed (e.g. .env was updated)
    if _client is not None and _client_uri == uri:
        return _client
    if _client is not None:
        _client.close()
    _client = AsyncIOMotorClient(
        uri,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000,   # fail fast after 5s
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
    )
    _client_uri = uri
    return _client


def get_db(db_name: str = "gplan") -> Optional[AsyncIOMotorDatabase]:
    client = get_client()
    if client is None:
        return None
    return client[db_name]

