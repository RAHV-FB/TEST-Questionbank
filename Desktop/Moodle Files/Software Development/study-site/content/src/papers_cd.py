"""Generate content/_papers-cd.json: Paper C (worst case) and Paper D (beyond).

Run from the study-site folder:
    uv run python content/src/papers_cd.py
Every tool output shown in a stem was produced by running the tool (see brief/VERIFY.md);
the evidence lives outside the repository, in the scratchpad work folders paper-c and paper-d.
"""

import json
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parent.parent / "_papers-cd.json"
LETTERS = "abcd"


def mcq(
    qid: str,
    module: str,
    section: str,
    level: str,
    skills: list[str],
    stem: str,
    answer: str,
    options: list[tuple[str, str]],
    explanation: str,
    source_ref: str,
    origin: str,
    verified: str,
) -> dict[str, Any]:
    assert len(options) == 4 and answer in LETTERS, qid
    return {
        "id": qid,
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": stem.strip("\n"),
        "options": [
            {"text_md": text, "correct": LETTERS[i] == answer, "why_md": why}
            for i, (text, why) in enumerate(options)
        ],
        "explanation_md": explanation,
        "module_ref": module,
        "section_ref": section,
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified,
    }


def part(
    label: str,
    prompt: str,
    marks: int,
    model: str,
    rubric: list[str],
    weak: str,
) -> dict[str, Any]:
    return {
        "label": label,
        "prompt_md": prompt,
        "marks": marks,
        "model_answer_md": model,
        "rubric": rubric,
        "weak_answers_md": weak,
    }


def open_q(
    qid: str,
    module: str,
    section: str,
    level: str,
    skills: list[str],
    stem: str,
    parts: list[dict[str, Any]],
    lines: str,
    explanation: str,
    source_ref: str,
    origin: str,
    verified: str,
) -> dict[str, Any]:
    return {
        "id": qid,
        "type": "open",
        "level": level,
        "skills": skills,
        "stem_md": stem.strip("\n"),
        "parts": parts,
        "lines": lines,
        "explanation_md": explanation,
        "module_ref": module,
        "section_ref": section,
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified,
    }


# ---------------------------------------------------------------------------------------------
# PAPER C: worst case. Fifteen multiple-choice questions, then four open questions.
# ---------------------------------------------------------------------------------------------


def paper_c_mcq_a() -> list[dict[str, Any]]:
    qs: list[dict[str, Any]] = []

    qs.append(
        mcq(
            "paper-c-q01",
            "sdlc-agile",
            "sdlc-agile-s8",
            "hard",
            ["concept", "judgement"],
            """
The flashcard-trainer group sets two lines from the slides side by side. Session 2, on Waterfall: "The gate between phases is a document that gets approved." Session 4, on Checkpoint 1: the Definition of Done is "public, binary and checkable before you submit", and its first item is that `uv sync && uv run <your-app> --help` works from a clean clone.

Marta concludes: "A checkpoint is a Waterfall gate with a new name: a date, a checklist, a sign-off, then the next phase. So we should write the whole design now and stop re-planning."

Which reply follows sessions 2 and 4?
""",
            "b",
            [
                (
                    "Marta is right: both are dates on which something is approved, so the course is Waterfall with Scrum words, and finishing the design first is the safe order.",
                    'Session 2 maps the course the other way: "Checkpoints are sprints." Sign-offs do not define Waterfall. Its assumption is that requirements are known and stable, and software breaks that.',
                ),
                (
                    "Marta is wrong: a gate approves a document and closes a phase, a checkpoint tests working software against a checkable bar, and the next Sprint may change the plan.",
                    "Right. The first Definition of Done item is run on the code, not read in a document, and session 2 says the same phases happen again in every cycle, on a small slice.",
                ),
                (
                    "Marta is half right: a checkpoint is a gate, but nothing in the course stops a group from writing all of its design at the start, as long as each checkpoint is passed on its date.",
                    'A checkpoint is not a gate. Writing the whole design first bets on stable requirements, the first Waterfall assumption, and goes against "responding to change over following a plan".',
                ),
                (
                    "Marta is wrong because a customer never looks at a Waterfall gate, while the lecturer, as Product Owner, inspects every checkpoint in person.",
                    'In Waterfall the customer is "involved mostly at the start and the end", which includes approving the specification. What differs is what is inspected, a document or running software, and whether the plan stays open.',
                ),
            ],
            'Both lines have a date and an approval, which is what Marta sees. The difference is what is approved and what happens next. A Waterfall gate approves a document, such as a signed specification or the architecture documents, and the phase is then closed. A checkpoint is the edge of a Sprint ("checkpoints are sprints"): it checks working software against a Definition of Done that a machine can run, and the next Sprint can change what is built. Writing the whole design first assumes the requirements will not move, which is the assumption session 2 says software breaks.',
            "S2 slides 5, 7, 10 and 14; S4 slides 16–17",
            "slides",
            "source",
        )
    )

    qs.append(
        mcq(
            "paper-c-q02",
            "sdlc-agile",
            "sdlc-agile-s1",
            "exam",
            ["concept", "judgement"],
            """
The habit-tracker group renames the field `streak` to `current_streak` in one module. Nothing crashes and the group's CI check stays green. A week later the weekly report shows a streak of 0 for every user: two other modules still read `streak` from a dictionary and quietly got their default value. A teammate reviewed the rename and saw nothing wrong in the diff. The group has no test that checks a streak value.

Session 1 lists "six ways working code still fails", with a method or tool against each. Which answer fits this failure?
""",
            "d",
            [
                (
                    "Docker: a container makes every machine identical, so the rename would have behaved the same everywhere.",
                    'Docker answers "works on my machine". Here every machine gives the same wrong answer, so the environment is not the problem.',
                ),
                (
                    "Scrum: a shared plan and a daily meeting would have told everyone about the rename, so nobody would have missed the two modules that still read `streak`.",
                    'Scrum answers "no shared plan, four people build four corners". A Daily might mention the rename, but nothing would check the value the report shows.',
                ),
                (
                    "Version control and code review: a reviewer would have caught the rename before it reached the main branch.",
                    'These answer "a teammate\'s change breaks the build". The two modules that still read `streak` were not in the diff, and review does not run any check on the report.',
                ),
                (
                    "Tests that assert on the report values, run by the CI check on every push: the check is the referee and the tests are its rules.",
                    'Right. The slide pairs "unreadable, breaks silently" with clean code and testing. A test on a streak value turns a silent wrong answer into a red check.',
                ),
            ],
            'The failure is the slide\'s "change one thing, three others break, silently". Nothing failed loudly, so no tool noticed. The slide pairs silent breakage with testing: a test that asserts on a streak value turns the silent wrong answer into a red check, and CI then runs it on every push. Without such a test, a green CI check says only that ruff, mypy and whatever tests exist passed. The referee needs rules, and the tests are the rules.',
            "S1 slides 6 and 8; S3 slide 3",
            "slides",
            "source",
        )
    )

    qs.append(
        mcq(
            "paper-c-q03",
            "scrum",
            "scrum-s6",
            "hard",
            ["judgement", "concept"],
            """
End of the second sprint. The parking-lot group's Definition of Done reads: "CI is green; every item has at least one test for its new behaviour; bad input prints a message and exits non-zero." The item "A driver can pay for an overnight stay" works in the live demo, CI is green and the code is merged, but no test was written for it.

Dani: "It is 95% done. Present it at the Sprint Review as part of the Increment and write the test next sprint." The lecturer is the Product Owner.

Which statement follows session 4?
""",
            "c",
            [
                (
                    "It counts as done, because the Product Owner can accept an item that works in a demo, and the missing test becomes a technical-debt ticket.",
                    'Session 4 says "done except for tests" is not admissible. Technical debt (session 1) is a planned shortcut inside finished work; it does not let an item skip the group\'s own Definition of Done.',
                ),
                (
                    'It is shown as "done except for tests", because the Review exists to collect feedback and the label is honest.',
                    "Honesty about the gap is good, but the Increment holds only items that meet the Definition of Done. A label does not change whether the bar was met.",
                ),
                (
                    "It is not done and does not ship: the Increment holds only items that meet the Definition of Done, so it stays on the backlog.",
                    'Right. "An item that misses the Definition of Done is not done, and does not ship." The group cannot count 95%, because the bar is binary and checkable.',
                ),
                (
                    "It is done, because a green CI check is the only line of the Definition of Done that the lecturer enforces.",
                    'Green CI is the one line every group must keep. The lecturer\'s words are "I hold you to your own Definition of Done in November", so the whole list is the standard.',
                ),
            ],
            "The Increment's commitment is the Definition of Done: the quality bar every item meets, decided once and applied to everything. The group's own list asks for a test per item, so an item without one fails the bar, however well it demos. Session 4 names the excuse exactly: \"done except for tests\" is not admissible, and an item that misses the Definition of Done is not done and does not ship. A technical-debt ticket is for a shortcut taken on purpose inside finished work, not a way to count unfinished work as finished.",
            "S4 slides 8, 10, 16 and 29",
            "slides",
            "source",
        )
    )

    qs.append(
        mcq(
            "paper-c-q04",
            "scrum",
            "scrum-s7",
            "exam",
            ["judgement", "concept"],
            """
The vending-machine group's Sprint Planning for a two-week Sprint, as its Scrum Master noted it down:

- 14:00. The Product Owner, who is the lecturer, reads out the top of the backlog. The Developers choose three items and agree a Sprint Goal.
- 14:12. Someone brings up item 9, "A customer sees the change returned in the fewest coins". It is far down the backlog and not in this Sprint.
- 14:15. For the next 45 minutes the Developers and the Product Owner debate which coins to support, which algorithm to use and how to test it.
- 15:00. Planning ends. The group has not yet talked through the three items it chose.

Which statement follows session 4?
""",
            "a",
            [
                (
                    "The item 9 discussion is Refinement, not Planning: it needs its own time-box, so Planning stays on what this Sprint will deliver.",
                    'Right. Planning is an hour to "agree on what will be delivered at the end of the Sprint". Refinement is where the Product Owner and Developers discuss the details of items, "in detail only near the top".',
                ),
                (
                    "The discussion belongs in Planning, so the group should extend the time-box until every item on the backlog has been discussed in the same detail.",
                    'Planning keeps its hour for a two-week Sprint. Detailing an item far down the list early is waste, because "it will change before it is built".',
                ),
                (
                    "The Product Owner should have settled the algorithm alone, because Scrum gives the Product Owner every decision about how an item is built.",
                    'The Product Owner decides "what is worth doing, and in what order". The team decides how the work is done, and who does what.',
                ),
                (
                    "Nothing is wrong: the Daily Scrum is the meeting where the implementation details of the items that come next are worked out.",
                    "The Daily is fifteen minutes for the Developers, who state latest work, next work and blockers. Upcoming items are not designed there.",
                ),
            ],
            'Each ceremony answers one question in a time-box. Sprint Planning (one hour in a two-week Sprint) agrees what will be delivered by the end of this Sprint. Refinement (about four hours across the Sprint) is where the Product Owner and Developers discuss the details of upcoming items. The backlog is refined continuously and "in detail only near the top", so item 9, far down and outside this Sprint, was discussed in the wrong event, and Planning ran out of time for the three items it was there to settle. The Developers still decide how the work is done, so the algorithm is not the Product Owner\'s call alone.',
            "S4 slides 7, 9 and 11",
            "slides",
            "source",
        )
    )

    qs.append(
        mcq(
            "paper-c-q05",
            "project-anatomy",
            "project-anatomy-s8",
            "exam",
            ["read-tool-output", "judgement"],
            """
A teammate clones the group repository for the first time. The CI step "Install dependencies from the lockfile" has been red on every push. In the clone:

```console
$ uv sync --locked
Using CPython 3.13.15
Creating virtual environment at: .venv
error: Unable to find lockfile at `uv.lock`, but `--locked` was provided. To create a lockfile, run `uv lock` or `uv sync` without the flag.
$ git ls-files | grep -c lock
0
$ cat .gitignore
.venv/
__pycache__/
uv.lock
```

Which fix is right?
""",
            "b",
            [
                (
                    "Delete `.venv` and run `uv sync --locked` again.",
                    "The virtual environment is not the problem. uv stopped before using it, because there is no `uv.lock` to read.",
                ),
                (
                    "Remove `uv.lock` from `.gitignore`, run `uv lock` once, and commit `uv.lock`.",
                    "Right. The lockfile is committed so every teammate and CI install the same versions. It was never in the repository because `.gitignore` told git to ignore it.",
                ),
                (
                    "Change the CI step to plain `uv sync`, so that a missing lockfile no longer stops the build.",
                    "The step turns green by removing the referee. Plain `uv sync` quietly makes a new lockfile on each machine, so versions can differ again.",
                ),
                (
                    "Pin every version in `pyproject.toml` by hand, so that a lockfile is not needed.",
                    "`pyproject.toml` lists what you ask for. The lockfile also records the dependencies of your dependencies, down to the hash, which hand-pinning does not cover.",
                ),
            ],
            'CI runs `uv sync --locked`, which refuses to continue unless `uv.lock` exists and agrees with `pyproject.toml`. The transcript shows two facts: uv found no lockfile, and git tracks no file with "lock" in its name because `.gitignore` lists `uv.lock`. Session 4 says the lockfile is committed so that "works on my machine" can be pinpointed. The fix is to stop ignoring it, generate it once and commit it. Dropping `--locked` hides the problem instead of removing it.',
            "S4 slide 24; S5 slide 13",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q06",
            "cli-program",
            "cli-program-s9",
            "hard",
            ["read-tool-output", "judgement"],
            """
The parking-lot README and the group's tests all write the command as `parking T-104 --hours 3`, and it worked while `pay` was the only command. A teammate then adds a second command, `status`, and pushes. Nothing else changed.

```python
app = typer.Typer(help="A terminal parking lot.")


@app.command()
def pay(ticket: str, hours: int = typer.Option(1, help="Hours parked.")) -> None:
    typer.echo(f"{ticket}: {hours} h = {fee(hours):.2f} EUR")


@app.command()
def status() -> None:
    typer.echo("2 tickets open")
```

```console
$ uv run parking T-104 --hours 3
Usage: parking [OPTIONS] COMMAND [ARGS]...
Try 'parking --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ No such command 'T-104'.                                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
$ uv run parking pay T-104 --hours 3
T-104: 3 h = 7.50 EUR
```

What explains the first error, and what is the right change?
""",
            "c",
            [
                (
                    "Adding `status` broke `pay`: a typer app supports only one command, so `status` must be removed again and the README left as it is.",
                    "Two commands are normal, and the second line of the transcript shows `pay` working next to `status`.",
                ),
                (
                    "The old line needs an empty `@app.callback()` in the code, which brings back the behaviour of `parking T-104 --hours 3` for the first command.",
                    "The callback keeps command names when there is one command. With two commands the names are already required, and a callback does not drop them.",
                ),
                (
                    "With two commands typer needs the command name, so `T-104` was read as one: write `parking pay T-104 --hours 3` and fix the README and tests.",
                    "Right. The old line relied on the one-command shortcut. The form that is always valid names the command.",
                ),
                (
                    "`T-104` is read as the start of an option because it contains a dash, so it must be quoted as `'T-104'` whenever it is typed after the command.",
                    "Quotes pass the same text to the program. The error says No such command, and the usage line shows `COMMAND`.",
                ),
            ],
            "With a single command typer treats the whole app as that command and drops its name. That is why `parking T-104 --hours 3` worked (session 5, the third of the three that bite). A second command ends the shortcut: typer must now know which command you mean, so the first word after `parking` is read as a command name, and `T-104` is not one. The usage line `COMMAND [ARGS]...` shows it. The old line was only ever valid by accident, so the right change is the form that always works, `parking pay T-104 --hours 3`, and a fix to the README and tests that carried the old line.",
            "S5 slide 13; labs/01-scaffold.md troubleshooting",
            "lab",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q07",
            "cli-program",
            "cli-program-s4",
            "hard",
            ["judgement", "read-tool-output"],
            """
The parking-lot group's Definition of Done has the line "Invalid input prints a message and exits non-zero." A teammate tries the `pay` command with two bad inputs:

```python
@app.command()
def pay(ticket: str, hours: int = typer.Option(1, help="Hours parked.")) -> None:
    typer.echo(f"{ticket}: {hours} h = {fee(hours):.2f} EUR")
```

```console
$ uv run parking pay T-104 --hours three
Usage: parking pay [OPTIONS] {ticket}
Try 'parking pay --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value for '--hours': 'three' is not a valid int.                     │
╰──────────────────────────────────────────────────────────────────────────────╯
$ echo $?
2
$ uv run parking pay T-104 --hours -2
T-104: -2 h = -5.00 EUR
$ echo $?
0
```

Which statement about that line of the Definition of Done is right?
""",
            "d",
            [
                (
                    "Both inputs are bad, so `pay` needs a `try`/`except ValueError` around the hours, and an exit with code 1 for each of the two bad inputs in the transcript.",
                    "typer stopped `three` before `pay` ran, so a `try` inside `pay` never sees it, and no error is raised for `-2`.",
                ),
                (
                    "Neither is handled: exit code 2 means typer crashed, so the group must catch the error itself, print its own message and exit with 1 instead.",
                    "Exit code 2 is typer's usage error: a message and a non-zero exit, which is what the line asks for. A crash would show a traceback.",
                ),
                (
                    "Both are handled: typer rejects `-2` as well, since a number of hours cannot be negative, so the Definition of Done line is met for both inputs.",
                    "The transcript shows `-2` printing a fee of -5.00 EUR and exiting 0. The hint `int` accepts every whole number.",
                ),
                (
                    "`three` is handled: the hint `int` is the specification, and typer exits 2 with a message. `-2` is a valid `int`, so the group needs its own check.",
                    "Right. A hint can say a whole number, not a positive one. The second input needs the group's own check.",
                ),
            ],
            "Session 5: the type hints are the specification. typer reads `hours: int` and refuses `three` before `pay` runs, with a message and exit code 2, so for that input the line of the Definition of Done is met without more code. A hint cannot say positive, so `-2` passes and the program answers -5.00 EUR with exit code 0, which lies. That input needs the group's own check in the shell: print the reason to stderr, exit non-zero, and add a test for it (sessions 5 and 7).",
            "S4 slide 30; S5 slides 6–8 and 10; S7 slides 17–19",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q08",
            "clean-code",
            "clean-code-s6",
            "hard",
            ["read-code", "read-tool-output", "judgement"],
            """
The parking-lot group's `fee` returns the right number, and it also prints a line. The function, its test and what the checks and the `status` command say:

```python
def fee(hours: int) -> float:
    amount = min(hours * HOURLY_RATE, DAILY_CAP)
    print(f"Fee: {amount:.2f} EUR")
    return amount
```

```python
def test_fee_for_three_hours() -> None:
    assert fee(3) == 7.5
```

```console
$ uv run ruff check . && uv run mypy src tests
All checks passed!
Success: no issues found in 5 source files
$ uv run pytest -q
.                                                                        [100%]
1 passed in 0.00s
$ uv run parking status
Fee: 7.50 EUR
Fee: 18.00 EUR
Fee: 2.50 EUR
3 tickets open, 28.00 EUR in fees
```

`status` was meant to print one line. A teammate says: "Everything is green and `fee` returns the right value, so `fee` is fine." Which judgement follows session 6?
""",
            "a",
            [
                (
                    "`fee` does two jobs, computing and printing, so callers get a line they did not ask for; it should return the value, and the shell prints it.",
                    'Right. "A function that returns can be tested, reused and read on its own." Reuse is where the print hurts, and `status` reuses `fee`.',
                ),
                (
                    "It is fine: the extra lines are harmless, because ruff, mypy and pytest are all green and the total is correct.",
                    "Green checks answer only the questions they ask. They do not say whether a function does one job, and the `status` screen shows what the second job costs.",
                ),
                (
                    "The test is incomplete: it should also capture the printed line and compare it with `Fee: 7.50 EUR`, since printing is part of what `fee` does.",
                    "That would pin the extra output down instead of removing it, and `status` would still print three lines.",
                ),
                (
                    "`status` is wrong to call `fee`: it should repeat the price formula itself, so that `fee` can keep printing for the `pay` command.",
                    "Copying the formula puts the price rule in two places, and a new rate would need two edits. The fault is in `fee`, not in its caller.",
                ),
            ],
            "The checks are green and the number is right, so this is a design fault, not a failing test. `fee` mixes computation with output (session 6, computation is not output). Called from `pay` it looks harmless. Called from `status`, once per ticket, it writes a line each time and spoils the one-line summary. A function that returns a value can be tested, reused and read on its own; a function that prints can only be looked at. The fix is to remove the `print` from `fee` and let the command that talks to the user, the shell, print the result it needs.",
            "S6 slide 20; S7 slides 13 and 15",
            "slides",
            "run",
        )
    )

    return qs


