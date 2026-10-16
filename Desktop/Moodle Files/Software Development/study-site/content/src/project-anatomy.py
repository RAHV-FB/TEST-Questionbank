"""Generator for content/project-anatomy.json (module M1, order 3, sessions 3 and 4).

Every tool output in this file was produced by a real run; the inputs and raw outputs are in
$SCRATCH/work/project-anatomy/ (evidence.sh re-creates them in ev/). Only path prefixes were
rewritten (scratch paths -> /home/<name>/expense-tracker) and long outputs were trimmed.
The review fixes (q23 build error, q28 __pycache__, q06 python3.13, q40 stubs, q33 lockfile contents)
and the new items q45 and q47 were run in $SCRATCH/work/project-anatomy-fix/ (fix.sh -> ev/*.out).
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

MID = "project-anatomy"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def md(text: str) -> str:
    return textwrap.dedent(text).strip("\n")


def ind(text: str, n: int) -> str:
    """Indent every line by n spaces except the first (the template supplies its indent)."""
    return textwrap.indent(text, " " * n)[n:]


def sec(n: int) -> str:
    return f"{MID}-s{n}"


def qid(n: int) -> str:
    return f"{MID}-q{n:02d}"


def mcq(
    n: int,
    level: str,
    skills: list[str],
    s: int,
    stem: str,
    correct: tuple[str, str],
    wrong: list[tuple[str, str]],
    pos: str,
    explanation: str,
    source_ref: str,
    origin: str,
    verified_by: str,
) -> dict[str, Any]:
    assert len(wrong) == 3
    opts: list[dict[str, Any]] = [
        {"text_md": md(t), "correct": False, "why_md": md(w)} for t, w in wrong
    ]
    opts.insert(
        "abcd".index(pos), {"text_md": md(correct[0]), "correct": True, "why_md": md(correct[1])}
    )
    return {
        "id": qid(n),
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "options": opts,
        "explanation_md": md(explanation),
        "section_ref": sec(s),
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
        "rubric": [md(r) for r in rubric],
        "weak_answers_md": md(weak),
    }


def open_q(
    n: int,
    level: str,
    skills: list[str],
    s: int,
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    source_ref: str,
    origin: str,
    verified_by: str,
) -> dict[str, Any]:
    return {
        "id": qid(n),
        "type": "open",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "parts": parts,
        "lines": "5–8",
        "explanation_md": md(explanation),
        "section_ref": sec(s),
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified_by,
    }


def sort_q(
    n: int,
    level: str,
    skills: list[str],
    s: int,
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
    source_ref: str,
    origin: str,
    verified_by: str,
) -> dict[str, Any]:
    return {
        "id": qid(n),
        "type": "sort",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "categories": [{"id": c, "label": label} for c, label in categories],
        "items": [{"text_md": md(t), "category": c, "why_md": md(w)} for t, c, w in items],
        "explanation_md": md(explanation),
        "section_ref": sec(s),
        "source_ref": source_ref,
        "origin": origin,
        "verified_by": verified_by,
    }


# ---------------------------------------------------------------------------
# Real outputs (see work/project-anatomy/ev/*.out); paths rewritten only.
# ---------------------------------------------------------------------------

RUN_VENV_IMPORT = """\
$ uv sync -q
$ python3.13 -c "import typer"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import typer
ModuleNotFoundError: No module named 'typer'
$ uv run python -c "import typer; print(typer.__file__)"
/home/alice/expense-tracker/.venv/lib/python3.13/site-packages/typer/__init__.py"""

RUN_VENV_DELETE = """\
$ rm -rf .venv
$ uv sync
Using CPython 3.13.15
Creating virtual environment at: .venv
Resolved 20 packages in 5ms
Installed 19 packages in 24ms
$ git status --short"""

RUN_FLAT_IMPORT = """\
$ ls
LICENSE  README.md  expense_tracker  expenses.csv  pyproject.toml  tests  uv.lock
$ python3 -c "import expense_tracker; print(expense_tracker.__file__)"
/home/alice/expense-tracker/expense_tracker/__init__.py"""

RUN_UV_RUN_FRESH = """\
$ uv run expenses report
Using CPython 3.13.15
Creating virtual environment at: .venv
   Building expense-tracker @ file:///home/alice/expense-tracker
      Built expense-tracker @ file:///home/alice/expense-tracker
