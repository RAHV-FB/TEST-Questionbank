"""Generator for CRAM/types/T03.json: exercise type T03, Clean-code problems.

Run: python3 types/src/T03.py   (from the CRAM folder, or anywhere)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CRAM = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(CRAM, "types", "T03.json")
POOLS = os.path.join(CRAM, "pools.json")

TID = "T03"

b1 = """Session 6 opens with two functions, `calc(c, i, d)` and `invoice_total(lines, tax_rate, discount_rate)`. Both return 163.35 for the lab's invoice, and neither has a bug. The slide asks which one you would dare to change. That is the course's argument: **code is read far more often than it is written**, so the cost of maintaining it is the cost of understanding it. The next reader is a teammate, or you in six months. Unclean code is not wrong code. It is expensive code.

The exam asks you to name what makes code expensive. Learn these seven, each with its cost and its fix in words.

| What you see | Problem | Cost to the next reader | Fix in words |
|---|---|---|---|
| `d`, `t`, `r`, `process`, `flag`, `utils.py` | Vague name | Must trace the code to learn what it holds or returns | Name it for what it holds or returns |
| `# add the amount` above `total += amount` | Comment saying *what* | Restates the line, goes stale | Rename, then delete the comment |
| a bare `0.85`, `40`, `100` | Magic number | Must guess what it means | Named constant |
| reads, validates, totals, prints | Several jobs | Hard to test, hard to change | One function per job |
| `print` inside a computation | Computation mixed with output | The result can only be looked at | Return it, print in the caller |
| `row[2]`, `e[3]` | A tuple is a missing type | Nobody knows what position 3 holds | `@dataclass(frozen=True)` |
| `if` inside `if` inside `if` | Pyramid | Hold every condition in your head | Guard clauses |

Missing type hints and ruff findings come with tool output, in the last block."""

b2 = """**Names.** One rule per kind of name.

| Kind | Bad | Better | Rule |
|---|---|---|---|
| Variable | `d`, `t`, `x` | `totals`, `expense` | says what it holds |
| Function | `calculate_totals` | `total_by_category` | says what it returns |
| Boolean | `flag` | `is_duplicate` | reads as a yes/no question |
| Module | `utils.py` | `storage.py` | says what it is for |

A function name is a promise about the return value. `get_total` promises a number; if it only prints, the caller gets `None` and crashes on `None > 100.0`. A function `check` that returns the refunds sounds like a yes or no; `refunds` says what comes back. Vague names (`process`, `calculate_totals`) and a grab-bag module (`utils.py`) are the usual wrong options. A name that needs a comment is not finished.

**Comments.** A comment that explains what the code does is a failure of naming: rename, then delete it. A comment that says why stays: a business rule, a workaround with its reason, a deliberate oddity. The test is whether it says something the code cannot. A comment that contradicts the code (`# round to whole euros` above `round(total, 2)`) needs fixing now. "Truth can only be found in one place: the code."

**Magic numbers.** A constant with no name. `print("-" * 40)` becomes `RULE_WIDTH = 40`, changed once, in one place. The name says what the number means. `FORTY = 40` says what it equals and is still magic. The same digits can mean two things: a VAT rate of `0.21` and a savings rate of `0.21` need two names."""

b3 = """**One function, one job.** In v0.1 `run()` did five things: it parsed the file, handled the failure, printed the header, totalled by category, and found and printed the largest. The test is to describe the function without the word "and". "Reads the file and validates and totals and prints" fails. The principle is Single Responsibility. The cost to name is that the function is hard to test (you need a real file and captured output) and hard to change (a layout change edits the code that reads the file). "It is too long" is not the cost.

After the rename of `calculate_totals`, commit `9d6c607` pulled reading and printing out of the calculation. Each job has a function:

| Function | Its one job |
|---|---|
| `read_expenses(path)` | returns the expenses in a file |
| `total_by_category(expenses, category, minimum)` | returns the total per category |
| `format_report(...)` | returns the lines of the report |
| `run(...)` | calls the others, and is the only one that prints |

**Computation is not output.** "A function that returns can be tested, reused and read on its own. A function that prints can only be looked at." If `show_totals` prints the totals and returns `None`, a test has nothing to assert on. A function that prints and returns, like sample Q7, can be tested, but every call also prints. Fix in words: return the value, let the caller print.

