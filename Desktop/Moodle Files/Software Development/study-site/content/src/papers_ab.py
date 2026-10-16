"""Mock papers A and B (realistic): writes content/_papers-ab.json.

Run: uv run python content/src/papers_ab.py
Every artefact shown in a stem was produced by actually running the tool (evidence in the
author's scratchpad under work/paper-a and work/paper-b).
"""

import json
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parent.parent / "_papers-ab.json"


def md(text: str) -> str:
    return text.strip("\n")


def mcq(
    qid: str,
    module: str,
    section: str,
    level: str,
    skills: list[str],
    stem: str,
    options: list[tuple[str, str]],
    answer: str,
    explanation: str,
    source_ref: str,
    origin: str,
    verified_by: str,
) -> dict[str, Any]:
    assert len(options) == 4 and answer in "abcd"
    return {
        "id": qid,
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "options": [
            {"text_md": md(t), "correct": "abcd"[i] == answer, "why_md": md(w)}
            for i, (t, w) in enumerate(options)
        ],
        "explanation_md": md(explanation),
        "module_ref": module,
        "section_ref": section,
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified_by,
    }


def part(
    label: str, prompt: str, marks: int, model: str, rubric: list[str], weak: str
) -> dict[str, Any]:
    return {
        "label": label,
        "prompt_md": md(prompt),
        "marks": marks,
        "model_answer_md": md(model),
        "rubric": rubric,
        "weak_answers_md": md(weak),
    }


def open_q(
    qid: str,
    module: str,
    section: str,
    level: str,
    skills: list[str],
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    source_ref: str,
    origin: str,
    verified_by: str,
) -> dict[str, Any]:
    return {
        "id": qid,
        "type": "open",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "parts": parts,
        "lines": "5–8",
        "explanation_md": md(explanation),
        "module_ref": module,
        "section_ref": section,
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified_by,
    }


# ---------------------------------------------------------------------------------------------
# PAPER A
# ---------------------------------------------------------------------------------------------

A: list[dict[str, Any]] = []

A.append(
    mcq(
        "paper-a-q01",
        "refactor-types",
        "refactor-types-s1",
        "exam",
        ["concept", "judgement"],
        """
The parking-lot group's `fee` charges 2.50 EUR for every hour started, and all its tests pass:

```python
def fee(minutes: int) -> float:
    hours = minutes // 60 + 1
    return hours * 2.5
```

Which change to the parking fees module is a refactoring?
""",
        [
            (
                "Add `FREE_MINUTES = 15` to the module, so that the first quarter of an hour costs nothing, and update the tests",
                "The first 15 minutes are now free: `fee(10)` goes from 2.50 to 0.0 in a real run. That is new behaviour, so it is a feature.",
            ),
            (
                "Move the bare `2.5` into a constant `HOURLY_RATE = 2.5` and write `hours * HOURLY_RATE`, leaving every test unchanged",
                "Right: the structure changes (a name instead of a bare number) and every price stays the same. We ran `fee` on 0, 10, 59, 60, 90 and 120 minutes before and after: identical results.",
            ),
            (
                "Fix the off-by-one at exactly 60 minutes by writing `(minutes + 59) // 60`, so that one full hour costs 2.50 EUR, not 5.00",
                "`fee(60)` goes from 5.0 to 2.5 and `fee(0)` from 2.5 to 0.0 in a real run. A bug fix changes the output on purpose and belongs in its own commit.",
            ),
            (
                "Change the return type to `str` and return text such as `5.00 EUR`, so that the shell can print the fee without formatting",
                "The return type changes, and every caller that adds or compares fees breaks. A refactoring keeps what the program does for everyone who uses it.",
            ),
        ],
        "b",
        """
The test from session 7: change the structure, keep the behaviour, and "if the output changes, it was not a refactoring". Naming the rate is exactly that: the numbers `fee` returns are the same, so nothing a user, a test or CI sees has moved. The other three each change an output or a type, on purpose or not. The off-by-one at 60 minutes may well be a bug, and fixing it is worth doing, but as a separate change with its own test, because the fix alters `fee(60)`. Mixing a refactoring with a fix in one commit makes the history hard to read, and the tests cannot tell you which of the two broke something.
""",
        "S7 slides 5 and 6; sample Q2 shape",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q02",
        "sdlc-agile",
        "sdlc-agile-s6",
        "exam",
        ["concept", "judgement"],
        """
A vending-machine group plans like Waterfall: the specification is signed in week 1 and may change only through a formal change request. The project is due in week 8. In week 6 the owner tries the first working machine and asks for card payment, which the specification does not mention. What does this show?
""",
        [
            (
                "The analysis phase was done badly: a more careful specification would have listed card payment in week 1.",
                "Session 2 says the opposite. Customers understand what they want only when they see a working version, and that is normal, not a failure of analysis.",
            ),
            (
                "The owner is at fault, because a signed specification is a contract and later requests should be refused.",
                "Refusing may be Waterfall's rule, but it does not say what the situation shows. The group would deliver the signed machine and the owner would not want it.",
            ),
            (
                "The owner first saw working software near the end, so a wrong assumption surfaced late, at a high cost.",
                "Right: this is the second weakness on slide 7, feedback that arrives too late. The gate between phases is an approved document, so the customer sees a machine only at the end.",
            ),
            (
                "Waterfall cannot work for any project, so the group should have used Agile from the first week.",
                "Too strong. Waterfall suits projects with known, stable requirements, a fixed price or a regulator. 'Waterfall is always wrong' is as weak as 'Agile is always right'.",
            ),
        ],
        "c",
        """
Waterfall fixes the requirements early and approves a document at every gate, and the customer is involved mostly at the start and the end. When the owner finally sees working software in week 6 of 8, the missing requirement appears when most of the work is done, and a formal change request has to go back through the gates. This is feedback that arrives too late (slide 7). It is not a failure of the analysis: requirements changing once people see a first version is normal for software. Agile answers with short cycles in which the owner sees something usable every few weeks, so card payment would surface in the first iterations.
""",
        "S2 slides 5 to 8",
        "slides",
        "reasoning",
    )
)