Installed 19 packages in 20ms
Expense report for expenses.csv
----------------------------------------
groceries              6401.78
utilities              3474.15"""

RUN_LOCKED_STALE = """\
$ uv sync --locked
Resolved 22 packages in 6ms
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`."""

LOCK_TYPER = """\
[[package]]
name = "typer"
version = "0.27.2"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "annotated-doc" },
    { name = "colorama", marker = "sys_platform == 'win32'" },
    { name = "rich" },
    { name = "shellingham" },
]"""

RUN_SECRET = """\
$ ls -a
.  ..  .git  README.md
$ git log --oneline
0948038 Remove the API key
7cd2bd6 Add movie search
441f9ee Start the README
$ git show 7cd2bd6:.env
MOVIE_API_KEY=9f2c71d04ab35e8c"""

RUN_TEST_IN_SRC = """\
$ uv run pytest -q
........................                                                 [100%]
24 passed in 0.02s"""

RUN_SCRIPT_WRONG_DIR = """\
$ python3 tracker.py
python3: can't open file '/home/alice/tracker.py': [Errno 2] No such file or directory"""

LOCK_A953D05 = """\
version = 1
revision = 2
requires-python = ">=3.13"

[[package]]
name = "expense-tracker"
version = "0.1.0"
source = { editable = "." }"""

STAT_A953D05 = """\
$ git show --stat --format="%h %s" a953d05
a953d05 Turn the script into a uv package

 .gitignore                      |  6 ++++++
 .python-version                 |  1 +
 README.md                       |  0
 pyproject.toml                  | 17 +++++++++++++++++
 src/expense_tracker/__init__.py |  2 ++
 uv.lock                         |  8 ++++++++
 6 files changed, 34 insertions(+)"""

# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

sections: list[dict[str, Any]] = [
    {
        "id": sec(1),
        "heading": "Why we standardise: one referee for everyone",
        "body_md": md(
            """
            "Works on my machine" is the single problem this whole course is built to solve. Code that
            runs on one laptop and nowhere else is not finished: a teammate, the marker and CI cannot use
            it. Session 1 put it first among the ways working code still fails. The answer, in session 3's
            words, is to systematise how dependencies and builds happen, so that the artefacts the code
            produces are reproducible: the same repository at the same commit gives the same environment
            and the same result on any machine.

            The contract in session 3 and lab 00 gives you freedom and two rules. You may use any operating
            system and any editor. Two things are not negotiable:

            1. **Your work passes the CI check**: the automated `ruff` + `mypy` + `pytest` run on GitHub,
               every time anyone pushes. That is the referee. The machine that decides is one none of us
               owns, so "it passes on mine" settles nothing.
            2. **The recommended path is the only one the lecturer supports.** Going off-path is allowed,
               but the time it costs is yours: off-path help is office hours, not the lab.

            The project brief sets the same bar for the group project. A stranger can install and run it
            from your repository with no help from you; a type checker accepts it; its tests pass on a
            machine none of you owns. Every tool in this module serves that bar. uv makes the environment
            identical everywhere, git and GitHub carry exactly what you committed, and CI is the neutral
            machine that checks it.

            The project pages add the phrase you will hear all term: the check is "the referee, not the
            judge". It is not marked itself, but a red check means the submission is not mechanically
            valid, and at the partial submission it caps a criterion (section 9).
            """
        ),
        "key_points": [
            '"Works on my machine" is the problem the course exists to solve; the cure is reproducible artefacts.',
            "Any OS and any editor; the CI check and the supported path are not negotiable.",
            "CI runs `ruff`, `mypy` and `pytest` on GitHub: a machine none of us owns decides.",
            "The referee, not the judge: CI is not marked, but red means not mechanically valid.",
        ],
        "exam_note_md": md(
            """
            Expect a scenario in which something passes on one laptop. The judgement is always what the
            referee sees on a clean machine, never "but it works for me".
            """
        ),
        "source_ref": "S3 slides 2–3; labs/00-setup.md (The contract); S1 slides 6 and 8; moodle/project-pages.md",
        "check": [qid(1), qid(2)],
    },
    {
        "id": sec(2),
        "heading": "The six tools and what each is for",
        "body_md": md(
            """
            You install six things once. Each answers one question, and the slide gives each one sentence.

            | Tool | What it is for |
            |---|---|
            | WSL2 | A real Linux kernel inside Windows. The course lives in a Linux shell; macOS and Linux already have one. |
            | VS Code | The editor. On Windows it runs outside WSL and reaches in through the WSL (Remote-WSL) extension. |
            | uv | Installs Python itself and your project's dependencies, so everyone gets the same versions. |
            | git | Records the history of your code. Session 3 only needs it working; module 4 explains it. |
            | GitHub | Where your group's repository lives. You authenticate to it with an SSH key. |
            | Docker | Runs your project in a container. Not needed until the Docker module. |

            Three details from lab 00 decide whether the tools work together.

            - On Windows, everything happens in the Ubuntu shell, inside your Linux home `~`, not under
              `/mnt/c/...`. Files on `/mnt/c` sit on the Windows filesystem, so every git and uv command
              there is several times slower, and a repository cloned from the Windows side gets Windows line
              endings (section 5).
            - In VS Code on Windows, connect to WSL first (`code .` from Ubuntu; the bottom-left corner shows
              `WSL: Ubuntu`) and only then install the Python and Ruff extensions. An extension installed
              before you connect lands on the Windows side and does not run in a WSL window: Ruff lints
              nothing, and the editor never flags what CI rejects.
            - Docker Desktop is a large download. Do not start it on the ESADE wifi during the lab; a red
              Docker line on your setup report is expected, and the lab says to install it at home before
              session 15.

            Notice what is not on the list: a system Python. uv installs Python itself
            (`uv python install 3.13`), which is why the Python on your laptop is the same as your
            teammates' and CI's.
            """
        ),
        "key_points": [
            "WSL2 gives Windows a real Linux shell; work in `~`, never under `/mnt/c`.",
            "uv installs Python itself and the project's dependencies: the same versions for everyone.",
            "git records history; GitHub hosts the repository and you reach it with an SSH key.",
            "In VS Code on Windows, connect to WSL before installing extensions, or Ruff lints nothing.",
            "Docker comes later; a red Docker line on the setup report is expected.",
        ],
        "exam_note_md": md(
            """
            Matching a need to the right tool, or diagnosing why the editor and CI disagree, is fair game.
            Install commands are not: no flag trivia.
            """
        ),
        "source_ref": "S3 slide 5; labs/00-setup.md (The recommended path; Windows steps 1–2)",
        "check": [qid(3), qid(4)],
    },
    {
        "id": sec(3),
        "heading": "What a virtual environment actually is",
        "body_md": md(
            f"""
            The slide promises three minutes and no magic.

            Python looks up packages in a fixed list of directories. A virtual environment is just another
            such directory, one per project, that Python is told to look in first. So "install a package"
            means "put it in this project's directory", not "change the whole computer". uv makes and fills
            that directory (`.venv`) from your `pyproject.toml`, and `uv run` uses it.

            You can watch it happen in a clone of the expense-tracker. After `uv sync`, `typer` sits inside
            `.venv`, but a bare `python3.13` (the same interpreter, which `uv python install 3.13` put on
            your `PATH`) was never told to look there:

            ```console
            {ind(RUN_VENV_IMPORT, 12)}
            ```

            Same machine, same Python 3.13, different answer. The only difference is which directories
            Python searched.

            Two consequences follow. First, `.venv` is disposable. Deleting it loses nothing that
            `uv sync` cannot rebuild from `pyproject.toml` and `uv.lock`, and `git status --short` prints
            nothing afterwards, because no file of the repository changed:

            ```console
            {ind(RUN_VENV_DELETE, 12)}
            ```

            Second, `.venv` never goes into git. It is the product, not the recipe. In a clone of the
            expense-tracker it is about 100 MB, its compiled files are built for one operating system, and
            its `python` is a link to an interpreter installed on that one computer. The recipe,
            `pyproject.toml` plus `uv.lock`, is small, is committed, and rebuilds an identical `.venv`
            anywhere. That is why `.venv/` is the first line of the expense-tracker's `.gitignore`.

            A practical corollary: deleting `.venv` is never the fix for an error uv prints about
            `pyproject.toml` or `uv.lock`. Those errors happen while uv reads the recipe, before it touches
            the environment.
            """
        ),
        "key_points": [
            "A virtual environment is one more directory per project that Python is told to look in first.",
            "Installing means putting a package in this project's `.venv`, not changing the computer.",
            "uv makes and fills `.venv` from `pyproject.toml` and `uv.lock`; `uv run` uses it.",
            "Deleting `.venv` loses nothing `uv sync` cannot rebuild, and it is never committed.",
        ],
        "exam_note_md": md(
            """
            "Delete `.venv`" is a distractor the teacher has already used (sample Q1, option a). It is
            right only when the environment itself is the problem, which an error about `pyproject.toml`
            or the lockfile never is.
            """
        ),
        "source_ref": "S3 slide 6; expense-tracker .gitignore (a953d05); runs in a clone of v0.4",
        "check": [qid(5), qid(6), qid(7)],
    },
    {
        "id": sec(4),
        "heading": "The setup lab: check, branch, push, watch CI",
        "body_md": md(
            """
            Session 3 had one goal: a working environment, and a first file pushed to the group repository
            and checked by CI. Two repositories are involved.

            First, the course materials. You clone them and run `bash scripts/setup-check.sh`. Every line
            it prints is pass or fail with a fix; it writes `setup-report.md` and prints your next commands
            with your GitHub username already filled in. **A red line is a ticket**: a to-do item you work
            down before the next session, at office hours, on a lab machine or with a neighbour. It is not a
            reason to stop.

            Second, your group's repository, which already exists. Four of you push to it in the same
            twenty minutes, and on `main` only the first push would succeed; the others are rejected because
            GitHub now holds a commit they do not have. So each person takes a branch.
            `git switch -c setup/<your-github-username>` means "make a new branch and move onto it". It is
            yours alone, and nobody can collide with you on it.

            The git survival kit, by what each command records:

            | Command | What it does |
            |---|---|
            | `git clone <url>` | Copies a repository down, with its whole history |
            | `git switch -c <name>` | Starts your own branch and moves you onto it |
            | `git status` | Says what you have changed: untracked, not staged, staged, or commits not yet pushed |
            | `git add <file>` | Stages a change: puts it in the next commit |
            | `git commit -m "..."` | Records the staged changes as one commit, on your laptop only |
            | `git push` | Sends your commits to GitHub |
            | `git tag -a v0.1 ...` | Gives one commit a permanent name; checkpoints are marked at tags |

            The loop of the day was switch, status, add, commit, push. Mechanics now, meaning in module 4.

            After the push, open the repository on GitHub, then the Actions tab. A workflow called `check`
            runs on your branch. Green means the referee accepts your repository. This check now runs on
            every push all term, and from module 4 a red check blocks a merge. Red lines on your report but
            green on Actions is fine: the report is your to-do list, and Actions checks the repository.
            """
        ),
        "key_points": [
            "A red line on the setup report is a ticket: push the report anyway and work it down.",
            "One branch per person, because four pushes to `main` at once means only the first succeeds.",
            "`add` stages, `commit` records on your laptop, `push` sends to GitHub.",
            "A tag is a permanent name for one commit; checkpoints are marked at tags.",
            "Green on Actions means the referee accepts the repository.",
        ],
        "exam_note_md": md(
            """
            Expect a `git status` or `git push` output and a question about what has, or has not, been
            recorded yet, or why a teammate cannot see your work.
            """
        ),
        "source_ref": "S3 slides 9–14; labs/00-setup.md (Run the check; Push your first file); labs/01-scaffold.md §9",
        "check": [qid(8), qid(9), qid(12)],
    },
    {
        "id": sec(5),
        "heading": "Troubleshooting: the eight that actually happen",
        "body_md": md(
            r"""
            Lab 00's rule: search the troubleshooting table for the text your machine actually printed, not
            for what you think the problem is. The slide lists eight cases. For the exam you need the
            diagnosis (what the message means and where the fix lives), not the commands.

            | What you see | What it means | The fix, in words |
            |---|---|---|
            | `wsl --install` fails, or Ubuntu never appears | Virtualisation is off in the BIOS/UEFI | Enable it in the firmware settings, then retry |
            | `docker: command not found` inside WSL while Docker Desktop runs | Docker and WSL are not sharing | Turn on Docker Desktop's WSL integration for Ubuntu |
            | `Permission denied (publickey)`, or `git push` asks for a password | Your SSH key is not on GitHub, or you cloned with an `https://` URL | Add the key; switch the remote to the `git@` URL |
            | `uv: command not found` after installing | This shell started before the installer edited your startup file | Open a new terminal; if it persists, add uv to `PATH` in the file your shell reads (`~/.bashrc` for bash, `~/.zshrc` for zsh) |
            | Everything times out | A corporate VPN, proxy or managed laptop blocks the downloads | Disconnect the VPN, use SSH over port 443, or a lab machine or neighbour for today |
            | `$'\r': command not found` | Cloned with Git for Windows, so the scripts have Windows line endings | Delete the clone and clone again from the Ubuntu shell into `~` |
            | Docker Desktop "cannot be opened because the developer cannot be verified" | macOS Gatekeeper | Allow it under Privacy & Security |
            | `! [rejected] ... (non-fast-forward)` | You pushed to `main` after a teammate did | On setup day: do not merge; switch to your own branch and push that |

            Some red text is not an error. `Failed to connect to system scope bus` during `apt upgrade` on
            WSL is harmless noise. SSH's question `Are you sure you want to continue connecting
            (yes/no/[fingerprint])?` appears the first time your machine talks to `github.com`: type `yes`.
            Permission errors from the uv installer about `~/.bash_profile` or fish files are harmless if
            `uv --version` works in a new terminal. The lab insists these are the exception: everywhere else
            in the course, red text means something is wrong and you read it.

            If you did not finish, re-run the check and work down the red lines. Nothing downstream is
            blocked on any one laptop.
            """
        ),
        "key_points": [
            "Search for the text your machine printed, not for what you think is wrong.",
            "`Permission denied (publickey)` is about your SSH key or an `https://` remote, not your code.",
            "`uv: command not found` right after installing usually needs only a new terminal.",
            r"`$'\r'` errors mean the repository was cloned from the Windows side.",
            "On setup day, a rejected push to `main` means a teammate pushed first: push your own branch.",
        ],
        "exam_note_md": md(
            """
            The judgement tested is diagnosis: which message is harmless, which points at your machine,
            which at GitHub access, and which at how you cloned or pushed.
            """
        ),
        "source_ref": "S3 slide 15; labs/00-setup.md (Troubleshooting §1–§11); labs/02-docker-setup.md (§1, §3)",
        "check": [qid(13), qid(16), qid(17)],
    },
    {
        "id": sec(6),
        "heading": "From script to project: every file and its job",
        "body_md": md(
            f"""
            The expense-tracker began, in February, as a script: two files, `tracker.py` and
            `expenses.csv`. It runs with `python tracker.py`. It has no name, no version, no dependencies
            and no home for tests. Fine for a weekend project; not something a stranger can install or four
            people can share.

            A project is the same code with a defined shape, and every file has one job:

            ```text
            pyproject.toml          the single source of truth
            uv.lock                 exact versions, pinned
            README.md               what it is, how to run it
            LICENSE                 what others may do with it
            .gitignore              what git must never see
            src/expense_tracker/    the package
              cli.py                the command-line interface
              __main__.py           makes python -m expense_tracker work
            tests/                  mirrors src/
            ```

            `tests/` mirrors `src/`: the tests for `report.py` live in `tests/test_report.py`. The
            expense-tracker's `.gitignore` lists `.venv/`, `__pycache__/`, the tool caches, and `data/`, the
            folder where `expenses add` writes real spending. The repository is public on purpose: it is a
            portfolio piece, it makes copying visible rather than tempting, and the tooling (automated
            checks, container hosting) is free on public repositories. The price is that nothing personal
            ever goes in: no credentials, no keys, no data about real people.

            The moment the script became a project is one commit:

            ```console
            {ind(STAT_A953D05, 12)}
            ```

            In the slide's words: `uv init --package`, and one edit. No code changed; the code became
            installable. `tracker.py` is not in the list, so it was not touched. What arrived is a name and
            a version (`pyproject.toml`), a Python version for uv to use (`.python-version` says 3.13), a
            lockfile, a `.gitignore`, an empty README and a package folder. The next commit, `2ecad20`, moved
            the report into the package behind a typer CLI.

            Your group repository already has all of it: it was generated from `project-template` with
            `pyproject.toml`, `src/app/`, `tests/`, CI and a licence, and lab 01 renamed `app` to your
            project.
            """
        ),
        "key_points": [
            "A script has no name, no version, no dependencies and no home for tests.",
            "`pyproject.toml` is the single source of truth; `uv.lock` pins exact versions.",
            "`.gitignore` lists what git must never see: `.venv/`, caches, `data/`.",
            "`a953d05`: `uv init --package` and one edit. No code changed; the code became installable.",
            "Public repository: portfolio, visible copying, free tooling, and never anything personal.",
        ],
        "exam_note_md": md(
            """
            You may be shown a project tree and asked what is missing for a stranger to install and run it,
            or a commit's file list and asked what it changed.
            """
        ),
        "source_ref": "S4 slides 19–20, 25–27; expense-tracker a953d05 and 2ecad20; moodle/project-pages.md (public repository)",
        "check": [qid(18), qid(19), qid(21)],
    },
    {
        "id": sec(7),
        "heading": "pyproject.toml line by line, and why src/",
        "body_md": md(
            f"""
            The slide's version of the expense-tracker's `pyproject.toml`:

            ```toml
            [project]
            name = "expense-tracker"
            version = "0.1.0"
            requires-python = ">=3.13"
            dependencies = ["typer>=0.12"]

            [project.scripts]
            expenses = "expense_tracker.cli:app"

            [build-system]
            requires = ["hatchling"]
            ```

            Read it as four answers: identity, what it needs, what it installs as a command, how it is built.

            - `[project]`: identity (`name`, `version`) and needs (`requires-python`, the Pythons it
              accepts; `dependencies`, the packages and the range of versions it accepts).
            - `[project.scripts]`: `expenses` is the command you type, `expense_tracker.cli` the module,
              `app` the object inside it. On install, uv writes a small wrapper called `expenses` into
              `.venv/bin`; it does `from expense_tracker.cli import app` and calls `app()`. Rename either
              side and the command disappears.
            - `[build-system]`: how the project is packaged into something installable, here by `hatchling`.

            `__main__.py` is the other door (session 5): it makes `python -m expense_tracker` run the CLI
            without going through the installed command. The slide's tree lists one, but the demo
            repository at `v0.4` has none; your template ships one, and it is the file everyone forgets to
            rename.

            The two spellings are not interchangeable: `expense-tracker` (hyphens) names the project,
            `expense_tracker` (underscores) is the package folder that Python imports, because Python names
            cannot contain hyphens.

            **The reason for `src/`.** Without it, `import expense_tracker` finds the folder you are
            standing in, whether or not the package is installed. A real run, with the package moved to the
            top of the repository and nothing installed (no `.venv` at all):

            ```console
            {ind(RUN_FLAT_IMPORT, 12)}
            ```

            With `src/`, the same command fails with `ModuleNotFoundError: No module named
            'expense_tracker'`. Only Python started through the project's environment, after the project
            is installed (`uv run python -c ...`), can import it. That is the point: the import only works
            if the project is installed, so the tests exercise what a user would get, not what happens to be
            lying next to them. The layout also separates the deployable code in `src/` from the tests in
            `tests/`, which are typically not included in the build.

            The layout is marked. CP1's Definition of Done, checked at your `v0.1` tag, has three binary
            items: `uv sync && uv run <your-app> --help` works from a clean clone; `src/` layout, package
            importable; the README says what the program does and how to run it. The partial rubric scores
            Structure 0 for "a script, or code outside `src/`".
            """
        ),
        "key_points": [
            "`[project]` is identity and needs; `[project.scripts]` the command; `[build-system]` how it is built.",
            '`expenses = "expense_tracker.cli:app"`: command `expenses`, module `expense_tracker.cli`, object `app`.',
            "Without `src/`, Python imports the folder you stand in, installed or not.",
            "With `src/`, only the installed package imports, so tests exercise what a user gets.",
            "`python -m` needs `__main__.py`; the installed command needs `[project.scripts]`.",
        ],
        "exam_note_md": md(
            """
            Typical questions: what a `[project.scripts]` line produces, what breaks when one side of it is
            renamed, and what you lose by moving the package out of `src/`.
            """
        ),
        "source_ref": "S4 slides 17 and 20–22; S5 slides 5–6 and 14; labs/01-scaffold.md §2 and §10; partial-rubric (Structure); runs (flat vs src layout, .venv/bin wrapper, v0.4 has no __main__.py)",
        "check": [qid(45), qid(27), qid(26)],
    },
    {
        "id": sec(8),
        "heading": "Installed, not just present: uv run and the lockfile",
        "body_md": md(
            f"""
            Two ways to run the same code:

            ```bash
            python tracker.py                # needs the file, and the right directory
            uv run expenses report           # needs the project, from anywhere
            ```

            The first runs a file with whatever Python and packages this computer happens to have, and only
            from the folder that holds it; from anywhere else Python answers `can't open file ... No such
            file or directory`. The second runs an installed command, from any folder inside the project.
            `uv run` resolves the environment from `pyproject.toml` and `uv.lock`, installs what is missing,
            and runs the command. In a fresh clone, with no `.venv` yet, one command does all of it:

            ```console
            {ind(RUN_UV_RUN_FRESH, 12)}
            ```

            The lockfile is what makes "same versions for every teammate and for CI" true.
            `pyproject.toml` says `typer>=0.12`, a range. `uv.lock` says exactly which typer, and which of
            its dependencies, down to the hash. From the expense-tracker's real lockfile (the entry goes on
            with download URLs and `sha256` hashes):

            ```toml
            {ind(LOCK_TYPER, 12)}
            ```

            The lockfile also records the project itself. The 8-line `uv.lock` of `a953d05`, committed
            before there was a single dependency, holds only the project's own entry:

            ```toml
            {ind(LOCK_A953D05, 12)}
            ```

            So `uv.lock` goes stale whenever you change something it records: a dependency,
            `requires-python`, or the project's own `name` or `version`. Command names under
            `[project.scripts]` are not in it, so renaming a command leaves the lockfile valid.

            `uv.lock` is committed. CI runs `uv sync --locked`, which installs exactly what the lockfile
            says and fails if `pyproject.toml` and `uv.lock` disagree. Add a dependency to
            `pyproject.toml` by hand, forget `uv lock`, and you get:

            ```console
            {ind(RUN_LOCKED_STALE, 12)}
            ```

            The fix is the hint: `uv lock`, then commit `uv.lock` with `pyproject.toml`. One trap: plain
            `uv sync` (without `--locked`) does not refuse. It quietly rewrites `uv.lock` to match and carries
            on, so your laptop is green while the updated lockfile sits uncommitted (`git status` shows
            `modified: uv.lock`). Session 4's diagnosis: "works on my machine" can usually be pinpointed to a
            lockfile that was never committed.
            """
        ),
        "key_points": [
            "`python tracker.py` needs the file and the right folder; `uv run expenses report` needs the project.",
            "`uv run` resolves the environment from `pyproject.toml` and `uv.lock`, installs what is missing, runs.",
            "`pyproject.toml` gives a range (`typer>=0.12`); `uv.lock` pins the exact version and hash, and also records the project's own `name`, `version` and `requires-python`.",
            "CI's `uv sync --locked` fails when the two disagree: run `uv lock` and commit both.",
            "Plain `uv sync` silently updates `uv.lock`; commit it or CI goes red.",
        ],
        "exam_note_md": md(
            """
            The sample paper's first question is a uv error with "what should you do next?". Read the
            message: it names the file, and usually the fix.
            """
        ),
        "source_ref": "S4 slides 23–24; labs/01-scaffold.md §4 and troubleshooting; expense-tracker uv.lock (a953d05 and v0.4) and .github/workflows/check.yml; runs",
        "check": [qid(30), qid(31), qid(32)],
    },
    {
        "id": sec(9),
        "heading": "Works on my machine: diagnosis, clean clones and the tag",
        "body_md": md(
            f"""
            When something passes on one laptop and fails in CI or on a teammate's machine, the cause is
            usually one of four things, and each leaves a clue.

            | Clue in a clean clone or in CI | Cause | Fix |
            |---|---|---|
            | `uv sync --locked`: the lockfile needs to be updated | `pyproject.toml` changed; the new `uv.lock` was never committed | `uv lock`, commit `uv.lock` |
            | `ModuleNotFoundError` for one of your own modules | The file exists only on one laptop; `git status` listed it as untracked | `git add` it, commit, push |
            | `ModuleNotFoundError` for a third-party package | Installed by hand into one environment, never declared | `uv add` it, so `pyproject.toml` and `uv.lock` record it; commit both |
            | Errors on one machine only, in code that is fine elsewhere | That person bypasses uv and runs a different Python | Use `uv run`; uv installs the Python the project requires |

            The cheapest way to catch all four before the marker does is the one lab 01 §10 and the
            partial rubric both give: clone your own repository into an empty folder and follow your
            README literally. A clean clone has no `.venv`,
            no caches and nothing you forgot to commit.

            History is also why secrets never go in. The project brief warns that "I deleted the file" does
            not remove it from a repository's history. A real run in a repository where a key was committed
            and then deleted:

            ```console
            {ind(RUN_SECRET, 12)}
            ```

            In a public repository, anyone can run that last command.

            Finally, the CI gate in the partial-submission rubric. The marker looks at `main` at the `v0.5`
            tag. If the `check` workflow is red on that commit, the Tests criterion is capped at 1, whatever
            else is true. A fix pushed after the tag does not count: fix, push, wait for a green tick on the
            new commit, and only then move the tag onto it. That is the referee in practice. CI does not mark
            your work, but it decides whether the submission is mechanically valid.
            """
        ),
        "key_points": [
            "Four usual causes: uncommitted lockfile, untracked file, undeclared package, a different Python.",
            "A clean clone has no `.venv`, no caches and nothing you forgot to commit.",
            "Deleting a file does not remove it from history; a pushed secret is exposed.",
            "Red CI at the `v0.5` tag caps Tests at 1; a later fix counts only once the tag is moved.",
        ],
        "exam_note_md": md(
            """
            The "works on my machine" story is the module's signature question: a green laptop, a red CI
            run, and one clue in the output. Name the cause and the fix, never "delete `.venv`".
            """
        ),
        "source_ref": "S4 slide 24; labs/01-scaffold.md §10; moodle/project-pages.md; partial-rubric (The CI gate; If CI is red on the tag); runs",
        "check": [qid(38), qid(43), qid(41)],
    },
]

# ---------------------------------------------------------------------------
# Terms
# ---------------------------------------------------------------------------

terms = [
    ("Works on my machine", "Code that runs on the laptop it was written on and nowhere else, because something it relies on (a file, a package version, a Python) exists only there. The problem the course is built to solve.", 1),
    ("Reproducible", "The same repository at the same commit gives the same environment and the same result on any machine. What standardising dependencies and builds is for.", 1),
    ("CI check (the referee)", "The `check` workflow on GitHub that runs on every push: `uv sync --locked`, `ruff`, `mypy` and `pytest`. Green means the referee accepts the repository; it is not marked itself.", 1),
    ("WSL2", "A real Linux kernel inside Windows, so Windows students work in the same Linux shell as everyone else. Work in `~`, not under `/mnt/c`.", 2),
    ("uv", "The tool that installs Python itself and the project's dependencies, the same versions for everyone. It makes and fills `.venv`; `uv run` runs commands in it.", 2),
    ("Virtual environment (`.venv`)", "One more directory per project that Python is told to look in first. Installing puts packages there, not on the whole computer. Rebuilt by `uv sync`; never committed.", 3),
    ("Setup check", "`bash scripts/setup-check.sh` in the course materials: every line pass or fail with a fix. A red line is a ticket, a to-do item, not a reason to stop.", 4),
    ("Branch", "A separate line of commits. `git switch -c <name>` makes one and moves you onto it, so your pushes cannot collide with a teammate's.", 4),
    ("Staging (`git add`)", "Marking a change to go into the next commit. A file that was never added is untracked and is not in any commit.", 4),
    ("Commit", "A recorded snapshot of the staged changes, in the repository on your laptop until you push it.", 4),
    ("Push", "Sending your commits to GitHub, where teammates and CI can see them.", 4),
    ("Tag", "A permanent name for one commit, such as `v0.1` or `v0.5`. Checkpoints are marked at their tag; a tag does not move by itself.", 4),
    ("`pyproject.toml`", "The single source of truth: the project's identity (`name`, `version`), needs (`requires-python`, `dependencies`), commands (`[project.scripts]`) and build system.", 7),
    ("`uv.lock`", "The exact versions, with hashes, of every package the project installs, including indirect ones. Generated by `uv lock`, committed, read by `uv sync`.", 8),
    ("`uv sync --locked`", "Install exactly what `uv.lock` says, and fail if `uv.lock` and `pyproject.toml` disagree. What CI runs first.", 8),
    ("`.gitignore`", "The list of what git must never see: `.venv/`, `__pycache__/`, tool caches, local data such as `data/`, and anything secret.", 6),
    ("`src/` layout", "The package lives in `src/<package>/`, so it only imports once installed; tests then exercise what a user gets, and deployable code is kept apart from tests.", 7),
    ("`[project.scripts]`", 'The table that turns an object into a command: `expenses = "expense_tracker.cli:app"` installs a command `expenses` that runs `app` from `expense_tracker.cli`.', 7),
    ("`__main__.py`", "The file inside a package that makes `python -m <package>` work; the other door, next to the installed command.", 7),
    ("Clean clone", "A fresh `git clone` into an empty folder: no `.venv`, no caches and nothing you forgot to commit. The cheapest way to see what the marker and CI will see.", 9),
]

