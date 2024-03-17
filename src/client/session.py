from uuid import UUID
from dataclasses import dataclass


@dataclass
class Session:
    """Helper class to store information about current session"""
    id_: UUID
    client_id: UUID
    server_address: str
