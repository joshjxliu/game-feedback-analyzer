import pytest

from src.pipeline import load_feedback


def test_load_feedback_removes_empty_text_and_duplicate_ids(tmp_path):
    path = tmp_path / "feedback.csv"
    path.write_text(
        "id,text\n"
        "1,hello\n"
        "1,duplicate\n"
        "2,\n",
        encoding="utf-8"
    )

    df = load_feedback(path)

    assert df["id"].tolist() == ["1"]
    assert df["text"].tolist() == ["hello"]


def test_load_feedback_preserves_leading_zeros(tmp_path):
    path = tmp_path / "feedback.csv"
    path.write_text(
        "id,text\n"
        "001,hello\n"
        "002,world\n",
        encoding="utf-8"
    )

    df = load_feedback(path)

    assert df["id"].tolist() == ["001", "002"]


def test_load_feedback_rejects_missing_ids(tmp_path):
    path = tmp_path / "feedback.csv"
    path.write_text(
        "id,text\n"
        ",hello\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="non-empty id"):
        load_feedback(path)