# ---------------------------------------------------------------------------
# Traps
# ---------------------------------------------------------------------------

traps = [
    '"Delete `.venv` and sync again" fixes uv errors. It cannot fix an error about `pyproject.toml` or `uv.lock`: uv stops while reading those files, before it touches the environment, and the rebuilt `.venv` is identical anyway.',
    "`uv.lock` is generated clutter you can ignore. It is the only record of the exact versions everyone installs; CI's `uv sync --locked` needs the committed copy and refuses to run without it.",
    "Committing `.venv` gives teammates the same packages. It is built for one machine (its `python` links to an interpreter on that computer); teammates rebuild an identical one from `uv.lock` with `uv sync`.",
    "If `uv sync` works on my laptop, the lockfile is fine. Plain `uv sync` silently rewrites `uv.lock` to match `pyproject.toml`; if that change is never committed, CI's `uv sync --locked` goes red.",
    "After `uv sync`, `python3` can import the project's packages. A bare `python3` never looks in `.venv`; only `uv run ...` (or an activated environment) does.",
    "Without `src/`, nothing really changes. Without it, `import` finds the folder you are standing in even when nothing is installed, so tests can pass against files a user would never get.",
    "Deleting a file removes a leaked key. The earlier commit still holds it, and in a public repository anyone can read it with `git show`.",
    "A red line on the setup report means setup failed. A red line is a ticket: push the report anyway. Actions checks the repository, not your laptop.",
    "A fix pushed after the `v0.5` tag counts. Marking is at the tag, which never moves by itself; move it onto the green commit, or Tests stays capped at 1.",
]

# ---------------------------------------------------------------------------
# Flashcards
# ---------------------------------------------------------------------------

cards = [
    ("What single problem is the course built to solve, according to session 3?", '"Works on my machine": code that runs on one laptop and nowhere else. The cure is to systematise dependencies and builds so the artefacts are reproducible.', "concept", 1),
    ("The two non-negotiable rules of the setup contract", "1. Your work passes the CI check (`ruff` + `mypy` + `pytest` on GitHub), the referee. 2. The recommended path is the only one the lecturer supports; off-path costs your own time.", "recall", 1),
    ("Referee or judge: which is the CI check?", "The referee. It is not marked itself, but a red check means the submission is not mechanically valid, and red at `v0.5` caps Tests at 1.", "distinction", 1),
    ("The six tools of session 3, one job each", "WSL2: Linux inside Windows. VS Code: the editor. uv: Python and dependencies, the same versions for everyone. git: history. GitHub: hosts the repository (SSH key). Docker: runs the project in a container, later.", "recall", 2),
    ("Why install VS Code's Python and Ruff extensions only after connecting to WSL?", "Installed before, they land on the Windows side and do not run in a WSL window: Ruff lints nothing and the editor never flags what CI rejects.", "concept", 2),
    ("What is a virtual environment, in the slide's words?", "Python looks up packages in a fixed list of directories. A virtual environment is one more such directory, one per project, that Python is told to look in first.", "concept", 3),
    ('After `uv sync`, `python3 -c "import typer"` fails but `uv run python -c "import typer"` works. Why?', "A bare `python3` never looks in `.venv`; `uv run` starts Python with the project's environment, where `typer` was installed.", "reading", 3),
    ("What do you lose by deleting `.venv`?", "Nothing that `uv sync` cannot rebuild from `pyproject.toml` and `uv.lock`. No file of the repository changes.", "concept", 3),
    ("Why is `.venv` ignored while `uv.lock` is committed?", "`.venv` is the product, built for one machine; `uv.lock` is the recipe that rebuilds an identical `.venv` anywhere.", "distinction", 3),
    ('"A red line is a ticket." Meaning?', "Each red line on the setup report is a to-do with a fix. Push the report anyway and work down the lines before the next session.", "concept", 4),
    ("Why did everyone push to their own branch in the setup lab?", "Four people pushing to `main` in the same twenty minutes: only the first push succeeds. A branch per person cannot collide.", "concept", 4),
    ("`git add` vs `git commit` vs `git push`", "`add` stages a change; `commit` records the staged changes in the repository on your laptop; `push` sends your commits to GitHub.", "distinction", 4),
    ("`git status` says `Your branch is ahead of 'origin/setup/carla' by 1 commit.` What has not happened yet?", "The push. The commit exists on the laptop only; GitHub, CI and teammates cannot see it.", "reading", 4),
    ("Red lines on the setup report, green on Actions: a problem?", "No. The report checks your machine and is your to-do list; Actions checks the repository. Green means the referee accepts the repository.", "distinction", 4),
    (r"`$'\r': command not found` when a script runs in WSL", "The repository was cloned with Git for Windows, which gave it Windows (CRLF) line endings. Delete it and clone again from the Ubuntu shell into `~`.", "reading", 5),
    ("`Permission denied (publickey)`, or `git push` asks for a password", "Your SSH key is not on GitHub, or the remote is an `https://` URL. Add the key and switch the remote to the `git@github.com:` form.", "reading", 5),
    ("`uv: command not found` straight after installing uv", "This shell started before the installer edited its startup file: open a new terminal. If it persists, add uv's folder to `PATH` in `~/.bashrc` (bash) or `~/.zshrc` (zsh).", "reading", 5),
    ("What does a script lack that a project has?", "A name, a version, declared dependencies and a home for tests.", "concept", 6),
    ("The job of `pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `.gitignore`", "The single source of truth; exact versions, pinned; what it is and how to run it; what others may do with it; what git must never see.", "recall", 6),
    ("Three reasons the group repository is public", "A portfolio piece; it makes copying visible rather than tempting; the tooling (checks, container hosting) is free. So never anything personal: no credentials, keys or data about real people.", "recall", 6),
    ("What did commit `a953d05` change in the code?", "Nothing. `uv init --package` and one edit made the code installable: `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `src/expense_tracker/`.", "concept", 6),
    ('`expenses = "expense_tracker.cli:app"` under `[project.scripts]`', "On install, a command `expenses` that runs the object `app` in the module `expense_tracker.cli`. Rename either side and the command disappears.", "reading", 7),
    ("`pyproject.toml` read as four answers", "Identity (`name`, `version`); what it needs (`requires-python`, `dependencies`); what it installs as a command (`[project.scripts]`); how it is built (`[build-system]`).", "recall", 7),
    ("Why the `src/` layout?", "Without `src/`, `import` finds the folder you stand in, installed or not. With it, only the installed package imports, so tests exercise what a user gets, and deployable code stays apart from tests.", "concept", 7),
    ("`python tracker.py` vs `uv run expenses report`", "The first needs the file, the right directory and whatever Python the machine has. The second needs the project: uv resolves the environment from `pyproject.toml` and `uv.lock`, installs what is missing, and runs.", "distinction", 8),
    ("`typer>=0.12` in `pyproject.toml` vs the typer entry in `uv.lock`", "A range the project accepts vs the exact version chosen (0.27.2 in the expense-tracker), with its hash.", "distinction", 8),
    ("`error: The lockfile at uv.lock needs to be updated, but --locked was provided.`", "`pyproject.toml` changed without re-locking. Run `uv lock`, then commit `uv.lock` together with `pyproject.toml`.", "reading", 8),
    ("Four usual causes of \"works on my machine\"", "A lockfile changed but never committed; a file never added (untracked); a package installed by hand and never declared; a different Python because uv was bypassed.", "concept", 9),
    ("Does deleting a committed file remove a key from the repository?", "No. The earlier commit still contains it (`git show <commit>:<file>` prints it). Treat the key as leaked.", "concept", 9),
    ("The CI gate in the partial-submission rubric", "Red `check` on the `v0.5` commit caps Tests at 1. A fix pushed after the tag counts only once the tag is moved onto a green commit.", "recall", 9),
]

# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------

Q: list[dict[str, Any]] = []

# ----- s1 ------------------------------------------------------------------
Q.append(mcq(
    1, "core", ["concept"], 1,
    """
    Your group's repository runs a workflow called `check` on GitHub every time anyone pushes. Which
    statement describes its role in the course?
    """,
    ("It is the referee: a run on a machine none of you owns, where green means the work is accepted",
     "Right. Session 3 calls it the referee, and the project pages add \"the referee, not the judge\": it decides validity on neutral ground."),
    [
        ("It is the judge: its result is the mark your group gets for each checkpoint and for the partial",
         "The brief says the check is not marked itself. Criteria such as naming, tests and the README are marked by the lecturer; CI only decides whether the submission is valid."),
        ("It is optional; if the same checks pass on your own laptop, that counts just as much as CI",
         "This is the \"works on my machine\" thinking the course rejects. Passing the CI check is one of the two non-negotiable rules."),
        ("It only confirms that the files arrived on GitHub; the code itself is checked on Demo Day",
         "The workflow runs the linter, the type checker and the tests on every push, all term. It checks the code, not just its arrival."),
    ],
    "a",
    """
    The session 3 contract has two non-negotiable rules, and the first is that your work passes the CI
    check: the automated `ruff` + `mypy` + `pytest` run on GitHub. Because it runs on a machine none of us
    owns, it settles the "works on my machine" argument for good. The project pages call it "the referee,
    not the judge": it is not marked itself, but a red check means the submission is not mechanically
    valid, and at the `v0.5` tag a red check caps the Tests criterion at 1.
    """,
    "S3 slide 3; labs/00-setup.md (The contract); moodle/project-pages.md", "slides", "source",
))

Q.append(mcq(
    2, "exam", ["judgement"], 1,
    """
    Arnau uses Fedora Linux and the Neovim editor, and installs Python with Fedora's package manager
    instead of uv. His tests pass on his laptop. Under the course's setup contract, which statement is
    right?
    """,
    ("He may do this, but his work must pass the CI check, and help costs his own time",
     "Right. Any OS and any editor are allowed; the CI check and the supported path for live help are the two fixed points."),
    [
        ("He is breaking the rules: the course requires Windows with WSL2 or macOS, plus VS Code",
         "Session 3 says the opposite: any operating system and any editor is your freedom. What is fixed is the CI check, and that only the recommended path gets live support."),
        ("He is fine, as long as he hands in a screenshot showing his local checks passing",
         "A screenshot shows his machine, which is exactly what the referee ignores. The check that counts runs on GitHub."),
        ("He may do this, and because his own tests pass, a red CI result can be ignored",
         "Passing the CI check is non-negotiable. A red check means the work is not accepted, whatever his laptop says."),
    ],
    "c",
    """
    Session 3 and lab 00 give you freedom (any OS, any editor) and two rules. First, the work passes the
    CI check on GitHub, the referee. Second, the recommended path (WSL2 on Windows, VS Code, uv, git, GitHub)
    is the only one supported live in the room: off-path is allowed, but the time it costs is yours, and
    off-path help is office hours, not the lab. Arnau's setup is legal. His laptop's verdict is simply not
    the one that counts.
    """,
    "S3 slide 3; labs/00-setup.md (The contract)", "lab", "source",
))

# ----- s2 ------------------------------------------------------------------
Q.append(sort_q(
    3, "core", ["concept"], 2,
    """
    Match each need to the tool from session 3 that answers it. (VS Code, the editor, is left out.)
    """,
    [("wsl", "WSL2"), ("uv", "uv"), ("git", "git"), ("github", "GitHub"), ("docker", "Docker")],
    [
        ("A real Linux shell on a Windows laptop", "wsl",
         "WSL2 runs a real Linux kernel inside Windows; the course lives in a Linux shell."),
        ("Python 3.13 itself, installed the same way on every laptop", "uv",
         "uv installs Python itself (`uv python install 3.13`); no system Python is needed."),
        ("The exact same `typer` version on four laptops and in CI", "uv",
         "uv installs the project's dependencies from `uv.lock`: the same versions for everyone."),
        ("A record of every change to the code, and who made it", "git",
         "git records the history of your code, commit by commit."),
        ("Starting a branch of your own so you do not collide with teammates", "git",
         "`git switch -c` is a git command; the branch exists in your local repository until you push it."),
        ("The place your group's repository lives, reached with an SSH key", "github",
         "GitHub hosts the repository; you authenticate with the SSH key you added in the lab."),
        ("The `check` workflow that runs on every push", "github",
         "The workflow runs on GitHub (the Actions tab). That neutral machine is the referee."),
        ("Running the program on a computer with no Python installed, on Demo Day", "docker",
         "Docker runs the project in a container; on Demo Day the program runs from the image your repository published."),
    ],
    """
    Each of the six tools answers one question. WSL2 gives Windows the Linux shell the course assumes. uv
    installs Python and the dependencies, so versions match everywhere. git records history (including
    branches); GitHub hosts that history and runs the `check` workflow. Docker comes later and solves the
    last version of "works on my machine": running on a computer that has no Python at all.
    """,
    "S3 slide 5; labs/00-setup.md (The recommended path); moodle/project-pages.md (Demo day)", "slides", "source",
))

Q.append(mcq(
    4, "exam", ["judgement"], 2,
    """
    Lucía, on Windows, edits her project in VS Code connected to WSL (the bottom-left corner says
    `WSL: Ubuntu`). CI keeps rejecting lint errors that her editor never underlines. In the Extensions
    pane, Ruff shows an **Install in WSL: Ubuntu** button. What is the most likely explanation?
    """,
    ("Ruff was installed before she connected, so it runs on the Windows side, not in WSL",
     "Right. Lab 00 describes this exact symptom: Ruff lints nothing and the editor never flags what CI rejects. Clicking the button installs it where the code runs."),
    [
        ("The editor's Ruff uses its own default rules, while CI reads the rules in `pyproject.toml`",
         "Both read the same `[tool.ruff]` settings from `pyproject.toml`. The button shows that the editor's Ruff is not running in WSL at all."),
        ("Her Ubuntu is still on WSL1, where VS Code extensions install but do not lint",
         "A WSL version problem shows up in `wsl -l -v` and at install time. The button in the Extensions pane points directly at where Ruff is installed."),
        ("Her repository lives under `/mnt/c`, and files stored there hide lint errors from the editor",
         "Working under `/mnt/c` makes git and uv slow; it does not stop an extension from linting. The button says Ruff is not installed in WSL."),
    ],
    "b",
    """
    Lab 00 is explicit about order: open the project from Ubuntu with `code .`, check the corner says
    `WSL: Ubuntu`, and only then install the Python and Ruff extensions. Extensions installed before you
    connect land on the Windows side, and an extension on the Windows side does not run in a WSL window.
    The editor then shows nothing while CI, which runs `ruff check`, rejects the code. The
    **Install in WSL: Ubuntu** button is the giveaway; the lab says to click it.
    """,
    "labs/00-setup.md (Windows step 2)", "lab", "source",
))

# ----- s3 ------------------------------------------------------------------
Q.append(mcq(
    5, "core", ["concept"], 3,
    """
    Inside your project, `uv sync` installs `typer` into the virtual environment. According to session 3,
    what has this changed?
    """,
    ("It sits in the project's own directory, which Python looks in first when started through `uv run`",
     "Right: installing means putting it in this project's directory. Nothing else on the computer changes."),
    [
        ("Every Python program on this computer, in any folder, can now import it",
         "That is the misconception the slide corrects: installing means \"put it in this project's directory\", not \"change the whole computer\"."),
        ("It has been added to the project's dependencies in `pyproject.toml`, for everyone",
         "`uv sync` reads `pyproject.toml` and `uv.lock`; it does not edit `pyproject.toml`. Declaring a dependency is a separate step."),
        ("A copy of it has been committed to the repository, so teammates receive it on their next pull",
         "`.venv` is in `.gitignore` and never committed. Teammates get `typer` by running `uv sync` themselves, from the same lockfile."),
    ],
    "d",
    """
    Python looks up packages in a fixed list of directories. A virtual environment is one more directory,
    one per project, that Python is told to look in first. So installing puts the package in this
    project's `.venv`, nothing else on the computer changes, and only Python started through the
    environment (`uv run ...`) sees it. uv makes and fills that directory from `pyproject.toml` and
    `uv.lock`. That is the entire idea; the slide's words are "No magic".
    """,
    "S3 slide 6", "slides", "source",
))