A.append(
    mcq(
        "paper-a-q03",
        "project-anatomy",
        "project-anatomy-s5",
        "exam",
        ["read-tool-output", "judgement"],
        """
You clone the group repository, make a commit and run `git push`. Git asks for a username and password. You check the remote:

```console
$ git remote -v
origin\thttps://github.com/esade-swdev-2026/gym-booking.git (fetch)
origin\thttps://github.com/esade-swdev-2026/gym-booking.git (push)
```

What should you do next?
""",
        [
            (
                "Switch the remote to SSH with `git remote set-url`, then run `ssh -T git@github.com`.",
                "Right. An `https://` remote makes git ask for a username and password. The course authenticates with an SSH key, so the remote has to start with `git@github.com:`.",
            ),
            (
                "Type your GitHub account password at the prompt and carry on with the push as usual.",
                "The course authenticates with an SSH key, not a password. The prompt appears only because the remote is an `https://` URL, so typing the password leaves the cause in place.",
            ),
            (
                "Run `ssh-keygen` again and upload the new public key to your GitHub account settings.",
                "The key is not what the transcript shows. An `https://` remote never uses an SSH key, so a new key changes nothing until the remote URL changes.",
            ),
            (
                "Delete the clone and clone it again from the Windows side, using Git for Windows this time.",
                "That is the line-endings entry of the troubleshooting table, a different problem. A new `https://` clone would ask for the same password again.",
            ),
        ],
        "a",
        """
A `git push` that asks for a username and password is the signature of an `https://` remote, and `git remote -v` shows it. Lab 00's troubleshooting table gives the fix: switch the remote to the SSH form with `git remote set-url origin git@github.com:...`, then run `ssh -T git@github.com` until GitHub greets you by name. Session 3 says you authenticate to GitHub with an SSH key, so a password prompt means git is not using the key at all. A second key or a second clone does not change the URL.
""",
        "S3 slide 5; labs/00-setup.md troubleshooting 3",
        "lab",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q04",
        "scrum",
        "scrum-s6",
        "exam",
        ["read-tool-output", "judgement"],
        """
It is Thursday, 11:00, and the Sprint Review is at 12:00. The habit-tracker group's item "As a user, I can see my average minutes per day, so that I know if I am keeping up" works for every week that has entries. CI is red at the Tests step of the last push (output trimmed):

```text
    def weekly_average(minutes_by_day: dict[str, int]) -> float:
>       return sum(minutes_by_day.values()) / len(minutes_by_day)
E       ZeroDivisionError: division by zero

src/habits/weekly.py:2: ZeroDivisionError
=========================== short test summary info ============================
FAILED tests/test_weekly.py::test_a_week_with_nothing_logged_averages_zero - ...
1 failed, 3 passed in 0.01s
```

The group's Definition of Done includes the green CI check. What should the team do?
""",
        [
            (
                "Show it as done at the Review: the empty week is rare, and every real user has already logged something.",
                "'Done except for ...' is not admissible. The green CI check is a line of the Definition of Done that the group does not waive for one item, and a brand-new user starts with an empty week.",
            ),
            (
                "Delete the empty-week test and push, so that CI is green again well before the Review starts at noon.",
                "Deleting the test removes the referee and keeps the bug: CI turns green and a new user still meets a `ZeroDivisionError`. The test is right; it found a real edge case.",
            ),
            (
                "Show it as 'done except for the empty week', and put that single case on the backlog for the next Sprint.",
                "This moves a missed standard into the backlog. The Definition of Done is applied to every item before it counts, not collected afterwards as a separate task.",
            ),
            (
                "Call it not done: make `weekly_average` return 0.0 for an empty week, push, and show it when CI is green.",
                "Right. An item that misses the Definition of Done is not done and does not ship. The repair is a guard clause of two lines, and the hour before the Review is enough for it.",
            ),
        ],
        "d",
        """
The course's Definition of Done is a green CI check, the same one for every group. A red Tests step means the increment is not done, however well the item works on a normal week. The failing test is not noise: a new user has an empty week, `len(...)` is zero and the first run would crash. Deleting the test hides the problem and keeps the crash, and "done except for ..." is not admissible (session 4, slide 10). The repair is small: a guard clause that returns 0.0 for an empty week, a push, and a wait for green before the item is shown at the Review.
""",
        "S4 slides 10, 16 and 17; S8 slide 11",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q05",
        "cli-program",
        "cli-program-s6",
        "exam",
        ["read-tool-output", "judgement"],
        """
The habit tracker's `log` command, and two runs of it:

```python
@app.command()
def log(habit: str, minutes: int = 30) -> None:
    if minutes <= 0:
        typer.echo("minutes must be positive", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Logged {habit}: {minutes} min")
```

```console
$ uv run habits log
Usage: habits log [OPTIONS] {habit}
Try 'habits log --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Missing argument 'habit'.                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
$ echo $?
2
$ uv run habits log Run --minutes 0
minutes must be positive
$ echo $?
1
```

What can you conclude?
""",
        [
            (
                "Both messages come from the `if` in `log`, which picks code 2 for a missing value and code 1 for a wrong one.",
                "The function never ran for the first command, and it has no `if` for a missing `habit`. typer built that check from the signature, where `habit` has no default.",
            ),
            (
                "Exit code 2 means the program crashed with a Python error, and exit code 1 means a normal, expected failure.",
                "Both are ordinary failures. A program that stops on an uncaught Python exception also exits 1, and the number only says 'not success', never why.",
            ),
            (
                "typer refused the first command before `log` ran; the second got into `log`, whose own check exited with 1.",
                "Right. `habit` has no default, so typer makes it a required argument and refuses the command line itself. `--minutes 0` is a valid `int`, so it reaches the function, and `raise typer.Exit(code=1)` ends it.",
            ),
            (
                "The first command should also exit with 1, because an exit code of 2 shows that typer is badly set up.",
                "Any non-zero code means failure, and the shell, `&&` and CI read only that. typer uses 2 for a command line it refuses, and nothing is misconfigured.",
            ),
        ],
        "c",
        """
Session 5 says the type hints are the specification. From `log(habit: str, minutes: int = 30)` typer builds the usage line, makes `habit` a required argument and `--minutes` an option, and checks the command line before your function runs. A missing `habit` is refused there, with typer's own message and its exit code 2. The value `0` is a perfectly good `int`, so it reaches `log`, where the group's own check prints to stderr and ends with `raise typer.Exit(code=1)`. Both runs end non-zero, which is what the shell, `&&` and CI read: 0 means success and anything else means failure.
""",
        "S5 slides 7 to 9",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q06",
        "clean-code",
        "clean-code-s7",
        "exam",
        ["read-code", "judgement"],
        """
In the parking-lot group a ticket is a tuple `(plate, entry_minute, exit_minute)`, and `minutes_parked` reads it by position:

```python
def minutes_parked(ticket):
    return ticket[2] - ticket[1]
```

A teammate adds the parking level to every ticket as its second item, a number, giving `("1234ABC", 3, 540, 600)`, and does not touch `minutes_parked`. Called with the new ticket it returns 537 for a car that stayed 60 minutes, and no tool reports anything. Which clean-code problem does this describe best?
""",
        [
            (
                "A tuple stands in for a type: the function reads fields by position, so a new item shifts them without a warning.",
                "Right: `ticket[2]` is now the entry minute and `ticket[1]` the level, so it returns 537 where 60 is expected. Nothing fails, so nobody is warned.",
            ),
            (
                "The function does several jobs at once: it reads the ticket and does the arithmetic, so it is hard to test and to change.",
                "It does one job: it subtracts two minutes. The failure comes from how the ticket is represented, not from how much the function does.",
            ),
            (
                "The function name `minutes_parked` is too vague to say what it returns, so callers have to read the code.",
                "The name says exactly what comes back, minutes parked. A better name would not stop the silent shift when a field is inserted.",
            ),
            (
                "The function repeats the same subtraction in several places, so a change to the ticket has to be made more than once.",
                "There is one subtraction in one place. Duplication is a real problem, but not one this function has.",
            ),
        ],
        "a",
        """
Reading `ticket[2] - ticket[1]` needs a table in someone's head: which position is which field. When a field is inserted, every index after it shifts, and the function keeps running. Here it returns 540 - 3 = 537 minutes with no error, which is the worst kind of failure because it is silent. This is session 6's "a tuple is a missing type". With a `@dataclass(frozen=True)` the code reads `ticket.exit_minute - ticket.entry_minute`: the names do not move when a field is added, and a misspelt field is an error rather than a wrong answer. Real run: the old ticket gives 60, the new one 537.
""",
        "S6 slides 21 to 24",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q07",
        "core-shell-failing",
        "core-shell-failing-s7",
        "exam",
        ["read-code", "read-tool-output", "judgement"],
        """
The habit-tracker group's `average` command reads a file with one number of minutes per line. CI is green, and so is `mypy --strict`. Then a user's file has a stray word in it:

```python
def parse_minutes(text: str) -> int:
    return int(text)


def weekly_average(minutes: list[int]) -> float:
    if not minutes:
        return 0.0
    return sum(minutes) / len(minutes)
```

```python
@app.command()
def average(path: str) -> None:
    lines = Path(path).read_text().split()
    minutes = [parse_minutes(line) for line in lines]
    typer.echo(f"Average: {weekly_average(minutes):.1f} min")
```

```console
$ uv run mypy --strict src
Success: no issues found in 3 source files
$ cat week.txt
30
45
rest
60
$ uv run habits average week.txt
(traceback frames trimmed)
ValueError: invalid literal for int() with base 10: 'rest'
$ echo $?
1
```

What does this show, and what is the right next step?
""",
        [
            (
                "`--strict` missed this line, so the group needs a stricter type checker in CI before the next release.",
                "No type checker can read the file. mypy compares the types written in the code, and `parse_minutes(text: str) -> int` is a correct signature.",
            ),
            (
                "The user's file is at fault, so no change is needed: a program may assume that its input is well formed.",
                "Bad input is the normal case at the edge of a program. The course asks the shell to expect it and to fail loudly with a message, not with a raw traceback.",
            ),
            (
                "`parse_minutes` should catch the `ValueError` and return `-1`, so that the average can still be printed.",
                "Slide 17 says not to return `-1` and hope somebody checks. A `-1` would flow into the average and give a wrong number with no error at all.",
            ),
            (
                "mypy checks types, not file contents: the shell should catch `ValueError`, use stderr and exit non-zero.",
                "Right. A bad value in a file only shows up at run time, at the boundary. The shell is the layer that catches the expected exceptions and turns them into a message and an exit code.",
            ),
        ],
        "d",
        """
mypy compares the types written in the code. Every hint here is correct, and mypy cannot know that a file will one day contain the word `rest`. Session 7 draws the line: the checker finds what can be known before the program runs, such as the `None` that is not handled, and the shell deals with what only appears at run time. A bad line in a file is an expected failure at the boundary, so the shell catches `ValueError`, prints a message such as `week.txt has a line that is not a number` to stderr and raises `typer.Exit(code=1)`. A raw traceback gives the user nothing to act on, and returning `-1` would put a fake number into the average.
""",
        "S7 slides 8, 17 and 19",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q08",
        "testing-tdd",
        "testing-tdd-s9",
        "exam",
        ["read-tool-output", "judgement"],
        """
The gym-booking group keeps `classes.csv` in the project root, and this test reads it. Marc runs `uv run pytest` from the project root and it passes. Ines runs the same command from inside `tests/`:

```python
def test_yoga_has_four_bookings() -> None:
    bookings = read_bookings("classes.csv")
    assert len(bookings["yoga"]) == 4
```

```console
$ pwd
/home/ines/code/gym-booking/tests
$ uv run pytest -q
F                                                                        [100%]
...
E       FileNotFoundError: [Errno 2] No such file or directory: 'classes.csv'

../src/gym_booking/bookings.py:6: FileNotFoundError
=========================== short test summary info ============================
FAILED test_bookings.py::test_yoga_has_four_bookings - FileNotFoundError: [Er...
1 failed in 0.01s
```

Which change follows session 8's advice and removes the problem for good?
""",
        [
            (
                "Open the file by its absolute path, `/home/ines/code/gym-booking/classes.csv`, so that every folder works.",
                "That path exists on Ines's laptop only. It fixes the folder problem here and breaks the test on Marc's laptop and in CI, where the clone lives somewhere else.",
            ),
            (
                "Give the test its own data: a plain list for a pure function, or a tiny file written into `tmp_path`.",
                "Right. A test that carries its own data does not care which folder it runs from or which files lie around. Session 8 calls the failure 'tests that need your laptop', and this is the same family.",
            ),
            (
                "Add a line to the README saying that `pytest` must always be started from the project root.",
                "A note does not change the test. It still fails for anyone who forgets, and it still needs a file in one particular place.",
            ),
            (
                "Copy `classes.csv` into `tests/` as well, so that both folders hold a copy of the file.",
                "Two copies drift apart, and the test still depends on a file nobody checks and on the folder where pytest starts. The dependency is hidden, not removed.",
            ),
        ],
        "b",
        """
The test opens `classes.csv` by a relative path, and a relative path starts from the folder you are standing in (session 9). From the project root the file is there; from `tests/` it is not, which is why the traceback names the bare file. It is the same family as session 8's third 'one that bites', tests that need your laptop: the test needs a file in a particular place. The cure is to give the test its own data, either a plain list passed to a pure function or a small file written into `tmp_path`, which pytest creates fresh and deletes afterwards. An absolute path, a README note and a second copy all keep the dependency and only move the failure somewhere else.
""",
        "S8 slides 23 and 28; S9 slides 10 and 11",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q09",
        "refactor-types",
        "refactor-types-s9",
        "exam",
        ["read-tool-output", "judgement"],
        """
The parking-lot group adds a surcharge to its hourly rates. Strict mypy is part of CI:

```python
RATES = {"car": 2.50, "van": 4.00}


def find_rate(vehicle: str) -> float | None:
    return RATES.get(vehicle)


def price_with_surcharge(vehicle: str) -> float:
    return find_rate(vehicle) + 1.00
```

```console
$ uv run mypy --strict src
src/parking/rates.py:9: error: Unsupported operand types for + ("None" and "float")  [operator]
src/parking/rates.py:9: note: Left operand is of type "float | None"
Found 1 error in 1 file (checked 1 source file)
```

Which fix is most appropriate?
""",
        [
            (
                "Add `# type: ignore[operator]` to the line, because every vehicle the program sees is in `RATES`, so `None` cannot happen",
                "Nothing in the code or in a test says so: `price_with_surcharge(\"boat\")` would raise a `TypeError`. A comment is a claim, not a check.",
            ),
            (
                "Check for `None` before adding, and decide what an unknown vehicle should do, for example raise `ValueError`",
                "Right: `find_rate` can return `None`, so the caller must decide what that means. A clear error beats a crash with a confusing message.",
            ),
            (
                "Change the return type of `price_with_surcharge` to `float | None`, so that mypy accepts the line",
                "We ran it: mypy reports the same error. The addition on `None` is the problem, not the declared type of the result.",
            ),
            (
                "Make `find_rate` return `RATES.get(vehicle, 0)`, so that an unknown vehicle costs nothing and the line is quiet",
                "mypy is quiet, but a boat is now priced at 1.00 EUR with no warning (we ran it). A made-up default hides the missing case instead of deciding it.",
            ),
        ],
        "b",
        """
Session 7's three kinds: this is None not handled. `find_rate` is honest about its result, `float | None`, and the caller adds a number to it without looking. mypy reports it under `operator` and the note `Left operand is of type "float | None"` says what is missing. The fix is to deal with the `None` where it arrives: check it, and choose what an unknown vehicle means (here an error). Silencing it with `# type: ignore`, changing the result type, or inventing a default would each make the line quiet and leave the case undecided. Real run on all four versions.
""",
        "S7 slides 8 to 10; labs/07-refactor.md troubleshooting",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q10",
        "terminal-files",
        "terminal-files-s7",
        "exam",
        ["read-tool-output"],
        """
Ines lists her project folder:

```console
$ ls -l
-rw-r--r-- 1 ines ines  412 Oct 12 09:14 README.md
-rwxr-x--- 1 ines ines  186 Oct 12 09:14 check.sh
drwxr-xr-x 2 ines ines 4096 Oct 12 09:14 data
-rw------- 1 ines ines  399 Oct 12 09:14 deploy_key
```

Marc has an account on the same computer. He is not `ines` and not in her group. Which of these can he do?
""",
        [
            (
                "Read `README.md`.",
                "Right: the last three characters, the permissions for everyone else, are `r--`, so anyone with an account can read it but not change it.",
            ),
            (
                "Run `./check.sh`.",
                "For everyone else `check.sh` has `---`: no read and no execute. Only the owner and the group have `x`.",
            ),
            (
                "Read `deploy_key`.",
                "`-rw-------` is mode 600: only the owner can read or write it. That is exactly why it fits a private key.",
            ),
            (
                "Create a new file inside `data`.",
                "For everyone else `data` has `r-x`: he can list the folder and enter it, but creating a file needs `w`, which only Ines has.",
            ),
        ],
        "a",
        """
Read each line in four parts: the type, then three triplets for the owner, the group and everyone else. Marc is in the last triplet for every file. `README.md` ends in `r--`, so he can read it. `check.sh` ends in `---`, so he can neither read nor run it. `deploy_key` ends in `---`, the 600 pattern that keeps a private key private. `data` is a folder, and `r-x` lets him look and enter but not create or delete anything, because that needs `w`.
""",
        "S9 slide 17",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q11",
        "pipes-bash",
        "pipes-bash-s5",
        "hard",
        ["predict-output", "read-code"],
        """
The library group keeps its loans in `loans.csv`:

```text
member,book,days_late
ana,Dune,0
marc,Emma,3
joan,Ulysses,0
marc,Dune,0
ana,Persuasion,2
lia,Emma,0
marc,Ulysses,5
joan,Persuasion,0
ana,Ulysses,0
marc,Persuasion,1
joan,Emma,4
lia,Dune,0
```

What does this command print? (`cut -d, -f1` keeps the first column, `uniq -c` puts the count in front of each line, `sort -rn` sorts by number, largest first, and `head -n 1` keeps the first line. Ignore the spaces.)

```bash
cut -d, -f1 loans.csv | sort | uniq -c | sort -rn | head -n 1
```
""",
        [
            (
                "`marc`",
                "The names are right but `uniq -c` adds a count in front of each one, and `head -n 1` keeps the whole first line, count included.",
            ),
            (
                "`3 ana`",
                "That is the first line after `uniq -c`, in alphabetical order. The second `sort -rn` then puts the largest count first, so `3 ana` is not first.",
            ),
            (
                "`1 member`",
                "The header word is a line like any other and counts once. It would come first only with an ascending sort, `sort -n`. `-rn` puts the largest count first.",
            ),
            (
                "`4 marc`",
                "Right: `cut` takes the name column, `sort` puts equal names together, `uniq -c` counts each group, `sort -rn` puts the largest count first and `head -n 1` keeps that line.",
            ),
        ],
        "d",
        """
Read it stage by stage. `cut -d, -f1` keeps the first column, header word included. `sort` puts identical names next to each other, which `uniq` needs. `uniq -c` collapses each run into one line with its count: 3 ana, 3 joan, 2 lia, 4 marc, 1 member. `sort -rn` sorts numerically, largest first, so 4 marc comes to the top, and `head -n 1` keeps only that line. The header counts once and sorts to the bottom, so it does no harm here.
""",
        "S10 slides 6–7; S9 slide 6 and take-aways",
        "slides",
        "run",
    )
)

