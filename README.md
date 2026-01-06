# Chess OCR + Lichess Eval (Desktop Skeleton)

This repo now ships a minimal, standalone desktop prototype for Windows/macOS/
Linux that:

- Lets you select a PNG screenshot of a chess board.
- Runs lightweight OCR to guess the FEN.
- Calls Lichess Cloud Eval (with automatic mock fallback) to get an engine
  score and principal variation.
- Produces a short, chess.com-style “free-lite” summary of the position.

The implementation keeps the original FastAPI demo for reference but adds a
Tkinter desktop shell to avoid hosting a local web server.

## Quickstart (Desktop)

1. Install Python 3.10+.
2. (Windows) Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
   and ensure `tesseract` is on your PATH.
3. Install deps:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run the desktop app:
   ```bash
   python desktop.py
   ```

## OCR notes
- OCR is intentionally simple. It assumes an 8x8 board fills the image and
  attempts per-square character recognition. Accuracy depends on the piece set.
- If OCR is wrong, edit the FEN field manually and re-run **Analyze**.
- TODO: add board auto-detection and template matching for better accuracy.

## Lichess evaluation
- The app calls the public Lichess Cloud Eval endpoint. If the request fails
  (offline/rate limit), it falls back to a mock response so the UI keeps
  working.

## Development
- `analysis_summary.py` isolates the wording/thresholds for the summary layer.
- Tests: `pytest tests/test_summary.py`

## Known limitations / next steps
- OCR is fragile; add board detection and better piece recognition.
- No packaging yet (pyinstaller/briefcase); run via `python desktop.py`.
- Move-by-move review and PGN parsing remain in the legacy FastAPI demo.
