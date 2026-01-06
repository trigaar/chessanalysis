"""Lightweight client for fetching evaluations from Lichess Cloud Eval.

The real endpoint is public and does not require an API token, but network
errors or rate limits can occur. To keep the desktop app usable offline, this
module provides a mock fallback that returns a canned evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import chess
import requests

DEFAULT_TIMEOUT = 10
LICHESS_CLOUD_URL = "https://lichess.org/api/cloud-eval"


@dataclass
class Evaluation:
    fen: str
    cp: Optional[int]
    mate: Optional[int]
    pv_uci: str
    depth: Optional[int]
    source: str

    @property
    def side_to_move(self) -> str:
        return self.fen.split()[1] if self.fen else "w"


def _mock_eval(fen: str) -> Evaluation:
    # Provide a deterministic, mild advantage for white.
    return Evaluation(
        fen=fen,
        cp=35,
        mate=None,
        pv_uci="e2e4 e7e5 g1f3 b8c6 f1b5",
        depth=18,
        source="mock",
    )


def _uci_to_san_line(fen: str, pv_uci: str) -> str:
    if not pv_uci:
        return ""
    board = chess.Board(fen)
    san_moves = []
    for token in pv_uci.split():
        try:
            move = board.parse_uci(token)
        except ValueError:
            break
        if move not in board.legal_moves:
            break
        san_moves.append(board.san(move))
        board.push(move)
    return " ".join(san_moves)


def fetch_cloud_eval(fen: str, allow_mock: bool = True) -> Dict[str, object]:
    params = {"fen": fen}
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(LICHESS_CLOUD_URL, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        cp = None
        mate = None
        pv_uci = ""
        depth = payload.get("depth")
        pvs = payload.get("pvs") or []
        if pvs:
            first = pvs[0]
            cp = first.get("cp")
            mate = first.get("mate")
            pv_uci = first.get("moves", "")
        evaluation = Evaluation(
            fen=payload.get("fen", fen),
            cp=cp,
            mate=mate,
            pv_uci=pv_uci,
            depth=depth,
            source="lichess",
        )
    except Exception:
        if not allow_mock:
            raise
        evaluation = _mock_eval(fen)

    pv_san = _uci_to_san_line(evaluation.fen, evaluation.pv_uci)
    return {
        "fen": evaluation.fen,
        "cp": evaluation.cp,
        "mate": evaluation.mate,
        "pv_uci": evaluation.pv_uci,
        "pv_san": pv_san,
        "depth": evaluation.depth,
        "source": evaluation.source,
        "side_to_move": evaluation.side_to_move,
    }


__all__ = ["fetch_cloud_eval"]
