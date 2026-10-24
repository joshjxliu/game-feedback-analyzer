# Game Feedback Analyzer

A work-in-progress Python application exploring how a large language model (LLM) can help organize multilingual game-player feedback into structured information for product teams.

The prototype accepts comments from a CSV file, uses an LLM API to classify each comment, and presents the results in a small dashboard. It is intended as decision support for human review—not as a replacement for product, localization, or community experts.

## Features

- **CSV preprocessing:** checks required columns, trims comment text, removes blank comments and duplicate IDs, and supplies optional metadata columns when missing.
- **LLM-based classification:** assigns each comment a language, sentiment, issue category, severity, and localization-issue flag.
- **Structured results:** generates a concise summary and a suggested actionable insight for each comment.
- **Summary dashboard:** displays counts and bar charts for sentiment and issue categories, alongside a table of analyzed comments.
- **Command-line output:** exports analyzed comments to CSV and aggregate counts to JSON.
- **Defined categories:** uses a consistent issue taxonomy: `gameplay`, `balance`, `characters`, `story`, `performance`, `bugs`, `monetization`, `localization`, `customer_support`, `content`, and `other`.

This project calls an existing LLM through an API; it does not train its own model. It does not automatically scrape Reddit, YouTube, HoYoLAB, or other websites. Feedback must be provided as a CSV.

## Workflow

```text
CSV feedback
    ↓
Validate and clean with Pandas
    ↓
Split comments into batches
    ↓
Call the LLM API with a classification prompt
    ↓
Parse structured JSON and merge results by ID
    ↓
Aggregate counts
    ↓
Streamlit dashboard or CSV/JSON output
```

## Repository structure

```text
game-feedback-analyzer/
├── app.py                    # Streamlit dashboard
├── README.md
├── requirements.txt          # Python dependencies
├── .env.example              # Example API configuration
├── .gitignore
├── data/
│   └── sample_feedback.csv   # Synthetic demonstration comments
├── prompts/
│   └── classify.txt          # LLM instructions and category definitions
├── src/
│   ├── llm.py                # LLM API call and output schema
│   └── pipeline.py           # Cleaning, batching, merging, and summaries
├── tests/
│   └── test_pipeline.py      # Basic preprocessing test
└── outputs/                  # Generated command-line results
```

## How it works

### `src/pipeline.py`

- **`load_feedback(path)`** reads the CSV, checks that `id` and `text` are present, preserves any supplied language label as `provided_language`, trims text, removes blank comments and duplicate IDs, and adds `source` and `date` columns if absent.
- **`chunks(records, size)`** divides comments into batches to reduce the number of individual API calls.
- **`analyze_dataframe(df, batch_size=10)`** sends each batch to `classify_batch()`, then joins the AI results to the original records using `id`.
- **`build_summary(df)`** counts comments by sentiment, issue category, and predicted language, plus high-severity and localization-flagged comments.

### `src/llm.py`

- **`SCHEMA`** defines the expected response format and constrains sentiment, severity, and issue category to predefined values.
- **`classify_batch(records)`** combines the classification prompt with a batch of comments, calls the OpenAI Responses API with structured output, and parses the returned JSON.

Structured output constrains the response format, but it does not guarantee that a classification is semantically correct. Model predictions should be checked against human judgments.

### `app.py`

The Streamlit interface lets users upload a CSV or use the included sample data, choose an LLM batch size, run the pipeline, and explore summary metrics, bar charts, and the resulting comment-level table.

## Input format

The CSV must contain `id` and `text`. `source` and `date` are optional metadata fields. An optional `language` field is preserved as `provided_language`, while `language` in the analyzed output refers to the model's prediction.

```csv
id,text,source,date
001,"The event combat feels repetitive.",Reddit,2026-09-01
002,"日本語の翻訳が不自然です。",YouTube,2026-09-02
003,"新版本运行很卡。",HoYoLAB,2026-09-03
```

The rows above are illustrative examples, not real research data. The repository's `data/sample_feedback.csv` contains synthetic demonstration comments and should not be treated as representative evidence of player opinions.

Use feedback only from sources whose terms permit the intended collection and use. Avoid collecting unnecessary personal information and document the sources and time period for any real dataset. Keep IDs unique, stable, and consistently formatted so that model results can be matched back to their original comments.

## Setup

Python 3.10 or later is recommended.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a local `.env` file based on `.env.example` and configure an API key and model available to the account:

```text
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=your_available_model
```

## Run the application

Start the dashboard:

```bash
streamlit run app.py
```

To run the command-line pipeline and write output files:

```bash
python -m src.pipeline data/sample_feedback.csv
```

The command-line workflow writes:

- `outputs/analyzed_feedback.csv` — original comments and model-generated fields.
- `outputs/summary.json` — aggregate counts by sentiment, category, and language, plus severity and localization counts.

Actual classification requires a working API configuration and network access. The dashboard displays charts in the browser; the command-line workflow writes CSV and JSON files.

## Tests

The repository includes a basic test for input cleaning. Install `pytest` if it is not already available, then run:

```bash
python -m pytest
```

The current test does not call the LLM or measure classification accuracy.

## Current limitations and future work

- **Evaluation is not implemented:** there is no human-labeled evaluation set or systematic measurement of classification quality yet.
- **Data collection is manual:** the application accepts CSV input but does not collect comments from external platforms.
- **ID validation can be strengthened:** the pipeline relies on IDs to merge model output with input data. Robust checks for missing IDs, input/output ID mismatches, and numeric-versus-string ID handling remain future improvements.
- **API resilience can be improved:** retries, rate-limit handling, and clearer handling of incomplete or invalid model responses are not yet implemented.
- **Analysis is exploratory:** summary values are counts, not proof that an issue is widespread. Language groups and sources may have different sample sizes or biases.
- **Dependencies can be cleaned up:** Plotly is listed in `requirements.txt` but is not currently used by the application; `pytest` is required for tests but is not currently listed there.

## Motivation

The project investigates whether an LLM-based tool can help a game team triage multilingual feedback, identify recurring topics, and flag potential product or localization issues for human review. Its usefulness should be assessed through a labeled evaluation set and careful review of model errors before making product decisions from its output.