A.append(
    mcq(
        "paper-a-q12",
        "pipes-bash",
        "pipes-bash-s7",
        "beyond",
        ["read-tool-output", "judgement"],
        """
The gym-booking group's `scripts/check.sh` is run by CI. A teammate trimmed pytest's output with `tail` to keep the log short. One test fails, and CI is green:

```bash
#!/usr/bin/env bash
set -e
uv run ruff check .
uv run mypy src tests
uv run pytest -q | tail -n 2
```

```console
$ ./scripts/check.sh
All checks passed!
Success: no issues found in 3 source files
FAILED tests/test_rules.py::test_exactly_two_hours_before_refunds_in_full - a...
1 failed, 2 passed in 0.01s
$ echo $?
0
```

Why did the script exit with 0? (`set -e` makes a script stop at the first command that exits non-zero.)
""",
        [
            (
                "`set -e` stops the script only at `uv run mypy`, so any failure of `ruff` or `pytest` is ignored.",
                "`set -e` stops the script at any command that exits non-zero. The trouble is that the failing `pytest` is not a command on its own line here.",
            ),
            (
                "`pytest | tail` is a pipeline, and its exit status is that of the last command, so `tail`'s 0 hid it.",
                "Right: without `pipefail`, the status of the pipeline is the status of `tail`, which succeeded. `set -e` therefore sees a success and the script carries on.",
            ),
            (
                "`pytest -q` is quiet mode, which reports failures on the screen but always exits with the code 0.",
                "Quiet mode only shortens the output. Run alone, `pytest` exits non-zero when a test fails, which is how CI normally goes red.",
            ),
            (
                "`uv run` swallows the exit code of the tool it starts, so a failing test can never turn the CI step red.",
                "`uv run` passes the exit code of the program through. If it did not, no CI step in the course could ever fail.",
            ),
        ],
        "b",
        """
An exit code can be lost inside a pipeline. By default a pipeline's exit status is that of its last command, here `tail`, which happily printed two lines and exited 0. `set -e` looks at that single status, so the script goes on and ends with 0, and CI trusts the number. The same happens with `grep ... | wc -l`. The fix is `set -o pipefail`, which makes the pipeline fail if any stage fails, as in `set -euo pipefail`; or do not pipe pytest at all. The screen shows the failure, but only the exit code counts.
""",
        "S10 slide 16 (pipefail); S5 slide 9; S9 take-aways",
        "slides",
        "run",
    )
)

# --- open questions of Paper A -------------------------------------------------------------

