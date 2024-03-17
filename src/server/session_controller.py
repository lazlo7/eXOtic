import uuid
from random import choice
import logging
import asyncio
from time import time

from .session import Session
from .client import Client


class SessionController:
    # Clients will be timed out after 30 seconds.
    CLIENT_TIMEOUT = 30
    # 1 tick per second for tick() function.
    TPS = 1

    __sessions: dict[uuid.UUID, Session] = {}
    __pendingClients: dict[uuid.UUID, Client] = {}
    __afkClientIds: set[uuid.UUID] = set()
    

    def create_session(self, client1_id: uuid.UUID, client2_id: uuid.UUID) -> uuid.UUID | None:
        # Remove clients from pending state, checking that they exist by passing None as default.
        client1 = self.__pendingClients.pop(client1_id, None)
        if client1 == None:
            return None
        client2 = self.__pendingClients.pop(client2_id, None)
        if client2 == None:
            return None

        session = Session(client1, client1_id, client2, client2_id)
        session_id = uuid.uuid4()

        self.__sessions[session_id] = session
        return session_id
    

    def get_session(self, session_id: uuid.UUID) -> Session | None:
        return self.__sessions.get(session_id, None)


    def is_client_in_session(self, client_id: uuid.UUID) -> uuid.UUID | None:
        for session_id, session in self.__sessions.items():
            for client_in_session_id, _ in session.clients:
                if client_in_session_id == client_id:
                    return session_id
        return None


    def add_pending_client(self, client_id: uuid.UUID):
        # Client is already pending, return.
        if client_id in self.__pendingClients.keys():
            return
        client = Client()
        self.__pendingClients[client_id] = client
    

    def find_another_pending_client_id(self, client_id: uuid.UUID) -> uuid.UUID | None:
        if client_id not in self.__pendingClients.keys():
            logging.warn(f"find_another_pending_client_id: given client_id ({client_id}) is not pending")
            return None
        
        other_clients_ids = list(self.__pendingClients.keys())
        other_clients_ids.remove(client_id)
        if len(other_clients_ids) == 0:
            return None
        
        return choice(other_clients_ids)


    def generate_client_id(self) -> uuid.UUID:
        return uuid.uuid4()

    
    def is_client_afk(self, client_id: uuid.UUID):
        return client_id in self.__afkClientIds
    

    def remove_afk_client(self, client_id: uuid.UUID):
        return self.__afkClientIds.remove(client_id)


    async def tick(self):
        while True:
            # Close sessions with clients who have been offline for more than CLIENT_TIMEOUT.
            current_time = time()
            sessions_ids_to_close = []
            for session_id, session in self.__sessions.items():
                for client_id, client in session.clients:
                    if client.last_access_time < current_time - SessionController.CLIENT_TIMEOUT:
                        print("Found afk client")
                        sessions_ids_to_close.append(session_id)
                        self.__afkClientIds.add(client_id)
            for session_id in sessions_ids_to_close:
                self.__sessions.pop(session_id)

            await asyncio.sleep(1 / SessionController.TPS)