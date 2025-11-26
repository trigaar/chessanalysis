"""PGN parsing and move classification logic."""
from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import chess
import chess.pgn

from engine_interface import evaluate_position

# Thresholds (centipawns) for classifying moves based on evaluation loss.
BEST_THRESHOLD = 20
GOOD_THRESHOLD = 50
INACCURACY_THRESHOLD = 100
MISTAKE_THRESHOLD = 250
BLUNDER_THRESHOLD = 250

OPENING_MAX_PLIES = 20


@dataclass
class MoveAnalysis:
    move_number: int
    san: str
    color: str
    evaluation: int
    best_move: Optional[str]
    loss: int
    label: str


@dataclass
class PlayerSummary:
    name: str
    accuracy: float
    move_counts: Dict[str, int]


@dataclass
class AnalysisResult:
    white: PlayerSummary
    black: PlayerSummary
    evaluations: List[int]
    moves: List[MoveAnalysis] = field(default_factory=list)


def classify_move(loss: int, board: chess.Board, move: chess.Move, prev_eval: int, post_eval: int) -> str:
    """Assign a label to the move based on evaluation loss and simple heuristics."""
    # Opening book heuristic
    if len(board.move_stack) <= OPENING_MAX_PLIES:
        return "Book"

    # Detect missed win when throwing away a large advantage.
    if prev_eval > 200 and post_eval < -50:
        return "Miss"

    if loss <= BEST_THRESHOLD:
        # Simple brilliance heuristic: positive or equal trade that maintains eval.
        if board.is_capture(move) or board.gives_check(move):
            moving_piece = board.piece_at(move.from_square)
            captured_piece = board.piece_at(move.to_square)
            if captured_piece and moving_piece:
                if piece_value(captured_piece.piece_type) - piece_value(moving_piece.piece_type) >= 2:
                    return "Brilliant"
            return "Great"
        return "Best"
    if loss <= GOOD_THRESHOLD:
        return "Excellent" if loss <= 2 * BEST_THRESHOLD else "Good"
    if loss <= INACCURACY_THRESHOLD:
        return "Inaccuracy"
    if loss <= MISTAKE_THRESHOLD:
        return "Mistake"
    if loss > BLUNDER_THRESHOLD:
        return "Blunder"
    return "Mistake"


def piece_value(piece_type: int) -> int:
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0,
    }
    return values.get(piece_type, 0)


def calculate_accuracy(losses: List[int]) -> float:
    if not losses:
        return 100.0
    avg_loss = sum(losses) / len(losses)
    accuracy = max(0.0, 100 - (avg_loss / 3))
    return round(accuracy, 2)


def analyze_game(pgn_text: str, seed: Optional[int] = None) -> AnalysisResult:
    """Analyse a PGN game and return summaries and move details."""
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("Invalid PGN provided")

    board = game.board()
    evaluations: List[int] = []
    move_analyses: List[MoveAnalysis] = []
    white_losses: List[int] = []
    black_losses: List[int] = []

    for move_number, move in enumerate(game.mainline_moves(), start=1):
        prev_eval_data = evaluate_position(board, seed=seed)
        prev_eval = prev_eval_data["score"]
        prev_eval_white = prev_eval if board.turn == chess.WHITE else -prev_eval

        board.push(move)
        post_eval_data = evaluate_position(board, seed=seed + move_number if seed is not None else None)
        post_eval = post_eval_data["score"]

        mover_color = "White" if board.turn == chess.BLACK else "Black"
        # Convert evaluation after the move to mover's perspective (opposite of side to move now)
        post_eval_from_mover = -post_eval

        best_eval = prev_eval_data["score"]
        loss = max(0, best_eval - post_eval_from_mover)

        label = classify_move(loss, board, move, prev_eval, post_eval_from_mover)

        evaluations.append(prev_eval_white)

        move_analysis = MoveAnalysis(
            move_number=move_number,
            san=board.san(board.peek()),
            color=mover_color,
            evaluation=post_eval_from_mover,
            best_move=prev_eval_data["best_move"],
            loss=loss,
            label=label,
        )
        move_analyses.append(move_analysis)

        if mover_color == "White":
            white_losses.append(loss)
        else:
            black_losses.append(loss)

    white_summary = PlayerSummary(
        name=game.headers.get("White", "White"),
        accuracy=calculate_accuracy(white_losses),
        move_counts=count_labels(move_analyses, "White"),
    )
    black_summary = PlayerSummary(
        name=game.headers.get("Black", "Black"),
        accuracy=calculate_accuracy(black_losses),
        move_counts=count_labels(move_analyses, "Black"),
    )

    return AnalysisResult(
        white=white_summary,
        black=black_summary,
        evaluations=evaluations,
        moves=move_analyses,
    )


def count_labels(moves: List[MoveAnalysis], color: str) -> Dict[str, int]:
    labels = [
        "Brilliant",
        "Great",
        "Best",
        "Excellent",
        "Good",
        "Book",
        "Inaccuracy",
        "Mistake",
        "Miss",
        "Blunder",
    ]
    counts = {label: 0 for label in labels}
    for m in moves:
        if m.color == color:
            counts[m.label] = counts.get(m.label, 0) + 1
    return counts


__all__ = [
    "analyze_game",
    "AnalysisResult",
    "PlayerSummary",
    "MoveAnalysis",
]
