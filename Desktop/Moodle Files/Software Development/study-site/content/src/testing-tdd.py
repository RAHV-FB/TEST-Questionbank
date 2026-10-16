"""Generator for content/testing-tdd.json (module M2, session 8: Testing and TDD).

Every tool output in this file was produced by running it (pytest 9.1.1, mypy 2.4.0, ruff 0.16.9,
pytest-cov 7.1.0, Python 3.13) in the work folder for this module; scratch path prefixes were
rewritten to project-relative paths. Run:  uv run python content/src/testing-tdd.py
"""

from __future__ import annotations

import json
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

MID = "testing-tdd"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def md(s: str) -> str:
    return textwrap.dedent(s).strip("\n")


def sid(n: int) -> str:
    return f"{MID}-s{n}"


def qid(n: int) -> str:
    return f"{MID}-q{n:02d}"


QUESTIONS: list[dict[str, Any]] = []


def common(
    n: int,
    qtype: str,
    level: str,
    skills: list[str],
    section: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    explanation: str,
    variant_of: str | None = None,
) -> dict[str, Any]:
    q: dict[str, Any] = {
        "id": qid(n),
        "type": qtype,
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "explanation_md": md(explanation),
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }
    if variant_of:
        q["variant_of"] = variant_of
    return q


def mcq(
    n: int,
    level: str,
    skills: list[str],
    section: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    right: tuple[str, str],
    wrongs: list[tuple[str, str]],
    pos: str,
    explanation: str,
    variant_of: str | None = None,
) -> None:
    assert len(wrongs) == 3
    q = common(
        n, "mcq", level, skills, section, source, origin, verified, stem, explanation, variant_of
    )
    options = [{"text_md": md(t), "correct": False, "why_md": md(w)} for t, w in wrongs]
    options.insert("abcd".index(pos), {"text_md": md(right[0]), "correct": True, "why_md": md(right[1])})
    q["options"] = options
    QUESTIONS.append(q)


def open_q(
    n: int,
    level: str,
    skills: list[str],
    section: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    parts: list[dict[str, Any]],
    lines: str,
    explanation: str,
    variant_of: str | None = None,
) -> None:
    q = common(
        n, "open", level, skills, section, source, origin, verified, stem, explanation, variant_of
    )
    q["parts"] = [
        {
            "label": str(i + 1),
            "prompt_md": md(p["prompt"]),
            "marks": p["marks"],
            "model_answer_md": md(p["model"]),
            "rubric": [md(r) for r in p["rubric"]],
            "weak_answers_md": md(p["weak"]),
        }
        for i, p in enumerate(parts)
    ]
    q["lines"] = lines
    QUESTIONS.append(q)


def sort_q(
    n: int,
    level: str,
    skills: list[str],
    section: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
) -> None:
    q = common(n, "sort", level, skills, section, source, origin, verified, stem, explanation)
    q["categories"] = [{"id": c, "label": label} for c, label in categories]
    q["items"] = [{"text_md": md(t), "category": c, "why_md": md(w)} for t, c, w in items]
    QUESTIONS.append(q)


# ---------------------------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------------------------

SECTIONS: list[dict[str, Any]] = []


def section(
    n: int,
    heading: str,
    body: str,
    key_points: list[str],
    source: str,
    check: list[int],
    exam_note: str | None = None,
) -> None:
    s: dict[str, Any] = {
        "id": sid(n),
        "heading": heading,
        "body_md": md(body),
        "key_points": [md(k) for k in key_points],
        "source_ref": source,
        "check": [qid(c) for c in check],
    }
    if exam_note:
        s["exam_note_md"] = md(exam_note)
    SECTIONS.append(s)


section(
    1,
    "Red, green, refactor: write the test first",
    """
    Test-driven development (TDD) turns the usual order round: you write the test before the code.
    The cycle has three steps, and you repeat it for every small piece of behaviour.

    1. **Red.** Write a test for behaviour that does not exist yet. Run it and watch it fail.
    2. **Green.** Write the smallest code that makes it pass. Not the cleverest: the smallest.
    3. **Refactor.** Clean the code up, with the test as your safety net. Run the tests again:
       they must still pass.

    The slide gives the reason in one line: "The test forces you to say what 'done' means before
    you can fool yourself." Writing the assertion first makes you decide what the function should
    return for a concrete input. Once the code exists, it is tempting to write a test that checks
    whatever the code happens to do, and that test can never disagree with it.

    **Watch it fail first.** A test you never saw fail has not shown that it can notice anything. It
    might call the wrong function, assert something that is always true, or never be found by
    pytest at all. The lab's troubleshooting table names the symptom: "The test passes but you did not see it
    fail". The fix is cheap: break the code on purpose once, watch the test notice, then put the
    code back.

    **Green is deliberately modest.** In the live demo the first passing version of
    `remove_duplicates` was a plain loop, and the slide says "Not elegant. Nobody asked for elegant
    yet." Elegance belongs to the refactor step, and refactoring is safe only because the tests are
    already there. Session 7 defined a refactoring as a change of structure that keeps the
    behaviour; with tests, "keeps the behaviour" becomes checkable: the same tests, unchanged,
    still pass.

    The lab's conventions: tests live in `tests/`, in files named `test_<something>.py`. Each test
    is a function whose name says what it checks, with `-> None`, because CI runs `mypy --strict`
    on `tests/` too.

    ```python
    def test_empty_basket_costs_nothing() -> None:
        assert basket_total([]) == 0.0
    ```
    """,
    [
        "Red: a test for behaviour that does not exist yet, seen failing. Green: the smallest code that passes. Refactor: clean up while the tests stay green.",
        "\"The test forces you to say what 'done' means before you can fool yourself.\"",
        "A test you never saw fail proves nothing: break the code once on purpose and watch it notice.",
        "Refactoring is safe because the same tests, unchanged, still pass.",
    ],
    "S8 slides 3–5; labs/08-tdd.md step 2 and troubleshooting",
    [1, 2],
    "Expect to explain why the test comes first, or to judge a teammate who wrote a test after the code and never saw it fail.",
)

section(
    2,
    "Arrange, Act, Assert, and reading a failure",
    """
    Every test in the course has the same three-part shape, **Arrange-Act-Assert**. In the slide's
    test, Arrange builds three expenses, Act calls the one function under test, and Assert compares
    the result with the answer you worked out by hand (clothing 40, dining 10 + 5 = 15, largest
    first):

    ```python
    from expense_tracker.report import Expense, total_by_category


    def test_totals_are_grouped_by_category() -> None:
        expenses = [
            Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
            Expense("2025-07-02", "Zara", "clothing", 40.0),
            Expense("2025-07-03", "Bar Ramon", "dining", 5.0),
        ]
        result = total_by_category(expenses, category="", minimum=0.0)
        assert result == [("clothing", 40.0), ("dining", 15.0)]
    ```

    Run it with `uv run pytest -q`: one dot per passing test, then `1 passed`. On failure, pytest
    shows the values on both sides of the `assert`. Read the diff: it usually tells you the bug.
    Here is the real output after someone changed the sort in `total_by_category`:

    ```text
    >       assert result == [("clothing", 40.0), ("dining", 15.0)]
    E       AssertionError: assert [('dining', 1...thing', 40.0)] == [('clothing',...ining', 15.0)]
    E         At index 0 diff: ('dining', 15.0) != ('clothing', 40.0)

    tests/test_totals.py:11: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_totals.py::test_totals_are_grouped_by_category - AssertionE...
    1 failed in 0.01s
    ```

    Read it bottom up: the last line says how many failed; the `FAILED` line names the file and the
    test; the `>` line is the assert that failed; the `E` lines compare the left side with the right
    side, in the order the assert wrote them. The course writes the result first
    (`assert result == expected`), so the left is what the code returned and the right is what the
    test expected. That comes from how the test is written: in `assert 95.0 == apply_discount(100.0)`
    the sides swap. Here both totals are right, but dining comes first: the code now sorts smallest
    first.

    **A failure says the test and the code disagree. It does not say which one is wrong.** In sample
    Q4 a teammate changes `apply_discount` and a test fails with `assert 90.0 == 95.0`. "The test
    was written first" does not make it right; "the function changed more recently" does not make it
    right either; rerunning changes nothing. You can't tell yet: check which of the two matches
    what the discount is supposed to be (the backlog item, the README, the product owner). If the
    test matches the rule, the change introduced a bug. If the rule changed on purpose, update the
    test in the same change so it documents the new rule.
    """,
    [
        "Arrange the data, Act by calling one function, Assert against an answer you worked out by hand.",
        "pytest shows both sides of a failed `assert` in the order the test wrote them; the course puts the result on the left and the expected value on the right.",
        "Read from the bottom: counts, then the `FAILED` line, then the `>` line, then the `E` diff.",
        "A failing test means code and test disagree; the specification decides which is wrong.",
    ],
    "S8 slides 6–7; sample question Q4",
    [4, 5],
    "Sample Q4 is the model: a failing test after a teammate's change, and the right answer is to check the specification, not to trust whichever changed first or last.",
)

section(
    3,
    "Floats, fixtures and parametrize",
    """
    Three pytest tools remove most of the friction in writing tests.

    **Floats: compare with `pytest.approx`.** `0.1 + 0.2 == 0.3` is `False`: neither 0.1 nor 0.2 can
    be stored exactly in binary, so the sum is a hair off. A test that adds two Bar Ramon meals fails
    on noise, not on a bug:

    ```text
    >       assert total == 30.3
    E       assert 30.299999999999997 == 30.3
    ```

    Write `assert total == pytest.approx(30.3)` instead: it accepts a tiny tolerance. Money in floats
    needs a tolerance. (Real money code uses `Decimal`; the slide says that is another course.)

    **Fixtures: shared set-up.** When several tests need the same data, put it in a function marked
    `@pytest.fixture`:

    ```python
    @pytest.fixture
    def expenses() -> list[Expense]:
        return [
            Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
            Expense("2025-07-02", "Zara", "clothing", 40.0),
        ]

    def test_category_filter(expenses: list[Expense]) -> None:
        result = total_by_category(expenses, category="dining", minimum=0.0)
        assert result == [("dining", 10.0)]
    ```

    A fixture is a function pytest calls for you. You never call it yourself: you ask for it by
    name in the test's arguments, and pytest passes in what it returns. Because the match is by
    name, a typo stops the test before it starts: `fixture 'expense' not found`, followed by a list
    of available fixtures that includes `expenses`.

    **`parametrize`: one test, many cases.** When the only difference between tests is the
    numbers, write the test once and give it a table:

    ```python
    @pytest.mark.parametrize(
        ("minimum", "expected"),
        [
            (0.0, [("dining", 15.0)]),
            (10.0, [("dining", 10.0)]),
            (100.0, []),
        ],
    )
    def test_minimum_filters_small_amounts(
        minimum: float, expected: list[tuple[str, float]]
    ) -> None:
        expenses = [Expense("d", "m", "dining", 5.0), Expense("d", "m", "dining", 10.0)]
        assert total_by_category(expenses, "", minimum) == expected
    ```

    pytest runs it once per row and reports each row as its own test, with the values in its id:
    `test_minimum_filters_small_amounts[0.0-expected0]`, `[10.0-expected1]` and `[100.0-expected2]`.
    A number appears as itself; a list appears as its argument name plus the row's position,
    counting from 0. When one row fails, the `FAILED` line carries that id, so you see exactly which case broke, and
    the other rows still run.
    """,
    [
        "`0.1 + 0.2 == 0.3` is `False`: compare money in floats with `pytest.approx`.",
        "A fixture is a function pytest calls for you; ask for it by naming it as a test argument.",
        "Fixtures are matched by name, so `fixture '...' not found` almost always means a typo.",
        "`parametrize`: one test, many cases, each reported separately with its values in the name.",
    ],
    "S8 slides 8–10; labs/08-tdd.md step 2",
    [10, 12, 48],
    "Expect real pytest output: a float diff, a fixture error or a failing parametrize row, and a question about what it means and what to change.",
)

section(
    4,
    "Choose edge cases on purpose",
    """
    The happy path (a normal input with a normal answer) is the test everybody writes. Bugs live
    elsewhere. The slide gives five questions to ask before writing a test:

    | Ask | Example in the expense-tracker |
    |---|---|
    | **Empty**: nothing in? | `total_by_category([], "", 0.0) == []` |
    | **Zero**: the boundary? | an amount exactly equal to `minimum` |
    | **Negative**: nonsense? | a refund |
    | **Duplicate**: twice? | `expenses.csv` has six exact duplicates |
    | **Missing**: not there? | a category nobody used |

    The rule behind the table: "Do not test what feels likely. Test what could break." Boundaries
    break most often. `<` against `<=` is a one-character change that flips the answer only for the
    value exactly on the line, so only a test on the line can catch it. That is why v0.4 checks a
    minimum of `10.0` against an expense of exactly `10.0` (kept) and a minimum of `10.01` (dropped).

    The v0.4 suite has an edge case for each row: `test_no_expenses_means_no_totals`,
    `test_minimum_keeps_amounts_equal_to_it`, `test_a_refund_reduces_its_category_total`, the
    `remove_duplicates` tests, and a category filter for `"nobody-used-this"`. Ties count too:
    `test_largest_expense_tie_goes_to_the_first` pins down which of two equal amounts wins.

    The same questions work for the group topics. The project brief says the topics with rules
    (change-making, pricing bands, weighted averages, fare zones) "are easy to get subtly wrong and
    easy to test". A gradebook needs a test at exactly the pass mark; a vending machine needs an
    exact payment, so no change; a parking lot needs a stay that ends exactly on the edge of a
    pricing band. Session 7's invoice lab asked you to write down the inputs that could break it (an
    empty list, a discount above 100%, a negative quantity, a price of zero): those become tests now.

    **Tests behave as documentation.** A name such as `test_minimum_keeps_amounts_equal_to_it`
    states a rule a teammate can read without opening the code, and unlike a comment it is checked
    every time CI runs. Checkpoint 2 asks for at least two tests aimed at an edge case, not the
    happy path.
    """,
    [
        "Empty, Zero (the boundary), Negative, Duplicate, Missing: ask all five before writing tests.",
        "\"Do not test what feels likely. Test what could break.\"",
        "Only a test exactly on a boundary can tell `<` from `<=`.",
        "A good test name states a rule, so the suite doubles as checked documentation.",
    ],
    "S8 slide 11; labs/08-tdd.md edge-case table; moodle/project-pages.md (choosing well)",
    [14, 16],
    "Expect a function from a group topic (gradebook, vending machine, parking) and a choice of which test is most likely to catch a bug; the boundary is usually the answer.",
)

section(
    5,
    "Live: one full cycle on remove_duplicates",
    """
    The demo started at tag `v0.3`: `report.py` was already a functional core (no `print`, no
    `sys.exit`) and `uv run pytest` said `no tests ran`. The data had a problem: `expenses.csv`
    contains six exact duplicate rows. The goal was `remove_duplicates(expenses)`. (The demo ends at
    `v0.4`; your group's tag for this work is `v0.2`.)

    **Red (commit `e1b96de`).** First five tests: an empty list gives an empty list; `[BAR, ZARA]`,
    with no duplicates, comes back unchanged; `[BAR, ZARA, BAR]` gives `[BAR, ZARA]`, the first one
    kept; the same merchant on another day is not a duplicate; three copies collapse to one. Then a
    stub, so the failure says something:

    ```python
    def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
        return expenses
    ```

    Without the stub the test file cannot import the function, and pytest stops with an
    `ImportError` during collection: no test runs and you learn nothing about behaviour. With the
    stub, the run is real:

    ```text
    FAILED tests/test_duplicates.py::test_an_exact_duplicate_is_removed_and_the_first_one_kept
    FAILED tests/test_duplicates.py::test_many_copies_of_one_expense_collapse_to_one
    2 failed, 3 passed in 0.01s
    ```

    Two fail; the others pass by luck, because returning the list unchanged is right whenever there
    are no duplicates. "Red is information, not a problem."

    **Green (commit `1e421bc`).** The smallest code that passes: remember what you have seen, and
    keep each expense the first time it appears.

    ```python
    def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
        seen: set[Expense] = set()
        unique: list[Expense] = []
        for expense in expenses:
            if expense not in seen:
                seen.add(expense)
                unique.append(expense)
        return unique
    ```

    "Not elegant. Nobody asked for elegant yet. All green."

    **Refactor (commit `d3df52b`).**

    ```python
    def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
        return list(dict.fromkeys(expenses))
    ```

    Dictionary keys are unique and dictionaries keep insertion order, so this keeps the first of
    each expense, in order. The tests did not change and still pass: that is what refactoring means.

    It works only because session 6 made `Expense` a `@dataclass(frozen=True)`. A set member or a
    dictionary key must be hashable. A frozen dataclass gets a hash computed from its fields, so two
    expenses with the same four values count as the same key. A plain `@dataclass` has no hash:
    every test that hashes an expense fails with `TypeError: unhashable type: 'Expense'`, and the
    seen-set version fails the same way. `mypy --strict` reports no issues; only the tests catch it.

    On the real file, `read_expenses("expenses.csv")` gives 420 rows and `remove_duplicates` leaves 414.
    """,
    [
        "A stub that returns something wrong makes the first failure about behaviour, not about an import.",
        "\"Red is information, not a problem\": with the stub two tests fail and three pass by luck.",
        "Seen-set (green) to `dict.fromkeys` (refactor): same tests, still green, so it is a refactoring.",
        "`frozen=True` makes `Expense` hashable; without it, sets and `dict.fromkeys` raise `TypeError`.",
        "420 rows become 414: six exact duplicates removed, first copy kept.",
    ],
    "S8 slides 12–16; expense-tracker e1b96de, 1e421bc, d3df52b",
    [18, 22],
    "The history is on the exam: read the three commits as red, green and refactor, and connect session 6's `frozen=True` to why the one-liner works.",
)

section(
    6,
    "The parts that touch the world: what is worth unit testing",
    """
    Not all code is equally worth unit testing. The diagram on slide 18 places code on two axes.
    Vertically, the **benefit** of a unit test, roughly how non-obvious the code is. Horizontally,
    the **cost** of a unit test, roughly how many dependencies it has (files, the command line,
    other modules).

    | | Low cost (few dependencies) | High cost (many dependencies) |
    |---|---|---|
    | **High benefit** (non-obvious) | Algorithms | Overcomplicated code: needs refactoring |
    | **Low benefit** (obvious) | Trivial code | Coordinators |

    - **Algorithms** make the decisions with few dependencies: `total_by_category`,
      `remove_duplicates`, a parking price for a duration, change-making. Test these thoroughly: it
      is cheap and it catches real bugs.
    - **Trivial code**: a constant, a dataclass with four fields. Little can go wrong, so a test
      gains little.
    - **Coordinators** only wire things together. The `report` command reads the file, calls the
      core and prints the lines. It has little logic of its own and many dependencies, so one or two
      edge tests are enough.
    - **Overcomplicated code**: important logic tangled with files and printing, like sample Q5's
      `process(rows)`. You do not test it as it is: you refactor it into an algorithm plus a
      coordinator, and the logic moves to the cheap quadrant.

    **Pure functions test themselves.** `total_by_category` takes a list and returns a list: no
    file, no setup, no clean-up. That is what session 7's functional core bought. If a function you
    want to test needs a file, ask: can I split the file reading out? Slide 27 turns it into a
    rule: "If your logic is tangled up with `print` or `open`, split it first. That is refactoring
    under test."

    Printing is the same problem. A function that prints its answer returns `None`, so the test has
    nothing to compare. Real output from a gradebook function that prints:

    ```text
    E       AssertionError: assert None == 'Ana: pass'
    E        +  where None = show_result('Ana', 50.0)

    tests/test_grades.py:5: AssertionError
    ----------------------------- Captured stdout call -----------------------------
    Ana: pass
    ```

    The right text was printed, not returned. Make the function return, and print in the shell.
    """,
    [
        "Benefit of a unit test is roughly how non-obvious the code is; cost is roughly how many dependencies it has.",
        "Algorithms: test thoroughly. Trivial code and coordinators: little or nothing. Overcomplicated code: refactor first.",
        "Pure functions test themselves: a list in, a list out, no file and no clean-up.",
        "You cannot assert on a print: make it return, and print in the shell.",
    ],
    "S8 slides 17–19 (slide 18 diagram, image-only-slides.md); slide 28",
    [24, 26],
    "Expect to place a piece of code on the diagram and say what to do about it, or to explain why a function that prints or opens a file is hard to test.",
)

