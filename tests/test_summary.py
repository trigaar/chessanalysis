import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from analysis_summary import summarize_position


def test_advantage_labels():
    assert summarize_position(0, None, "", "w").advantage == "Equal"
    assert "White" in summarize_position(120, None, "", "w").advantage
    assert "Black" in summarize_position(-300, None, "", "b").advantage


def test_mate_priority():
    summary = summarize_position(None, 2, "", "w")
    assert "mate" in summary.advantage.lower()


def test_notes_variation():
    assert "Balanced" in summarize_position(10, None, "", "w").notes
    assert "Big swing" in summarize_position(500, None, "", "w").notes
