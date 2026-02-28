# CodeRefine – Streamlit (SaaS-style)

Run: `streamlit run app.py` (from this folder).

## Features

1. **Auth** – Signup / Login / Logout with session (SQLite).
2. **Code Review** – Static analysis, **total** time & space complexity (with reasoning), quality score 0–100, AI line-by-line explanation, AI bug detection & fix suggestions, downloadable PDF report.
3. **Code Conversion** – C ↔ Python (Groq AI).
4. **Code Comparison** – Two snippets, AI summary of differences.
5. **History** – All reviews/conversions/comparisons saved in SQLite.

## Setup

```bash
cd streamlit_app
pip install -r requirements.txt
```

1. Get a **free** Groq API key (no billing required): https://console.groq.com
2. Paste it in `streamlit_app/.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
3. Run:
   ```bash
   streamlit run app.py
   ```

## Env

- `GROQ_API_KEY` – Required for AI features. Free at https://console.groq.com (no credit card needed).
- `GROQ_MODEL` – Model to use (default: `llama-3.1-8b-instant`). Other options: `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`.
- Without the key, only rule-based analysis and quality score work.

## Folder structure

```
streamlit_app/
  app.py                 # Main entry, auth gate, dashboard
  config.py
  requirements.txt
  auth/
    auth.py              # Login, signup, logout, session
    db.py                # User table, password hashing
  pages/
    1_Code_Review.py     # Review, complexity, score, AI, PDF
    2_Code_Conversion.py # C ↔ Python
    3_Code_Comparison.py # Compare two snippets
    4_History.py         # Saved history
  modules/
    analyzer.py          # Static + total time/space complexity
    quality_score.py     # 0–100 score
    groq_client.py       # Groq API wrapper (free LLM)
    ai_explainer.py      # Line-by-line explanation
    ai_bug_fix.py        # Bug detection & fix suggestions
    code_converter.py    # C ↔ Python
    code_comparison.py   # Compare summary
    report_pdf.py        # PDF report
  utils/
    db.py                # History CRUD, schema
  database/
    coderefine.db        # SQLite (created at runtime)
```

## Complexity

- **Time**: Derived from loops (nesting depth), recursion, and operations like `sorted()` to produce a single **overall** time complexity (e.g. O(1), O(n), O(n²), O(n³)+) plus line-level reasons.
- **Space**: Derived from comprehensions, loop depth, and auxiliary structures to produce overall space complexity and reasons.
