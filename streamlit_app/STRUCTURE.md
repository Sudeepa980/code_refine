# CodeRefine Streamlit – Full Folder Structure

```
CodeRefine/
  streamlit_app/
    app.py                    # Main entry: auth gate, dashboard, sidebar
    config.py                 # Paths, Groq API settings
    requirements.txt          # streamlit, groq, reportlab
    README.md
    STRUCTURE.md              # This file

    auth/                     # Authentication module
      __init__.py
      auth.py                 # login(), signup(), logout(), get_current_user(), is_authenticated()
      db.py                   # create_user(), check_password(), get_user_by_id()

    pages/                    # Streamlit multipage (auto sidebar)
      1_Code_Review.py         # Code review: static, complexity, score, AI explain, bug/fix, PDF
      2_Code_Conversion.py     # C ↔ Python conversion (Groq)
      3_Code_Comparison.py    # Compare two snippets (Groq summary)
      4_History.py             # List saved reviews/conversions/comparisons

    modules/                  # Business logic
      __init__.py
      analyzer.py             # analyze_static(), analyze_complexity() → total time & space + reasons
      quality_score.py        # compute_quality_score() → 0–100 + reasons
      groq_client.py          # chat() wrapper for Groq free API
      ai_explainer.py          # explain_line_by_line(), explain_lines_batch()
      ai_bug_fix.py           # detect_bugs_and_suggest_fixes(), get_fix_suggestion_for_line()
      code_converter.py       # convert_code() C ↔ Python
      code_comparison.py      # compare_and_summarize()
      report_pdf.py           # generate_pdf() → BytesIO

    utils/
      __init__.py
      db.py                   # save_history(), get_history(), get_one(), ensure_schema()

    database/                 # Created at runtime
      coderefine.db           # SQLite: users, history
```

## Complexity behaviour

- **Time complexity** is estimated for the **whole code**: loops (nesting depth), recursion, and operations like `sorted()` are combined to produce one overall label (e.g. O(1), O(n), O(n²), O(n³)+) plus line-by-line reasons.
- **Space complexity** is estimated from comprehensions, loop depth, and auxiliary data structures, again with reasons.