section(
    7,
    "tmp_path, CliRunner and monkeypatch: testing the edge on purpose",
    r"""
    Your program does touch the world somewhere. Test that place on purpose, once or twice, with
    the tool made for it.

    **`tmp_path`: when you really do want a file.** Ask for the `tmp_path` fixture and pytest gives
    the test a fresh, empty directory and deletes it afterwards. The test writes exactly the file it
    needs, including the broken row it wants to see skipped (commit `f3d9870`):

    ```python
    def test_rows_that_are_not_four_fields_are_skipped(tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        csv_file.write_text(
            "date,merchant,category,amount\n"
            "2025-07-01,Bar Ramon,dining,10.00\n"
            "broken\n"
            "2025-07-02,Zara,clothing,40.00\n"
        )

        merchants = [expense.merchant for expense in read_expenses(str(csv_file))]

        assert merchants == ["Bar Ramon", "Zara"]
    ```

    Your real files are never touched, and the test passes on any machine.

    **`CliRunner`: the command line.** `typer.testing.CliRunner` runs your app inside the test and
    hands back a result with `exit_code`, `stdout` and `stderr`. Session 5's exit code, now checked
    by a machine:

    ```python
    def test_report_on_a_missing_file_exits_with_one_and_explains_on_stderr() -> None:
        result = runner.invoke(app, ["report", "nosuch.csv"])

        assert result.exit_code == 1
        assert "could not read nosuch.csv" in result.stderr
    ```

    **`monkeypatch`: change the environment for one test.** It sets the working directory, an
    environment variable or an attribute for this test only, and restores it afterwards. The `add`
    command writes `data/expenses.csv` relative to the folder it runs in, so the slide's test moves
    into `tmp_path` first; without that line, the test would write into your real `data/` folder.

    ```python
    def test_add_writes_into_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        runner.invoke(app, ["add", "Bar Ramon", "dining", "12.50"])
        assert (tmp_path / "data" / "expenses.csv").exists()
    ```

    **The Checkpoint 2 table (slide 23).**

    | Tool | Use it for | Counts as an I/O test |
    |---|---|---|
    | plain list | pure functions | no: most of your tests |
    | `tmp_path` | the one place you read or write a file | yes |
    | `CliRunner` | the command line: exit code, output | yes |
    | `monkeypatch` | the working directory, environment | yes |

    "CP2 allows one or two I/O tests, chosen on purpose. Eight tests that all need a file is the
    opposite of what we practised."

    Your group's template already came with `CliRunner` tests in `tests/test_cli.py`. The lab is
    explicit: they count towards your 8, but they are I/O tests, so they count against "mostly
    pure". Keep one or two, rewrite them for your own commands, and delete the rest once you have
    pure tests to replace them (lab 08, step 3).
    """,
    [
        "`tmp_path`: a fresh empty directory per test, deleted afterwards; real files never touched.",
        "`CliRunner`: run the app inside a test and assert on `exit_code`, `stdout`, `stderr`.",
        "`monkeypatch`: working directory, environment variables, attributes; set for one test, restored after.",
        "Most tests use plain lists; one or two I/O tests, chosen on purpose.",
    ],
    "S8 slides 20–23; expense-tracker f3d9870; labs/08-tdd.md step 3",
    [30, 33, 45],
    "Expect to choose the right tool for a described test, or to judge a suite against Checkpoint 2's third item.",
)

section(
    8,
    "Coverage is a map, and a pointer to properties",
    """
    Coverage measures which lines of your code ran while the tests ran. With the `pytest-cov`
    plugin (`uv add --dev pytest-cov`), the real report for the demo at `v0.4` is:

    ```console
    $ uv run pytest --cov=expense_tracker --cov-report=term-missing
    ...
    Name                              Stmts   Miss  Cover   Missing
    ---------------------------------------------------------------
    src/expense_tracker/__init__.py       0      0   100%
    src/expense_tracker/cli.py           33     14    58%   36-39, 49-58
    src/expense_tracker/report.py        62      0   100%
    ---------------------------------------------------------------
    TOTAL                                95     14    85%
    ```

    The useful column is **Missing**: lines no test ran. In `cli.py`, lines 36–39 are the normal
    path of `report` (compute, format, print) and 49–58 are the body of the `add` command. "Use it
    to find what you forgot." It is a pointer, which you then judge: on the slide-18 diagram both
    commands are coordinators (low benefit, high cost), and slide 23 allows one or two such tests,
    chosen on purpose.

    **Coverage is a map, not a score.** A line counts as covered when it ran, whether or not any
    assert checked what it produced. This test has no assert at all:

    ```python
    def test_largest_expense() -> None:
        expenses = [
            Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
            Expense("2025-07-02", "Zara", "clothing", 40.0),
        ]
        largest_expense(expenses)
    ```

    With `largest_expense` broken on purpose to return the smallest expense, it still reports
    `1 passed`, and it runs every line of the function. "100% coverage with weak assertions proves
    nothing. Never chase the number."

    **A pointer: property-based testing.** An example test checks one input you chose. A
    property-based test states something that must hold for every input, and the `hypothesis`
    library invents hundreds of inputs to try to break it:

    ```python
    from hypothesis import given, strategies as st

    @given(st.lists(st.floats(min_value=0, max_value=1e6)))
    def test_total_never_negative(amounts: list[float]) -> None: ...
    ```

    "Instead of examples, you state a property and the library invents hundreds of inputs. Not
    required. For the curious."
    """,
    [
        "Coverage lists the lines no test ran: a map of what you forgot.",
        "A covered line is a line that ran, not a result that was checked.",
        "100% coverage with weak assertions proves nothing. Never chase the number.",
        "Property-based testing: state a property, and `hypothesis` invents the inputs.",
    ],
    "S8 slides 24–25",
    [35, 37],
    "Expect a coverage report or a weak test that passes, and a question about what it does and does not prove.",
)

section(
    9,
    "The three that bite, the troubleshooting table and Checkpoint 2",
    """
    The demo's CI (commit `0e05065`, "Run ruff, mypy and pytest on every push") runs
    `uv sync --locked`, `ruff check`, `ruff format --check`, `mypy src tests` and `pytest` on a fresh
    Ubuntu machine. That machine is the referee for Checkpoint 2, so the problems that bite are the
    ones where your laptop and CI disagree.

    **The three that will bite** (slide 28):

    1. **`-> None` missing on a test.** `pytest` alone passes; strict mypy does not, and CI is red:

       ```text
       tests/test_duplicates.py:25: error: Function is missing a return type annotation  [no-untyped-def]
       tests/test_duplicates.py:25: note: Use "-> None" if function does not return a value
       ```
    2. **The function prints.** You cannot assert on a print. Make it return, and print in the shell.
    3. **Tests that need your laptop.** A test that reads `data/expenses.csv` passes only on your
       machine. The demo's `.gitignore` lists `data/`, so CI's fresh clone fails with
       `FileNotFoundError: [Errno 2] No such file or directory: 'data/expenses.csv'`. Use
       `tmp_path`, or build the data inside the test.

    **The lab's troubleshooting table:**

    | Symptom | What it means |
    |---|---|
    | `no tests ran`, exit code 5 | pytest found no test: file not in `tests/`, not named `test_*.py`, or function not named `test_*`. 5 is not 0, so CI is red |
    | `ModuleNotFoundError` for your package | Run `uv sync`, and use `uv run pytest`, not bare `pytest` |
    | A test passes locally and fails in CI | It reads a file that is only on your laptop. Build the data inside the test |
    | `assert 0.30000000000000004 == 0.3` | Floats. Use `pytest.approx(0.3)` |
    | The test passes but you did not see it fail | You skipped red. Break the code on purpose once and watch the test notice |
    | `fixture 'tmp_path' not found` | A typo in the argument name; pytest matches fixtures by name |
    | CI is green but `git tag` points at an older commit | Tag the commit CI approved: `git log --oneline` and tag that hash |

    **Checkpoint 2**, three binary items, marked at the `v0.2` tag: (1) at least 8 tests, all
    passing, CI green on the `v0.2` commit; (2) at least 2 tests aimed at an edge case, not the happy
    path; (3) most tests call pure functions with plain data, and at most one or two use `tmp_path`,
    `CliRunner` or `monkeypatch`, on purpose. "A missing tag means nothing to mark."
    """,
    [
        "Every test needs `-> None`: CI runs strict mypy on `tests/` as well as `src/`.",
        "`no tests ran` exits with 5, which is not 0: CI is red even though nothing failed.",
        "`ModuleNotFoundError` for your own package: `uv sync`, then `uv run pytest`.",
        "Passes on your laptop, fails in CI: the test reads a file only you have.",
        "CP2 is marked at the `v0.2` tag: the tagged commit itself must be green.",
    ],
    "S8 slides 27–29; labs/08-tdd.md troubleshooting; expense-tracker 0e05065",
    [39, 41],
    "Each row of the troubleshooting table is a ready-made multiple-choice question: the output, then 'what should you do next?'.",
)

# ---------------------------------------------------------------------------------------------
# Questions: section 1
# ---------------------------------------------------------------------------------------------

mcq(
    1, "core", ["concept"], 1, "S8 slide 5", "slides", "source",
    """
    You are adding `largest_expense` to your project using test-driven development. What does the
    **red** step ask you to do?
    """,
    (
        "Write a test for behaviour that does not exist yet, run it, and watch it fail",
        "Red is a test for behaviour that does not exist yet, seen failing. Watching it fail shows the test can notice the missing behaviour.",
    ),
    [
        (
            "Write the function first, then add a test that passes against it straight away",
            "That is testing after the fact: the test checks whatever the code happens to do, and you never see it fail.",
        ),
        (
            "Run the existing suite and fix whatever is already failing before writing anything new",
            "Red is not 'tests that happen to be failing'. It is the deliberate first failure of a new test for new behaviour.",
        ),
        (
            "Write the smallest code that makes the new test pass, even if it is not elegant",
            "That describes green, the step after red. You cannot make a test pass before it exists and has failed.",
        ),
    ],
    "b",
    """
    The cycle is red, green, refactor. Red: write a test for behaviour that does not exist yet and
    watch it fail. Green: the smallest code that passes. Refactor: clean up with the test as a
    safety net. Writing the test first "forces you to say what 'done' means before you can fool
    yourself", and seeing it fail is the proof that the test is able to notice the behaviour is
    missing. A test written after the code and never seen failing may be checking nothing.
    """,
)

mcq(
    2, "exam", ["judgement"], 1, "labs/08-tdd.md troubleshooting", "lab", "source",
    """
    A teammate writes `test_largest_expense_tie_goes_to_the_first` after `largest_expense` already
    exists. It passes on the first run, and they want to commit it and move on. Following the lab,
    what should they do first?
    """,
    (
        "Break `largest_expense` on purpose once, watch the test fail, then undo the break",
        "The lab's fix for 'the test passes but you did not see it fail': you skipped red, so make the code wrong once and watch the test notice.",
    ),
    [
        (
            "Run the test several more times, alone and with the whole suite, to make sure it passes every time",
            "A test that can never fail also passes every time. Rerunning a passing test adds no information.",
        ),
        (
            "Delete the test, because a test that passes on its first run is not testing anything",
            "Passing first time is not proof of a useless test, only of an unproven one. Deleting it throws away a check you could have verified in a minute.",
        ),
        (
            "Add more asserts to the test until one of them fails against the current code",
            "The goal is a test that fails when the code is wrong, not one that fails against correct code. Forcing red this way breaks a good test.",
        ),
    ],
    "d",
    """
    The lab's troubleshooting table lists exactly this symptom: "The test passes but you did not see
    it fail. You skipped red. Break the code on purpose once and watch the test notice." A test you
    never saw fail might assert something that is always true, call the wrong function or compare
    the result with itself. Making the code wrong for a moment (for example, letting the later of
    two tied expenses win) and seeing the test go red is the cheapest proof that it guards the rule
    its name promises. Then undo the change and commit.
    """,
)

# ---------------------------------------------------------------------------------------------
# Section 2
# ---------------------------------------------------------------------------------------------

mcq(
    3, "core", ["read-code"], 2, "S8 slide 6", "slides", "source",
    """
    ```python
    def test_totals_are_grouped_by_category() -> None:
        expenses = [
            Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
            Expense("2025-07-02", "Zara", "clothing", 40.0),
            Expense("2025-07-03", "Bar Ramon", "dining", 5.0),
        ]
        result = total_by_category(expenses, category="", minimum=0.0)
        assert result == [("clothing", 40.0), ("dining", 15.0)]
    ```

    Which description matches this test's Arrange, Act and Assert?
    """,
    (
        "Arrange builds the expenses, Act calls `total_by_category`, Assert checks the result against hand-worked totals",
        "That is the pattern: set up the input, call the one function under test, compare with an expected value you can check yourself.",
    ),
    [
        (
            "Arrange is the import line at the top of the file; Act builds the three expenses; Assert calls `total_by_category`",
            "Importing is not arranging, and building the data is not acting. The act is the call to the function under test.",
        ),
        (
            "Arrange calls `total_by_category`; Act stores its value in `result`; Assert prints the totals",
            "Calling the function is the act, and tests assert; they never print for a human to read.",
        ),
        (
            "All three happen on the last line, because that is the line pytest reports when it fails",
            "pytest reports the assert line, but Arrange, Act and Assert are three separate jobs spread over the test.",
        ),
    ],
    "a",
    """
    Arrange-Act-Assert gives every test the same readable shape. Arrange: the list of three
    expenses (Bar Ramon twice, Zara once). Act: one call to the function under test,
    `total_by_category(expenses, category="", minimum=0.0)`, stored in `result`. Assert: compare
    `result` with an answer you worked out by hand: clothing 40.0, dining 10.0 + 5.0 = 15.0, largest
    first. A reader sees at a glance what goes in, what is called and what should come out, and a
    failure points straight at the one call being tested.
    """,
)

mcq(
    4, "core", ["read-tool-output"], 2, "S8 slides 6–7", "slides", "run",
    """
    A teammate's commit touched the sorting line in `total_by_category`. The slide's test now fails:

    ```console
    $ uv run pytest -q
    F                                                                        [100%]
    =================================== FAILURES ===================================
    _____________________ test_totals_are_grouped_by_category ______________________

        def test_totals_are_grouped_by_category() -> None:
            expenses = [
                Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
                Expense("2025-07-02", "Zara", "clothing", 40.0),
                Expense("2025-07-03", "Bar Ramon", "dining", 5.0),
            ]
            result = total_by_category(expenses, category="", minimum=0.0)
    >       assert result == [("clothing", 40.0), ("dining", 15.0)]
    E       AssertionError: assert [('dining', 1...thing', 40.0)] == [('clothing',...ining', 15.0)]
    E         At index 0 diff: ('dining', 15.0) != ('clothing', 40.0)
    E         Use -v to get more diff

    tests/test_totals.py:11: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_totals.py::test_totals_are_grouped_by_category - AssertionE...
    1 failed in 0.01s
    ```

    What does the failure tell you?
    """,
    (
        "The totals are right, but the code now returns them smallest first and the test expects largest first",
        "Index 0 holds dining 15.0 where clothing 40.0 was expected, and the left list still ends with clothing 40.0: same values, reversed order.",
    ),
    [
        (
            "The dining total is wrong: the code returns 15.0 where the test expects 40.0",
            "This misreads the diff. Index 0 compares two different categories; dining 15.0 is the correct dining total.",
        ),
        (
            "The clothing expense was dropped, so the result has one item fewer than expected",
            "pytest would say the right side 'contains one more item'. The left side still shows clothing 40.0 at the end.",
        ),
        (
            "The test is out of date and should be rewritten to accept the order the code now returns",
            "A failure only says code and test disagree; it never says which one to change. Rewriting the test to match the code because the code changed last is the move sample Q4 warns against.",
        ),
    ],
    "d",
    """
    Read the `E` lines: the left side is `result`, what the code returned; the right side is what
    the test expected. "At index 0 diff: ('dining', 15.0) != ('clothing', 40.0)" says the first
    element differs, and the truncated left list still ends with `('clothing', 40.0)`. Both totals
    are right; their order is reversed. The change to the sort made it ascending. pytest showed both
    sides, and the diff told you the bug without opening a debugger: "Read the diff; it usually
    tells you the bug."
    """,
)

mcq(
    5, "exam", ["read-diff", "judgement"], 2, "Sample Q4; S8 slide 7", "teacher-variant", "run",
    """
    A teammate pushes this commit, with the message `Tidy pricing module`:

    ```diff
    -DISCOUNT_RATE = 0.05
    +DISCOUNT_RATE = 0.10
    ```

    CI goes red:

    ```text
    >       assert apply_discount(100.0) == 95.0
    E       assert 90.0 == 95.0
    E        +  where 90.0 = apply_discount(100.0)

    tests/test_totals.py:5: AssertionError
    FAILED tests/test_totals.py::test_total_with_discount - assert 90.0 == 95.0
    ```

    Before you edit either file, what is the most useful thing to do?
    """,
    (
        "Check the agreed discount (backlog item or product owner) against both numbers",
        "The failure only says the test (5%) and the code (10%) disagree. The specification decides which one is wrong.",
    ),
    [
        (
            "Revert the commit, because the test was in the repository first and so defines the behaviour",
            "Being first does not make a test right. If the rule really changed to 10%, the test is the out-of-date one.",
        ),
        (
            "Change the test to expect 90.0, because the teammate changed the rate on purpose",
            "Nothing says the rule changed: 'Tidy' describes cleaning up, not a new discount. Newer is not the same as right.",
        ),
        (
            "Rerun the suite, and if it fails again, mark the test as skipped for now",
            "The failure is deterministic: 100 times 0.9 is 90 every time. Skipping it hides a disagreement someone must settle.",
        ),
    ],
    "a",
    """
    This is sample Q4 with the diff visible. The test expects 5% off; the code now gives 10%. A
    failing test tells you they disagree, not which one is wrong, so "the test came first" and "the
    change is newer" are both guesses. The commit message makes it worse: `Tidy pricing module`
    hides a change of behaviour inside what claims to be a clean-up. Check the rule the team agreed
    (the backlog item, or the product owner) and only then decide: fix the code if the rule is
    still 5%, update the test in the same change if it really became 10%.
    """,
    variant_of="sample-paper-q04",
)

mcq(
    6, "hard", ["read-diff", "judgement"], 2, "Sample Q4; S8 slide 11 (zero: the boundary)", "teacher-variant", "run",
    """
    The backlog item says: *Orders of 100 EUR or more get 5% off.* A teammate pushes this change
    with the message `Simplify discount check`:

    ```diff
     def apply_discount(total: float) -> float:
    -    if total >= DISCOUNT_THRESHOLD:
    +    if total > DISCOUNT_THRESHOLD:
             return total * (1 - DISCOUNT_RATE)
         return total
    ```

    (`DISCOUNT_THRESHOLD` is `100.0` and `DISCOUNT_RATE` is `0.05`.) The suite now fails:

    ```text
    >       assert apply_discount(100.0) == 95.0
    E       assert 100.0 == 95.0
    E        +  where 100.0 = apply_discount(100.0)

    tests/test_totals.py:5: AssertionError
    FAILED tests/test_totals.py::test_total_with_discount - assert 100.0 == 95.0
    ```

    What can you conclude?
    """,
    (
        "The test matches the rule; the change broke the boundary at exactly 100 EUR",
        "The rule says 'or more', so 100.0 must be discounted to 95.0. Changing `>=` to `>` excludes exactly that value.",
    ),
    [
        (
            "You can't tell yet: you would need to find out which of the two matches the discount rule",
            "Here you can tell, because the rule is given in the backlog item and the test agrees with it. 'Check the spec' is the method, and the spec is right there.",
        ),
        (
            "The test is wrong, because exactly 100 EUR is a rare order and tests should use typical amounts",
            "Typical amounts are the happy path. The edge-case table says to test the boundary, because that is where `>` and `>=` differ.",
        ),
        (
            "Both are right: the difference is float rounding, so the test should compare with `pytest.approx`",
            "A 5 EUR gap is not float noise. `pytest.approx` would still fail, and it should.",
        ),
    ],
    "b",
    """
    Sample Q4's lesson is "you can't tell from the failure alone; check the specification". This
    time the specification is in front of you: 100 EUR *or more* gets 5% off, so
    `apply_discount(100.0)` must be 95.0. The test agrees with the rule; the code no longer does.
    Changing `>=` to `>` looks like a harmless simplification, and for every amount except exactly
    100.0 it is. That is why the edge-case table says "Zero: the boundary?" and why a test sitting
    exactly on the threshold is the one that catches it. Fix the code, keep the test.
    """,
    variant_of="sample-paper-q04",
)

