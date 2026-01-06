"""Minimal Tkinter desktop shell for OCR + Lichess eval demo.

This keeps the project runnable on Windows without extra packaging. The app is
single-window and delegates OCR and evaluation to helper modules.
"""
from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from typing import Optional

from analysis_summary import summarize_position
from lichess_client import fetch_cloud_eval
from ocr import extract_fen_from_image


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Chess OCR + Eval (Skeleton)")
        self.geometry("900x700")

        self.image_path: Optional[str] = None
        self.fen_var = tk.StringVar()
        self.eval_var = tk.StringVar(value="No evaluation yet")
        self.summary_var = tk.StringVar(value="Load an image to begin")

        self._build_ui()

    def _build_ui(self) -> None:
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(top, text="Select PNG", command=self.select_image).pack(side=tk.LEFT)
        tk.Button(top, text="Extract position", command=self.run_ocr).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Analyze", command=self.run_eval).pack(side=tk.LEFT)

        self.image_label = tk.Label(self, text="No image selected", fg="gray")
        self.image_label.pack(fill=tk.X, padx=10, pady=5)

        fen_frame = tk.LabelFrame(self, text="FEN")
        fen_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Entry(fen_frame, textvariable=self.fen_var).pack(fill=tk.X, padx=5, pady=5)

        eval_frame = tk.LabelFrame(self, text="Evaluation")
        eval_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(eval_frame, textvariable=self.eval_var).pack(anchor="w", padx=5, pady=2)
        tk.Label(eval_frame, textvariable=self.summary_var, wraplength=850, justify="left").pack(anchor="w", padx=5)

        output_frame = tk.LabelFrame(self, text="Status log")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log = scrolledtext.ScrolledText(output_frame, state="disabled", height=20)
        self.log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def select_image(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PNG images", "*.png"), ("All files", "*.*")])
        if not path:
            return
        self.image_path = path
        self.image_label.config(text=f"Selected: {os.path.basename(path)}")
        self.log_message(f"Image selected: {path}")

    def run_ocr(self) -> None:
        if not self.image_path:
            messagebox.showwarning("No image", "Select an image first")
            return
        threading.Thread(target=self._run_ocr_thread, daemon=True).start()

    def _run_ocr_thread(self) -> None:
        self.log_message("Running OCR...")
        try:
            result = extract_fen_from_image(self.image_path)
        except Exception as exc:
            self.log_message(f"OCR failed: {exc}")
            messagebox.showerror("OCR error", str(exc))
            return
        self.fen_var.set(result.fen)
        warn_text = "; ".join(result.warnings) if result.warnings else ""
        self.log_message(f"FEN: {result.fen} (confidence {result.confidence:.2f}) {warn_text}")

    def run_eval(self) -> None:
        fen = self.fen_var.get().strip()
        if not fen:
            messagebox.showwarning("No FEN", "Run OCR or enter a FEN first")
            return
        threading.Thread(target=self._run_eval_thread, args=(fen,), daemon=True).start()

    def _run_eval_thread(self, fen: str) -> None:
        self.log_message("Calling Lichess Cloud Eval (mock on failure)...")
        try:
            eval_data = fetch_cloud_eval(fen)
        except Exception as exc:
            self.log_message(f"Eval error: {exc}")
            messagebox.showerror("Eval error", str(exc))
            return
        cp = eval_data.get("cp")
        mate = eval_data.get("mate")
        best_line = eval_data.get("pv_san") or eval_data.get("pv_uci") or ""
        summary = summarize_position(cp, mate, best_line, eval_data.get("side_to_move", "w"))
        eval_text = f"Eval: {'mate ' + str(mate) if mate is not None else (cp if cp is not None else 'N/A')} (depth {eval_data.get('depth') or '?'}; source {eval_data.get('source')})"
        self.eval_var.set(eval_text)
        self.summary_var.set(f"Advantage: {summary.advantage} | To move: {summary.side_to_move}\nBest line: {summary.best_line}\nNotes: {summary.notes}")
        self.log_message("Analysis complete")

    def log_message(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert(tk.END, text + "\n")
        self.log.configure(state="disabled")
        self.log.see(tk.END)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
