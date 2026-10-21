"""Stop S7 of the 6-hour cram: sample Q7, read code and say what is wrong (open).

Writes types/S7.json in the shape given by CRAM6_SPEC.md. The teacher's answer is copied verbatim
from study-site/sources/moodle/midterm-sample-answers.md.
"""

import json
from pathlib import Path

QUESTION = (
    "```python\n"
    "def process(rows):\n"
    "    total = 0\n"
    "    for r in rows:\n"
    "        if r[2] == \"food\":\n"
    "            total += float(r[1])\n"
    "    print(\"Food total:\", total)\n"
    "    return total\n"
    "```"
)

HIS_ANSWER = (
    "1. It adds up the amounts of the rows whose third column is \"food\", prints the total, and returns it.\n"
    "2. Any two of:\n"
    "   - Names say nothing: `process`, `rows`, `r`, `r[2]`, `r[1]`. The reader must guess that column 2 is the "
    "category and column 1 the amount.\n"
    "   - It does two jobs, calculating and printing, so a test of the total also prints.\n"
    "   - \"food\" is hard-coded. Other categories need a copy of the function.\n"
    "   - It trusts the file: a short row or a non-numeric amount crashes with an unhelpful error.\n"
    "3. Give the function a descriptive name and name the columns (or use an Expense dataclass) to fix the unclear "
    "names. Pass the category as a parameter to fix the hard-coding. Move the print out to the caller so the "
    "function only returns the total. This fixes the two jobs."
)

DECODED = (
    "- **The pattern.** A short function with no explanation, then three parts that climb: say what it does, "
    "name two problems, say how you would change it and which problem each change solves.\n"
    "- **Part 1.** One sentence about what comes out, not how it loops: the amounts of the rows whose third "
    "column is \"food\", added up, printed and returned. It says \"prints\" because parts 2 and 3 build on it.\n"
    "- **Part 2: any two of four, each tied to the code.** The unclear names (`r[2]` and `r[1]` make the reader "
    "guess the columns), calculating plus printing (a test of the total also prints), `\"food\"` hard-coded "
    "(another category needs a copy of the function), and trust in the file (a short row or a text amount "
    "crashes with an unhelpful error). Each has a line to point at and a cost to a teammate. That cost is the "
    "reason, the \"because\".\n"
    "- **Part 3: each change next to the problem it fixes.** A descriptive name and named columns fix the "
    "unclear names. A category parameter fixes the hard-coding. Moving the `print` to the caller fixes the two "
    "jobs. The pairing is what the marks look for. It is all in words.\n"
    "- **What does not score.** \"The names are bad\" with no example, \"add comments\" (the course renames "
    "instead), and remarks about speed. Terms that are not connected to the code earn nothing.\n"
    "- **Level.** One or two sentences per part, 5 to 8 lines for the whole question."
)

SPOT = (
    "- A function of 5 to 15 lines with one-letter names (`r`, `t`, `n`), tuples read by number (`r[2]`, "
    "`r[3]`) and a `print` or a bare number inside.\n"
    "- The words \"what is wrong\", \"problems a teammate would face when reading, testing or changing it\" "
    "and \"Describe (in words, do not write code)\".\n"
    "- Three numbered parts: what it does, two problems, then the changes and which problem each solves.\n"
    "- Other domains are possible (a gradebook, a parking fee, library fines) with the same few problems. "
    "They are the course's own ideas, not tricks."
)

BASICS = [
    {
        "id": "S7-b1",
        "heading": "The four problems he rewards",
        "body_md": (
            "His answer to part 2 lists four problems and asks for any two. Each is a course idea.\n\n"
            "| Problem | Point at | What a teammate cannot do |\n"
            "|---|---|---|\n"
            "| Names say nothing | `process`, `r`, `r[2]`, `r[1]` | tell which column is which without guessing |\n"
            "| Two jobs: calculating and printing | the `print` inside | use or test the total without the screen output |\n"
            "| A value is hard-coded | `\"food\"` in the `if` | use another category without copying the function |\n"
            "| It trusts the file | `float(r[1])`, `r[2]` | get a useful error from a short row or a text amount |\n\n"
            "Pick the two you can tie to a line. \"The names are bad\" is an opinion. \"`r[2]` hides which column "
            "is the category, so a teammate must guess\" is a problem."
        ),
    },
    {
        "id": "S7-b2",
        "heading": "Part 3: every change next to its problem",
        "body_md": (
            "Part 3 is marked on the pairing. Write each change in words and say which problem it fixes. He never "
            "asks for code.\n\n"
            "- Give the function a descriptive name and name the columns, or use an `Expense` dataclass. This fixes "
            "the unclear names (\"a tuple is a missing type\").\n"
            "- Pass the category as a parameter. This fixes the hard-coded value.\n"
            "- Move the `print` to the caller so the function only returns the total. This fixes the two jobs. "
            "\"Computation is not output\": a function that returns can be tested, reused and read on its own.\n\n"
            "Use the frame \"I would ..., which fixes ...\". Answer with the two problems you named in part 2, so "
            "every change has a problem next to it."
        ),
    },
]

