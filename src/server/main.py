from time import sleep
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from pydantic import UUID4
import asyncio
from contextlib import asynccontextmanager

from .session_controller import SessionController
from .victory_state import VictoryState


session_controller = SessionController()


task_refs = set()
@asynccontextmanager
async def test(app: FastAPI):
    task = asyncio.create_task(session_controller.tick())
    # Making a strong reference to the task by adding it to the set,
    # so it doesn't get cleaned by GC.
    task_refs.add(task)
    yield


app = FastAPI(lifespan = test)


def parse_row_col(s: str) -> int | None:
    try:
        n = int(s)
        if not (1 <= n <= 3):
            return None
        # To address 0-indexed array.
        return n - 1
    except:
        return None


@app.get("/getClientId")
async def get_client_id():
    return {"client_id": session_controller.generate_client_id()}


@app.post("/tryJoinSession")
async def try_join_session(client_id: UUID4):
    if session_controller.is_client_afk(client_id):
        session_controller.remove_afk_client(client_id)
        raise HTTPException(
            status.HTTP_408_REQUEST_TIMEOUT,
            "You have been marked as AFK"
        )

    session_id = session_controller.is_client_in_session(client_id)
    if session_id is not None:
        return { "session_id": session_id }

    session_controller.add_pending_client(client_id)
    another_pending_client_id = session_controller.find_another_pending_client_id(client_id)
    if another_pending_client_id is None:
        raise HTTPException(
            status.HTTP_406_NOT_ACCEPTABLE, 
            "No other client available for session"
        )
    
    session_id = session_controller.create_session(client_id, another_pending_client_id)
    return {"session_id": session_id}


@app.get("/session/getState")
async def get_game_state(session_id: UUID4, client_id: UUID4):
    session = session_controller.get_session(session_id)
    if session is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Such session does not exist"
        )
    
    if not session.is_client_playing(client_id):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You are not playing in this session"
        )

    state = {
        "board": session.board,
        "your_turn": session.is_client_turning(client_id),
        "victory_state": session.victory_state,
        "wins_n": session.get_wins_n(client_id),
        "losses_n": session.get_losses_n(client_id),
        "draws_n": session.draws_n
    }

    session.update_client_access_time(client_id)

    return state


async def restart_session(session_id: UUID4):
    await asyncio.sleep(10)
    session = session_controller.get_session(session_id)
    if session is not None:
        session.reset()


@app.post("/session/makeTurn")
async def make_turn(session_id: UUID4, client_id: UUID4, row_col: str, background_tasks: BackgroundTasks):
    session = session_controller.get_session(session_id)
    if session is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Such session does not exist"
        )
    
    if not session.is_client_playing(client_id):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You are not playing in this session"
        )
    
    if not session.is_client_turning(client_id):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You are not making the turn"
        )
    
    if len(row_col) != 3 or \
       row_col[1] != " " or \
       (row := parse_row_col(row_col[0])) == None or \
       (col := parse_row_col(row_col[2])) == None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Invalid format of turn"
        )
    
    if not session.can_make_turn(row, col):
        raise HTTPException(
            status.HTTP_412_PRECONDITION_FAILED,
            "Such turn is impossible"
        )
    
    session.make_turn(row, col)
    session.update_victory_state()
    session.update_stats()
    if session.victory_state != VictoryState.STILL_PLAYING:
        background_tasks.add_task(restart_session, session_id)


if __name__ == "__main__":
    print("abc")