mcq(
    7, "hard", ["judgement"], 2, "Sample Q4; S8 slide 11 (tests as documentation)", "teacher-variant", "run",
    """
    At the sprint review the product owner changes the rule, and the backlog item now reads:
    *Members get 10% off (was 5%).* Your teammate implements it in a commit called
    `Raise member discount to 10%`, changing only `DISCOUNT_RATE`. CI goes red:

    ```text
    FAILED tests/test_totals.py::test_total_with_discount - assert 90.0 == 95.0
    1 failed in 0.01s
    ```

    What is the right fix?
    """,
    (
        "Update the test to expect 90.0, with a commit message saying the rule changed",
        "The rule changed on purpose and the code follows it; the test still describes the old rule, so it is the test that is out of date.",
    ),
    [
        (
            "Revert the commit, because the test was written first and therefore defines the behaviour",
            "Tests encode the specification. When the product owner changes the specification, the test has to follow it.",
        ),
        (
            "Delete the test, because discount rules change too often to be worth testing",
            "Rules that change are exactly the ones to pin down, so each change is deliberate and visible in the history.",
        ),
        (
            "Leave CI red until the next sprint review, where the team can discuss the failure",
            "The decision is already made and written in the backlog item. A red main blocks everyone who pushes in the meantime.",
        ),
    ],
    "b",
    """
    The same failure as sample Q4, `assert 90.0 == 95.0`, but now you know what the discount is
    supposed to be: 10%. The code matches the new rule; the test documents the old one. So the test
    changes, ideally in the same commit as the code, with a message that says the rule changed. A
    good habit is to check the test's name too: if it named the old percentage, rename it. Reverting
    would undo a decision the product owner made; deleting the test would leave the new rule with no
    check at all.
    """,
    variant_of="sample-paper-q04",
)

open_q(
    8, "hard", ["read-diff", "read-tool-output", "judgement"], 2,
    "Sample Q4; expense-tracker tests/test_report.py (refund test)", "teacher-variant", "run",
    """
    A teammate pushes this change to `total_by_category`, with the message `Ignore refunds in totals`:

    ```diff
             if expense.amount < minimum:
                 continue
    +        if expense.amount < 0:
    +            continue
             totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
    ```

    CI goes red:

    ```text
    >       assert total_by_category(expenses, category="", minimum=-100.0) == [("clothing", 25.0)]
    E       AssertionError: assert [('clothing', 40.0)] == [('clothing', 25.0)]
    E         At index 0 diff: ('clothing', 40.0) != ('clothing', 25.0)

    tests/test_report.py:77: AssertionError
    FAILED tests/test_report.py::test_a_refund_reduces_its_category_total - Asser...
    1 failed, 23 passed in 0.05s
    ```

    The test builds a 40.00 Zara purchase and a -15.00 Zara refund. Your teammate says: "My change
    is newer, so just update the test to 40.0."
    """,
    [
        {
            "prompt": "What does the failure show? Say what each side of the comparison is.",
            "marks": 1,
            "model": "The left side is what the code now returns, clothing 40.0 with the refund ignored; the right side is what the test expects, 25.0 (40 minus the 15 refund).",
            "rubric": [
                "States that the code now returns 40.0 for clothing (refund ignored) while the test expects 25.0 (40 minus 15)",
            ],
            "weak": "'It failed because 40 is not 25' repeats the line without reading it. A full answer says which side is the code (the left, the result) and which is the expectation, and what the numbers mean: the refund is no longer subtracted.",
        },
        {
            "prompt": "Is your teammate's reasoning sound? What would you check before changing anything?",
            "marks": 2,
            "model": "No. Which side changed last says nothing about which is right. I would check the agreed rule in the backlog item or with the product owner: should a refund reduce its category's total?",
            "rubric": [
                "Rejects 'newer wins' (and 'the test was first'): the failure alone cannot say which side is wrong",
                "Names a concrete place to check the rule: the backlog item, the product owner or the README",
            ],
            "weak": "Answers that simply pick a side ('tests are always right', 'the code is newer') miss sample Q4's point. 'Check the specification' without saying where it lives (backlog item, product owner) earns only the first mark.",
        },
        {
            "prompt": "Describe what you would do in each of the two possible outcomes.",
            "marks": 2,
            "model": "If refunds still count, the change is a bug: fix or revert the code and keep the test. If the group decided to ignore refunds, update the expected value and the test's name in the same commit, with a message saying the rule changed.",
            "rubric": [
                "Rule unchanged: the code is fixed or reverted, and the test stays as it is",
                "Rule changed: the test (expected value and name) is updated in the same change, with a message saying so",
            ],
            "weak": "Rerunning, skipping or deleting the test is never one of the outcomes. Many answers cover only one case; the question asks for both. Changing 25.0 to 40.0 but keeping the name `test_a_refund_reduces_its_category_total` leaves a test whose name now lies.",
        },
    ],
    "6–8",
    """
    The structure is sample Q4's: a test fails after someone changed the code, and the temptation is
    to let age decide. The failure shows a disagreement (40.0 returned, 25.0 expected) and nothing
    more. The refund test exists because "Negative: nonsense?" is one of the edge cases to choose on
    purpose, so it documents a decision. Only the agreed rule can say whether the code or the test
    must change, and both outcomes are legitimate as long as test and rule end up agreeing.
    """,
    variant_of="sample-paper-q04",
)

# ---------------------------------------------------------------------------------------------
# Section 3
# ---------------------------------------------------------------------------------------------

mcq(
    9, "core", ["read-tool-output", "concept"], 3, "S8 slide 8; labs/08-tdd.md troubleshooting", "lab", "run",
    """
    A test of a shopping-basket function fails like this:

    ```text
        def test_two_items_add_up() -> None:
            total = basket_total([0.1, 0.2])
    >       assert total == 0.3
    E       assert 0.30000000000000004 == 0.3

    tests/test_basket.py:7: AssertionError
    ```

    Why does it fail, and what is the fix?
    """,
    (
        "Floats cannot store 0.1 or 0.2 exactly, so the sum is slightly off; use `pytest.approx(0.3)`",
        "`0.1 + 0.2 == 0.3` is `False` in Python. Money in floats needs a tolerance, which is what `pytest.approx` gives.",
    ),
    [
        (
            "`basket_total` adds one amount twice; fix the loop so each price is counted once",
            "An extra item would add 0.1 or 0.2, not 0.00000000000000004. The size of the difference tells you it is rounding noise.",
        ),
        (
            "pytest rounds the expected value; write `0.30000000000000004` as the expected value instead",
            "pytest does not round anything. Copying float noise into the test makes it fragile and unreadable as a rule.",
        ),
        (
            "Floats can never be compared in a test; rewrite `basket_total` to use `Decimal` before testing it",
            "Real money code uses `Decimal`, but the slide leaves that to another course. Floats can be compared in a test, with a tolerance: `pytest.approx`.",
        ),
    ],
    "c",
    """
    The lab's troubleshooting table has this exact line: `assert 0.30000000000000004 == 0.3` means
    floats, and the fix is `pytest.approx(0.3)`. Binary floating point cannot store 0.1 or 0.2
    exactly, so their sum lands a tiny distance from 0.3, and `==` demands exact equality. The code
    is fine; the comparison is too strict. As the slide puts it, "Money in floats needs a
    tolerance." Real money code would use `Decimal`, which the slide leaves to another course.
    """,
)

mcq(
    10, "exam", ["read-tool-output", "judgement"], 3, "S8 slide 8", "slides", "run",
    """
    ```text
        def test_two_meals_add_up() -> None:
            expenses = [
                Expense("2025-07-01", "Bar Ramon", "dining", 10.10),
                Expense("2025-07-03", "Bar Ramon", "dining", 20.20),
            ]
            total = total_by_category(expenses, category="dining", minimum=0.0)[0][1]
    >       assert total == 30.3
    E       assert 30.299999999999997 == 30.3

    tests/test_floats.py:16: AssertionError
    ```

    Which change is most appropriate?
    """,
    (
        "Compare with `pytest.approx(30.3)`, because money held in floats needs a tolerance",
        "The sum is off by about 0.000000000000004, which is float noise. `pytest.approx` accepts that tiny error and still fails on a real mistake.",
    ),
    [
        (
            "Change the expected value to `30.299999999999997` so it matches what Python computes",
            "That bakes float noise into the test: it stops reading as a rule and breaks if the order of additions changes.",
        ),
        (
            "Round every amount to a whole euro inside `total_by_category` so the totals are exact",
            "That changes the program's behaviour (cents disappear) to suit a test. The test's comparison is the problem.",
        ),
        (
            "Delete the test, because totals held in floats cannot be tested reliably",
            "They can, with a tolerance. Deleting it loses the check on adding two meals together.",
        ),
    ],
    "a",
    """
    `10.10 + 20.20` is `30.299999999999997` in Python, so `==` fails even though the code adds
    correctly. The slide's tool is `pytest.approx`: `assert total == pytest.approx(30.3)` passes
    for a difference in the fifteenth decimal place and still fails for a wrong total such as 20.2.
    The wrong moves all change something that is not broken: the expected value (now unreadable),
    the production code (now losing cents) or the suite (now missing a test).
    """,
)

mcq(
    11, "core", ["concept", "read-code"], 3, "S8 slide 9", "slides", "source",
    """
    ```python
    @pytest.fixture
    def expenses() -> list[Expense]:
        return [
            Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
            Expense("2025-07-02", "Zara", "clothing", 40.0),
        ]

    def test_category_filter(expenses: list[Expense]) -> None:
        result = total_by_category(expenses, category="dining", minimum=0.0)
        assert result == [("dining", 10.0)]
    ```

    How does `test_category_filter` get its list of expenses?
    """,
    (
        "pytest matches the parameter's name to the fixture, calls it and passes in its result",
        "\"A fixture is a function pytest calls for you. Ask for it by name in the test's arguments.\"",
    ),
    [
        (
            "The test calls `expenses()` itself at the start, before the first line of its body",
            "You never call a fixture yourself. Nothing in the test body calls it; pytest fills the argument.",
        ),
        (
            "Python shares the list automatically because the fixture and the test are in the same file",
            "Being in the same file does not pass values into a function. The link is the parameter's name, read by pytest.",
        ),
        (
            "`@pytest.fixture` runs `expenses` once when the file loads and stores the list in a global variable",
            "No global is created. pytest calls the fixture for each test that asks for it by name.",
        ),
    ],
    "d",
    """
    A fixture is shared set-up: a function marked `@pytest.fixture` that returns the data several
    tests need. The test never calls it. Instead it declares a parameter with the same name,
    `expenses`, and pytest, which runs the tests, sees that name, calls the fixture and passes its
    return value in. This is why the name must match exactly: the fixture and the test are joined
    by nothing but the name.
    """,
)

mcq(
    12, "core", ["read-tool-output"], 3, "S8 slide 9; labs/08-tdd.md troubleshooting", "lab", "run",
    """
    ```console
    $ uv run pytest -q tests/test_filter.py
    E                                                                        [100%]
    ==================================== ERRORS ====================================
    ____________________ ERROR at setup of test_category_filter ____________________
    file tests/test_filter.py, line 14
      def test_category_filter(expense: list[Expense]) -> None:
    E       fixture 'expense' not found
    >       available fixtures: cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, doctest_namespace, expenses, monkeypatch, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, subtests, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory
    >       use 'pytest --fixtures [testpath]' for help on them.

    tests/test_filter.py:14
    =========================== short test summary info ============================
    ERROR tests/test_filter.py::test_category_filter
    1 error in 0.00s
    ```

    What does this tell you?
    """,
    (
        "A typo: the test asks for `expense`, but the fixture is named `expenses`",
        "The available list contains `expenses`. One missing letter in the argument is the whole problem.",
    ),
    [
        (
            "The fixture returned the wrong type, so pytest refused to pass it to the test",
            "pytest does not check types. The message says the fixture was not found at all.",
        ),
        (
            "Fixtures defined in a test file need a plugin; install it with `uv add --dev`",
            "Fixtures are built into pytest, and the list shows `expenses` was found in this file.",
        ),
        (
            "The category filter returned no dining expenses, so the assert failed",
            "This is an `ERROR at setup`, not a failure: the test body, and its assert, never ran.",
        ),
    ],
    "b",
    """
    The lab's table: "`fixture 'tmp_path' not found`: a typo in the argument name; pytest matches
    fixtures by name." Here the test's parameter is `expense` and the fixture is `expenses`, which
    pytest even lists among the available fixtures. Note the `E` at the top and the word `ERROR`:
    the test could not start, so nothing about `total_by_category` has been tested yet. Fix the
    name and run again.
    """,
)

mcq(
    13, "hard", ["read-tool-output", "read-code"], 3, "S8 slides 10–11; expense-tracker tests/test_report.py", "history", "run",
    """
    The demo's v0.4 test, then the output after a teammate's commit `Tidy the minimum filter` changed
    one line in `total_by_category`:

    ```python
    @pytest.mark.parametrize(
        ("minimum", "expected"),
        [
            (0.0, [("dining", 15.0)]),
            (5.0, [("dining", 15.0)]),
            (10.0, [("dining", 10.0)]),
            (10.01, []),
        ],
    )
    def test_minimum_keeps_amounts_equal_to_it(
        minimum: float, expected: list[tuple[str, float]]
    ) -> None:
        dining = [
            Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
            Expense("2025-07-03", "Bar Ramon", "dining", 5.0),
        ]

        assert total_by_category(dining, category="", minimum=minimum) == expected
    ```

    ```text
    minimum = 5.0, expected = [('dining', 15.0)]
    E       AssertionError: assert [('dining', 10.0)] == [('dining', 15.0)]

    minimum = 10.0, expected = [('dining', 10.0)]
    E       AssertionError: assert [] == [('dining', 10.0)]

    FAILED tests/test_report.py::test_minimum_keeps_amounts_equal_to_it[5.0-expected1]
    FAILED tests/test_report.py::test_minimum_keeps_amounts_equal_to_it[10.0-expected2]
    2 failed, 22 passed in 0.05s
    ```

    What do the two failing cases have in common?
    """,
    (
        "In both, an expense equal to the minimum is now dropped instead of kept",
        "With minimum 5.0 the 5.0 meal vanished; with minimum 10.0 the 10.0 meal vanished. The filter now drops amounts equal to the minimum.",
    ),
    [
        (
            "Every row of the parametrized test fails, so the whole minimum filter is broken",
            "Only two of the four rows fail; rows 0.0 and 10.01 are among the 22 passed.",
        ),
        (
            "The rows with a minimum of 5.0 or above fail, so large minimums are mishandled",
            "The largest minimum, 10.01, passes. Size is not the pattern; equality is.",
        ),
        (
            "parametrize ran one case twice under two names, so it is a single failure reported twice",
            "The ids carry different values (5.0 and 10.0) and the two `E` lines differ: two real cases.",
        ),
    ],
    "c",
    """
    Each parametrize row is reported as its own test, with its values in the id, so you can line the
    failures up. Row `[5.0-expected1]` lost the 5.0 meal; row `[10.0-expected2]` lost the 10.0 meal.
    Rows 0.0 (nothing equal to it) and 10.01 (nothing reaches it) still pass. The only thing the
    failing rows share is an amount exactly equal to the minimum: the teammate turned `<` into `<=`
    in the skip condition. This is why the edge-case table asks "Zero: the boundary?", and why the
    test's name states the rule it protects.
    """,
)

# ---------------------------------------------------------------------------------------------
# Section 4
# ---------------------------------------------------------------------------------------------

mcq(
    14, "exam", ["judgement"], 4, "S8 slide 11; moodle/project-pages.md (parking lot topic)", "slides", "reasoning",
    """
    Your group's parking lot charges 2 EUR per started hour for stays of up to three hours, and a
    flat 10 EUR for anything longer. You already have tests for 40 minutes (2 EUR) and 5 hours
    (10 EUR). Which test is most likely to catch a bug next?
    """,
    (
        "A stay of exactly 180 minutes, on the edge of the two bands",
        "Zero: the boundary. A `<` written where `<=` was meant changes the price only at exactly three hours.",
    ),
    [
        (
            "A stay of 100 minutes, in the middle of the hourly band",
            "Another happy-path case: it exercises the same branch as the 40-minute test.",
        ),
        (
            "A stay of 7 hours, well inside the flat-rate band",
            "It repeats what the 5-hour test already checks; the same branch with a bigger number.",
        ),
        (
            "A second 40-minute stay, this time for a different car",
            "The same input with a different label. The price rule cannot tell the two cars apart.",
        ),
    ],
    "d",
    """
    "Do not test what feels likely. Test what could break." The two existing tests sit comfortably
    inside each pricing band. Bugs in band rules live on the edges: whether exactly 180 minutes is
    charged 6 EUR or 10 EUR depends on a single comparison, and only a test exactly on that line can
    tell `<` from `<=`. The project brief picks out pricing bands as rules that are "easy to get
    subtly wrong and easy to test". The other options add cases the program already handles the
    same way.
    """,
)

mcq(
    15, "core", ["concept"], 4, "S8 slide 11", "slides", "source",
    """
    The edge-case slide ends: "it is often said that tests also behave as documentation." Which of
    these shows that idea best?
    """,
    (
        "`test_minimum_keeps_amounts_equal_to_it`, whose name and cases state the rule it checks",
        "A teammate learns the rule from the name and sees it applied in the cases, and CI checks it on every push.",
    ),
    [
        (
            "A test named `test_report` that compares the whole printed report with a saved copy",
            "It may catch changes, but its name says nothing about which rule matters or why.",
        ),
        (
            "A test that reads `expenses.csv` and asserts that exactly 420 expenses come back",
            "420 is a fact about one data file, not a rule of the program; a reader learns nothing about what the code should do.",
        ),
        (
            "A long comment above a test explaining what `total_by_category` does in general",
            "A comment is not checked by anything. When the code changes, the comment can quietly become false.",
        ),
    ],
    "a",
    """
    Tests behave as documentation when they state rules in words a teammate can read and then
    prove them with concrete cases. `test_minimum_keeps_amounts_equal_to_it`, with cases at
    `10.0` (kept) and `10.01` (dropped), documents a decision that is otherwise invisible in the
    code: amounts equal to the minimum count. Unlike a comment or a README sentence, it fails the
    moment the code stops matching the rule. Vague names and magic numbers document nothing.
    """,
)

sort_q(
    16, "core", ["concept"], 4, "S8 slide 11; labs/08-tdd.md edge-case table; moodle/project-pages.md", "slides", "reasoning",
    """
    The edge-case table on slide 11 asks five questions. Put each planned test from a group project
    under the question it answers.
    """,
    [
        ("empty", "Empty: nothing in?"),
        ("zero", "Zero: the boundary?"),
        ("negative", "Negative: nonsense?"),
        ("duplicate", "Duplicate: twice?"),
        ("missing", "Missing: not there?"),
    ],
    [
        ("Meal planner: a shopping list for a week with no recipes planned", "empty", "Nothing goes in, so the list should come out empty rather than crash."),
        ("`total_by_category([], \"\", 0.0)` returns `[]`", "empty", "The slide's own example of the empty case."),
        ("Gradebook: a weighted average of exactly 50.0, the pass mark", "zero", "A value exactly on the threshold is where `>` and `>=` differ."),
        ("Vending machine: the customer pays the exact price, so no change is due", "zero", "Change of zero is the boundary of change-making: no coins should come back."),
        ("Expense tracker: a Zara refund of -15.00", "negative", "A negative amount is the slide's own example; it must reduce the total, not be ignored."),
        ("Parking lot: an exit time earlier than the entry time", "negative", "A negative duration is nonsense input; the program must reject it, not charge for it."),
        ("Library: the same member checks out the same book twice", "duplicate", "The same thing twice: should the second checkout be refused or counted?"),
        ("Flashcard trainer: one card added to the same box twice", "duplicate", "A repeated item, like the six exact duplicate rows in `expenses.csv`."),
        ("Habit tracker: a report for a habit nobody has logged yet", "missing", "Asking about something that is not there, like a category nobody used."),
        ("Movie watchlist: filtering by a genre that no movie has", "missing", "The filter should return an empty result, not crash, when the value does not exist."),
    ],
    """
    The five questions are a checklist for finding the tests that could break. Empty asks what
    happens when there is no input at all. Zero asks about the boundary, the exact value where a
    rule switches. Negative asks about input that makes no sense, such as a refund or a negative
    duration. Duplicate asks about the same thing appearing twice. Missing asks about something the
    data does not contain. Checkpoint 2 wants at least two tests like these, not happy paths.
    """,
)

