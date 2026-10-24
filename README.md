# Game Feedback Analyzer

A small portfolio project exploring how an LLM can help a game product team organize multilingual player feedback. The intended workflow is to turn free-form comments into structured labels and summaries that can be reviewed in a dashboard.

**Current status:** Starter implementation / work in progress. The included feedback is synthetic demo data, and several known issues listed below have not been fixed yet. Do not present the demo data or its outputs as real player research.

## What it does

The intended workflow is:

1. **Load feedback** from a CSV file.
2. **Preprocess it** with Python and Pandas by checking required columns, trimming text, removing blank comments and duplicate IDs, and adding missing optional metadata columns.
3. **Analyze batches with an LLM API** to classify language, sentiment, issue category, severity, localization concerns, and generate a short summary and suggested follow-up insight.
4. **Merge the model results** with the original comments using each comment's ID.
5. **Summarize and display results** in a small Streamlit dashboard.

This project calls an existing LLM through an API; it does **not** train its own model. It also does **not** automatically scrape Reddit, YouTube, HoYoLAB, or other sites. A CSV must be supplied by the user.

## Repository structure

```text
game-feedback-analyzer/
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   └── sample_feedback.csv
├── prompts/
│   └── classify.txt
├── src/
│   ├── llm.py
│   └── pipeline.py
├── tests/
│   └── test_pipeline.py
└── outputs/
    └── .gitkeep
```

- **`app.py`** — Streamlit interface. Accepts an uploaded CSV or loads the sample dataset, lets the user select an LLM batch size, runs the analysis, and displays summary metrics, charts, and the classified records.
- **`src/pipeline.py`** — Coordinates loading, cleaning, batching, joining results, and calculating aggregate counts.
- **`src/llm.py`** — Builds the prompt, calls the configured LLM API, requests a defined JSON structure, and parses the response.
- **`prompts/classify.txt`** — Instructions for the model. It defines the categories and fields expected from each comment.
- **`data/sample_feedback.csv`** — Eight synthetic example comments used to demonstrate the expected input format. They are not a real or representative sample of player opinions.
- **`outputs/`** — The command-line workflow writes `analyzed_feedback.csv` and `summary.json` here. The folder contains `.gitkeep` so Git can track the otherwise empty directory.
- **`tests/test_pipeline.py`** — One basic automated test for dropping blank comments and duplicate IDs during preprocessing. It does not evaluate the LLM.
- **`.env.example`** — Template for local API configuration. Copy it to `.env` and add a valid API key locally.
- **`.gitignore`** — Excludes local secrets, virtual environments, caches, and generated output files from Git.
- **`requirements.txt`** — Lists the Python packages used or planned for the app: the OpenAI SDK, Pandas, python-dotenv, Streamlit, and Plotly. Plotly is currently unused, and the test runner is not listed here.

## How the main functions work

### `src/pipeline.py`

- **`load_feedback(path)`** reads a CSV into a Pandas DataFrame, verifies that `id` and `text` exist, normalizes text, removes blank entries and repeated IDs, and adds empty `source`/`date` columns if they are absent.
- **`chunks(records, size)`** splits records into smaller lists so the program can submit several comments in one API request instead of calling the API once per comment.
- **`analyze_dataframe(df, batch_size=10)`** converts rows into records, calls `classify_batch()` for each batch, then merges model results into the input DataFrame by `id`.
- **`build_summary(df)`** counts comments by sentiment, issue category, and language, and counts high-severity and localization-flagged comments. These are basic counts, not a statistical study or proof that a problem is widespread.

### `src/llm.py`

- **`SCHEMA`** describes the required JSON fields, including `id`, `language`, `sentiment`, `issue_category`, `severity`, `localization_issue`, `summary`, and `actionable_insight`.
- **`classify_batch(records)`** reads `prompts/classify.txt`, appends a batch of comments, sends the request to the configured LLM using the OpenAI Responses API with structured output, and parses the returned JSON. A valid JSON structure does not guarantee that the model's classifications are correct.

### `app.py`

The app uses Streamlit to display the input preview, provide a **Run AI analysis** button, and show metrics, bar charts, and a table of analyzed comments. The interface calls the pipeline functions rather than reimplementing the data-processing logic itself.

## Input format

The CSV must contain `id` and `text`. The `source` and `date` fields are optional but useful for documenting where and when feedback was posted.

```csv
id,text,source,date
001,"The event combat feels repetitive.",Reddit,2026-09-01
002,"日本語の翻訳が不自然です。",YouTube,2026-09-02
003,"新版本运行很卡。",HoYoLAB,2026-09-03
```

These rows are illustrative only. For a real project, collect public feedback only from sources whose terms permit the planned collection and use. Record sources and collection dates, avoid collecting unnecessary personal information, and document the limitations of the sample.

## Setup and run

Python 3.10+ is recommended.

```bash
# Create and activate a virtual environment (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux activation:
# source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set a valid API key and a model available to your account:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=your_available_model
```

**Never commit `.env` or your API key to GitHub.**

Run the dashboard:

```bash
streamlit run app.py
```

Or run the command-line pipeline:

```bash
python -m src.pipeline data/sample_feedback.csv
```

The command-line pipeline is intended to write `outputs/analyzed_feedback.csv` and `outputs/summary.json`. Both workflows require a working API configuration for actual LLM analysis.

To run the existing test, install `pytest` if needed and run:

```bash
python -m pytest
```

## Evaluation and intended improvements

The next important step is to create a small human-labeled evaluation set (for example, 30–50 comments) with reference labels for sentiment and issue category. Compare model predictions against those labels, inspect errors by language/category, revise the prompt, and measure the change. Do not invent accuracy figures; report only results from an actual evaluation.

Potential improvements include stricter allowed-category validation, robust checking that each input ID has exactly one corresponding model result, error/retry and rate-limit handling, language/category filters, trend analysis over time, and a better dashboard.

## Known issues in this starter

These are intentionally documented rather than presented as fixed:

1. **Language-column collision:** the sample CSV contains a `language` column, and the LLM response also returns `language`. The current merge can rename these columns to `language_x` / `language_y`, while the summary and dashboard expect `language`; this can cause a runtime error. Decide how to preserve supplied metadata versus model-predicted language, then update the merge and downstream code consistently.
2. **Uploaded CSV preprocessing:** `app.py` currently reads an uploaded CSV directly with `pandas.read_csv()` rather than passing it through `load_feedback()`. Uploaded files therefore do not receive the same preprocessing and validation as the sample file.
3. **Category schema:** the prompt lists issue categories, but the JSON schema currently allows `issue_category` to be any string. Add an allowed-value enum to standardize labels.
4. **Evaluation is not implemented:** the current test only checks input cleaning. There is no evaluation-set loader, metric calculation, prompt comparison, or model-quality test yet.
5. **Collection is manual:** no external-platform ingestion or scraping code has been implemented.
6. **Dependencies:** Plotly is listed but unused, and `pytest` is needed to run the test but is not listed in `requirements.txt`.

## Why this project

The goal is to investigate whether an LLM-based tool can help a game team triage multilingual player feedback, surface recurring themes, and flag possible localization or product issues for human review. It is intended as **decision support**, not as a replacement for human judgment: model errors, sampling bias, differences between language communities, and comment volume must all be considered before drawing product conclusions.