A.append(
    open_q(
        "paper-a-q13",
        "refactor-types",
        "refactor-types-s3",
        "exam",
        ["read-code", "judgement"],
        """
**Read code and say what is wrong.** A teammate's function for the group's flashcard trainer. `cards.csv` sits next to the program, with one card per line: the question and its box (1, 2 or 3).

```text
capital of Peru,1
ser vs estar,2
stem of 'tener',3
two plus two,2
```

```python
def due_cards(day):
    f = open("cards.csv")
    out = []
    for line in f:
        p = line.strip().split(",")
        # box 1 every day, box 2 every third day, box 3 every seventh day
        if int(p[1]) == 1 or (int(p[1]) == 2 and day % 3 == 0) or (int(p[1]) == 3 and day % 7 == 0):
            out.append(p[0])
    return out
```

Two calls in a Python session:

```console
>>> due_cards(6)
['capital of Peru', 'ser vs estar', 'two plus two']
>>> due_cards(7)
['capital of Peru', "stem of 'tener'"]
```
""",
        [
            part(
                "1",
                "In one sentence, what does this function do?",
                1,
                "It reads `cards.csv` and returns the questions that are due on a given day: box 1 every day, box 2 every third day and box 3 every seventh day.",
                [
                    "Says it reads the cards file and returns the questions that are due on that day",
                    "Says the rule: the box decides how often a card is due (box 1 daily, box 2 every third day, box 3 every seventh day)",
                ],
                "'It returns cards' or 'it filters the list' leaves out the file and the day. 'It returns the cards in box 1' describes one branch of the condition. Saying it prints the cards is wrong: it returns a list, and the console shows the value of each call.",
            ),
            part(
                "2",
                "Name two problems a teammate would face when reading, testing or changing it.",
                2,
                "It opens a fixed file inside the function, so a test needs that file in the right folder instead of a plain list. The schedule is one long condition of unexplained numbers, written with `p[1]` and cryptic names, so changing it means decoding the line first.",
                [
                    "Opens `cards.csv` inside the function (reading mixed with the decision), so a test needs the file in the right folder and the function cannot be reused with other data",
                    "One long condition with unexplained numbers (1, 2, 3, 7), so the rule is hard to read and to change and is explained only by a comment",
                    "The position `p[1]` and the names `f`, `p`, `out` make a reader guess what each one means",
                    "Accept one of these only when tied to a consequence: the comment says what the code does instead of the code saying it; the file is never closed (ruff flags it); there are no type hints (`mypy --strict` flags the function)",
                ],
                "'It is long' or 'it is hard to read' with no cause scores nothing. 'It needs more comments' is the wrong lesson: the one comment here exists because the numbers have no names. 'The file name is hard-coded' earns a mark only with its consequence: a test then needs that file in that folder.",
            ),
            part(
                "3",
                "Describe in words how you would change it, and which of your two problems each change solves.",
                2,
                "Read the file in the shell and pass the cards in, so the function is testable with a plain list. Name the condition (`is_due`) and the intervals as constants, and give the card a dataclass, so `p[1]` becomes `card.box`.",
                [
                    "Moves the file reading out to the shell and passes the data in (core and shell), and says this makes the function testable with a list",
                    "Names the condition (a function such as `is_due`) and/or the numbers (constants), and says this makes the rule readable and easy to change",
                    "Gives the card a named type or names for its fields, tied to the guesswork about positions",
                ],
                "'Refactor it into smaller functions' without saying which jobs or why is too vague. Replacing the comment with a longer comment removes no problem. Changing the file name or the folder does not help testing: the function would still open a file.",
            ),
        ],
        """
This is the shape of sample question 7 on a function with a different mix of problems from the samples: the data comes from a file opened inside the function, and the rule is a long condition of numbers that only a comment explains. A full-marks answer names two problems with their cost for a teammate (cannot test without the file, cannot read or change the schedule, cannot tell what `p[1]` is) and pairs each change with the problem it solves: read in the shell and pass the data in, name the condition and the numbers, give the card a type. Run with the course's tools, `ruff` flags the unclosed file and `mypy --strict` the missing annotation.
""",
        "S6 slide 16; S7 slides 5, 6 and 13",
        "slides",
        "run",
    )
)

A.append(
    open_q(
        "paper-a-q14",
        "history",
        "history-s8",
        "exam",
        ["read-diff", "compare", "judgement"],
        """
**Compare.** A teammate shows you this diff from the parking-lot group's history:

```diff
--- a/fees.py
+++ b/fees.py
@@ -1,2 +1,8 @@
+FREE_MINUTES = 15
+HOURLY_RATE = 2.5
+
+
 def fee(minutes):
-    return 2.5 * (minutes // 60 + 1)
+    if minutes <= FREE_MINUTES:
+        return 0.0
+    return HOURLY_RATE * (minutes // 60 + 1)
```

Two candidate commit messages:

- A: `Add FREE_MINUTES and HOURLY_RATE to fees.py`
- B: `Charge nothing for stays of up to 15 minutes`
""",
        [
            part(
                "1",
                "What does this change do?",
                2,
                "It names the two numbers as constants, which changes nothing, and adds a rule: a stay of 15 minutes or less now costs 0.0 instead of 2.5. Longer stays are charged as before.",
                [
                    "Says the numbers 15 and 2.5 become named constants",
                    "Says the behaviour changes: stays up to 15 minutes become free (they used to cost 2.5)",
                    "Says longer stays are charged as before",
                ],
                "Describing only the constants misses the behaviour change, which is the part that matters. Saying the function 'now has an if' restates the diff without saying what a driver sees. Saying everything is cheaper is wrong: only stays of 15 minutes or less change.",
            ),
            part(
                "2",
                "Which message is better, and why? Answer from the point of view of someone reading the history six months later.",
                2,
                "B. It says what the program now does for a driver, so someone searching later for why short stays became free finds it. A mentions only the constants and hides the new rule; two separate commits would be best.",
                [
                    "Chooses B",
                    "Gives the reason: B states the behaviour change for the user, while A describes only the constants and would mislead a reader looking for the pricing change; or notes that the diff mixes a refactoring with a behaviour change and should be two commits",
                ],
                "Choosing A because it is 'more technical' or 'matches the diff' misses the reader. A message that repeats what the diff already shows adds nothing six months later. 'B is shorter' is not a reason. A right choice with no reason earns one mark.",
            ),
            part(
                "3",
                "Name one test you would add for this change, in words.",
                1,
                "A stay of exactly 15 minutes costs nothing, and 16 minutes costs 2.5: the boundary of the new rule.",
                [
                    "Names the boundary (exactly 15 minutes, or 15 against 16) and states the expected fee",
                    "Or names another clear case with its expected result, such as 0 minutes costing 0.0",
                ],
                "'Test the fee function' names no input and no expected result. A test with a typical stay, such as 90 minutes, does not exercise the new rule. Remember that the edge case is the point: 'do not test what feels likely, test what could break'.",
            ),
        ],
        """
This is sample question 8 on a new diff. The commit does two things: it extracts constants, a refactoring, and it adds a rule, a behaviour change. A message that names only the constants hides the part a reader needs. Running the old and the new `fee` shows that 10 and 15 minutes change from 2.5 to 0.0, while 16, 59, 60, 75 and 120 minutes give the same fee as before. The natural test sits on that edge.
""",
        "S6 slide 16; S7 slide 5; commit-message practice from the history",
        "history",
        "run",
    )
)

A.append(
    open_q(
        "paper-a-q15",
        "refactor-types",
        "refactor-types-s9",
        "hard",
        ["read-tool-output", "judgement"],
        """
**Read tool output.** CI is red at the Types step of the library group's repository. You run `uv run mypy --strict src` on the branch:

```text
src/library/fines.py:15: error: Unsupported left operand type for - ("None")  [operator]
src/library/fines.py:15: note: Left operand is of type "date | None"
src/library/fines.py:26: error: Incompatible return value type (got "float", expected "int")  [return-value]
src/library/fines.py:29: error: Function is missing a type annotation for one or more parameters  [no-untyped-def]
src/library/fines.py:33: error: Function is missing a return type annotation  [no-untyped-def]
Found 4 errors in 1 file (checked 2 source files)
```

Line 15 is in `days_late(loan)`, which subtracts the due date from `loan.returned`. A loan's `returned` stays empty until the member brings the book back. Line 26 is in `total_fines`, which adds up fines such as 0.60 and 1.20.
""",
        [
            part(
                "1",
                "Sort the four errors into the kinds we discussed in session 7.",
                2,
                "Line 15 is None not handled (`returned` can be `None`). Line 26 is types disagree (an `int` promised, a `float` returned). Lines 29 and 33 are missing annotation.",
                [
                    "Line 15 sorted as None not handled and line 26 as types disagree",
                    "Lines 29 and 33 both sorted as missing annotation",
                ],
                "Copying the codes (`operator`, `return-value`) without naming the kinds does not answer the question. Calling line 15 'types disagree' because the message says 'unsupported operand type' misses the clue in the note: `date | None` means a value can be missing. Putting all four under 'types are wrong' loses both marks.",
            ),
            part(
                "2",
                "Which error points to a bug that can crash the program for a real user, and when?",
                1,
                "Line 15. An unreturned book has `returned` equal to `None`, and subtracting from `None` raises a `TypeError`, so asking for its fine stops the program. The other errors crash nothing by themselves.",
                [
                    "Picks line 15 (the None one)",
                    "Explains the mechanism: an unreturned book has `returned = None` and the subtraction raises `TypeError` at run time",
                ],
                "Choosing line 26 because the numbers 'disagree' or line 29 or 33 because 'missing' sounds serious: neither crashes. Picking line 15 with no mechanism earns half; say when the value is `None` and what happens next.",
            ),
            part(
                "3",
                "A teammate says: \"CI only has to go green. Fix the two missing hints properly and put `# type: ignore` on lines 15 and 26.\" Do you accept? Give your reasoning.",
                2,
                "No. The two ignores sit on the errors that matter. Line 15 hides the crash for an unreturned book and line 26 hides a return type that does not match, so CI turns green while the program still raises a `TypeError` for the first unreturned book. I would handle the `None` and declare the return type as `float`.",
                [
                    "Says no, because the ignore on line 15 hides the real crash (an unreturned book has `returned` equal to `None`), so CI goes green while the program still fails for a user",
                    "Says what to do instead (handle the `None` by checking it or changing the type, and make the return type agree with `float`), or that CI is the shared referee and a forced green defeats it",
                ],
                "'Yes, the hints are fixed and CI is green' judges by the tick, which is the trap. 'No, ignores are bad practice' is a verdict without the reason. The marker wants the reason: the ignores sit on the two errors that describe real behaviour, so the first unreturned book still raises a `TypeError`, and the `float` that comes back still disagrees with the `int` that was promised.",
            ),
        ],
        """
This is sample question 9 with a noisier log. The three kinds are the same: missing annotation, types disagree and None not handled. The twist is that the None error does not say `union-attr`: it says `operator`, and only the note `date | None` shows what is missing, so you have to read the message rather than recognise a code. Only that error crashes a real user, and an ignore on lines 15 and 26 would turn CI green while the crash stays: the same shortcut as `# type: ignore` in sample question 9, applied to the errors that matter.
""",
        "S7 slides 8 to 11",
        "slides",
        "run",
    )
)