Q.append(mcq(
    6, "exam", ["read-tool-output", "concept"], 3,
    """
    In a fresh clone of the expense-tracker you run:

    ```console
    $ uv sync -q
    $ python3.13 --version
    Python 3.13.15
    $ python3.13 -c "import typer"
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
        import typer
    ModuleNotFoundError: No module named 'typer'
    $ uv run python -c "import typer; print(typer.__file__)"
    /home/alice/expense-tracker/.venv/lib/python3.13/site-packages/typer/__init__.py
    ```

    What explains the difference between the two imports?
    """,
    ("Only `uv run` starts Python with the project's `.venv` on its search list",
     "Right. Same computer, same Python version; the only difference is which directories each one searches."),
    [
        ("The install failed during the sync, and the quiet flag hid the error message from you",
         "`uv run` imports it from `.venv` one command later, so it is installed. `-q` only hides progress lines."),
        ("The two commands run different Python versions, and `typer` supports only one of them",
         "Both are Python 3.13; the version line rules this out. The difference is which directories each one searches."),
        ("The second command downloaded the package from the internet, just for that one run",
         "The printed path is inside the project's `.venv`, where `uv sync` put it. `uv run` uses the environment and installs only what is missing; nothing was."),
    ],
    "b",
    """
    A virtual environment is a directory Python is told to look in first, but only when Python is started
    through it. `uv sync` filled `.venv` with `typer`. A bare `python3.13` was never told about `.venv`, so it
    searches only its own fixed list and fails. `uv run python` starts Python with the project's
    environment, and the printed path proves `typer` came from `.venv/lib/python3.13/site-packages`. This
    is why the course runs everything as `uv run ...`.
    """,
    "S3 slide 6; run in a clone of v0.4", "slides", "run",
))

Q.append(mcq(
    7, "core", ["read-tool-output"], 3,
    f"""
    Marc's `.venv` "feels broken", so he deletes it and rebuilds it:

    ```console
    {ind(RUN_VENV_DELETE, 4)}
    ```

    (`git status --short` printed nothing.) What did deleting `.venv` cost him?
    """,
    ("Nothing: `uv sync` rebuilt the same environment; no repository file changed",
     "Right. The recipe is in the repository; the product can be thrown away and rebuilt at any time."),
    [
        ("Python 3.13 itself, which he must now install again before the project can run",
         "`.venv/bin/python` only links to the Python that uv installed elsewhere, and the output's `Using CPython 3.13.15` shows it is still there."),
        ("The lockfile, which uv has now regenerated with the newest versions available",
         "`uv.lock` is a file in the repository, not in `.venv`. It was read, not rewritten; `git status` would list it as modified otherwise."),
        ("All 19 packages, which he will now have to reinstall one at a time with pip",
         "`uv sync` already reinstalled all 19 in one step, from the lockfile. Installing by hand with pip is the move that creates \"works on my machine\"."),
    ],
    "a",
    """
    `.venv` is a product built from a recipe. The recipe, `pyproject.toml` plus `uv.lock`, lives in the
    repository; the product can be thrown away and rebuilt, which is what `Creating virtual environment`
    and `Installed 19 packages` show. `git status --short` printing nothing confirms that no tracked file
    changed. Deleting `.venv` is harmless, which is also why it rarely fixes anything: an error about
    `pyproject.toml` or the lockfile has nothing to do with it.
    """,
    "S3 slide 6; run in a clone of v0.4", "slides", "run",
))

# ----- s4 ------------------------------------------------------------------
Q.append(mcq(
    8, "core", ["concept"], 4,
    """
    In the setup lab, every student ran `git switch -c setup/<your-github-username>` before pushing their
    setup report to the group repository. Why?
    """,
    ("With four people pushing to the same branch at once, only the first push succeeds",
     "Right. This is session 3's reason, and lab 00 adds that it is how you will work all term."),
    [
        ("Because the main branch is protected on GitHub and refuses every push from a student",
         "Lab 01 notes there is no branch protection yet. Pushes to `main` work; only the first of several simultaneous ones succeeds."),
        ("Because the CI check only runs on branches named after a student, never on main",
         "The `check` workflow runs on every push to any branch. The name only keeps each person's work apart."),
        ("Because the lecturer marks each student's setup branch as a separate checkpoint",
         "The setup report is not a checkpoint. Checkpoints are marked at tags on the group repository."),
    ],
    "a",
    """
    Your group of four pushes to the same repository within the same twenty minutes. On `main`, the first
    push succeeds and the rest are rejected, because GitHub now holds a commit the others do not have.
    `git switch -c` makes a new branch and moves you onto it; it is yours alone, so nobody can collide with
    you on it. Lab 00's troubleshooting §8 gives the same advice for the rejected push: do not try to
    merge, switch to your own branch and push that.
    """,
    "S3 slide 10; labs/00-setup.md (Push your first file)", "slides", "source",
))

Q.append(mcq(
    9, "exam", ["read-tool-output"], 4,
    """
    Carla is on her own branch. She copied her report into `setup-reports/` and tried to commit:

    ```console
    $ git commit -m "add setup report"
    On branch setup/carla
    Untracked files:
      (use "git add <file>..." to include in what will be committed)
    	setup-reports/

    nothing added to commit but untracked files present (use "git add" to track)
    ```

    What should she do next?
    """,
    ("Run `git add setup-reports/`, then commit again",
     "Right. Staging is what puts a change into the next commit; nothing was staged, so nothing was committed."),
    [
        ("Run `git push`, to send the report to GitHub",
         "There is no new commit to send. `push` sends commits, and this one was never recorded."),
        ("Delete the clone and clone the group repository again",
         "Nothing is broken. A fresh clone would not contain her report either, and she would lose the copy she just made."),
        ("Run `git switch -c setup/carla` again, to restart the branch",
         "She is already on her branch (`On branch setup/carla`), and switching branches does not stage anything."),
    ],
    "b",
    """
    git reports `setup-reports/` as untracked: it sees the folder but has not been told to include it. A
    commit records only what is staged, so with nothing staged there is nothing to commit. The order is
    `git add` (stage), `git commit` (record), `git push` (send to GitHub). The output even says what to
    do: `use "git add" to track`. Reading the message before acting is the whole skill here.
    """,
    "S3 slides 11 and 13; run in a local repository", "slides", "run",
))

Q.append(mcq(
    10, "exam", ["read-tool-output"], 4,
    """
    Carla pushed her branch during the lab. At home she fixed a red line, updated her report, committed,
    and told the group it was done. Nobody can see the update on GitHub. She runs:

    ```console
    $ git status
    On branch setup/carla
    Your branch is ahead of 'origin/setup/carla' by 1 commit.
      (use "git push" to publish your local commits)

    nothing to commit, working tree clean
    ```

    What is going on?
    """,
    ("Her new commit is recorded only on her laptop; `git push` sends it to GitHub",
     "Right. `ahead ... by 1 commit` means the commit exists locally and GitHub has not received it."),
    [
        ("The commit failed, because the output says the working tree is clean and nothing is staged",
         "\"Working tree clean\" means everything is committed. The commit exists; it just has not left her laptop."),
        ("GitHub takes a few minutes to show new commits, so she should wait and refresh the page",
         "GitHub has not received anything yet. Waiting changes nothing until she pushes."),
        ("She must `git add` the report again, because GitHub reads what is staged, not committed",
         "Staging comes before a commit, and the commit is already made. GitHub receives commits through `push`, not `add`."),
    ],
    "a",
    """
    Each survival-kit command records something in a different place. `add` stages, `commit` records the
    staged change as a commit in the repository on her laptop, and `push` sends commits to GitHub. `git
    status` says it plainly: her branch is one commit ahead of the copy on GitHub (`origin/setup/carla`),
    and the hint is `use "git push" to publish your local commits`. Until she pushes, neither her
    teammates nor CI can see the change.
    """,
    "S3 slide 13; run in a local repository", "slides", "run",
))

Q.append(mcq(
    11, "exam", ["read-tool-output", "judgement"], 4,
    """
    During the setup lab, Bob forgets to make his own branch. He commits his report on `main` and pushes:

    ```console
    $ git push
    To github.com:esade-swdev-2026/parking-lot.git
     ! [rejected]        main -> main (fetch first)
    error: failed to push some refs to 'github.com:esade-swdev-2026/parking-lot.git'
    hint: Updates were rejected because the remote contains work that you do not
    hint: have locally. This is usually caused by another repository pushing to
    hint: the same ref. If you want to integrate the remote changes, use
    hint: 'git pull' before pushing again.
    hint: See the 'Note about fast-forwards' in 'git push --help' for details.
    ```

    What happened, and what does lab 00 tell him to do?
    """,
    ("A teammate pushed to `main` first; he should make his own branch and push that instead",
     "Right. Lab 00 §8: do not try to merge, take your own branch and push it. His commit comes with him onto the new branch."),
    [
        ("His SSH key is not on GitHub yet; he should add the public key and push again",
         "An SSH problem stops the connection with `Permission denied (publickey)`. Here GitHub accepted the connection and refused the update."),
        ("He should run `git push --force`, so that his own commit replaces whatever is there now",
         "Forcing would throw away the teammate's commit on `main`. The lab's answer is your own branch, not overwriting someone else's work."),
        ("His clone is corrupted; he should delete it and clone the repository again",
         "Nothing is corrupted, and a fresh clone would not contain his commit. The hints say GitHub has work he lacks."),
    ],
    "d",
    """
    The hints say the remote contains work he does not have locally: a teammate pushed to the same branch
    first. This is exactly why the lab gives everyone a branch. Lab 00 §8 lists the same rejection (as
    `non-fast-forward`; git says `fetch first` when it has not yet seen the teammate's commit) and says:
    do not try to merge, switch to your own branch and push that, with `git push -u origin
    setup/<your-github-username>`. Merging properly is module 4.
    """,
    "S3 slide 10; labs/00-setup.md §8; run against a local bare repository (URL rewritten)", "lab", "run",
))

Q.append(mcq(
    12, "core", ["judgement"], 4,
    """
    Your setup report has a red line for Docker. You pushed it anyway, and on GitHub, in the Actions tab,
    the `check` workflow on your branch is green. What does that mean?
    """,
    ("The referee accepts the repository; the red line is a ticket on your own to-do list",
     "Right. The report checks your machine; Actions checks the repository."),
    [
        ("Something is wrong: CI should have failed, because the report contains a red line",
         "CI does not read your report. It checks the repository: lint, types and tests."),
        ("You should delete the report from the repository and push it again once every line is green",
         "The lab says to push the report even if lines are red. A red line is a ticket, not something to hide."),
        ("Your setup is complete, so the red Docker line can be ignored for the rest of the course",
         "Docker is needed later; the lab says to install it at home before session 15. Green on Actions says nothing about your laptop's Docker."),
    ],
    "a",
    """
    Two different things are being checked. The setup report is about your machine: every line pass or
    fail with a fix, and a red line is a ticket you work down. The `check` workflow is about the
    repository: green means the referee accepts it. Session 3 says it directly: red on the report but
    green on Actions is fine, because the report is your to-do list and Actions checks the repository. A
    red Docker line was expected on lab day.
    """,
    "S3 slides 9 and 14; labs/00-setup.md (About Docker, today)", "slides", "source",
))

# ----- s5 ------------------------------------------------------------------
Q.append(sort_q(
    13, "exam", ["read-tool-output", "judgement"], 5,
    """
    Messages from setup day, as the lab's troubleshooting table quotes them. Sort each by where the fix
    lives.
    """,
    [
        ("machine", "Your machine's own setup"),
        ("access", "Network or GitHub access"),
        ("clone", "How you cloned or pushed"),
        ("none", "Not an error: nothing to fix"),
    ],
    [
        ("`wsl --install` fails and Ubuntu never appears", "machine",
         "Virtualisation is disabled in the BIOS/UEFI; enable it in the firmware settings and retry."),
        ("`docker: command not found` inside WSL while Docker Desktop is running", "machine",
         "Docker Desktop is not sharing with your Ubuntu; turn on its WSL integration."),
        ("`git: command not found`", "machine",
         "The shell cannot find a program called `git`: it is not installed, or not on the `PATH` of this machine. The fix is on your side."),
        ("`uv: command not found` in a new terminal, after installing uv", "machine",
         "The installer wrote the `PATH` line to a startup file your shell does not read; add it to `~/.bashrc` or `~/.zshrc`."),
        ("`Permission denied (publickey)` from `ssh -T git@github.com`", "access",
         "Your SSH key is not on GitHub; add the public key and test until GitHub greets you by name."),
        ("Everything times out on a managed laptop with an always-on VPN", "access",
         "The VPN or proxy blocks the downloads; disconnect it, use SSH over port 443, or use a lab machine for today."),
        (r"`$'\r': command not found` when running the setup check", "clone",
         "The repository was cloned with Git for Windows, so it has Windows line endings; clone it again from the Ubuntu shell."),
        ("`! [rejected] ... (non-fast-forward)` when pushing to `main`", "clone",
         "A teammate pushed first; switch to your own branch and push that."),
        ("`ssh: connect to host github.com port 22: Operation timed out`", "access",
         "The request never reached GitHub: a firewall, VPN or proxy is blocking port 22. The fix is about the network, not your key."),
        ("`Switched to a new branch 'setup/ana'`", "none",
         "Git is reporting that it did what you asked. It is not an error."),
    ],
    """
    Lab 00's rule is to search for the text your machine printed, and the text itself usually tells you where
    to look. Four messages are about your machine (virtualisation, Docker and WSL sharing, a program missing
    from the `PATH`), three about reaching the outside world (SSH key, VPN or proxy, a blocked port) and two
    about how you used git (cloned from the Windows side, pushed to `main` after a teammate). One line is
    only git telling you what it did.
    """,
    "S3 slide 15; labs/00-setup.md (Troubleshooting); labs/02-docker-setup.md §1 and §3", "lab", "source",
))

Q.append(mcq(
    14, "exam", ["read-tool-output", "judgement"], 5,
    """
    Testing her new SSH key, Nora runs `ssh -T git@github.com` for the first time on her laptop and sees:

    ```console
    $ ssh -T git@github.com
    The authenticity of host 'github.com (140.82.121.3)' can't be established.
    ED25519 key fingerprint is SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU.
    Are you sure you want to continue connecting (yes/no/[fingerprint])?
    ```

    What should she do?
    """,
    ("Type `yes`: her machine is meeting `github.com` for the first time",
     "Right. Lab 00 §10: SSH is asking you to confirm you trust the server; you will not be asked again."),
    [
        ("Generate a new SSH key, because GitHub does not recognise the one she has",
         "The fingerprint is GitHub's host key, not hers. The question says nothing about her key and appears on every operating system the first time."),
        ("Answer `no`: an unknown host means someone is intercepting the connection",
         "It is unknown only because her machine has never talked to `github.com`. Answering `no` stops the test, and the question comes back next time."),
        ("Close the terminal and switch the repository to an `https://` URL instead",
         "That swaps a harmless question for the password-prompt problem of troubleshooting §3. The course uses SSH."),
    ],
    "c",
    """
    Lab 00 §10: the first time a machine talks to `github.com`, SSH asks you to confirm you trust the
    server. It is not an error and it says nothing about your key. Type `yes` (the whole word) and press
    Enter; the host is remembered and you are not asked again. It happens on every operating system at the
    `ssh -T git@github.com` step. The setup check script never shows it, because it accepts new hosts on
    its own.
    """,
    "labs/00-setup.md §10; run with an empty known-hosts file; prompt text as quoted in lab 00 §10", "lab", "run",
))

Q.append(mcq(
    15, "exam", ["judgement"], 5,
    """
    On her Mac, Elena runs the uv installer, then types `uv --version` in the same Terminal window. The
    shell answers that the command `uv` is not found. What should she do first?
    """,
    ("Close the Terminal window, open a new one, and try again",
     "Right. Lab 00 §4: the installer edited the startup file after this shell had already started."),
    [
        ("Reinstall uv, because the first install evidently failed",
         "The installer worked; it added uv to a startup file that this already-open shell read before the change. Reinstalling does not change that."),
        ("Run the installer again with `sudo` so that it installs for the whole system",
         "uv installs into your home folder and needs no administrator rights. The problem is the shell that has not re-read its startup file."),
        ("Install Python 3.13 first, because uv needs Python to start",
         "uv does not need Python; it installs Python itself (`uv python install 3.13`). The shell simply cannot find uv yet."),
    ],
    "b",
    """
    Lab 00 §4: the installer added `uv` to your shell's startup file, but this shell started before that.
    Close the terminal and open a new one. Only if it still fails do you dig further: `echo $SHELL` tells
    you which shell you run, and the `PATH` line must go in the file that shell reads, `~/.zshrc` on every
    recent macOS, `~/.bashrc` on WSL Ubuntu. The `Login shell` line of the setup report gives the same
    information.
    """,
    "labs/00-setup.md §4 (macOS step 3)", "lab", "source",
))

