import json
from pathlib import Path
import pandas as pd
from src.llm import classify_batch

def load_feedback(path):
    df = pd.read_csv(path).copy()
    required = {"id", "text"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    # Preserve the input language label separately from the model's prediction.
    if "language" in df.columns:
        df = df.rename(columns={"language": "provided_language"})
    # Clean comment text.
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    # Remove empty comments and duplicate IDs.
    df = df[df["text"] != ""].drop_duplicates("id")
    # Add optional metadata columns if absent.
    for col in ["source", "date"]:
        if col not in df.columns:
            df[col] = ""
    return df

def chunks(records, size):
    for i in range(0, len(records), size):
        yield records[i:i+size]

def analyze_dataframe(df, batch_size=10):
    records = [
        {"id": str(r["id"]), "text": str(r["text"]),
         "source": str(r.get("source", "")), "date": str(r.get("date", ""))}
        for _, r in df.iterrows()
    ]
    outputs = []
    for batch in chunks(records, batch_size):
        outputs.extend(classify_batch(batch))
    return df.merge(pd.DataFrame(outputs), on="id", how="left", validate="one_to_one")

def build_summary(df):
    return {
        "total_feedback": len(df),
        "sentiment": df["sentiment"].value_counts().to_dict(),
        "issue_categories": df["issue_category"].value_counts().to_dict(),
        "languages": df["language"].value_counts().to_dict(),
        "high_severity_count": int((df["severity"] == "high").sum()),
        "localization_issue_count": int(df["localization_issue"].fillna(False).sum())
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m src.pipeline data.csv")
    df = load_feedback(sys.argv[1])
    result = analyze_dataframe(df)
    Path("outputs").mkdir(exist_ok=True)
    result.to_csv("outputs/analyzed_feedback.csv", index=False)
    Path("outputs/summary.json").write_text(
        json.dumps(build_summary(result), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Analyzed {len(result)} comments.")