PAPER_A = {
    "id": "paper-a",
    "title": "Paper A",
    "kind": "realistic",
    "minutes": 60,
    "intro_md": (
        "This paper is built to look like the teacher's: twelve multiple-choice questions, then three short open questions, "
        "at the difficulty of his nine samples. Sit it in 60 minutes with a pen, no notes and no devices. Give each multiple-choice "
        "question about 90 seconds and each open question about 8 minutes, and answer the open questions in 5–8 lines of prose, "
        "because you never write code. Marks: 1 for each multiple-choice question and 5 for each open question, 27 in all. "
        "Mark yourself with the model answers, and follow the Revise link on every question you miss."
    ),
    "questions": A,
}

# ---------------------------------------------------------------------------------------------
# PAPER B
# ---------------------------------------------------------------------------------------------

B: list[dict[str, Any]] = []

B.append(
    mcq(
        "paper-b-q01",
        "clean-code",
        "clean-code-s5",
        "exam",
        ["concept", "judgement"],
        """
A function called `summary(path)` in the gradebook group opens `marks.csv`, drops every row with a missing mark, adds up the marks per student and prints the table. Which clean-code problem does this describe best?
""",
        [
            (
                "A magic number: the widths and limits in the table are written as bare numbers and need names in one place",
                "The description mentions no numbers at all. Magic numbers are a real problem (session 6) but not what this describes.",
            ),
            (
                "Duplicated logic: the code that totals one student is copied for every other student in the table, line by line",
                "Nothing in the description is repeated: the marks are added up per student by one piece of code.",
            ),
            (
                "It does several jobs at once: it reads, filters, totals and prints, so it is hard to test and to change",
                "Right: four jobs. To test the totals you need a real file and a way to capture the printed table, and changing the layout means touching the calculation.",
            ),
            (
                "The signature has too many type hints, which makes the function hard to read at a glance for a new teammate",
                "Type hints are contracts that mypy and teammates read; there is no such thing as too many. The description says nothing about hints.",
            ),
        ],
        "c",
        """
Session 6's test: can you describe the function without the word "and"? This one opens a file and drops rows and adds up the marks and prints the table: the Single Responsibility Principle broken four times. What a teammate feels is that the totals cannot be tested without a file on disk and captured output, and that any change to one job risks the others. The course's fix is the demo's own path: reading (`read_expenses`), computing (`total_by_category`) and printing (`format_report`) each get their own function, and only the shell prints.
""",
        "S6 slides 18 and 20; sample Q5 shape",
        "slides",
        "source",
    )
)

B.append(
    mcq(
        "paper-b-q02",
        "sdlc-agile",
        "sdlc-agile-s7",
        "exam",
        ["concept", "judgement"],
        """
The Agile Manifesto ends its four values with this sentence: "While there is value in the items on the right, we value the items on the left more." After its first demo, the student-club website group makes four decisions. Which one misreads the Manifesto?
""",
        [
            (
                "The team stops writing any plan, because the Manifesto says that responding to change replaces following a plan.",
                "Right: this turns 'values more' into 'replaces'. The Manifesto ranks a plan below responding to change; it does not abolish it, and every Agile cycle still starts with Plan.",
            ),
            (
                "The team signs a contract with the client and still shows a working version every two weeks to hear what should change.",
                "A correct reading. The contract still has value, and customer collaboration is ranked above negotiating it.",
            ),
            (
                "The team keeps a one-page README and a short plan for the next sprint, and ranks both below a working demo.",
                "A correct reading. Documentation and plans are the right-hand items: kept, and ranked lower than working software and change.",
            ),
            (
                "The team uses a board with a limit on work in progress, and changes its columns when the people doing the work ask.",
                "A correct reading. A board is a tool, valued less than the individuals who use it, and not thrown away.",
            ),
        ],
        "a",
        """
The last sentence of the Manifesto is the one people skip. It ranks the two sides of each pair; it does not delete the right-hand side. The group that stops planning has read "over" as "instead of", which is one of the two classic misreadings, together with "no documentation". The other three decisions keep the right-hand item and rank it lower: a contract next to regular demos, a short README and plan below working software, and a board that the people who use it may change. Session 2 adds that every Agile cycle still starts with Plan, on a small slice, so a team that never plans is not running a cycle at all.
""",
        "S2 slides 10 and 11",
        "slides",
        "source",
    )
)

B.append(
    mcq(
        "paper-b-q03",
        "project-anatomy",
        "project-anatomy-s4",
        "exam",
        ["read-tool-output", "judgement"],
        """
Ana follows the setup lab: she makes her own branch, adds her report, commits, and types `git push`.

```console
$ git switch -c setup/ana
Switched to a new branch 'setup/ana'
$ git add setup-reports/
$ git commit -m "add setup report"
[setup/ana 9acfe08] add setup report
 1 file changed, 1 insertion(+)
 create mode 100644 setup-reports/ana.md
$ git push
fatal: The current branch setup/ana has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin setup/ana

To have this happen automatically for branches without a tracking
upstream, see 'push.autoSetupRemote' in 'git help config'.
```

What should Ana do?
""",
        [
            (
                "Delete the branch and push from `main`, because `main` already knows where to push.",
                "`main` is exactly where the lab says not to push: four students pushing in the same twenty minutes collide, and the second push is rejected. The branch is right; it just does not know its remote yet.",
            ),
            (
                "Run `git push --force`, so that git stops asking where the branch should go.",
                "Nothing has been rejected, so there is nothing to force. Force overwrites what is on the remote, and it does not give git a destination.",
            ),
            (
                "Run the command git printed, `git push --set-upstream origin setup/ana`, and push again.",
                "Right. A branch made with `switch -c` exists only on her laptop. The first push has to say where it goes, and `-u` (short for `--set-upstream`) remembers it. Git printed the exact command.",
            ),
            (
                "Clone the repository again and redo the report, because a branch with no upstream is broken.",
                "The branch is fine. 'No upstream' only means that it has never been pushed. A new clone and a new `switch -c` would end in the same message.",
            ),
        ],
        "c",
        """
`git switch -c` creates the branch on Ana's laptop only. A plain `git push` asks git where the branch should go, and git has no answer yet, hence 'no upstream branch'. The message prints the fix, and it is the command the setup lab gives: `git push -u origin setup/<your-github-username>`, where `-u` is short for `--set-upstream`. After that first push, a plain `git push` works on this branch. Pushing to `main` instead is what the lab avoids, `--force` answers a rejection and nothing was rejected, and a fresh clone fixes nothing, because the branch was never broken. Read the message before trying anything else: git printed the exact command it needs.
""",
        "S3 slides 10, 11 and 13; labs/00-setup.md (branch and push)",
        "lab",
        "run",
    )
)

B.append(
    mcq(
        "paper-b-q04",
        "scrum",
        "scrum-s5",
        "core",
        ["concept", "judgement"],
        """
The gym-booking group orders its Product Backlog. Which item is written the way the course asks: an outcome a user gets, small enough to finish in a sitting, where you can tell when it is done?
""",
        [
            (
                "Create the `bookings` table and write the code that reads and writes its rows in the database",
                "A task, not an outcome. Nobody can tell when it is done, and a user gets nothing from it on its own.",
            ),
            (
                "As a member, I can cancel a booking up to two hours before class, so that I do not pay for it",
                "Right: it names who, what they can do and the benefit, it is small, and you can check it by running the program.",
            ),
            (
                "Clean up the booking code so that it becomes fast, tidy and easy to read for everyone on the team",
                "Not checkable: 'fast' and 'easy' have no yes or no answer. Quality belongs in the Definition of Done, as things you can check.",
            ),
            (
                "Write unit tests for the booking functions and for the cancellation functions of the app",
                "Every item is tested, so this is a standard, not a backlog entry. 'Write tests' belongs in the Definition of Done.",
            ),
        ],
        "b",
        """
The backlog brief defines an item as an outcome a user gets, not a task you perform, small enough to finish in a sitting, where you can tell when it is done. Its shape is "As a ..., I can ..., so that ...", and the "so that" names the benefit, which stops the team building something nobody needs. The cancel item has all of that. The table is a task, "fast and easy to read" cannot be checked, and "write tests" is part of what done means for every item, so it sits in the Definition of Done.
""",
        "S4 slides 29 and 30; backlog brief",
        "slides",
        "source",
    )
)