Q.append(mcq(
    16, "exam", ["judgement", "read-tool-output"], 5,
    """
    Four students show you red text from setup day. Which one needs no fix at all?
    """,
    ("Martina: installer permission errors for shells she never uses, while `uv --version` works in a new terminal",
     "Right. Lab 00 §4 calls these finished business: startup files for shells she does not use."),
    [
        ("Iker: `Permission denied (publickey)` every time he tries to push his commits up to the group's repository on GitHub",
         "His SSH key is not on GitHub, or he cloned with an `https://` URL. Until he fixes it, nothing he commits reaches GitHub."),
        (r"Sara: `$'\r': command not found` as soon as she runs the setup check script from her Ubuntu shell",
         "She cloned from the Windows side, so the scripts carry Windows line endings. She must clone again from the Ubuntu shell."),
        ("Leo: `uv: command not found` even in a brand-new terminal window, on the morning after he installed uv and restarted his laptop",
         "A new terminal rules out the quick fix. The installer wrote to a startup file his shell does not read, so he must add uv to `PATH` in the right file."),
    ],
    "d",
    """
    Lab 00 marks only a few red messages as harmless, and Martina's is the one §4 names: permission errors
    for startup files of shells you do not use are finished business once `uv --version` works in a new
    terminal. The others are real: a missing SSH key or `https://` remote, Windows line endings from
    cloning on the Windows side, and uv missing from `PATH` even in a fresh shell. The lab stresses the
    rule behind the exception: everywhere else in the course, red text means something is wrong and you
    read it.
    """,
    "labs/00-setup.md §3, §4, §6", "lab", "source",
))

Q.append(mcq(
    17, "exam", ["judgement"], 5,
    r"""
    Pol, on Windows, cloned the course materials with Git for Windows into his Documents folder. Then he
    opened Ubuntu and ran the setup check from there. It stops at once with `$'\r': command not found`.
    What is the diagnosis?
    """,
    ("Git for Windows gave his clone Windows line endings; he should re-clone from the Ubuntu shell",
     "Right. This is lab 00 §6: Windows (CRLF) line endings from cloning on the Windows side."),
    [
        ("The script has a bug, so he should report it to the lecturer and wait for a fixed version",
         r"The same script runs for everyone else. The `\r` (carriage return) in the message points at how the file reached his disk."),
        ("The file lacks execute permission, and running `chmod +x` on the script will fix it",
         "He ran it as `bash scripts/setup-check.sh`, which only needs read permission. A permission problem says `Permission denied`."),
        ("His Ubuntu runs on WSL1 instead of WSL2, and upgrading the WSL version will fix it",
         "The WSL version decides whether Linux runs properly, not which bytes are inside the file. The carriage returns came from cloning on the Windows side."),
    ],
    "c",
    r"""
    Lab 00 §6: Git for Windows rewrites line endings to CRLF, and a Linux shell cannot run a script with
    carriage returns (`\r`) in it. The fix is to delete that clone and clone again from inside the Ubuntu
    shell, into the Linux home `~`. That also moves the files off the slow Windows filesystem under
    `/mnt/c`. The lab warns about this in Windows step 1: everything happens in the Ubuntu shell, not in
    PowerShell and not in Git Bash.
    """,
    "labs/00-setup.md §6 and Windows step 1", "lab", "source",
))

# ----- s6 ------------------------------------------------------------------
Q.append(mcq(
    18, "core", ["concept"], 6,
    """
    At tag `v0.0` the expense-tracker is two files, `tracker.py` and `expenses.csv`, and it runs with
    `python tracker.py`. According to session 4, what does it lack that makes it a script rather than a
    project?
    """,
    ("A name, a version, declared dependencies and a home for tests",
     "Right. Slide 19, word for word: no name, no version, no dependencies, no home for tests."),
    [
        ("A way to run it at all, because it has no command of its own yet",
         "It runs: `python tracker.py` prints the report. Running is not what separates a script from a project."),
        ("Version control, because the script is not yet in git",
         "`v0.0` is a tag in the git history, so it is already under version control. Being in git does not make it a project."),
        ("Functions, because all of its code still sits at the top level of the file",
         "`tracker.py` already has `calculate_totals` and `run`. Structure inside the file is a clean-code question, not what makes a project."),
    ],
    "a",
    """
    Session 4, slide 19: a script runs with `python tracker.py` and has no name, no version, no
    dependencies and no home for tests. Fine for a weekend project. A project adds `pyproject.toml`
    (identity and needs), `uv.lock` (exact versions), a package under `src/`, `tests/`, a README and a
    licence, so that a stranger can install it and four people can work on it. The expense-tracker made
    that step in commit `a953d05`.
    """,
    "S4 slide 19; expense-tracker v0.0", "slides", "source",
))

Q.append(mcq(
    19, "exam", ["read-diff", "concept"], 6,
    f"""
    Session 4 calls this commit the moment the expense-tracker became a project:

    ```console
    {ind(STAT_A953D05, 4)}
    ```

    Which description of the commit is accurate?
    """,
    ("It changed no existing code; it added what makes the code installable",
     "Right. The slide: `uv init --package`, and one edit. No code changed, the code became installable."),
    [
        ("It moved the script into the new package folder and rewrote its code as a package",
         "`tracker.py` is not in the list, so it was not touched. The report moved into the package in the next commit, `2ecad20`."),
        ("It added typer as a dependency and built the command-line interface on top of it",
         "At this commit `dependencies = []`. `typer` and the `expenses` command arrived in `2ecad20`."),
        ("It added the first tests for the report, so that CI had something to check",
         "No file under `tests/` appears. The first tests arrived much later, after `v0.3`."),
    ],
    "d",
    """
    Every line of the stat is a new file: `pyproject.toml` (name, version, Python requirement), `uv.lock`,
    `.python-version`, `.gitignore`, an empty `README.md` and a package folder `src/expense_tracker/` with
    a two-line `__init__.py`. `tracker.py` is not listed, so its code is exactly as before. That is the
    slide's point: `uv init --package` and one edit; no code changed, the code became installable. The CLI
    and `typer` came in the next commit, `2ecad20`.
    """,
    "S4 slides 25–26; expense-tracker a953d05 and 2ecad20", "history", "run",
))

Q.append(mcq(
    20, "core", ["concept"], 6,
    """
    Every group repository in the course is public. Which of these is one of the reasons the project brief
    gives?
    """,
    ("Automated checks and container hosting cost nothing on public repositories",
     "Right. The brief's three reasons: a portfolio piece, copying becomes visible, and the tooling is free."),
    [
        ("So that GitHub's CI can clone the repository without needing anyone's SSH key",
         "CI runs inside GitHub and checks out private repositories as well. The brief's reason is cost: checks and container hosting are free on public repositories."),
        ("So that other groups can reuse your code freely in their own projects",
         "The opposite: being public makes copying visible rather than tempting."),
        ("So that the lecturer can push his own fixes straight to your main branch",
         "Public means anyone can read it, not write to it. The lecturer marks what you push."),
    ],
    "a",
    """
    The project brief gives three reasons for a public repository: it is a portfolio piece, it makes
    copying visible rather than tempting, and it makes the tooling free (automated checks and container
    hosting cost nothing on public repositories). It also gives the warning that comes with it: never put
    anything personal in the repository, no credentials, no keys, no data about real people, because "I
    deleted the file" does not remove it from history.
    """,
    "moodle/project-pages.md (Project Brief)", "slides", "source",
))

Q.append(sort_q(
    21, "exam", ["judgement", "concept"], 6,
    """
    Your group is about to make its first real commit. Sort each path by what should happen to it.
    """,
    [
        ("commit", "Commit it: part of the project's definition"),
        ("rebuilt", "Never commit: rebuilt or generated on each machine"),
        ("private", "Never commit: secret or personal"),
    ],
    [
        ("`pyproject.toml`", "commit", "The single source of truth: identity, needs, commands, build."),
        ("`uv.lock`", "commit", "The exact pinned versions; CI's `uv sync --locked` needs the committed copy."),
        ("`.python-version`", "commit", "Tells uv which Python to use for the project; `a953d05` committed it with the rest."),
        ("`tests/test_report.py`", "commit", "Tests are part of the project; CI runs them on every push."),
        ("`LICENSE`", "commit", "Says what others may do with the code; lab 01 has you put your group's names in it."),
        ("`.venv/`", "rebuilt", "Built for one machine from `pyproject.toml` and `uv.lock`; `uv sync` rebuilds it anywhere."),
        ("`__pycache__/`", "rebuilt", "Compiled bytecode that Python writes as it runs; it is regenerated automatically."),
        ("`.mypy_cache/`", "rebuilt", "A tool's cache that speeds up the next run; it is rebuilt when missing."),
        ("`.env` holding the group's API key", "private", "A credential. Once committed it stays in the history, and the repository is public."),
        ("`data/expenses.csv`, where `expenses add` writes your real spending", "private", "Data about a real person; the expense-tracker keeps `data/` out of version control in its `.gitignore`."),
    ],
    """
    The rule: commit the recipe, ignore the products, and never let anything secret or personal near the
    repository. `pyproject.toml`, `uv.lock`, `.python-version` and the tests define the project, so a
    clean clone needs them. `.venv/` and the caches are rebuilt on every machine, which is why they head
    the expense-tracker's `.gitignore`. Keys and personal data never go in, because deleting them later
    does not remove them from history.
    """,
    "S4 slide 20; expense-tracker .gitignore; moodle/project-pages.md", "slides", "source",
))

Q.append(open_q(
    22, "exam", ["read-diff", "compare"], 6,
    f"""
    Two candidate commit messages for the same change to the expense-tracker. The change:

    ```text
    {ind(STAT_A953D05.split(chr(10), 3)[3], 4)}
    ```

    - A: `Turn the script into a uv package`
    - B: `add files`
    """,
    [
        part("1", "What does this change do?", 2,
             "It turns the `tracker.py` script into an installable project without changing its code: `uv init --package` adds `pyproject.toml` (name, version, Python requirement), a lockfile, a `.gitignore`, a Python version file and a package folder `src/expense_tracker/` holding only a placeholder `__init__.py`.",
             ["Says it makes the code installable or turns the script into a package (for example via `uv init --package`)",
              "Says no existing code changed (`tracker.py` untouched); only new project files were added"],
             "\"It adds some config files\" describes the list but not the meaning. The mark is for the consequence: the code becomes installable, with a name and a version. Many students also claim the script was moved into `src/`; it was not, since `tracker.py` is not in the list, and that only happens in the next commit."),
        part("2", "Which message is better for someone reading the history six months later, and why?", 2,
             "A. It says what the commit achieves, so a reader scanning `git log --oneline` finds the moment the script became a project without opening the diff. B is true of almost any commit and tells them nothing.",
             ["Chooses A",
              "Reason: A states the purpose or outcome and is findable in a one-line log; B is vague and could describe any commit"],
             "Choosing A without a reason earns one mark at most. \"A is longer\" or \"A is more professional\" is not a reason. Answer from the reader's point of view: what does the line tell someone who has not seen the diff?"),
        part("3", "Name one thing the project can do after this commit that the script could not.", 1,
             "It can be installed with `uv sync` into its own environment, with a name and a version, so dependencies can now be declared and locked, and a command added through `[project.scripts]`.",
             ["Names a concrete new capability: installable with `uv sync`, declared and locked dependencies, a name and version, or a command via `[project.scripts]`"],
             "\"It is better organised\" is not a capability. Name something you can now do that a bare `tracker.py` cannot, such as installing it with `uv sync` into its own environment or declaring a dependency that gets locked."),
    ],
    """
    This is the sample paper's "compare" shape applied to the expense-tracker history. Part 1 needs the
    meaning of the file list (installable, no code changed); part 2 needs the reader's point of view; part
    3 checks you know what the project gained. The real message is A.
    """,
    "S4 slides 25–26; expense-tracker a953d05; sample paper Q8 shape", "history", "run",
))

Q.append(open_q(
    23, "hard", ["read-code", "judgement"], 6,
    """
    A group asks you to review their repository before Checkpoint 1. A stranger must be able to clone it
    and run `uv sync && uv run parking-lot --help`. In a fresh clone (`git ls-files` lists the files git
    tracks):

    ```console
    $ ls -a
    .  ..  .git  .gitignore  .venv  README.md  parking.py  pyproject.toml  test_parking.py
    $ cat .gitignore
    __pycache__/
    $ wc -c README.md
    0 README.md
    $ git ls-files .venv | wc -l
    636
    $ cat pyproject.toml
    [project]
    name = "parking-lot"
    version = "0.1.0"
    requires-python = ">=3.13"
    dependencies = ["typer>=0.12"]

    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    ```
    """,
    [
        part("1", "Name three things that would stop or mislead a stranger, and why each matters.", 3,
             "`parking.py` is a loose file, not a package `src/parking_lot/`, so the build finds no `parking_lot` and `uv sync` fails before installing anything. With no `[project.scripts]` entry, even a working install would create no `parking-lot` command. With no committed `uv.lock`, versions are unpinned and CI's `uv sync --locked` stops at once.",
             ["No `[project.scripts]` entry: even once it installs, no `parking-lot` command exists",
              "No `uv.lock`: versions are not pinned, and `uv sync --locked` in CI fails",
              "Code is not a package in `src/parking_lot/`: the build finds nothing named `parking_lot`, so `uv sync` itself fails",
              "`.venv` is committed (636 tracked files) although it is built for one machine; it should be untracked and listed in `.gitignore`",
              "README is empty: a stranger cannot tell what it does or how to run it",
              "Tests are not in a `tests/` folder that mirrors `src/`"],
             "Listing problems without saying why they matter (\"no lock file\", \"bad layout\") earns little: each point needs its consequence for the stranger. A common miss is the absent `[project.scripts]` table; students check what is there, not what is missing. Another is assuming the install works: with no `parking_lot` package, `uv sync` stops at the build. Saying \"the `.gitignore` is wrong\" without naming `.venv/` is too vague."),
        part("2", "Describe in words how you would fix two of them, and which problem each change solves.", 2,
             "Move the code into a package `src/parking_lot/` and add a `[project.scripts]` entry pointing `parking-lot` at the `app` object in `parking_lot.cli`, so the build works and creates the command. Run `uv lock`, commit `uv.lock`, and untrack and ignore `.venv/`, so every machine builds the same environment.",
             ["Describes a fix for the command or layout (package under `src/`, `[project.scripts]` pointing at the CLI object)",
              "Describes a fix for reproducibility (commit `uv.lock`; untrack and ignore `.venv/`) or for the README (what it does, `uv sync`, an example)",
              "Links each change to the problem it solves"],
             "Writing the TOML is not asked for and gains nothing; describe the change in words. Answers that say \"add a lock file\" without saying it must be committed miss why it exists. Deleting `.venv` locally without removing it from git does not fix the repository."),
        part("3", "Which item of CP1's three-item Definition of Done does the layout fail?", 1,
             "Item 2, `src/` layout with an importable package; item 1 fails too, as `uv sync` cannot build it.",
             ["Names CP1 item 2: `src/` layout with an importable package"],
             "Quoting the README item instead of the layout item misses the question. CP1 is three binary items: clean-clone install and `--help`, `src/` layout with the package importable, and a README that says what it does and how to run it."),
    ],
    """
    The question is the session 4 anatomy slide in reverse: compare the tree with the list of files a
    well-formed project has, and for each gap say what a stranger would hit. The strongest answers
    connect each gap to a consequence (a build error on `uv sync`, no command, unpinned versions) and
    then to CP1's Definition of Done. A real run of `uv sync` in a clone of this repository stops at the
    build: hatchling reports that no directory matches the project's name, `parking_lot`.
    """,
    "S4 slides 17 and 20–22; S5 slide 14; labs/01-scaffold.md §10; runs of the reviewed repository and of `uv sync` in a clone of it (outputs in GNU format)", "slides", "run",
))

# ----- s7 ------------------------------------------------------------------
Q.append(mcq(
    24, "core", ["concept", "read-code"], 7,
    """
    The expense-tracker's `pyproject.toml` contains:

    ```toml
    [project.scripts]
    expenses = "expense_tracker.cli:app"
    ```

    What does this line produce?
    """,
    ("After install, a command `expenses` that runs `app` from `expense_tracker.cli`",
     "Right. Session 5: `expenses`, then module `expense_tracker.cli`, then object `app`."),
    [
        ("A file `expenses.py` in the repository that imports `app` from the package for you",
         "Nothing is added to the repository. A small wrapper is written into the environment (`.venv/bin/expenses`) when the project is installed."),
        ("A dependency on a package called `expenses`, which uv downloads from PyPI on install",
         "Dependencies are listed in `dependencies` under `[project]`. `[project.scripts]` declares the commands this project provides."),
        ("A shortcut called `expenses` that VS Code adds to its built-in terminal",
         "It is an ordinary command in the project's environment: `uv run expenses` works in any terminal, and CI can use it too."),
    ],
    "c",
    """
    Session 4 reads `[project.scripts]` as "what it installs as a command", and session 5 spells it out:
    `expenses` is the command, `expense_tracker.cli` the module, `app` the object. When uv installs the
    project it writes a wrapper named `expenses` into `.venv/bin`; in a real environment that wrapper does
    `from expense_tracker.cli import app` and then calls `app()`. That is why `uv run expenses report`
    works from any folder inside the project.
    """,
    "S4 slide 21; S5 slide 5; .venv/bin/expenses inspected after uv sync", "slides", "source",
))

