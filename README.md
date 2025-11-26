# Chess Game Review

A lightweight FastAPI + vanilla JS demo that analyses a Lichess game or raw PGN,
labels each move with chess.com-style annotations, and renders a dark-themed
results panel inspired by the chess.com Game Review UI.

## Features
- Input a PGN directly or paste a Lichess game URL to fetch the PGN.
- Mocked engine evaluation (pluggable for Stockfish/Lichess cloud later).
- Move labels: Brilliant, Great, Best, Excellent, Good, Book, Inaccuracy, Mistake, Miss, Blunder.
- Accuracy score per player plus label counts.
- Simple evaluation graph and summary table in the browser.

## Getting started
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://localhost:8000 in your browser, paste a PGN (or Lichess URL), and
click **Analyse Game**.

## Configuration notes
- The engine is mocked in `engine_interface.py`. Replace `evaluate_position`
  with a call to Stockfish or the Lichess Cloud Evaluation API to get real
  analysis.
- Move classification thresholds live in `analysis.py` for easy tuning.

## Example PGN
See `examples/sample.pgn` for a quick test game.