B.append(
    mcq(
        "paper-b-q05",
        "terminal-files",
        "terminal-files-s4",
        "exam",
        ["read-tool-output", "judgement"],
        """
On a new laptop you clone the group repository and try to install it:

```console
$ cd ~/code
$ git clone git@github.com:esade-swdev-2026/gym-booking.git
$ uv sync
error: No `pyproject.toml` found in current directory or any parent directory
```

What should you do next?
""",
        [
            (
                "Run `uv init` to create the missing `pyproject.toml` in the current folder, then run `uv sync`.",
                "`uv init` would start a new, empty project in the wrong folder. The group's project already has its `pyproject.toml`, in the folder you did not enter.",
            ),
            (
                "Run `uv lock` first to create the lockfile, and `uv sync` will then find the project.",
                "A lockfile is built from `pyproject.toml`, so `uv lock` needs the project file just as `uv sync` does and stops with the same error in this folder.",
            ),
            (
                "Run `git pull` to fetch the `pyproject.toml` that the clone seems to be missing.",
                "The clone is complete: `git clone` already brought every file, into the new `gym-booking` folder. `~/code` itself is not the repository, so `git pull` would fail there too.",
            ),
            (
                "Run `pwd` and `ls`, see that you are above the clone, then `cd gym-booking` and run `uv sync`.",
                "Right. The clone created a folder, and `pyproject.toml` lives inside it. Most 'not found' errors are the wrong current directory, so run `pwd` first.",
            ),
        ],
        "d",
        """
uv looks for `pyproject.toml` in the folder you stand in and then in its parents. After `git clone` you are still in `~/code`, one level above the new `gym-booking` folder, so uv finds nothing. Session 9 gives the habit: most "file not found" errors are the wrong current directory, so run `pwd` before you suspect anything else. Then `cd gym-booking` and repeat the command. Creating a new project, building a lockfile first or pulling again treats a navigation slip as a tool problem.
""",
        "S4 slides 20 to 23; S9 slides 10 and 11",
        "slides",
        "run",
    )
)

B.append(
    mcq(
        "paper-b-q06",
        "cli-program",
        "cli-program-s4",
        "exam",
        ["read-code", "read-tool-output", "judgement"],
        """
The gradebook group's `add` command takes a student and a mark. A teammate tries a mark with a decimal:

```python
@app.command()
def add(student: str, mark: int) -> None:
    typer.echo(f"Added {student}: {mark}")
```

```console
$ uv run gradebook add Ana 7.5
Usage: gradebook add [OPTIONS] {student} {mark}
Try 'gradebook add --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ Invalid value for 'mark': '7.5' is not a valid int.                          │
╰──────────────────────────────────────────────────────────────────────────────╯
$ echo $?
2
```

The teacher marks in half points, so `7.5` must work. Which change follows session 5?
""",
        [
            (
                "Wrap the body of `add` in `try` and `except ValueError`, so that the function deals with the decimal itself.",
                "`add` never runs. typer converts and checks the arguments from the type hints first, and refuses the command line before the function starts.",
            ),
            (
                "Change the hint to `mark: float`; typer then accepts decimals, and `--help` shows the new type.",
                "Right. The type hints are the specification: typer reads `int` as 'whole numbers only', so the fix is to change the spec. The check and the help follow the hint.",
            ),
            (
                "Change the hint to `mark: str`, so that any text arrives, and convert it inside `add`.",
                "This gives up the check that the hint provides for free: the help would say text, and a word such as `seven` would now reach the function, which has to reject it itself.",
            ),
            (
                "Leave the hint and ask the users to round every mark to a whole number before they type it.",
                "That moves the limit of the program onto its users. A mark with a half point is a real value, and the specification in the code should say so.",
            ),
        ],
        "b",
        """
Session 5: the type hints are the specification. From `mark: int` typer builds the usage line, converts the text and checks it. It refuses `7.5` before `add` runs, which is why the transcript shows typer's own error box and exit code 2, not a message written by the group. The fix is to change the spec: with `mark: float` the same command accepts `7.5` and `8`, and `--help` lists the argument as `<float>`. Catching the error inside `add` cannot work, because the function is never reached, and `str` throws away the check that the hint gives for free.
""",
        "S5 slides 7 and 8",
        "slides",
        "run",
    )
)

B.append(
    mcq(
        "paper-b-q07",
        "clean-code",
        "clean-code-s8",
        "exam",
        ["read-code", "read-tool-output", "judgement"],
        """
The group's `separator` function and two calls to it. The program runs, and then mypy is run on it:

```python
def separator(char: str, width: int) -> str:
    return char * width


print(separator(10, "-"))
print(separator("-", 10))
```

```console
$ uv run python separator.py
----------
----------
$ uv run mypy --strict separator.py
separator.py:5: error: Argument 1 to "separator" has incompatible type "int"; expected "str"  [arg-type]
separator.py:5: error: Argument 2 to "separator" has incompatible type "str"; expected "int"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)
```

A teammate says: "The report prints correctly, so the two mypy errors are noise." What is the right reading?
""",
        [
            (
                "Python checks the hints when the code runs and found nothing wrong, so mypy must be mistaken here.",
                "Python ignores type hints at run time. It ran line 5 only because `10 * \"-\"` is also a valid expression.",
            ),
            (
                "Plain `mypy` would accept the swapped call; the two errors come only from the extra checks that `--strict` adds.",
                "`separator` is fully annotated, so even plain mypy checks the call against its signature. `--strict` adds checks for untyped code, which is not the issue here.",
            ),
            (
                "mypy is right: the call breaks the contract `char: str, width: int` and runs only because `10 * \"-\"` is valid.",
                "Right. The hints are a contract that the next reader and mypy rely on. This call happens to work, and the next swapped call with different values may not.",
            ),
            (
                "The hints are only advice for readers, so if the output is correct the call can stay as it is.",
                "The hints are read by mypy, and CI runs mypy on every push. A call that breaks the contract turns the referee red whether or not it prints the right text.",
            ),
        ],
        "c",
        """
Session 6 calls type hints contracts: they say what goes in and what comes out, and they are read by the next person and by mypy. Python itself never checks them while the program runs, so the swapped call executes. It even prints the right line, because multiplying an integer by a string is also valid. mypy compares the call with the signature before the program runs and reports both arguments. A wrong call that happens to work is still wrong, and CI will stay red until it is fixed.
""",
        "S6 slide 26; S7 slide 10",
        "slides",
        "run",
    )
)

B.append(
    mcq(
        "paper-b-q08",
        "refactor-types",
        "refactor-types-s1",
        "exam",
        ["compare", "read-tool-output", "judgement"],
        """
A teammate commits "Extract `is_peak` and flatten the nested ifs in `class_price`" and calls it a refactoring. `uv run pytest` is green. To check, they print the prices for the hours 15 to 20 with the old and the new code into `before.txt` and `after.txt`:

```console
$ diff before.txt after.txt
4c4
< 18 member 12.0 guest 15.0
---
> 18 member 8.0 guest 10.0
```

What can you conclude?
""",
        [
            (
                "It is not a refactoring: the output changed at 18:00, so the commit changed behaviour; find the cause.",
                "Right: 'if the output changes, it was not a refactoring'. The diff shows a booking at 18:00 now priced as off-peak.",
            ),
            (
                "It is still a refactoring, because the other five hours are identical and one line is a rounding detail.",
                "The difference is 12.0 against 8.0, a price a member pays, not rounding. One changed line is enough to disqualify the commit.",
            ),
            (
                "It is a refactoring, because the structure is cleaner and the existing tests still pass.",
                "Green tests only say that no test looks at 18:00. The diff covers that hour, and it shows a changed price.",
            ),
            (
                "The old code was wrong at 18:00, so the new output is a fix and the commit can keep its name.",
                "Nothing in the transcript says which price is right, and a fix is still not a refactoring. A fix changes the output on purpose and belongs in its own commit.",
            ),
        ],
        "a",
        """
Session 7's test for a refactoring is simple: change the structure, keep the behaviour, and if the output changes it was not a refactoring. Comparing the output before and after on the same input is the check. One line differs: at 18:00 the new code charges the off-peak price, so a condition was probably altered while the code was tidied, for example a `>=` that became a `>`. Green tests only mean that no test looks at 18:00, which is itself a missing edge case. The commit should be fixed, and any intended price change should go in a separate commit with its own message.
""",
        "S7 slide 5; S8 slide 11",
        "slides",
        "run",
    )
)

B.append(
    mcq(
        "paper-b-q09",
        "testing-tdd",
        "testing-tdd-s2",
        "hard",
        ["read-code", "read-tool-output", "judgement"],
        """
The gym-booking backlog item reads: "As a member, I can cancel a class at least 2 hours before it starts and get my money back in full; closer than that I get half back, so that late cancellations still cost the gym something." A teammate's function and the group's tests, with CI red (output trimmed):

```python
def refund(hours_before: float, price: float) -> float:
    if hours_before > 2:
        return price
    return price / 2
```

```python
@pytest.mark.parametrize(
    ("hours_before", "expected"),
    [(24, 10.0), (2, 10.0), (1, 5.0), (0, 10.0)],
)
def test_refund(hours_before: float, expected: float) -> None:
    assert refund(hours_before, 10.0) == expected
```

```text
E       assert 5.0 == 10.0
E        +  where 5.0 = refund(2, 10.0)
...
E       assert 5.0 == 10.0
E        +  where 5.0 = refund(0, 10.0)
=========================== short test summary info ============================
FAILED tests/test_refunds.py::test_refund[2-10.0] - assert 5.0 == 10.0
FAILED tests/test_refunds.py::test_refund[0-10.0] - assert 5.0 == 10.0
2 failed, 2 passed in 0.01s
```

Which change is right?
""",
        [
            (
                "Change both expected values to `5.0`, so that the tests describe what `refund` really does.",
                "That lets the code decide what is correct. The backlog item says the full price comes back at exactly 2 hours, so the `2` case is a bug that this change would hide.",
            ),
            (
                "Change only the code, to `hours_before >= 2`: the two failures are one bug reported twice.",
                "The identical message hides two different causes. The `2` case then passes, but `0` still fails, because a cancellation at the start of the class gets half back.",
            ),
            (
                "Change the code to `hours_before >= 2` and skip the `0` case with `pytest.mark.skip`, since nobody can explain it.",
                "The `0` case can be explained: the rule gives half back. Skipping it keeps a wrong expected value in the file and makes CI green without the test looking at that case.",
            ),
            (
                "Change the code to `hours_before >= 2` and the `0` case to expect `5.0`; the rule decides each one.",
                "Right. A failing test only says that code and test disagree. The backlog item says which side is wrong, and here it is the code for the `2` case and the test for the `0` case.",
            ),
        ],
        "d",
        """
A failing test says only that the code and the test disagree, and here two tests disagree with the same message. Sample question 4's lesson is to check each one against what is supposed to happen, and the backlog item states it: at least 2 hours before gives the full price, closer than that gives half. The `2` case matches the rule, so the code is wrong: `>` should be `>=`, the boundary slip that edge cases exist to find. The `0` case expects the full price at the start of the class, which the rule does not give, so the test is wrong. The same assertion line, one code bug and one test bug.
""",
        "S8 slides 11 and 31; sample question 4",
        "slides",
        "run",
    )
)

