"""Convert raw evaluation data into a human-readable summary.

The goal is to mimic a lightweight version of chess.com game review wording.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PositionSummary:
    advantage: str
    side_to_move: str
    evaluation_cp: Optional[int]
    mate_in: Optional[int]
    best_line: str
    notes: str


def _advantage_label(cp: Optional[int], mate: Optional[int]) -> str:
    if mate is not None:
        if mate > 0:
            return "White is delivering mate"
        if mate < 0:
            return "Black is delivering mate"
        return "Forced draw"
    if cp is None:
        return "Evaluation unavailable"
    if abs(cp) < 20:
        return "Equal"
    if 20 <= cp < 80:
        return "White slightly better" if cp > 0 else "Black slightly better"
    if 80 <= cp < 200:
        return "White better" if cp > 0 else "Black better"
    return "White winning" if cp > 0 else "Black winning"


def _notes(cp: Optional[int]) -> str:
    if cp is None:
        return "No eval; showing placeholder"
    if abs(cp) > 300:
        return "Big swing detected; review tactics"
    if abs(cp) < 15:
        return "Balanced position; play solid moves"
    return "Look for improving moves and king safety"


def summarize_position(cp: Optional[int], mate: Optional[int], pv: str, side_to_move: str) -> PositionSummary:
    advantage = _advantage_label(cp, mate)
    notes = _notes(cp)
    return PositionSummary(
        advantage=advantage,
        side_to_move="White" if side_to_move == "w" else "Black",
        evaluation_cp=cp,
        mate_in=mate,
        best_line=pv,
        notes=notes,
    )


__all__ = ["summarize_position", "PositionSummary"]
