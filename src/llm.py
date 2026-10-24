import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "language": {"type": "string"},
                    "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                    "issue_category": {
                        "type": "string",
                        "enum": [
                            "gameplay",
                            "balance",
                            "characters",
                            "story",
                            "performance",
                            "bugs",
                            "monetization",
                            "localization",
                            "customer_support",
                            "content",
                            "other"
                        ]
                    },
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "localization_issue": {"type": "boolean"},
                    "summary": {"type": "string"},
                    "actionable_insight": {"type": "string"}
                },
                "required": ["id","language","sentiment","issue_category","severity",
                             "localization_issue","summary","actionable_insight"],
                "additionalProperties": False
            }
        }
    },
    "required": ["results"],
    "additionalProperties": False
}

def classify_batch(records):
    if not records:
        return []

    prompt = Path("prompts/classify.txt").read_text(encoding="utf-8")
    prompt += "\nComments:\n" + json.dumps(records, ensure_ascii=False, indent=2)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Copy .env.example to .env and add your key.")

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5"),
        store=False,
        input=prompt,
        text={"format": {
            "type": "json_schema",
            "name": "game_feedback_classification",
            "schema": SCHEMA,
            "strict": True
        }}
    )
    return json.loads(response.output_text)["results"]