**Guard clauses, not pyramids.** Deal with the exceptions first and get out; what is left is the main path.

```python
if category != "" and expense.category != category:
    continue
if expense.amount < minimum:
    continue
totals[expense.category] += expense.amount
```"""

b4 = """**A tuple is a missing type.** In v0.1 an expense was a tuple, so `if e[3] < z:` cannot be read without finding where the tuple was built. Commit `017f926` named the concept:

```python
@dataclass(frozen=True)
class Expense:
    date: str
    merchant: str
    category: str
    amount: float
```

`e[3]` becomes `expense.amount`. A misspelt field is an error (`AttributeError ... Did you mean: 'category'?`), where a wrong tuple index runs on and reports a quiet wrong total. `frozen=True` means an `Expense` does not change after creation: assigning to a field raises `FrozenInstanceError`, so you build a new one instead.

**Type hints are contracts.** They say what goes in and what comes out, and people and mypy read them. Python does not check them while the program runs: a call with swapped arguments runs and returns a wrong answer until mypy reads the contract.

**ruff is the arbiter.** `ruff check` finds problems. `ruff format` fixes layout only and never removes an unused import. The rules live once in `pyproject.toml` and CI enforces them.

| Code | Meaning | Can it hurt a user? |
|---|---|---|
| `F401` | import never used | no |
| `E501` | line over the agreed 100 | no |
| `E722` | bare `except` catches every error | yes, a failure shows as "no data" |
| `F841` | value assigned, never used | maybe: the code may have forgotten to use it |

Read the code, read the message, fix the cause. `# noqa`, a looser `line-length` or deleting the flagged line are the careless answers. A refactoring keeps the output identical: `diff before.txt after.txt` prints nothing."""

q5 = """A function called `process(rows)` reads a file, validates each row, calculates totals and prints a report. Which clean-code problem does this describe best?

- a) The function name is too long
- b) The function does several jobs at once, so it is hard to test and to change
- c) The function repeats the same code in several places
- d) The function uses too many type hints"""

q7 = """**Q7: read code and say what is wrong**

```python
def process(rows):
    total = 0
    for r in rows:
        if r[2] == "food":
            total += float(r[1])
    print("Food total:", total)
    return total
```