def paper_c_mcq_b() -> list[dict[str, Any]]:
    qs: list[dict[str, Any]] = []

    qs.append(
        mcq(
            "paper-c-q09",
            "refactor-types",
            "refactor-types-s3",
            "hard",
            ["read-code", "judgement"],
            """
The demo's `total_by_category` skips an expense in two guard clauses. In the report, `category == ""` means every category.

```python
if category != "" and expense.category != category:
    continue
if expense.amount < minimum:
    continue
```

A pair decomposes the conditional. They write a helper `is_wanted(expense, category, minimum)` that returns `True` for the expenses that are not skipped, and replace both guards by `if not is_wanted(expense, category, minimum): continue`. The output of the program must not change.

Which body of `is_wanted` keeps the behaviour?
""",
            "b",
            [
                (
                    '`return category == "" or expense.category == category`',
                    "It drops the minimum: an expense of 5.00 with a minimum of 10.00 is wanted by this body, but the guards skip it.",
                ),
                (
                    '`return (category == "" or expense.category == category) and expense.amount >= minimum`',
                    "Right. Each guard negated: the category test passes when none is asked for or it matches, and the amount test passes at the boundary, because the old guard skipped only amounts below the minimum.",
                ),
                (
                    '`return (category == "" or expense.category == category) and expense.amount > minimum`',
                    "`>` drops an amount equal to the minimum, which the old guard kept. It is the boundary row of session 8's edge-case table.",
                ),
                (
                    "`return expense.category == category and expense.amount >= minimum`",
                    'It forgets that an empty category means every category. With the default `category = ""` it keeps nothing, and a plain `report` would print an empty report.',
                ),
            ],
            'Decompose conditional keeps the behaviour, so the helper must return True exactly when neither guard fires. The first guard skips when a category was asked for and the expense does not match; it passes when `category == ""` or the categories match. The second guard skips when the amount is below the minimum; it passes when `amount >= minimum`. Joined with `and`, that is option b, the form on the session 7 slide. The other bodies each change one case: the minimum is lost, the boundary moves, or the empty category stops meaning all. Checking both versions over small values finds a difference for every other option.',
            "S7 slides 5–6; S8 slide 11",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q10",
            "core-shell-failing",
            "core-shell-failing-s7",
            "exam",
            ["read-code", "judgement"],
            """
A teammate's program totals the amount column; `lines` holds the data rows without the header. This copy of the data has one unreadable amount.

```python
def parse_amount(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        return -1.0


def total_amount(lines: list[str]) -> float:
    return sum(parse_amount(line.split(",")[3]) for line in lines)
```

```console
$ cat expenses_bad.csv
date,merchant,category,amount
2025-07-01,Cabify,transport,36.25
2025-07-01,Lidl,groceries,N/A
2025-07-02,Abacus,education,56.77
$ uv run python totals.py expenses_bad.csv
Total: 92.02
```

The two readable rows add up to 93.02, and the program reported 92.02 without a word. Which change follows session 7's "fail loudly, at the boundary"?
""",
            "c",
            [
                (
                    "Keep the `-1.0` and add the comment `# -1.0 means the amount could not be read`, so that the next reader understands the oddity.",
                    "A comment tells a reader about the sentinel but changes nothing at run time. The total is still wrong, and nobody is told when it happens.",
                ),
                (
                    "Return `0.0` instead of `-1.0`, so that an unreadable amount can no longer pull the total down.",
                    "The total becomes 93.02 and looks right, yet a bad row is still ignored in silence. A silent default is the same fault with a nicer number.",
                ),
                (
                    "Let `parse_amount` raise `ValueError` for non-numbers; the shell catches it, writes the message to stderr and exits with code 1.",
                    "Right. The core raises on bad input and never prints; the shell turns the exception into a message on stderr and a non-zero exit code.",
                ),
                (
                    "Keep the sentinel, but call `logging.warning(...)` whenever it is returned, and still print the total at the end of the run.",
                    "A log line is the program's diary. The caller still receives -1.0, the report is still wrong and the exit code is still 0, so a script downstream sees success.",
                ),
            ],
            'Session 7: "Do not return -1 and hope somebody checks." The sentinel travels into `sum`, and a wrong total comes out with exit code 0. The fix the slides give is split in two. The core raises on bad input and never prints an error. The shell catches only what it expects, here `ValueError`, prints the reason to stderr and exits with a non-zero code, so that a user, `&&` and CI all notice. A comment, a different default or a log line each leave the program saying yes.',
            "S7 slides 17–19",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q11",
            "testing-tdd",
            "testing-tdd-s5",
            "hard",
            ["read-tool-output", "judgement"],
            """
The expense-tracker group wants a refund feature. A teammate adds this to `report.py`, where `Expense` is the frozen dataclass from session 6 and `remove_duplicates` is still `return list(dict.fromkeys(expenses))`:

```python
def apply_refund(expense: Expense, refund: float) -> None:
    expense.amount = expense.amount - refund
```

```console
$ uv run mypy --strict src tests
src/expense_tracker/report.py:99: error: Property "amount" defined in "Expense" is read-only  [misc]
Found 1 error in 1 file (checked 6 source files)
```

To satisfy mypy the teammate changes `@dataclass(frozen=True)` to plain `@dataclass`. mypy now says `Success: no issues found in 6 source files`.

What should the group do?
""",
            "a",
            [
                (
                    "Restore `frozen=True`, and write `apply_refund` so that it returns a new `Expense` with the reduced amount, not an edited old one.",
                    "Right. Frozen is what makes `Expense` hashable, which `dict.fromkeys` needs. Building a new value keeps the design and gives the refund feature what it needs.",
                ),
                (
                    "Keep the dataclass unfrozen and push: mypy was the only check that complained, and it now passes.",
                    "A green mypy says that the types agree. It cannot see that `remove_duplicates` needs `Expense` to be hashable, so pytest would fail on the first call.",
                ),
                (
                    "Keep the dataclass unfrozen and replace `dict.fromkeys(expenses)` with `set(expenses)`, which also removes duplicates in a single call.",
                    "A set needs hashable items just as a dict key does, so it fails with the same `TypeError`. It would also lose the original order.",
                ),
                (
                    "Keep `frozen=True` and add `# type: ignore[misc]` to the assignment, since the refund is needed and mypy is only being strict.",
                    "The ignore silences the message, not the fault: when the code runs, the assignment raises `FrozenInstanceError`.",
                ),
            ],
            'Two sessions meet here. Session 6: `frozen=True` means the object cannot change after creation. Session 8: that is what makes `Expense` hashable, so `dict.fromkeys` can use it as a key, and "session 6\'s frozen=True pays off here". The first mypy error was the design speaking: an `Expense` is a value, not something to edit in place. Removing `frozen` silenced mypy, but an unfrozen dataclass has no hash, so `remove_duplicates` fails with `TypeError: unhashable type` as soon as pytest calls it. An `# type: ignore` fails differently, with a `FrozenInstanceError` at run time. The fix keeps the design: restore frozen and create a new `Expense` with the corrected amount.',
            "S6 slide 24; S8 slide 16",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q12",
            "terminal-files",
            "terminal-files-s5",
            "exam",
            ["predict-output", "concept"],
            """
In an empty folder on the group's laptop:

```console
$ mkdir reports archive
$ touch reports/jan.csv reports/feb.csv
$ mv reports archive
$ mv archive/reports/jan.csv .
```

Which statement is true afterwards?
""",
            "d",
            [
                (
                    "`feb.csv` and `jan.csv` are both still in `archive/reports`, because the last `mv` copied `jan.csv` out instead of moving it.",
                    "`mv` moves and never leaves a copy behind. Copying is what `cp` does.",
                ),
                (
                    "`jan.csv` is in the current folder and `feb.csv` is in `archive`, because the first `mv` renamed `reports` to `archive`.",
                    "`archive` already existed, so `mv` put `reports` inside it. It renames only when the target does not exist.",
                ),
                (
                    "Nothing moved, because the first `mv` fails with Directory not empty when `archive` already exists, and the later `mv` commands then have nothing to move.",
                    "Moving into an existing folder is the normal case and needs no message. The last `mv` would then have had nothing to move.",
                ),
                (
                    "`jan.csv` is in the current folder and `feb.csv` is in `archive/reports`: the first `mv` put the whole `reports` folder inside `archive`.",
                    "Right. An existing folder as the target means go inside it, and the last command names the path inside `archive` and `.`, the current folder.",
                ),
            ],
            "`mv` moves, and it also renames (session 9, slide 14); which one happens depends on the target. If the target is an existing folder, the thing goes inside it. If the target does not exist, it becomes the new name. `archive` was created on the first line, so `mv reports archive` put the whole `reports` folder inside it, giving `archive/reports/jan.csv` and `archive/reports/feb.csv`. The last command names that path and `.`, the current folder, so `jan.csv` moves out and `feb.csv` stays. Had `archive` not existed, the same first `mv` would only have renamed `reports` to `archive`.",
            "S9 slide 14",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q13",
            "terminal-files",
            "terminal-files-s9",
            "exam",
            ["judgement", "read-tool-output"],
            """
On the lab machine Ana owns `check.sh`, and her group `team` includes Bruno.

```console
$ ls -l check.sh
-rw-r--r-- 1 ana team 127 Oct 15 11:42 check.sh
```

Ana wants Bruno to be able to run the script but not edit it, and she wants nobody outside the group to read or run it. Which command does that?
""",
            "b",
            [
                (
                    "`chmod 755 check.sh`",
                    "755 is `rwxr-xr-x`: the group is right, but everyone else can also read and run the script.",
                ),
                (
                    "`chmod 750 check.sh`",
                    "Right. Owner `rwx` = 7, group `r-x` = 5, others nothing = 0.",
                ),
                (
                    "`chmod 770 check.sh`",
                    "770 is `rwxrwx---`: nobody outside is let in, but the group has `w`, so Bruno could edit the script.",
                ),
                (
                    "`chmod 640 check.sh`",
                    "640 is `rw-r-----`: no one has `x`, so nobody could run it as a program, and Bruno could only read it.",
                ),
            ],
            'r is 4, w is 2, x is 1, added for each of the three groups in order: owner, group, others. Ana keeps read, write and execute: 7. Bruno, as group, needs to read and run but not write: r-x is 5. Everyone else gets nothing: 0. The mode is 750. The other numbers each break one requirement: 755 lets others in, 770 lets the group edit, and 640 removes the x bit that makes a file a program ("no x, no run").',
            "S9 slides 17 and 21",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q14",
            "pipes-bash",
            "pipes-bash-s6",
            "hard",
            ["read-code", "read-tool-output", "judgement"],
            """
A teammate writes `scripts/clean.sh` to empty the `reports` folder before a new run:

```bash
#!/usr/bin/env bash
cd reports
rm -r *
```

The `reports` folder exists only on the laptop where the script was written. On another clone, from the project root:

```console
$ ls
LICENSE  README.md  pyproject.toml  scripts  src  tests  uv.lock
$ ./scripts/clean.sh
./scripts/clean.sh: line 2: cd: reports: No such file or directory
$ echo $?
0
$ ls
$
```

What happened, and which change makes the script safe?
""",
            "c",
            [
                (
                    "The failed `cd` made `rm` refuse to run, so the files are only hidden and `ls -a` brings them back; the script needs no change.",
                    "A failed `cd` stops nothing in a script. `rm` ran, and `rm` is permanent: there is no bin (session 9).",
                ),
                (
                    "`rm -r *` emptied the parent folder instead of the project, because `cd` expanded the `*`; the script is safe if `reports` is created first.",
                    "The shell expands `*` in the current folder, and no `cd` happened, so the current folder was the project root.",
                ),
                (
                    "The failed `cd` did not stop the script, so `rm -r *` ran in the project root; `set -e`, or `cd reports && rm -r *`, would stop at the failed `cd`.",
                    "Right. A script carries on after a failing command unless `set -e` or `&&` says otherwise.",
                ),
                (
                    "The error message shows that the script stopped there, so something else, such as CI, must have removed the files; nothing in the script is at fault.",
                    "Exit code 0 shows that the script ran to its end, and its last command was `rm`.",
                ),
            ],
            "A script is a list of commands, and by default the shell carries on after one fails. `cd reports` failed, but the exit code of the script is that of its last command, `rm -r *`, which succeeded: 0. The `*` expanded in the folder the script was started from, so the project went, with no bin to recover it. Two changes stop the script at the failed `cd`: `set -e` at the top, or `cd reports && rm -r *`, which runs `rm` only if `cd` succeeded. Session 9's rule, look at the exact path before you `rm` it, becomes in a script: do not run `rm` unless you know where you are.",
            "S9 slide 15; S10 slide 16 (set -e); S5 slide 9 (&&)",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-c-q15",
            "pipes-bash",
            "pipes-bash-s4",
            "exam",
            ["predict-output"],
            """
The parking-lot group keeps its tickets in `tickets.csv`:

```console
$ cat tickets.csv
ticket,plate,hours,fee
T-101,1234BCD,2,5.00
T-102,5678FGH,30,33.00
T-103,9012JKL,1,2.50
T-104,3456MNP,8,18.00
T-105,7890QRS,4,10.00
```

A teammate wants the largest fee and runs this pipeline:

```bash
tail -n +2 tickets.csv | cut -d, -f4 | sort | tail -n 1
```

(`tail -n +2` prints the file from line 2 onward, `cut -d, -f4` keeps the fourth comma-separated field, and `tail -n 1` keeps the last line.) What does it print?
""",
            "a",
            [
                (
                    "`5.00`",
                    "Right. `sort` without `-n` compares text one character at a time, so `5.00` comes after `33.00`.",
                ),
                (
                    "`33.00`",
                    "That is what the teammate wanted, and what `sort -n` would give. Plain `sort` is text order.",
                ),
                (
                    "`2.50`",
                    "That would be the last line if the fees were sorted from largest to smallest; nothing here reverses the order.",
                ),
                (
                    "`fee`",
                    "The header is removed by `tail -n +2` before `cut` sees it, so the word `fee` never enters the pipe.",
                ),
            ],
            "Read left to right and ask what text flows through each `|`. `tail -n +2` drops the header. `cut` leaves five fees: 5.00, 33.00, 2.50, 18.00, 10.00. `sort` without `-n` orders them as text, character by character: 10.00, 18.00, 2.50, 33.00, 5.00, because `1` comes before `2`, `3` and `5`. The last line is 5.00. With `sort -n` the answer would be 33.00. Each stage sees only the previous stage's text, so an early mistake travels to the end.",
            "S9 take-aways; S10 slides 6–7 (sort needs -n)",
            "slides",
            "run",
        )
    )

    return qs


