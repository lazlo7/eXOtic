from uuid import UUID
from time import time

from .victory_state import VictoryState
from .client import Client
from .cell_state import CellState


class Session:
    def __init__(self, x_client: Client, x_client_id: UUID, o_client: Client, o_client_id: UUID):
        self.__clients = [
            (x_client_id, x_client), 
            (o_client_id, o_client)
        ]
        self.__board = [[ CellState.EMPTY for _ in range(3) ] for _ in range(3) ]
        self.__turning_client_idx = 0 
        self.__victory_state = VictoryState.STILL_PLAYING
        
        self.__x_client_victories_n = 0
        self.__draws_n = 0
        self.__games_played_n = 0


    @property
    def clients(self) -> list[tuple[UUID, Client]]:
        return self.__clients


    @property
    def board(self) -> list[list[CellState]]:
        return self.__board

    
    @property
    def victory_state(self) -> VictoryState:
        return self.__victory_state


    @property
    def draws_n(self) -> int:
        return self.__draws_n


    def is_client_playing(self, client_id: UUID) -> bool:
        for playing_client_id, _ in self.__clients:
            if playing_client_id == client_id:
                return True
        return False


    def is_client_turning(self, client_id: UUID) -> bool:
        return self.__clients[self.__turning_client_idx][0] == client_id
    

    def can_make_turn(self, row: int, col: int) -> bool:
        return self.__board[row][col] == CellState.EMPTY


    def get_wins_n(self, client_id: UUID) -> int:
        # X client.
        if client_id == self.__clients[0][0]:
            return self.__x_client_victories_n
        # O client.
        return self.__games_played_n - (self.__x_client_victories_n + self.__draws_n)


    def get_losses_n(self, client_id: UUID) -> int:
        # X client.
        if client_id == self.__clients[0][0]:
            return self.get_wins_n(self.__clients[1][0])
        return self.get_wins_n(self.__clients[0][0])


    def update_victory_state(self):
        # Check horizontal.
        for row in range(3):
            sum = 0
            for col in range(3):
                if self.__board[row][col] == CellState.X:
                    sum += 1
                elif self.__board[row][col] == CellState.O:
                    sum -= 1
            if sum == 3:
                self.__victory_state = VictoryState.X_VICTORY
                return
            if sum == -3:
                self.__victory_state = VictoryState.O_VICTORY
                return
        
        # Check vertical.
        for col in range(3):
            sum = 0
            for row in range(3):
                if self.__board[row][col] == CellState.X:
                    sum += 1
                elif self.__board[row][col] == CellState.O:
                    sum -= 1
            if sum == 3:
                self.__victory_state = VictoryState.X_VICTORY
                return
            if sum == -3:
                self.__victory_state = VictoryState.O_VICTORY
                return

        # Check main diagonal.
        sum = 0
        for offset in range(3):
            if self.__board[offset][offset] == CellState.X:
                sum += 1
            elif self.__board[offset][offset] == CellState.O:
                sum -= 1
        if sum == 3:
            self.__victory_state = VictoryState.X_VICTORY
            return
        if sum == -3:
            self.__victory_state = VictoryState.O_VICTORY
            return
        
        # Check other diagonal.
        sum = 0
        for offset in range(3):
            if self.__board[offset][2 - offset] == CellState.X:
                sum += 1
            elif self.__board[offset][2 - offset] == CellState.O:
                sum -= 1
        if sum == 3:
            self.__victory_state = VictoryState.X_VICTORY
            return
        if sum == -3:
            self.__victory_state = VictoryState.O_VICTORY
            return

        # Clients should continue playing if there are any empty cells left.
        for row in range(3):
            for col in range(3):
                if self.__board[row][col] == CellState.EMPTY:
                    self.__victory_state = VictoryState.STILL_PLAYING
                    return

        # Otherwise, a draw has occured.
        self.__victory_state = VictoryState.DRAW


    def update_stats(self):
        match self.__victory_state:
            case VictoryState.STILL_PLAYING:
                return
            case VictoryState.X_VICTORY:
                self.__x_client_victories_n += 1
            case VictoryState.DRAW:
                self.__draws_n += 1
        self.__games_played_n += 1

    def make_turn(self, row: int, col: int):
        self.__board[row][col] = CellState.X if self.__turning_client_idx == 0 else CellState.O 
        self.__turning_client_idx = (self.__turning_client_idx + 1) % 2


    def update_client_access_time(self, client_id: UUID):
        for playing_client_id, client in self.__clients:
            if playing_client_id == client_id:
                client.last_access_time = time()
                break

    
    def reset(self):
        self.__board = [[ CellState.EMPTY for _ in range(3) ] for _ in range(3) ]
        self.__turning_client_idx = 0 
        self.__victory_state = VictoryState.STILL_PLAYING
