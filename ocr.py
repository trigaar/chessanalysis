"""Lightweight OCR pipeline to extract a chess FEN from a board image.

This is intentionally minimal: it loads a PNG, applies basic preprocessing,
and attempts OCR per-square. Accuracy depends heavily on image quality and
piece font; a TODO is left for improved detection (template matching or ML).
"""
from __future__ import annotations

import string
from dataclasses import dataclass
from typing import List, Optional, Tuple

import chess
from PIL import Image
import pytesseract


# Simple mapping from detected character to piece symbol.
CHAR_TO_PIECE = {
    "p": "p",
    "r": "r",
    "n": "n",
    "b": "b",
    "q": "q",
    "k": "k",
    "P": "P",
    "R": "R",
    "N": "N",
    "B": "B",
    "Q": "Q",
    "K": "K",
}


@dataclass
class OcrResult:
    fen: str
    confidence: float
    warnings: List[str]


def _preprocess(img: Image.Image) -> Image.Image:
    # Convert to grayscale and increase contrast; future: thresholding and denoise.
    grayscale = img.convert("L")
    return grayscale


def _split_board(img: Image.Image) -> List[Image.Image]:
    width, height = img.size
    square_w = width // 8
    square_h = height // 8
    squares = []
    for row in range(8):
        for col in range(8):
            left = col * square_w
            upper = row * square_h
            right = left + square_w
            lower = upper + square_h
            squares.append(img.crop((left, upper, right, lower)))
    return squares


def _detect_square(square_img: Image.Image) -> Tuple[Optional[str], float]:
    # Use a tiny whitelist to reduce noise; treat empty as None.
    config = "-c tessedit_char_whitelist=" + string.ascii_letters
    text = pytesseract.image_to_string(square_img, config=config)
    text = text.strip()
    if not text:
        return None, 0.0
    char = text[0]
    piece = CHAR_TO_PIECE.get(char)
    if piece is None:
        return None, 0.0
    # Confidence is crude; pytesseract returns per-character confidences via image_to_data
    return piece, 0.6


def _squares_to_fen(pieces: List[Optional[str]]) -> str:
    fen_rows = []
    for r in range(8):
        row_syms = []
        empties = 0
        for c in range(8):
            piece = pieces[r * 8 + c]
            if piece:
                if empties:
                    row_syms.append(str(empties))
                    empties = 0
                row_syms.append(piece)
            else:
                empties += 1
        if empties:
            row_syms.append(str(empties))
        fen_rows.append("".join(row_syms) or "8")
    fen_board = "/".join(fen_rows)
    # Default side to move: white; castle/en-passant/half/fullmove defaults.
    return f"{fen_board} w KQkq - 0 1"


def extract_fen_from_image(path: str) -> OcrResult:
    image = Image.open(path)
    processed = _preprocess(image)
    squares = _split_board(processed)
    pieces: List[Optional[str]] = []
    confidences: List[float] = []
    for sq in squares:
        piece, conf = _detect_square(sq)
        pieces.append(piece)
        confidences.append(conf)
    fen = _squares_to_fen(pieces)
    avg_conf = sum(confidences) / len(confidences)
    warnings: List[str] = []
    try:
        chess.Board(fen)
    except ValueError as exc:
        warnings.append(str(exc))
    return OcrResult(fen=fen, confidence=avg_conf, warnings=warnings)


__all__ = ["extract_fen_from_image", "OcrResult"]
