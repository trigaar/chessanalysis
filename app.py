from __future__ import annotations

import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from analysis import analyze_game

app = FastAPI(title="Chess Game Review")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/analyse")
def analyse_game(payload: dict) -> JSONResponse:
    pgn_text = payload.get("pgn")
    url = payload.get("url")

    if url and not pgn_text:
        pgn_text = fetch_pgn_from_lichess(url)

    if not pgn_text:
        raise HTTPException(status_code=400, detail="Provide PGN text or a Lichess game URL")

    try:
        result = analyze_game(pgn_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JSONResponse(jsonable_encoder(result))


def fetch_pgn_from_lichess(url: str) -> str:
    game_id = url.rstrip("/").split("/")[-1]
    api_url = f"https://lichess.org/game/export/{game_id}?moves=true&pgnInJson=true"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch PGN: {exc}") from exc

    # Lichess returns PGN text by default
    return response.text


# Static frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def root() -> FileResponse:
    index_path = os.path.join(frontend_dir, "index.html")
    return FileResponse(index_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