def paper_c_open() -> list[dict[str, Any]]:
    qs: list[dict[str, Any]] = []

    qs.append(
        open_q(
            "paper-c-q16",
            "clean-code",
            "clean-code-s5",
            "hard",
            ["read-code", "judgement"],
            """
The gradebook group (topic 9) has this function. `grades.csv` has the columns `student`, `kind` and `score`. A run on a small file is shown below it.

```python
def final_grade(path):
    total = 0
    weight = 0
    for line in open(path).read().splitlines()[1:]:
        p = line.split(",")
        try:
            if p[1] == "exam":
                total += float(p[2]) * 0.6
                weight += 0.6
            else:
                total += float(p[2]) * 0.4
                weight += 0.4
        except:
            print("bad row:", line)
    print("Final grade:", round(total / weight, 1))
```

```console
$ cat grades.csv
student,kind,score
Marta,exam,8.0
Marta,project,9.5
Marta,quiz,seven
Marta,project,6.0
$ python run.py
bad row: Marta,quiz,seven
Final grade: 7.9
```
""",
            [
                part(
                    "1",
                    "In one sentence, what does the function do?",
                    1,
                    "It reads a CSV and prints the weighted average of the scores: exams count 0.6, every other kind 0.4, and unreadable rows are skipped with a message.",
                    [
                        "Says it reads the file and computes a weighted average (a final grade)",
                        "Mentions the two different weights for exams and other kinds, or that unreadable rows are skipped with a message",
                    ],
                    '"It calculates the grade" misses that exam rows and other rows are weighted differently. "It prints bad rows" describes only the `except` branch. Saying it returns the grade is wrong: it only prints.',
                ),
                part(
                    "2",
                    "Name three problems a teammate would face when reading, testing or changing it.",
                    3,
                    "It does four jobs (read, parse, calculate, print) and prints instead of returning, so no test can get the grade. The bare `except:` hides every error and carries on with less data. `0.6`, `0.4`, `p[1]` and `p[2]` have no names.",
                    [
                        "One function does several jobs (read, parse, compute, print); it prints instead of returning, so it cannot be tested",
                        "The bare except hides every kind of error and carries on with less data (catch only what you can handle; fail loudly)",
                        "Magic numbers 0.6 and 0.4, repeated and unnamed",
                        "Positions p[1] and p[2] instead of named fields (a tuple is a missing type)",
                        "Also accepted: the file is never closed; a file with no readable row ends in a division by zero",
                    ],
                    '"Bad names" is true of `p` and `total`, but name the course\'s problems first: mixed jobs, the bare except, the unnamed numbers. "It is long" is not a problem: fifteen lines is fine. "There are no comments" is the opposite of session 6\'s rule. "No type hints" is true but costs a teammate less than the three above.',
                ),
                part(
                    "3",
                    "Describe in words how you would change it, and say which problem each change solves.",
                    2,
                    "Split it: one function returns rows with named fields (a frozen dataclass), one returns the weighted average, and the shell prints it, so the grade is testable. Catch only `ValueError`, report it on stderr and exit non-zero, so no row is skipped in silence. Name the weights as constants.",
                    [
                        "Separates reading, calculating and printing so the calculation returns a value; linked to testability",
                        "Replaces the bare except by catching a named error (ValueError) and either reporting it at the boundary (stderr, non-zero exit) or logging a warning for a row skipped on purpose; linked to the hidden bad row",
                        "Names the weights as constants and/or uses a named type for a row; linked to the unreadable numbers and positions",
                    ],
                    '"Rewrite it better" or "add comments" names no change. A list of changes with no problem attached earns half: the question asks for the pairing. Three smaller functions that all still print solve nothing, because the calculation has to return a value.',
                ),
            ],
            "6–8",
            "The teacher's first open shape (sample question 7), made harder: three problems instead of two, and a bare `except` that hides a bad row. A full answer uses the course's own ideas: one function, one job and computation is not output (session 6), catch only what you can handle and fail loudly at the boundary (session 7), and magic numbers and tuples as a missing type (session 6). Pair every change with its problem, in words.",
            "S6 slides 14–23; S7 slides 17–19; sample question 7",
            "slides",
            "run",
        )
    )

    qs.append(
        open_q(
            "paper-c-q17",
            "history",
            "history-s8",
            "hard",
            ["read-diff", "compare", "judgement"],
            """
A teammate shows you this diff, made on top of v0.4 of the expense-tracker (`git diff` output, without its `index` lines). `uv run pytest -q` reports `25 passed`, and ruff and mypy are green.

```diff
--- a/src/expense_tracker/cli.py
+++ b/src/expense_tracker/cli.py
@@ -26,6 +26,7 @@ def report(
     path: str = typer.Argument("expenses.csv", help="CSV file to read."),
     category: str = typer.Option("", help="Only this category."),
     minimum: float = typer.Option(0.0, "--minimum", "--min", help="Ignore amounts below this."),
+    month: str = typer.Option("", help="Only this month, as YYYY-MM."),
 ) -> None:
     try:
         expenses = read_expenses(path)
@@ -33,7 +34,7 @@ def report(
         typer.echo(f"could not read {path}", err=True)
         raise typer.Exit(1) from None
 
-    totals = total_by_category(expenses, category, minimum)
+    totals = total_by_category(expenses, category, minimum, month)
     largest = largest_expense(expenses)
     for line in format_report(path, category, minimum, totals, largest):
         typer.echo(line)
--- a/src/expense_tracker/report.py
+++ b/src/expense_tracker/report.py
@@ -39,12 +39,14 @@ def read_expenses(path: str) -> list[Expense]:
 
 
 def total_by_category(
-    expenses: list[Expense], category: str, minimum: float
+    expenses: list[Expense], category: str, minimum: float, month: str = ""
 ) -> list[tuple[str, float]]:
     totals: dict[str, float] = {}
     for expense in expenses:
         if category != "" and expense.category != category:
             continue
+        if month != "" and not expense.date.startswith(month):
+            continue
         if expense.amount < minimum:
             continue
         totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
--- a/tests/test_report.py
+++ b/tests/test_report.py
@@ -111,3 +111,9 @@ def test_report_total_is_the_sum_of_the_categories(expenses: list[Expense]) -> N
     lines = format_report("expenses.csv", "", 0.0, totals, largest_expense(expenses))
 
     assert [line for line in lines if line.startswith("TOTAL")][0].split()[-1] == "70.00"
+
+
+def test_month_filter_keeps_only_that_month(expenses: list[Expense]) -> None:
+    result = total_by_category(expenses, category="", minimum=0.0, month="2025-07")
+
+    assert result == [("clothing", 40.0), ("dining", 15.0), ("transport", 15.0)]
```

The `expenses` fixture in `tests/test_report.py` is the course's usual four sample expenses, dated 1 to 4 July 2025.

Two candidate commit messages:

- A: `Refactor report filtering`
- B: `Add a --month option to report: only expenses whose date starts with that text are totalled`
""",
            [
                part(
                    "1",
                    "What does this change do?",
                    1,
                    "It adds an optional `--month` option to `report` and a `month` parameter to `total_by_category`, which skips expenses whose date does not start with it; empty means all. One test is added.",
                    [
                        "Says it adds a month option or parameter that filters the report",
                        "Says expenses whose date does not start with the text are skipped, and that empty means all",
                    ],
                    '"It changes the filtering" repeats message A and says nothing the diff does not already show. "It adds a parameter" without saying what the parameter does describes the plumbing, not the change. Listing the three files touched is a tour of the diff, not a description of what it does.',
                ),
                part(
                    "2",
                    "Which message is better for someone reading the history six months later, and why? Name one thing a reader of message A would wrongly expect from this commit.",
                    2,
                    "B, because it says what was added and how it matches. A reader of A would expect a refactoring that leaves the output unchanged, but the report now has a new option.",
                    [
                        "Chooses B",
                        "Says a reader of A would expect a refactoring: the same output, nothing new for the user",
                        'Reasons from the history reader: B states what and how, while A hides a feature behind "refactor"',
                    ],
                    '"B because it is longer" judges length. "A is fine because the tests pass" confuses green tests with keeping the output the same. Calling it a refactoring because no old test changed misses that a new option is new behaviour.',
                ),
                part(
                    "3",
                    "The new test passes. Say why it protects the filter less than it seems to, and name in words one test you would add.",
                    2,
                    "Every fixture expense is dated July 2025, so nothing is excluded and the test passes even with the filter removed. I would add an expense from another month and assert that it is left out. An edge case is `2025-1`, which also matches October to December.",
                    [
                        "Notices every fixture expense is in July 2025, so nothing is excluded and the test would pass without the filter",
                        "Proposes a test with an expense from another month that must be excluded, or checks that no month keeps everything",
                        "Names an edge case such as a partial month matching too much, or a nonsense month giving no categories and a zero total (also accept noticing that the largest-expense line ignores `--month`)",
                    ],
                    '"The test is too short" or "needs more asserts" misses that its data cannot tell a working filter from none. Adding a second July month changes nothing. "Test --month works" is too vague to count.',
                ),
            ],
            "5–8",
            "The compare shape (sample question 8) on a diff that spans three files. The trap is the word refactor: a new option changes the output, so the label is wrong. The second trap is a test whose data cannot tell the difference between a filter and no filter, so that with the filter removed the new test still passes (25 passed). The edge-case table of session 8 supplies the next test.",
            "S7 slide 5; S8 slides 6 and 11; sample question 8",
            "slides",
            "run",
        )
    )

    qs.append(
        open_q(
            "paper-c-q18",
            "refactor-types",
            "refactor-types-s6",
            "hard",
            ["read-tool-output", "judgement"],
            """
You run `uv run mypy src` on a teammate's branch of the transport-fares project (strict mode is on in `pyproject.toml`). First the file, with line numbers, then mypy's answer:

```text
 1  from dataclasses import dataclass
 2
 3  ZONE_PRICES = {1: 1.10, 2: 1.65, 3: 2.20}
 4
 5
 6  @dataclass(frozen=True)
 7  class Trip:
 8      zone: int
 9      count: int
10
11
12  def weekly_cap(prices):
13      return max(prices.values()) * 5
14
15
16  def trip_cost(trip: Trip) -> float:
17      return ZONE_PRICES.get(trip.zone) * trip.count
18
19
20  def week_cost(trips: list[Trip]) -> float:
21      total = 0
22      for trip in trips:
23          total += trip_cost(trip)
24      return min(total, weekly_cap(ZONE_PRICES))
25
26
27  def load(rows: list[list[str]]) -> list[Trip]:
28      return [Trip(row[0], int(row[1])) for row in rows]
```

```text
src/fares.py:12: error: Function is missing a type annotation  [no-untyped-def]
src/fares.py:17: error: Unsupported operand types for * ("None" and "int")  [operator]
src/fares.py:17: note: Left operand is of type "float | None"
src/fares.py:23: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
src/fares.py:24: error: Returning Any from function declared to return "float"  [no-any-return]
src/fares.py:24: error: Call to untyped function "weekly_cap" in typed context  [no-untyped-call]
src/fares.py:28: error: Argument 1 to "Trip" has incompatible type "str"; expected "int"  [arg-type]
Found 6 errors in 1 file (checked 1 source file)
```
""",
            [
                part(
                    "1",
                    "Sort the six errors by line into the three kinds of session 7 (missing annotation, types disagree, None not handled). Which of them are repeats of an earlier error?",
                    2,
                    "Line 12 is the missing annotation, and both errors on line 24 repeat it: they vanish once it is annotated. Line 17 is None not handled. Lines 23 and 28 are types disagree.",
                    [
                        "Line 12 is a missing annotation",
                        "Both errors on line 24 are consequences of line 12 and vanish when it is annotated (accept types disagree for the no-any-return error if the student says the Any comes from the untyped weekly_cap; seeing that line 12 is the root matters more than the sort)",
                        "Line 17 is None not handled, and lines 23 and 28 are types disagree",
                    ],
                    'Counting six separate causes misses that the first error is the root of the two on line 24: annotate line 12 and the log shrinks from six errors to three. Sorting the `no-any-return` error under "types disagree" is acceptable only if the answer notes where the `Any` comes from.',
                ),
                part(
                    "2",
                    'Two of the errors point to bugs that crash a real user, and they work together. Which two, and what data triggers the crash? Which "types disagree" error is harmless, and why?',
                    2,
                    "Lines 28 and 17: the CSV gives the zone as text, so no key matches, `.get` returns `None` and line 17 raises a `TypeError`; an unknown zone does the same. Line 23 is harmless: an int total plus floats works.",
                    [
                        "Line 17: `.get` returns None for a zone with no price, and None times a number crashes",
                        "Line 28: a zone read from the CSV is text, so it never matches the number keys and feeds None into line 17",
                        "Line 23 is harmless at run time: an int total plus floats works; start from 0.0",
                    ],
                    'Naming lines 12 or 24 points at annotations, which never crash a user. Calling line 23 a crash treats all "types disagree" errors alike, when the point is to judge them one by one. Naming only line 17 is a half answer: the CSV data on line 28 is what makes every lookup fail.',
                ),
                part(
                    "3",
                    "To clear line 17 quickly, a teammate suggests changing the return type of `trip_cost` to `Any`, or adding `# type: ignore`. Do you accept? What would you do instead?",
                    2,
                    "No. `Any` or an ignore hides the only warning while the crash stays. I would handle the missing price explicitly, convert the zone with `int` on loading, and test an unknown zone.",
                    [
                        "Refuses, because Any or an ignore hides the bug and the crash remains",
                        "Handles the missing price explicitly: check for None or raise a clear error at the boundary",
                        "Converts the zone on loading so the keys match, and adds a test for an unknown zone",
                    ],
                    '"Yes, as long as CI is green" treats the check as the goal; it is the referee, not the judge. "No, ignoring is lazy" gives no alternative. Making the function return `float | None` without handling the `None` in its callers only moves the error.',
                ),
            ],
            "6–8",
            'The third open shape (sample question 9) with more noise: six errors, two of them repeats, and a harmless "types disagree" among the real bugs. Read the first error, fix it and run again: after annotating line 12 the log shrinks from six errors to three. Sorting is the session 7 skill, judging which errors can crash a user is the judgement, and refusing a blanket ignore is the course\'s position.',
            "S7 slides 8–11; labs/07-refactor.md troubleshooting; sample question 9",
            "slides",
            "run",
        )
    )

    qs.append(
        open_q(
            "paper-c-q19",
            "scrum",
            "scrum-s6",
            "hard",
            ["read-tool-output", "judgement"],
            """
At the Sprint Review the parking-lot group presents the item "A driver is charged the right fee for the hours on a ticket". Its Definition of Done, written in session 4:

1. CI is green.
2. Every item has at least one test for its new behaviour.
3. Bad input prints a message and exits non-zero.

The rule agreed with the Product Owner is 2.50 EUR per hour, capped at 18.00 EUR for each day of the stay. This is `fee`:

```python
HOURLY_RATE = 2.50
DAILY_CAP = 18.00


def fee(hours: int) -> float:
    return min(hours * HOURLY_RATE, DAILY_CAP)
```

The group says: "It is done. Watch." `tests/` holds three tests, all of `fee`. You look at the terminal:

```console
$ uv run parking pay T-104
T-104: 3 h = 7.50 EUR
$ uv run parking pay T-999
╭───────────────────── Traceback (most recent call last) ──────────────────────╮
│ ...                                                                          │
│ ❱ 12 │   hours = TICKETS[ticket]                                             │
│ ...                                                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
KeyError: 'T-999'
$ echo $?
1
$ uv run ruff check . && uv run mypy src tests
All checks passed!
Success: no issues found in 5 source files
$ uv run pytest
=================================== FAILURES ===================================
________________________ test_thirty_hours_cost_33_eur _________________________

    def test_thirty_hours_cost_33_eur() -> None:
>       assert fee(30) == 33.0
E       assert 18.0 == 33.0
E        +  where 18.0 = fee(30)

tests/test_pricing.py:13: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pricing.py::test_thirty_hours_cost_33_eur - assert 18.0 == ...
========================= 1 failed, 2 passed in 0.01s ==========================
```
""",
            [
                part(
                    "1",
                    "For each of the three Definition of Done items, say whether the terminal shows it met or not met, and give the evidence.",
                    3,
                    "Item 1 is not met: ruff and mypy pass but pytest has one failure, so CI is red. Item 2 is met: tests of `fee` exist, and one is red because the code is wrong. Item 3 is not met: an unknown ticket gives a `KeyError` traceback, not a message.",
                    [
                        "Item 1 not met: pytest shows 1 failed, so the pytest step of CI would be red (ruff and mypy are fine)",
                        "Item 2 met: tests of `fee` exist; the red one belongs to item 1 (do not mark item 2 as not met because a test fails)",
                        "Item 3 not met: a traceback and KeyError for T-999, no message; exit 1 comes from the crash",
                    ],
                    "Saying item 2 is not met because the test fails mixes it up with item 1: item 2 asks only that a test exists. Saying item 3 is met because the exit code is 1 forgets the first half, a message. Not noticing that ruff and mypy pass hides why CI would be red.",
                ),
                part(
                    "2",
                    "Is the item done? What happens to it at the Review?",
                    1,
                    "No. It misses the Definition of Done, so it is not in the Increment and does not ship.",
                    [
                        "Not done: it misses the Definition of Done, so it is not part of the Increment and does not ship",
                        "Adds that a green CI line is not the group's to remove, or that the item returns to the backlog",
                    ],
                    '"Nearly done" or "done with two bugs" is exactly what the slide calls not admissible. "The lecturer decides" misses that the Definition of Done is a public standard, the same for everyone.',
                ),
                part(
                    "3",
                    "In words, what do you ask the group to do next? Judge the failing test first.",
                    2,
                    "The test states the agreed rule (18.00 plus 6 × 2.50 is 33.00), so `fee` is wrong: fix it, not the test. The command should catch the unknown ticket, print a message on stderr and exit non-zero, with a test.",
                    [
                        "Judges that the test matches the agreed rule (33.00) and the code is wrong: fix `fee`, not the test",
                        "Handles the unknown ticket at the boundary: the command catches the lookup failure, prints a message on stderr and exits non-zero",
                        "Adds a test for the unknown ticket, or reruns all four checks until green",
                    ],
                    'Changing the test to expect 18.0 makes CI green by dropping the rule: here the test is the specification. "Fix the bugs" without saying which, or where, earns nothing. Catching `Exception` around the whole command hides other bugs; session 7 says to catch only what you can handle.',
                ),
            ],
            "6–8",
            'The fourth shape of the worst-case paper: a Definition-of-Done judgement on a terminal transcript. Read the evidence item by item, do not let a failing test and a missing test blur together, and decide who is wrong when a test fails, as in sample question 4. The Definition of Done is binary and checkable, so "almost done" does not exist.',
            "S4 slides 10 and 16–17; S7 slide 19; S8 slides 7 and 28; sample question 4",
            "slides",
            "run",
        )
    )

    return qs


