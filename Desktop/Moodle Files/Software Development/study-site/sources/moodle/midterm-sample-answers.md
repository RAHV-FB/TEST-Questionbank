# Mid-term: sample answers (the teacher's official answers, verbatim; added to Moodle on 21 Oct 2026)

Source: `00 General/midterm-sample-questions (2).pdf`, pages 5–6 (pages 1–4 are the nine questions, unchanged; see midterm-sample-questions.md).

"Open this after you have answered midterm-sample-questions.md on paper.
For the open questions, the exam is marked on reasons, not on matching this wording. Different phrasing is fine as long as the idea is there."

## Multiple choice

| Q | Answer | Why |
|---|---|---|
| Q1 | b | The error names the file and the line. Read it and fix the syntax. Deleting `.venv`, upgrading or reinstalling uv can't fix a malformed file. |
| Q2 | c | A refactoring changes structure and keeps behaviour, and unchanged tests passing is the evidence. (a) is a feature, (b) a bug fix, (d) a design change. |
| Q3 | b | The error says the value can be None. Handle that case. `# type: ignore` and `Any` hide the problem and keep the crash. Removing annotations makes the checker blind. |
| Q4 | d | A failing test only says that test and code disagree. Neither being older or newer proves which one is right. Check the requirement (is the discount 10% or 5%?), then fix the one that is wrong. |
| Q5 | b | One function with several jobs is hard to test (you can't check the total without printing) and hard to change (a new output format touches the calculation). |
| Q6 | a | grep keeps the lines that contain food. `wc -l` counts lines. Two matches on one line count once, so (b) is wrong. grep alone would give (c). |

## Q7
1. It adds up the amounts of the rows whose third column is "food", prints the total, and returns it.
2. Any two of:
   - Names say nothing: `process`, `rows`, `r`, `r[2]`, `r[1]`. The reader must guess that column 2 is the category and column 1 the amount.
   - It does two jobs, calculating and printing, so a test of the total also prints.
   - "food" is hard-coded. Other categories need a copy of the function.
   - It trusts the file: a short row or a non-numeric amount crashes with an unhelpful error.
3. Give the function a descriptive name and name the columns (or use an Expense dataclass) to fix the unclear names. Pass the category as a parameter to fix the hard-coding. Move the print out to the caller so the function only returns the total. This fixes the two jobs.

## Q8
1. After loading the expenses, it checks whether any amount is negative and, if so, raises an error that names the file. Previously negative amounts went through silently.
2. B. It says what changed in behaviour and what it covers. Someone searching the history for "why do negative amounts fail?" will find it. A says nothing: the reader must open the diff to learn anything.
3. Any one of: a file with one negative amount raises ValueError; a file with only non-negative amounts still loads; a zero amount is accepted (edge case).

## Q9
1. Line 8 is a missing annotation ("what type is this?"). Line 15 is a None not handled ("this can be missing"). Line 22 is Any leaks in ("I gave up on this value").
2. Line 15. If `Expense | None` is None at runtime (an empty list or a missing id), the program crashes with an AttributeError for a real user. The other two are weaknesses in the checking, not crashes in themselves.
3. No. `# type: ignore` hides the warning without removing the problem. The line 15 crash stays, and now CI no longer shows it. The honest fixes are to annotate line 8, handle None on line 15 (check it, or change the type), and give line 22 a real return type. `# type: ignore` is acceptable only for a rare case that is understood, commented and deliberately accepted.

## Marking guide for the open questions
- Full marks: the right idea, with a reason (the "because").
- Partial marks: the right idea with no reason, or a reason that is half right.
- No marks: an answer that lists terms without connecting them to the code or output.

## Notes for us
- Q9.1 names a kind not in session 7 slide 10's table (missing annotation / types disagree / None not handled): **"Any leaks in" ("I gave up on this value")** for `Returning Any from function declared to return "float"  [no-any-return]`. Teach four kinds; never file `Returning Any` under "types disagree".
- The answers are short: one or two sentences per part, always with the reason, always tied to the code or output shown.