B.append(
    mcq(
        "paper-b-q10",
        "refactor-types",
        "refactor-types-s9",
        "exam",
        ["read-tool-output", "judgement"],
        """
The gym-booking group stores a running total in a JSON file such as `{"total": 12.5}`. Strict mypy runs in CI:

```python
import json


def load_total(path: str) -> float:
    with open(path) as file:
        data = json.load(file)
    return data["total"]
```

```console
$ uv run mypy --strict src
src/gym/totals.py:7: error: Returning Any from function declared to return "float"  [no-any-return]
Found 1 error in 1 file (checked 1 source file)
```

What is the right fix?
""",
        [
            (
                "Add `# type: ignore[no-any-return]`, because the total in the file is always a number",
                "That is a claim nobody checks: a file with `\"12.50\"` in it would return a string from a function that promises a `float`.",
            ),
            (
                "Convert the value with `float(data[\"total\"])`, so that a real `float` leaves the function",
                "Right: `json.load` gives `Any`, so mypy cannot vouch for the type. Converting it at the boundary makes the promise true (we ran it: `\"12.50\"` becomes `12.5`).",
            ),
            (
                "Change the declared return type to `Any`, so that the function and mypy agree about what comes out",
                "mypy goes quiet because the promise is gone. Every caller now gets an unchecked value, which is what the hint was there to prevent.",
            ),
            (
                "Delete the `-> float` annotation, so that mypy has nothing to compare the returned value with",
                "Under `--strict` a missing return type is itself an error, `no-untyped-def` (we ran it), and the contract is lost.",
            ),
        ],
        "b",
        """
`Returning Any` is the types-disagree kind, caused by a value mypy cannot see into: `json.load` returns `Any`. The function promises a `float`, and nothing has checked that the file holds one. The fix is to make the promise true where the unknown value enters the program, which `float(...)` does, and it also turns a numeric string into a number. An ignore comment or a wider type would silence the message and leave the promise unchecked. Real run on all four versions with mypy 2.4.0.
""",
        "S7 slides 8 to 10; labs/07-refactor.md troubleshooting",
        "slides",
        "run",
    )
)

B.append(
    mcq(
        "paper-b-q11",
        "terminal-files",
        "terminal-files-s9",
        "core",
        ["concept", "judgement"],
        """
Two files on Ines's laptop: `scripts/check.sh` in her project, which she runs with `./scripts/check.sh`, and `~/.ssh/id_ed25519`, her private SSH key. Which pair of `chmod` modes fits the two files?
""",
        [
            (
                "`check.sh` 644 and `id_ed25519` 600",
                "600 is right for the key, but 644 has no `x` for anyone. A script that must be run by its own name needs the execute bit.",
            ),
            (
                "`check.sh` 755 and `id_ed25519` 777",
                "755 fits the script, but 777 gives everyone read, write and execute on a private key. 777 is almost never the answer.",
            ),
            (
                "`check.sh` 755 and `id_ed25519` 600",
                "Right: 755 is `rwxr-xr-x`, a script anyone can run and only the owner can change; 600 is `rw-------`, readable and writable by the owner only.",
            ),
            (
                "`check.sh` 600 and `id_ed25519` 755",
                "The modes are swapped. 600 has no `x`, so the script cannot be run by name, and 755 lets everyone read the private key.",
            ),
        ],
        "c",
        """
Permissions are r = 4, w = 2, x = 1, added per group of three: owner, group, everyone else. A script that is run by its own name needs `x`, so 755 (`rwxr-xr-x`): everyone can run it, only the owner can change it. A private key must be readable by its owner alone, so 600 (`rw-------`). 644 is the ordinary file, 777 is almost never the answer, and `chmod 777` makes an error go away and the problem worse. Session 9's slide gives these four numbers with their typical uses.
""",
        "S9 slide 21",
        "slides",
        "source",
    )
)

B.append(
    mcq(
        "paper-b-q12",
        "pipes-bash",
        "pipes-bash-s4",
        "exam",
        ["predict-output", "judgement"],
        """
The gym keeps its bookings in `bookings.csv`, one booking per line, with the class first and the member second (there is no header line):

```text
yoga,ana
yoga,marc
spin,lia
spin,joan
yoga,ana
pilates,marc
spin,ana
spin,lia
yoga,joan
```

The manager asks how many different members have booked at least one class. Which command prints that number? (`cut -d, -f2` keeps the second column. `uniq` merges equal lines that sit next to each other.)
""",
        [
            (
                "`cut -d, -f2 bookings.csv | sort | uniq | wc -l`",
                "Right: `cut` takes the member column, `sort` puts equal names side by side, `uniq` leaves one line per name and `wc -l` counts them: ana, joan, lia and marc, so 4.",
            ),
            (
                "`cut -d, -f2 bookings.csv | uniq | wc -l`",
                "Without `sort`, `uniq` merges only neighbours, and no name here sits next to an equal name. It removes nothing and prints 9, the number of bookings.",
            ),
            (
                "`cut -d, -f2 bookings.csv | sort | wc -l`",
                "`sort` orders the names but removes no repeat, so `wc -l` counts every booking and prints 9.",
            ),
            (
                "`sort bookings.csv | uniq | cut -d, -f2 | sort | wc -l`",
                "This removes repeated bookings (same class and same member), not repeated members. ana, joan and marc each still appear more than once after the `cut`, so it prints 7.",
            ),
        ],
        "a",
        """
Read the right command stage by stage. `cut -d, -f2 bookings.csv` prints the member of each booking, nine names. `sort` puts equal names next to each other, which `uniq` needs, because it merges only neighbours. `uniq` leaves one line per name: ana, joan, lia and marc. `wc -l` counts those lines and prints 4. Each other command misses a step. `uniq` without `sort` merges nothing and prints 9. `sort` and `wc -l` without `uniq` count the bookings, also 9. `sort bookings.csv | uniq` compares whole lines, class and member together, so a member who booked two different classes survives twice, and it prints 7.
""",
        "S10 slides 4 and 6 (sort, uniq, wc); S9 slide 6",
        "slides",
        "run",
    )
)

# --- open questions of Paper B -------------------------------------------------------------

B.append(
    open_q(
        "paper-b-q13",
        "clean-code",
        "clean-code-s6",
        "exam",
        ["read-code", "judgement"],
        r"""
**Read code and say what is wrong.** The vending-machine group wrote this function. `machine` maps a slot name to a list `[price, stock]`.

```python
def buy(machine, slot, coins):
    # check the slot
    if slot in machine:
        item = machine[slot]
        if item[1] > 0:
            if coins >= item[0]:
                item[1] = item[1] - 1
                return coins - item[0]
            else:
                return -1
        else:
            return -2
    else:
        return -3
```

With `machine = {"A1": [1.50, 3], "A2": [2.00, 0], "B1": [0.80, 5]}`:

```console
>>> buy(machine, "A1", 2.00)
0.5
>>> buy(machine, "A1", 1.00)
-1
>>> buy(machine, "A2", 2.00)
-2
>>> buy(machine, "C9", 2.00)
-3
>>> machine["A1"]
[1.5, 2]
```
""",
        [
            part(
                "1",
                "In one sentence, what does `buy` do?",
                1,
                "It sells one item from a slot: it returns the change and lowers the stock by one, or returns `-1` (too few coins), `-2` (sold out) or `-3` (no such slot).",
                [
                    "Says it sells an item from a slot and returns the change, lowering the stock",
                    "Says that `-1`, `-2` and `-3` signal the failures (not enough coins, sold out, no such slot)",
                ],
                "'It buys something' or 'it checks the machine' is too vague to score. Saying it returns the price instead of the change is wrong (`coins - price`). Leaving out the stock change misses a side effect that the second call in the transcript shows.",
            ),
            part(
                "2",
                "Name two problems a teammate would face when reading, testing or changing it.",
                2,
                "The three nested `if`s bury the sale deep in the function, far from the failures they test for. The results `-1`, `-2` and `-3` look like numbers, so a caller who forgets to check treats them as change.",
                [
                    "Nested `if`s (a pyramid) bury the main path",
                    "Return codes `-1`, `-2`, `-3` are unnamed, look like data, and a caller must remember to check them",
                    "Positions `item[0]` and `item[1]` instead of names for price and stock",
                    "The comment `# check the slot` only restates the code",
                ],
                "'The function is too long' is not true of this one: it is short and still hard to read. 'There are not enough comments' is the wrong lesson. 'It has three returns' without saying why that hurts earns nothing. Each answer needs the consequence for a teammate.",
            ),
            part(
                "3",
                "Describe in words how you would change it, and which of your two problems each change solves.",
                2,
                "Guard clauses for the unknown slot, the empty slot and too few coins leave the sale as the main path and remove the pyramid. Raising an error for each case instead of returning codes means a failure cannot be mistaken for change. A small dataclass (`price`, `stock`) turns `item[0]` into `item.price`.",
                [
                    "Guard clauses for the three failure cases, with the sale as the main path, solving the pyramid",
                    "Raises errors (or returns a named result) instead of `-1`, `-2` and `-3`, solving the codes that look like data",
                    "Gives the list a name or type (dataclass) so positions become `price` and `stock`, solving the guesswork",
                ],
                "'Clean it up' names no change. Changes with no link to the problem they solve lose a mark. Replacing the numbers with constants such as `NO_COINS = -1` names the codes but keeps the habit of returning them and hoping somebody checks. Splitting the function in two does not remove the pyramid or the codes.",
            ),
        ],
        """
This is the shape of sample question 7 with a different set of problems from a function that mixes everything. The function is short, which is the point: the nested ifs, the return codes and the positions each cost a teammate time. A full-marks answer names two problems with a consequence and pairs each change with the problem it solves, so the guard clauses go with the pyramid, the exceptions with the codes and the named type with the positions. Session 6's guard clauses and session 7's "do not return -1 and hope somebody checks" are the two ideas behind it.
""",
        "S6 slides 19, 22 and 23; S7 slide 17",
        "slides",
        "run",
    )
)