open_q(
    17, "exam", ["read-diff", "judgement"], 4,
    "Sample Q8.3; S8 slides 8 and 11", "teacher-variant", "run",
    """
    A teammate adds this function for a new monthly report, with the message `Add spent_in_month`:

    ```diff
    +def spent_in_month(expenses: list[Expense], month: str) -> float:
    +    total = 0.0
    +    for expense in expenses:
    +        if expense.date.startswith(month):
    +            total += expense.amount
    +    return total
    ```

    Dates are stored as text such as `"2025-07-01"`, and the command passes a month such as
    `"2025-07"`. `ruff`, `mypy --strict` and the existing tests all pass.
    """,
    [
        {
            "prompt": "In one sentence, what does the function do?",
            "marks": 1,
            "model": "It adds up the amounts of every expense whose date starts with the given month text, so it returns the total spent in that month, or 0.0 if there is none.",
            "rubric": [
                "Says it sums the amounts of the expenses whose date begins with the month string and returns that total",
            ],
            "weak": "'It loops over the expenses' narrates the code without saying what comes out. The answer must name the result: the total spent in one month. 'It finds the expenses of a month' is close but misses that it returns one number, a sum, not a list.",
        },
        {
            "prompt": "Name three tests you would add, in words. Aim each at a different edge case and say what it expects.",
            "marks": 3,
            "model": "An empty list gives 0.0. An expense on 31 July and one on 1 August, asked for `2025-07`, gives only the July amount. A July purchase of 40.00 and a July refund of -15.00 give 25.0.",
            "rubric": [
                "An empty list of expenses returns 0.0 (empty)",
                "A month with no expenses returns 0.0 (missing)",
                "A boundary pair: the last day of the month counts, the first day of the next month does not",
                "A refund (negative amount) in the month reduces the total (negative)",
                "A month written without its leading zero, such as `2025-1`, must not match October to December (today it does, because `startswith` matches `2025-10`)",
            ],
            "weak": "Three happy-path tests ('July with three expenses') are one test written three times. Each test needs an input and an expected result; 'a test with bad data' is not checkable. The `2025-1` case is the kind that finds a real bug here, because `startswith` is looser than it looks.",
        },
        {
            "prompt": "One of your tests adds 10.10 and 20.20. How should it compare the result, and why?",
            "marks": 1,
            "model": "With `pytest.approx(30.3)`, because the float sum is 30.299999999999997, and money in floats needs a tolerance.",
            "rubric": [
                "Compares with `pytest.approx` (a tolerance) because floats cannot store these amounts exactly",
            ],
            "weak": "Plain `==` fails on float noise. 'Round it' is half right, but the course's tool is `pytest.approx`. 'Switch to Decimal' changes the production code, which the slide calls another course. Writing the expected value as 30.299999999999997 makes the test pass but no longer read as a rule.",
        },
    ],
    "6–8",
    """
    This is sample Q8 part 3 ("name one test you would add for this change, in words") made harder:
    three tests, each aimed at a different row of the edge-case table. Good answers give each test
    an input and an expected output, so a marker could turn it into code. The strongest answers
    notice what could break rather than what feels likely: `startswith` treats `2025-1` as a prefix
    of `2025-10`, which a run confirms (an October expense is counted for month `2025-1`).
    """,
    variant_of="sample-paper-q08",
)

# ---------------------------------------------------------------------------------------------
# Section 5
# ---------------------------------------------------------------------------------------------

mcq(
    18, "exam", ["read-tool-output", "judgement"], 5, "S8 slide 14; expense-tracker e1b96de", "history", "run",
    """
    At commit `e1b96de` the demo has five new tests and a stub:

    ```python
    def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
        return expenses
    ```

    ```console
    $ uv run pytest -q tests/test_duplicates.py
    ..F.F                                                                    [100%]
    ...
    FAILED tests/test_duplicates.py::test_an_exact_duplicate_is_removed_and_the_first_one_kept
    FAILED tests/test_duplicates.py::test_many_copies_of_one_expense_collapse_to_one
    2 failed, 3 passed in 0.01s
    ```

    A classmate says: "Three out of five already pass, so the stub is nearly right." What is the
    best reading of this run?
    """,
    (
        "The three pass by luck: an unchanged list is right whenever there are no duplicates to drop",
        "The passing tests (empty list, no duplicates, same merchant on another day) expect the input back unchanged, which the stub happens to do.",
    ),
    [
        (
            "The stub is nearly right, so one more `if` inside it will probably finish the job",
            "Counting passes does not measure closeness. The stub does nothing at all; it is right only where nothing needs doing.",
        ),
        (
            "Most of the suite agrees with the stub, so the two failing tests probably expect the wrong thing",
            "A majority vote is not a specification. The failing tests are the only ones that contain duplicates.",
        ),
        (
            "The run tells you nothing until all five tests fail, so change the passing ones until they fail too",
            "Red does not require every test to fail. Tests for behaviour that already holds pass legitimately.",
        ),
    ],
    "c",
    """
    "Run it: two fail, the others pass by luck. Red is information, not a problem." The stub returns
    its input untouched, which is exactly right for an empty list, for a list without duplicates and
    for the same merchant on another day. Only the two tests that actually contain duplicates can
    fail, and they do, with pytest showing the extra copies. The failures are the information: they
    are the behaviour that does not exist yet. Green comes next, with the smallest code that makes
    them pass.
    """,
)

mcq(
    19, "hard", ["read-tool-output", "concept"], 5, "S8 slide 14; expense-tracker e1b96de", "history", "run",
    """
    In the red step the teacher wrote a stub (`return expenses`) before running the new tests. A
    classmate skips the stub and runs the new test file straight away:

    ```console
    $ uv run pytest -q tests/test_duplicates.py

    ==================================== ERRORS ====================================
    __________________ ERROR collecting tests/test_duplicates.py ___________________
    ImportError while importing test module 'tests/test_duplicates.py'.
    ...
    E   ImportError: cannot import name 'remove_duplicates' from 'expense_tracker.report' (src/expense_tracker/report.py)
    =========================== short test summary info ============================
    ERROR tests/test_duplicates.py
    !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
    1 error in 0.04s
    ```

    Why was the stub the better first move?
    """,
    (
        "Without it, pytest cannot import the test module, so no test runs and nothing is learned",
        "Collection stopped at the import. The stub makes the module importable so the failures are about behaviour, with both sides shown.",
    ),
    [
        (
            "The stub makes all five tests pass, which proves the tests themselves are written correctly",
            "With the stub, two tests fail. Passing tests are not the goal of the red step.",
        ),
        (
            "The `ImportError` means the package is not installed, and writing the stub fixes the environment",
            "The package imported fine: the error names `expense_tracker.report` and its file. Only the function name is missing.",
        ),
        (
            "An import error already counts as red, so the stub is only a matter of personal taste",
            "Red is a test that runs and fails on behaviour. Here no test ran at all; the run was interrupted during collection.",
        ),
    ],
    "c",
    """
    "First a stub, `return expenses`, so the failure says something." Without the function,
    `from expense_tracker.report import Expense, remove_duplicates` fails while pytest is still
    collecting the file, the run is interrupted, and you learn only that a name is missing, which
    you already knew. With a stub that returns something wrong, every test runs: three pass by luck
    and two fail with left and right values shown. Those failures describe the behaviour you are
    about to write, which is the whole point of red.
    """,
)

mcq(
    20, "exam", ["predict-output", "read-code"], 5, "S8 slides 14–16; expense-tracker tests/test_duplicates.py", "history", "run",
    """
    ```python
    BAR = Expense("2025-07-01", "Bar Ramon", "dining", 10.0)
    ZARA = Expense("2025-07-02", "Zara", "clothing", 40.0)
    next_day = Expense("2025-07-02", "Bar Ramon", "dining", 10.0)

    remove_duplicates([BAR, next_day, BAR, ZARA, next_day])
    ```

    With the demo's v0.4 `remove_duplicates`, what is returned?
    """,
    (
        "`[BAR, next_day, ZARA]`",
        "Each distinct expense once, in the order it first appeared. `next_day` differs from `BAR` in its date, so both stay.",
    ),
    [
        (
            "`[BAR, ZARA]`",
            "This treats the same merchant on another day as a duplicate. The tests say it is not: only all four fields equal makes a duplicate.",
        ),
        (
            "`[BAR, ZARA, next_day]`",
            "This is the order of the last copies. `dict.fromkeys` keeps the first position of each key.",
        ),
        (
            "`[ZARA]`",
            "This removes every expense that appears more than once. The function keeps one copy, the first.",
        ),
    ],
    "a",
    """
    A duplicate is an exact duplicate: same date, merchant, category and amount, which is what a
    frozen dataclass's equality compares. `BAR` and `next_day` differ in date, so the test
    `test_same_merchant_on_another_day_is_not_a_duplicate` keeps both. `dict.fromkeys` keeps each
    key at the position where it first appeared, so the result is `BAR`, `next_day`, `ZARA`. On the
    real file, this removes the six exact duplicates: 420 rows become 414.
    """,
)

mcq(
    21, "exam", ["read-diff", "concept"], 5, "S8 slide 16; expense-tracker d3df52b", "history", "source",
    """
    Commit `d3df52b`, "Use dict.fromkeys to drop duplicates in order":

    ```diff
     def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
    -    seen: set[Expense] = set()
    -    unique: list[Expense] = []
    -    for expense in expenses:
    -        if expense not in seen:
    -            seen.add(expense)
    -            unique.append(expense)
    -    return unique
    +    return list(dict.fromkeys(expenses))
    ```

    The five tests in `tests/test_duplicates.py` pass before and after this commit, and the commit
    does not touch them. Which statement best describes it?
    """,
    (
        "A refactoring: same behaviour, new structure, and the unchanged tests prove it",
        "Session 7's definition, checked by session 8's tests: same behaviour, better structure, tests untouched and green.",
    ),
    [
        (
            "A bug fix: the loop version kept the wrong copy of each duplicate",
            "Both versions keep the first copy, and `test_an_exact_duplicate_is_removed_and_the_first_one_kept` passed before and after.",
        ),
        (
            "A new feature: from this commit on, the 420 rows of `expenses.csv` come out as 414",
            "The seen-set version from `1e421bc` already turned 420 rows into 414. Same output before and after, so nothing new.",
        ),
        (
            "A risky change that needs new tests first, because one line cannot do what seven lines did",
            "Length is not behaviour. The existing tests are the safety net, and they stayed green.",
        ),
    ],
    "d",
    """
    "Refactor: with the tests as a net... Run the tests: still green. That is what 'refactoring'
    means." The seen-set loop was the green step, the smallest code that passed. The one-liner does
    the same job because dictionary keys are unique and dictionaries keep insertion order. The proof
    is not that it looks equivalent; it is that the same five tests, not edited, still pass (and
    both versions turn the 420 rows of `expenses.csv` into 414). If a refactoring needs its tests
    changed, it changed the behaviour.
    """,
)

mcq(
    22, "hard", ["read-tool-output", "concept"], 5, "S8 slide 16; S6 slide 24 (frozen=True)", "history", "run",
    """
    A teammate removes `frozen=True` from `Expense` ("nothing changes an expense anyway"). The demo's
    `remove_duplicates` is the one-liner from `d3df52b`. Type checking is clean, but the tests are not:

    ```console
    $ uv run mypy src tests
    Success: no issues found in 6 source files
    $ uv run pytest -q tests/test_duplicates.py
    .FFFF                                                                    [100%]
    ...
        def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
    >       return list(dict.fromkeys(expenses))
    E       TypeError: unhashable type: 'Expense'
    ...
    4 failed, 1 passed in 0.01s
    ```

    Which explanation and fix are right?
    """,
    (
        "Dictionary keys must be hashable, and `frozen=True` is what made `Expense` hashable; put it back",
        "Slide 16: \"`@dataclass(frozen=True)` makes `Expense` hashable. Session 6's `frozen=True` pays off here.\"",
    ),
    [
        (
            "`dict.fromkeys` only accepts strings; go back to the seen-set loop from `1e421bc`",
            "`dict.fromkeys` takes any hashable keys. The seen-set loop puts expenses in a set, which needs a hash too, and fails with the same error.",
        ),
        (
            "mypy found no issues, so the code is correct and the four failing tests need updating",
            "mypy does not flag this case; passing the type checker is not passing the tests. The tests caught a real crash.",
        ),
        (
            "The empty-list test still passes, so only the test data is wrong and the function is fine",
            "The empty list passes because nothing gets hashed. Every test with at least one expense crashes.",
        ),
    ],
    "c",
    """
    A set member or a dictionary key needs a hash. With `@dataclass(frozen=True)` (and the default
    `eq=True`), the dataclass gets a hash computed from its four fields, so two equal expenses
    collide as the same key and duplicates disappear. A plain `@dataclass` defines equality but no
    hash, so `dict.fromkeys` raises `TypeError: unhashable type: 'Expense'`. Running it shows the
    seen-set version fails identically (`expense not in seen` hashes too), and that `mypy --strict`
    reports no issues: here only the tests notice. "Session 6's frozen=True pays off here."
    """,
)

open_q(
    23, "hard", ["read-diff", "concept", "compare"], 5,
    "S8 slides 14–16; expense-tracker e1b96de, 1e421bc, d3df52b; S6 slide 24", "history", "run",
    """
    Three consecutive commits in the expense-tracker history:

    ```text
    e1b96de Add failing tests for remove_duplicates
    1e421bc Remove duplicates with a seen-set
    d3df52b Use dict.fromkeys to drop duplicates in order
    ```

    `e1b96de` adds five tests and a stub that returns `expenses` unchanged. The last commit's diff:

    ```diff
     def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
    -    seen: set[Expense] = set()
    -    unique: list[Expense] = []
    -    for expense in expenses:
    -        if expense not in seen:
    -            seen.add(expense)
    -            unique.append(expense)
    -    return unique
    +    return list(dict.fromkeys(expenses))
    ```

    `Expense` is a `@dataclass(frozen=True)`.
    """,
    [
        {
            "prompt": "Why does `e1b96de` commit tests that fail, together with a stub?",
            "marks": 2,
            "model": "It is the red step: the tests say what 'done' means before the code exists, and seeing them fail proves they can catch the missing behaviour. The stub lets the file import the function, so the tests fail on behaviour instead of stopping at an import error.",
            "rubric": [
                "Red step: the tests define 'done' first and are seen failing, which proves they can catch the missing behaviour",
                "The stub makes the module importable, so the tests actually run and the failures show values rather than an `ImportError` at collection",
            ],
            "weak": "'Because TDD says so' names the rule without the reason. Many answers miss the stub's job: without it pytest stops while collecting and no test runs. Calling the stub 'a first attempt at the solution' is wrong; it is deliberately not one.",
        },
        {
            "prompt": "Why is `d3df52b` a refactoring, and how do you know it did not break anything?",
            "marks": 2,
            "model": "Seven lines become one, but the behaviour is the same: dictionary keys are unique and keep insertion order, so the first copy is kept, in order. The proof is that the same five tests, unchanged, still pass.",
            "rubric": [
                "Behaviour unchanged: still keeps the first copy of each expense, in order (dictionaries keep insertion order)",
                "Evidence: the unchanged tests still pass after the change",
            ],
            "weak": "'It is shorter' is not what makes a refactoring; a short change can still change behaviour. 'I would write tests to check' misses that the tests already exist and stayed green, which is why they were written first.",
        },
        {
            "prompt": "Another group copies the one-liner into a project where `Checkout` is a plain `@dataclass` without `frozen=True`. What happens, and why?",
            "marks": 2,
            "model": "Any call with at least one checkout crashes with `TypeError: unhashable type: 'Checkout'`: dictionary keys must be hashable, and `frozen=True` is what gives a dataclass a hash. mypy does not catch it; the tests do.",
            "rubric": [
                "Predicts a `TypeError` about an unhashable type when the function runs",
                "Explains that dictionary keys (and set members) must be hashable and that `frozen=True` is what makes the dataclass hashable",
            ],
            "weak": "Guessing a wrong result ('it removes nothing', 'it keeps duplicates') misses that it crashes. Blaming `dict.fromkeys` and suggesting the seen-set loop misses that sets hash their members too. 'mypy would have warned them' is wrong: strict mypy reports no issues here, and only a test that runs the function finds it.",
        },
    ],
    "6–8",
    """
    The three commits are the red, green and refactor of slides 14–16, preserved in the history the
    teacher tells you to study. Red commits failing tests on purpose, with a stub so the failures
    describe behaviour. Green is the plain loop. Refactor swaps the loop for `dict.fromkeys`, and the
    unchanged tests are the evidence that behaviour stayed the same. Part 3 connects session 6: a
    run confirms that a plain `@dataclass` raises `TypeError: unhashable type` in both versions,
    while `mypy --strict` reports no issues.
    """,
)

# ---------------------------------------------------------------------------------------------
# Section 6
# ---------------------------------------------------------------------------------------------

mcq(
    24, "exam", ["judgement", "concept"], 6, "S8 slides 18–19 (image-only-slides.md)", "slides", "source",
    """
    Your gradebook's `import_and_report(path)` opens a CSV, computes each student's weighted average,
    decides pass or fail and prints a table. Where does it sit on the slide-18 diagram, and what
    should you do about it?
    """,
    (
        "Overcomplicated code (high benefit, high cost): split its rules into pure functions",
        "The logic is valuable to test but buried under a file and printing. Refactoring moves it into the cheap, high-benefit corner.",
    ),
    [
        (
            "A coordinator (low benefit, high cost): leave it untested, since coordinators are not worth it",
            "Coordinators have little logic of their own. This function holds the program's key decisions, so the benefit is high.",
        ),
        (
            "An algorithm (high benefit, low cost): write many `tmp_path` tests for it as it is",
            "Needing a file and capturing output for every test is what high cost means. It is not in the algorithm corner yet.",
        ),
        (
            "Trivial code (low benefit, low cost): one smoke test that it runs is enough",
            "Weighted averages and a pass boundary are exactly the non-obvious rules that are easy to get subtly wrong.",
        ),
    ],
    "b",
    """
    The diagram's vertical axis is the benefit of a unit test (how non-obvious the code is); the
    horizontal axis is its cost (how many dependencies). Grading logic is high benefit; a function
    that also opens files and prints is high cost. That corner is labelled "Overcomplicated code,
    needs refactoring": split it into pure functions (an algorithm: marks in, average out; average
    in, pass or fail out) and a thin coordinator that reads and prints. "If a function you want to
    test needs a file, ask: can I split the file reading out?"
    """,
)

mcq(
    25, "hard", ["read-tool-output", "judgement"], 6, "S8 slide 28 (the function prints); S7 functional core", "slides", "run",
    """
    In `src/gradebook/grades.py`:

    ```python
    PASS_MARK = 50.0


    def show_result(name: str, grade: float) -> None:
        if grade >= PASS_MARK:
            print(f"{name}: pass")
        else:
            print(f"{name}: fail")
    ```

    In `tests/test_grades.py`:

    ```python
    def test_fifty_is_a_pass() -> None:
        assert show_result("Ana", 50.0) == "Ana: pass"
    ```

    ```console
    $ uv run pytest -q
    >       assert show_result("Ana", 50.0) == "Ana: pass"
    E       AssertionError: assert None == 'Ana: pass'
    E        +  where None = show_result('Ana', 50.0)

    tests/test_grades.py:5: AssertionError
    ----------------------------- Captured stdout call -----------------------------
    Ana: pass
    =========================== short test summary info ============================
    FAILED tests/test_grades.py::test_fifty_is_a_pass - AssertionError: assert No...
    1 failed in 0.01s
    $ uv run mypy src tests
    tests/test_grades.py:5: error: "show_result" does not return a value (it only ever returns None)  [func-returns-value]
    Found 1 error in 1 file (checked 3 source files)
    ```

    What is going on, and what fix does the course recommend?
    """,
    (
        "It prints instead of returning; make it return the result and print in the shell",
        "\"You cannot assert on a print. Make it return, and print in the shell.\" The captured output shows the rule itself works.",
    ),
    [
        (
            "The pass rule is wrong: a grade of 50.0 should pass, but the function says it fails",
            "The captured stdout says `Ana: pass`. The decision is right; it just never comes back to the test.",
        ),
        (
            "50.0 is a float, so the test should compare the result with `pytest.approx`",
            "The comparison is `None` against a string. No tolerance can make those equal.",
        ),
        (
            "mypy's message is a false alarm; add `# type: ignore` on line 5 and the test will pass",
            "mypy is right that nothing is returned, and silencing it does not change `None == 'Ana: pass'`.",
        ),
    ],
    "a",
    """
    Read both sides: the left is `None`, the right is the text the test wanted. The "Captured stdout
    call" section shows the function printed exactly that text, so the decision is correct; it just
    went to the screen instead of back to the caller. mypy says the same in its own words. This is
    "the function prints", one of the three that bite. Session 7's split applies: the core returns
    values (a string, or better a `bool` for pass), and the shell prints them. Then the test can
    assert on the returned value.
    """,
)

