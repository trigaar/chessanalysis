"""Engine interface module.

Currently provides a mocked evaluation function that returns a pseudo-random
centipawn score and a placeholder best move. This keeps the project runnable
without a bundled engine; swap the implementation with a call to Stockfish or
Lichess cloud eval later.
"""

from __future__ import annotations

import random
from typing import Dict, Optional

import chess


def evaluate_position(board: chess.Board, seed: Optional[int] = None) -> Dict[str, object]:
    """Return a mocked evaluation of the position.

    Args:
        board: Current board state.
        seed: Optional seed to make evaluations deterministic for testing.

    Returns:
        dict with keys:
            - score: centipawn score from the perspective of the side to move.
            - best_move: SAN string of a plausible best move candidate.
    """

    rng = random.Random(seed)
    # Keep scores in a realistic range for casual games.
    score = rng.randint(-300, 300)

    legal_moves = list(board.legal_moves)
    if legal_moves:
        candidate_move = rng.choice(legal_moves)
        best_move_san = board.san(candidate_move)
    else:
        best_move_san = None

    return {"score": score, "best_move": best_move_san}


__all__ = ["evaluate_position"]
