"""Two small, complete fixtures for `build_cram.py --example` and the tests.

`types/_example6.json` is S3 (an mcq stop with a sample block) and `types/_example6_open.json` is S7
(an open stop: lined sample, open practice with `short_answers`). They also show the shape of a type
file for the authors of the real S*/P* files. The practice ids are real bank questions.

Run: uv run --project ../../../study-site python types/src/_example6.py
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

S3_QUESTION = (
    "`mypy --strict` reports this error on the code below:\n\n"
    "```python\n"
    "def find_expense(expenses: list[Expense], expense_id: int) -> Expense | None: ...\n\n"
    "expense = find_expense(expenses, 3)\n"
    "total += expense.amount\n"
    "```\n\n"
    "```text\n"
    'error: Item "None" of "Expense | None" has no attribute "amount"  [union-attr]\n'
    "```\n\n"
    "Which fix is most appropriate?"
)

s3 = {
    "tid": "S3",
    "name": "A mypy error: which fix?",
    "minutes": 15,
    "shape_md": (
        "Sample Q3. One `mypy --strict` error under a few lines of code, and four fixes. "
        "Expect one of these on the paper, with a different error."
    ),
    "one_md": "Read the bracket at the end of the error, name the kind, and pick the fix that removes the cause.",
    "sample": {
        "qnum": "Q3",
        "kind": "mcq",
        "question_md": S3_QUESTION,
        "options": [
            "Add `# type: ignore` to the line",
            "Handle the `None` case before using `expense.amount`",
            "Change the return type of `find_expense` to `Any`",
            "Delete the type annotations from the function",
        ],
        "answer": 1,
        "his_answer_md": (
            "**b.** The error says the value can be None. Handle that case. `# type: ignore` and "
            "`Any` hide the problem and keep the crash. Removing annotations makes the checker blind."
        ),
        "decoded_md": (
            "- The pattern: one error line, one fix to pick. The bracket `[union-attr]` says "
            '"this can be missing".\n'
            "- b is right because it removes the cause. After a `None` check the crash cannot happen.\n"
            "- a, c and d are the careless moves. They silence mypy, give up on the value, or "
            "switch the checker off. The crash stays.\n"
            "- His reason is three short sentences: what the error says, what to do, why the "
            "others fail. That is the length to aim for."
        ),
    },
    "spot_md": (
        "- One `error:` line from `mypy --strict`, with a code in square brackets.\n"
        "- Four fixes, and two of them are `# type: ignore` or `Any`.\n"
        '- The question says "most appropriate" or "which fix".\n'
        "- On a different topic: the same error on a `dict.get`, a search that finds nothing, "
        "or an optional argument."
    ),
    "basics": [
        {
            "id": "S3-b1",
            "heading": "Four kinds of mypy error, four honest fixes",
            "body_md": (
                "mypy reports one line per problem. The code in square brackets tells you the kind, "
                "and the kind tells you the fix.\n\n"
                "| What mypy says | Kind | Honest fix |\n|---|---|---|\n"
                "| `Function is missing a type annotation` | missing annotation | write the types in the signature |\n"
                '| `Item "None" of ... has no attribute` | None not handled | check for `None` before using the value |\n'
                "| `Incompatible types in assignment` | types disagree | make both sides the same type, such as `0.0` for a float |\n"
                '| `Returning Any from function declared to return "float"` | Any leaks in | give the value a real type, such as `float(...)` |\n\n'
                "The careless moves are the same every time. `# type: ignore` hides the line. "
                "`Any` says you gave up on the value. Deleting annotations switches the checker off. "
                "None of them removes the crash, so none of them is the fix."
            ),
        }
    ],
    "checks": [
        {
            "id": "S3-c1",
            "q_md": 'mypy says `Item "None" of "Expense | None" has no attribute "amount"`. What can happen when the program runs?',
            "options": [
                "Nothing: it is only a style warning",
                "An `AttributeError` when no expense is found",
                "The program prints the wrong amount",
            ],
            "answer": 1,
            "why_md": "If `find_expense` returns `None`, asking it for `.amount` raises `AttributeError`.",
        },
        {
            "id": "S3-c2",
            "q_md": "Which of these removes the cause of the error?",
            "options": [
                "`# type: ignore` on the line",
                "An `if expense is None` check before the line",
                "Changing the return type to `Any`",
            ],
            "answer": 1,
            "why_md": "Only the check makes the crash impossible. The other two keep it and hide it.",
        },
    ],
    "method": [
        "Read the error line and the bracket at the end. Say the kind in your own words.",
        "Ask what could go wrong when the program runs: a `None`, a wrong type, a missing hint.",
        "Reject the careless options: `# type: ignore`, `Any`, deleting annotations, upgrading.",
        "Pick the option that removes the cause, and say why in one sentence.",
    ],
    "worked": [
        {
            "title": "The same shape on another topic",
            "question_md": (
                "`mypy --strict` reports this error:\n\n"
                "```python\ntotal = 0\nfor expense in expenses:\n    total += expense.amount\n```\n\n"
                "```text\nerror: Incompatible types in assignment (expression has type \"float\", "
                'variable has type "int")  [assignment]\n```\n\n'
                "Which fix is most appropriate?\n\n"
                "- a) Add `# type: ignore`\n"
                "- b) Start the total at `0.0`\n"
                "- c) Declare `total: Any`\n"
                "- d) Remove the type hints from the file"
            ),
            "steps_md": [
                "The bracket says `assignment`: the variable was an `int` and now receives a `float`.",
                "a, c and d silence or switch off the check. The types still disagree.",
                "b makes the variable a `float` from the start.",
            ],
            "answer_md": "**b.** The amounts are floats, so `0.0` makes both sides agree. The other options hide the mismatch.",
        }
    ],
    "twists": [
        {
            "twist_md": 'The error is `Missing positional argument` or `Function is missing a type annotation`.',
            "how_md": "Name the kind first. A missing annotation is fixed in the signature, not with `# type: ignore`.",
        },
        {
            "twist_md": "The return type of `find_expense` is `Expense`, and the fix offered is `if expense is None`.",
            "how_md": "That check is dead code. Say the declared type already promises a value.",
        },
        {
            "twist_md": "One option is `Optional[Expense]` on the caller's variable.",
            "how_md": "It declares the problem instead of handling it. The crash stays.",
        },
    ],
    "traps": [
        "`# type: ignore` is tempting because CI goes green. The crash stays, and now nobody sees it.",
        "`Any` feels like a fix. It means mypy stops checking that value.",
        "Deleting the annotations makes the error disappear and the checker blind.",
    ],
    "say_md": (
        "- the error says the value can be `None`, so handle that case\n"
        "- `# type: ignore` and `Any` hide the problem and keep the crash\n"
        "- name the kind: missing annotation, None not handled, types disagree, Any leaks in"
    ),
    "practice": [
        "refactor-types-q30",
        "refactor-types-q28",
        "refactor-types-q29",
        "refactor-types-q17",
        "refactor-types-q33",
    ],
}

S7_CODE = (
    "```python\n"
    "def process(rows):\n"
    "    total = 0\n"
    "    for r in rows:\n"
    '        if r[2] == "food":\n'
    "            total += float(r[1])\n"
    '    print("Food total:", total)\n'
    "    return total\n"
    "```"
)

s7 = {
    "tid": "S7",
    "name": "Read code and say what is wrong (open)",
    "minutes": 25,
    "shape_md": (
        "Sample Q7. A short function, then three parts: what it does, two problems, and how you "
        "would change it in words. About 5 to 8 lines in all."
    ),
    "one_md": "Name the problem, say what a teammate cannot do because of it, and pair each fix with its problem.",
    "sample": {
        "qnum": "Q7",
        "kind": "open",
        "question_md": S7_CODE,
        "parts": [
            "In one sentence, what does this function do?",
            "Name two problems a teammate would face when reading, testing or changing it.",
            "Describe (in words, do not write code) how you would change it, and which of the two problems each change solves.",
        ],
        "his_answer_md": (
            '1. It adds up the amounts of the rows whose third column is "food", prints the total, and returns it.\n'
            "2. Any two of:\n"
            "   - Names say nothing: `process`, `rows`, `r`, `r[2]`, `r[1]`. The reader must guess that column 2 is the category and column 1 the amount.\n"
            "   - It does two jobs, calculating and printing, so a test of the total also prints.\n"
            '   - "food" is hard-coded. Other categories need a copy of the function.\n'
            "   - It trusts the file: a short row or a non-numeric amount crashes with an unhelpful error.\n"
            "3. Give the function a descriptive name and name the columns (or use an Expense dataclass) to fix the unclear names. "
            "Pass the category as a parameter to fix the hard-coding. Move the print out to the caller so the function only returns the total. "
            "This fixes the two jobs."
        ),
        "decoded_md": (
            "- Part 1 is a plain reading: which rows, what it adds up, what it does with the result.\n"
            "- Part 2 wants two problems, each with its cost: guessing what `r[2]` holds, or a test that also prints.\n"
            "- Part 3 pairs a change with a problem. Naming the change alone earns half.\n"
            "- Do not write code in part 3. He asks for words.\n"
            "- Each part is one or two sentences. Always tie it to the line you mean."
        ),
    },
    "spot_md": (
        '- A code block under "read code and say what is wrong".\n'
        "- Three numbered parts: what it does, two problems, how to change it.\n"
        "- Tuples indexed by number, a `print` inside a calculation, a hard-coded value.\n"
        "- The same shape on a different function: a count, a filter, a report."
    ),
    "basics": [
        {
            "id": "S7-b1",
            "heading": "What counts as a problem",
            "body_md": (
                "He marks reasons, not terms. A problem is a thing in the code plus what it stops a "
                "teammate doing.\n\n"
                "- **Unclear names or positions** (`r[2]`): the reader must guess what a value holds. "
                "The fix is a descriptive name or a dataclass.\n"
                "- **Two jobs in one function** (calculating and printing): a test of the total also "
                "prints, and a new output format touches the calculation. The fix is to return the "
                "value and print in the caller.\n"
                "- **A hard-coded value** (`\"food\"`): another category needs a copy of the function. "
                "The fix is a parameter.\n"
                "- **Trusting the file**: a short row crashes with an unhelpful error.\n\n"
                "Pick two, and write the cost after each one."
            ),
        }
    ],
    "checks": [],
    "method": [
        "Part 1: say which rows, what it adds up and what it does with the result, in one sentence.",
        "Part 2: pick two problems you can point at in the code and add what each costs a teammate.",
        "Part 3: for each problem, one change in words, then the words 'this fixes' and the problem.",
        "Do not write code. Do not list a third problem you cannot explain.",
    ],
    "worked": [],
    "twists": [
        {
            "twist_md": "The function counts the rows whose fourth field is over 100.",
            "how_md": "Part 1 changes. Parts 2 and 3 stay: names, print inside the count, the bare `100`.",
        },
        {
            "twist_md": "Part 2 asks for one problem with reading and one with testing.",
            "how_md": "Choose the names for reading and the `print` for testing, and say so.",
        },
        {
            "twist_md": "Part 3 asks what you would test first.",
            "how_md": "Name a case in words, such as a file with no food rows, and the result you expect.",
        },
    ],
    "traps": [
        '"The names are bad" is a verdict. Say which names and what a teammate cannot do.',
        "Writing code in part 3 costs time and earns nothing extra.",
        "Naming a fix without the problem it solves earns half the marks.",
    ],
    "say_md": (
        "- it does X, prints it and returns it\n"
        "- a reader must guess what `r[2]` holds, so give the columns names\n"
        "- the print mixes the calculation with the output, so move it to the caller"
    ),
    "practice": [
        "clean-code-q17",
        "clean-code-q03",
        "clean-code-q14",
        "clean-code-q21",
    ],
    "short_answers": {
        "clean-code-q17": {
            "1": "It counts the expenses whose amount (`r[3]`) is over 100, prints the count and returns it.",
            "2": "The names `check`, `r`, `n` and `r[3]` say nothing, so a reader must trace the code. It also prints inside the count, so every caller gets output it did not ask for.",
            "3": "Rename it after what it returns and use named fields instead of `r[3]`: that fixes the names. Move the `print` to the caller: that fixes the output.",
        },
        "clean-code-q03": {
            "1": "`invoice_total`, because its names say what each value is, so I can see what to change. `calc` has to be decoded first.",
            "2": "That `i` is the tax rate and `d` the discount rate, and that `p[1] * p[2]` is price times quantity.",
            "3": "Both are correct, so the difference is cost: code is read far more often than written, and unclear names make every change slower.",
        },
    },
}


def write(name: str, data: dict[str, object]) -> None:
    out = HERE / name
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    write("_example6.json", s3)
    write("_example6_open.json", s7)