sort_q(
    26, "core", ["concept"], 6, "S8 slide 18 (image-only-slides.md)", "slides", "source",
    """
    The diagram on slide 18 has two axes: the **benefit** of unit testing (how non-obvious the code
    is) and the **cost** of unit testing (how many dependencies it has). Place each piece of code in
    its quadrant.
    """,
    [
        ("algorithms", "Algorithms (high benefit, low cost)"),
        ("overcomplicated", "Overcomplicated code: needs refactoring (high benefit, high cost)"),
        ("trivial", "Trivial code (low benefit, low cost)"),
        ("coordinators", "Coordinators (low benefit, high cost)"),
    ],
    [
        ("`total_by_category(expenses, category, minimum)`: filters, groups and sorts a list it is given", "algorithms", "Non-obvious rules (filters, ties, order) with no dependencies: a list in, a list out."),
        ("A vending machine's `make_change(paid, price)` that returns the coins to give back", "algorithms", "Change-making is easy to get subtly wrong and needs nothing but two numbers."),
        ("Sample Q5's `process(rows)`: reads a file, validates each row, calculates totals and prints a report", "overcomplicated", "Valuable logic tangled with a file and printing: refactor it before testing it."),
        ("A parking `checkout()` that reads the clock, looks up the ticket file, computes the price band and prints a receipt", "overcomplicated", "The pricing rule matters, but every test would need a clock, a file and captured output."),
        ("`PASS_MARK = 50.0` in the gradebook", "trivial", "A constant cannot be wrong in an interesting way; a test of it repeats the code."),
        ("The `Expense` dataclass with its four fields and no methods", "trivial", "There is no logic to get wrong; Python generates the behaviour."),
        ("The demo's `report` command: calls `read_expenses`, `total_by_category`, `largest_expense`, `format_report`, then echoes each line", "coordinators", "Little logic of its own and many dependencies: one or two edge tests, such as the missing-file exit code."),
        ("A `main()` that reads settings, opens the data file, calls the core and writes the output file", "coordinators", "Pure wiring between parts that are tested elsewhere; costly to test, little to find."),
    ],
    """
    The diagram explains where unit tests pay. Algorithms make decisions with few dependencies, so
    tests are cheap and catch real bugs. Trivial code has little that can go wrong. Coordinators
    wire tested parts together: costly to test and little to find, so one or two edge tests at
    most. Overcomplicated code mixes valuable logic with dependencies; the answer is to refactor it
    into an algorithm plus a coordinator, which is what session 7's functional core did to the
    demo.
    """,
)

open_q(
    27, "exam", ["read-code", "judgement"], 6,
    "S8 slides 18–19, 21, 23; expense-tracker src/expense_tracker/cli.py", "slides", "source",
    """
    The demo's `report` command at v0.4:

    ```python
    @app.command()
    def report(
        path: str = typer.Argument("expenses.csv", help="CSV file to read."),
        category: str = typer.Option("", help="Only this category."),
        minimum: float = typer.Option(0.0, "--minimum", "--min", help="Ignore amounts below this."),
    ) -> None:
        try:
            expenses = read_expenses(path)
        except (OSError, ValueError):
            typer.echo(f"could not read {path}", err=True)
            raise typer.Exit(1) from None

        totals = total_by_category(expenses, category, minimum)
        largest = largest_expense(expenses)
        for line in format_report(path, category, minimum, totals, largest):
            typer.echo(line)
    ```

    A teammate plans six `CliRunner` tests for `report`, one per totals rule: the category filter,
    the minimum, a refund, an empty file, the largest-first order and ties.
    """,
    [
        {
            "prompt": "Where does `report` sit on the slide-18 diagram (benefit against cost of unit testing), and why?",
            "marks": 2,
            "model": "It is a coordinator: low benefit, because it has almost no logic of its own (read, call the core, print), and high cost, because each test needs a file or the command line and has to pick numbers out of printed text.",
            "rubric": [
                "Names the coordinator quadrant (low benefit, high cost)",
                "Justifies both axes: little logic of its own, and many dependencies (a file, the command line, printed output)",
            ],
            "weak": "'An algorithm, because it computes totals' confuses calling the computation with doing it: `total_by_category` does the work. 'Overcomplicated code' misreads the `try`/`except` as logic; it only turns a failed read into a message and exit code 1. Naming the quadrant without both reasons earns one mark.",
        },
        {
            "prompt": "Where should the six rule checks go instead, and what does that gain?",
            "marks": 2,
            "model": "Into plain-data tests of `total_by_category` and `largest_expense`: build a list of `Expense` in the test, call the function, compare the result. No file, no set-up, and a failure points at the rule. It also keeps most of the suite pure, as Checkpoint 2's third item asks.",
            "rubric": [
                "Moves the rule checks to direct tests of the pure core functions, with the data built in the test",
                "Names a concrete gain: no file or set-up, failures point at the rule, or CP2's 'most tests pure' item",
            ],
            "weak": "'Use `tmp_path` instead of `CliRunner`' still tests every rule through a file, so it stays expensive and counts against Checkpoint 2's third item. 'Use a fixture' is a detail of how to share data, not where the checks belong: the move is to call `total_by_category` and `largest_expense` directly with a list built in the test.",
        },
        {
            "prompt": "Which one or two tests of `report` itself are worth keeping?",
            "marks": 1,
            "model": "One `CliRunner` test that a missing file exits with code 1 and explains on stderr; at most one more happy-path run on a small `tmp_path` file.",
            "rubric": [
                "Keeps one or two edge tests of the command, such as the missing-file exit code 1 with its message",
            ],
            "weak": "'None' ignores that the exit code is real behaviour of the shell (session 5), which only a command-line test can check. 'All six' misses the point of the diagram. A test of the totals through `report` is also the wrong pick: those rules are already checked, more cheaply, on the core.",
        },
    ],
    "5–7",
    """
    The diagram and the Checkpoint 2 table say the same thing from two sides. `report` is a
    coordinator: its only decisions are whether the file could be read and printing each line. The totals
    rules live in `total_by_category`, a pure function that "tests itself". Testing those rules
    through the command line is the high-cost route to the same checks. Keep one or two tests at the
    edge, on purpose, where only the edge can be checked: the exit code.
    """,
)

open_q(
    28, "exam", ["read-code", "judgement"], 6,
    "S8 slides 19, 27–28; sample Q7 shape; moodle/project-pages.md (gradebook)", "teacher-variant", "reasoning",
    """
    Your group's gradebook has this function. The rule agreed in the backlog: *a final mark of 50 or
    more passes*.

    ```python
    def print_results(path):
        with open(path) as handle:
            rows = list(csv.reader(handle))
        for name, mark in rows:
            if float(mark) > 50:
                print(name, "pass")
            else:
                print(name, "fail")
    ```
    """,
    [
        {
            "prompt": "Give two reasons why this function is hard to unit test.",
            "marks": 2,
            "model": "It opens a file, so every test needs a real CSV on disk. It prints instead of returning, so it returns `None` and a test has nothing to assert on. The pass rule is buried between the two.",
            "rubric": [
                "It reads a file, so each test needs a file (input mixed into the logic)",
                "It prints and returns `None`, so there is nothing to assert on",
            ],
            "weak": "'It has no type hints' is true but is not what blocks testing. 'It is too long' is vague; name the jobs (reading, deciding, printing) that get in the way.",
        },
        {
            "prompt": "Describe in words how you would restructure it so the pass rule can be tested with plain data.",
            "marks": 2,
            "model": "Extract a pure function that takes a mark and returns whether it passes, with no `open` and no `print`. Keep reading the file and printing in a thin outer function in the shell that calls it for each row.",
            "rubric": [
                "Extracts the decision into a pure function: a number in, pass or fail out, no file and no print",
                "Leaves reading and printing in a thin shell function that calls it (functional core, imperative shell)",
            ],
            "weak": "'Add tests' is not a restructuring. 'Use `tmp_path` and capture the output' tests it as it is, at high cost, and keeps the rule tangled. Do not write code: describe the split in words.",
        },
        {
            "prompt": "Name two tests for the extracted rule, in words, and say what the edge-case test would reveal here.",
            "marks": 2,
            "model": "A mark of 72 passes (happy path). A mark of exactly 50 passes, as the rule says; it would fail today, because `> 50` makes 50 a fail, so the boundary test finds a real bug.",
            "rubric": [
                "One happy-path test with its expected result",
                "A boundary test at exactly 50 expecting a pass, noting it reveals the `>` against `>=` bug",
            ],
            "weak": "'Test a high mark and a low mark' misses the boundary, which is where the bug is. Saying 'test 50' without saying it should pass, and that the current code says fail, earns half.",
        },
    ],
    "6–8",
    """
    Sample Q7's shape (what is wrong, then how to change it in words) applied to session 8. The
    function mixes the three jobs the course separates: reading (a file), deciding (the pass rule)
    and printing. Each makes testing harder, which is why slide 27 says "If your logic is tangled up
    with print or open, split it first. That is refactoring under test." Once the rule is a pure
    function, the edge-case table finds the bug at once: "Zero: the boundary?" means exactly 50.
    """,
    variant_of="sample-paper-q07",
)

# ---------------------------------------------------------------------------------------------
# Section 7
# ---------------------------------------------------------------------------------------------

mcq(
    29, "core", ["concept", "read-code"], 7, "S8 slide 20; expense-tracker f3d9870", "history", "source",
    r"""
    The demo's test from commit `f3d9870`:

    ```python
    def test_rows_that_are_not_four_fields_are_skipped(tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        csv_file.write_text(
            "date,merchant,category,amount\n"
            "2025-07-01,Bar Ramon,dining,10.00\n"
            "broken\n"
            "2025-07-02,Zara,clothing,40.00\n"
        )

        merchants = [expense.merchant for expense in read_expenses(str(csv_file))]

        assert merchants == ["Bar Ramon", "Zara"]
    ```

    Why does it build its own file in `tmp_path` instead of reading the repository's `expenses.csv`?
    """,
    (
        "It controls exactly what the file holds, on any machine, without touching real files",
        "\"`tmp_path` is a fresh empty directory for this test. pytest deletes it afterwards. Your real files are never touched.\"",
    ),
    [
        (
            "pytest is not allowed to open files that live anywhere outside the `tmp_path` folder",
            "pytest can open any file; that is why tests that read `data/expenses.csv` pass on a laptop and fail in CI.",
        ),
        (
            "Files in `tmp_path` are read much faster, which keeps the whole suite under a second",
            "Speed is not the reason. The real file is small; the problem is control and portability.",
        ),
        (
            "Only files in `tmp_path` count towards coverage, so the test would not count otherwise",
            "Coverage measures lines of your code that ran, not which data files were read.",
        ),
    ],
    "d",
    """
    The test needs a file with one malformed row to prove that `read_expenses` skips it. The
    repository's `expenses.csv` may not contain such a row and may change; a file on your laptop may
    not exist in CI. Writing three good lines and one broken one into `tmp_path` gives the test
    exactly the input it needs, on any machine, without touching real files. This is "the one place
    you read or write a file", one of the one or two I/O tests Checkpoint 2 allows.
    """,
)

mcq(
    30, "hard", ["read-tool-output", "read-diff", "judgement"], 7,
    "S8 slide 21; labs/01-scaffold.md (keep the callback); S5 exit codes", "lab", "run",
    """
    A teammate deletes the `add` command (to rewrite it later) and the empty `@app.callback()`
    ("it does nothing"), leaving `report` as the only command. Then:

    ```console
    $ uv run pytest -q tests/test_io.py
    .F                                                                       [100%]
        def test_report_on_a_missing_file_exits_with_one_and_explains_on_stderr() -> None:
            result = runner.invoke(app, ["report", "nosuch.csv"])

    >       assert result.exit_code == 1
    E       assert 2 == 1
    E        +  where 2 = <Result SystemExit(2)>.exit_code
    ...
    1 failed, 1 passed in 0.15s
    ```

    ```console
    $ uv run expenses report nosuch.csv
    Usage: expenses [OPTIONS] [path]
    Try 'expenses --help' for help.
    ╭─ Error ──────────────────────────────────────────────────────────────────────╮
    │ Got unexpected extra argument(s) (nosuch.csv)                                │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    $ echo $?
    2
    ```

    What should you conclude?
    """,
    (
        "typer now reads `report` as the path and rejects the extra argument; restore the callback",
        "The usage error is about the command line itself. Lab 01 warns that without the callback a single command loses its name and tests fail with exit code 2.",
    ),
    [
        (
            "The missing-file handling now exits with 2 instead of 1, so update the test to expect exit code 2",
            "The program never got as far as opening a file: there is no 'could not read' message, only a usage error.",
        ),
        (
            "`CliRunner` cannot test a missing file reliably; write the file into `tmp_path` and test that instead",
            "The same test passed before the change. The point of the test is the missing file, so creating it would test something else.",
        ),
        (
            "The test is flaky because `CliRunner` shares state between tests in one run; rerun it on its own",
            "The hand run gives exit code 2 too. A deterministic usage error is not flakiness.",
        ),
    ],
    "c",
    """
    Exit code 2 and "Got unexpected extra argument(s)" mean typer rejected the command line before
    any of your code ran. Lab 01 explains why: with a single command, typer assumes the command is
    the program and drops its name, so `report` is taken as the `path` argument and `nosuch.csv` is
    extra. "The empty callback tells typer there will be more commands." The test did its job: it
    checks session 5's exit code by machine, and it noticed that the command-line interface changed.
    Fix the cause, not the expected number.
    """,
)

mcq(
    31, "exam", ["read-tool-output", "concept"], 7, "S8 slide 22", "slides", "run",
    """
    The slide's test, with one line removed by a teammate ("the chdir looks unnecessary"):

    ```python
    def test_add_without_chdir(tmp_path: Path) -> None:
        runner.invoke(app, ["add", "Bar Ramon", "dining", "12.50"])
        assert (tmp_path / "data" / "expenses.csv").exists()
    ```

    ```text
    >       assert (tmp_path / "data" / "expenses.csv").exists()
    E       AssertionError: assert False
    FAILED tests/test_add.py::test_add_without_chdir - AssertionError: assert False
    ```

    ```console
    $ cat data/expenses.csv
    date,merchant,category,amount
    2026-10-14,Bar Ramon,dining,12.50
    ```

    The last command was run in the project folder after the test. What happened?
    """,
    (
        "Without the `chdir`, `add` wrote to the real `data/` folder; the test looked in `tmp_path`",
        "`monkeypatch.chdir(tmp_path)` moved the working directory into the temporary folder for this one test, then restored it.",
    ),
    [
        (
            "`tmp_path` was never created, because `monkeypatch` is the fixture that creates it",
            "`tmp_path` is its own fixture and was created; it simply stayed empty.",
        ),
        (
            "`CliRunner` ran the command in its own temporary folder, which was deleted before the assert",
            "The command ran in the current working directory, which is why a new row appeared in the project's `data/` folder.",
        ),
        (
            "The `chdir` only made the test faster, so the failure must come from the `add` command itself",
            "`add` worked and wrote its row; it wrote it in the wrong place. The `chdir` decides where.",
        ),
    ],
    "b",
    """
    `DATA_FILE` is the relative path `data/expenses.csv`, so `add` writes wherever the program runs.
    pytest runs from the project folder, so without the `chdir` the test appended a real row, dated
    today, to your own data, and then looked for the file in the empty `tmp_path`. `monkeypatch`
    exists for this: "Working directory, environment variables, attributes: set for this test,
    restored after." Together with `tmp_path` it gives the test a private folder, and your real
    files are never touched.
    """,
)

mcq(
    32, "exam", ["judgement"], 7, "S8 slides 23 and 29", "slides", "source",
    """
    A group's suite has 9 tests, all passing, with CI green at `v0.2`. Eight of them write a CSV
    into `tmp_path`, call `read_expenses` on it and then check a total; two of those eight check a
    refund and an amount exactly equal to the minimum. The ninth passes an empty list to a pure
    function. Which Checkpoint 2 item is at risk?
    """,
    (
        "Item 3: most tests should call pure functions with plain data",
        "Eight of nine tests go through a file. Slide 23: \"Eight tests that all need a file is the opposite of what we practised.\"",
    ),
    [
        (
            "Item 1: tests that use `tmp_path` do not count towards the eight required tests",
            "They count as tests. With 9 passing and CI green at the tag, item 1 is met.",
        ),
        (
            "Item 2: an empty list does not count as an edge case, so there are too few",
            "Empty is the first row of the edge-case table, and the refund and boundary tests are edge cases too.",
        ),
        (
            "None: `tmp_path` never touches real files, so these tests count as pure",
            "Not touching your files is what makes them safe, not pure. Slide 23 counts `tmp_path` as an I/O test.",
        ),
    ],
    "d",
    """
    Checkpoint 2 has three binary items: at least 8 passing tests with CI green at `v0.2`; at least
    2 edge-case tests; and most tests calling pure functions with plain data, with at most one or
    two using `tmp_path`, `CliRunner` or `monkeypatch`, on purpose. This suite meets the first two
    and fails the third. The totals rules could be tested by passing a list straight to
    `total_by_category`; only one test needs to prove the file reading works.
    """,
)

sort_q(
    33, "exam", ["judgement"], 7, "S8 slides 19–23; labs/08-tdd.md step 3", "slides", "reasoning",
    """
    For each test your group plans, pick the tool from slide 23 that it needs.
    """,
    [
        ("plain", "Plain list: pure function, data built in the test"),
        ("tmp_path", "`tmp_path`: a file"),
        ("clirunner", "`CliRunner`: the command line"),
        ("monkeypatch", "`monkeypatch`: working directory or environment"),
    ],
    [
        ("`total_by_category` keeps an amount exactly equal to the minimum", "plain", "A pure function: build two expenses in the test and compare the result."),
        ("A parking stay of 181 minutes is charged the flat day rate", "plain", "A pricing rule: minutes in, price out, nothing to touch."),
        ("`read_expenses` skips a row that does not have four fields", "tmp_path", "The behaviour is about reading a file, so the test writes one, broken row included."),
        ("Reading a CSV that has a header row and nothing else gives an empty list", "tmp_path", "Again the file itself is the input; create it in a fresh directory."),
        ("`expenses report nosuch.csv` exits with code 1 and explains on stderr", "clirunner", "Exit code and stderr only exist at the command line."),
        ("`expenses --help` lists both the `report` and `add` commands", "clirunner", "The help text is output of the command-line app."),
        ("The gradebook reads its pass mark from the `GRADEBOOK_PASS_MARK` environment variable when it is set", "monkeypatch", "Set the variable for this test only; `monkeypatch` restores it afterwards."),
        ("`currency()` returns the `EXPENSES_CURRENCY` environment variable, or `EUR` when it is not set", "monkeypatch", "The test sets or removes the variable with `monkeypatch`, which restores it afterwards; no file and no command line are involved."),
    ],
    """
    The table on slide 23 matches tools to what the test touches. Pure functions need nothing but
    data built in the test, and they should be most of your suite. `tmp_path` is for "the one place
    you read or write a file", `CliRunner` for "the command line: exit code, output", and
    `monkeypatch` for "the working directory, environment". The last three count as I/O tests, so
    Checkpoint 2 wants only one or two of them, chosen on purpose.
    """,
)