Q.append(mcq(
    25, "core", ["concept"], 7,
    """
    In the expense-tracker's `pyproject.toml`, what is the `[build-system]` table, with
    `requires = ["hatchling"]`, for?
    """,
    ("It says how the project is built into something installable",
     "Right. The slide's fourth answer: how it is built."),
    [
        ("It lists the development tools that every teammate needs: `ruff`, `mypy` and `pytest`",
         "In the expense-tracker those live under `[dependency-groups]` as `dev`. `[build-system]` names the build tool."),
        ("It defines the steps the CI workflow runs on GitHub after every push",
         "CI's steps are in `.github/workflows/check.yml`, not in `pyproject.toml`."),
        ("It sets which Python versions the project accepts and installs",
         "That is `requires-python` under `[project]`, with `.python-version` telling uv which one to use."),
    ],
    "a",
    """
    Slide 21 reads `pyproject.toml` as four answers: identity (`name`, `version`), what it needs
    (`requires-python`, `dependencies`), what it installs as a command (`[project.scripts]`) and how it is
    built (`[build-system]`). The build system is the tool that turns the code in `src/` into an
    installable package; the expense-tracker uses `hatchling`. You rarely edit it, but it is why `uv sync`
    can install your own project into `.venv`.
    """,
    "S4 slide 21; expense-tracker pyproject.toml", "slides", "source",
))

Q.append(mcq(
    26, "hard", ["read-diff", "read-tool-output"], 7,
    """
    A teammate's last commit changed one line:

    ```diff
     [project.scripts]
    -expenses = "expense_tracker.cli:app"
    +tracker = "expense_tracker.cli:app"
    ```

    You pull and run the command from the README:

    ```console
    $ uv run expenses report
       Building expense-tracker @ file:///home/you/expense-tracker
          Built expense-tracker @ file:///home/you/expense-tracker
    Uninstalled 1 package in 0.59ms
    Installed 1 package in 1ms
    error: Failed to spawn: `expenses`
      cause: No such file or directory (os error 2)
    ```

    What is the right diagnosis?
    """,
    ("The left-hand side is the command's name, so the installed command is now `tracker`",
     "Right. Session 5: rename either side and the command disappears."),
    [
        ("The lockfile no longer matches the project file, so it must be re-locked before running",
         "A real run of `uv sync --locked` still passes after this change: the lockfile records packages and versions, not command names. Re-locking changes nothing."),
        ("The environment was damaged by the rebuild; delete it and run the sync again",
         "The rebuild worked (`Installed 1 package`). A fresh `.venv` would contain the same commands, and `expenses` is not one of them."),
        ("The package folder was renamed, so `expense_tracker.cli` can no longer be imported",
         "The right-hand side, `expense_tracker.cli:app`, did not change. Only the command's name did."),
    ],
    "d",
    """
    In `[project.scripts]` the left-hand side is the command you type, and the right-hand side is the
    module and the object. uv saw `pyproject.toml` change, reinstalled the project (`Uninstalled 1
    package`, `Installed 1 package`) and wrote a wrapper called `tracker` instead of `expenses`. Then it
    could not find any `expenses` to run. `uv run tracker report` would work; the group should decide on
    one name and make the README agree, because the README's commands must work.
    """,
    "S5 slide 5; labs/01-scaffold.md troubleshooting (Failed to spawn); run in a clone of v0.4", "lab", "run",
))

Q.append(mcq(
    27, "exam", ["read-tool-output", "concept"], 7,
    f"""
    A teammate moved the package out of `src/` to the top of the repository "to simplify things". In a
    fresh clone, with nothing installed (there is no `.venv`), you run:

    ```console
    {ind(RUN_FLAT_IMPORT, 4)}
    ```

    What does this show?
    """,
    ("Python found the folder you stand in, installed or not; tests would skip the installed package",
     "Right. This is slide 22's reason for `src/`, shown by a real run."),
    [
        ("Nothing is wrong here: the package is installed correctly, so moving it out of the folder was harmless",
         "Nothing is installed: there is no `.venv` and `uv sync` was never run. The import worked for a different reason."),
        ("`python3` found the project's virtual environment on its own and imported the package from there",
         "A bare `python3` never looks in `.venv`, and here there is no `.venv` at all. It found the folder in the current directory."),
        ("The `src/` folder was unnecessary all along, since imports from the top work without it",
         "Working without installation is the problem, not a benefit: the tests stop proving that the installed package works."),
    ],
    "b",
    """
    Slide 22: without `src/`, `import expense_tracker` finds the folder you are standing in, whether or not
    the package is installed. The printed path is the loose folder in the repository, and nothing was
    installed. With `src/`, the same command fails with `ModuleNotFoundError`; the import works only
    through the installed project (`uv run`), so the tests exercise what a user would get. The move also
    costs marks: CP1 requires the
    `src/` layout, and the partial rubric scores Structure 0 for code outside `src/`.
    """,
    "S4 slide 22; partial-rubric (Structure); run on a flat-layout copy of v0.4", "slides", "run",
))

Q.append(mcq(
    28, "hard", ["read-tool-output"], 7,
    """
    In a clone of the expense-tracker, `uv run expenses --help` prints the usage text. Then:

    ```console
    $ ls src/expense_tracker
    __init__.py  __pycache__  cli.py  report.py
    $ uv run python -m expense_tracker
    /home/you/expense-tracker/.venv/bin/python: No module named expense_tracker.__main__; 'expense_tracker' is a package and cannot be directly executed
    ```

    Which conclusion is right?
    """,
    ("There is no `__main__.py`, which `python -m` needs; the command is a separate door",
     "Right. Slide 20 lists `__main__.py` for exactly this; session 5 calls it the other door."),
    [
        ("The project is not installed yet, so `uv sync` must run before `python -m` can find it",
         "The error comes from `.venv/bin/python`, the project's own environment, and `uv run expenses` works. The project is installed."),
        ("`[project.scripts]` points at the wrong object, which also stops `python -m` from working",
         "`uv run expenses --help` works, so `[project.scripts]` is fine, and it powers the command, not `python -m`."),
        ("`python -m` does not work for code under `src/`; it needs the package at the top level",
         "Installed `src/` code imports normally; with a `__main__.py`, `python -m expense_tracker` would run."),
    ],
    "b",
    """
    The error names exactly what is missing: `expense_tracker.__main__`. Slide 20 lists `__main__.py` as
    the file that makes `python -m expense_tracker` work, and session 5 calls it "the other door", next to
    the installed command from `[project.scripts]`. The demo repository at `v0.4` really has no
    `__main__.py` (your template ships one, which is why it is the file everyone forgets to rename). Two
    entry points, two files: the command needs `[project.scripts]`, `python -m` needs `__main__.py`.
    """,
    "S4 slide 20; S5 slide 6; run in a clone of v0.4", "slides", "run",
))

Q.append(open_q(
    29, "hard", ["concept", "judgement"], 7,
    """
    In your group, Hugo wants to move `src/parking_lot/` to `parking_lot/` at the top of the repository:
    "Then `python3 -c 'import parking_lot'` works even without uv, and the tests pass anyway."
    """,
    [
        part("1", "What changes about how `import parking_lot` behaves if the package sits at the top?", 2,
             "Python then imports the folder in the directory you are standing in, whether or not the project is installed. With `src/`, the import only works once the project is installed.",
             ["Without `src/`, the import finds the local folder in the current directory",
              "This happens whether or not the package is installed (with `src/`, only when installed)"],
             "\"Imports get easier\" restates Hugo's claim without the mechanism. The mark needs the reason: Python looks in the folder you are standing in, so the import succeeds even when nothing has been installed at all."),
        part("2", "Why does that make passing tests less trustworthy?", 2,
             "The tests then exercise the files lying next to them, not the package a user installs. They can pass even when the project is not installed at all, so a problem with what the installed package contains would only surface for a stranger installing from the repository.",
             ["Tests run against the local files, not what a user installs",
              "So a problem with what the installed package contains stays hidden until a stranger installs it"],
             "Answers that say \"tests might fail\" have it backwards: the risk is that tests pass when the installed package is broken. A second common miss is not saying who suffers: the stranger installing from the repository."),
        part("3", "What would the move cost the group in the course's marking?", 1,
             "CP1 requires `src/` layout with the package importable, and the partial rubric scores Structure 0 for \"a script, or code outside `src/`\".",
             ["Names CP1's `src/` layout item, or the partial rubric's Structure criterion (0 for code outside `src/`)"],
             "\"The lecturer prefers `src/`\" is not enough; name where it is marked. CP1's second item checks the `src/` layout with the package importable, and the partial rubric scores Structure 0 for code outside `src/`."),
    ],
    """
    Hugo's argument is the slide's warning turned into a feature. Without `src/`, imports succeed because
    of where you stand, not because the project installs; the tests then prove only that the loose files
    work. The course's marking makes the layout non-negotiable at CP1 and in the partial rubric.
    """,
    "S4 slide 22; S5 slide 14; partial-rubric (Structure)", "slides", "source",
))

# ----- s8 ------------------------------------------------------------------
Q.append(mcq(
    30, "core", ["read-tool-output"], 8,
    f"""
    In a fresh clone of the expense-tracker, without running `uv sync` first, you type:

    ```console
    {ind(RUN_UV_RUN_FRESH, 4)}
    ```

    What did `uv run` do?
    """,
    ("It built the project's environment from `uv.lock`, then ran the installed command",
     "Right. Slide 23: resolve the environment, install what is missing, run the command."),
    [
        ("It installed `typer` and the rest for the whole computer, so any `python3` can import them now",
         "The packages went into the project's new `.venv` (`Creating virtual environment at: .venv`). A bare `python3` still cannot import them."),
        ("It downloaded the newest release of every dependency, ignoring the versions in the lockfile",
         "uv installs the versions recorded in `uv.lock`; that is how every teammate and CI get the same ones."),
        ("It ran the file `src/expense_tracker/cli.py` directly, exactly the way `python3` would",
         "`expenses` is the command that `[project.scripts]` installs. A bare `python3` running the file fails, because it cannot see `typer`."),
    ],
    "c",
    """
    Session 4, slide 23: `uv run` resolves the environment from `pyproject.toml` and `uv.lock`, installs
    what is missing, and runs the command. In a fresh clone everything is missing, so you see it create
    `.venv`, build the project, install 19 packages and only then run `expenses report`. Compare `python
    tracker.py`, which needs the file, the right directory and whatever Python the machine has. Same
    versions for every teammate and for CI.
    """,
    "S4 slide 23; run in a fresh clone of v0.4", "slides", "run",
))

Q.append(mcq(
    31, "exam", ["read-code", "compare"], 8,
    f"""
    `pyproject.toml` says `dependencies = ["typer>=0.12"]`. The committed `uv.lock` contains:

    ```toml
    {ind(LOCK_TYPER, 4)}
    ```

    (followed by download URLs and `sha256` hashes). Which statement is right?
    """,
    ("`pyproject.toml` states a range; `uv.lock` records the exact version chosen, with its hash",
     "Right. Slide 24: the lockfile says exactly which typer, and which of its dependencies, down to the hash."),
    [
        ("The two files disagree (0.12 against 0.27.2), so CI's locked sync is going to fail",
         "0.27.2 satisfies `>=0.12`, so they agree. `--locked` fails only when the lockfile no longer matches what `pyproject.toml` asks for."),
        ("The lockfile is only a download cache, so deleting it changes nothing for anyone",
         "Without it each machine resolves its own versions, and CI's `uv sync --locked` stops with `Unable to find lockfile`."),
        ("The project file pins typer to exactly 0.12, and the lockfile then overrides that pin",
         "`>=0.12` is a range, not a pin. The lockfile does not override it; it records which version in that range was chosen."),
    ],
    "d",
    """
    `pyproject.toml` is where you state what the project accepts: typer 0.12 or newer. `uv.lock` is what
    uv resolved from that: exactly typer 0.27.2, plus exact versions of its own dependencies (`rich`,
    `shellingham`, ...) and a hash for each download. Committing the lockfile is what makes "same versions
    for every teammate and for CI" true. Session 4: "works on my machine" can usually be pinpointed to a
    lockfile that was never committed.
    """,
    "S4 slide 24; expense-tracker uv.lock (v0.4); run of uv sync --locked without uv.lock", "slides", "run",
))

Q.append(mcq(
    32, "beyond", ["read-tool-output", "judgement"], 8,
    f"""
    You add a dependency to `pyproject.toml` by hand:

    ```diff
     dependencies = [
         "typer>=0.12",
    +    "python-dateutil>=2.9",
     ]
    ```

    Before pushing, you run what CI runs first:

    ```console
    {ind(RUN_LOCKED_STALE, 4)}
    ```

    What should you do next?
    """,
    ("Run `uv lock`, then commit `uv.lock` together with `pyproject.toml`",
     "Right. The hint names the fix, and afterwards `uv sync --locked` passes. Committing both files keeps CI's copy in step."),
    [
        ("Delete `uv.lock` and push, so that CI generates a fresh lockfile of its own",
         "With no lockfile, `uv sync --locked` stops with `Unable to find lockfile at uv.lock` (a real run). CI never writes files back to your repository."),
        ("Delete `.venv`, then run `uv sync --locked` again to rebuild the environment",
         "The environment is not involved: uv compared two files and stopped. The same error comes back."),
        ("Reinstall uv, since its resolver seems confused by the new dependency",
         "uv did its job: it noticed that `pyproject.toml` changed and the lockfile did not. The tool is fine; the lockfile is stale."),
    ],
    "a",
    """
    `--locked` means "install exactly what `uv.lock` says, and refuse if `uv.lock` no longer matches
    `pyproject.toml`". You changed `pyproject.toml`, so the lockfile is stale. `uv lock` resolves the new
    dependency and records it (a real run printed `Added python-dateutil v2.9.0.post0` and `Added six
    v1.17.0`); after that `uv sync --locked` passes, and you commit both files together. Lab 01 lists this
    message as the most likely reason a first push goes red.
    """,
    "S4 slide 24; labs/01-scaffold.md §4 and troubleshooting; run in a clone of v0.4", "lab", "run",
))

Q.append(mcq(
    33, "beyond", ["judgement", "concept"], 8,
    """
    Four teammates each change one line of `pyproject.toml`, commit only that file, and push. CI starts
    with `uv sync --locked`. Whose push stays green?
    """,
    ("Cesc renames the command in `[project.scripts]` from `expenses` to `tracker`",
     "Right. Command names are not recorded in the lockfile, so `uv.lock` still matches; a real run of `uv sync --locked` passed."),
    [
        ('Ana bumps the project version from `"0.1.0"` to `"0.2.0"` for the partial',
         "The lockfile records the project's own name and version (the `a953d05` lockfile shows them), so it is now stale; in a real run `--locked` refused."),
        ('Bea adds `"python-dateutil>=2.9"` to the list of dependencies by hand',
         "A new dependency has no entry in the lockfile, so `--locked` refuses until someone runs `uv lock`."),
        ('Dani relaxes `requires-python` so that Python 3.12 is also accepted',
         "The lockfile records the project's `requires-python` and resolves versions for that range; in a real run `--locked` refused."),
    ],
    "c",
    """
    `uv.lock` records the project's own name and version, its `requires-python`, and every dependency
    at its exact resolved version. The 8-line lockfile of `a953d05` already shows the first three. Change
    any of these in `pyproject.toml` and the two files disagree, so CI's `uv sync --locked` refuses until
    someone runs `uv lock` and commits the result. All four cases were run. A command name only decides
    which wrapper goes into `.venv/bin`, so the lockfile is unaffected. The habit that makes this
    question unnecessary: after any edit to `pyproject.toml`, run `uv lock` and commit both files.
    """,
    "S4 slide 24; expense-tracker uv.lock at a953d05; labs/01-scaffold.md §4; runs of uv sync --locked after each edit", "slides", "run",
))

Q.append(mcq(
    34, "exam", ["read-tool-output", "judgement"], 8,
    """
    A teammate changed `.python-version` "to match the Python that Ubuntu ships". After pulling, on your
    Mac, you run:

    ```console
    $ cat .python-version
    3.12
    $ uv sync
    Using CPython 3.12.14
    error: The Python request from `.python-version` resolved to Python 3.12.14, which is incompatible with the project's Python requirement: `>=3.13` (from `project.requires-python`)
    Use `uv python pin` to update the `.python-version` file to a compatible version
    ```

    What should you do next?
    """,
    ("Put `.python-version` back to 3.13, which `requires-python` allows",
     "Right. The file that changed is the file that is wrong, and uv installs Python for you."),
    [
        ("Delete `.venv` and run `uv sync` again, so the environment is built from scratch",
         "uv stopped before creating anything, because the two files ask for incompatible Pythons. A new `.venv` hits the same check."),
        ("Reinstall uv, so that it can find the Python 3.13 already on this machine",
         "uv found exactly what it was asked for, 3.12. The request is wrong, not the tool."),
        ("Run `uv sync --upgrade`, so that the project moves on to a newer Python",
         "`--upgrade` upgrades packages, not the Python request; a real run printed the same error."),
    ],
    "b",
    """
    The error names both sides: `.python-version` asks for 3.12, while `requires-python` under `[project]`
    says the project needs 3.13 or newer. They cannot both hold, so uv stops. The fix belongs in the file
    that changed: put `.python-version` back to 3.13 (the hint's `uv python pin` does that). The teammate's
    reason was wrong too: the course never uses Ubuntu's own Python, because uv installs Python itself, the
    same version for everyone and for CI.
    """,
    "S3 slide 5; S4 slide 21; run in a clone of v0.4 on macOS (download lines trimmed)", "slides", "run",
))