1. In one sentence, what does this function do?
2. Name two problems a teammate would face when reading, testing or changing it.
3. Describe (in words, do not write code) how you would change it, and which of the two problems each change solves."""

data = {
    "tid": TID,
    "name": "Clean-code problems",
    "shape_md": (
        "Mirrors sample Q5 (a function described in a sentence: which clean-code problem is it?) and sample Q7 "
        "(read a short function, say what it does, name two problems, describe the changes in words). "
        "It appears as multiple choice about names, comments, jobs, tuples and ruff output, and as one 5–8 line open question."
    ),
    "minutes": 40,
    "one_md": "Name the clean-code problem you can point at in the code, say what it costs the next reader, and say in words how you would fix it.",
    "spot_md": (
        "- A short function (5–18 lines), or a one-sentence description of one, often called `process`, `check` or `get_total`.\n"
        "- Wording such as \"Which clean-code problem does this describe best?\", \"Name two problems a teammate would face\", "
        "\"Which name or comment would the course keep?\" or \"Which of these problems does it **not** have?\"\n"
        "- The tools are often green (`ruff check` and `mypy --strict` pass), so the answer is a design problem, not an error message.\n"
        "- A ruff finding (`F401`, `E501`, `E722`, `F841`), a traceback (`FrozenInstanceError`, `'NoneType'`) or a pytest block that is a clean-code problem in disguise.\n"
        "- In the open version the change is described in words. You never write code."
    ),
    "basics": [
        {"id": "T03-b1", "heading": "Why clean code, and the seven problems to name", "body_md": b1},
        {"id": "T03-b2", "heading": "Names, comments and magic numbers", "body_md": b2},
        {"id": "T03-b3", "heading": "One job, return instead of print, guard clauses", "body_md": b3},
        {"id": "T03-b4", "heading": "Tuples, type hints, ruff and the refactoring check", "body_md": b4},
    ],
    "checks": [
        {
            "id": "T03-c1",
            "q_md": "`calc(c, i, d)` from session 6 returns the right total for the lab's invoice. A teammate says it therefore has no clean-code problem. What is the course's reply?",
            "options": [
                "Agreed: code that returns the right answer is clean by definition",
                "It runs, but whoever changes it next must first decode `c`, `i`, `d` and `p[1]`, and that reading is the cost",
                "It will return wrong totals as soon as the list of lines gets long",
            ],
            "answer": 1,
            "why_md": "Unclean code is not wrong code, it is expensive code. The cost of maintaining code is the cost of understanding it, and `calc` charges that cost on every change.",
        },
        {
            "id": "T03-c2",
            "q_md": "Which of these comments would the course delete?",
            "options": [
                "`# add the amount` above `total += expense.amount`",
                "`# refunds are negative and finance nets them off` above `total += expense.amount`",
                "`# the bank's file can end with a short summary row` above `if len(row) == FIELDS_PER_ROW:`",
            ],
            "answer": 0,
            "why_md": "`# add the amount` restates the line, because `total` and `expense.amount` already say it: a failure of naming. The other two give a business rule and a workaround with its reason, which the code cannot say.",
        },
        {
            "id": "T03-c3",
            "q_md": "`show_totals(expenses)` prints the total per category and returns `None`. What is the main cost, in the course's terms?",
            "options": [
                "It runs slower, because `print` is a slow call",
                "mypy refuses to check any function that prints",
                "A test has no returned value to check, so the function can only be looked at",
            ],
            "answer": 2,
            "why_md": "Computation is not output. A function that returns can be tested, reused and read on its own. The fix in words: one function returns the totals and the caller prints them.",
        },
        {
            "id": "T03-c4",
            "q_md": "What does `frozen=True` on the `Expense` dataclass give you?",
            "options": [
                "Python checks that each field has the right type when an `Expense` is created",
                "An `Expense` cannot change after creation: assigning to a field raises `FrozenInstanceError`",
                "The program runs faster than it did with tuples",
            ],
            "answer": 1,
            "why_md": "Frozen means it does not change after creation, so an expense stays as it was read from the file. Python does not check type hints while running, and the course never argues for dataclasses on speed.",
        },
        {
            "id": "T03-c5",
            "q_md": "CI is red on `E501 Line too long (112 > 100)` the evening before a deadline. Which response does the course want?",
            "options": [
                "Add `# noqa` to the line so that CI turns green",
                "Raise `line-length` in `pyproject.toml` until the line fits",
                "Shorten or split the line: the limit was agreed once and CI enforces it for everyone",
            ],
            "answer": 2,
            "why_md": "The slide's method is read the code, read the message, fix the cause. The cause is a line over the agreed 100 characters. `# noqa` and a looser limit make the tool quiet and fix nothing.",
        },
    ],
    "method": [
        "Read the code and any output before the options. Say in one sentence what it does, and trust the code over the function name and over any comment.",
        "Run the \"and\" test on that sentence. Count the verbs (reads, validates, totals, prints). More than one job is the Single Responsibility problem. Note whether the function prints, returns, or does both.",
        "Walk the seven problems and point at the exact token for each: a vague name, a comment that restates, a bare number, `row[2]`, a `print`, nested `if`s. Only count what you can point at.",
        "Multiple choice: pick the option the artefact shows best. Cross out options that are true of some other code (duplication, too many hints, a different file format). In a \"which does it not have\" question, tick each option against the code. When two real problems are listed, choose the one the description or the output points at.",
        "Open question: for each problem write its name, the cost to a teammate, and the fix in words, and say which fix solves which problem. Two precise problems beat five vague ones. Do not write code.",
        "Tool output: read the code, read the message, fix the cause. Decide which finding changes what the program does. Refuse `# noqa`, a looser limit and `# type: ignore` as ways to get CI green.",
    ],
    "worked": [
        {
            "title": "Sample Q5: name the problem",
            "question_md": q5,
            "steps_md": [
                "Underline the verbs in the description: reads, validates, calculates, prints. Four verbs joined by \"and\".",
                "Apply the course's test: describe it without the word \"and\". You cannot, so the function has several jobs.",
                "Check the other options against the description. a) `process` is short, not long. c) Nothing is repeated. d) Hints are not mentioned.",
                "Choose b, and keep the consequence for an open answer: to test the totals you need a real file and captured output, and a change to the layout edits the code that does the arithmetic.",
            ],
            "answer_md": "**b)** The function does several jobs at once, so it is hard to test and to change. This is the Single Responsibility Principle. The course's own fix is commit `9d6c607`, which separated reading and printing from the calculation: `read_expenses`, `total_by_category` and `format_report` each have one job, and only `run` prints.",
        },
        {
            "title": "Sample Q7: read code and say what is wrong",
            "question_md": q7,
            "steps_md": [
                "Part 1: trust the code. It adds the second field (`r[1]`) of the rows whose third field (`r[2]`) is \"food\", prints the total and returns it. Three facts: which rows, what is added, what happens to the result (printed and returned).",
                "Part 2: walk the checklist and keep the two problems with the clearest cost. Names: `process`, `r[1]` and `r[2]` say nothing, so a teammate must guess which field is the amount (a tuple is a missing type). Output: the `print` runs on every call, so the total cannot be reused quietly and the wording is welded to the arithmetic. Do not write \"a test cannot check the total\", because the function returns it. The hard-coded \"food\" is a third problem if you have room.",
                "Part 3: give one change per problem and link them. A dataclass with named fields and a name that says what it returns (`food_total`) solves the reading problem. Removing the `print` and letting the caller print solves the output problem.",
                "Length check: this is about six handwritten lines. Stop there.",
            ],
            "answer_md": (
                "1. It adds up the amounts (second field) of the rows whose third field is \"food\", prints that total and returns it.\n"
                "2. Reading: `process`, `r[1]` and `r[2]` say nothing, so a teammate must guess which field is the amount. Changing: the `print` runs on every call, so the total cannot be reused quietly and changing the wording means editing the arithmetic.\n"
                "3. Use an `Expense` dataclass so `r[1]` becomes `expense.amount`, and a name that says what it returns, such as `food_total`: that solves the reading problem. Remove the `print` and let the caller print the result: that solves the output problem."
            ),
        },
    ],
    "twists": [
        {
            "twist_md": "A negative question: \"Which of these problems does this function **not** have?\" The function has a bare `25`, a `# loop over the expenses` comment and a `print` inside the loop.",
            "how_md": "Treat the four options as a checklist and tick each against the code, pointing at the line. The function usually has three of them. The one you cannot point at is the answer (here, a name that does not say what it returns, because `count_large_expenses` returns a count).",
        },
        {
            "twist_md": "The tools are green and the function has one job. `ruff check` and `mypy --strict` pass, and you cannot split the description with \"and\". Example: `check(expenses)` returns the negative expenses.",
            "how_md": "Then \"several jobs\" is the distractor. Look at the name. `check` sounds like a yes/no question and the function returns a list, so a caller who writes `if check(expenses):` is misled. The fix is a name that says what it returns, such as `refunds`. Passing tools say nothing about design.",
        },
        {
            "twist_md": "A comment that contradicts the code: `# round to whole euros` above `total = round(total, 2)`.",
            "how_md": "Trust the code, not the comment. The code rounds to two decimals. Name the lying comment as a problem, and in the fix first find out which was meant, cents or whole euros, then delete the comment. \"Change the comment to say two decimals\" is only half right, because the code may be the wrong one.",
        },
        {
            "twist_md": "A teammate's commit `Remove comments (a comment is a failure of naming)` deletes the bank-export comment above `if len(row) == FIELDS_PER_ROW:`.",
            "how_md": "Ask whether the comment says something the code cannot. It gives the reason for the check (the bank's file can end with a short summary row), so it stays. Applying the rule blindly is the trap; the slide says never to follow it blindly. Putting the reason in the commit message does not help the next reader of the file.",
        },
        {
            "twist_md": "Three ruff findings (`F401`, `E722`, `E501`) and a teammate who wants `# noqa` on all three and a longer `line-length` \"to get CI green before the deadline\".",
            "how_md": "Say which finding changes behaviour (`E722`: a missing file or a bug inside the `try` becomes an empty list and the user sees \"no data\"). Refuse to silence the referee: the rules were agreed once and CI enforces them for everyone. The real fixes are small: delete the import, catch only `OSError` and `ValueError`, split the line.",
        },
        {
            "twist_md": "A guard-clause rewrite is called a refactoring, but with an empty `category` the two versions give different totals. Or `diff before.txt after.txt` prints a changed line.",
            "how_md": "A refactoring keeps the output identical. Compare the conditions on the odd input (an empty category), or read the `<` and `>` lines of the `diff`. If the output changed, it is not a refactoring yet: undo the step, or make the behaviour change its own commit with its own message.",
        },
        {
            "twist_md": "A traceback from a frozen dataclass: `FrozenInstanceError: cannot assign to field 'amount'`, raised by a function that rounds every amount in place.",
            "how_md": "The type is doing its job, so do not remove `frozen=True`. Build a new `Expense` with the rounded amount, collect them in a new list and return it. Name the function for what it returns (`rounded_expenses`) and change the return type from `None`.",
        },
        {
            "twist_md": "A pytest block: `TypeError: 'NoneType' object is not subscriptable`, with the correct totals printed under \"Captured stdout call\".",
            "how_md": "The computation is right and was only printed. Computation is not output: return the value and print in the caller. Do not change the test to expect `None`, and do not compare printed text.",
        },
    ],
    "traps": [
        "\"It is too long\" or \"the name is too long\" is not the problem. The problem is several jobs, and you name the cost: hard to test and hard to change.",
        "\"Comments are bad, delete them all.\" A comment that says why (a business rule, a workaround with its reason, a deliberate oddity) stays. Only the comment that restates the line goes, after you have renamed.",
        "Naming the value (`FORTY = 40`) or searching and replacing `0.21` does not fix a magic number. The name must say what the number means, and the same digits can mean two things (VAT and a savings rate), while `1.21` hides the VAT rate from the search.",
        "Trusting the comment or the function name over the code. The code is the truth: read what it does first, then judge the comment and the name.",
        "A function called `get_total` that only prints returns `None`. A function name promises what it returns, and a boolean reads as a yes/no question (`is_paid`, not `payment`).",
        "\"An empty `diff` proves the refactoring is correct.\" It proves the same output for that command and that data only. A change that alters the output is not a refactoring, even when it is an improvement: give it its own commit.",
        "Silencing the referee: `# noqa`, a longer `line-length`, `# type: ignore`, deleting the line a finding points at, or renaming to `_discounted`. Read the code, read the message, fix the cause. `ruff format` fixes layout only.",
        "\"Type hints are checked when the program runs.\" Python ignores them, so a call with swapped arguments runs and returns a wrong answer until mypy reads the contract. `Any` is a hint in form only.",
    ],
    "say_md": (
        "- \"The function does several jobs (Single Responsibility), so it is hard to test and hard to change.\"\n"
        "- \"I cannot describe it without the word 'and'.\"\n"
        "- \"Computation is not output: it should return the value and the caller should print it. A function that prints can only be looked at.\"\n"
        "- \"A tuple is a missing type: `row[2]` says nothing. Use a `@dataclass(frozen=True)` with named fields.\"\n"
        "- \"A comment that explains what the code does is a failure of naming: rename, then delete it. A comment that says why stays.\"\n"
        "- \"A variable says what it holds, a function what it returns, a boolean reads as a yes/no question, a module says what it is for.\"\n"
        "- \"A magic number: give it a name that says what it means, once, in one place.\"\n"
        "- \"Guard clauses: deal with the exceptions first and get out; what is left is the main path.\"\n"
        "- \"Code is read far more often than it is written; the cost of maintaining it is the cost of understanding it.\"\n"
        "- \"Refactoring: the structure changes and the output stays identical (`diff` prints nothing).\"\n"
        "- \"Read the code, read the message, fix the cause. The linter is the arbiter and CI enforces it.\"\n"
        "- \"Type hints are contracts read by people and by mypy; Python does not enforce them while running.\""
    ),
    "practice": [
        "clean-code-q01",
        "clean-code-q15",
        "clean-code-q19",
        "clean-code-q05",
        "clean-code-q08",
        "clean-code-q49",
        "sample-paper-q23",
        "clean-code-q30",
        "clean-code-q33",
        "clean-code-q17",
        "clean-code-q13",
        "clean-code-q27",
        "clean-code-q34",
        "clean-code-q18",
    ],
}

# Self-check: every practice id must exist in pools[TID].
with open(POOLS, encoding="utf-8") as handle:
    pool_ids = {q["id"] for q in json.load(handle)["pools"][TID]}
missing = [qid for qid in data["practice"] if qid not in pool_ids]
assert not missing, f"practice ids not in pools[{TID}]: {missing}"
assert len(set(data["practice"])) == len(data["practice"]), "duplicate practice ids"

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(data, handle, ensure_ascii=False, indent=1)
    handle.write("\n")
print("wrote", OUT)