open_q(
    34, "exam", ["read-code", "judgement"], 7,
    "S8 slides 23 and 28; labs/08-tdd.md step 3 and troubleshooting; expense-tracker .gitignore and README", "lab", "run",
    """
    A group's test file looks like this; three more tests follow the same pattern. All of them pass
    with `uv run pytest` on the laptop of the student who wrote them.

    ```python
    def test_dining_total() -> None:
        expenses = read_expenses("data/expenses.csv")
        totals = dict(total_by_category(expenses, category="", minimum=0.0))
        assert totals["dining"] == 412.5


    def test_number_of_rows() -> None:
        assert len(read_expenses("data/expenses.csv")) == 87


    def test_largest_is_zara() -> None:
        expenses = read_expenses("data/expenses.csv")
        assert largest_expense(expenses).merchant == "Zara"
    ```

    (In the demo, `data/` is listed in `.gitignore`; the README says `add` writes to
    `data/expenses.csv`, "which is not in version control".)
    """,
    [
        {
            "prompt": "Name two problems this suite will cause.",
            "marks": 2,
            "model": "`data/` is not in the repository, so CI's fresh clone fails with `FileNotFoundError`. And the expected numbers depend on whatever the file holds, so the next `expenses add` breaks the tests with no code change.",
            "rubric": [
                "Depends on a file that exists only on one laptop (`data/` is not in the repository), so CI fails",
                "The expectations are tied to data that changes: adding an expense breaks the tests, and the numbers cannot be checked by hand",
                "Every test touches a file; none tests a pure function with plain data",
                "`largest_expense` can return `None`, so strict mypy rejects `.merchant` on it",
            ],
            "weak": "'The tests are slow' is not the problem. 'The file might be missing' is half of the first point; say why: it is not in the repository, so CI never has it.",
        },
        {
            "prompt": "Describe how you would rewrite the suite.",
            "marks": 2,
            "model": "Build a small list of `Expense` in each test, or in a fixture, with numbers I can add by hand, and call `total_by_category` and `largest_expense` directly. Keep one `read_expenses` test on a tiny file in `tmp_path`.",
            "rubric": [
                "Builds the data inside the tests (plain lists or a fixture) with values checkable by hand, calling the pure functions directly",
                "Keeps at most one or two file tests, using `tmp_path` instead of the real file",
            ],
            "weak": "'Commit `data/expenses.csv`' makes CI find the file but keeps the tests tied to personal, changing data in a public repository. 'Use monkeypatch' names a tool without saying what it would change.",
        },
        {
            "prompt": "Checkpoint 2's third item says most tests should call pure functions with plain data. Why does the course insist on that?",
            "marks": 1,
            "model": "Pure tests need no set-up, run the same on every machine and fail only when a rule breaks; file tests are costly and fail for reasons that have nothing to do with the logic.",
            "rubric": [
                "Pure tests run anywhere with no set-up and fail only when a rule is broken, while I/O tests are costly and fail for unrelated reasons",
            ],
            "weak": "'Because the checkpoint says so' restates the rule. The reason is the 2x2: algorithms are cheap to test and worth it, while dependencies make every test costly and fragile. 'Pure tests are faster' is true but minor; the point is that they fail only for a reason in the logic.",
        },
    ],
    "6–8",
    """
    Slide 28's third trap: "A test that reads data/expenses.csv passes only on your machine." The
    demo even documents that `data/` is not in version control, and a run in a fresh clone gives
    `FileNotFoundError: [Errno 2] No such file or directory: 'data/expenses.csv'` for all three
    tests. The numbers are a second problem: 412.5 is a fact about one person's spending this month,
    not a rule. The fix is the course's whole approach: plain data for the core, one `tmp_path`
    test for the file.
    """,
)

# ---------------------------------------------------------------------------------------------
# Section 8
# ---------------------------------------------------------------------------------------------

mcq(
    35, "exam", ["read-tool-output", "judgement"], 8, "S8 slide 24", "slides", "run",
    """
    You run coverage on the demo at v0.4:

    ```console
    $ uv run pytest --cov=expense_tracker --cov-report=term-missing
    ...
    Name                              Stmts   Miss  Cover   Missing
    ---------------------------------------------------------------
    src/expense_tracker/__init__.py       0      0   100%
    src/expense_tracker/cli.py           33     14    58%   36-39, 49-58
    src/expense_tracker/report.py        62      0   100%
    ---------------------------------------------------------------
    TOTAL                                95     14    85%
    ============================== 24 passed in 0.54s ==============================
    ```

    In `cli.py`, lines 36–39 are the normal path of `report` (compute, format, print) and lines
    49–58 are the body of the `add` command. What is the most useful conclusion?
    """,
    (
        "No test runs the normal path of `report` or any of `add`; judge which deserves one",
        "\"The report lists lines no test ran. Use it to find what you forgot.\" Then judge: `report` is a coordinator.",
    ),
    [
        (
            "85% of the code is correct and the other 15% contains bugs",
            "Coverage says which lines ran, nothing about whether they are right. Uncovered lines may be fine; covered ones may be wrong.",
        ),
        (
            "`report.py` is fully tested, so no more tests of it are ever needed",
            "100% means every line ran. Whether every rule was checked depends on the asserts, which coverage cannot see.",
        ),
        (
            "CI will stay red until the total reaches 100%, so write tests for every missing line",
            "The demo's CI does not run coverage at all, and the slide says never to chase the number.",
        ),
    ],
    "c",
    """
    Coverage is a map, not a score. The Missing column is the useful part: here it shows that no
    test exercises `add`, or `report` on a file that can be read. You judge that information; you
    do not chase it. The slide-18 diagram puts a coordinator at low benefit and high cost, and
    Checkpoint 2 allows one or two I/O tests, so one happy-path `CliRunner` run might be worth
    adding, and perhaps an `add` test with `monkeypatch` and `tmp_path`. The 100% on `report.py`
    says every line ran; it says nothing about whether an assert checked the result.
    """,
)

mcq(
    36, "beyond", ["read-tool-output", "read-code", "judgement"], 8, "S8 slide 24", "slides", "run",
    """
    The group's rule is *a final grade of 50 or more passes*. Their code, their tests and the
    coverage report:

    In `src/gradebook/grades.py`:

    ```python
    PASS_MARK = 50.0


    def final_grade(scores: list[float], weights: list[float]) -> float:
        total = 0.0
        for score, weight in zip(scores, weights, strict=True):
            total += score * weight
        return total


    def has_passed(grade: float) -> bool:
        return grade > PASS_MARK
    ```

    In `tests/test_grades.py`:

    ```python
    def test_final_grade_runs() -> None:
        grade = final_grade([80.0, 60.0], [0.5, 0.5])
        assert grade > 0


    def test_has_passed_gives_an_answer() -> None:
        assert has_passed(50.0) in (True, False)
    ```

    ```text
    Name                        Stmts   Miss  Cover   Missing
    ---------------------------------------------------------
    src/gradebook/__init__.py       0      0   100%
    src/gradebook/grades.py         8      0   100%
    ---------------------------------------------------------
    TOTAL                           8      0   100%
    ============================== 2 passed in 0.25s ===============================
    ```

    What does this show?
    """,
    (
        "Coverage counts lines that ran, not answers checked; `has_passed(50.0)` is actually `False`",
        "Every line ran, so 100%. But `grade > 0` and `in (True, False)` are true for almost any result, so the boundary bug passes unnoticed.",
    ),
    [
        (
            "The code is correct: 100% coverage with every test passing means every line was verified",
            "Run is not the same as verified. The asserts accept nearly any answer, so the tests verify almost nothing.",
        ),
        (
            "The coverage tool is wrong: the line with `>` should be listed as missing",
            "The line did run, when `has_passed(50.0)` was called. Coverage reports that correctly; it just cannot judge the assert.",
        ),
        (
            "The tests are fine but should compare grades with `pytest.approx`, since grades are floats",
            "A tolerance does not fix an assert that cannot fail. The tests need exact expected values, such as 70.0 and `True` at 50.",
        ),
    ],
    "d",
    """
    "100% coverage with weak assertions proves nothing. Never chase the number." Both tests call the
    functions, so every line runs and the report says 100%. But `assert grade > 0` passes for any
    positive result, and `assert has_passed(50.0) in (True, False)` passes for any boolean: they
    cannot fail. Running the code shows `has_passed(50.0)` returns `False`, which breaks the agreed
    rule. Strong tests would assert exact answers: `final_grade([80.0, 60.0], [0.5, 0.5])` equals
    `pytest.approx(70.0)`, and `has_passed(50.0)` is `True`, which would fail and expose the `>`.
    """,
)

mcq(
    37, "beyond", ["read-tool-output", "judgement"], 8, "S8 slides 5 and 24", "slides", "run",
    """
    A teammate broke `largest_expense` so that it returns the *smallest* expense:

    ```diff
    -        if largest is None or expense.amount > largest.amount:
    +        if largest is None or expense.amount < largest.amount:
    ```

    Their new test, and what the tools say:

    ```python
    def test_largest_expense() -> None:
        expenses = [
            Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
            Expense("2025-07-02", "Zara", "clothing", 40.0),
        ]
        largest_expense(expenses)
    ```

    ```console
    $ uv run pytest -q tests/test_largest.py
    .                                                                        [100%]
    1 passed in 0.00s
    $ uv run ruff check .
    All checks passed!
    $ uv run mypy src tests
    Success: no issues found in 7 source files
    ```

    What does this passing test prove?
    """,
    (
        "Only that `largest_expense` runs to the end without raising an exception",
        "With no `assert`, the test can fail only if the call crashes. The wrong answer comes back and is ignored.",
    ),
    [
        (
            "That `largest_expense` returns the Zara expense, because pytest checks return values for you",
            "pytest checks nothing on its own; only `assert` statements can fail a test.",
        ),
        (
            "Nothing at all, because pytest skips a test that contains no `assert`",
            "It was not skipped: the dot and `1 passed` show it ran. It proves very little, but not nothing.",
        ),
        (
            "That the bug must be elsewhere, because ruff and mypy pass as well",
            "ruff checks style and mypy checks types. Neither knows which expense is the largest.",
        ),
    ],
    "b",
    """
    A test passes when it reaches its end without an exception. With no `assert`, the only way this
    test can fail is a crash, so it passes with the broken function and would pass with the correct
    one too. It also counts every line of `largest_expense` as covered, which is why the slide warns
    that coverage with weak assertions proves nothing. The demo's real tests,
    `test_largest_expense_is_the_biggest_amount` and `test_largest_expense_tie_goes_to_the_first`,
    fail against this change, because they assert the exact expense. Seeing a new test fail once
    (red) would have exposed this test as empty.
    """,
)

mcq(
    38, "core", ["concept"], 8, "S8 slide 25", "slides", "source",
    """
    ```python
    from hypothesis import given, strategies as st

    @given(st.lists(st.floats(min_value=0, max_value=1e6)))
    def test_total_never_negative(amounts: list[float]) -> None: ...
    ```

    How is this test different from the example-based tests in `tests/test_report.py`?
    """,
    (
        "It states a property for any input, and `hypothesis` invents the inputs",
        "\"Instead of examples, you state a property and the library invents hundreds of inputs.\"",
    ),
    [
        (
            "It replays the inputs that real users typed into the program during the last week",
            "The inputs are generated from the strategy (lists of floats from 0 to a million), not recorded from users.",
        ),
        (
            "It measures how many lines of `report.py` the test suite runs",
            "That is coverage, a different tool (`pytest-cov`) with a different question.",
        ),
        (
            "It runs the same three hand-picked cases as `parametrize`, only in parallel",
            "With `parametrize` you write the table of cases. Here you write no cases at all; the library chooses them.",
        ),
    ],
    "a",
    """
    Example-based tests check inputs you chose: an empty list, a refund, an amount equal to the
    minimum. A property-based test states something that must be true for every input in a range,
    such as "the total of non-negative amounts is never negative", and `hypothesis` generates many
    inputs (including awkward ones you might not think of) looking for one that breaks it. The slide
    presents it as "a pointer": "Not required. For the curious." The edge-case table remains the
    course's main tool.
    """,
)

# ---------------------------------------------------------------------------------------------
# Section 9
# ---------------------------------------------------------------------------------------------

mcq(
    39, "exam", ["read-tool-output", "judgement"], 9, "S8 slide 28; labs/08-tdd.md troubleshooting; S7 slide 11", "lab", "run",
    """
    `uv run pytest` is green on your laptop, but the **Types** step of CI is red. You run both
    commands locally:

    ```console
    $ uv run pytest -q
    ........................                                                 [100%]
    24 passed in 0.04s
    $ uv run mypy src tests
    tests/test_duplicates.py:25: error: Function is missing a return type annotation  [no-untyped-def]
    tests/test_duplicates.py:25: note: Use "-> None" if function does not return a value
    Found 1 error in 1 file (checked 6 source files)
    ```

    What should you do?
    """,
    (
        "Add `-> None` to the test on line 25, since CI type-checks tests strictly",
        "One of the three that bite: pytest alone passes, strict mypy does not. Every `def test_...()` needs `-> None`.",
    ),
    [
        (
            "Change the CI step to `mypy src`, so that tests are no longer type-checked",
            "That weakens the referee for everyone. Session 7 turned strict on for tests on purpose.",
        ),
        (
            "Add `# type: ignore` at the end of line 25 to get the check green",
            "It hides the message instead of fixing a one-word cause. The note even tells you the fix.",
        ),
        (
            "Rerun the workflow: pytest passed, so the failure must be on GitHub's side",
            "The same error appears locally. mypy is deterministic; rerunning changes nothing.",
        ),
    ],
    "d",
    """
    Slide 28: "`-> None` missing on a test. Strict mypy: Function is missing a return type
    annotation. CI is red; pytest alone passes." CI runs `mypy src tests` with `strict = true`, so
    a test function without a return annotation is an error even though the test itself passes.
    mypy's note gives the fix in words: a function that returns nothing is annotated `-> None`.
    Session 7 warned it in advance: "Every `def test_...()` needs `-> None`."
    """,
)

mcq(
    40, "exam", ["read-tool-output", "judgement"], 9, "labs/08-tdd.md troubleshooting; S4 uv run", "lab", "run",
    """
    You clone the group repo into a new folder and type `pytest`, which runs a copy you installed
    globally weeks ago:

    ```console
    $ pytest -q

    ==================================== ERRORS ====================================
    __________________ ERROR collecting tests/test_duplicates.py ___________________
    ImportError while importing test module 'tests/test_duplicates.py'.
    ...
    E   ModuleNotFoundError: No module named 'expense_tracker'
    ______________________ ERROR collecting tests/test_io.py _______________________
    ImportError while importing test module 'tests/test_io.py'.
    ...
    E   ModuleNotFoundError: No module named 'typer'
    ____________________ ERROR collecting tests/test_report.py _____________________
    ImportError while importing test module 'tests/test_report.py'.
    ...
    E   ModuleNotFoundError: No module named 'expense_tracker'
    =========================== short test summary info ============================
    ERROR tests/test_duplicates.py
    ERROR tests/test_io.py
    ERROR tests/test_report.py
    !!!!!!!!!!!!!!!!!!! Interrupted: 3 errors during collection !!!!!!!!!!!!!!!!!!!!
    3 errors in 0.04s
    ```

    What should you do next?
    """,
    (
        "Run `uv sync`, then `uv run pytest`, inside the project's environment",
        "The lab's fix: the project's virtual environment has your package and `typer`; a global `pytest` sees neither.",
    ),
    [
        (
            "Move `src/expense_tracker` to the top of the repository so Python can find it",
            "That breaks the `src/` layout to work around running the wrong `pytest`. The environment is the problem.",
        ),
        (
            "Install `typer` into the global Python and run `pytest` again",
            "It patches one symptom: `expense_tracker` is still missing, and the versions would not come from `uv.lock`.",
        ),
        (
            "Delete `tests/test_io.py`, since it needs a package the other tests do not",
            "`typer` is a dependency of the project. Deleting tests to get past an environment problem loses real checks.",
        ),
    ],
    "c",
    """
    The lab's troubleshooting table: "`ModuleNotFoundError` for your package: run `uv sync`, and use
    `uv run pytest`, not bare `pytest`." A globally installed `pytest` runs in a Python that has
    neither your package nor its dependencies. `uv sync` builds the project's `.venv` from
    `uv.lock`, including your own package, and `uv run` runs the command inside it: the same
    environment CI builds. Every fix that edits the repository treats a set-up problem as a code
    problem.
    """,
)

mcq(
    41, "hard", ["read-tool-output", "judgement"], 9, "labs/08-tdd.md troubleshooting; S5 exit codes", "lab", "run",
    """
    A teammate adds the group's first tests in `tests/pricing_tests.py`:

    ```python
    def test_one_hour_costs_two_euros() -> None:
        assert price_for(60) == 2.0
    ```

    ```console
    $ uv run pytest -q

    no tests ran in 0.00s
    $ echo $?
    5
    ```

    They say: "Nothing failed, so CI will be green." Which response is right?
    """,
    (
        "The file name does not match `test_*.py`, and exit code 5 makes CI fail",
        "Renaming the file to `test_pricing.py` makes pytest collect it (`1 passed`, exit code 0).",
    ),
    [
        (
            "They are right: no test failed, so pytest exits successfully and CI passes",
            "`echo $?` shows 5, and 0 is the only exit code that means success to CI.",
        ),
        (
            "pytest found the test but skipped it, because skipped tests are not counted as run",
            "Nothing was skipped; nothing was found. A skipped test would be reported as skipped.",
        ),
        (
            "Exit code 5 means a package is missing; run `uv sync` and try again",
            "A missing package shows `ModuleNotFoundError` while collecting. Here nothing was collected at all.",
        ),
    ],
    "b",
    """
    The lab's first troubleshooting row: "`no tests ran`, exit code 5: pytest found no test: file not
    in `tests/`, or not named `test_*.py`, or function not named `test_*`." `pricing_tests.py` does
    not match, so pytest collected nothing. Session 5's rule then applies: 0 means success, anything
    else means failure, and "every tool downstream reads that number: the shell, `&&`, CI". A suite
    that runs no tests must not count as green, and it does not.
    """,
)

mcq(
    42, "hard", ["read-tool-output", "judgement"], 9, "S8 slide 28; labs/08-tdd.md troubleshooting", "lab", "run",
    """
    This test passes on your laptop:

    ```python
    def test_dining_total_is_right() -> None:
        expenses = read_expenses("data/expenses.csv")
        totals = dict(total_by_category(expenses, category="", minimum=0.0))
        assert totals["dining"] == 412.5
    ```

    In CI, on a fresh clone:

    ```text
        def read_expenses(path: str) -> list[Expense]:
            expenses: list[Expense] = []
    >       with open(path) as handle:
    E       FileNotFoundError: [Errno 2] No such file or directory: 'data/expenses.csv'

    src/expense_tracker/report.py:25: FileNotFoundError
    FAILED tests/test_laptop.py::test_dining_total_is_right - FileNotFoundError: ...
    ```

    The repository's `.gitignore` contains `data/`. Which fix is best?
    """,
    (
        "Build the data inside the test, or in `tmp_path`, with totals you can check by hand",
        "Slide 28: \"Use `tmp_path`, or build the data inside the test.\" The test then runs the same on every machine.",
    ),
    [
        (
            "Commit `data/expenses.csv` to the repository so that CI has the same file as your laptop",
            "`data/` is ignored on purpose: it is personal data in a public repository, and it changes every time someone runs `add`.",
        ),
        (
            "Pin CI's Python version to the exact one installed on your laptop, so both run the same way",
            "The error is a missing file, not a version difference. The same Python would fail the same way.",
        ),
        (
            "Catch `FileNotFoundError` inside the test and let it pass when the file is missing",
            "A test that passes when it cannot check anything turns a red CI into a false green.",
        ),
    ],
    "a",
    """
    "Tests that need your laptop. A test that reads `data/expenses.csv` passes only on your machine."
    CI clones the repository, and `data/` is in `.gitignore`, so the file does not exist there. Even
    on your laptop the test is fragile: 412.5 changes whenever you add an expense. Building a few
    `Expense` values in the test checks the totals rule with numbers anyone can verify; one
    `tmp_path` test can cover reading a file, if that is what you want to check.
    """,
)

mcq(
    43, "exam", ["read-tool-output", "judgement"], 9, "labs/08-tdd.md troubleshooting; S8 slide 29", "lab", "run",
    """
    It is 13:10 on the day of Checkpoint 2:

    ```console
    $ git log --oneline -3
    40c019e (HEAD -> main, origin/main) Add -> None to the new tests
    53f51dc (tag: v0.2) Add tests for the core
    0b73bc9 Split the fare rules out of the CLI
    ```

    The Actions tab shows a red run for `53f51dc` and a green run for `40c019e`. Checkpoint 2 is
    marked at your group's `v0.2` tag (not the demo's). What is the situation?
    """,
    (
        "The tag marks the red `53f51dc`; move it to the green `40c019e` and push it",
        "The lab: \"CI is green but `git tag` points at an older commit: tag the commit CI approved.\"",
    ),
    [
        (
            "Nothing to do: the latest commit on `main` is green, and that is what gets marked",
            "Checkpoint 2 is \"marked at the `v0.2` tag\", not at the newest commit.",
        ),
        (
            "Push an empty commit so that CI runs again on `53f51dc` and turns it green",
            "CI's verdict on `53f51dc` will not change: the missing `-> None` is still in that commit.",
        ),
        (
            "Delete the red run from the Actions tab so that only green runs are visible",
            "Hiding the run does not change the code at the tag. The tagged commit still fails the checks.",
        ),
    ],
    "c",
    """
    A tag is a name fixed to one commit. Here `v0.2` was put on `53f51dc` before the `-> None` fix,
    so the tagged commit is red even though `main` is now green. Checkpoint 2's first item asks for
    "CI green on the v0.2 commit", and "a missing tag means nothing to mark". The lab's last
    troubleshooting row gives the move: find the commit CI approved with `git log --oneline` and tag
    that hash, then push the tag.
    """,
)