B.append(
    open_q(
        "paper-b-q14",
        "testing-tdd",
        "testing-tdd-s5",
        "exam",
        ["read-diff", "compare", "judgement"],
        """
**Compare.** The library group commits the first step of a new feature:

```diff
diff --git a/src/library/fines.py b/src/library/fines.py
new file mode 100644
index 0000000..534162c
--- /dev/null
+++ b/src/library/fines.py
@@ -0,0 +1,5 @@
+from datetime import date
+
+
+def overdue_fine(due: date, returned: date) -> float:
+    return 0.0
diff --git a/tests/test_fines.py b/tests/test_fines.py
new file mode 100644
index 0000000..106fb2e
--- /dev/null
+++ b/tests/test_fines.py
@@ -0,0 +1,13 @@
+from datetime import date
+
+import pytest
+
+from library.fines import overdue_fine
+
+
+def test_a_book_returned_on_the_due_date_costs_nothing() -> None:
+    assert overdue_fine(date(2026, 10, 1), date(2026, 10, 1)) == 0.0
+
+
+def test_three_days_late_costs_sixty_cents() -> None:
+    assert overdue_fine(date(2026, 10, 1), date(2026, 10, 4)) == pytest.approx(0.60)
```

Two candidate commit messages:

- A: `Add tests`
- B: `Add failing tests for overdue_fine, with a stub that returns 0.0`
""",
        [
            part(
                "1",
                "What does this commit add, and what will `uv run pytest` report for these two tests? Is that result a problem?",
                2,
                "It adds a stub returning 0.0 and two tests. The due-date test passes by luck of the stub and the three-days-late test fails: 1 failed, 1 passed. That is the intended red step: the tests say what done means before the code exists.",
                [
                    "Says it adds a stub returning 0.0 plus two tests",
                    "Predicts that one test fails (three days late) and one passes (due date, because the stub returns 0.0)",
                    "Says the red result is intended (the red step of red, green, refactor): the tests define done and prove they can fail",
                ],
                "Saying 'both tests fail' misses that the stub returns 0.0, which happens to be the right answer for the due date. Saying 'both pass' ignores that 0.0 is not 0.60. Calling the red result a mistake misses session 8's point: red is information, not a problem.",
            ),
            part(
                "2",
                "Which message is better, and why? Answer from the point of view of someone reading the history six months later.",
                2,
                "B. It tells the reader the failure is intended and why, so a red commit with a stub in it is not mistaken for an error. A says only that tests were added.",
                [
                    "Chooses B",
                    "Gives the reason: B says the tests are meant to fail and why (stub, red step) while A is too vague for a reader six months later",
                ],
                "Choosing A because it is short, or B only because it is longer, is not a reason. A message that could describe any commit adds nothing to the history. The good message names the function and the intent, as the real history does with `Add failing tests for remove_duplicates`.",
            ),
            part(
                "3",
                "Name one more test you would add for `overdue_fine`, in words.",
                2,
                "A book returned before its due date must cost 0.0, not a negative amount. The two tests cover only the due date and a late return.",
                [
                    "Names a case the two tests do not cover (returned before the due date, a very late return, a return across a month end)",
                    "States the expected result (0.0 for an early return, or the number of days times 0.20 for a late one)",
                ],
                "'Test more dates' names no case and no expected result. Repeating a late return with different days adds little. The marker wants an edge chosen on purpose: early return, empty or odd input, a boundary. State what the function should give.",
            ),
        ],
        """
This is sample question 8 with a history commit of the TDD kind. The diff adds a stub and tests, with no real code. Running it gives one pass and one fail: `.F`, then `1 failed, 1 passed`. Session 8 says that red is information, and that a stub which returns a plausible value lets the failure say something. The real history has exactly this commit shape, `Add failing tests for remove_duplicates`. The message that says so is the one a reader can use; the missing test is an early return, which a signed difference in days would make negative.
""",
        "S8 slides 5 and 13 to 15; expense-tracker e1b96de",
        "history",
        "run",
    )
)

B.append(
    open_q(
        "paper-b-q15",
        "refactor-types",
        "refactor-types-s9",
        "hard",
        ["read-tool-output", "judgement"],
        """
**Read tool output.** The gradebook group's CI is red at the Types step (`strict = true` is set in `pyproject.toml`). The file and the log:

```python
def class_average(marks):
    total = 0
    for mark in marks.values():
        total += mark
    return total / len(marks)


def best_mark(marks: dict[str, float]) -> float:
    best = 0
    for mark in marks.values():
        if mark > best:
            best = mark
    return best


def mark_of(marks: dict[str, float], student: str) -> float:
    mark = marks.get(student)
    return round(mark, 1)
```

```console
$ uv run mypy src
src/gradebook/marks.py:1: error: Function is missing a type annotation  [no-untyped-def]
src/gradebook/marks.py:12: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
src/gradebook/marks.py:18: error: Argument 1 to "round" has incompatible type "float | None"; expected "_SupportsRound2[float]"  [arg-type]
Found 3 errors in 1 file (checked 1 source file)
```

`best_mark` finds the best mark of the class, and `mark_of` returns one student's mark rounded to one decimal.
""",
        [
            part(
                "1",
                "Sort the three errors into the kinds we discussed in session 7.",
                2,
                "Line 1 is a missing annotation. Line 12 is types disagree: `best` starts as the `int` 0 and then holds a float. Line 18 is None not handled: `marks.get(student)` can return `None`, and `round` does not accept it.",
                [
                    "Line 1: missing annotation, and line 12: types disagree (an `int` start value that later holds floats)",
                    "Line 18: None not handled, although the message says `arg-type` and not `union-attr`: the clue is `float | None`",
                ],
                "Calling line 18 a types-disagree error because of the word `arg-type` is the trap: read the type, `float | None`, and ask what is missing. Mixing up lines 1 and 12 loses a mark.",
            ),
            part(
                "2",
                "Which error can crash a user, and with what input?",
                2,
                "Line 18. `mark_of` for a student who is not in the marks gets `None`, and `round(None, 1)` raises a `TypeError` (we ran it). The other two errors crash nothing.",
                [
                    "Line 18 / `mark_of` is the crash",
                    "The input: a student that is not in the marks, giving `None` and a `TypeError`",
                ],
                "Choosing line 12 \"because int and float are different\" confuses a type disagreement with a runtime error: Python compares floats with an int without complaint. Naming line 18 without the student that triggers it earns one mark.",
            ),
            part(
                "3",
                "A teammate says: \"Strict mode is slowing us down. Set `strict = false` until after the Review.\" Do you accept? Give your reasoning.",
                2,
                "No. CI would go green, but the three problems stay, including the crash for an unknown student, and the referee would no longer report it. Fix them instead: add the hints, start `best` at 0.0 and handle the `None`.",
                [
                    "Refuses, because switching the check off hides the evidence and the crash stays",
                    "Offers the real fixes: hints, `0.0`, and handling `None`",
                ],
                "\"Yes, it is only a type checker\" ignores that one of the three errors is a real crash. \"No, strict is the rule\" gives no reason: say what stays broken and what the group would be inspecting.",
            ),
        ],
        """
This is sample question 9 on a different artefact. The three kinds are the same: missing annotation, types disagree and None not handled. The None error is reported under `arg-type`, so the code in brackets does not tell you the kind; the type `float | None` does. Only that one crashes a real user, and turning strict off, like an ignore comment, would make CI green while the crash stays. We ran the code: `mark_of` with a known student prints 7.2, and with an unknown one raises `TypeError: type NoneType doesn't define __round__ method`.
""",
        "S7 slides 8 to 10; sample Q9 shape",
        "slides",
        "run",
    )
)

PAPER_B = {
    "id": "paper-b",
    "title": "Paper B",
    "kind": "realistic",
    "minutes": 60,
    "intro_md": (
        "Paper B has the same shape as Paper A, twelve multiple-choice questions then three short open questions, "
        "but it leans harder on the terminal, on tests and on reading history, and its open questions use different artefacts: "
        "a function with nested ifs, a commit that starts a test cycle and a strict-mypy log. Sit it in 60 minutes with a pen and no notes. "
        "Answer the open questions in 5–8 lines of prose. Marks: 1 for each multiple-choice question and 5, 6 and 6 for the open questions, "
        "29 in all. Mark yourself with the model answers afterwards."
    ),
    "questions": B,
}


def main() -> None:
    data = {"papers": [PAPER_A, PAPER_B]}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT.name}: {[p['id'] for p in data['papers']]}")


if __name__ == "__main__":
    main()