Q.append(mcq(
    35, "exam", ["read-tool-output", "judgement"], 8,
    """
    A teammate added `rich` to the dependencies by editing `pyproject.toml` by hand. After pulling, you run:

    ```console
    $ uv sync
    warning: Failed to parse `pyproject.toml` during settings discovery:
      TOML parse error at line 14, column 5
         |
      14 |     "rich>=13",
         |     ^
      missing comma between array elements, expected `,`

    error: Failed to parse: `pyproject.toml`
      cause: TOML parse error at line 14, column 5
                |
             14 |     "rich>=13",
                |     ^
             missing comma between array elements, expected `,`
    ```

    Which conclusion is right?
    """,
    ("uv could not read `pyproject.toml` and stopped; fix the list near line 14",
     "Right. The message names the file, the line and what the parser expected."),
    [
        ("The lockfile is out of date, and `uv lock` will rewrite it and clear the error",
         "`uv lock` reads `pyproject.toml` first and fails with the same parse error (a real run). The lockfile is not involved yet."),
        ("`rich` is not available for Python 3.13, so an older version must be pinned",
         "uv never got as far as looking up `rich`. A parse error means it could not read the file at all."),
        ("The `.venv` is damaged, so it should be deleted before running `uv sync` again",
         "uv stopped while reading `pyproject.toml`, before it touched the environment. Deleting `.venv` changes nothing."),
    ],
    "d",
    """
    Read the message before acting. It names the file, the line and the column, and says what the parser
    expected: a comma between the elements of a list. Because uv could not read `pyproject.toml`, it did
    nothing else, so neither `.venv` nor `uv.lock` can be the problem. Open the file at the dependencies
    list: the entry before `"rich>=13"` lacks its comma, which the parser only notices when it reaches
    line 14. Fix the file, run `uv lock`, and commit both files.
    """,
    "Sample paper Q1 shape; S4 slide 21; run in a clone of v0.4", "slides", "run",
))

Q.append(open_q(
    36, "exam", ["concept", "judgement"], 8,
    """
    A new teammate asks in the group chat: "Why do we commit `uv.lock`? It is 400 lines nobody reads.
    And why does CI run `uv sync --locked` instead of plain `uv sync`?" Explain in 5–8 lines.
    """,
    [
        part("1", "What does `uv.lock` record that `pyproject.toml` does not?", 2,
             "`pyproject.toml` gives ranges, such as `typer>=0.12`. `uv.lock` records the exact version uv chose for every package, including typer's own dependencies, with a hash for each download.",
             ["Says `pyproject.toml` states acceptable ranges (e.g. `typer>=0.12`)",
              "Says `uv.lock` records the exact resolved versions, including indirect dependencies or hashes"],
             "\"It locks the packages\" restates the name. \"It lists the dependencies\" is also true of `pyproject.toml`; the mark is for the difference: a range versus the exact version chosen from it, for every package including ones you never named, such as `rich` under typer."),
        part("2", "Why must it be committed?", 2,
             "So that every teammate and CI install exactly the same versions with `uv sync`. Without it each machine resolves its own versions, and \"works on my machine\" comes back: the slide says it can usually be pinpointed to a lockfile that was never committed.",
             ["Same versions for every teammate and for CI (reproducibility)",
              "Without it each machine may resolve different versions, so results differ (works on my machine)"],
             "\"Because CI needs it\" is half an answer: say why, namely that it is the only shared record of exact versions. Answers that suggest committing `.venv` instead have it backwards: the environment is rebuilt from the lockfile, never shipped."),
        part("3", "What does `--locked` add in CI?", 2,
             "`uv sync --locked` installs exactly what the lockfile says and fails if `uv.lock` and `pyproject.toml` disagree. So someone who edits `pyproject.toml` and forgets `uv lock`, or forgets to commit the new lockfile, gets a red check instead of a silent difference.",
             ["`--locked` fails when the lockfile and `pyproject.toml` disagree (a stale lockfile)",
              "Contrast: plain `uv sync` would silently re-lock, so CI could test different versions from the committed ones"],
             "Many answers stop at \"it uses the lockfile\"; plain `uv sync` uses it too. The point of `--locked` is that it refuses instead of quietly rewriting the lockfile, so a forgotten `uv lock` turns CI red rather than going unnoticed."),
    ],
    """
    The task asks for the session 4 slide on `uv.lock` in your own words: range versus exact version,
    committed so that everyone and CI share it, and `--locked` as the check that catches a lockfile that
    has fallen out of step. A full answer uses a concrete example (`typer>=0.12` against the exact version
    in the lockfile).
    """,
    "S4 slides 23–24; labs/01-scaffold.md §4", "slides", "source",
))

# ----- s9 ------------------------------------------------------------------
Q.append(mcq(
    37, "beyond", ["read-tool-output", "judgement"], 9,
    """
    Marta added `python-dateutil` to `pyproject.toml`, ran `uv sync` (it installed fine), and all four
    checks passed on her laptop. Then she committed and pushed. Afterwards:

    ```console
    $ git status
    On branch main
    Your branch is up to date with 'origin/main'.

    Changes not staged for commit:
      (use "git add <file>..." to update what will be committed)
      (use "git restore <file>..." to discard changes in working directory)
    	modified:   uv.lock

    no changes added to commit (use "git add" and/or "git commit -a")
    ```

    CI is red at the step `Install dependencies from the lockfile`, and the log shows:

    ```text
    error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.
    ```

    Why was it green for her and red in CI?
    """,
    ("Her plain `uv sync` rewrote `uv.lock`, but she committed only `pyproject.toml`",
     "Right. `modified: uv.lock` is the evidence: the updated lockfile never left her laptop."),
    [
        ("CI runs a different patch release of Python, which resolves different versions",
         "A Python difference would not make uv say the lockfile needs updating. The message is about `uv.lock` against `pyproject.toml`."),
        ("GitHub's package cache was stale, and re-running the job will turn it green",
         "Re-running checks the same commit with the same stale lockfile and fails the same way."),
        ("`python-dateutil` cannot be installed on Linux, which is what CI runs",
         "The step never got as far as installing anything. uv refused because the two files disagree, before any download."),
    ],
    "b",
    """
    Plain `uv sync` does not refuse a stale lockfile: it re-resolves, rewrites `uv.lock` and carries on,
    so her laptop was green. `git status` shows the evidence: `modified: uv.lock`, never staged. CI runs
    `uv sync --locked`, which compares the committed `uv.lock` with the committed `pyproject.toml` and
    refuses. Session 4: "works on my machine" can usually be pinpointed to a lockfile that was never
    committed. The fix: commit `uv.lock` and push.
    """,
    "S4 slide 24; expense-tracker check.yml; runs (laptop clone and clean CI-like clone)", "slides", "run",
))

Q.append(mcq(
    38, "hard", ["read-tool-output", "judgement"], 9,
    """
    Before committing, Pau's terminal showed:

    ```console
    $ git status
    On branch main
    Your branch is up to date with 'origin/main'.

    Changes not staged for commit:
      (use "git add <file>..." to update what will be committed)
      (use "git restore <file>..." to discard changes in working directory)
    	modified:   src/expense_tracker/cli.py

    Untracked files:
      (use "git add <file>..." to include in what will be committed)
    	src/expense_tracker/dates.py

    no changes added to commit (use "git add" and/or "git commit -a")
    ```

    He committed and pushed `cli.py`; all 24 tests pass on his laptop. In your fresh clone,
    `uv sync --locked` succeeds, and `uv run pytest` ends with:

    ```text
    ______________________ ERROR collecting tests/test_io.py _______________________
    ImportError while importing test module '/home/you/expense-tracker/tests/test_io.py'.
    tests/test_io.py:5: in <module>
        from expense_tracker.cli import app
    src/expense_tracker/cli.py:7: in <module>
        from expense_tracker.dates import parse_date
    E   ModuleNotFoundError: No module named 'expense_tracker.dates'
    =========================== short test summary info ============================
    ERROR tests/test_io.py
    !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
    ```

    What is the cause?
    """,
    ("`dates.py` exists only on Pau's laptop: it was untracked, and he never added it",
     "Right. The commit imports a module that is not in the repository."),
    [
        ("Your environment is out of date; delete `.venv` and run the sync again",
         "Your environment was built seconds ago from the committed lockfile. What is missing is a source file, not a package."),
        ("The lockfile does not list your new module, so `uv lock` must be run first",
         "The lockfile records packages and versions, not your own modules, and `uv sync --locked` passed."),
        ("The test is flaky; run `pytest` a few more times until it passes",
         "An import error is deterministic. It fails every time, on every machine that lacks the file."),
    ],
    "c",
    """
    `git status` listed `src/expense_tracker/dates.py` under `Untracked files`, and Pau then staged only
    `cli.py`. So the commit contains an import of a module that is not in the repository. On his laptop
    the file exists and all 24 tests pass; in a clean clone it does not, so collecting `tests/test_io.py`
    fails. Lab 01: a clean clone has no `.venv`, no caches and nothing you forgot to commit. The fix is to
    `git add` the file, commit and push.
    """,
    "labs/01-scaffold.md §10; S3 slide 13; runs (Pau's clone and a clean clone)", "lab", "run",
))

Q.append(mcq(
    39, "hard", ["read-tool-output", "judgement"], 9,
    """
    Jordi never installed uv. To check that the report module at least loads, he runs it with the
    `python3` his Mac came with:

    ```console
    $ python3 --version
    Python 3.9.6
    $ python3 src/expense_tracker/report.py
    Traceback (most recent call last):
      File "/Users/jordi/expense-tracker/src/expense_tracker/report.py", line 56, in <module>
        def largest_expense(expenses: list[Expense]) -> Expense | None:
    TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
    ```

    On his teammates' laptops the same file loads without error under `uv run`, and CI is green. What is
    the best response?
    """,
    ("Install uv and use `uv run`, which brings the Python 3.13 the project requires",
     "Right. Stop bypassing the tool that gives everyone the same Python."),
    [
        ("Rewrite the annotation in the report module so that it also works on his Python 3.9",
         'That bends shared code to suit one laptop. The project declares `requires-python = ">=3.13"`, and CI and every teammate run 3.13.'),
        ("Add `# type: ignore` to line 56 so that the error stops appearing",
         "That comment silences mypy, which is not running here. This is Python itself failing at run time on an old interpreter."),
        ("Delete `.venv` and then run the file with `python3` once more",
         "A bare `python3` does not use `.venv` at all, so deleting it changes nothing about this error."),
    ],
    "d",
    """
    This is the "different Python" kind of works-on-my-machine. Jordi's `python3` is 3.9.6, while
    `pyproject.toml` requires `>=3.13`; on 3.9, writing `Expense | None` in an annotation fails as soon
    as the function is defined. Under `uv run` the same file runs on Python 3.13 and loads fine. uv exists
    to give everyone the same Python and the same packages, so the fix is to stop bypassing it, not to
    change the code for one machine.
    """,
    "S3 slides 3 and 5; S4 slide 23; run with macOS /usr/bin/python3 (3.9.6) and uv run", "slides", "run",
))

Q.append(open_q(
    40, "hard", ["read-tool-output", "judgement"], 9,
    """
    Pau's branch passes all four checks on his laptop. In a fresh clone, where `pyproject.toml` declares
    only `typer>=0.12` under `dependencies`, you install exactly what the lockfile says and run the tests:

    ```console
    $ uv sync --locked
    Using CPython 3.13.15
    Creating virtual environment at: .venv
    Resolved 20 packages in 3ms
    Installed 19 packages in 21ms
    $ uv run pytest
    ```

    ```text
    ______________________ ERROR collecting tests/test_io.py _______________________
    ImportError while importing test module '/home/you/expense-tracker/tests/test_io.py'.
    tests/test_io.py:5: in <module>
        from expense_tracker.cli import app
    src/expense_tracker/cli.py:6: in <module>
        from dateutil import parser
    E   ModuleNotFoundError: No module named 'dateutil'
    =========================== short test summary info ============================
    ERROR tests/test_io.py
    !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
    ```
    """,
    [
        part("1", "Why does `uv sync --locked` succeed although a package is missing?", 2,
             "`--locked` only checks that `uv.lock` agrees with `pyproject.toml`, and it does: neither file mentions `python-dateutil`. uv installed exactly what the two files declare, so by their definition the environment is complete.",
             ["`--locked` checks the lockfile against `pyproject.toml` (consistency), not the code's imports",
              "Notes that `dateutil` is declared in neither file, so nothing disagrees"],
             "\"The lockfile is broken\" is the tempting answer and it is wrong: the two files agree perfectly. Students often think `--locked` checks that everything the code needs is installed; it only checks that the recipe is consistent."),
        part("2", "Why do the tests pass on Pau's laptop?", 1,
             "He installed `python-dateutil` straight into his own `.venv` (for example with `uv pip install`) instead of declaring it, so his environment has a package the repository does not describe.",
             ["Installed by hand into his environment without declaring it in `pyproject.toml`"],
             "\"His computer is different\" is too vague. Name the mechanism: a package in his `.venv` that `pyproject.toml` does not declare, so no environment built from the repository can have it."),
        part("3", "A teammate proposes adding a step to `check.yml` that installs `python-dateutil` by hand before the checks run. Do you accept? Give your reasoning.", 2,
             "No. That makes the referee's machine special instead of fixing the project: a stranger or a teammate following the README would still crash. Declare it with `uv add python-dateutil` (and its stubs with `uv add --dev types-python-dateutil`), which updates `pyproject.toml` and `uv.lock`, commit both, and every install gets it.",
             ["Rejects it: it hides the problem in CI while the project still breaks for anyone installing from the repository",
              "Gives the real fix: declare it with `uv add` and commit `pyproject.toml` and `uv.lock`"],
             "Accepting \"because then CI can pass\" treats the referee as the obstacle. The check exists to prove that a clean machine can install and run the project; patching the check proves nothing. Rejecting without the fix (declare and lock the dependency) earns half."),
    ],
    """
    The sample paper's "read tool output, harder" shape on the anatomy topic. The trap in part 1 is
    believing `--locked` guarantees completeness; it guarantees consistency. Part 3 mirrors sample Q9.3
    ("do you accept `# type: ignore` to get CI green?"): the answer is never to bend the referee. A
    complete fix also declares the stubs: `python-dateutil` ships no type hints, so without
    `types-python-dateutil` the Types step reports `Library stubs not installed for "dateutil"` and CI
    goes red there.
    """,
    "S4 slides 23–24; S8 (uv add --dev); runs (Pau's clone with a hand-installed package, clean clone, mypy without the stubs)", "slides", "run",
))

Q.append(mcq(
    41, "exam", ["read-tool-output", "judgement"], 9,
    f"""
    Nil pushed a commit with a `.env` file holding the group's movie API key, then deleted the file in the
    next commit. The repository is public. Anyone can run:

    ```console
    {ind(RUN_SECRET, 4)}
    ```

    Is the key safe now?
    """,
    ("No: the earlier commit still holds it; treat the key as leaked and replace it",
     "Right. Deleting a file only removes it from later commits."),
    [
        ("Yes: the file is gone from the latest commit, so GitHub no longer shows it",
         "The latest commit lacks the file, but the earlier commit still contains it. A `git clone` copies the whole history, and `git show` prints the key."),
        ("Yes, as soon as the file name is added to the ignore list in `.gitignore`",
         "`.gitignore` stops future mistakes; it does nothing to commits already in the history."),
        ("No, but only members of the group can see the older commits of a repository",
         "The repository is public: its whole history is visible to anyone, which is exactly why nothing secret may go in."),
    ],
    "c",
    """
    The project brief: "I deleted the file" does not remove it from a repository's history. A commit
    records a snapshot; `0948038` removed the file from later snapshots, but `7cd2bd6` still holds it, and
    in a public repository anyone can run `git show 7cd2bd6:.env`. So the key is exposed, and the safe
    response is to treat it as leaked: cancel it with the provider and use a new one that is never
    committed, with `.env` in `.gitignore` so it cannot happen again.
    """,
    "moodle/project-pages.md (Project Brief); run in a local repository", "slides", "run",
))

