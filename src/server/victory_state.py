from enum import Enum


class VictoryState(Enum):
    STILL_PLAYING = 0
    DRAW = 1
    X_VICTORY = 2
    O_VICTORY = 3