open_q(
    44, "hard", ["read-tool-output", "judgement"], 9,
    "S8 slides 7–9; labs/08-tdd.md troubleshooting", "lab", "run",
    """
    You pull a teammate's branch and run the suite (output trimmed):

    ```console
    $ uv run pytest -q
    FE.......FF...............                                               [100%]
    ==================================== ERRORS ====================================
    ___________________ ERROR at setup of test_meals_and_clothes ___________________
      def test_meals_and_clothes(meal: list[Expense]) -> None:
    E       fixture 'meal' not found
    =================================== FAILURES ===================================
    ____________________________ test_two_meals_add_up _____________________________
    >       assert total == 30.3
    E       assert 30.299999999999997 == 30.3

    tests/test_branch.py:16: AssertionError
    ____________ test_totals_are_grouped_by_category_and_largest_first _____________
    >       assert result == [("clothing", 40.0), ("dining", 15.0), ("transport", 15.0)]
    E       AssertionError: assert [('dining', 1...thing', 40.0)] == [('clothing',...sport', 15.0)]
    E         At index 0 diff: ('dining', 15.0) != ('clothing', 40.0)

    tests/test_report.py:24: AssertionError
    ___________ test_equal_totals_keep_the_order_they_first_appeared_in ____________
    >       assert [name for name, _ in result][1:] == ["dining", "transport"]
    E       AssertionError: assert ['transport', 'clothing'] == ['dining', 'transport']
    E         At index 0 diff: 'transport' != 'dining'

    tests/test_report.py:30: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_branch.py::test_two_meals_add_up - assert 30.29999999999999...
    FAILED tests/test_report.py::test_totals_are_grouped_by_category_and_largest_first
    FAILED tests/test_report.py::test_equal_totals_keep_the_order_they_first_appeared_in
    ERROR tests/test_branch.py::test_meals_and_clothes
    3 failed, 22 passed, 1 error in 0.05s
    ```

    The branch's file `tests/test_branch.py` defines a fixture called `meals`.
    """,
    [
        {
            "prompt": "What does the last line tell you, and how is an error different from a failure?",
            "marks": 1,
            "model": "Three tests ran and failed, 22 passed, and one could not run at all. A failure is an assert that came out false; an error means the test never started, here because pytest could not find its fixture.",
            "rubric": [
                "Distinguishes a failure (an assert was false) from an error (the test could not start, a set-up problem)",
            ],
            "weak": "'Four tests failed' merges the two kinds. An error is not a failed check: the test's body, and its assert, never ran, so it says nothing about the code yet. 'Three failed, so three bugs' also skips the step of reading which side of each assert is wrong.",
        },
        {
            "prompt": "For each problem (the error, the float failure, the two ordering failures), say whether the test or the code is wrong, and give your evidence.",
            "marks": 3,
            "model": "The error is a test typo: it asks for `meal`, the fixture is `meals`. The float failure is a test problem: the sum is right, so use `pytest.approx`. The two ordering failures are one code bug: the totals are right but the smallest comes first, against the test name.",
            "rubric": [
                "The error: a typo in the test (`meal` against `meals`), not a problem in the code",
                "The float failure: the sum is right, so the test should compare with `pytest.approx`",
                "The ordering failures: the code is wrong (smallest first instead of largest first), and both share that one cause",
            ],
            "weak": "Calling all three 'bugs in the code' is the careless reading. Treating the two ordering failures as two separate problems doubles the work. For the ordering, the evidence is the test name or the README, not 'the test must be right'.",
        },
        {
            "prompt": "In which order would you work through them, and what do you do after each fix?",
            "marks": 2,
            "model": "The two quick test fixes first, so those tests really check something, then the sort, which clears both ordering failures. Rerun after each change and check that the counts drop as expected.",
            "rubric": [
                "A justified order that treats the two ordering failures as one fix (quick test fixes first, or the real bug first because it matters most)",
                "Reruns the suite after each fix and checks that the change had the expected effect",
            ],
            "weak": "'Fix everything, then run once' throws away what each run tells you. 'Rerun until it passes' is never a step. Changing the ordering tests to expect smallest first would make the suite green and the program wrong.",
        },
    ],
    "6–8",
    """
    A realistic report mixes kinds of problem, and the skill is sorting them. pytest separates
    errors (could not run) from failures (ran and disagreed), and shows both sides of every failed
    assert. Two of the four problems are in the tests: a fixture typo ("pytest matches fixtures by
    name") and a float comparison ("Use `pytest.approx`"). The other two are one bug in the code,
    visible because the totals match but the order does not. Reading the diff, not just the count,
    is what tells you this.
    """,
)

# ---------------------------------------------------------------------------------------------
# Added after review: q45 (s7), q46 (s5), q47 (s9), q48 (s3)
# ---------------------------------------------------------------------------------------------

mcq(
    45, "exam", ["judgement"], 7, "labs/08-tdd.md step 3; S8 slides 23 and 29", "lab", "source",
    """
    Your group's template came with four tests in `tests/test_cli.py` that use `CliRunner` on the
    template's example commands. You have written five tests of your own pure pricing functions,
    two of them on a boundary. All nine pass and CI is green. A teammate wants to tag `v0.2` now:
    "Nine tests, Checkpoint 2 done." Following the lab, what should you do before tagging?
    """,
    (
        "Keep one or two `CliRunner` tests for your own commands; replace the rest with pure tests",
        "The lab: the template's tests \"count towards your 8, but they are I/O tests, so they count against 'mostly pure'\". Item 3 allows at most one or two.",
    ),
    [
        (
            "Tag now: the template's tests count towards the eight, and all nine of them pass",
            "They do count for item 1, but four I/O tests break item 3's \"at most one or two\", and they test the template's commands, not yours.",
        ),
        (
            "Delete all four `CliRunner` tests, because tests that came with the template never count",
            "They count. Deleting all four leaves five tests, below item 1's eight, and the lab wants one or two tests at your I/O edge.",
        ),
        (
            "Rewrite the four `CliRunner` tests to use `tmp_path` instead, so that they count as pure tests",
            "Slide 23 counts `tmp_path` as an I/O test too. Swapping one I/O tool for another changes nothing.",
        ),
    ],
    "d",
    """
    Checkpoint 2 has three binary items: at least 8 passing tests with CI green at `v0.2`, at least
    2 edge-case tests, and most tests on pure functions with at most one or two using `tmp_path`,
    `CliRunner` or `monkeypatch`. Nine passing tests with two boundaries meet the first two. Four
    template `CliRunner` tests break the third, and they check the template's commands rather than
    your own. The lab says what to do: keep one or two, rewrite them for your commands, and replace
    the rest with pure tests so the count stays at eight or more.
    """,
)

open_q(
    46, "exam", ["read-diff", "compare"], 5,
    "expense-tracker 1e421bc; S8 slides 14–15; sample Q8 shape", "teacher-variant", "run",
    """
    A teammate shows you this commit from the expense-tracker history. The commit before it,
    `e1b96de`, added five tests for `remove_duplicates`, two of which failed, and a stub that returned
    `expenses` unchanged.

    ```diff
     def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
    -    return expenses
    +    seen: set[Expense] = set()
    +    unique: list[Expense] = []
    +    for expense in expenses:
    +        if expense not in seen:
    +            seen.add(expense)
    +            unique.append(expense)
    +    return unique
    ```

    Two candidate commit messages:

    - A: `Make the tests pass`
    - B: `Remove duplicates with a seen-set`
    """,
    [
        {
            "prompt": "What does this change do?",
            "marks": 1,
            "model": "It replaces the stub with real code: it keeps each expense the first time it appears and skips later exact copies, so duplicates are dropped and the order is kept.",
            "rubric": [
                "Says exact duplicates are now dropped, keeping the first copy of each expense in its original order",
            ],
            "weak": "'It adds a loop and a set' narrates the code without saying what comes out. A full answer names the result: the same list without exact duplicates, first copy kept, order unchanged. Calling it a bug fix misreads the history: the commit before was a deliberate red step.",
        },
        {
            "prompt": "Which message is better for someone reading the history six months later, and why?",
            "marks": 2,
            "model": "B. It says what the code now does and still makes sense on its own in `git log --oneline`. A describes the tests rather than the change: any green step could carry it, so later nobody knows what behaviour arrived here.",
            "rubric": [
                "Chooses B because it names the behaviour added (removing duplicates) and how (a seen-set)",
                "Explains why A fails the later reader: it describes the state of the tests, not the change, and would fit any green commit",
            ],
            "weak": "'B is longer' or 'B sounds more professional' gives no reason. 'A is fine because in TDD the goal is green' answers for the author on the day, not for the reader of the history. Judge a message by whether it makes sense with only `git log --oneline` in front of you.",
        },
        {
            "prompt": "The five tests cover an empty list, a list with no duplicates, one exact duplicate, the same merchant on another day, and three copies. Name one more test you would add, in words, and say what it expects.",
            "marks": 2,
            "model": "A Zara purchase of 40.00 and a Zara refund of -40.00 on the same day: both are kept, because the amount differs. It checks that all four fields decide what counts as a duplicate.",
            "rubric": [
                "Names a concrete input the five tests do not cover, such as two expenses equal in three fields but not the fourth (a purchase and its refund, or `dining` against `Dining`)",
                "States the expected result (both kept, or exactly which one is kept), so the test can fail",
            ],
            "weak": "'Test more duplicates' or 'test edge cases' is not a test: give the input and the expected list. 'Read `expenses.csv` and expect 414' is an I/O test tied to one data file, and it already passes. Repeating one of the five existing cases earns nothing.",
        },
    ],
    "5–8",
    """
    Sample Q8's compare shape, applied to the TDD history. The diff is the green step of the live
    cycle: the smallest code that makes the red tests from `e1b96de` pass ("Not elegant. Nobody
    asked for elegant yet."). A commit message is read later, by someone who was not there, usually
    in `git log --oneline`. B names the behaviour and the approach, so a reader can find where
    duplicate removal arrived; A only says the tests went green, which every green commit could
    say. For the extra test, ask which fields make two expenses equal. A run on `1e421bc` confirms
    that a 40.00 purchase and a -40.00 refund at Zara on the same day are both kept, because the
    dataclass compares all four fields.
    """,
    variant_of="sample-paper-q08",
)

mcq(
    47, "beyond", ["read-tool-output", "judgement"], 9,
    "S8 slides 22 and 28; expense-tracker cli.py (add --date)", "slides", "run",
    """
    On 9 October a teammate added this test for the demo's `add` command. It passed, and CI was
    green.

    ```python
    def test_add_appends_the_new_row(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)

        runner.invoke(app, ["add", "Bar Ramon", "dining", "12.50"])

        lines = (tmp_path / "data" / "expenses.csv").read_text().splitlines()
        assert lines[-1] == "2026-10-09,Bar Ramon,dining,12.50"
    ```

    On 14 October, with no code changed, CI is red:

    ```text
    >       assert lines[-1] == "2026-10-09,Bar Ramon,dining,12.50"
    E       AssertionError: assert '2026-10-14,B...,dining,12.50' == '2026-10-09,B...,dining,12.50'
    E         - 2026-10-09,Bar Ramon,dining,12.50
    E         ?         ^^
    E         + 2026-10-14,Bar Ramon,dining,12.50
    E         ?         ^^

    tests/test_add.py:17: AssertionError
    FAILED tests/test_add.py::test_add_appends_the_new_row - AssertionError: asse...
    ```

    `add` takes an optional `--date`; without it, the row gets today's date. Which fix is best?
    """,
    (
        "Pass `--date 2026-10-09` in the test, so the row no longer depends on the day",
        "Part of the input came from the clock, not from the test. Fixing the date puts everything the result depends on inside the test, so it passes on any day and any machine.",
    ),
    [
        (
            "Change the expected date to `2026-10-14`, the date `add` wrote on this run",
            "That is green until midnight. The expectation still depends on the day the suite runs, so it fails again tomorrow.",
        ),
        (
            "Set CI's clock to Madrid time, since GitHub's machines run in another time zone",
            "A time zone moves the date by one day at most, and this is five days off. The same test fails on your laptop today too.",
        ),
        (
            "Delete the test, since a command that writes a file cannot be tested reliably",
            "Slide 22 tests `add` exactly this way, with `tmp_path` and `monkeypatch`. The file part works; only the unstated date is the problem.",
        ),
    ],
    "a",
    """
    This is "tests that need your laptop" one step further: a test that needs a particular day.
    Without `--date`, `add` writes `datetime.date.today().isoformat()`, so the row changes every day, and the
    expected string was true only on 9 October. In the diff, the `+` line is what `add` wrote on
    this run and the `-` line is what the test expected. Passing `--date 2026-10-09` makes the test
    build all of its own input, as slide 28 asks, so it gives the same answer on any day and any
    machine. Updating the expected date only moves the failure to tomorrow, and deleting the test
    throws away the one I/O test of `add` that slide 22 demonstrates.
    """,
)

mcq(
    48, "core", ["concept", "read-code"], 3, "S8 slide 10; labs/08-tdd.md step 2", "slides", "run",
    """
    Your gradebook has three tests that differ only in their numbers:

    ```python
    def test_49_fails() -> None:
        assert not has_passed(49.0)


    def test_50_passes() -> None:
        assert has_passed(50.0)


    def test_72_passes() -> None:
        assert has_passed(72.0)
    ```

    A teammate wants one test instead of three. Which change does that, and still reports each
    grade as its own case when one fails?
    """,
    (
        "Use `@pytest.mark.parametrize` with one row per grade and its expected answer",
        "One test, many cases: pytest runs each row as its own test with its values in the id, such as `[50.0-True]`, so a failing row is named and the other rows still run.",
    ),
    [
        (
            "Put the three grades in a fixture and let each of the three tests ask for it",
            "A fixture shares data between tests; it does not run one test over several cases, so the three tests stay written out.",
        ),
        (
            "Merge them into one test that loops over the three grades and asserts each",
            "A loop is still one test: the first failing grade stops it, the grades after it never run, and the `FAILED` line names only that one test.",
        ),
        (
            "Keep only the 72.0 test, because all three check the same pass rule",
            "50.0 is the boundary and 49.0 sits just below it: they are the cases that catch `>` written for `>=`. Dropping them leaves only the happy path.",
        ),
    ],
    "b",
    """
    Slide 10: "`parametrize`: one test, many cases." The lab says to use it "when the only
    difference between tests is the numbers", which is this situation. pytest runs the test once
    per row and reports each row separately. A run with `has_passed` written as
    `grade > PASS_MARK` shows `FAILED tests/test_param.py::test_pass_mark[50.0-True]` while the
    49.0 and 72.0 rows pass, so you see at once which grade broke. The same bug in a loop stops at
    50.0 and never checks 72.0; a fixture shares data but does not multiply cases.
    """,
)

# ---------------------------------------------------------------------------------------------
# Added by the calibration pass
# ---------------------------------------------------------------------------------------------

open_q(
    49, "hard", ["read-diff", "compare", "judgement"], 2,
    "S8 slides 3, 6; sample Q4 and Q8 shapes; run in calibration-fix/td", "teacher-variant", "run",
    """
The members' group has a rule in its backlog: "members get a 5% discount". A teammate pushes this commit, and CI is green:

```diff
diff --git a/src/members/pricing.py b/src/members/pricing.py
index 1107c68..e3dd365 100644
--- a/src/members/pricing.py
+++ b/src/members/pricing.py
@@ -1,4 +1,4 @@
-DISCOUNT_RATE = 0.05
+DISCOUNT_RATE = 0.10
 
 
 def apply_discount(price: float) -> float:
diff --git a/tests/test_pricing.py b/tests/test_pricing.py
index 8b8d87e..0b98ab0 100644
--- a/tests/test_pricing.py
+++ b/tests/test_pricing.py
@@ -2,4 +2,4 @@ from members.pricing import apply_discount
 
 
 def test_member_discount_is_five_percent() -> None:
-    assert apply_discount(100.0) == 95.0
+    assert apply_discount(100.0) == 90.0
```

Two candidate commit messages:

- A: `Fix test`
- B: `Raise the member discount to 10% and update its test`
""",
    [
        {
            "prompt": "What does the commit do?",
            "marks": 1,
            "model": "It raises `DISCOUNT_RATE` from 5% to 10% and changes the test's expected price from 95 to 90, so the test passes with the new rate.",
            "rubric": ["Says the rate changed from 0.05 to 0.10 and the expected value in the test changed with it"],
            "weak": "\"It fixes a test\" describes the smaller half. The rate in the code changed too, and that is the change a customer feels.",
        },
        {
            "prompt": "The code and its test changed in the same commit. Why should a reviewer be careful, and what evidence do you ask for before accepting it?",
            "marks": 2,
            "model": "A test is the specification. If the expected value is edited together with the code, the test agrees with whatever the code now does, so it cannot catch a mistake. I would ask for the backlog item or the Product Owner's decision that moves the discount to 10%.",
            "rubric": [
                "Says the test no longer independently checks the code, because both were changed to agree",
                "Asks for evidence outside the commit: the backlog item or the Product Owner's decision",
            ],
            "weak": "\"The test passes, so it is fine\" is the trap: it passes because it was edited to pass. \"Run it again\" gives the same answer. The marks are for asking which of the two, test or code, matches what is supposed to happen.",
        },
        {
            "prompt": "Which message is better for someone reading the history six months later, and what else in the diff is now misleading?",
            "marks": 2,
            "model": "B. It says the rule changed, so a reader looking for when the discount moved finds it. A suggests the test was wrong, which hides a change in behaviour. The test's name still says five percent, so it now describes the wrong rule.",
            "rubric": [
                "Chooses B because it names the behaviour change; A calls it a test fix",
                "Spots that the test name still says five percent",
            ],
            "weak": "\"B is longer\" is not a reason. Missing the stale test name loses the second mark: a test that documents a rule with the wrong number is documentation that lies.",
        },
    ],
    "5–8",
    """
Sample Q4 and Q8 together. A failing test after a change cannot tell you who is wrong, and here the test did not fail: it was edited to pass. When the expected value and the code move in the same commit, green means nothing until you know the rule changed on purpose. The evidence is the backlog item (session 4) or the Product Owner's decision, not the test. We ran both versions: with the old test the new code fails, with the edited test it passes. B's message says what a reader needs, and the leftover test name `test_member_discount_is_five_percent` is a small lie that a careful reviewer catches.
""",
    variant_of="sample-paper-q08",
)

mcq(
    50, "core", ["read-code"], 2, "S8 slide 6", "slides", "reasoning",
    """
```python
def test_total_of_all_categories() -> None:
    expenses = [
        Expense("2025-07-01", "Bar Ramon", "dining", 10.0),
        Expense("2025-07-02", "Zara", "clothing", 40.0),
    ]
    assert sum(amount for _, amount in total_by_category(expenses, "", 0.0)) == 50.0
```

Which part of this test is the Act?
""",
    ("The call to `total_by_category`, written inside the `assert` line",
     "The Act is the moment the code under test runs. Here it is hidden in the assert: separating it as `result = total_by_category(...)` makes the three steps visible."),
    [
        ("The list of expenses, because it is what the test does to the code",
         "Building the data is the Arrange. The Act is the call to the function under test."),
        ("The `sum(...)`, because it computes the number the test checks",
         "`sum` is the test's own arithmetic on the result, part of the Assert. The code under test is `total_by_category`."),
        ("There is no Act: a test with a single `assert` only has an Assert",
         "Every test calls something. The call is just written on the same line as the assert, which is why the three steps blur."),
    ],
    "c",
    """
Slide 6's pattern is Arrange (build the data), Act (call the code under test), Assert (check the result). In this test the Arrange is the list, the Act is the call to `total_by_category`, and the Assert is the comparison with 50.0. They are all there, but the Act sits inside the Assert, so a failure message shows a number and not the result that produced it. Writing `result = total_by_category(expenses, "", 0.0)` on its own line and then `assert sum(...) == 50.0` costs one line and makes the test readable at a glance. We ran the test: it passes either way.
""",
)

