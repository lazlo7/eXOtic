import sys
import os
from uuid import UUID
import requests
from time import sleep
from session import Session
from typing import Any


def request_client_id(server_address: str) -> UUID | None:
    r = requests.get(f"{server_address}/getClientId")
    if r.status_code != 200:
        return None
    client_id_str = r.json()["client_id"]
    return UUID(client_id_str)


def try_join_session(server_address: str, client_id: UUID) -> UUID | None:
    r = requests.post(
        f"{server_address}/tryJoinSession", 
        params = {"client_id": str(client_id)}
    )
    if r.status_code != 200:
        return None
    session_id_str = r.json()["session_id"]
    return UUID(session_id_str)


def get_game_state(session: Session) -> dict[str, Any] | None:
    r = requests.get(
        f"{session.server_address}/session/getState",
        params = {
            "session_id": str(session.id_),
            "client_id": str(session.client_id)
        }
    )
    if r.status_code != 200:
        return None
    return r.json()


def make_turn(session: Session, row_col: str) -> bool:
    r = requests.post(
        f"{session.server_address}/session/makeTurn",
        params = {
            "session_id": str(session.id_),
            "client_id": str(session.client_id),
            "row_col": row_col
        }
    )
    return r.status_code == 200


def clear_screen():
    # Maybe not the best way to clear the screen, 
    # but works well enough across all platforms.
    os.system('cls' if os.name == 'nt' else 'clear')


def pad_left():
    print(" " * 2, end="")

def print_board(board: list[list[int]]):
    cell_types = { 0: " ", 1: "X", 2: "O" }

    # 2-line top padding.
    print("\n" * 2, end="")
    pad_left()
    print("    Board")

    pad_left()
    # Print cell ceilings.
    print(" ___" * 3)

    for row in range(3):        
        pad_left()
        print("|   " * 3 + "|")
        
        pad_left()
        for col in range(3):
            symbol = cell_types[board[row][col]]
            print(f"| {symbol} ", end="")
        # Close right wall of right-most cell
        print("|")

        pad_left()
        print("|___" * 3 + "|")
    
    # 2-line bottom padding.       
    print("\n" * 2, end="")


def session_loop(session: Session):
    prev_your_turn = None
    turn_successful = True

    while True:
        # Fetch information about game state.
        game_state = get_game_state(session)
        if game_state is None:
            print("Failed to get game state from the server, retrying...")
            sleep(1)
            continue

        your_turn = game_state["your_turn"]
        if prev_your_turn is not None and turn_successful and your_turn == prev_your_turn:
            sleep(1)
            continue
        prev_your_turn = your_turn

        clear_screen()        
        board = game_state["board"]
        print_board(board)
        
        victory_state = game_state["victory_state"]
        if victory_state != 0:
            match victory_state:
                case 1:
                    print("Draw! Game will restart in 10s...")
                case 2:
                    print("X Victory! Game will restart in 10s...")
                case 3:
                    print("O Victory! Game will restart in 10s...")
            sleep(10)
            continue

        if your_turn:
            if not turn_successful:
                pad_left()
                print("Invalid turn, try again")

            pad_left()
            print("Your turn (i.e. '1 1' for top-left cell, '2 1' for mid-left, '3 3' for bottom-right):")
            
            pad_left()
            row_col = input()
            # It would make more sense to at least validate some of the input here, 
            # but the task disallows it.
            turn_successful = make_turn(session, row_col)
        else:
            pad_left()
            print("Waiting for opponent's turn...")


def main(server_address: str):
    print("Initializing...")

    while (client_id := request_client_id(server_address)) == None:
        print("Couldn't request a client id from server, retrying in 10s...")
        sleep(10)
    
    while True:
        cycle_index = 0
        while (session_id := try_join_session(server_address, client_id)) == None:
            cycle = "-\\|/"
            cycle_index = (cycle_index + 1) % len(cycle)
            print(f"Waiting for available players [{cycle[cycle_index]}]", end="\r")
            sleep(1)

        print(f"Found game, connecting...")
        session = Session(session_id, client_id, server_address)
        clear_screen()
        session_loop(session)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <server_address>")
        print(f"Example: python {sys.argv[0]} http://127.0.0.1:8000/")
        exit(-1)
    
    server_address = sys.argv[1]
    main(server_address)