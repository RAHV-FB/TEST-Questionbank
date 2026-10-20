"""Build CRAM/types/T02.json: "Programs and the command line".

Run: python3 types/src/T02.py   (from anywhere; paths are resolved from this file)
Worked-example stems and options are copied verbatim from the verified bank (cli-program.json).
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRAM = HERE.parent.parent
SITE = CRAM.parent / "study-site"
BANK = json.loads((SITE / "content" / "cli-program.json").read_text())
BY_ID = {q["id"]: q for q in BANK["questions"]}


def verbatim(qid: str) -> str:
    """Stem and options of a bank mcq, exactly as the bank has them."""
    q = BY_ID[qid]
    lines = [q["stem_md"].rstrip(), ""]
    for letter, opt in zip("abcd", q["options"]):
        lines.append(f"- {letter}) {opt['text_md']}")
    return "\n".join(lines)


BASICS = [
    {
        "id": "T02-b1",
        "heading": "Two doors into the program: the command and `python -m`",
        "body_md": (
            "`python tracker.py` runs a file with whichever interpreter you name. "
            "`uv run expenses report` runs a command the project installed. Same code, but the command has "
            "a name, a version, dependencies and an entry point, all declared in `pyproject.toml`.\n\n"
            "The entry point is one line:\n\n"
            "```toml\n[project.scripts]\nexpenses = \"expense_tracker.cli:app\"\n```\n\n"
            "Read it as **command, module, object**. `expenses` is what you type. `expense_tracker.cli` is the "
            "file `src/expense_tracker/cli.py`. `app` is the typer object inside it. On install, uv writes a small "
            "wrapper into `.venv/bin/` that imports `app` and calls it. Break one part and the message tells you which:\n\n"
            "| What broke | What you see |\n"
            "|---|---|\n"
            "| name on the left | `error: Failed to spawn` |\n"
            "| module on the right | traceback from `.venv/bin/<command>`, then `ModuleNotFoundError` |\n"
            "| object after the colon | traceback from `.venv/bin/<command>`, then `ImportError: cannot import name 'app'` |\n\n"
            "`Failed to spawn` means no command by that name exists. A traceback that starts in `.venv/bin/` means "
            "the command exists and its import failed.\n\n"
            "The second door is `python -m expense_tracker`. It runs the package's `__main__.py`, which imports the same "
            "`app` and calls it. It does not read `[project.scripts]`, so one door can break while the other works.\n\n"
            "Running `cli.py` as a plain file is neither door. With the system Python it stops at "
            "`ModuleNotFoundError: No module named 'typer'`, because typer lives only in the project's `.venv`. "
            "With `uv run python src/expense_tracker/cli.py report` it prints nothing and exits 0: the demo's `cli.py` only "
            "defines `app`, and no line calls it."
        ),
    },
    {
        "id": "T02-b2",
        "heading": "typer: the signature is the command line",
        "body_md": (
            "typer builds the command line from a function. `@app.command()` registers the function under its name. "
            "Each parameter becomes a value the user types, and its type hint tells typer how to convert the text "
            "(`12.50` arrives as the float `12.50`). One rule decides the shape:\n\n"
            "| | Argument | Option |\n"
            "|---|---|---|\n"
            "| In Python | no default | has a default |\n"
            "| Written | `add \"Bar Ramon\" 12.50` | `--category dining` |\n"
            "| For | what the command acts on | how it behaves |\n"
            "| Missing | error | the default is used |\n\n"
            "The type hint never decides: `amount: float` with no default is an argument. `--help` is generated from the "
            "signature. For the lab's `add(merchant: str, amount: float)` the usage line is:\n\n"
            "```text\n Usage: expenses add [OPTIONS] {merchant} {amount}\n```\n\n"
            "Arguments follow `[OPTIONS]` in the order you type them. The slide writes the same line in capitals, "
            "`MERCHANT AMOUNT`; read both the same way. Square brackets mean optional, as in `[path]`.\n\n"
            "A default turns a parameter into an option, even when you meant it to be positional. "
            "`amount: float = 0.0` becomes `--amount`, the usage line loses `{amount}`, and `add \"Bar Ramon\" 12.50` fails "
            "with `Got unexpected extra argument(s) (12.50)`. `typer.Argument(\"expenses.csv\")` keeps a parameter "
            "positional and optional, which is how `report` reads its file.\n\n"
            "argparse says the same with more code: a name without dashes is positional, `--hours` with a default is an "
            "option. When typer itself refuses the command line (missing argument, a value it cannot convert, an unknown "
            "option), it exits with code 2 before your function runs."
        ),
    },
    {
        "id": "T02-b3",
        "heading": "Exit codes: a program that does not lie",
        "body_md": (
            "Every program ends by handing the shell a number. **0 means success. Anything else means failure.** "
            "`echo $?` prints the number of the last command.\n\n"
            "```console\n$ uv run expenses add \"Bar Ramon\" 0\namount must be positive\n$ echo $?\n1\n```\n\n"
            "In typer you choose the number: `raise typer.Exit(code=1)`, after sending the message to stderr with "
            "`typer.echo(\"...\", err=True)`. Two ways to get it wrong: `raise typer.Exit()` with no "
            "code exits 0, and `print(...)` followed by `return` exits 0 as well.\n\n"
            "The number matters because the tools downstream read it, not your message:\n\n"
            "| Reader | What it does with the number |\n"
            "|---|---|\n"
            "| the shell | `cmd1 && cmd2` runs `cmd2` only if `cmd1` exited 0 |\n"
            "| CI | a step that exits non-zero turns the run red |\n"
            "| tests | `CliRunner` gives `result.exit_code` to assert on |\n\n"
            "So a program that prints an error and exits 0 is a program that lies:\n\n"
            "```console\n$ uv run expenses add \"Bar Ramon\" 0 && echo \"expense saved\"\n"
            "amount must be positive\nexpense saved\n```\n\n"
            "Tell two numbers apart. **1** is your own check failing. **2** is typer refusing the command line before "
            "your function ran. Both mean failure."
        ),
    },
    {
        "id": "T02-b4",
        "heading": "Renaming the template and the three that bite",
        "body_md": (
            "The lab turns the template (package `app`) into your project. Two spellings, and they are not interchangeable:\n\n"
            "| | Example | Used for |\n"
            "|---|---|---|\n"
            "| project and command | `parking-lot` | `name`, what you type |\n"
            "| package | `parking_lot` | the folder under `src/`, every import |\n\n"
            "`import parking-lot` is a `SyntaxError`, so imports and folders use underscores. The rename touches six "
            "places: the folder, `name`, the `[project.scripts]` line, the wheel `packages` line, `__main__.py` and "
            "`tests/test_cli.py`. The `app` that stays is the typer object. Then `uv lock`, then `uv sync`.\n\n"
            "Slide 13 names the three that bite:\n\n"
            "| Mistake | What you see | Fix |\n"
            "|---|---|---|\n"
            "| `uv lock` skipped | CI's first step: `The lockfile at uv.lock needs to be updated, but --locked was provided` | `uv lock`, commit `uv.lock` |\n"
            "| `__main__.py` still imports `app.cli` | pytest green, mypy red: `Cannot find implementation or library stub for module named \"app.cli\"` | fix the import |\n"
            "| one command, no `@app.callback()` | usage line has no `COMMAND`; `Got unexpected extra argument(s)`; tests exit 2 | add the empty callback |\n\n"
            "pytest misses the second because the tests import `parking_lot.cli` and never load `__main__.py`. mypy "
            "reads every file under `src`. With a single command and no callback, typer drops the command's name, so "
            "`park` is read as the plate.\n\n"
            "Checkpoint 1 is marked at the tag `v0.1`: `uv sync && uv run <app> --help` from a clean clone, `src/` layout "
            "importable, a README that says what, how to install and how to run. `git push` sends commits only; the tag "
            "needs `git push origin v0.1`."
        ),
    },
]

CHECKS = [
    {
        "id": "T02-c1",
        "q_md": (
            "A `pyproject.toml` contains:\n\n"
            "```toml\n[project.scripts]\nparking-lot = \"parking_lot.cli:app\"\n```\n\n"
            "Which part is the command you type after `uv run`?"
        ),
        "options": ["`parking_lot`", "`parking-lot`", "`parking_lot.cli`", "`app`"],
        "answer": 1,
        "why_md": (
            "The left side of the line is the command. `parking_lot.cli` is the module (the file `cli.py`) and `app` is "
            "the object inside it."
        ),
    },
    {
        "id": "T02-c2",
        "q_md": (
            "`uv run tracker report` prints a traceback whose first frame is `.venv/bin/tracker`. It ends with "
            "`ModuleNotFoundError: No module named 'ledger'`. What does that tell you?"
        ),
        "options": [
            "No command called `tracker` was installed",
            "typer is missing from the project's `.venv`",
            "The command exists; importing its module failed",
            "The lockfile disagrees with `pyproject.toml`",
        ],
        "answer": 2,
        "why_md": (
            "A first frame in `.venv/bin/tracker` means the wrapper exists, so the command is installed. "
            "The import inside it failed, and the message names `ledger`, not typer. "
            "A missing command would show `Failed to spawn`."
        ),
    },
    {
        "id": "T02-c3",
        "q_md": (
            "```python\n@app.command()\ndef convert(amount: float, currency: str = \"EUR\") -> None:\n```\n\n"
            "How does typer read the two parameters?"
        ),
        "options": [
            "Both are arguments, because both are typed after `convert`",
            "`amount` is an option, because it is a `float`",
            "`currency` is an argument that may be left out",
            "`amount` is an argument; `currency` is the option `--currency`",
        ],
        "answer": 3,
        "why_md": (
            "No default gives an argument; a default gives an option. The type hint only tells typer how to convert "
            "the text. `convert 12.50 --currency USD` is the natural call."
        ),
    },
    {
        "id": "T02-c4",
        "q_md": (
            "`add` has just written `amount must be positive` to stderr. Which ending of the error path makes it "
            "exit with code 1?"
        ),
        "options": [
            "`raise typer.Exit(code=1)`",
            "`return`",
            "`raise typer.Exit()`",
            "Nothing more: writing the message sets the code",
        ],
        "answer": 0,
        "why_md": (
            "Only `code=1` sets the number. `return` and a bare `typer.Exit()` both end normally with exit code 0, "
            "and a message on its own never changes the code."
        ),
    },
    {
        "id": "T02-c5",
        "q_md": (
            "You rename the template from `app` to `parking-lot` / `parking_lot`. Which of these lines does the rename "
            "leave unchanged?"
        ),
        "options": [
            "`name = \"app\"` under `[project]`",
            "`app = typer.Typer(...)` in `cli.py`",
            "`packages = [\"src/app\"]` under the wheel target",
            "`from app.cli import app` in `tests/test_cli.py`",
        ],
        "answer": 1,
        "why_md": (
            "The typer object keeps its name. The project name, the wheel `packages` line and the module in every "
            "import all change, because they name the project or the package."
        ),
    },
]

METHOD = [
    "**Name the artefact.** A `[project.scripts]` line or a traceback (how the command is found), a signature next to "
    "a usage line or an error box (arguments and options), a transcript with `echo $?` or `&&` (exit codes), or CI and "
    "mypy output after the rename (the three that bite).",
    "**Read the first line that names a command or a file.** `Failed to spawn` points at the command name on the left. "
    "A frame in `.venv/bin/...` means the command exists: `ModuleNotFoundError` points at the module, "
    "`ImportError: cannot import name` at the object.",
    "**For typer, go parameter by parameter and ask one question: default or no default?** No default is an argument, "
    "a default is an option, `typer.Argument(...)` is an optional argument. Ignore the types. Then match the usage "
    "line: `{x}` is required, `[x]` is optional, `[OPTIONS]` hides the options.",
    "**For exit codes, find the number and name who reads it.** 0 is success, anything else is failure. "
    "`&&`, CI and `CliRunner` read the number, not the text. 2 comes from typer refusing the command line, 1 from "
    "your own check.",
    "**Choose the fix that removes the cause.** Drop the default, correct the left or right side of the line, "
    "write `code=1`, add the empty callback, run `uv lock` and commit it, fix the import. Reject the careless moves: "
    "delete `.venv`, reinstall, `# type: ignore`, change the test to match the bug, rerun until green.",
    "**In an open answer, write three beats:** what is wrong and why (the cause in the course's words), who or what is "
    "misled (`&&`, CI, a teammate, a test), and the change in words linked to the problem it solves.",
]

WORKED = [
    {
        "title": "Reading an error after a rename (the Failed to spawn shape)",
        "question_md": verbatim("cli-program-q06"),
        "steps_md": [
            "Read the artefact before the options. `Failed to spawn` is uv saying it found no command called `parking-lot` to start.",
            "A missing command is a question about the left side of `[project.scripts]`. The file still says `app = \"app.cli:app\"`, "
            "so the command that exists is `app`. Nothing is called `parking-lot`.",
            "Test each distractor against the message. A stale `uv.lock` gives `needs to be updated`, not `Failed to spawn`. "
            "A fresh `.venv` is built from the same table and installs the same wrong command. "
            "A folder called `src/parking-lot` could not be imported, because hyphens are not allowed in a package name.",
            "Check the right side too. `app.cli` no longer exists after the folder move, so this line is wrong in both halves. "
            "The message you were shown is about the left half.",
        ],
        "answer_md": (
            "**b)** The left side of `[project.scripts]` is still `app`, so no `parking-lot` command was installed. "
            "The fix is `parking-lot = \"parking_lot.cli:app\"`: hyphens on the left, underscores in the module, `app` for the object. "
            "Rule to keep: `Failed to spawn` points at the command name, a traceback from `.venv/bin/` points at the module or the object."
        ),
    },
    {
        "title": "A default turns an argument into an option",
        "question_md": verbatim("cli-program-q17"),
        "steps_md": [
            "Read the usage line first: `Usage: expenses add [OPTIONS] {merchant}`. `{amount}` has gone. "
            "That is typer telling you what it thinks the command accepts.",
            "Go to the signature and ask the one question. `amount: float = 0.0` has a default, so `amount` is now the option `--amount`. "
            "The type is still `float`; types never decide.",
            "`12.50` was typed as a positional value. The usage line has no positional slot for it, so typer calls it a leftover: "
            "`Got unexpected extra argument(s)`.",
            "Test the distractors. `12.50` is a perfectly good float. `\"Bar Ramon\"` is quoted, so it is one word. "
            "A default on `merchant` would turn it into `--merchant` as well and make things worse.",
        ],
        "answer_md": (
            "**d)** The default made `amount` the option `--amount`, so `12.50` has no slot. "
            "The fix is to drop the default, or to write `typer.Argument(0.0)` if the value must stay positional and optional. "
            "Notice the side effect: with the default in place a forgotten amount is no longer typer's `Missing argument` error. "
            "`add \"Bar Ramon\"` runs with 0.0, and only the command's own check stops it."
        ),
    },
]

TWISTS = [
    {
        "twist_md": "The question gives you the usage line and asks for the signature, instead of the other way round.",
        "how_md": (
            "Read `{x}` as an argument with no default, `[x]` as an argument with a default given through "
            "`typer.Argument`, and anything hidden in `[OPTIONS]` as a parameter with a default. "
            "A bare name in an argparse `usage:` line is required; the same name in square brackets is optional."
        ),
    },
    {
        "twist_md": "The one-command, no-callback mistake shows a different message: `Invalid value for 'amount': 'Bar Ramon' is not a valid float` instead of `Got unexpected extra argument(s)`.",
        "how_md": (
            "Read the usage line, not the box. If it has no `COMMAND` (`expenses [OPTIONS] {merchant} {amount}`), the "
            "command's name was dropped because there is one command and no callback. typer converts the values before it "
            "counts leftovers, so `add` fills `merchant` and `Bar Ramon` fails as `amount`."
        ),
    },
    {
        "twist_md": "The command is typed `add Bar Ramon 12.50` without quotes.",
        "how_md": (
            "The shell splits words, so typer receives `Bar`, `Ramon` and `12.50`. Arguments fill in order: `Ramon` goes to "
            "`amount` and fails the `float` conversion. The result is a typer error with exit code 2, and `add` never runs."
        ),
    },
    {
        "twist_md": "A pytest line shows `assert 0 == 1` or `assert 2 == 1` on `result.exit_code`.",
        "how_md": (
            "0 means the command ended normally and lied about bad input: fix the command, not the test. "
            "2 means typer refused the command line before `add` ran, usually a default that made an option or a missing callback. "
            "When the spec says non-zero on bad input, the test is right."
        ),
    },
    {
        "twist_md": "A diff changes `print(...)` and `return` into `typer.echo(..., err=True)` and `raise typer.Exit(code=1)`, with two commit messages to judge.",
        "how_md": (
            "Say what changes for the person (same message, now on stderr) and for the tools (exit 0 becomes 1, so `&&` stops "
            "and CI sees a failure). The better message names that behaviour, for example `Exit with code 1 when add gets a "
            "non-positive amount`. `Tidy up add` hides a behaviour change behind a word that suggests a refactoring."
        ),
    },
    {
        "twist_md": "It works on my laptop, but CI is red or a clean clone fails.",
        "how_md": (
            "CI and a clean clone start from committed files only. Look for a `uv.lock` refreshed locally and not committed "
            "(`--locked` refuses the old one), a package folder that `git status` shows as `??` (untracked), or a dependency "
            "installed with `uv pip install` and never declared with `uv add`."
        ),
    },
    {
        "twist_md": "The command works but `python -m parking_lot` crashes with `No module named 'app'`, or the reverse.",
        "how_md": (
            "The two doors fail independently. The command depends on `[project.scripts]` and its wrapper. "
            "`python -m` depends on `__main__.py`, which is the file everyone forgets to rename. "
            "Name the file each door depends on, then say which one is broken."
        ),
    },
    {
        "twist_md": "An argparse script is shown only through its `--help` page, and you predict what a given command line does.",
        "how_md": (
            "Brackets are optional parts, a bare name is a required positional, and `--minimum MINIMUM` takes a value while "
            "`--verbose` is a plain switch. If a required positional is missing, argparse prints the usage, an error line, and "
            "exits with 2 before the program's own code runs."
        ),
    },
]

TRAPS = [
    "**`python src/expense_tracker/cli.py` is the same as `uv run expenses`.** The file route uses whatever interpreter you name, and for the demo it only defines `app` and never calls it. Nothing is printed and the exit code is 0.",
    "**The type hint decides argument or option.** The default decides. `amount: float` with no default is a required argument; the hint only converts the text.",
    "**A default just makes an argument optional.** A plain default turns the parameter into an option (`--amount`), and the positional value then has no slot. To keep it positional and optional, use `typer.Argument(default)`.",
    "**Printing an error is enough.** The shell, `&&`, CI and tests read the exit code, not the text. `print` plus `return`, and a bare `raise typer.Exit()`, both exit 0.",
    "**If pytest passes, the rename is complete.** The tests never load `__main__.py`, so an old `from app.cli import app` survives them. mypy reads every file under `src` and catches it. Fix the import; do not add `# type: ignore`.",
    "**Delete `.venv`, reinstall, `pip install typer`, or rerun until green.** These are the careless moves. Read the message, name the part that broke (command name, module, object, lockfile, import) and change that.",
    "**One command does not need a callback.** Without `@app.callback()` typer treats the command as the whole program and drops its name, so `<app> <command>` fails and the tests get exit code 2.",
    "**Hyphens and underscores are interchangeable.** The project and the command use hyphens (`parking-lot`); the folder, the wheel `packages` line and every import use underscores (`parking_lot`). `import parking-lot` is a `SyntaxError`.",
]

SAY_MD = (
    "- `[project.scripts]` maps the command to a module and an object: command, module, object.\n"
    "- `Failed to spawn`: no command by that name is installed. A traceback from `.venv/bin/...`: the command exists but its import failed.\n"
    "- `python -m <package>` runs `__main__.py`; it does not read `[project.scripts]`. The two doors lead to the same `app`.\n"
    "- A file run by an interpreter only defines `app`; something has to call `app()`. The system Python has no typer, only the project's `.venv` has.\n"
    "- The type hints are the specification: typer builds the command line from the signature, and `--help` is generated.\n"
    "- No default: argument, what the command acts on, missing is an error. A default: option, how it behaves, missing falls back to the default.\n"
    "- `typer.Argument(...)` keeps it positional but optional. A default made it an option, so the positional value has no slot.\n"
    "- Exit code 0 means success, anything else means failure. The shell (`&&`), CI and tests read the number, not the message.\n"
    "- A program that prints an error and exits 0 is a program that lies. Fix: message to stderr and `raise typer.Exit(code=1)`.\n"
    "- Exit 2: typer refused the command line before the function ran. Exit 1: the command's own check failed.\n"
    "- One command and no `@app.callback()`: typer drops the command's name.\n"
    "- pytest never loads `__main__.py`; mypy checks every file under `src`. Fix the import, do not ignore it.\n"
    "- CI starts from the committed files. `uv sync --locked` refuses a lockfile that disagrees with `pyproject.toml`: run `uv lock` and commit `uv.lock`.\n"
    "- argparse: standard library, no dependency, more code, worth recognising. typer: one signature."
)

PRACTICE = [
    "cli-program-q01",  # core mcq: the four things a command has
    "cli-program-q20",  # core sort: argument, optional argument, option
    "cli-program-q30",  # core mcq: hyphens for the project, underscores for the package
    "cli-program-q02",  # exam: system Python vs the project's command
    "cli-program-q16",  # exam: which call typer accepts
    "cli-program-q19",  # exam: argparse against typer
    "cli-program-q24",  # exam: && chain after a failing add
    "cli-program-q37",  # exam: one command, no callback
    "cli-program-q10",  # exam open: explain the two doors
    "cli-program-q28",  # exam open: interface and exit behaviour
    "cli-program-q07",  # hard: ImportError, the object was renamed
    "cli-program-q25",  # hard: bare typer.Exit()
    "cli-program-q40",  # hard sort: which CI step goes red first
    "cli-program-q41",  # hard open: mypy on __main__.py and # type: ignore
]

T02 = {
    "tid": "T02",
    "name": "Programs and the command line",
    "shape_md": (
        "No teacher sample question covers session 5 directly. It comes in the shape of Q3, Q4 and Q9: you read a "
        "typer signature, a `--help` page, a transcript with `echo $?` or an error after the rename, and say what it "
        "means or what is wrong. It can appear as a multiple-choice question or as one part of an open answer."
    ),
    "minutes": 35,
    "one_md": (
        "A command is found through `[project.scripts]`, typer builds its arguments and options from the signature "
        "(a default makes an option), and a command that fails must exit non-zero."
    ),
    "spot_md": (
        "- A `[project.scripts]` line, or an error after a rename: `Failed to spawn`, `ModuleNotFoundError` or "
        "`ImportError` raised from `.venv/bin/<command>`.\n"
        "- A short typer function next to a usage line or a boxed error: `Missing argument`, "
        "`Got unexpected extra argument(s)`, `Invalid value for 'amount'`.\n"
        "- A terminal transcript with `echo $?` or `&&`, or a pytest line such as `assert 0 == 1` on `result.exit_code`.\n"
        "- CI or mypy output after renaming the template, with `# type: ignore` or \"delete `.venv`\" among the options.\n"
        "- Wording such as \"Which statement explains the error?\", \"What does `uv run ...` run?\", \"What is wrong?\" "
        "or \"Which change makes the command tell the truth?\"."
    ),
    "basics": BASICS,
    "checks": CHECKS,
    "method": METHOD,
    "worked": WORKED,
    "twists": TWISTS,
    "traps": TRAPS,
    "say_md": SAY_MD,
    "practice": PRACTICE,
}


def main() -> None:
    out = CRAM / "types" / "T02.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(T02, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