Q.append(open_q(
    42, "beyond", ["concept", "judgement"], 9,
    """
    Your group's repository is public. On Monday a teammate committed and pushed `config.py` with a real
    API key in it. On Tuesday they deleted the file, committed, pushed, and wrote in the chat: "Fixed, the
    key is gone."
    """,
    [
        part("1", "Is the key still exposed? Explain using what a commit records.", 2,
             "Yes. Each commit records a snapshot of the files. Tuesday's commit removes the file from later snapshots, but Monday's commit still contains it, and anyone can show that commit, because the repository is public.",
             ["Says yes, the key is still exposed",
              "Explains that history keeps every earlier commit, so the deleted file can still be read (for example with `git show <commit>:config.py`)"],
             "\"It is in the history\" without saying what that means earns one point. The second point needs the mechanism: a commit is a snapshot, deleting creates a new snapshot without the file, and the old one is untouched and public."),
        part("2", "What should the group do now? Name two actions.", 2,
             "Treat the key as leaked: cancel it with the provider and create a new one. Keep the new key out of the repository, for example in a `.env` file listed in `.gitignore`.",
             ["Revoke or replace the key (treat it as compromised)",
              "Keep secrets out of the repository from now on (an ignored file, a `.gitignore` entry, never committed)"],
             "\"Delete the commit\" or \"make the repository private\" misses that the key may already have been copied; once public, it is compromised. Adding `.gitignore` alone protects the future but not the leaked key."),
        part("3", "Why does the course make repositories public despite this risk? Give one of its reasons.", 1,
             "A public repository is a portfolio piece, it makes copying visible rather than tempting, and the tooling (automated checks, container hosting) is free. The price is never putting anything personal or secret in it.",
             ["Gives one of the brief's three reasons: portfolio, copying visible rather than tempting, free tooling"],
             "\"So the lecturer can see it\" is not one of the brief's reasons; a private repository could be shared with the lecturer too. Name one of the three: a portfolio piece, copying made visible, or free tooling."),
    ],
    """
    Part 1 is straight from the brief ("I deleted the file" does not remove it from history). Part 2 is the
    obvious next consequence: a key that has been public must be replaced, not hidden. Part 3 checks you
    know why the course accepts the risk.
    """,
    "moodle/project-pages.md (Project Brief)", "slides", "source",
))

Q.append(mcq(
    43, "hard", ["read-tool-output", "judgement"], 9,
    """
    Sunday 18 October, 23:50. Lena's group tagged `v0.5` and pushed the tag, then saw CI red on that commit
    (at `Formatting`). She fixed it, pushed to `main`, and the new commit is green. Now:

    ```console
    $ git log --oneline -3
    5bf3483 (HEAD -> main, origin/main) Fix the failing check
    2b1b151 (tag: v0.5) Add the report command
    f6f3ce0 Add weighted averages
    ```

    If nothing else happens before 23:59, what does the marker see?
    """,
    ("The red tagged commit, so Tests is capped at 1 unless she moves the tag and pushes it",
     "Right. The rubric marks the tag, and a fix after the tag only counts once the tag is moved."),
    [
        ("The green commit, because marking uses the newest commit on `main`",
         "The rubric marks `main` at the `v0.5` tag, and the tag still points at `2b1b151`. A fix pushed after the tag does not count."),
        ("No effect on the mark: CI is the referee, not the judge, so its colour is irrelevant",
         "CI is not a criterion, but the rubric's gate is explicit: red at the tag caps Tests at 1, whatever else is true."),
        ("The green commit, because a tag moves forward with each new commit on `main`",
         "A tag is a permanent name for one commit and never moves by itself. That is why the rubric gives steps to move it."),
    ],
    "b",
    """
    A tag names one commit and stays there; `git log` shows `tag: v0.5` on `2b1b151`, below the fix. The
    partial rubric marks `main` at `v0.5`, and its CI gate says that if the check is red on the `v0.5`
    commit, Tests is capped at 1, and a fix pushed after the tag does not count. The rubric's procedure:
    fix, push, wait for a green tick on the new commit, then move the tag onto it and push the tag. What
    counts is where `v0.5` points at 23:59.
    """,
    "partial-rubric (The CI gate; If CI is red on the tag); labs/01-scaffold.md §9; run in a local repository", "slides", "run",
))

Q.append(open_q(
    44, "exam", ["judgement", "concept"], 9,
    """
    It is Sunday 18 October, 23:30. Your group's `v0.5` tag is on a commit whose `check` run is red at the
    `Formatting` step. A teammate says: "Leave the tag. The marker will obviously look at our latest
    commit, and anyway CI is only the referee, not the judge."
    """,
    [
        part("1", "What happens to your mark if you leave the tag where it is? Answer the teammate's two claims.", 2,
             "The rubric marks `main` at the `v0.5` tag, not the latest commit. CI is not a criterion itself, but red CI on the tagged commit caps the Tests criterion at 1 out of 3, whatever else is true.",
             ["Marking happens at the commit the `v0.5` tag points to, not the latest commit",
              "Red CI at the tag caps the Tests criterion at 1, even though CI is not marked itself"],
             "Answers that only say \"we lose marks\" do not say which criterion or why. The second claim is half right: CI is not marked, which is exactly why the rubric uses it as a gate on Tests."),
        part("2", "Describe in words the steps to put it right before 23:59.", 3,
             "Open the red run and read the failing step's log, and reproduce it locally by running the same checks. Fix it, commit and push to `main`, then wait for a green tick on that new commit. Only then move `v0.5` onto the green commit, push the tag, and check that it points there.",
             ["Find what failed: read the failing step's log, or run the same checks locally",
              "Fix, commit and push to `main`, then wait until CI is green on the new commit",
              "Move the tag onto the green commit and push it (a fix after the tag counts only once the tag moves)"],
             "Moving the tag before CI has gone green on the new commit risks tagging another red commit; the rubric says wait for the green tick first. Forgetting to push the moved tag leaves GitHub's `v0.5` where it was."),
    ],
    """
    The partial rubric's CI gate in practice. Part 1 tests the two facts students mix up: marking is at the
    tag, and CI, though not marked, caps Tests. Part 2 is the rubric's own four-step procedure in your
    words. No commands are needed, only the order and the reason for it.
    """,
    "partial-rubric (The CI gate; If CI is red on the tag)", "slides", "source",
))

# ----- added after review (s7, s4, s8) ------------------------------------------
Q.append(mcq(
    45, "hard", ["read-tool-output", "judgement"], 7,
    f"""
    Oriol writes his first test for the expense-tracker's report and saves it next to the code, as
    `src/expense_tracker/test_largest.py`, "so each test sits beside what it tests". He wrote it to
    fail first. Before he added the file, the suite had 24 tests. Now:

    ```console
    {ind(RUN_TEST_IN_SRC, 4)}
    ```

    The project's `pyproject.toml` contains:

    ```toml
    [tool.pytest.ini_options]
    testpaths = ["tests"]
    ```

    What is the best conclusion?
    """,
    ("pytest never ran his file, which would also ship to users: move it to `tests/`",
     "Right. `testpaths` points pytest at `tests/`, and everything under `src/expense_tracker/` is part of the package that gets built and installed."),
    [
        ("His test passed on the first run, so the red step can be skipped this time",
         "The count is still 24, the same as before his file existed, so his test never ran. A green bar that contains no new test proves nothing."),
        ("pytest cannot import code from under `src/`, so it skipped his file without a warning",
         "Installed code under `src/` imports normally; that is how `tests/test_report.py` imports `report`. Run by name, his file is collected and fails (a real run). pytest was simply pointed at `tests/`."),
        ("The `.venv` still holds the old test suite; delete it and run `uv sync` again",
         "`.venv` holds installed packages, not test files; pytest reads tests from the repository. Rebuilding it changes nothing about where pytest looks."),
    ],
    "d",
    """
    There are two clues. The count did not change, and `testpaths = ["tests"]` tells pytest where to
    look, so it never collects a file under `src/`. Run by name, his test fails, exactly as he intended.
    The layout says the same thing for a deeper reason. Slide 20: `tests/` mirrors `src/`, so the tests
    for `report.py` live in `tests/`. Slide 22: `src/` holds the deployable code, and the tests in
    `tests/` are typically not included in the build. A wheel built with his file in place really does
    contain `expense_tracker/test_largest.py`. Moved to `tests/test_largest.py`, it is collected, goes
    red, and stays out of what users install.
    """,
    "S4 slides 20 and 22; S8 (red, green, refactor); expense-tracker v0.4 pyproject.toml; runs (pytest with the file under src/, by name, after the move; wheel build)",
    "slides", "run",
))

Q.append(sort_q(
    46, "core", ["concept"], 4,
    """
    The survival-kit commands from the setup lab and lab 01, in the order you might type them. Sort each
    by what it changes, and where.
    """,
    [
        ("reports", "Reports only: changes nothing"),
        ("laptop", "Changes your laptop only"),
        ("github", "Sends something to GitHub"),
    ],
    [
        ("`git clone git@github.com:esade-swdev-2026/<your-group>.git`", "laptop",
         "Copies the repository, with its whole history, onto your laptop. GitHub is only read."),
        ("`git switch -c setup/<your-github-username>`", "laptop",
         "Makes a new branch and moves you onto it, in your local repository. GitHub has no such branch until you push."),
        ("`git status`", "reports",
         "Tells you what is untracked, not staged, staged, or committed but not pushed. It records nothing."),
        ("`git add setup-reports/`", "laptop",
         "Stages the folder for the next commit. Nothing is in the history yet, and nobody else can see it."),
        ('`git commit -m "add setup report"`', "laptop",
         "Records the staged change as a commit on your laptop. Teammates and CI see it only after a push."),
        ("`git push -u origin setup/<your-github-username>`", "github",
         "Sends the branch and its commits to GitHub, where the `check` workflow runs on them."),
        ('`git tag -a v0.1 -m "Scaffolded project"`', "laptop",
         "Names one commit in your local repository. Until the tag is pushed, GitHub has no `v0.1` to mark."),
        ("`git push origin v0.1`", "github",
         "Sends the tag to GitHub. Checkpoints are marked at the tag, so this is the step that makes it count."),
    ],
    """
    Only `push` sends anything to GitHub. Everything else happens in the repository on your laptop:
    `clone` copies it down with its whole history, `switch -c` makes a branch, `add` stages, `commit`
    records and `tag` names a commit. All of it is invisible to teammates, CI and the marker until you
    push. `git status` changes nothing; it tells you which of those states each change is in. That is why
    an unpushed commit, or a tag that was never pushed, counts for nothing at a checkpoint: lab 01 says a
    missing tag means there is nothing to mark.
    """,
    "S3 slides 10–13; labs/00-setup.md (Push your first file); labs/01-scaffold.md §9; moodle/project-pages.md (Every checkpoint is a git tag)",
    "slides", "source",
))

Q.append(mcq(
    47, "core", ["read-tool-output", "concept"], 8,
    f"""
    At tag `v0.0` the expense-tracker is a script. Alice is in her home folder, one level above the
    clone, and runs:

    ```console
    {ind(RUN_SCRIPT_WRONG_DIR, 4)}
    ```

    From inside `expense-tracker/` the same command prints the report. What does this show?
    """,
    ("A script needs the file and the right folder; an installed command needs the project",
     "Right. Slide 23: `python tracker.py` needs the file and the right directory, while `uv run expenses report` needs the project and works from any folder inside it."),
    [
        ("Her Python installation is broken and has to be reinstalled before the script can run",
         "Python started and printed its own error naming the path it tried. It looked in the folder Alice is standing in, where there is no `tracker.py`."),
        ("The last commit deleted `tracker.py`, so she has to restore the file from the history",
         "The same command works one folder down. The file exists; Python simply looked in the wrong directory."),
        ("The script needs `uv sync` first, because a bare `python3` reads the project's lockfile",
         "A bare `python3` never reads `pyproject.toml` or `uv.lock`. At `v0.0` there is not even a project to sync."),
    ],
    "c",
    """
    Session 4, slide 23 contrasts two ways to run the same code. `python tracker.py` runs a file, so it
    needs that file in the current directory, plus whatever Python and packages the machine happens to
    have; the error names the path Python tried, `/home/alice/tracker.py`. `uv run expenses report` runs
    an installed command: uv finds the project from any folder inside it, builds the environment from
    `pyproject.toml` and `uv.lock`, and runs it. Packaging the script, from `a953d05` on, is what made
    the second form possible.
    """,
    "S4 slide 23; S5 slide 4; run on expense-tracker v0.0 (path rewritten)", "slides", "run",
))

Q.append(mcq(
    48, "exam", ["concept", "judgement"], 2,
    """
    The day before the first checkpoint, Pol cannot get Docker Desktop to start on his laptop. He has
    WSL2, VS Code, uv, git and his SSH key working, and he can push to the group's repository. He asks
    whether this blocks the group's CI run and his work this month. Which answer is right?
    """,
    ("No: session 3 says Docker is not needed until session 16; CI today runs ruff, mypy and pytest through uv",
     "Right. Slide 5: Docker \"is not needed until session 16\", and the `check` workflow installs uv and Python on GitHub's runner. He should skip Docker for now."),
    [
        ("Yes: CI runs every push inside a Docker container, so Docker has to work on his laptop first",
         "CI runs on GitHub's own machine, which installs uv and Python itself. Nothing in the `check` workflow needs Docker, on his laptop or anywhere else."),
        ("Yes: without Docker `uv.lock` cannot be created, so `uv sync --locked` fails in CI",
         "uv builds the lockfile from `pyproject.toml` by itself. Docker plays no part until the sessions on containers."),
        ("No: CI runs only on GitHub, so none of the six tools on his laptop matters to it",
         "The other tools matter: uv produces the lockfile CI checks, git and the SSH key get his commits to GitHub, and the workflow only runs once they arrive."),
    ],
    "a",
    """
    Session 3's table gives each of the six tools one job. Docker runs a project in a container and, in
    the slide's words, is "not needed until session 16: install it today if it is painless, skip it if it
    fights". The referee is the CI run on GitHub, and the course's `check` workflow uses uv to install
    Python and the locked dependencies, then runs ruff, mypy and pytest. A Docker problem therefore blocks
    nothing yet. The other five tools each sit on the path from his laptop to a green run.
    """,
    "S3 slides 3, 5; labs/00-setup.md; expense-tracker 0e05065 (workflow)", "slides", "source",
))

# ---------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------

module: dict[str, Any] = {
    "id": MID,
    "order": 3,
    "module": "M1",
    "title": "Setup, environments and the anatomy of a project",
    "sessions": [3, 4],
    "predicted": False,
    "sources": [
        "slides-session-3",
        "slides-session-4 (slides 17–27)",
        "labs/00-setup.md",
        "labs/01-scaffold.md",
        "moodle/project-pages.md",
        "partial-rubric",
        "expense-tracker a953d05",
        "expense-tracker v0.4 (pyproject.toml, uv.lock, .gitignore, .github/workflows/check.yml)",
    ],
    "summary_md": md(
        """
        Session 3 set up one environment for everyone, because "works on my machine" is the problem this
        course exists to solve, and made a CI check on GitHub (`ruff`, `mypy`, `pytest`) the referee.
        Session 4 took a project apart file by file: what a script lacks, what `pyproject.toml`,
        `uv.lock`, `.gitignore`, `src/` and `tests/` are each for, and why `uv run expenses report`
        (installed) beats `python tracker.py` (merely present). This module teaches the six tools, what a
        virtual environment really is, the git survival kit, the eight troubleshooting cases of lab 00,
        and how to diagnose the usual ways a project works on one laptop and fails everywhere else. It
        matters because every checkpoint is marked at a tag, as a clean clone shows it, and a red
        referee at the `v0.5` tag caps the Tests mark.
        """
    ),
    "exam_focus_md": md(
        """
        - A real uv error (a TOML parse error, `--locked` refusing a stale lockfile, a Python version clash)
          and "what should you do next?", with distractors such as deleting `.venv`, reinstalling uv or
          `--upgrade`.
        - A "works on my machine" story: green on one laptop, red in CI or in a clean clone. You name the
          cause (lockfile not committed, file never added, package installed by hand, a different Python)
          and the fix.
        - Reading a project tree or `pyproject.toml`: which file does which job, what `[project.scripts]`
          produces, what a stranger would need to install and run it.
        - Why the `src/` layout, why `.venv` is ignored but `uv.lock` is committed, why CI runs
          `uv sync --locked`.
        - Survival-kit git output (`git status`, a rejected push): what has been recorded where, and what
          to do next.
        - A public repository and a leaked key: whether deleting the file removes it from history.
        - The partial rubric's CI gate: red at the `v0.5` tag caps Tests at 1, and a fix after the tag
          counts only once the tag is moved.
        """
    ),
    "sections": sections,
    "terms": [{"term": t, "definition_md": d, "section_ref": sec(s)} for t, d, s in terms],
    "traps": traps,
    "flashcards": [
        {"id": f"{MID}-f{i:02d}", "front_md": f, "back_md": b, "kind": k, "section_ref": sec(s)}
        for i, (f, b, k, s) in enumerate(cards, start=1)
    ],
    "questions": Q,
}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(module, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {OUT} ({len(Q)} questions)")


if __name__ == "__main__":
    main()