CHECKS = [
    {
        "id": "S7-c1",
        "q_md": "Part 3 of Q7. Which sentence earns the mark for a change?",
        "options": [
            "I would clean up the function and make it more readable.",
            "I would move the `print` to the caller, which fixes the two jobs.",
            "I would add a comment above each line.",
        ],
        "answer": 1,
        "why_md": (
            "A change scores when it names the move and the problem it fixes. The first is a wish. The third "
            "contradicts the course: a comment that explains what the code does is a failure of naming."
        ),
    },
    {
        "id": "S7-c2",
        "q_md": "A function returns its total and also prints it. Which reason for calling that a problem is right?",
        "options": [
            "pytest refuses to run a function that calls `print`.",
            "A function that calls `print` always returns `None`.",
            "Every call also prints, so a test or another report gets output it did not ask for.",
        ],
        "answer": 2,
        "why_md": (
            "The function still returns the total, so a test can check it. The cost is the output on every call. "
            "That is \"computation is not output\"."
        ),
    },
]

METHOD = [
    "Read the code once and say what comes out in one sentence: what it adds up or counts, over which rows, and "
    "that it prints and returns.",
    "Scan for the four problems: names and tuple indexes, a `print` inside, a hard-coded value, no check on the "
    "input.",
    "Choose the two you can tie to a line. For each, write the line and what a teammate cannot do because of it.",
    "Part 3: one sentence per change, \"I would ..., which fixes ...\", in words.",
    "Leave out comments, docstrings and speed. The course fixes unclear code by renaming it.",
]

WORKED = [
    {
        "title": "Same shape, other topic: library fines",
        "question_md": (
            "A library group wrote this. Each loan is a tuple `(title, member, days_late)`.\n\n"
            "```python\n"
            "def check(loans):\n"
            "    fine = 0\n"
            "    for x in loans:\n"
            "        if x[2] > 0:\n"
            "            fine += x[2] * 0.20\n"
            "    print(\"Fines:\", fine)\n"
            "    return fine\n"
            "```\n\n"
            "1. In one sentence, what does this function do?\n"
            "2. Name two problems a teammate would face when reading, testing or changing it.\n"
            "3. Describe in words how you would change it, and which problem each change solves."
        ),
        "steps_md": [
            "Part 1: say what comes out. It charges 0.20 for each day late, only on late loans, then prints and "
            "returns the total.",
            "Part 2: the names (`check`, `x`, `x[2]`) hide that the third item is the days late. The `print` "
            "means every caller gets output it did not ask for. The bare `0.20` is a third candidate.",
            "Part 3: pair each change with its problem. A `Loan` dataclass and a name fix the names. Returning "
            "only the total fixes the two jobs.",
        ],
        "answer_md": (
            "1. It adds up 0.20 per late day for each late loan, prints the total and returns it.\n"
            "2. The names (`check`, `x`, `x[2]`) hide that the third item is the days late, so a teammate must "
            "guess. It also prints, so every caller gets output it did not ask for.\n"
            "3. A `Loan` dataclass and a clear name fix the names. Moving the `print` to the caller fixes the two "
            "jobs."
        ),
    }
]

TWISTS = [
    {
        "twist_md": "A gradebook function opens `grades.csv`, adds up marks times weights, prints PASS or FAIL and returns the total.",
        "how_md": (
            "Problem: reading, deciding and printing are mixed, so the pass rule cannot be tested with plain data. "
            "Change: a function that takes marks and weights and returns the total, and a thin outer function "
            "that reads the file and prints."
        ),
    },
    {
        "twist_md": "The function wraps the reading in a bare `except:` and returns `-1` on failure.",
        "how_md": (
            "Problem: every failure becomes the same silent `-1`, which a caller can add or average like a real "
            "value. Change: catch only `OSError` and `ValueError`, and let the outer layer print the reason to "
            "stderr and exit non-zero."
        ),
    },
    {
        "twist_md": "A parking function holds `60`, `2.50` and `1.80` inside its `if`.",
        "how_md": (
            "Problem: numbers with no name, so nobody can say what they are. Change: named constants such as "
            "`FREE_MINUTES`, so a rate change is made once, in one place."
        ),
    },
    {
        "twist_md": "A nested `if` pyramid, or a comment above each line that says what the line does.",
        "how_md": (
            "Use guard clauses, or give the condition a name such as `is_wanted`. A comment that explains what the "
            "code does is a failure of naming: rename instead."
        ),
    },
]

