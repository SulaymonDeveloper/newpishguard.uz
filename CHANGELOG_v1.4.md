# PhishGuard v1.4 — Quiz & Exam Scoring Overhaul

## Released: 2026-02-03

---

### Bug Fixes

#### m1-lesson2 — Mini Game "Is it Phishing?" (Critical — fully broken)
- **`correctAnswers` was a number (`0`), not an object** — all comparisons failed silently. Replaced with `{ msg1: true, msg2: true, msg3: false }`.
- **`answered` and `score` variables were never declared** — caused ReferenceError on first click. Added `let score = 0` and tracking via `answeredQuestions` Set.
- **Feedback element ID mismatch** — `checkAnswer` looked for `'f' + q` (→ `fmsg1`) but actual IDs are `feedback1`. Fixed to extract number from `q` and target `feedback{num}`.
- **Button highlight regex matched `[a-d]` but choices are booleans** — regex now correctly matches `true|false` from onclick attributes.
- **`showScore()` displayed `correctAnswers` (the old number) instead of `score`** — fixed to use the `score` counter.
- **Duplicate `checkAnswer` function body** — orphaned code fragment after closing brace removed.
- **msg3 button values were swapped** — dentist appointment (NOT phishing) had Phishing=`false` and Not-Phishing=`true`. Corrected so Phishing=`true` (wrong answer) and Not-Phishing=`false` (correct answer).
- **Auto-show score** — score now displays automatically after all 3 messages are answered.

#### m1-lesson5 — Module 1 Final Quiz (Orphan code)
- **Orphaned duplicate code block** after `checkAnswer` closing brace caused JS syntax error. Removed and rewrote `checkAnswer` cleanly with all proper closing braces.
- **Added auto-show score** after all 5 questions answered.

#### m2-lesson6 — Module 2 Final Quiz (Boolean type mismatch — Critical)
- **`choice === correctAnswers[q]` always failed** — onclick passes booleans as literals (`true`/`false`) which arrive correctly typed in JS, but the highlight comparison `optValue === choice` could fail if ever coerced to string. Added explicit `typeof` guard: if `choice` is a string, parse it to boolean.
- **Orphaned duplicate code block** removed (same pattern as m1-lesson5).
- **Added auto-show score** after all 8 questions answered.

#### m3-lesson5 — Module 3 Final Quiz (Multiple critical bugs)
- **`correctAnswers` was a 0-indexed array but accessed with 1-based indices** — `correctAnswers[1]` returned the second item, not the first. Converted to a keyed object `{ 1: 'report', 2: 'report', ... }`.
- **`answered` and `score` variables never declared** — added `let answered = {}` and `let score = 0`.
- **Feedback ID mismatch** — `buildQuiz` created `id="feedback${i}"` but `checkAnswer` looked for `id="f${i}"`. Standardized to `f${i}`.
- **Highlight regex matched `[a-d]` but actual choices are `'ignore'`/`'verify'`/`'report'`** — regex updated to `['"]([^'"]+)['"]` to match any string choice.
- **Duplicate `buildQuiz` and `checkAnswer` definitions** removed.
- **`showScore()` function was missing entirely** — added with proper percent calculation and pass/fail logic.

#### final-exam.html (Critical — exam completely non-functional)
- **Questions were never rendered** — the Jinja `questions` object was passed to the template but no loop existed to generate HTML. Added `{% for q in questions %}` loop rendering each question with A/B/C/D options.
- **Submit button called `showScore()` which didn't exist** — changed to `submitExam()` which performs the actual `fetch('/submit-exam')`.
- **`selectAnswer()` tried to find `input[name="q{id}"]`** but options are `div.quiz-option` — rewritten to highlight `.quiz-option` divs using a `.selected` CSS class.
- **Added `.selected` CSS class** for visual feedback when an option is clicked.

#### app.py — `submit_exam()` route (Robustness)
- **Crashes on invalid/missing JSON body** — wrapped in try/catch with `force=True, silent=True`. Returns `{"error": "No data received"}` on failure instead of 500.
- **Answer comparison was case-sensitive and format-rigid** — added normalization: `strip().lower()` on both user and DB answers. Handles `option_a`/`option_b`/etc. format by stripping the `option_` prefix before comparison.

---

### Test Results (automated)
- ✅ All 16 lesson pages render (HTTP 200)
- ✅ All 3 module completions work
- ✅ Final exam renders 10 questions with 4 options each
- ✅ Submit button calls `submitExam()` → `fetch('/submit-exam')`
- ✅ Exam scoring: exact match (`b`) → 10/10 (100%)
- ✅ Exam scoring: mixed formats (`B`, `option_b`, `C`, `option_c`) → 10/10 (100%)
- ✅ Exam scoring: bad JSON body → clean error response (no crash)
- ✅ All JS files pass Node.js `--check` syntax validation
- ✅ `app.py` passes Python syntax validation
- ✅ Zero duplicate function definitions across all 16 lesson files