# ---------------------------------------------------------------------------------------------
# PAPER D: a small step beyond. Twelve multiple-choice questions, then three open questions.
# ---------------------------------------------------------------------------------------------


def paper_d_mcq() -> list[dict[str, Any]]:
    qs: list[dict[str, Any]] = []

    qs.append(
        mcq(
            "paper-d-q01",
            "sdlc-agile",
            "sdlc-agile-s2",
            "exam",
            ["judgement", "concept"],
            """
The habit-tracker group writes its plan for the term:

| Weeks | Work |
|---|---|
| 1–2 | Idea and Analysis |
| 3 | Design |
| 4–8 | Development |
| 9 | Testing, once, before the release |
| 10 | Deployment. The project then closes. |

Which comment follows session 1?
""",
            "c",
            [
                (
                    "Development starts too late: session 1 treats three phases before the first line of code as a mistake that a good plan avoids by coding from week 1.",
                    'The slide says "Development arrives comparatively late. Three phases happen before anyone types code." Thinking before coding is the point of the sequence, not a fault.',
                ),
                (
                    "Deployment should come before Testing, so that real users find the problems the group would otherwise miss before the release.",
                    "The sequence exists to build and protect the software before users get to it. Users are not meant to be the test suite.",
                ),
                (
                    "Testing is planned once, but session 1 calls it a checklist run every time, and the plan has no Maintenance.",
                    'Right. Both gaps come straight from the slides: "A checklist, run every time, not once" and "Maintenance: ... Forever."',
                ),
                (
                    "The plan is fine: the seven phases are a finished sequence, and the lifecycle ends for good when the software is deployed.",
                    "Session 1 says the lifecycle is not a finite set of steps that ends in a perfect program. Bugs, features, refactors and tech debt start the cycle again at Design.",
                ),
            ],
            'The plan treats the lifecycle as a line that stops. Session 1 gives two corrections. Testing is "a checklist, run every time, not once", which is the idea behind a CI check on every push rather than a week of testing before release. And Maintenance is not an afterthought: most software is maintained far longer than it is written, and every bug, feature, refactor or piece of tech debt sends the project back to Design. Having three phases before Development is intended, so option a misreads the slide.',
            "S1 slides 15–19",
            "slides",
            "source",
        )
    )

    qs.append(
        mcq(
            "paper-d-q02",
            "refactor-types",
            "refactor-types-s1",
            "beyond",
            ["judgement", "read-diff"],
            """
A teammate pushes this commit to the expense-tracker at `v0.2`, with the message `Refactor: send the error through stderr`:

```diff
-        print(f"could not read {path}")
+        print(f"could not read {path}", file=sys.stderr)
```

Before the commit, on a missing file:

```console
$ uv run expenses report nosuch.csv > out.txt
$ wc -l < out.txt
1
```

After the commit:

```console
$ uv run expenses report nosuch.csv > out.txt
could not read nosuch.csv
$ wc -l < out.txt
0
```

In both runs the words are the same and the exit code is 1. Is the commit a refactoring?
""",
            "b",
            [
                (
                    "Yes: the message text and the exit code are the same, so the program does the same thing as before.",
                    "The words and the code are the same, but not the place they go. A user who redirects the output sees a different result (we ran both).",
                ),
                (
                    "No: the message moved from stdout to stderr, so a user who redirects the output now finds it on screen, not in the file.",
                    "Right: the same command leaves a different file behind. A refactoring keeps what the program does for its users, and where a message goes is part of that.",
                ),
                (
                    "Yes: choosing which stream a message uses is a change to the structure, like extracting a function, and not to the behaviour.",
                    "The stream is behaviour: it decides what `>` and `|` capture. Moving it is a change that users can see.",
                ),
                (
                    "No: the exit code changed from 1 to 0 when the message moved to stderr, and tools downstream read the exit code.",
                    "The exit code is 1 in both runs, as the stem says. The change is in the stream, not in the number.",
                ),
            ],
            "Session 7's test: a refactoring keeps the behaviour. The diff looks like tidying, one argument added to a `print`, and the words and exit code are unchanged. But stdout and stderr are different channels (session 7's failing well, and the shell's redirection): `> out.txt` captures stdout only. Before, the message went into the file; after, it stays on the screen and the file is empty. That is a behaviour change, a good one for the reasons session 7 gives (the person sees the failure even when the output is redirected), and in the real history it arrived in its own commit with the move of the printing to the shell. Real run on a copy of v0.2.",
            "S7 slides 5, 18 and 19; S10 slide 5 (redirection)",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q03",
            "project-anatomy",
            "project-anatomy-s8",
            "beyond",
            ["read-tool-output", "judgement"],
            """
The parking-lot group's `pyproject.toml` declares one dependency, `typer>=0.12`. Dani adds a coloured table to the `status` command with `from rich.table import Table` and pushes. Everything is green, and the other three clones work too:

```console
$ uv run ruff check . && uv run mypy src tests
All checks passed!
Success: no issues found in 5 source files
$ uv run parking status
┏━━━━━━━━┳━━━━━━━┳━━━━━━━┓
┃ Ticket ┃ Hours ┃ Fee   ┃
┡━━━━━━━━╇━━━━━━━╇━━━━━━━┩
│ T-104  │ 3     │ 7.50  │
│ T-221  │ 30    │ 18.00 │
└────────┴───────┴───────┘
$ grep -c rich pyproject.toml
0
```

The lockfile has this entry for `typer` (trimmed):

```toml
[[package]]
name = "typer"
version = "0.27.2"
...
dependencies = [
    { name = "annotated-doc" },
    { name = "colorama", marker = "sys_platform == 'win32'" },
    { name = "rich" },
    { name = "shellingham" },
]
```

Marta: "`rich` is in `uv.lock`, so it is already part of the project. Leave it." What is the right judgement?
""",
            "d",
            [
                (
                    "Marta is right: `uv.lock` records every package the project uses, so `rich` is already declared there and nothing more is needed.",
                    "The lockfile is generated from `pyproject.toml`. It records what was installed, including what `typer` asked for. What the project itself asks for is written only in `pyproject.toml`.",
                ),
                (
                    "Marta is right for now, but the import should sit in `try`/`except ImportError`, with a fall back to plain `print` when `rich` is missing.",
                    "That hides the dependency instead of declaring it. A program should state which libraries it needs, not guess which ones it will find.",
                ),
                (
                    "Marta is wrong: add a line to the README telling every teammate to run `pip install rich` once, so that it is present in their environment.",
                    "It documents the gap and does not close it. A new clone, CI and a stranger would still depend on a library that the project never asked for.",
                ),
                (
                    "Marta is wrong: `rich` is there only as a dependency of `typer`. The code imports it, so run `uv add rich` and commit both files.",
                    "Right. `pyproject.toml` says what the project asks for, the lockfile says what it got, and a different `typer` release may not depend on `rich` at all.",
                ),
            ],
            'Session 4 puts the two files side by side: "`pyproject.toml` says `typer>=0.12`. The lockfile says exactly which `typer`, and which of its dependencies." `rich` is in the lockfile as a dependency of `typer`, not as something the group asked for, and `grep` shows that `pyproject.toml` never mentions it. The code works today because of a choice `typer` made. If a later `typer` stops needing `rich`, the import fails although the group changed nothing. A project should declare every library it imports itself, so `uv add rich` records the request in `pyproject.toml` and updates `uv.lock`, and both files are committed.',
            "S4 slides 21 and 24; S3 slide 6",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q04",
            "scrum",
            "scrum-s9",
            "exam",
            ["judgement", "concept"],
            """
The vending-machine group finds the strict type checker slow to satisfy. It votes 4 to 0 to delete "the CI check is green" from its Definition of Done. Their argument: "In Scrum the Developers are self-managing. The team decides how the work is done, and the Definition of Done is ours."

What does the course say?
""",
            "b",
            [
                (
                    "The vote stands: the Developers are self-managing, so the team alone decides every line of its Definition of Done, including this one.",
                    "Self-managing covers how the work is done and who does what. The project brief names one line that is not the group's to choose.",
                ),
                (
                    "The group decides the rest of its Definition of Done, but green CI is the same referee for every group, so the vote cannot remove it.",
                    'Right. The brief says: "The one that is not yours to choose: a green CI check is in every group\'s Definition of Done."',
                ),
                (
                    "The vote stands once the Product Owner has approved it at the next Sprint Review, because the lecturer owns the backlog.",
                    "The brief offers no approval route for this line. It is the check that runs on a machine none of the groups owns.",
                ),
                (
                    "The vote cannot remove it, because Scrum forbids changing a Definition of Done after the first Sprint has started.",
                    "Scrum has no such rule, and the brief invites groups to edit and cut the starter list. The reason this line stays is the course's, not Scrum's.",
                ),
            ],
            'Session 4 maps the Scrum Definition of Done onto the course as "a green CI check, the same one for all" the groups. The backlog brief repeats it: the starter list can be edited and cut ("a Definition of Done with six items you ignore is worse than three you keep"), but green CI is the one line that is not the group\'s choice. Self-managing gives the Developers the how, not the bar. The type checker is part of that referee, so a slow checker is a reason to fix the types, not to remove the check.',
            "S4 slides 7 and 16; Moodle backlog brief",
            "slides",
            "source",
        )
    )

    qs.append(
        mcq(
            "paper-d-q05",
            "testing-tdd",
            "testing-tdd-s2",
            "beyond",
            ["read-code", "read-tool-output", "judgement"],
            """
The group agreed that parking costs 2.50 EUR per hour, so 3 hours should cost 7.50. This is its only test of `fee`, and two runs of it:

```python
def test_fee_for_three_hours() -> None:
    result = fee(3)
    print(f"fee(3) = {result}")
```

```console
$ uv run pytest -q
.                                                                        [100%]
1 passed in 0.00s
$ uv run pytest -q -s
fee(3) = 25.5
.
1 passed in 0.00s
```

A teammate says: "Green, so `fee` is tested." What can you conclude?
""",
            "b",
            [
                (
                    "`fee(3)` is correct, because pytest ran the test and reported no failure, and a wrong value would have shown up as one.",
                    "The `-s` run prints 25.5, and the agreed price is 7.50. A pass without an assertion says nothing about the value.",
                ),
                (
                    "Only that `fee(3)` did not raise an exception: the test compares the result with nothing, so it passes whatever `fee` returns.",
                    "Right. Arrange and Act are there, Assert is missing. With nothing that can fail, the test cannot be red.",
                ),
                (
                    "That the printed value was checked: pytest compares what a test prints with what the function returns, and would fail the test on a mismatch.",
                    "pytest never compares printed output with anything. It captures it and shows it when a test fails, or when you ask with `-s`.",
                ),
                (
                    "Nothing, because a test with no `assert` is not run at all and the dot is only a placeholder.",
                    "It ran: `1 passed` counts it and `-s` shows its print. The test simply has nothing that could fail.",
                ),
            ],
            "A test fails when an assertion fails or when an exception escapes. This test has neither, so it passes for any function that does not crash. Arrange, Act, Assert: without the Assert, the test proves only that the Act did not blow up. The second run makes the point visible, since `fee(3)` is 25.5 where the group agreed 7.50, and pytest still says passed. The lab's troubleshooting row says the same from the other side: if you never saw the test fail, you skipped red.",
            "S8 slides 6–7; labs/08-tdd.md troubleshooting",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q06",
            "testing-tdd",
            "testing-tdd-s3",
            "beyond",
            ["read-code", "read-tool-output", "judgement"],
            """
A teammate adds two tests for `remove_duplicates`, with the sample data written once at the top of the file:

```python
from expense_tracker.report import Expense, remove_duplicates

EXPENSES = [Expense("2025-07-01", "Bar Ramon", "dining", 10.0)]


def test_a_copy_of_an_expense_is_removed() -> None:
    EXPENSES.append(EXPENSES[0])

    assert len(remove_duplicates(EXPENSES)) == 1


def test_the_list_has_one_expense() -> None:
    assert len(EXPENSES) == 1
```

```console
$ uv run pytest -q tests/test_shared.py
.F                                                                       [100%]
...
E       AssertionError: assert 2 == 1
E        +  where 2 = len([Expense(...), Expense(...)])
...
FAILED tests/test_shared.py::test_the_list_has_one_expense - AssertionError: ...
1 failed, 1 passed in 0.01s
$ uv run pytest -q tests/test_shared.py::test_the_list_has_one_expense
.                                                                        [100%]
1 passed in 0.00s
```

No code changed between the two runs. What explains the failure, and what prevents it?
""",
            "d",
            [
                (
                    "pytest runs the tests of a file in random order, so the failure is luck; the order should be pinned with a plugin, and then the suite will pass.",
                    "pytest runs a file's tests in the order they are written. What differs between the two runs is which tests ran at all.",
                ),
                (
                    "`remove_duplicates` changes the list it receives, so the second test sees the result of the first; the function should work on a copy of its argument.",
                    "`remove_duplicates` builds a new list and leaves its argument alone. The extra item comes from the `append` in the first test.",
                ),
                (
                    "The test is flaky: it passes when run alone, so rerunning the whole file until it is green is acceptable, and nothing needs to change.",
                    "It fails every time the first test runs before it. Rerunning does not remove a fault in the tests.",
                ),
                (
                    "The first test changed the shared list and the second sees that; a fixture builds a fresh list for each test, so no test affects another.",
                    "Right. One shared list carries a side effect from one test to the next. A fixture is called again for every test.",
                ),
            ],
            "`EXPENSES` is one list shared by every test in the file. The first test appends a copy, the second runs afterwards, finds two items and fails. Run alone, the first test never ran, so the second passes. Tests must not depend on each other or on their order. Session 8's fixture is the tool: pytest calls it again for each test that names it, so every test starts from its own fresh list (Arrange). A mutable value shared at module level is the same fault as a test that writes into the real `data/` folder: a side effect that outlives the test.",
            "S8 slide 9; S8 slides 20–23",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q07",
            "testing-tdd",
            "testing-tdd-s5",
            "beyond",
            ["read-code", "read-tool-output"],
            """
The group adds a field to the frozen dataclass of the expense-tracker, so that each expense can carry labels:

```diff
-from dataclasses import dataclass
+from dataclasses import dataclass, field
...
     amount: float
+    tags: list[str] = field(default_factory=list)
```

`uv run mypy src tests` still says `Success: no issues found in 6 source files`, but pytest goes red (one of four failures shown, trimmed):

```text
    def test_expenses_without_duplicates_are_unchanged() -> None:
>       assert remove_duplicates([BAR, ZARA]) == [BAR, ZARA]
...
src/expense_tracker/report.py:96: in remove_duplicates
    return list(dict.fromkeys(expenses))
                ^^^^^^^^^^^^^^^^^^^^^^^
...
self = Expense(date='2025-07-01', merchant='Bar Ramon', category='dining', amount=10.0, tags=[])

>   ???
E   TypeError: unhashable type: 'list'

<string>:26: TypeError
```

Which statement explains the failure?
""",
            "a",
            [
                (
                    "`frozen=True` hashes all the fields, and a `list` field cannot be hashed; a tuple of strings would work.",
                    "Right. The hash of an `Expense` is built from its fields. A list is mutable, so Python refuses to hash it, and `dict.fromkeys` needs the hash.",
                ),
                (
                    "`frozen=True` does not make `Expense` hashable at all, so the four tests passed before only by luck, not by design.",
                    "Session 8 says frozen makes `Expense` hashable, and it did until `tags` arrived. The old tests passed because every field could be hashed.",
                ),
                (
                    "`dict.fromkeys` accepts only strings and numbers as keys, and the new field changed the type of its argument.",
                    "Any hashable object can be a key, including a frozen dataclass. The argument is still a `list[Expense]`; what changed is whether an `Expense` can be hashed.",
                ),
                (
                    "mypy should have reported this, so mypy cannot have been running in strict mode.",
                    "The output shows mypy passing under the project's strict settings. Whether the values a field holds can be hashed at run time is not something its annotations expose.",
                ),
            ],
            'A frozen dataclass with the default `eq` gets a `__hash__` built from all its fields. Every old field was a string or a float, so hashing worked and `dict.fromkeys` could use `Expense` as a key ("session 6\'s frozen=True pays off here"). A `list` is mutable, so Python will not hash it, and the `TypeError` appears the first time an `Expense` is used as a key. `frozen` stops reassigning `tags`, not appending to the list. A `tuple[str, ...]` keeps the object hashable, and mypy cannot see the problem.',
            "S6 slide 24; S8 slide 16",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q08",
            "core-shell-failing",
            "core-shell-failing-s7",
            "hard",
            ["read-tool-output", "judgement"],
            """
A teammate writes a test for the missing-file case of the expense-tracker's `report` command, and it fails:

```python
def test_a_missing_file_is_explained_to_the_user() -> None:
    result = runner.invoke(app, ["report", "nosuch.csv"])

    assert result.exit_code == 1
    assert "could not read nosuch.csv" in result.stdout
```

```text
    def test_a_missing_file_is_explained_to_the_user() -> None:
        result = runner.invoke(app, ["report", "nosuch.csv"])

        assert result.exit_code == 1
>       assert "could not read nosuch.csv" in result.stdout
E       AssertionError: assert 'could not read nosuch.csv' in ''
E        +  where '' = <Result SystemExit(1)>.stdout

tests/test_missing.py:12: AssertionError
=========================== short test summary info ============================
FAILED tests/test_missing.py::test_a_missing_file_is_explained_to_the_user - ...
========================= 1 failed, 24 passed in 0.05s =========================
```

In a terminal, the message does appear:

```console
$ uv run expenses report nosuch.csv > out.txt
could not read nosuch.csv
$ wc -l < out.txt
0
```

What is the right change?
""",
            "c",
            [
                (
                    "Change `cli.py` to `print` the message, so that it lands in `result.stdout` and the test passes.",
                    "That moves the complaint into the data stream. A saved report would contain `could not read`, and a pipe would carry it to the next program.",
                ),
                (
                    "Delete the assertion on the message: the exit code already proves the failure, and the wording of a message does not need a test.",
                    "The exit code says that it failed, not why. The message is the part the user reads, and v0.4's own test checks it.",
                ),
                (
                    "Assert on `result.stderr` instead: the program rightly writes the complaint to stderr; the test looked in the wrong stream.",
                    "Right. Session 7: the shell prints the reason to stderr and exits non-zero. The terminal transcript shows it: with stdout redirected, the message still reaches the screen.",
                ),
                (
                    "Wrap the call in `try/except SystemExit` so that the message is captured.",
                    "`CliRunner` already catches the exit and records it in the result. The text is in a different stream, not hidden by the exit.",
                ),
            ],
            'The terminal transcript shows two streams. With stdout sent to `out.txt`, the message still appears on the screen and the file has 0 lines, so the message was written to stderr, as session 7 prescribes: "Shell: catches it, prints to stderr, exits non-zero." `CliRunner` keeps the two streams apart, and `result.stdout` is empty. The program is right and the test looked in the wrong place. The demo\'s own v0.4 test asserts on `result.stderr`.',
            "S7 slide 19; S8 slide 21; history f3d9870",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q09",
            "refactor-types",
            "refactor-types-s4",
            "beyond",
            ["read-code", "read-tool-output", "judgement"],
            """
The vending-machine group's code and its checks:

```python
import sys

PRICES: dict[str, float] = {"A1": 1.20, "A2": 1.50, "B1": 0.90}


def price_of(slot: str) -> float:
    return PRICES[slot]


def main() -> None:
    slot = sys.argv[1]
    print(f"{slot} costs {price_of(slot):.2f} EUR")


if __name__ == "__main__":
    main()
```

```console
$ uv run mypy --strict vending.py
Success: no issues found in 1 source file
$ uv run ruff check .
All checks passed!
$ uv run python vending.py A2
A2 costs 1.50 EUR
$ uv run python vending.py C9
Traceback (most recent call last):
  File "vending.py", line 16, in <module>
    main()
    ~~~~^^
  File "vending.py", line 12, in main
    print(f"{slot} costs {price_of(slot):.2f} EUR")
                          ~~~~~~~~^^^^^^
  File "vending.py", line 7, in price_of
    return PRICES[slot]
           ~~~~~~^^^^^^
KeyError: 'C9'
```

A teammate says: "Strict mypy and ruff are green, so this can't crash." What do you conclude?
""",
            "d",
            [
                (
                    "mypy is misconfigured: strict mode should have flagged the dictionary lookup, so switch on more of its checks.",
                    "The configuration is fine. A lookup `PRICES[slot]` is correctly typed as returning a `float`; whether the key exists is not a type question.",
                ),
                (
                    "Use `PRICES.get(slot, 0.0)` instead of the lookup: it never raises, so an unknown slot simply costs nothing and the program carries on.",
                    "The crash disappears and so does the information. A free item for any typo is a silent wrong answer, the same fault as returning -1.",
                ),
                (
                    "Declare `PRICES` as `dict[str, Any]`: mypy would then report the lookup, and that is the fix for this crash.",
                    "`Any` weakens the checker. It would stop mypy from helping, not make `C9` valid.",
                ),
                (
                    'The types are right, but "unknown slot" was never decided or tested; mypy checks types only, so choose the behaviour and test it.',
                    'Right. Session 8\'s edge-case table has a row for "Missing: not there?". The fix is a decision: a message on stderr and a non-zero exit at the boundary.',
                ),
            ],
            'Static types and runtime data are different things. mypy checks that `price_of` takes a string and returns a float, and it does. It cannot know which strings exist in the dictionary at run time. The checker finds one class of bugs, the empty-list-gives-None kind; a missing key is another class, found by an edge case on purpose ("Missing: not there?") and handled at the boundary, in line with session 7. Green tools mean the questions they ask were answered, not that nothing can go wrong.',
            "S7 slide 8; S8 slide 11",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q10",
            "pipes-bash",
            "pipes-bash-s7",
            "beyond",
            ["read-code", "read-tool-output", "predict-output"],
            """
A teammate adds a guard to `scripts/check.sh`: no `print(` calls may be left in `src/`, which keeps the functional core clean. The script:

```bash
#!/usr/bin/env bash
set -euo pipefail

grep -rn "print(" src/
uv run ruff check .
uv run mypy src tests
uv run pytest -q
```

The code in `src/` has no `print` calls. The run:

```console
$ ./scripts/check.sh
$ echo $?
1
```

Nothing is printed and the script ends at once. Why?
""",
            "c",
            [
                (
                    "`ruff check .` failed first, and `set -e` hides the messages of the command that stops the whole script, so only the exit code is left.",
                    "The script never reached ruff, and `set -e` hides nothing: it only stops the script at a failing command.",
                ),
                (
                    "`grep -r` stops at the first folder it cannot read, and `set -e` then ends the script silently.",
                    "Nothing is unreadable here. grep searched `src/` normally and found no line to print.",
                ),
                (
                    "`grep` exits with 1 when it finds no line, and `set -e` stops the script at any non-zero exit, so a clean tree fails the guard.",
                    "Right. The guard is backwards: a clean tree stops the script, and a tree with prints would print the lines and carry on.",
                ),
                (
                    "`set -o pipefail` treats an empty result as a failed pipeline, even though this line has no pipe.",
                    "pipefail concerns the stages of a pipeline. This is a single command, and the non-zero status is grep's own.",
                ),
            ],
            "grep uses three exit codes: 0 when it found a line, 1 when it ran fine and found none, 2 for trouble. For the shell, 1 is a failure, and `set -e` stops the script at the first one. So with a clean `src/` the guard line exits 1 and the script ends before ruff, in silence. Worse, with a `print(` left in, grep prints the line, exits 0 and the script carries on and passes: the guard is inverted. A check that should fail on a match must test the match, for example in an `if`, and exit non-zero itself.",
            "S5 slide 9; S10 slide 16 (grep exits 1 under set -e)",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q11",
            "pipes-bash",
            "pipes-bash-s6",
            "beyond",
            ["read-code", "read-tool-output", "predict-output"],
            """
Before tagging v0.5, a teammate writes `scripts/release-check.sh` and runs it on a branch where one test fails:

```bash
#!/usr/bin/env bash
uv run pytest -q
echo "pytest finished"
if [ $? -ne 0 ]; then
    echo "tests failed"
    exit 1
fi
echo "Release checks passed"
```

```console
$ ./scripts/release-check.sh
..F                                                                      [100%]
...
FAILED tests/test_pricing.py::test_thirty_hours_cost_33_eur - assert 18.0 == ...
1 failed, 2 passed in 0.01s
pytest finished
Release checks passed
$ echo $?
0
```

Why does the script say the release checks passed?
""",
            "a",
            [
                (
                    "`$?` holds the status of the latest command, which by then is the `echo`, so the `if` tests the `echo`'s 0 and not pytest's.",
                    "Right. pytest's exit code 1 was overwritten one line later by the status of `echo`.",
                ),
                (
                    "pytest exits with 0 whenever at least one test passes, so `$?` was already 0 after the run, whatever the failing test said.",
                    "pytest exits with a non-zero code when any test fails. That is what CI reads.",
                ),
                (
                    "`-ne` compares its two values as text, so `1` and `0` never count as different and the `if` body is skipped.",
                    "`-ne` compares numbers. The condition goes wrong because of what `$?` holds, not because of how it is compared.",
                ),
                (
                    "`exit 1` inside the `if` only leaves the `if` block, so the script carries on to its last line and prints the final message.",
                    "`exit` ends the whole script. The `if` body never ran in this transcript.",
                ),
            ],
            "`$?` is the exit status of the last command that finished. `echo \"pytest finished\"` ran in between and succeeded, so `$?` was 0 when the `if` looked at it, and pytest's failure was gone. Test the command itself, as in `if ! uv run pytest -q; then`, or let the shell stop with `set -e` at the top, as the course's `check.sh` does. Reading a status one line late is the same family of mistake as `| tail` hiding pytest's exit code in a pipeline: the script ends in success because the last thing that ran succeeded.",
            "S5 slide 9; S10 slides 15–16 ($? and set -e)",
            "slides",
            "run",
        )
    )

    qs.append(
        mcq(
            "paper-d-q12",
            "pipes-bash",
            "pipes-bash-s2",
            "beyond",
            ["read-tool-output", "predict-output"],
            """
The expense-tracker's `report` command writes `could not read nosuch.csv` to stderr when the file is missing. A teammate wants both streams in one file and tries two commands that differ only in the order of the redirections. (The shell applies redirections from left to right: each one points a stream at wherever its target points at that moment.)

```console
$ uv run expenses report nosuch.csv 2>&1 > all.txt
could not read nosuch.csv
$ wc -l < all.txt
0
$ uv run expenses report nosuch.csv > all.txt 2>&1
$ wc -l < all.txt
1
```

What explains the different results?
""",
            "b",
            [
                (
                    "`>` only takes effect when it comes last on the line, so the first command ignored it and the shell wrote nothing into `all.txt` at all.",
                    "The first command did create and empty `all.txt`: it has 0 lines. `>` moved stdout, which had nothing to write.",
                ),
                (
                    "In the first command `2>&1` copied stdout's target, the screen, before `> all.txt` moved stdout; in the second, stderr followed stdout into the file.",
                    "Right. `2>&1` means make stderr point where stdout points now.",
                ),
                (
                    "`2>&1` sends stderr to a file named `1`, so the first command put the message into that file, which is why the screen showed it, and the second command did not.",
                    "With the `&`, the `1` means the stream called 1, which is stdout. A file named `1` would need `2>1`.",
                ),
                (
                    "The first command ran before `all.txt` existed, so the shell could not write to it; the second command created the file first, which fixed the problem for the message.",
                    "`>` creates the file when the command starts, in both commands.",
                ),
            ],
            "`2>&1` means make stderr point where stdout points right now. The shell reads the redirections from left to right before the program starts. In `2>&1 > all.txt`, stdout still points at the screen when `2>&1` is processed, so stderr goes to the screen, and then `> all.txt` re-points stdout alone: the message stays on the screen and the file is empty. In `> all.txt 2>&1`, stdout already points at the file when stderr is joined to it, so the message lands in `all.txt`. The order that works is `cmd > all.txt 2>&1`.",
            "S7 slide 19; extension of S10 slide 5 (2>&1 is not on the slides)",
            "slides",
            "run",
        )
    )

    return qs