mcq(
    51, "exam", ["read-code", "judgement"], 2, "S8 slides 6-7; run in calibration-fix/td", "slides", "run",
    """
```python
def test_report_pieces() -> None:
    totals = total_by_category(EXPENSES, "", 0.0)
    assert totals == [("clothing", 40.0), ("dining", 15.0)]
    largest = largest_expense(EXPENSES)
    assert largest == EXPENSES[1]
```

This test passes. Which change makes it better?
""",
    ("Split it into two tests, one per function, each with one Act and one Assert",
     "When it fails, the name of the test says which behaviour broke. As written, a failure on the first assert hides whether the second would have passed."),
    [
        ("Merge the two asserts into one, `assert (totals, largest) == (..., ...)`, to keep it short",
         "A single assert on a pair gives a harder message, not a clearer one, and the test still checks two things."),
        ("Turn it into a `parametrize` test with one row for `totals` and one for `largest`",
         "`parametrize` runs the same test on different numbers. These two checks call different functions, so there is nothing to share."),
        ("Add a comment above each assert saying what it checks",
         "A comment that restates what the code does is the course's example of a failure of naming. Two tests with two names say it better."),
    ],
    "b",
    """
Slide 6 gives each test one Arrange, one Act and one Assert, so that its name can state one behaviour. This test has two Acts and two Asserts: the totals and the largest expense. If the first assert fails, pytest stops there and the second never runs, so you learn nothing about the largest expense. Split into `test_totals_are_grouped_by_category` and `test_largest_expense_is_the_biggest_amount`, each failure points at one rule. `parametrize` is for one behaviour on several inputs, not for two behaviours. We ran the original: it passes.
""",
)

mcq(
    52, "exam", ["read-tool-output", "judgement"], 8, "S8 slides 17, 24; expense-tracker d38d9e6 (run with pytest-cov)", "history", "run",
    """
The demo at commit `d38d9e6`, "Test the pure core", has 17 passing tests, all of them for the functions in `report.py` that take and return plain data. Coverage prints:

```console
$ uv run pytest --cov=expense_tracker --cov-report=term-missing
...
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/expense_tracker/__init__.py       0      0   100%
src/expense_tracker/cli.py           33     33     0%   1-58
src/expense_tracker/report.py        60      8    87%   24-38
---------------------------------------------------------------
TOTAL                                93     41    56%
============================== 17 passed in 0.03s ==============================
```

Lines 24 to 38 of `report.py` are the body of `read_expenses`. What is the most useful reading?
""",
    ("The pure functions are tested; the parts that touch the world are not yet: file reading and the whole CLI need `tmp_path` and `CliRunner` tests",
     "That is the 2x2 diagram of slide 17 made visible. The Missing column points to the next tests, and the tools for them are slide 20 and slide 21."),
    [
        ("The code is 56% correct and 44% buggy, so the core has to be rewritten",
         "Coverage counts lines that ran during the tests, not lines that are right. Untested is not the same as wrong."),
        ("`cli.py` can be ignored: 0% means the file is unused and can be deleted",
         "`cli.py` holds the commands users type. No test runs it yet, which is exactly what the map is telling you."),
        ("CI will stay red until the total reaches 100%, so every missing line must be tested at once",
         "Coverage is \"a map, not a score\": the demo's CI does not require 100%, and its own v0.4 total is 85%."),
    ],
    "d",
    """
Slide 24: "Coverage is a map, not a score." The Missing column lists the lines no test ran, and here they fall exactly on the side of the program that touches the world: `read_expenses` opens a file, and `cli.py` is the shell. Slide 17's diagram says those need different tests from pure functions, and slides 20 and 21 give the tools: `tmp_path` for a file, `CliRunner` for a command. That is what the next commit, `f3d9870`, adds; with it the total reaches 85% and `report.py` reaches 100%. Run for real on commit `d38d9e6`.
""",
)

mcq(
    53, "core", ["concept"], 8, "S8 slide 25", "slides", "reasoning",
    """
Slide 25 points at property-based testing (`hypothesis`). Which of these tests states a property, something that should hold for any input, instead of checking one example?
""",
    ("For any list, `remove_duplicates` never lengthens it, and applying it twice changes nothing",
     "No single example is named: the claim is about every list, which `hypothesis` would test with inputs it invents."),
    [
        ("The empty list gives an empty report: `assert total_by_category([], \"\", 0.0) == []`",
         "One input and one expected output: an example, and a good edge case, but not a property."),
        ("One hand-picked list with one expected answer: `assert remove_duplicates([BAR, ZARA, BAR]) == [BAR, ZARA]`",
         "One hand-picked list with its expected answer: an example."),
        ("The larger of two expenses is Zara: `assert largest_expense([BAR, ZARA]) == ZARA`",
         "One hand-picked list again: an example of the rule, not the rule for all lists."),
    ],
    "c",
    """
An example-based test names an input and the exact output you expect. A property is a statement that should be true for any input of a kind, such as "removing duplicates never makes a list longer" or "doing it twice changes nothing". Slide 25 only points at the idea: `hypothesis` generates many inputs, including ones you would not think of, and checks the property on each. The course asks you to recognise the idea, not to write the tests. The three examples here are all useful tests; they pin down single cases.
""",
)

mcq(
    54, "exam", ["read-code", "judgement"], 3, "S8 slides 9-10; labs/08-tdd.md", "slides", "reasoning",
    """
`apply_discount` takes a price and returns it with the 5% member discount, and raises `ValueError` for a negative price. The group has four tests:

```python
def test_discount_of_100() -> None:
    assert apply_discount(100.0) == 95.0

def test_discount_of_200() -> None:
    assert apply_discount(200.0) == 190.0

def test_discount_of_zero() -> None:
    assert apply_discount(0.0) == 0.0

def test_negative_price_is_rejected() -> None:
    with pytest.raises(ValueError):
        apply_discount(-1.0)
```

Which use of `parametrize` fits best?
""",
    ("One parametrized test with the rows 100, 200 and 0; the negative price stays its own test",
     "The lab's rule: use `parametrize` when the only difference between the tests is the numbers. The first three differ only in price and expected result. The fourth expects an exception, a different shape."),
    [
        ("One parametrized test with all four rows, using the expected value `\"error\"` for the negative price",
         "That forces two behaviours into one test with an `if` inside it. A reader can no longer tell from the test's name what it checks."),
        ("No parametrize: separate tests are clearer, because `parametrize` hides which case failed",
         "It does the opposite. pytest reports each row separately, with its values in square brackets, so the failing case is named."),
        ("One parametrized test with the rows 100 and 200 only, because zero is an edge case that needs its own test",
         "Zero is an edge case, and a row is the cheapest way to test it. Its test differs from the others only in the numbers."),
    ],
    "b",
    """
Slide 10: "`parametrize`: one test, many cases". The lab says to use it "when the only difference between tests is the numbers". Three of the four tests are the same test with different data (price and expected price), including the zero edge case. The fourth has a different shape, since it expects an exception, so it stays on its own. With a parametrized test, pytest runs one test per row and reports each row separately, so a wrong expectation for 200 shows up as a failure of that row while the others pass.
""",
)

# ---------------------------------------------------------------------------------------------
# Terms, traps, flashcards
# ---------------------------------------------------------------------------------------------

TERMS = [
    ("Test-driven development (TDD)", "Writing the test before the code, in short red, green, refactor cycles, so the test states what 'done' means first.", 1),
    ("Red, green, refactor", "Red: a test for behaviour that does not exist, seen failing. Green: the smallest code that passes. Refactor: clean up while the tests stay green.", 1),
    ("Stub", "A placeholder version of a function that returns something deliberately wrong (`return expenses`), so the new tests can run and fail on behaviour instead of on an import.", 5),
    ("Arrange-Act-Assert", "The shape of a test: build the input, call the one function under test, compare the result with an answer worked out by hand.", 2),
    ("`assert`", "The statement that makes a test fail when it is false. On failure pytest shows the values on both sides; a test without one can only fail by crashing.", 2),
    ("`pytest.approx`", "Compares floats with a small tolerance, because `0.1 + 0.2 == 0.3` is `False`. Money in floats needs a tolerance.", 3),
    ("Fixture", "A function marked `@pytest.fixture` that pytest calls for you to build shared test data; a test asks for it by naming it as a parameter.", 3),
    ("`parametrize`", "`@pytest.mark.parametrize`: one test, many cases. pytest runs it once per row and reports each row separately, with its values in the test id.", 3),
    ("Edge case", "An input at the limits of what a function handles: empty, zero or a boundary, negative, duplicate, missing. Chosen on purpose because that is where code breaks.", 4),
    ("Happy path", "A normal input with a normal answer. The test everybody writes first, and the one least likely to find a bug.", 4),
    ("Pure function", "A function that takes values and returns values, with no file, no `print`, no `sys.exit`. It \"tests itself\": no set-up, no clean-up.", 6),
    ("Hashable", "Having a hash value, which set members and dictionary keys need. `@dataclass(frozen=True)` makes `Expense` hashable; a plain `@dataclass` is not.", 5),
    ("Coordinator", "Code that only wires other parts together (read, call the core, print). Low benefit and high cost to unit test on the slide-18 diagram.", 6),
    ("`tmp_path`", "A pytest fixture that gives each test a fresh, empty directory, deleted afterwards, for the one place you really need a file.", 7),
    ("`CliRunner`", "From `typer.testing`: runs the command-line app inside a test and returns a result with `exit_code`, `stdout` and `stderr`.", 7),
    ("`monkeypatch`", "A pytest fixture that changes the working directory, an environment variable or an attribute for one test and restores it afterwards.", 7),
    ("I/O test", "A test that touches the outside world through `tmp_path`, `CliRunner` or `monkeypatch`. Checkpoint 2 allows one or two, chosen on purpose.", 7),
    ("Coverage", "The share of your code's lines that ran during the tests (`pytest --cov`). A map of what you forgot, not a score: it does not check asserts.", 8),
    ("Property-based testing", "Stating a property that must hold for all inputs and letting a library (`hypothesis`) invent hundreds of inputs to break it. A pointer, not required.", 8),
]

TRAPS = [
    "\"A test that passes proves the code works.\" It proves only what its `assert` checks, for the inputs it uses, and only if you have seen it fail once. A test with no `assert`, or with `assert x in (True, False)`, passes whatever the code does.",
    "\"When a test fails, the code is wrong.\" A failure only says code and test disagree. Check the specification (backlog item, product owner): sometimes the code broke, sometimes the rule changed and the test is out of date.",
    "\"The newer change wins\" (or \"the test was there first, so it wins\"). Age decides nothing in sample Q4; the agreed rule decides.",
    "\"Compare money with `==`.\" `0.1 + 0.2 == 0.3` is `False`. Use `pytest.approx`, and never copy `30.299999999999997` into a test.",
    "\"You call a fixture inside the test.\" pytest calls it for you; you ask for it by naming a parameter. That is why a one-letter typo gives `fixture '...' not found`.",
    "\"Tests that read the real `data/expenses.csv` are more realistic.\" They pass only on your laptop: `data/` is not in the repository, so CI fails, and the numbers change with every `add`.",
    "\"`tmp_path` tests are pure because they do not touch real files.\" They are I/O tests. Checkpoint 2 wants most tests on pure functions with plain data, and only one or two I/O tests.",
    "\"100% coverage means the code is tested.\" Coverage counts lines that ran, not results that were checked. Use the Missing column as a map; never chase the number.",
    "\"pytest passes locally, so CI will be green.\" CI also runs `ruff` and strict `mypy` on `tests/`: a test without `-> None` turns it red. And `no tests ran` exits with 5, which is red too.",
    "\"`dict.fromkeys` works on any list.\" Only on hashable items: without `frozen=True`, `Expense` raises `TypeError: unhashable type`, and `mypy --strict` does not warn you.",
]

FLASHCARDS = [
    ("What are the three steps of TDD, in one line each?", "Red: write a test for behaviour that does not exist and watch it fail. Green: the smallest code that passes. Refactor: clean up with the tests as a safety net.", "concept", 1),
    ("Why watch a new test fail before making it pass?", "A test you never saw fail has not shown it can notice anything. If you skipped red, break the code on purpose once and watch the test notice.", "concept", 1),
    ("Why write the test first, in the slide's words?", "\"The test forces you to say what 'done' means before you can fool yourself.\"", "recall", 1),
    ("What are Arrange, Act and Assert?", "Arrange: build the input data. Act: call the one function under test. Assert: compare the result with an answer worked out by hand.", "concept", 2),
    ("`E       AssertionError: assert [('dining', 1...thing', 40.0)] == [('clothing',...ining', 15.0)]`: which side is the code?", "The left side is `result`, what the code returned, because the test writes `assert result == ...`; the right side is what the test expected. Read the diff: it usually tells you the bug.", "reading", 2),
    ("A test fails after a teammate changed the function. Who is wrong?", "You can't tell yet. Check which of the two matches what the behaviour is supposed to be: the backlog item or the product owner.", "distinction", 2),
    ("`E       assert 30.299999999999997 == 30.3`: bug or not?", "Not a bug in the code: float noise. Compare with `pytest.approx(30.3)`. Money in floats needs a tolerance.", "reading", 3),
    ("What does real money code use instead of floats?", "`Decimal`, which the slide says is another course. In this course, floats plus `pytest.approx`.", "recall", 3),
    ("What is a fixture, and how does a test get one?", "A function pytest calls for you to build shared set-up data. The test asks for it by naming it as a parameter.", "concept", 3),
    ("Fixture or parametrize?", "Fixture: the same data shared by several tests. Parametrize: the same test run on several rows of inputs and expected results.", "distinction", 3),
    ("`fixture 'expense' not found`: what do you check?", "The spelling of the test's parameter. pytest matches fixtures by name; the list of available fixtures usually shows the right one.", "reading", 3),
    ("The five edge-case questions from slide 11?", "Empty: nothing in? Zero: the boundary? Negative: nonsense? Duplicate: twice? Missing: not there?", "recall", 4),
    ("\"Do not test what feels likely...\"", "\"...Test what could break.\" Boundaries, empties, refunds and duplicates, not a second happy path.", "recall", 4),
    ("Why are tests said to behave as documentation?", "A name like `test_minimum_keeps_amounts_equal_to_it` states a rule in words, its cases show it, and CI checks it on every push, which a comment never is.", "concept", 4),
    ("Why did the demo write `return expenses` before running the new tests?", "So the failure says something: without the stub the test file cannot import the function and no test runs.", "concept", 5),
    ("With the stub, two tests fail and three pass. What do the three passes mean?", "They pass by luck: an unchanged list is right when there are no duplicates. \"Red is information, not a problem.\"", "reading", 5),
    ("Why does `list(dict.fromkeys(expenses))` remove duplicates in order?", "Dictionary keys are unique, and dictionaries keep insertion order, so the first copy of each expense is kept where it appeared.", "concept", 5),
    ("What does `frozen=True` have to do with `remove_duplicates`?", "It makes `Expense` hashable, which set members and dictionary keys require. A plain `@dataclass` gives `TypeError: unhashable type: 'Expense'`.", "concept", 5),
    ("How many rows does `expenses.csv` have before and after `remove_duplicates`?", "420 before, 414 after: six exact duplicates removed.", "recall", 5),
    ("The four quadrants of the slide-18 diagram (benefit against cost of unit testing)?", "High benefit, low cost: algorithms. High benefit, high cost: overcomplicated code, needs refactoring. Low benefit, low cost: trivial code. Low benefit, high cost: coordinators.", "recall", 6),
    ("What does \"pure functions test themselves\" mean?", "A function that takes a list and returns a list needs no file, no set-up and no clean-up: build the data, call it, compare.", "concept", 6),
    ("`assert None == 'Ana: pass'`, and the captured stdout shows `Ana: pass`. Why?", "The function prints instead of returning. Make it return, and print in the shell.", "reading", 6),
    ("`tmp_path`, `CliRunner` or `monkeypatch`?", "`tmp_path`: a file. `CliRunner`: the command line (exit code, output). `monkeypatch`: working directory or environment variables, restored after the test.", "distinction", 7),
    ("Checkpoint 2's three items?", "At least 8 tests passing with CI green on the `v0.2` commit; at least 2 aimed at edge cases; most tests pure, at most one or two I/O tests on purpose.", "recall", 9),
    ("What is coverage good for, and what can it not tell you?", "It lists lines no test ran: a map of what you forgot. It cannot tell whether any assert checked the result, so 100% with weak asserts proves nothing.", "concept", 8),
    ("What does property-based testing do differently?", "You state a property that must hold for every input; `hypothesis` invents hundreds of inputs to break it. Not required, for the curious.", "concept", 8),
    ("pytest passes locally but CI's Types step says `Function is missing a return type annotation` in `tests/`. Fix?", "Add `-> None` to the test. CI runs strict mypy on `src` and `tests`.", "reading", 9),
    ("`no tests ran`, exit code 5. Meaning?", "pytest found no test: file not in `tests/`, not named `test_*.py`, or function not named `test_*`. Exit code 5 is not 0, so CI is red.", "reading", 9),
    ("`ModuleNotFoundError` for your own package when running tests?", "Run `uv sync`, then `uv run pytest`, not bare `pytest`.", "reading", 9),
    ("A test passes locally and fails in CI. First suspect?", "It reads a file only your laptop has, such as `data/expenses.csv`. Build the data inside the test or use `tmp_path`.", "concept", 9),
]

# ---------------------------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------------------------

MODULE: dict[str, Any] = {
    "id": MID,
    "order": 8,
    "module": "M2",
    "title": "Testing and test-driven development",
    "sessions": [8],
    "predicted": False,
    "sources": [
        "slides-session-8",
        "slides/image-only-slides.md (S8 slide 18 diagram)",
        "labs/08-tdd.md",
        "expense-tracker v0.3..v0.4 (d38d9e6, f3d9870, 0e05065, e1b96de, 1e421bc, d3df52b)",
        "moodle/midterm-sample-questions.md (Q4, Q8)",
        "moodle/project-pages.md (CP2, topics with rules)",
    ],
    "summary_md": md(
        """
        Session 8 turns "the core of your project is covered by tests that pass in CI" into a
        method. You write the test first and watch it fail (red), write the smallest code that
        passes (green), then clean up with the tests as a safety net (refactor), as the teacher did
        live on `remove_duplicates`. You learn to read pytest's failure output, compare floats with
        `pytest.approx`, share data with fixtures, run one test on many cases with `parametrize`, and
        choose edge cases on purpose. Then the parts that touch the world: why pure functions test
        themselves, and when to reach for `tmp_path`, `CliRunner` or `monkeypatch`. On the exam this
        is where you read a failing test, judge whether the test or the code is wrong, and name the
        tests you would add.
        """
    ),
    "exam_focus_md": md(
        """
        - A failing test after a teammate's change (sample Q4): you can't tell from the failure
          alone; check the specification, then decide whether the code or the test changes.
        - Real pytest output to read: a list diff ("At index 0 diff"), a float failure, a
          parametrize row id, `fixture '...' not found`, `no tests ran` with exit code 5,
          `ModuleNotFoundError`, `assert None == ...` from a function that prints.
        - "Name the test you would add, in words" for a diff (sample Q8.3): pick edge cases on
          purpose (empty, boundary, negative, duplicate, missing) and say what each expects.
        - The live TDD history: why `e1b96de` commits failing tests with a stub, why `d3df52b` is a
          refactoring, and why `frozen=True` makes `dict.fromkeys` work.
        - Which tool for which test (plain list, `tmp_path`, `CliRunner`, `monkeypatch`), the slide-18
          diagram, and Checkpoint 2's "most tests pure".
        - What a passing test or a coverage number does not prove: no assert, weak asserts,
          100% coverage with a bug.
        - Why something passes on a laptop and fails in CI: `-> None` under strict mypy, tests that
          read `data/expenses.csv`, a tag on the wrong commit.
        """
    ),
    "sections": SECTIONS,
    "terms": [{"term": t, "definition_md": md(d), "section_ref": sid(s)} for t, d, s in TERMS],
    "traps": [md(t) for t in TRAPS],
    "flashcards": [
        {
            "id": f"{MID}-f{i:02d}",
            "front_md": md(f),
            "back_md": md(b),
            "kind": k,
            "section_ref": sid(s),
        }
        for i, (f, b, k, s) in enumerate(FLASHCARDS, start=1)
    ],
    "questions": QUESTIONS,
}


def main() -> None:
    ids = [q["id"] for q in QUESTIONS]
    assert len(ids) == len(set(ids)), "duplicate question ids"
    assert ids == sorted(ids), "questions out of order"
    OUT.write_text(json.dumps(MODULE, ensure_ascii=False, indent=1) + "\n")
    types = Counter(q["type"] for q in QUESTIONS)
    levels = Counter(q["level"] for q in QUESTIONS)
    pos = Counter(
        "abcd"[[o["correct"] for o in q["options"]].index(True)]
        for q in QUESTIONS
        if q["type"] == "mcq"
    )
    print(f"wrote {OUT}")
    print(f"types {dict(types)} levels {dict(levels)} correct positions {dict(sorted(pos.items()))}")
    print(f"sections {len(SECTIONS)} terms {len(TERMS)} traps {len(TRAPS)} cards {len(FLASHCARDS)}")


if __name__ == "__main__":
    main()
