import pandas as pd
from src.pipeline import load_feedback

def test_load_feedback(tmp_path):
    p = tmp_path / "f.csv"
    pd.DataFrame([{"id":"1","text":"hello"},{"id":"1","text":"dup"},{"id":"2","text":""}]).to_csv(p,index=False)
    df = load_feedback(p)
    assert list(df["id"]) == ["1"]