def paper_d_open() -> list[dict[str, Any]]:
    qs: list[dict[str, Any]] = []

    qs.append(
        open_q(
            "paper-d-q13",
            "pipes-bash",
            "pipes-bash-s8",
            "beyond",
            ["read-code", "read-tool-output", "judgement"],
            """
A group's first `scripts/check.sh`, and a run on a branch where mypy reports an error and one test fails. (`tail -n 3` prints the last three lines of what it receives.)

```bash
#!/usr/bin/env bash
uv run ruff check . ; uv run ruff format --check .
uv run mypy src tests || echo "types need work"
uv run pytest -q | tail -n 3
echo "Safe to tag v0.5"
```

```console
$ ./scripts/check.sh
All checks passed!
6 files already formatted
src/parking_lot/pricing.py:9: error: Function is missing a type annotation  [no-untyped-def]
Found 1 error in 1 file (checked 5 source files)
types need work
=========================== short test summary info ============================
FAILED tests/test_pricing.py::test_thirty_hours_cost_33_eur - assert 18.0 == ...
1 failed, 2 passed in 0.01s
Safe to tag v0.5
$ echo $?
0
```
""",
            [
                part(
                    "1",
                    "In one sentence, what does the script do?",
                    1,
                    'It runs the lint check, the format check, mypy and pytest in turn and then prints "Safe to tag v0.5".',
                    [
                        "Says it runs the four checks (lint, format, types, tests) in order",
                        'Mentions the final "Safe to tag" message',
                    ],
                    '"It checks the code" is too loose: name the four checks, in the order they run. "It stops when something fails" is the opposite of what the transcript shows, where every line runs and the last line still reports success.',
                ),
                part(
                    "2",
                    "Name two problems the transcript shows.",
                    2,
                    "It prints \"Safe to tag\" and exits 0 although mypy and a test failed. Nothing stops at a failure, so the exit code is only the last `echo`'s. `|| echo` swallows mypy's failure and `| tail` hides pytest's exit code.",
                    [
                        "It prints Safe to tag and exits 0 although two checks failed (the exit code is only the last command's)",
                        "No `set -e`: a failing check does not stop the script",
                        "`|| echo` swallows mypy's failure",
                        "`| tail` hides pytest's exit code behind tail's",
                    ],
                    '"The test fails" and "mypy has an error" are not problems of the script: those are the branch\'s. The script\'s fault is that it reports success anyway. "It should have comments" or "the name is bad" misses the exit-code point that matters to CI.',
                ),
                part(
                    "3",
                    "Describe in words how you would change the script, and say which problem each change solves.",
                    2,
                    "Add `set -euo pipefail` under the shebang: it stops at the first failure with a non-zero exit, and pipefail stops `tail` hiding pytest's result. Delete `|| echo`. Then the final message appears only if everything passed.",
                    [
                        "Adds set -e (with pipefail): stops at the first failure and exits non-zero; linked to the continue/exit 0 problem",
                        "Removes `|| echo` and/or deals with the `tail` pipe (pipefail or removing it); linked to the swallowed failures",
                        "Notes that the final message now appears only if every check passed",
                    ],
                    '"Make it stricter" names no change. Replacing `;` by `&&` on one line fixes only that line. Adding `|| exit 1` after each plain command works for those lines but repeats the job that `set -e` does once, and it does not catch pytest behind the `| tail` pipe unless `pipefail` is also set; give credit only if the answer handles the pipe.',
                ),
            ],
            "5–8",
            'Session 10 covered pipes, text wrangling and bash scripts, and wrote `scripts/check.sh` together in class. This is the first open shape in a shell script: say what it does, find what is wrong, change it in words. The exit code is what CI reads, and session 5 puts it plainly: a program that prints an error and exits 0 is a program that lies.',
            "S5 slide 9; S9 slide 6; S10 slides 16–18 (check.sh, set -e, pipefail)",
            "slides",
            "run",
        )
    )

    qs.append(
        open_q(
            "paper-d-q14",
            "testing-tdd",
            "testing-tdd-s5",
            "beyond",
            ["read-diff", "read-tool-output", "judgement"],
            """
A teammate "simplifies" `remove_duplicates` in the expense-tracker (v0.4) and pushes:

```diff
 def remove_duplicates(expenses: list[Expense]) -> list[Expense]:
-    return list(dict.fromkeys(expenses))
+    return list(set(expenses))
```

Over the next hour CI goes red, green and red again on the same code. The teammate reruns the tests locally three times, with no other change:

```console
$ uv run pytest -q tests/test_duplicates.py
...
FAILED tests/test_duplicates.py::test_expenses_without_duplicates_are_unchanged
FAILED tests/test_duplicates.py::test_an_exact_duplicate_is_removed_and_the_first_one_kept
2 failed, 3 passed in 0.01s
$ uv run pytest -q tests/test_duplicates.py
5 passed in 0.01s
$ uv run pytest -q tests/test_duplicates.py
...
FAILED tests/test_duplicates.py::test_same_merchant_on_another_day_is_not_a_duplicate
1 failed, 4 passed in 0.01s
```

In a failing run, the assertion in `test_an_exact_duplicate_is_removed_and_the_first_one_kept` reports:

```text
>       assert remove_duplicates([BAR, ZARA, BAR]) == [BAR, ZARA]
E       AssertionError: assert [Expense(date... amount=10.0)] == [Expense(date... amount=40.0)]
E         At index 0 diff: Expense(date='2025-07-02', merchant='Zara', category='clothing', amount=40.0) != Expense(date='2025-07-01', merchant='Bar Ramon', category='dining', amount=10.0)
```

Two candidate commit messages for the change:

- A: `Simplify remove_duplicates`
- B: `Use set in remove_duplicates: the order of the expenses is no longer kept`
""",
            [
                part(
                    "1",
                    "What does the change do to the behaviour of `remove_duplicates`?",
                    1,
                    'It still removes duplicates, but a set has no order, so the result comes back in an arbitrary order and "the first one kept" is lost. `dict.fromkeys` kept the insertion order.',
                    [
                        "Says the duplicates are still removed but the order is no longer kept",
                        "Contrasts with dict.fromkeys, which keeps insertion order",
                    ],
                    '"It makes the code simpler" repeats message A. "It removes duplicates faster" is not shown by the diff. "It breaks the function" does not say how: the duplicates are still removed.',
                ),
                part(
                    "2",
                    "The same code gives different results on different runs. Explain why, and say what you do next and what you do not do.",
                    2,
                    "Python hashes strings differently in each run, so the order of a set of `Expense` objects changes, and tests that compare lists pass only when the order happens to match. I would not rerun until green or loosen the tests: I would restore `dict.fromkeys`.",
                    [
                        "A set has no insertion order, and with strings inside the objects the order differs between runs",
                        "The red and green runs are one real behaviour change showing up by chance, not a random test",
                        "Does not rerun until green and does not weaken the tests; restores dict.fromkeys or an order-keeping version",
                    ],
                    '"The tests are flaky, rerun them" is the move the sample questions warn about: the test is not at fault. "CI is broken" or "a cache problem" blames the tool. Deleting the order tests makes CI green by dropping the requirement.',
                ),
                part(
                    "3",
                    "Which message is better for someone reading the history six months later? Is the commit a refactoring?",
                    2,
                    'B, because it records the lost order. But it is not a refactoring, since the output changes, and "simplify" in A promises the same behaviour. Better not to make the commit.',
                    [
                        "Chooses B because it states the behaviour change (order no longer kept)",
                        'Says it is not a refactoring because the output (the order) changes, and that "simplify" claims otherwise',
                    ],
                    '"B because it is longer" judges length. "A, because the tests will tell us" ignores that the tests were already telling, and were being rerun away. Calling the commit a refactoring because the duplicates are still removed overlooks the order.',
                ),
            ],
            "5–8",
            "Session 8's live cycle ends with dict.fromkeys because dictionaries keep insertion order. The obvious next question is what a set does instead. It keeps no order, and with strings inside the objects the order changes with every run, so the same code goes red and green. The question joins that to session 7's definition of a refactoring (the output must not change) and to the habit of reading a failing test instead of rerunning it.",
            "S8 slide 16; S7 slide 5; sample question 4",
            "slides",
            "run",
        )
    )

    qs.append(
        open_q(
            "paper-d-q15",
            "testing-tdd",
            "testing-tdd-s8",
            "beyond",
            ["read-tool-output", "judgement"],
            """
At v0.4 of the expense-tracker, `cli.py` is the shell: lines 36–39 are what the `report` command does after the file was read successfully, and lines 49–58 are the body of the `add` command. No test ran either of them, so a teammate adds two tests in five minutes:

```python
def test_report_runs(tmp_path: Path) -> None:
    csv_file = tmp_path / "expenses.csv"
    csv_file.write_text("date,merchant,category,amount\\n2025-07-01,Bar Ramon,dining,10.00\\n")

    result = runner.invoke(app, ["report", str(csv_file)])

    assert result.exit_code == 0


def test_add_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["add", "Bar Ramon", "dining", "12.50"])

    assert result.exit_code == 0
```

```console
$ uv run pytest --cov=expense_tracker --cov-report=term-missing
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/expense_tracker/__init__.py       0      0   100%
src/expense_tracker/cli.py           33      0   100%
src/expense_tracker/report.py        62      0   100%
---------------------------------------------------------------
TOTAL                                95      0   100%
============================== 26 passed in 0.08s ==============================
```

"100%, and every test asserts something," says the teammate, "so `cli.py` is fully tested. Let us make pytest fail below 100% in `scripts/check.sh` and put that in our Definition of Done." To see how much 100% proves, the group's lead breaks `add` on purpose and runs the suite again:

```diff
-        writer.writerow([date, merchant, category, f"{amount:.2f}"])
+        writer.writerow([date, category, merchant, int(amount)])
```

```console
$ uv run pytest --cov=expense_tracker --cov-report=term-missing
...
TOTAL                                95      0   100%
============================== 26 passed in 0.07s ==============================
```
""",
            [
                part(
                    "1",
                    "What does the 100% prove, and what does the last run show it does not prove?",
                    2,
                    "That every line of `cli.py` ran, and nothing more. The tests assert only the exit code, so after `add` was broken to write the wrong columns, all 26 tests still passed at 100%.",
                    [
                        "Coverage means every line ran, not that its results were checked",
                        "Uses the last run: add was broken and the suite stayed green at 100%",
                        "Names the cause: the assertions check only the exit code, not what was written or printed",
                    ],
                    '"100% means it is tested" is the belief the slide warns about. "Coverage is useless" overshoots: the percentage is a good map of what never ran. "The tests have no asserts" is wrong here: they assert, but too little.',
                ),
                part(
                    "2",
                    "Do you accept the proposal to fail below 100% in `check.sh` and to put it in the Definition of Done? Give your reasoning and say what you would do instead.",
                    2,
                    "No. A gate invites tests that reach the number and check almost nothing. Coverage is a map: use Missing to find gaps, then assert on results and edge cases. The Definition of Done can ask for a test that would fail if the behaviour broke.",
                    [
                        "Rejects the 100% gate: the number can be reached with tests that check almost nothing",
                        "States that coverage is a map to find forgotten code, not a score to chase",
                        "Proposes assertion-based tests on behaviour, or a checkable Definition of Done line about meaningful tests",
                    ],
                    '"Yes, higher coverage is always better" ignores the last run. "No, because 100% is impossible" is wrong: it was reached here. "No" with no alternative scores half: the question asks what to do instead.',
                ),
                part(
                    "3",
                    "Name in words one assertion you would add to `test_add_runs` so that the broken `add` is caught.",
                    2,
                    "Pass a fixed `--date`, read `data/expenses.csv` in `tmp_path` and assert that its last row is that date, Bar Ramon, dining and 12.50, in that order.",
                    [
                        "Looks at what add wrote (the CSV row) and not only at the exit code",
                        "Pins the date with --date, or leaves it out of the comparison, so the test does not depend on the day it runs",
                        "Checks the column order and the two decimals, which the broken version gets wrong",
                    ],
                    '"Assert the exit code is 1" or "add more tests" names nothing. "Assert the file exists" passes on the broken version too. Comparing the row with today\'s date fails tomorrow.',
                ),
            ],
            "6–8",
            "Session 8 closes the coverage slide with a warning: 100% coverage with weak assertions proves nothing, so never chase the number. This question runs that sentence on the demo repository. A full answer says what the percentage does prove, that every line ran. It then uses the broken `add` to reject the gate, and ends with the assertion that would have caught it, aimed at the row the command writes.",
            "S8 slide 24; S8 slides 20–23",
            "slides",
            "run",
        )
    )

    return qs