TRAPS = [
    "\"The names are bad.\" On its own it is an opinion. Quote the identifier and say what the reader must guess.",
    "\"It cannot be tested because it prints.\" Here the function returns the total, so a test can still check it. "
    "His reason is that every call also prints, so a test or another report gets output it did not ask for.",
    "\"Add comments.\" The course rule is that a comment explaining what the code does is a failure of naming. "
    "The fix is a name.",
    "Two bad names are one problem, and a change with no problem next to it earns little. Pick two different "
    "kinds and pair every change.",
]

SAY = (
    "- \"It adds up ..., prints the total and returns it.\" One sentence, what comes out.\n"
    "- \"`r[2]` hides which column is the category, so a teammate must guess.\" A tuple is a missing type.\n"
    "- \"It prints as well as calculating, so every call also prints.\" Computation is not output.\n"
    "- \"`\"food\"` is hard-coded, so another category needs a copy of the function.\"\n"
    "- \"I would ..., which fixes ...\" for every change, in words."
)

PRACTICE = [
    "sample-paper-q41",
    "clean-code-q17",
    "sample-paper-q23",
    "clean-code-q24",
    "core-shell-failing-q13",
]

SHORT_ANSWERS = {
    "clean-code-q17": {
        "1": "It counts the expenses whose amount, the fourth item of the tuple, is over 100, prints the count and "
        "returns it.",
        "2": "The names say nothing: `check`, `r`, `n` and `r[3]` make the reader trace the code to learn that "
        "`r[3]` is the amount, and the comment only repeats the `if`. It also prints as well as counting, so "
        "every caller or test gets output it did not ask for.",
        "3": "Rename it after what it returns, such as `count_large_expenses`, and use an `Expense` dataclass so "
        "`r[3]` becomes `expense.amount`: that fixes the names and the comment can go. Name the 100 and move the "
        "`print` to the caller so the function only returns the count: that fixes the mixed jobs.",
    },
    "clean-code-q24": {
        "1": "It computes the totals and prints them but returns nothing, so a test has no value to assert on: the "
        "numbers exist only as text on the screen.",
        "2": "Split it in two. A function such as `category_totals` takes the expenses and returns the dictionary of "
        "totals without printing, and the caller prints. That follows \"computation is not output\".",
        "3": "Give the totals function the three expenses and check that it returns 66.82 for transport and 33.02 "
        "for dining. No file and no printed output are involved.",
    },
    "core-shell-failing-q13": {
        "1": "It reads the file, sums one student's marks times weights, prints PASS (50 or more) or FAIL and returns "
        "the total; if reading fails it prints `error` and returns -1.",
        "2": "It mixes reading, deciding and printing, so the pass rule cannot be tested with plain data and a test "
        "cannot assert on a print. The bare `except:` turns any failure on the reading line into the same "
        "`error`, and the `-1` can be averaged like a real grade.",
        "3": "Make the weighted sum and the 50 rule pure functions on plain values. Keep the file, the printing and "
        "the error handling (specific exceptions, stderr, non-zero exit) in a thin shell. Tests: 80 and 60 at "
        "weight 0.5 give 70, and exactly 50 passes.",
    },
}

S7 = {
    "tid": "S7",
    "name": "Read code and say what is wrong (open)",
    "minutes": 25,
    "shape_md": (
        "Sample Q7: a short function in the expense-tracker style, then three numbered parts. What does it do "
        "(one sentence), name two problems a teammate would face, and describe in words how you would change it, "
        "saying which problem each change solves. Expect one open question of this shape, with different code."
    ),
    "one_md": (
        "Say what the code does, name two problems with the line they sit on and what a teammate cannot do "
        "because of it, then pair every change with the problem it fixes."
    ),
    "sample": {
        "qnum": "Q7",
        "kind": "open",
        "question_md": QUESTION,
        "parts": [
            "In one sentence, what does this function do?",
            "Name two problems a teammate would face when reading, testing or changing it.",
            "Describe (in words, do not write code) how you would change it, and which of the two problems each "
            "change solves.",
        ],
        "his_answer_md": HIS_ANSWER,
        "decoded_md": DECODED,
    },
    "spot_md": SPOT,
    "basics": BASICS,
    "checks": CHECKS,
    "method": METHOD,
    "worked": WORKED,
    "twists": TWISTS,
    "traps": TRAPS,
    "say_md": SAY,
    "practice": PRACTICE,
    "short_answers": SHORT_ANSWERS,
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "S7.json"
    with out.open("w", encoding="utf-8") as handle:
        json.dump(S7, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    print(f"wrote {out}")
