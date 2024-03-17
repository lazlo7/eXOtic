from uuid import UUID

from .victory_state import VictoryState
from .client import Client
from .cell_state import CellState


class Session:
    __clients: list[tuple[UUID, Client]]
    __board: list[list[CellState]]
    __turning_client_idx: int
    __victory_state: VictoryState


    def __init__(self, x_client: Client, x_client_id: UUID, o_client: Client, o_client_id: UUID):
        self.__clients = [
            (x_client_id, x_client), 
            (o_client_id, o_client)
        ]
        self.__board = [[ CellState.EMPTY for _ in range(3) ] for _ in range(3) ]
        self.__turning_client_idx = 0 
        self.__victory_state = VictoryState.STILL_PLAYING


    @property
    def clients(self) -> list[tuple[UUID, Client]]:
        return self.__clients


    @property
    def board(self) -> list[list[CellState]]:
        return self.__board

    
    @property
    def victory_state(self) -> VictoryState:
        return self.__victory_state


    def is_client_playing(self, client_id: UUID) -> bool:
        for playing_client_id, _ in self.__clients:
            if playing_client_id == client_id:
                return True
        return False


    def is_client_turning(self, client_id: UUID) -> bool:
        return self.__clients[self.__turning_client_idx][0] == client_id
    

    def can_make_turn(self, row: int, col: int):
        return self.__board[row][col] == CellState.EMPTY


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


    def make_turn(self, row: int, col: int):
        self.__board[row][col] = CellState.X if self.__turning_client_idx == 0 else CellState.O 
        self.__turning_client_idx = (self.__turning_client_idx + 1) % 2

    
    def reset(self):
        self.__board = [[ CellState.EMPTY for _ in range(3) ] for _ in range(3) ]
        self.__turning_client_idx = 0 
        self.__victory_state = VictoryState.STILL_PLAYING