def build() -> dict[str, Any]:
    paper_c = {
        "id": "paper-c",
        "title": "Paper C",
        "kind": "worst-case",
        "minutes": 60,
        "intro_md": (
            "Paper C is the worst paper the teacher could set inside his own limits: longer and noisier "
            "artefacts, close distractors, and many questions that combine two sessions. Sit it cold, "
            "with pen and paper and no notes: fifteen multiple-choice questions, then four open "
            "questions, sixty minutes. Plan about 24 minutes for the multiple choice and 9 minutes for "
            "each open question, mark yourself afterwards, and follow the Revise link on every question "
            "you lose."
        ),
        "questions": paper_c_mcq_a() + paper_c_mcq_b() + paper_c_open(),
    }
    paper_d = {
        "id": "paper-d",
        "title": "Paper D",
        "kind": "beyond",
        "minutes": 60,
        "intro_md": (
            "Paper D goes a small step past the sample questions. It asks for the obvious next "
            "consequence of an idea the course taught, such as what a green test without an assertion "
            "proves, and it uses the session 10 material: pipes, redirection and "
            "bash scripts. It is harder than the real exam is likely to be, and everything in it can "
            "still be worked out from sessions 1–10 and careful reading. Sit it as you would the real "
            "paper: twelve multiple-choice questions, then three open questions, sixty minutes."
        ),
        "questions": paper_d_mcq() + paper_d_open(),
    }
    return {"papers": [paper_c, paper_d]}


def main() -> None:
    data = build()
    with OUT.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    for paper in data["papers"]:
        kinds = [q["type"] for q in paper["questions"]]
        print(f"{paper['id']}: {kinds.count('mcq')} mcq, {kinds.count('open')} open -> {OUT.name}")


if __name__ == "__main__":
    main()
