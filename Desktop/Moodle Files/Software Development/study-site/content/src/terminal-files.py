"""Generate content/terminal-files.json: session 9, the terminal (paths, files, permissions).

Every terminal transcript below was produced by a real run of bash in a fake home folder
(/home/alice) and is shown in GNU coreutils format, as on the course's Ubuntu/WSL machines.
Evidence (commands, raw BSD output, GNU-format output) lives in the work folder
scratchpad/work/terminal-files/final/*.cmds, *.raw and *.out.
Run:  uv run python content/src/terminal-files.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MID = "terminal-files"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def opt(text: str, why: str, correct: bool = False) -> dict[str, Any]:
    return {"text_md": text, "correct": correct, "why_md": why}


def mcq(
    n: int,
    level: str,
    skills: list[str],
    sec: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    options: list[dict[str, Any]],
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"{MID}-q{n:02d}",
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": stem.strip(),
        "options": options,
        "explanation_md": explanation.strip(),
        "section_ref": f"{MID}-s{sec}",
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }


def part(
    label: str, prompt: str, marks: int, model: str, rubric: list[str], weak: str
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
    n: int,
    level: str,
    skills: list[str],
    sec: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"{MID}-q{n:02d}",
        "type": "open",
        "level": level,
        "skills": skills,
        "stem_md": stem.strip(),
        "parts": parts,
        "lines": "5–8",
        "explanation_md": explanation.strip(),
        "section_ref": f"{MID}-s{sec}",
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }


def sort_q(
    n: int,
    level: str,
    skills: list[str],
    sec: int,
    source: str,
    origin: str,
    verified: str,
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"{MID}-q{n:02d}",
        "type": "sort",
        "level": level,
        "skills": skills,
        "stem_md": stem.strip(),
        "categories": [{"id": i, "label": label} for i, label in categories],
        "items": [{"text_md": t, "category": c, "why_md": w} for t, c, w in items],
        "explanation_md": explanation.strip(),
        "section_ref": f"{MID}-s{sec}",
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }


def q(n: int) -> str:
    return f"{MID}-q{n:02d}"


def s(n: int) -> str:
    return f"{MID}-s{n}"


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

SECTIONS: list[dict[str, Any]] = [
    {
        "id": s(1),
        "heading": "Terminal, shell and operating system",
        "body_md": """
Session 9 starts by separating three things that people lump together as "the terminal".

| | What it is | Example |
|---|---|---|
| Terminal | The window. It shows text and sends your keystrokes | Windows Terminal, GNOME Terminal |
| Shell | The program inside it that reads a line and runs it | `bash`, `zsh` |
| Operating system | What actually creates files and starts programs | the Linux kernel |

When you type `touch notes/todo.txt` and press Enter, the terminal sends the characters, the shell reads the line, cuts it into words at the spaces and asks the operating system to start the program `touch`, and `touch` in turn asks the operating system to create the file.

**Terminal and shell swap independently. Your scripts depend on the shell.** You can change the window and keep `bash`, and nothing about your scripts changes. Change the shell and things can. That is why lab 00 cares which shell you run: WSL's Ubuntu gives you `bash`, every recent macOS gives you `zsh`, and the `uv` installer edits the startup file of your shell (`~/.bashrc` or `~/.zshrc`). Even error messages belong to the shell: for the same problem, `bash` prints `bash: ./run.sh: Permission denied` and `zsh` prints `zsh: permission denied: ./run.sh`.

**Why a 50-year-old interface survived.** The slide gives four reasons:

- It composes. Small programs, joined by pipes (session 10).
- It scripts. Whatever you typed once, you can save and run again.
- It works over `ssh`. Every server you will ever touch has one, and nothing else.
- CI is a terminal. The check workflow is a list of commands someone else's computer types for you: `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src tests`, `uv run pytest`.

The slide's summary is the line to remember: a GUI is for doing something once; a terminal is for doing it a hundred times. Running the checks before every push is the hundred-times case, and it is why Friday's `scripts/check.sh` exists. The slide closes with a note on the present: the current trend in AI-assisted development drops IDEs (integrated development environments) in favour of terminals.

One word, two ideas. In session 7, the imperative shell was the outer layer of your code (`cli.py`, which reads files, prints and exits). In session 9, the shell is the program that reads your command line. Keep them apart in an answer.
""",
        "key_points": [
            "Terminal = the window; shell = the program that reads your line and runs it (`bash`, `zsh`); operating system = what creates files and starts programs.",
            "Terminal and shell swap independently. Your scripts depend on the shell.",
            "A GUI is for doing something once. A terminal is for doing it a hundred times.",
            "CI is a terminal: the check workflow is a list of commands someone else's computer types for you.",
        ],
        "exam_note_md": "Expect a scenario where one of the three changes (a new terminal app, a Mac teammate on `zsh`) and you judge what still works, or a 'why commands, not clicks' question tied to CI.",
        "source_ref": "S9 slides 5–6; labs/00-setup.md (macOS zsh, uv on PATH)",
        "check": [q(1), q(2)],
    },
    {
        "id": s(2),
        "heading": "One tree under /: where am I, what is here",
        "body_md": """
Linux has one tree of folders with one root, written `/`. Everything is under `/`. There are no drive letters. Your home folder is `/home/alice` (on macOS, `/Users/alice`), and `~` is short for it, as is `$HOME`. The course keeps every project in `~/code`:

```text
/
├── home/
│   └── alice/              ← your home, ~
│       └── code/
│           └── my-project/
│               ├── .git/
│               ├── src/
│               └── pyproject.toml
├── etc/
└── usr/
```

On WSL, your Windows disk is part of the same tree, at `/mnt/c`. A project under `/mnt/c/Users/...` lives on the Windows filesystem: lab 00 warns that every `git` and `uv` operation there is several times slower, and section 8 shows that permissions do not work there either. Keep projects in your Linux home; `pwd` should start with `/home/`, not `/mnt/`.

Two commands answer the questions you ask most, "where am I?" and "what is here?" (slide 9):

```console
$ pwd
/home/alice/code/expense-tracker
$ ls
LICENSE  README.md  expenses.csv  pyproject.toml  src  tests  uv.lock
$ ls -a
.  ..  .git  .github  .gitignore  .python-version  LICENSE  README.md  ...
```

`ls` hides names that start with a dot. `.git` is one: that is why you never see it, and why it is safe. `ls -a` shows everything, and answers lab 09's first question: the entries that appear only with `-a` all start with a dot. Two of them are in every folder: `.` is the folder you are in, and `..` is its parent. The CI workflow is hidden the same way: in your group repository, `ls -la .github/workflows` shows `check.yml`.

The tree is also what `find` searches (lab 09, exercise 4). `find src tests -name "*.py"` lists the expense-tracker's six Python files at v0.4, three in each folder. `find` does not skip dot folders: run from the project root, `find . -name "test_*" -type f` also walks into `.venv`, where uv installed packages that ship their own test files, and, in a fresh clone right after `uv sync`, prints 44 paths instead of 3 (more once pytest has left `__pycache__` files in `tests`). Names repeat across the tree (`find ~/code -name tests -type d` finds one `tests` per project); the full path is what tells two files apart.

Lab 09 then asks you to find every file in your group repository whose name contains `check`. In the expense-tracker after `uv sync`, `find . -name "*check*" -type f` prints 24 paths. Only two are outside `.venv`: the CI workflow, `./.github/workflows/check.yml`, and git's own `./.git/hooks/push-to-checkout.sample`, both inside hidden folders that plain `ls` never shows. The rest are mypy's own files, such as `checker.py`. Read the full path of each match, or start the search where you expect the file: `find .github -name "*check*"` prints only the workflow.
""",
        "key_points": [
            "Everything is under `/`. No drive letters; on WSL the Windows disk is `/mnt/c`.",
            "`~` is your home: `/home/alice` on Linux and WSL, `/Users/alice` on macOS.",
            "`ls` hides names that start with a dot; `ls -a` shows them, plus `.` (this folder) and `..` (its parent).",
            "`find` walks the whole tree from where you start it, hidden folders included.",
        ],
        "exam_note_md": "A listing where something seems missing (`.git`, `.github`) is a classic: the answer is the leading dot, not a broken repository.",
        "source_ref": "S9 slides 8–9; labs/09-terminal.md exercises 1 and 4; labs/00-setup.md (WSL home)",
        "check": [q(5), q(6)],
    },
    {
        "id": s(3),
        "heading": "Absolute and relative paths, and moving with cd",
        "body_md": """
A path names a file by the folders you pass through to reach it. There are two kinds, and the first character tells you which (slide 10):

| Path | Means |
|---|---|
| `/home/alice/code/expense-tracker` | Absolute. Starts at `/`. Same from anywhere |
| `src/expense_tracker/cli.py` | Relative. Starts here |
| `../project-template` | Up one level, then down |
| `~/code` | Your home, then `code` |

"Here" means the current directory, the one `pwd` prints. A relative path is read from there, so the same relative path names different files in different places. `..` is one level up, so `../..` is two.

Lab 09 walks the expense-tracker with relative paths only:

```console
$ cd src/expense_tracker
$ pwd
/home/alice/code/expense-tracker/src/expense_tracker
$ cd ../../tests
$ pwd
/home/alice/code/expense-tracker/tests
$ cd ..
$ pwd
/home/alice/code/expense-tracker
```

`cd ../../tests` climbs two levels, to the project root, then goes down into `tests`. Then the lab uses absolute paths and shortcuts:

```console
$ cd ~/code
$ cd "$HOME/code/expense-tracker/src"
$ cd -
/home/alice/code
$ cd
$ pwd
/home/alice
```

`cd -` goes back to where you just were (and prints it). `cd` alone goes home. `echo $HOME` prints `/home/alice`, the same as `pwd` right after a plain `cd`. These answer lab 09's questions 3 and 4.

The lab's path questions, for alice: the absolute path of `report.py` is `/home/alice/code/expense-tracker/src/expense_tracker/report.py`. The relative path from the project root is `src/expense_tracker/report.py`; from `tests` it is `../src/expense_tracker/report.py`; from `~` it is `code/expense-tracker/src/expense_tracker/report.py`.

Two spellings catch people out. The project's name uses a hyphen (`expense-tracker`: the repository, and the `name` in `pyproject.toml`); the Python package uses an underscore (`expense_tracker`, the folder under `src/`). These are the two spellings session 5 set up, because Python names cannot contain hyphens. A path has to match the real name character for character.
""",
        "key_points": [
            "Absolute paths start at `/` and mean the same file from anywhere. Relative paths start here.",
            "`..` is one level up; `cd -` goes back to where you just were; `cd` alone goes home.",
            "From the project root, `report.py` is `src/expense_tracker/report.py`; from `tests`, `../src/expense_tracker/report.py`.",
        ],
        "exam_note_md": "Track `pwd` line by line on paper. Each wrong option in a 'where are you now?' question is one misread shortcut.",
        "source_ref": "S9 slides 10, 12; S3 slide 12; labs/09-terminal.md exercise 1",
        "check": [q(7), q(8), q(9)],
    },
    {
        "id": s(4),
        "heading": "Reading a path in an error",
        "body_md": """
Slide 10's rule: most "file not found" errors are the wrong current directory. Run `pwd` first.

A program reads a relative path from the folder you are standing in, not from the folder where its code lives. Here alice is in `tests` and asks for `expenses.csv`:

```console
$ pwd
/home/alice/code/expense-tracker/tests
$ uv run expenses report expenses.csv
could not read expenses.csv
$ echo $?
1
$ ls expenses.csv
ls: cannot access 'expenses.csv': No such file or directory
$ cd ..
$ uv run expenses report expenses.csv
Expense report for expenses.csv
----------------------------------------
groceries              6401.78
```

Slide 11 asks: which `expenses.csv`? The one in the folder you are standing in, not the one next to the code. `uv run` found the project (it looks upwards for `pyproject.toml`), but the program then opened `tests/expenses.csv`, which does not exist. The message and the exit code 1 are the program failing well (session 7): it names what it could not read. Your job is to read that path against `pwd`. Nothing is broken and nothing needs reinstalling. Either stand in the right folder, or give a path that is right from where you are, such as `../expenses.csv`.

Slide 11 itself shows the opposite slip: `pwd` prints `/home/alice/code`, one level too high, `ls expenses.csv` says `cannot access`, and `cd expense-tracker` fixes it. Too high or too deep, the diagnosis is the same: read the path against `pwd`.

The same rule applies to files a program writes. `expenses add` writes to `data/expenses.csv`, a relative path, so running it from `tests` creates `tests/data/expenses.csv`.

Slide 12's time savers also keep you out of wrong paths:

- **Tab** completes names. If it does not complete, the name is wrong or ambiguous. Treat it as a check, not only as less typing.
- **↑** brings back the last command, so you change one word instead of retyping the line.
- **Ctrl-R** searches your history for an older command.
- **Ctrl-C** stops the program that is running.
- **`cd -`** goes back to where you just were; **`cd`** alone goes home.
""",
        "key_points": [
            'Most "file not found" errors are the wrong current directory. Run `pwd` first.',
            "A relative path in an error is relative to where you stand, not to where the code is.",
            "If Tab does not complete a name, the name is wrong or ambiguous.",
            "Ctrl-C stops the running program; Ctrl-R searches your history.",
        ],
        "exam_note_md": "The teacher's distractors for this transcript are the careless reflexes: reinstall, `chmod 777`, edit the code. The right move is always `pwd`, then the right folder.",
        "source_ref": "S9 slides 10–12; expense-tracker v0.4 cli.py",
        "check": [q(12), q(15), q(44)],
    },
    {
        "id": s(5),
        "heading": "Make, copy, move, remove",
        "body_md": """
Five commands manage files. Slide 14 runs them in order:

```console
$ mkdir notes
$ touch notes/todo.txt
$ cp notes/todo.txt notes/todo-backup.txt
$ cp -r notes notes-old
$ mv notes/todo-backup.txt notes/old.txt
$ rm notes/old.txt
```

- `mkdir` makes a folder; `touch` makes an empty file.
- `cp` copies a file. `cp -r` copies a folder and everything in it.
- `mv` moves, and is also rename: moving a file to a new name renames it.
- `rm` removes. It does not ask and there is no bin. What it removes is gone.

After those six lines, `notes` holds only `todo.txt`, and `notes-old` holds `todo-backup.txt` and `todo.txt`: `cp -r` copied the folder as it was at that moment, and the later `mv` and `rm` only touched `notes`.

Without `-r`, `cp` refuses a folder and copies nothing:

```console
$ cp reports reports-copy
cp: -r not specified; omitting directory 'reports'
```

`mv` follows one rule with two outcomes. If the target is an existing folder, the file goes inside it. If it is not, the target becomes the new name. So `mv reports/notes.txt reports/2025`, when `reports/2025` does not exist, silently turns `notes.txt` into a file called `2025`. Writing the folder with a trailing slash (`reports/2025/`), as in the table below, makes `mv` refuse with an error instead.

Lab 09, exercise 2, one command per task (in `~/lab09`):

| Task | Command |
|---|---|
| Copy `expenses.csv` into `reports/archive/` as `expenses-backup.csv` | `cp reports/expenses.csv reports/archive/expenses-backup.csv` |
| Move `notes.txt` into `reports/2025/` | `mv reports/notes.txt reports/2025/` |
| Rename it to `summary.txt` | `mv reports/2025/notes.txt reports/2025/summary.txt` |
| Copy the whole `reports` folder | `cp -r reports reports-copy` |

Then the part with no undo: after `rm -r reports-copy`, `ls reports-copy` says `ls: cannot access 'reports-copy': No such file or directory`, and there is no bin to get it back from.

The lab's habit for data: never edit `expenses.csv` in place, because it is a fixture the course relies on. Copy it, then work on the copy.
""",
        "key_points": [
            "`mv` is also rename. `cp -r` copies a folder and everything in it.",
            "`rm` does not ask and there is no bin. What it removes is gone.",
            "`mv` into a folder that does not exist renames instead of moving.",
            "Copy the data, never edit the original.",
        ],
        "exam_note_md": "Questions here are 'predict the result': follow the files line by line, as they are at each moment, rather than the commands.",
        "source_ref": "S9 slide 14; labs/09-terminal.md exercise 2",
        "check": [q(17), q(18)],
    },
    {
        "id": s(6),
        "heading": "rm is permanent: the space and the star",
        "body_md": """
Slide 15 shows two lines that differ by one space:

```console
$ rm -r notes-old
$ rm -r notes-old/ *
```

The first removes the folder `notes-old`. The second removes `notes-old/` and every file in the current directory. Two things combine.

**The space splits arguments.** The shell cuts the line into words at spaces. `notes-old/*` is one argument (everything inside `notes-old`); `notes-old/ *` is two: the folder, and a separate `*`.

**The shell expands `*` before `rm` runs.** `*` stands for every name in the current folder, except names that start with a dot. `rm` never sees the star; it receives the list. With `-r`, folders in that list go too.

Lab 09 asks you to reason out `rm -r reports-copy *` typed in `~/lab09`, where `ls` shows `reports  reports-copy`. The shell turns it into `rm -r reports-copy reports reports-copy`. `rm` removes `reports-copy`, then `reports` with everything in it, then complains that `reports-copy` is no longer there:

```console
$ rm -r reports-copy *
rm: cannot remove 'reports-copy': No such file or directory
$ ls
$ ls -a
.  ..
```

The only message looks like a failure, but the damage is done and the folder is empty. In a project folder, `.git`, `.github` and `.gitignore` would survive, because `*` skips dot names, while `src`, `tests` and `pyproject.toml` would not. Whatever you had pushed can be cloned again from GitHub; uncommitted work is gone.

The slide's habits:

- `ls` the exact path before you `rm` it. Then press ↑ and swap `ls` for `rm`, so what you checked is exactly what you delete.
- `rm -i` asks first. Use it when you are tired.
- Never `rm -rf` with a variable you have not printed. An empty variable turns `rm -rf "$DIR/"*` into `rm -rf /*`.
""",
        "key_points": [
            "The shell expands `*` to every name here before `rm` runs; `rm` never sees the star.",
            "A space turns one argument into two: `notes-old/*` is not `notes-old/ *`.",
            "`ls` the exact path first, then press ↑ and swap `ls` for `rm`.",
            "`rm -i` asks first; never `rm -rf` with a variable you have not printed.",
        ],
        "exam_note_md": "Lab 09 says 'do not run it, reason it out': expect the same on paper. Say who expands `*` (the shell) and what the list contains.",
        "source_ref": "S9 slide 15; labs/09-terminal.md exercise 2 Q7",
        "check": [q(21), q(22)],
    },
    {
        "id": s(7),
        "heading": "Reading permissions in ls -l",
        "body_md": """
`ls -l` prints one line per entry (slide 17):

```console
$ ls -l
-rw-rw-r-- 1 alice alice  1193 Oct 11 17:07 README.md
-rw-rw-r-- 1 alice alice 15221 Oct 11 17:07 expenses.csv
drwxrwxr-x 3 alice alice    60 Oct 11 17:07 src
```

Left to right: the type and permissions, a link count you can ignore, the owner, the group, the size in bytes, the date of the last change, and the name.

On a Mac, `ls -l` may show an `@` after the permission letters (`-rw-r--r--@`). Lab 09 says it marks extended attributes; ignore it. The listings in this module follow the slide's Linux format.

The first ten characters are the part to read carefully:

```text
-  rw-  rw-  r--
d  rwx  rwx  r-x
│   │    │    └── everyone else
│   │    └─────── your group
│   └──────────── you (the owner)
└──────────────── type: - file, d directory
```

The first character is the type: `-` for a file, `d` for a directory. That answers lab 09's question "which entries are folders?" without guessing from names or sizes. Then come three groups of three, always in the order owner, group, everyone else. In each group, `r` is read, `w` is write and `x` is execute; a `-` means that permission is missing.

For a folder, `x` means you may enter it. Without `x`, even the owner cannot go in or reach the files inside, whatever `r` and `w` say:

```console
$ ls -ld reports
drw-rw-r-- 2 alice alice 4096 Oct 13 10:12 reports
$ cd reports
bash: cd: reports: Permission denied
$ cat reports/notes.txt
cat: reports/notes.txt: Permission denied
```

So the slide's listing says: alice (the owner) and members of the group `alice` can read and write `README.md` and `expenses.csv`; everyone else can only read them; nobody can execute them. `src` is a folder everyone may enter. On Ubuntu each user gets a group of their own, which is why owner and group are both `alice`.

When a question shows `ls -l` output, read the first character, then the three groups, then answer what the scenario cares about: who can change this, and can it be run?
""",
        "key_points": [
            "First character: `-` file, `d` directory. Then owner, group, everyone else, three letters each.",
            "`r` read, `w` write, `x` execute; for a folder, `x` means you can enter it.",
            "Read the line for the question asked: who can change it, and can it run?",
        ],
        "exam_note_md": "Listings in questions are in GNU format, like the slide's. Read the first character before anything else.",
        "source_ref": "S9 slide 17; labs/09-terminal.md exercise 1 Q2",
        "check": [q(26), q(28)],
    },
    {
        "id": s(8),
        "heading": "Permission denied: chmod +x, ./ and PATH",
        "body_md": """
Slides 18–19 are the session's most common surprise:

```console
$ cat hello.sh
#!/usr/bin/env bash
echo hello
$ ./hello.sh
permission denied: ./hello.sh
$ ls -l hello.sh
-rw-rw-r-- 1 alice alice 31 Oct 11 17:07 hello.sh
```

There is no `x`. Nobody said this file is a program. A new file never gets execution permissions, whether you make it with `touch`, with `printf ... > run.sh` as lab 09 does, or in VS Code. The fix is to say it:

```console
$ chmod +x hello.sh
$ ls -l hello.sh
-rwxrwxr-x 1 alice alice 31 Oct 11 17:07 hello.sh
$ ./hello.sh
hello
```

`chmod +x` is a statement that a file is a program. (The slide's message comes from `zsh`; `bash` says `bash: ./hello.sh: Permission denied`.)

**Why `./`?** `./` means "this folder": run the `hello.sh` that is here. Without it, the shell does not look in the current folder; it searches the folders listed in `PATH` (where `uv`, `git` and `ls` live). Lab 09 makes you try it: after `chmod +x run.sh`, `./run.sh` prints `report ready`, but a bare `run.sh` gives `run.sh: command not found` (plain `bash`, without Ubuntu's helper, prints `bash: run.sh: command not found`).

**`bash run.sh` is a different thing.** It starts `bash` and hands it the file to read, so it needs only `r`; it is how session 3's `bash scripts/setup-check.sh` runs, with or without `x`. `./run.sh` asks to run the file itself, and that needs `x`. Slide 20 assumes the second way: a CI step that runs `./scripts/check.sh` needs the bit committed.

**Not every file should be a program.** In the expense-tracker, `ls -l src/expense_tracker` shows `__init__.py`, `cli.py` and `report.py` without `x`: none can be run directly. That is right for Python modules: the package imports them, and importing only needs `r`. The program is `expenses`, which uv builds from `[project.scripts]` into `.venv/bin` with the `x` bit set; `uv run expenses` runs that.

**Where chmod does nothing.** On WSL, a project under `/mnt/c` shows every file as `rwxrwxrwx`, and `chmod` silently does nothing. Keep projects in your Linux home, `~/code/...` (the same reason `uv` and `git` are faster there). Check: `pwd` should start with `/home/`, not `/mnt/`.

**CI needs the bit too.** Friday's `scripts/check.sh` depends on this: in CI it needs the `x` bit, and git remembers it. After `chmod +x scripts/check.sh`, `git diff` shows `old mode 100644` and `new mode 100755`; you commit and push that like any other change, and every fresh clone, CI's included, gets a runnable script.
""",
        "key_points": [
            "No `x`, no run. `chmod +x` is a statement that a file is a program.",
            "A new file never gets execute permission.",
            "`./` means this folder; without it the shell only searches `PATH`.",
            "On WSL, `chmod` silently does nothing under `/mnt/c`: keep projects in `~/code`.",
            "git remembers the `x` bit, and CI needs it on `scripts/check.sh`.",
        ],
        "exam_note_md": "The open-question version is 'explain to a teammate': name the missing `x`, say what `chmod +x` states, explain `./`, and reject 777.",
        "source_ref": "S9 slides 18–20; labs/09-terminal.md exercise 3; S3 slide 9 (bash scripts/setup-check.sh)",
        "check": [q(30), q(31), q(45)],
    },
    {
        "id": s(9),
        "heading": "Numbers instead of letters: 644, 755, 600, 777",
        "body_md": """
`chmod` also takes numbers. r = 4, w = 2, x = 1. Add them per group of three, in the usual order owner, group, everyone else (slide 21):

| Number | Letters | Typical use |
|---|---|---|
| 644 | `rw-r--r--` | A normal file |
| 755 | `rwxr-xr-x` | A script or a folder |
| 600 | `rw-------` | A private key |
| 777 | `rwxrwxrwx` | Almost never the answer |

So `rwxr-xr-x` is 4+2+1, 4+1, 4+1 = 755, and `rw-------` is 4+2, 0, 0 = 600: lab 09's question 4.

Each row is a judgement about who needs what. A normal file: you edit it, others may read it, nobody runs it. A script or a folder: everyone may run or enter it, only you change it. A private key: nobody but you may even read it; `ssh-keygen` creates `~/.ssh/id_ed25519` as 600 for that reason, and `ssh` refuses a private key that others can read.

Lab 09 then sets 600 on the script:

```console
$ chmod 600 run.sh
$ ls -l run.sh
-rw------- 1 alice alice 40 Oct 13 10:12 run.sh
$ ./run.sh
bash: ./run.sh: Permission denied
$ cat run.sh
#!/usr/bin/env bash
echo "report ready"
```

You can no longer run it (no `x`), but you can still read it with `cat` (the owner kept `r`).

**Why 777 is almost never the answer.** `chmod 777` makes the error go away and the problem worse. "Permission denied" on a script means one bit is missing, the `x`. 777 adds it, and also gives every user on the machine permission to change the file. On a script that CI runs, or a key that proves who you are, that is the opposite of what you want. Add the one bit that is missing (`chmod +x`, or 755) and nothing else.

**A few more tools.** `man ls` opens the manual (`q` quits) and `ls --help` is shorter. `whoami`, `date`, `uname -a`, `df -h`, `top` and `nano` exist too. The slide is plain about them: you may look these up when they are needed; they are not examined as recall. The mid-term asks what a command does in a scenario, never what a letter stands for.
""",
        "key_points": [
            "r = 4, w = 2, x = 1, added per group: 755 = `rwxr-xr-x`, 644 = `rw-r--r--`, 600 = `rw-------`.",
            "644 a normal file, 755 a script or folder, 600 a private key.",
            "`chmod 777` makes the error go away and the problem worse.",
            "`man` and `--help` exist so you do not have to memorise flags.",
        ],
        "exam_note_md": "Conversions come inside a judgement: which number fits this file, and why the tempting one (777, or 600 on a script) is wrong.",
        "source_ref": "S9 slides 21–22; labs/09-terminal.md exercise 3",
        "check": [q(38), q(41)],
    },
]

# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------

TERMS = [
    (
        "Terminal",
        "The window: it shows text and sends your keystrokes. Windows Terminal and GNOME Terminal are examples.",
        1,
    ),
    (
        "Shell",
        "The program inside the terminal that reads a line and runs it: `bash` on WSL and Linux, `zsh` on macOS. It also splits the line at spaces and expands `*` before any program starts.",
        1,
    ),
    (
        "Operating system",
        "What actually creates files and starts programs. On WSL and Linux, the Linux kernel.",
        1,
    ),
    (
        "Root (`/`)",
        "The top of the one tree that holds every file. Absolute paths start there. There are no drive letters.",
        2,
    ),
    (
        "Home folder (`~`)",
        "Your own folder: `/home/alice` on Linux and WSL, `/Users/alice` on macOS. `~` and `$HOME` both mean it, and `cd` alone goes there.",
        2,
    ),
    (
        "`/mnt/c`",
        "Where WSL shows your Windows C: drive. `git` and `uv` are slow there and `chmod` silently does nothing; keep projects in `~/code`.",
        2,
    ),
    (
        "Hidden file",
        "A name that starts with a dot, such as `.git` or `.github`. `ls` hides it, `ls -a` shows it, and `*` does not match it.",
        2,
    ),
    (
        "`.` and `..`",
        "`.` is the folder you are in; `..` is its parent. `./run.sh` means the `run.sh` in this folder.",
        2,
    ),
    (
        "Current directory",
        "The folder you are standing in, printed by `pwd`. Relative paths are read from it, for reading and for writing.",
        3,
    ),
    (
        "Absolute path",
        "A path that starts at `/`, such as `/home/alice/code/expense-tracker`. It names the same file from anywhere.",
        3,
    ),
    (
        "Relative path",
        "A path that starts here, such as `src/expense_tracker/cli.py` or `../tests`. What it names depends on the current directory.",
        3,
    ),
    (
        "Tab completion",
        "Tab completes a file or folder name as you type. If it does not complete, the name is wrong or ambiguous.",
        4,
    ),
    (
        "Wildcard `*`",
        "On its own, `*` stands for every name in the current folder except names that start with a dot; `notes-old/*` stands for every name inside `notes-old`. The shell expands it into a list before the command runs.",
        6,
    ),
    (
        "Permission string",
        "The first ten characters of an `ls -l` line: the type (`-` file, `d` directory), then `r`, `w`, `x` for the owner, the group and everyone else.",
        7,
    ),
    (
        "Execute permission (`x`)",
        "On a file: it may be run as a program. On a folder: you may enter it. A new file never gets it.",
        7,
    ),
    (
        "`chmod`",
        "Changes permissions, with letters (`chmod +x run.sh`) or numbers (`chmod 755 run.sh`).",
        8,
    ),
    (
        "`PATH`",
        "The list of folders the shell searches for a command typed without a path. The current folder is not in it, which is why you type `./run.sh`.",
        8,
    ),
    (
        "File mode in git",
        "git records whether a file is executable (`100755`) or not (`100644`). A fresh clone, CI's included, gets the mode that was committed.",
        8,
    ),
    (
        "Permission numbers",
        "Permissions as three digits, one per group, with r = 4, w = 2, x = 1: 644, 755, 600, 777.",
        9,
    ),
]

TRAPS = [
    '"The terminal runs my script." The terminal is only the window. The shell (`bash`, `zsh`) reads and runs your line, and the operating system creates files and starts programs.',
    '"There is no `.git`, so the clone is broken." `ls` hides names that start with a dot; `ls -a` shows `.git`.',
    '"File not found means the file is missing or the program is broken." Most of the time you are in the wrong folder: relative paths are read from where you stand. Run `pwd` first.',
    '"A program reads files from the folder its code is in." It reads (and writes) relative paths from the current directory: `expenses add` run in `tests` creates `tests/data/expenses.csv`.',
    '"`rm -r old *` only removes `old`." The space makes `*` its own argument, and the shell expands it to every name in the folder before `rm` runs.',
    '"I can get it back from the bin." `rm` has no bin and no undo. Only your own copy or a committed version brings it back.',
    '"Permission denied, so `chmod 777`." Only the `x` was missing. 777 also gives everyone write permission: it makes the error go away and the problem worse.',
    '"`run.sh` is right here, so typing `run.sh` should run it." Without `./`, the shell only searches the folders in `PATH`, and the current folder is not one of them.',
    '"No error, so `chmod` worked." Under `/mnt/c` on WSL, `chmod` silently does nothing. Check with `ls -l`, and keep projects in `~/code`.',
    '"It runs on my laptop, so it runs in CI." CI clones what git recorded. If the `x` bit of `scripts/check.sh` was never committed, CI says Permission denied.',
    '"`bash run.sh` works, so the `x` bit does not matter." `bash run.sh` only reads the file, which needs `r`. Running it by its own name, as CI runs `./scripts/check.sh`, needs `x`.',
]

FLASHCARDS = [
    (
        "Terminal, shell, operating system: one line each.",
        "Terminal: the window that shows text and sends keystrokes. Shell: the program that reads a line and runs it (`bash`, `zsh`). Operating system: what creates files and starts programs (the Linux kernel).",
        "recall",
        1,
    ),
    (
        "Your teammate swaps Windows Terminal for another terminal app. Do your `bash` scripts change?",
        "No. Terminal and shell swap independently; scripts depend on the shell, which is still `bash`.",
        "concept",
        1,
    ),
    (
        '"The shell" in session 9 vs "imperative shell" in session 7?',
        "Session 9: the program that reads your command line (`bash`, `zsh`). Session 7: the outer layer of your code (`cli.py`) that reads files, prints and exits.",
        "distinction",
        1,
    ),
    (
        "Four reasons the 50-year-old terminal survived.",
        "It composes (pipes), it scripts (save and rerun), it works over `ssh` on every server, and CI is a terminal.",
        "recall",
        1,
    ),
    (
        'What does "CI is a terminal" mean?',
        "The check workflow is a list of commands someone else's computer types for you. What you can type, CI can repeat.",
        "concept",
        1,
    ),
    (
        "A GUI vs a terminal, in the slide's words.",
        "A GUI is for doing something once. A terminal is for doing it a hundred times.",
        "distinction",
        1,
    ),
    (
        "Where is your Windows C: drive inside WSL, and why not keep projects there?",
        "At `/mnt/c`. `git` and `uv` are slower there and `chmod` silently does nothing; keep projects in `~/code`.",
        "recall",
        2,
    ),
    (
        "Why do you never see `.git` with `ls`?",
        "`ls` hides names that start with a dot. `ls -a` shows it. That is also why it is safe.",
        "concept",
        2,
    ),
    (
        "What are `.` and `..`?",
        "`.` is the folder you are in; `..` is its parent. Both appear in `ls -a` in every folder.",
        "recall",
        2,
    ),
    (
        'Right after `uv sync` in a fresh clone, why does `find . -name "test_*" -type f` list 44 files, not 3?',
        "`find` walks the whole tree, hidden folders included: it also searches `.venv`, where installed packages ship their own test files.",
        "reading",
        2,
    ),
    (
        "Absolute vs relative path.",
        "Absolute starts at `/` and means the same file from anywhere. Relative starts here, from the folder `pwd` prints.",
        "distinction",
        3,
    ),
    (
        "`pwd` is `/home/alice/code/expense-tracker/src/expense_tracker`. Where does `cd ../../tests` take you?",
        "`/home/alice/code/expense-tracker/tests`: two levels up to the project root, then into `tests`.",
        "reading",
        3,
    ),
    (
        "`cd -` vs `cd` alone.",
        "`cd -` goes back to where you just were (and prints it). `cd` alone goes home.",
        "distinction",
        3,
    ),
    (
        "A program says it cannot find a file. First command?",
        '`pwd`. Most "file not found" errors are the wrong current directory.',
        "concept",
        4,
    ),
    (
        "`could not read expenses.csv` while standing in `tests/`. Which file did the program look for?",
        "`tests/expenses.csv`: a relative name is read from the folder you stand in, not from where the code is.",
        "reading",
        4,
    ),
    (
        "Tab does not complete a name. What does that tell you?",
        "The name is wrong or ambiguous. Check with `ls` before pressing Enter.",
        "concept",
        4,
    ),
    (
        "`cp` vs `cp -r` vs `mv`.",
        "`cp` copies a file; `cp -r` copies a folder and everything in it; `mv` moves, and is also rename.",
        "distinction",
        5,
    ),
    (
        "What happens to a file after `rm`?",
        "It is gone. `rm` does not ask and there is no bin.",
        "concept",
        5,
    ),
    (
        "`mv notes.txt reports/2025` when `reports/2025` does not exist?",
        "`notes.txt` is renamed to a file called `2025`; `mv` only moves into folders that exist.",
        "reading",
        5,
    ),
    (
        "In `~/lab09` (holding `reports` and `reports-copy`), what does `rm -r reports-copy *` remove?",
        "Both folders: the shell expands `*` to every name here, so `rm` gets `reports-copy reports reports-copy`.",
        "reading",
        6,
    ),
    (
        "Who expands `*`, and when?",
        "The shell, before the command runs. The command receives the list of names, never the star.",
        "concept",
        6,
    ),
    (
        "The three `rm` habits from slide 15.",
        "`ls` the exact path, then ↑ and swap `ls` for `rm`; `rm -i` when tired; never `rm -rf` with a variable you have not printed.",
        "recall",
        6,
    ),
    (
        "Read `-rw-rw-r--` aloud.",
        "A file; owner read and write; group read and write; everyone else read only. Nobody can execute it.",
        "reading",
        7,
    ),
    (
        "What does `x` mean on a folder?",
        "Permission to enter it (and reach the files inside).",
        "concept",
        7,
    ),
    (
        "Why does `./hello.sh` say permission denied, and what is the fix?",
        "There is no `x`: nobody said this file is a program, and a new file never gets it. `chmod +x hello.sh`.",
        "concept",
        8,
    ),
    (
        "What does `./` mean, and why is it needed?",
        "This folder. Without it, the shell searches only the folders in `PATH`, and the current folder is not one of them.",
        "concept",
        8,
    ),
    (
        "Lab 09: which files in `src/expense_tracker` can you run directly, and why is that right?",
        "None has `x`. They are modules the package imports; the program is `expenses`, which uv installs in `.venv/bin` with `x`.",
        "concept",
        8,
    ),
    (
        "How does CI get the `x` bit of `scripts/check.sh`?",
        "git remembers it: commit the mode change (`100644` to `100755`), and every fresh clone gets a runnable script.",
        "concept",
        8,
    ),
    (
        "644, 755, 600, 777: typical use of each.",
        "644 a normal file; 755 a script or a folder; 600 a private key; 777 almost never the answer.",
        "recall",
        9,
    ),
    (
        "`rwxr-xr-x` and `rw-------` as numbers.",
        "755 and 600 (r = 4, w = 2, x = 1, added per group).",
        "recall",
        9,
    ),
]

# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------

QUESTIONS: list[dict[str, Any]] = []
add = QUESTIONS.append

# --- s1 ------------------------------------------------------------------
add(
    sort_q(
        1,
        "core",
        ["concept"],
        1,
        "S9 slide 5; labs/00-setup.md (macOS zsh)",
        "slides",
        "source",
        """
Session 9 separates three things people lump together as "the terminal". Put each item under the one it belongs to.
""",
        [
            ("terminal", "Terminal (the window)"),
            ("shell", "Shell (reads the line and runs it)"),
            ("os", "Operating system (creates files, starts programs)"),
        ],
        [
            (
                "Windows Terminal, or GNOME Terminal",
                "terminal",
                "Window programs: they show text and send your keystrokes, and you can swap one for another.",
            ),
            (
                "`bash` on WSL's Ubuntu",
                "shell",
                "`bash` is the program that reads each line you type and runs it.",
            ),
            (
                "`zsh`, the default on every recent macOS",
                "shell",
                "Another shell. It is why lab 00 sends Mac users to `~/.zshrc` rather than `~/.bashrc`.",
            ),
            (
                "The Linux kernel",
                "os",
                "The slide's example of the operating system: what actually creates files and starts programs.",
            ),
            (
                "Splits `rm -r notes-old/ *` at the spaces and turns `*` into a list of names",
                "shell",
                "Cutting the line into arguments and expanding `*` happen in the shell, before any program runs.",
            ),
            (
                "Actually creates `notes/todo.txt` on the disk when `touch` asks for it",
                "os",
                "`touch` asks the operating system to create the file; neither the window nor the shell writes to the disk itself.",
            ),
            (
                "Can be replaced by another app without changing what your scripts do",
                "terminal",
                "Terminal and shell swap independently. Scripts depend on the shell, not on the window.",
            ),
            (
                "Shows text and sends your keystrokes",
                "terminal",
                "Word for word, the slide's definition of the terminal.",
            ),
        ],
        """
The slide's table has three rows. The terminal is the window (Windows Terminal, GNOME Terminal). The shell is the program inside it that reads a line and runs it (`bash` on WSL and Linux, `zsh` on macOS). The operating system is what actually creates files and starts programs (the Linux kernel). Two consequences follow. Terminal and shell swap independently, so changing the window changes nothing about your scripts. And anything that happens to your command line before a program starts, such as splitting it at spaces or expanding `*`, is the shell's doing.
""",
    )
)

add(
    mcq(
        2,
        "exam",
        ["concept", "judgement"],
        1,
        "S9 slide 5",
        "slides",
        "source",
        """
Your group's `scripts/check.sh` starts with `#!/usr/bin/env bash`. A teammate on Windows replaces Windows Terminal with a different terminal app. Inside it she still opens WSL's Ubuntu, where `bash` runs as before. She asks whether the script needs changing. What do you tell her?
""",
        [
            opt(
                "No. The terminal is only the window; the script depends on the shell, and that is still `bash`.",
                "Right: terminal and shell swap independently, and scripts depend on the shell. Nothing that runs the script has changed.",
                True,
            ),
            opt(
                "Yes. Each terminal app runs scripts in its own way, so the script must be tested and adapted again.",
                "This treats the window as the thing that runs commands. The terminal only shows text and sends keystrokes; the shell runs the script.",
            ),
            opt(
                "Yes. A new terminal app means a new operating system underneath, so file paths will be different.",
                "The operating system is still WSL's Ubuntu with the Linux kernel. Changing the window changes neither the OS nor the tree under `/`.",
            ),
            opt(
                "No. Scripts depend only on the operating system, so neither the window nor the shell matters.",
                "Right verdict, wrong reason. The slide says your scripts depend on the shell: a script written for `bash` can behave differently under another shell.",
            ),
        ],
        """
Session 9 splits the everyday word "terminal" into three: the terminal (the window), the shell (the program that reads a line and runs it) and the operating system (what creates files and starts programs). The slide's conclusion is the one tested here: terminal and shell swap independently, and your scripts depend on the shell. Only the window changed. The shell is still `bash`, so `check.sh` behaves exactly as before. Option d reaches the same verdict with a reason that contradicts the slide; session 8's advice for checking your answers applies: judge your reasons, not the letter.
""",
    )
)

add(
    mcq(
        3,
        "exam",
        ["concept", "judgement"],
        1,
        "S9 slide 6",
        "slides",
        "source",
        """
Before each push, a teammate runs the four checks by clicking buttons in VS Code's sidebar. He says writing them down as commands in `scripts/check.sh` is a waste of time. Which argument from session 9 answers him best?
""",
        [
            opt(
                "Typed commands run faster than clicked buttons, so the four checks finish sooner and he can push more often.",
                "Speed is not the slide's argument. The same tools run either way; what differs is whether the steps can be repeated exactly.",
            ),
            opt(
                "A GUI is for doing something once, a terminal for a hundred times; CI types the same saved commands on every push.",
                "Right: the terminal scripts (type it once, save it, run it again) and CI is a terminal, so the commands you write down are what the referee runs.",
                True,
            ),
            opt(
                "VS Code's buttons cannot run ruff, mypy or pytest at all, so his clicks are not really checking anything.",
                "Not the point: the editor can run these tools through its extensions. The problem is that clicks cannot be saved, shared or typed by CI.",
            ),
            opt(
                "The terminal works over `ssh`, so with commands he could log in to GitHub's machines and run the checks there himself.",
                "Working over `ssh` is a real reason the terminal survived, but nobody logs in to CI by hand. CI types the commands itself.",
            ),
        ],
        """
The slide gives four reasons a 50-year-old interface survived: it composes (small programs joined by pipes), it scripts (whatever you typed once you can save and run again), it works over `ssh` (every server has one), and CI is a terminal (the check workflow is a list of commands someone else's computer types for you). Its one-line summary answers the teammate: a GUI is for doing something once, a terminal is for doing it a hundred times. Checks before every push are the hundred-times case, and only commands can be saved in `check.sh` and typed identically by CI.
""",
    )
)

add(
    open_q(
        4,
        "core",
        ["concept", "compare"],
        1,
        "S9 slides 3, 5–6",
        "slides",
        "source",
        """
A teammate who joined the group late says: "The terminal is just an old-fashioned way of clicking. I will do everything from VS Code's menus, and CI can do what it wants." Answer him in 5–8 lines.
""",
        [
            part(
                "1",
                "Explain the difference between the terminal, the shell and the operating system, with an example of each.",
                2,
                "The terminal is the window that shows text and sends my keystrokes, such as Windows Terminal. The shell is the program inside it that reads a line and runs it: `bash` on WSL, `zsh` on a Mac. The operating system, the Linux kernel, actually creates files and starts programs.",
                [
                    "Terminal: the window that shows text and sends keystrokes, with an example (Windows Terminal, GNOME Terminal)",
                    "Shell: the program that reads a line and runs it (`bash`, `zsh`); operating system: what creates files and starts programs (Linux kernel)",
                ],
                '"The terminal is where you type commands and the shell is the same thing" loses the distinction the slide makes. Naming examples without saying what each one does earns half. Calling VS Code the shell confuses an editor with the program that reads command lines. Each of the three needs its job, not only a name.',
            ),
            part(
                "2",
                "Give two reasons from session 9 why the course still works in a terminal.",
                2,
                "It scripts: what I type once can be saved and run again, which is what `scripts/check.sh` is. And CI is a terminal: the check workflow is a list of commands someone else's computer types for me.",
                [
                    "One of the slide's reasons, explained: it composes (pipes), it scripts (save and rerun), it works over `ssh`, CI is a terminal",
                    "A second, different reason from that list, explained",
                ],
                '"It is faster" or "professionals use it" are opinions, not the slide\'s reasons. Listing the four reasons as bare words ("pipes, ssh") without saying what each one gives you scores less than explaining two. Reading "works over ssh" as "works offline" is a common slip: it means every remote server can be used through it.',
            ),
            part(
                "3",
                "Answer his last point in one sentence.",
                1,
                "CI does not do what it wants: it types the same commands I would type, on a machine none of us owns, and a red check at v0.5 caps our tests mark at 1.",
                [
                    "CI runs the same commands as the terminal (it is the referee), so what you can type and repeat is what gets checked"
                ],
                '"CI is just a GitHub thing" misses that the check workflow is commands typed by another computer. "CI will pass anyway" forgets that it runs the same ruff, mypy and pytest he would run, without his clicks.',
            ),
        ],
        """
A "compare and explain" question on the opening of session 9. Part 1 is the three-row table: terminal, shell, operating system, each with its job and an example. Part 2 needs two of the four reasons on slide 6 (composes, scripts, `ssh`, CI is a terminal), each with what it gives you. Part 3 ties the terminal to the referee: the check workflow is a list of commands someone else's computer types for you, and slide 3 adds the stake, since a red check on the v0.5 tag caps the tests criterion at 1. Full marks need jobs, not just names.
""",
    )
)

# --- s2 ------------------------------------------------------------------
add(
    mcq(
        5,
        "core",
        ["read-tool-output", "concept"],
        2,
        "S9 slide 9",
        "slides",
        "run",
        """
A teammate clones the group repository and runs `ls`:

```console
$ ls
LICENSE  README.md  pyproject.toml  scripts  src  tests  uv.lock
```

She messages you: "There is no `.git` folder, so the clone is broken. I'll run `git init`." What do you reply?
""",
        [
            opt(
                "Run `git init`: a clone without a visible `.git` folder has no history, so it needs a new one.",
                "The clone is fine. Acting on the symptom before checking the diagnosis is the careless move; the history is already there, hidden.",
            ),
            opt(
                "`.git` exists only on GitHub; her copy receives the history the first time she pushes.",
                "`git clone` copies a repository down with its history (session 3's survival kit). The history lives in her local `.git`.",
            ),
            opt(
                "`.git` lives in her home folder and is shared by all the repositories she has cloned.",
                "Each repository has its own `.git` inside its folder, as the slide's tree shows under `my-project/`.",
            ),
            opt(
                "`.git` is there, but hidden: `ls` hides names that start with a dot. `ls -a` will show it.",
                "Right: `.git` starts with a dot, so `ls` hides it. That is why you never see it, and why it is safe.",
                True,
            ),
        ],
        """
Slide 9: `ls` hides names that start with a dot. `.git` is one: that is why you never see it, and why it is safe. In the same folder, `ls -a` lists `.git`, `.github`, `.gitignore` and `.python-version` as well, plus `.` and `..`. The teammate's reasoning is the pattern the teacher's distractors are built on: a symptom (nothing visible) is read as a broken tool, and a fix is applied before the diagnosis is checked. One extra command, `ls -a`, settles it.
""",
    )
)

add(
    mcq(
        6,
        "exam",
        ["read-tool-output", "judgement"],
        2,
        "labs/09-terminal.md exercise 4; S9 slide 9",
        "lab",
        "run",
        """
In lab 09's stretch exercise, alice runs `find` in a fresh clone of the expense-tracker where she has only run `uv sync` so far. Its `tests` folder holds three test files:

```console
$ find . -name "test_*" -type f | wc -l
44
$ find . -name "test_*" -type f | head -5
./tests/test_report.py
./tests/test_io.py
./tests/test_duplicates.py
./.venv/lib/python3.13/site-packages/mypyc/test/test_pprint.py
./.venv/lib/python3.13/site-packages/mypyc/test/test_rarray.py
```

Why 44 and not 3?
""",
        [
            opt(
                "`find` counts every test function inside the matching files, not the files themselves.",
                "`find` matches names in the tree and never opens files. Each line of its output is one path.",
            ),
            opt(
                "From `.`, `find` also walked into the hidden `.venv`, where installed packages ship test files.",
                "Right: the extra paths are under `./.venv/lib/...`. Unlike `ls`, `find` does not skip names that start with a dot.",
                True,
            ),
            opt(
                "`find` also searched the old versions of each test file that git keeps inside the hidden `.git` folder.",
                "git stores old versions under hashed object names, not as `test_*.py` files, and none of the paths shown is under `.git`.",
            ),
            opt(
                "`tests/` holds 41 hidden copies of the test files, which plain `ls` never shows.",
                "A hidden copy would start with a dot, so it could not match `test_*`; the extra paths shown are under `./.venv`.",
            ),
        ],
        """
`find` searches a tree, starting from the folder you give it; `.` is the folder you are in. It does not hide dot names the way `ls` does, so it walks into `.venv`, the virtual environment uv created, where mypy and mypyc ship their own test files whose names match `test_*`. Lab 09's exercise 4 is about exactly this: a name repeats across the tree, and the full path is what tells two files apart. To count only the project's tests, start where they live and match the source files: `find tests -name "test_*.py" -type f` prints the three. After `uv run pytest`, `tests/__pycache__` also holds compiled copies named `test_*.pyc`, which the bare `"test_*"` pattern would count.
""",
    )
)

# --- s3 ------------------------------------------------------------------
add(
    mcq(
        7,
        "exam",
        ["predict-output"],
        3,
        "S9 slides 10, 12; labs/09-terminal.md exercise 1",
        "lab",
        "run",
        """
alice types these five commands, one after another:

```bash
cd ~/code/expense-tracker/src/expense_tracker
cd ../../tests
cd -
cd ..
pwd
```

What does the last one print?
""",
        [
            opt(
                "`/home/alice/code/expense-tracker/src`",
                "Right: `cd -` returns to `src/expense_tracker`, and `cd ..` then goes up one level, to `src`.",
                True,
            ),
            opt(
                "`/home/alice/code/expense-tracker`",
                "This skips the `cd -`: from `tests`, `cd ..` would reach the project root. But `cd -` first went back to `src/expense_tracker`.",
            ),
            opt(
                "`/home/alice/code`",
                'This reads `cd -` as "up one level", like `cd ..`. `cd -` goes back to where you just were.',
            ),
            opt(
                "`/home`",
                'This reads `cd -` as "go home" (that is `cd` alone) and then goes up one level from `/home/alice`.',
            ),
        ],
        """
Track `pwd` line by line. The first `cd` lands in `/home/alice/code/expense-tracker/src/expense_tracker`. `cd ../../tests` climbs two levels to the project root and goes down into `tests`. `cd -` goes back to where you just were, `src/expense_tracker` (bash prints that path as it goes). `cd ..` goes up one level, to `/home/alice/code/expense-tracker/src`. Each wrong option comes from misreading a single shortcut: ignoring `cd -`, taking it for `cd ..`, or taking it for `cd` alone.
""",
    )
)

add(
    mcq(
        8,
        "core",
        ["concept"],
        3,
        "S9 slide 10; labs/09-terminal.md ('What done looks like' Q2)",
        "slides",
        "source",
        """
Which of these paths names the expense-tracker's `report.py` the same way whatever the current directory is?
""",
        [
            opt(
                "`src/expense_tracker/report.py`",
                "Relative: it starts here, so it only works from the project root.",
            ),
            opt(
                "`../expense-tracker/src/expense_tracker/report.py`",
                "Relative: it only works from a folder directly inside `~/code`, such as `~/code/flashcard-trainer`.",
            ),
            opt(
                "`code/expense-tracker/src/expense_tracker/report.py`",
                "Relative: it only works from alice's home folder, `/home/alice`.",
            ),
            opt(
                "`/home/alice/code/expense-tracker/src/expense_tracker/report.py`",
                "Right: it starts at `/`, so it is absolute and means the same file from anywhere.",
                True,
            ),
        ],
        """
The first character decides. A path that starts with `/` is absolute: it is read from the root of the one tree, so it names the same file from any current directory. Every other path here is relative: it starts here, from the folder `pwd` prints, so it names `report.py` only from certain places (the project root, a folder directly inside `~/code`, or the home folder). All three relative paths are correct somewhere, which is exactly why none is correct everywhere.
""",
    )
)

add(
    mcq(
        9,
        "core",
        ["concept", "predict-output"],
        3,
        "S9 slide 10",
        "slides",
        "run",
        """
alice is in `/home/alice/code/expense-tracker/tests` and wants to look at `report.py` without moving. Which path reaches `src/expense_tracker/report.py` from where she stands?
""",
        [
            opt(
                "`src/expense_tracker/report.py`",
                "That is the path from the project root. From `tests` it points to `tests/src/...`, which does not exist.",
            ),
            opt(
                "`../src/expense_tracker/report.py`",
                "Right: `..` goes up from `tests` to the project root, then the path goes down into `src`.",
                True,
            ),
            opt(
                "`/src/expense_tracker/report.py`",
                "A leading `/` starts at the root of the whole tree, not at the project, and there is no `/src` folder.",
            ),
            opt(
                "`../../src/expense_tracker/report.py`",
                "Two levels up from `tests` is `/home/alice/code`, one level too far.",
            ),
        ],
        """
A relative path is read from the current directory. From `tests`, one `..` reaches the project root, and from there `src/expense_tracker/report.py` goes down to the file. A real run confirms it: from `tests`, `ls ../src/expense_tracker/report.py` finds the file, while the other three paths all give `No such file or directory`. The distractors are the three classic slips: forgetting where you stand, confusing `/` with the project root, and counting one level too many.
""",
    )
)

add(
    mcq(
        10,
        "hard",
        ["concept", "judgement"],
        3,
        "S9 slide 10",
        "slides",
        "run",
        """
alice has two projects side by side: `~/code/expense-tracker` and `~/code/flashcard-trainer`. In which pair do both paths name the same file?
""",
        [
            opt(
                "From `~/code/expense-tracker`: `README.md`. From `~/code/flashcard-trainer`: `README.md`.",
                "Same text, different starting folders: these are the two projects' own READMEs.",
            ),
            opt(
                "From `~/code/expense-tracker/tests`: `../README.md`. From `~/code`: `../README.md`.",
                "The first is the expense-tracker's README; the second would be `/home/alice/README.md`, which does not exist.",
            ),
            opt(
                "From `~/code/flashcard-trainer`: `../expense-tracker/README.md`. From `~`: `code/expense-tracker/README.md`.",
                "Right: both resolve to `/home/alice/code/expense-tracker/README.md`.",
                True,
            ),
            opt(
                "From `~`: `code/expense-tracker/README.md`. From `~/code/expense-tracker`: `code/expense-tracker/README.md`.",
                "Same text, different start: from the project root it points to a `code` folder inside the project, which does not exist.",
            ),
        ],
        """
Resolve each relative path by writing out the absolute one: start from the folder, apply each `..` (up one) and each name (down one). In the right pair, `/home/alice/code/flashcard-trainer` + `..` + `expense-tracker/README.md` and `/home/alice` + `code/expense-tracker/README.md` both give `/home/alice/code/expense-tracker/README.md`. The trap in the other pairs is that identical text means nothing for relative paths: they start here, and here differs. Running `realpath` on each path from its folder confirms all four answers.
""",
    )
)

add(
    mcq(
        11,
        "exam",
        ["read-tool-output"],
        3,
        "S9 slide 12; labs/09-terminal.md exercise 1 Q3",
        "slides",
        "run",
        """
```console
$ pwd
/home/alice/code/expense-tracker/tests
$ cd
$ cd expense-tracker
bash: cd: expense-tracker: No such file or directory
```

alice's project is at `/home/alice/code/expense-tracker`, where she was a moment ago. Why does the last command fail?
""",
        [
            opt(
                "`cd` alone took her home, to `/home/alice`, and `expense-tracker` is not there: it is inside `code`.",
                "Right: with no argument, `cd` goes home, and the relative name is then looked up in the home folder.",
                True,
            ),
            opt(
                "`cd` alone went back to the previous folder, so the relative name was read from somewhere unexpected.",
                "That is `cd -`. A plain `cd` always goes home.",
            ),
            opt(
                'The name contains a hyphen, so `cd` needs it in quotes: `cd "expense-tracker"`.',
                "Hyphens are ordinary characters in names; quotes matter for spaces. The folder simply is not in her home.",
            ),
            opt(
                "`cd` alone does nothing, so she is still in `tests`, which has no `expense-tracker` inside.",
                "`cd` with no argument is not a no-op: it goes home, and `pwd` would now print `/home/alice`.",
            ),
        ],
        """
Two shortcuts from slide 12 are easy to mix up: `cd -` goes back to where you just were, and `cd` alone goes home. After the plain `cd`, alice is in `/home/alice`, so `cd expense-tracker` looks for `/home/alice/expense-tracker`. The project is one level deeper, in `~/code`. The fix is `cd code/expense-tracker` from home, or `cd ~/code/expense-tracker` from anywhere. When a `cd` fails, `pwd` and `ls` tell you where you are and what is there.
""",
    )
)

# --- s4 ------------------------------------------------------------------
add(
    mcq(
        12,
        "exam",
        ["read-tool-output", "judgement"],
        4,
        "S9 slides 10–11",
        "slides",
        "run",
        """
```console
$ pwd
/home/alice/code/expense-tracker/tests
$ uv run expenses report expenses.csv
could not read expenses.csv
$ echo $?
1
```

`expenses.csv` is in the project root, where it always is. What should alice do next?
""",
        [
            opt(
                "Run `uv sync` again: the program could not load its dependencies, so it failed to read the file.",
                "The program ran far enough to print its own message, so its dependencies loaded. Reinstalling fixes nothing here.",
            ),
            opt(
                "Run `chmod 777 expenses.csv`, so that the program is allowed to read the file.",
                "There is no permission problem: the file is not in this folder at all. And 777 is almost never the answer.",
            ),
            opt(
                "Go up to the project root with `cd ..` (or pass `../expenses.csv`) and run the same command again.",
                "Right: the relative name `expenses.csv` was looked up in `tests`, where it does not exist.",
                True,
            ),
            opt(
                "Change `cli.py` to open `/home/alice/code/expense-tracker/expenses.csv`, so the path always works.",
                "Hard-coding alice's absolute path breaks the program on every other machine. The code is right; she is standing in the wrong place.",
            ),
        ],
        """
Slide 11 asks: which `expenses.csv`? The one in the folder you are standing in, not the one next to the code. `uv run` found the project by looking upwards for `pyproject.toml`, but the program then opened `expenses.csv` relative to the current directory, `tests`. The message and the exit code 1 are the program failing well; reading the path in the error against `pwd` gives the diagnosis. The distractors are the careless moves: reinstall, loosen permissions, edit code that works.
""",
    )
)

add(
    mcq(
        13,
        "hard",
        ["read-tool-output", "read-code"],
        4,
        "S9 slide 11; expense-tracker v0.4 cli.py; S8 (monkeypatch.chdir)",
        "slides",
        "run",
        """
```console
$ cd ~/code/expense-tracker/tests
$ uv run expenses add "Bar Ramon" dining 12.50
added Bar Ramon (dining) 12.50 to data/expenses.csv
$ cd ..
$ uv run expenses report data/expenses.csv
could not read data/expenses.csv
```

In `cli.py`, `add` writes to `DATA_FILE = Path("data") / "expenses.csv"`. Where is the expense alice just added?
""",
        [
            opt(
                "Nowhere: `add` failed, but printed a success message and exited 0, a program that lies.",
                "Nothing failed: `add` wrote the file and said where. The question is which folder that `data/` was in.",
            ),
            opt(
                "In `~/code/expense-tracker/data/expenses.csv`, but `report` cannot read files that `add` wrote.",
                "There is no `data` folder in the project root, and `report` reads any CSV in the expected format.",
            ),
            opt(
                "In `~/code/expense-tracker/tests/data/expenses.csv`: `data/` was read from where she stood.",
                "Right: from the root, `find . -name expenses.csv` lists `./tests/data/expenses.csv` next to the sample `./expenses.csv`.",
                True,
            ),
            opt(
                "In `.venv/data/expenses.csv`, because `uv run` runs every program inside the virtual environment.",
                "`uv run` uses the environment's Python and packages, but the current directory stays where you are.",
            ),
        ],
        """
Relative paths cut both ways: a program reads them from the current directory, and writes them there too. `Path("data") / "expenses.csv"` has no leading `/`, so when alice ran `add` from `tests`, the program created `tests/data/expenses.csv`. Back at the root, `report data/expenses.csv` looked for `./data/expenses.csv`, which was never made. The success message even printed the relative path; read it against the folder you were in. Session 8 tests `add` with `monkeypatch.chdir(tmp_path)` for this reason: the file lands in the current directory.
""",
    )
)

add(
    mcq(
        14,
        "exam",
        ["read-tool-output", "judgement"],
        4,
        "S9 slide 12; S5 slide 12 and labs/01-scaffold.md (two spellings)",
        "slides",
        "run",
        """
In the expense-tracker root, alice types `cd src/expense-tr` and presses Tab. Nothing completes. She types the rest of the name by hand, presses Enter, then looks:

```console
$ cd src/expense-tracker
bash: cd: src/expense-tracker: No such file or directory
$ ls src
expense_tracker
```

What was Tab telling her?
""",
        [
            opt(
                "That Tab completion is switched off in WSL and has to be enabled in the settings first.",
                "Tab completion works in `bash` out of the box, and `ls src` shows the real cause: a different name.",
            ),
            opt(
                "That the folder is hidden, so Tab ignores it until it has been listed once with `ls -a`.",
                "Only names starting with a dot are hidden, and Tab completes those too. `expense_tracker` is not hidden.",
            ),
            opt(
                "That two folders start with `expense-tr`, so Tab could not choose between them.",
                "`ls src` shows a single folder, and its name does not start with `expense-tr` at all.",
            ),
            opt(
                "That the name is wrong: the package folder is `expense_tracker`, with an underscore.",
                "Right: if Tab does not complete, the name is wrong or ambiguous. `ls` shows it is wrong; the hyphen belongs to the project's name, `expense-tracker`.",
                True,
            ),
        ],
        """
Slide 12: Tab completes names; if it does not complete, the name is wrong or ambiguous. That makes Tab a check, not only a time saver. The check failed because of session 5's two spellings: a hyphen in the project's name (`expense-tracker`, also the repository), an underscore in the Python package (`expense_tracker`). `ls src` shows the real name. The habit to take away: when Tab refuses, stop and look with `ls`, instead of typing the rest by hand and pressing Enter.
""",
    )
)

add(
    sort_q(
        15,
        "core",
        ["concept"],
        4,
        "S9 slide 12",
        "slides",
        "source",
        """
Slide 12's time savers. Match each situation with the one that fits it best.
""",
        [
            ("tab", "Tab"),
            ("up", "↑"),
            ("ctrlr", "Ctrl-R"),
            ("ctrlc", "Ctrl-C"),
            ("cdback", "`cd -`"),
        ],
        [
            (
                "You are not sure whether the folder is `expense_tracker` or `expense-tracker`.",
                "tab",
                "Tab completes only names that exist, so it settles the spelling before you press Enter.",
            ),
            (
                "`uv run pytest` has printed nothing for two minutes since a teammate changed a `while` loop.",
                "ctrlc",
                "Ctrl-C stops the program that is running; a loop that never ends needs stopping, not waiting.",
            ),
            (
                "You want to rerun the command you just ran, with `--min 20` changed to `--min 50`.",
                "up",
                "↑ brings back the last command, so you edit one number instead of retyping the line.",
            ),
            (
                "Yesterday you ran a long `uv run expenses report --category dining --min 20` and want it back.",
                "ctrlr",
                "Ctrl-R searches your history: type `dining` and it finds the old line.",
            ),
            (
                "You went from the project root to `~/code/flashcard-trainer/tests` to check something and want to return.",
                "cdback",
                "`cd -` goes back to where you just were, without typing the path.",
            ),
            (
                "You typed `cat` with no file name and the terminal seems to hang.",
                "ctrlc",
                "`cat` with no file waits for you to type something; Ctrl-C stops it.",
            ),
            (
                "Before pressing Enter, you want to be sure `.github/workflows/check.yml` is spelled right.",
                "tab",
                "If Tab completes each part of the path, every part exists.",
            ),
            (
                "You typed `cd /mnt/c/Users/ana` by mistake and want the folder you were in before.",
                "cdback",
                "`cd -` returns to the previous folder, wherever that was.",
            ),
        ],
        """
Slide 12 calls these huge time savers. Two of them also prevent mistakes: Tab, because a name that does not complete is wrong or ambiguous, and ↑, because re-using a command you have already checked avoids retyping errors (the same idea as the `ls`-then-`rm` habit). Ctrl-R reaches further back than ↑ by searching your history. Ctrl-C stops the program that is running. `cd -` returns to the previous folder, while `cd` alone goes home.
""",
    )
)

add(
    open_q(
        16,
        "exam",
        ["read-tool-output", "judgement"],
        4,
        "S9 slides 10–12",
        "slides",
        "run",
        """
alice pastes this from her terminal into the group chat and writes: "The project is broken. Should I clone it again?"

```console
$ pwd
/home/alice
$ cd expense-tracker
bash: cd: expense-tracker: No such file or directory
$ ls
code
$ cd code/expense-tracker/tests
$ uv run expenses report expenses.csv
could not read expenses.csv
```
""",
        [
            part(
                "1",
                "Where was she at each failure, and why did each command fail?",
                2,
                "The first `cd` failed because she was in her home, `/home/alice`, and the project is not there: it is inside `code`. The report failed because she then went one level too deep, into `tests`, so the relative name `expenses.csv` was looked up as `tests/expenses.csv`, which does not exist.",
                [
                    "First failure: she is in her home, `/home/alice`, and `expense-tracker` is inside `code`, not in home",
                    "Second failure: standing in `tests`, the relative path `expenses.csv` is read from there; the file is in the project root",
                ],
                '"The file is missing" or "uv is broken" ignores the evidence: `ls` shows where she is, and the program printed its own message, so it ran. Explaining only one of the two failures loses a mark. A subtler slip is "the program looks next to its code"; slide 11 says it uses the folder you are standing in.',
            ),
            part(
                "2",
                "Say in words which commands she should type next, and what each one shows her.",
                2,
                "Go up one level with `cd ..` to the project root. `pwd` should then print `/home/alice/code/expense-tracker`, and `ls expenses.csv` shows the file is there. Then bring the report command back with ↑ and run it again.",
                [
                    "Moves to the project root (`cd ..`, or `cd ~/code/expense-tracker`)",
                    "Checks with `pwd` and/or `ls` before rerunning, then reruns the same command",
                ],
                '"Use `cd` to go to the right place" is not a command in words: say which folder and how. Jumping straight to rerunning without checking where you are skips the habit the session teaches. Moving `expenses.csv` into `tests`, or writing an absolute path into the code, fixes the symptom and damages the project.',
            ),
            part(
                "3",
                "Should she clone it again? Answer with the session 9 rule.",
                1,
                'No. Nothing is broken: most "file not found" errors are the wrong current directory, so run `pwd` first.',
                [
                    "No re-clone, with the rule: most file-not-found errors are the wrong current directory, so run `pwd` first"
                ],
                '"Yes, to be safe" wastes time and fails in the same way from the same folder. A bare "no" earns nothing: the mark is for naming the wrong current directory as the cause.',
            ),
        ],
        """
The "read tool output" shape applied to session 9. Every line of the transcript is evidence: `pwd` says home, the `cd` error says the name is not in home, `ls` shows `code`, and the program's own message names a relative path. Slide 10's rule (most "file not found" errors are the wrong current directory; run `pwd` first) and slide 11's reading of the path in an error answer all three parts. A real run confirms that `cd ..`, `pwd`, `ls expenses.csv` and the same report command then work.
""",
    )
)

# --- s5 ------------------------------------------------------------------
add(
    mcq(
        17,
        "exam",
        ["predict-output"],
        5,
        "S9 slide 14",
        "slides",
        "run",
        """
These are the six commands from slide 14, run in an empty folder:

```bash
mkdir notes
touch notes/todo.txt
cp notes/todo.txt notes/todo-backup.txt
cp -r notes notes-old
mv notes/todo-backup.txt notes/old.txt
rm notes/old.txt
```

What do `notes` and `notes-old` contain afterwards?
""",
        [
            opt(
                "`notes` holds `todo.txt`; `notes-old` holds `todo-backup.txt` and `todo.txt`.",
                "Right: `cp -r` copied the folder with both files, and the later `mv` and `rm` only touched `notes`.",
                True,
            ),
            opt(
                "`notes` holds `todo.txt`; `notes-old` holds `todo.txt` only.",
                "This forgets that the backup was made before the folder was copied, so the copy includes it.",
            ),
            opt(
                "`notes` holds `old.txt` and `todo.txt`; `notes-old` holds `todo-backup.txt` and `todo.txt`.",
                "The last line removed `notes/old.txt`, and `rm` leaves nothing behind.",
            ),
            opt(
                "`notes` holds `todo.txt`; `notes-old` holds `old.txt` and `todo.txt`.",
                "`mv` renamed the file inside `notes` only. `notes-old` is an independent copy, not a link to `notes`.",
            ),
        ],
        """
Follow the files, not the commands. After line 3, `notes` holds `todo.txt` and `todo-backup.txt`. Line 4 copies the whole folder, with both files, into `notes-old`: `cp -r` copies a folder and everything in it, as it is at that moment. Line 5 renames the backup inside `notes` to `old.txt` (`mv` is also rename), and line 6 removes it for good. A real run of the six lines, followed by `ls notes notes-old`, prints exactly this.
""",
    )
)

add(
    mcq(
        18,
        "core",
        ["read-tool-output"],
        5,
        "S9 slide 14; labs/09-terminal.md exercise 2",
        "lab",
        "run",
        """
```console
$ ls
reports
$ cp reports reports-copy
cp: -r not specified; omitting directory 'reports'
$ ls
reports
```

What happened?
""",
        [
            opt(
                "`reports-copy` was created but left empty, because only `-r` copies what is inside.",
                "The second `ls` shows nothing new. `cp` refused the folder and created nothing.",
            ),
            opt(
                "Nothing was copied: plain `cp` skips a folder, and copying one needs `cp -r`.",
                "Right: the message says `-r` was not given, so the folder was skipped.",
                True,
            ),
            opt(
                "`reports` was renamed to `reports-copy`, because `cp` on a folder behaves like `mv`.",
                "`ls` still shows `reports`. Renaming is `mv`'s job, never `cp`'s.",
            ),
            opt(
                "The files inside `reports` were copied, but the folder name itself was left out.",
                'No new name appears in `ls`; "omitting directory" means the whole folder was skipped.',
            ),
        ],
        """
Slide 14: `cp -r` copies a folder and everything in it. Without `-r`, `cp` prints `-r not specified; omitting directory 'reports'` and copies nothing (its exit code is 1). The message is not a flag to memorise: it says what was skipped and why, and the second `ls` confirms it. `cp -r reports reports-copy` is the command lab 09 uses for "copy the whole `reports` folder".
""",
    )
)

add(
    mcq(
        19,
        "core",
        ["concept"],
        5,
        "S9 slide 14; labs/09-terminal.md exercise 2 Q6",
        "slides",
        "source",
        """
In your group repository, a minute ago you ran `rm notes/old.txt`, a file you created this morning and never committed. Now you realise you needed it. Which statement is true?
""",
        [
            opt(
                "It is in the bin (the Trash, or the Windows Recycle Bin), and you can drag it back from there.",
                "`rm` has no bin. Desktop bins belong to the file manager, not to the terminal.",
            ),
            opt(
                "Running `rm -i notes/old.txt` now asks whether you want to restore the file you removed.",
                "`rm -i` asks before removing. Nothing in `rm` restores.",
            ),
            opt(
                "It is gone. `rm` has no bin; only a copy you made, or a version you committed, brings it back.",
                "Right: what `rm` removes is gone. This file was never committed, so only a copy you made yourself could bring it back.",
                True,
            ),
            opt(
                "`git restore notes/old.txt` brings it back, since git keeps a copy of every file in the repository.",
                "git keeps only what you committed. This file never was, so git has nothing to restore.",
            ),
        ],
        """
Slide 14: `rm` does not ask and there is no bin. What it removes is gone. Lab 09 makes you see it: after `rm -r reports-copy`, `ls reports-copy` says `No such file or directory`, and there is nothing to get it back from. That is why slide 15's habits exist, and why lab 09 copies `expenses.csv` before touching it. If the file had been committed, its content could come back from git; work you never committed cannot.
""",
    )
)

add(
    mcq(
        20,
        "hard",
        ["read-tool-output", "predict-output"],
        5,
        "S9 slide 14; labs/09-terminal.md exercise 2",
        "lab",
        "run",
        """
alice meant to move `notes.txt` into a folder called `2025`, but she had created `2026` by mistake:

```console
$ ls reports
2026  notes.txt
$ mv reports/notes.txt reports/2025
$ ls reports
2025  2026
$ cd reports/2025
bash: cd: reports/2025: Not a directory
```

What did `mv` do?
""",
        [
            opt(
                "It created a new folder called `2025` and then moved `notes.txt` into it.",
                "`mv` never creates folders, and `cd` says `2025` is not a directory.",
            ),
            opt(
                "It renamed `notes.txt` to a file called `2025`, as no such folder existed.",
                "Right: `mv` is also rename. With no folder to move into, the target becomes the new name.",
                True,
            ),
            opt(
                "It refused, printed nothing at all, and left `notes.txt` exactly where it was.",
                "The second `ls` shows that `notes.txt` is gone and `2025` has appeared.",
            ),
            opt(
                "It moved `notes.txt` into `2026`, the closest folder name it could find.",
                "Neither the shell nor `mv` guesses. A new entry, `2025`, appeared; `2026` was not touched.",
            ),
        ],
        """
`mv` has one rule with two outcomes. If the target is an existing folder, the file goes inside it. If not, the target is the new name: slide 14's "mv is also rename". Here `reports/2025` did not exist, so `notes.txt` silently became a file called `2025`. The clue is the `cd` error, `Not a directory`. Writing the target with a trailing slash, `reports/2025/`, makes `mv` refuse with an error instead, because the slash says the target must be a folder.
""",
    )
)

# --- s6 ------------------------------------------------------------------
add(
    mcq(
        21,
        "exam",
        ["read-tool-output", "predict-output"],
        6,
        "S9 slide 15; labs/09-terminal.md exercise 2 Q7",
        "lab",
        "run",
        """
```console
$ pwd
/home/alice/lab09
$ ls
reports  reports-copy
$ rm -r reports-copy *
rm: cannot remove 'reports-copy': No such file or directory
```

Lab 09 asks you to reason this one out. What did the last command remove?
""",
        [
            opt(
                "Nothing: `rm` stopped at the error, so both folders are still there.",
                "The error came last. `rm` had already removed both folders when it tried `reports-copy` a second time.",
            ),
            opt(
                "Only `reports-copy`: the space after the name made the shell ignore the `*`.",
                "The space is what made `*` a separate argument. The shell expanded it; it did not ignore it.",
            ),
            opt(
                "Only files with a `*` in their name; finding none, `rm` printed an error.",
                "No file has a star in its name. The shell replaces `*` with every name here before `rm` starts.",
            ),
            opt(
                "Both folders: the shell turned `*` into every name here first.",
                "Right: `rm` received `reports-copy reports reports-copy`, and `-r` removed both folders.",
                True,
            ),
        ],
        """
Two things combine. The space makes `*` an argument of its own, and the shell expands `*` to every name in the current folder before `rm` runs. So `rm` received `reports-copy reports reports-copy`. It removed `reports-copy`, then `reports` with everything in it, then failed on the second `reports-copy`, which no longer existed. That error is the only output, and it hides the damage: in the real run, the next `ls` prints nothing and `ls -a` shows only `.` and `..`. There is no bin.
""",
    )
)

add(
    mcq(
        22,
        "hard",
        ["compare", "predict-output"],
        6,
        "S9 slide 15",
        "slides",
        "run",
        """
In a folder where `ls` shows `draft.txt  notes  notes-old`, compare these two commands:

```bash
rm -r notes-old/*
rm -r notes-old/ *
```

Which statement is right?
""",
        [
            opt(
                "The first empties `notes-old`; the second removes it, `draft.txt` and `notes`.",
                "Right: `notes-old/*` is one argument (what is inside); `notes-old/ *` is two (the folder, then every name here).",
                True,
            ),
            opt(
                "Both remove only what is inside `notes-old`; the shell ignores a space before `*`.",
                "The shell cuts the line into arguments at spaces, so the space creates a new argument.",
            ),
            opt(
                "The first removes `notes-old` and everything here; the second only empties `notes-old`.",
                "This swaps them: without the space, the star stays inside `notes-old/`.",
            ),
            opt(
                "The second is safer, because a separate `*` makes `rm` ask before removing each name.",
                "`rm` asks only with `-i`. A separate `*` simply hands `rm` every name in the folder.",
            ),
        ],
        """
The shell cuts the line into arguments at spaces, then expands each `*` into the names it matches. `notes-old/*` matches the names inside `notes-old`, so the folder survives, empty. `notes-old/ *` is two arguments: the folder itself, and `*`, which matches every name in the current folder, here `draft.txt`, `notes` and `notes-old`. This is slide 15's example: the second line removes `notes-old/` and every file in the current directory. A real run confirms both outcomes.
""",
    )
)

add(
    mcq(
        23,
        "exam",
        ["judgement"],
        6,
        "S9 slide 15",
        "slides",
        "source",
        """
You want to delete `~/code/flashcard-trainer/old-exports`, a folder of CSV files nobody needs any more. Which routine follows the session 9 habits?
""",
        [
            opt(
                "`cd` into `old-exports` and run `rm -r *`, so that nothing outside the folder can be touched.",
                "It relies on the `cd` having worked. If it failed, `rm -r *` empties whatever folder you are really in: the slide's accident.",
            ),
            opt(
                "Run `rm -rf old-exports`, so that `rm` does not stop halfway through to ask questions.",
                "`-f` removes the last safety, and the relative path depends on where you stand, which you have not checked.",
            ),
            opt(
                "Run `ls` on the full path, check the list, then press ↑ and change `ls` to `rm -r`.",
                "Right: what you checked is exactly what you delete, character for character.",
                True,
            ),
            opt(
                "Run `chmod 777 old-exports` first, so that `rm` has permission for every file inside it.",
                "Permissions are not the problem, and 777 is almost never the answer.",
            ),
        ],
        """
Slide 15's habits: `ls` the exact path before you `rm` it, then press ↑ and swap `ls` for `rm`; use `rm -i` when you are tired; never `rm -rf` with a variable you have not printed. The ↑ trick matters because retyping is where a stray space or `*` slips in. Each other routine relies on something unchecked: that a `cd` worked, that a relative path starts where you think it does, or that permissions were the problem in the first place.
""",
    )
)

add(
    mcq(
        24,
        "beyond",
        ["read-tool-output", "judgement"],
        6,
        "S9 slide 15; S10 slide 12 (variables)",
        "slides",
        "run",
        """
A teammate's clean-up script sets `REPORT_DIR` near the top and later runs `rm -rf "$REPORT_DIR/"*`. You suspect the line that sets the variable has a typo. Before running the `rm` line by hand, you print what it would use:

```console
$ echo "$REPORT_DIR/"
/
```

What should you conclude?
""",
        [
            opt(
                "Nothing is wrong: `/` simply means the command will work in the current folder.",
                "`/` is the root of the whole tree. The current folder would be `.`.",
            ),
            opt(
                "`REPORT_DIR` holds an absolute path, and absolute paths always print as `/`.",
                "An absolute path prints in full, such as `/home/alice/reports/`. Only the slash you typed is left.",
            ),
            opt(
                "It is harmless, because `rm` cannot remove anything outside your home folder.",
                "`rm` removes whatever your user is allowed to remove, your whole home included.",
            ),
            opt(
                "`REPORT_DIR` is empty, so the line would run `rm -rf /*`. Do not run it.",
                "Right: an empty variable leaves only the `/`, and `*` then expands to every top-level folder.",
                True,
            ),
        ],
        """
Slide 15's third habit: never `rm -rf` with a variable you have not printed. The shell replaces `$REPORT_DIR` with its value before `rm` runs, exactly as it expands `*`. If the variable is empty, `"$REPORT_DIR/"*` becomes `/*`, which the shell expands to every folder at the root of the tree, and `-f` means `rm` never asks. Printing the path costs one line and exposes the problem; fixing the line that sets the variable comes before any `rm`. Variables are Friday's topic, but the habit is session 9's.
""",
    )
)

add(
    open_q(
        25,
        "hard",
        ["read-tool-output", "judgement"],
        6,
        "S9 slide 15; labs/09-terminal.md exercise 2 Q7; S3 slide 13 (git status)",
        "lab",
        "run",
        """
alice wanted to delete an old folder of exports in her group repository. Her last push was this morning; since then she has edited `boxes.py` without committing.

```console
$ pwd
/home/alice/code/flashcard-trainer
$ ls
LICENSE  README.md  exports-old  pyproject.toml  scripts  src  tests  uv.lock
$ git status --short
 M src/flashcard_trainer/boxes.py
?? exports-old/
$ rm -r exports-old *
rm: cannot remove 'exports-old': No such file or directory
$ ls -a
.  ..  .git  .github  .gitignore  .python-version
```
""",
        [
            part(
                "1",
                "Explain exactly why one command removed so much.",
                2,
                "The space made `*` a separate argument, and the shell expanded it to every name in the folder before `rm` ran, so `rm -r` received `exports-old` plus `LICENSE`, `README.md`, `scripts`, `src`, `tests` and the rest. The error is only the second attempt at `exports-old`.",
                [
                    "The space split the line, making `*` an argument of its own",
                    "The shell (not `rm`) expanded `*` to every name in the folder, and `-r` removed the folders too",
                ],
                '"`rm` deletes everything when it hits an error" is wrong: the error came last, after the damage. "The star means all files" is half an answer: the mark is for saying who expands it (the shell, before `rm` runs) and that the space made it a separate argument. Blaming `-r` alone misses that `-r` only matters once `*` has put the folders in the list.',
            ),
            part(
                "2",
                "Why did `.git`, `.github` and `.gitignore` survive, and what can she get back?",
                2,
                "`*` does not match names that start with a dot, so the hidden entries survived. Everything committed and pushed is still in git and on GitHub, so it can come back. Her uncommitted edit to `boxes.py` is gone: `rm` has no bin.",
                [
                    "`*` skips names that start with a dot, so the hidden entries were not removed",
                    "Committed and pushed work comes back from git (clone again, or from the surviving `.git`); the uncommitted edit to `boxes.py` is lost",
                ],
                '"Nothing can be recovered" ignores git: what was pushed is on GitHub. "git brings everything back" ignores that the edit to `boxes.py` was never committed, as `git status` showed. Saying the dot files survived by luck misses the rule: `*` does not match names that start with a dot.',
            ),
            part(
                "3",
                "Name two habits from session 9 that would have prevented this.",
                2,
                "`ls` the exact path first (`ls exports-old`), then press ↑ and swap `ls` for `rm`, so what she checked is what she deletes. When tired, use `rm -i`, which asks before each removal.",
                [
                    "`ls` the exact path first, then ↑ and swap `ls` for `rm`",
                    "A second habit: `rm -i` (asks first) when tired, or never `rm -rf` with a variable you have not printed",
                ],
                '"Be more careful" is not a habit. "Use the file manager instead" dodges the question. Naming `rm -i` without saying that it asks first, or the ↑ trick without saying why it helps (nothing is retyped), earns half.',
            ),
        ],
        """
This combines three session 9 ideas: how the shell turns a line into arguments (spaces and `*`), which names `*` matches (not dot names), and the permanence of `rm`. `git status --short` is the extra evidence: before, one modified file and one untracked folder. In the real run, `git status --short` afterwards lists every tracked file as deleted (` D`), so committed content can be restored from git while the uncommitted edit cannot. The habits are slide 15's, word for word.
""",
    )
)

# --- s7 ------------------------------------------------------------------
add(
    mcq(
        26,
        "core",
        ["read-tool-output"],
        7,
        "S9 slide 17; labs/09-terminal.md exercise 1 Q2",
        "lab",
        "run",
        """
```console
$ ls -l
-rw-rw-r-- 1 alice alice  1072 Oct 13 10:12 LICENSE
-rw-rw-r-- 1 alice alice  1193 Oct 13 10:12 README.md
-rw-rw-r-- 1 alice alice 15221 Oct 13 10:12 expenses.csv
-rw-rw-r-- 1 alice alice   767 Oct 13 10:12 pyproject.toml
drwxrwxr-x 3 alice alice  4096 Oct 13 10:12 src
drwxrwxr-x 2 alice alice  4096 Oct 13 10:12 tests
-rw-rw-r-- 1 alice alice 73053 Oct 13 10:12 uv.lock
```

Which entries are folders, and how can you tell?
""",
        [
            opt(
                "`src` and `tests`: their lines start with `d`.",
                "Right: the first character is the type, `-` for a file and `d` for a directory.",
                True,
            ),
            opt(
                "`LICENSE`, `src` and `tests`: names without a dot are folders.",
                "Names say nothing about type. `LICENSE` starts with `-`: it is a file.",
            ),
            opt(
                "`expenses.csv` and `uv.lock`: they are the largest entries in the listing.",
                "Size is not type. A folder's size is the space for its list of names (4096 here), not the size of what it contains.",
            ),
            opt(
                "None: `ls -l` shows only files, and folders appear only with `ls -a`.",
                "`ls -l` shows folders too. `-a` adds the hidden names, not folders.",
            ),
        ],
        """
In an `ls -l` line, read the first character before anything else: `-` is a file, `d` is a directory. That answers lab 09's question "which entries are folders?" without guessing from names or sizes. The rest of the line is the permissions (three groups of three), a link count, the owner, the group, the size in bytes, the date of the last change, and the name.
""",
    )
)

add(
    mcq(
        27,
        "exam",
        ["read-tool-output"],
        7,
        "S9 slide 17",
        "slides",
        "run",
        """
On a shared university Linux server, alice's project contains this file:

```console
$ ls -l expenses.csv
-rw-rw-r-- 1 alice alice 15221 Oct 13 10:12 expenses.csv
```

ben has an account on the same server but is not in the group `alice`. What can ben do with this file?
""",
        [
            opt(
                "Read it and change it: the middle `rw-` applies to every other user.",
                "The middle group is for members of the file's group, `alice`, and ben is not one.",
            ),
            opt(
                "Read it, but not change it: the last three characters, `r--`, are for everyone else.",
                "Right: ben is neither the owner nor in the group, so the third group applies.",
                True,
            ),
            opt(
                "Nothing at all, because only the owner, `alice`, is named on the line.",
                "The third group gives everyone else `r`, so ben can read it.",
            ),
            opt(
                "Run it as a program, because everyone can read it and readable files can be executed.",
                "Running needs `x`, and nobody has `x` on this file.",
            ),
        ],
        """
Read the permission string as type, then owner, group, everyone else: `-` (a file), `rw-` (alice can read and write), `rw-` (members of the group `alice` can read and write), `r--` (everyone else can only read). ben is neither the owner nor in the group, so the last three characters apply to him. Who can write: the owner and the group. Who can execute: nobody.
""",
    )
)

add(
    mcq(
        28,
        "exam",
        ["read-tool-output", "concept"],
        7,
        "S9 slide 17",
        "lab",
        "run",
        """
```console
$ ls -ld reports
drw-rw-r-- 2 alice alice 4096 Oct 13 10:12 reports
$ cd reports
bash: cd: reports: Permission denied
```

alice owns `reports` and has `r` and `w` on it. Why can she not enter it?
""",
        [
            opt(
                "Only the administrator can enter folders, so she needs `sudo cd reports`.",
                "Owners enter their own folders all day long. What is missing is one letter, not a different user.",
            ),
            opt(
                "`cd` needs write permission for everyone else, and the last group shows `r--`.",
                "Other users' permissions do not affect alice: she is the owner, so the first group applies.",
            ),
            opt(
                "`x` only matters for programs, so the folder is damaged: recreate it and move the files back.",
                "For a folder, `x` is exactly what lets you enter it (slide 17). Nothing is damaged; recreating the folder is the reinstall reflex for a one-letter problem.",
            ),
            opt(
                "None of the three groups of letters, hers included, has `x`; for a folder `x` means permission to enter it.",
                "Right: without `x` she cannot go in, whatever `r` and `w` say.",
                True,
            ),
        ],
        """
Slide 17 adds one line under the letters: for a folder, `x` means enter it. The owner's three letters here are `rw-`, and on a folder `r` and `w` are of little use without `x`: alice cannot enter it or reach the files inside. In the same run, `cat reports/notes.txt` is refused too. After `chmod 775 reports`, `cd reports` works. This is why slide 21 gives 755 as the number for "a script or a folder": both need `x`.
""",
    )
)

add(
    open_q(
        29,
        "exam",
        ["read-tool-output", "judgement"],
        7,
        "S9 slides 9, 17–21; labs/09-terminal.md exercise 1",
        "lab",
        "run",
        """
On Tuesday, alice runs this in her group repository. On Friday the group plans to run `./scripts/check.sh`.

```console
$ pwd
/home/alice/code/flashcard-trainer
$ ls -la
drwxrwxr-x 7 alice alice  4096 Oct 13 10:12 .
drwxrwxr-x 4 alice alice  4096 Oct 13 10:12 ..
drwxrwxr-x 7 alice alice  4096 Oct 13 10:12 .git
drwxrwxr-x 3 alice alice  4096 Oct 13 10:12 .github
-rw-rw-r-- 1 alice alice    77 Oct 13 10:12 .gitignore
-rw-rw-r-- 1 alice alice     5 Oct 13 10:12 .python-version
-rw-rw-r-- 1 alice alice  1072 Oct 13 10:12 LICENSE
-rw-rw-r-- 1 alice alice   311 Oct 13 10:12 README.md
-rw-rw-r-- 1 alice alice   450 Oct 13 10:12 pyproject.toml
drwxrwxr-x 2 alice alice  4096 Oct 13 10:12 scripts
drwxrwxr-x 3 alice alice  4096 Oct 13 10:12 src
drwxrwxr-x 2 alice alice  4096 Oct 13 10:12 tests
-rw-rw-r-- 1 alice alice 73051 Oct 13 10:12 uv.lock
$ ls -l scripts
-rw-rw-r-- 1 alice alice 112 Oct 13 10:12 check.sh
```
""",
        [
            part(
                "1",
                "Which entries would plain `ls` not show, and why? In which of them does the CI workflow live?",
                2,
                "`.`, `..`, `.git`, `.github`, `.gitignore` and `.python-version`: `ls` hides names that start with a dot. The CI workflow is inside the hidden `.github` folder, at `.github/workflows/check.yml`.",
                [
                    "Names the dot entries (`.git`, `.github`, `.gitignore`, `.python-version`, and `.` and `..`) and says `ls` hides names that start with a dot",
                    "Places the workflow in `.github` (`.github/workflows/check.yml`)",
                ],
                'Listing only `.git` misses three hidden entries. "They are hidden because they are system files" gives the wrong reason: the reason is the leading dot. Placing the workflow in `scripts` confuses the CI configuration with the script it will call.',
            ),
            part(
                "2",
                "Which entries are folders, and who may change `README.md`?",
                2,
                "The lines that start with `d`: `.`, `..`, `.git`, `.github`, `scripts`, `src` and `tests`. `README.md` is `rw-rw-r--`, so alice (the owner) and members of the group `alice` may change it; everyone else may only read it.",
                [
                    "Folders identified by the leading `d` (`scripts`, `src`, `tests`, `.git`, `.github`)",
                    "`README.md`: owner and group can write (`rw-`), everyone else can only read (`r--`)",
                ],
                'Spotting folders by their names ("no extension") is a guess the listing does not need. "Only alice can change it" forgets the group\'s `w`. Reading the groups in the wrong order (group first) reads the string backwards: it is owner, group, everyone else.',
            ),
            part(
                "3",
                "What will `./scripts/check.sh` do on Friday as things stand, and which permissions should `check.sh` have, in letters and as a number?",
                2,
                "It will fail with Permission denied: `check.sh` is `-rw-rw-r--`, with no `x` anywhere. It should be `rwxr-xr-x`, 755 (or at least get `chmod +x`), and the change must be committed so that CI's clone gets it.",
                [
                    "Predicts Permission denied because `check.sh` has no `x`",
                    "Gives `rwxr-xr-x` / 755 (or `chmod +x`) as the target, committed so CI gets it",
                ],
                'Proposing 777 "so it always works" trades one missing `x` for write access for everyone. "It will run because alice owns it" confuses owning with executing. Forgetting to commit the change leaves CI with the old, non-executable file.',
            ),
        ],
        """
A reading question in the shape of the sample paper's Q9: one artefact, three judgements. The first character gives the type; the leading dot gives the hidden names; the three groups give who can do what. `check.sh` is a new file, and a new file never gets execute permission, so it needs `chmod +x` (755 is slide 21's number for a script). git remembers the bit, so committing the change is what allows CI to run the script on Friday.
""",
    )
)

# --- s8 ------------------------------------------------------------------
add(
    mcq(
        30,
        "exam",
        ["read-tool-output", "judgement"],
        8,
        "S9 slides 18–19; labs/09-terminal.md exercise 3",
        "lab",
        "run",
        r"""
```console
$ printf '#!/usr/bin/env bash\necho "report ready"\n' > run.sh
$ ls -l run.sh
-rw-rw-r-- 1 alice alice 40 Oct 13 10:12 run.sh
$ ./run.sh
bash: ./run.sh: Permission denied
```

What is the right fix?
""",
        [
            opt(
                "`chmod 777 run.sh`, so that no permission can ever block the script again.",
                "777 adds the missing `x` and also gives everyone write permission: it makes the error go away and the problem worse.",
            ),
            opt(
                "Delete the file and create it again in VS Code, since `printf` made it wrongly.",
                "A file you write with an editor, `touch` or `printf` never gets execute permission, so the new copy would have no `x` either.",
            ),
            opt(
                "Run `sudo ./run.sh`, so that the script runs with administrator rights.",
                "The problem is not who runs it: nobody has said the file is a program.",
            ),
            opt(
                "`chmod +x run.sh`: the file has no `x`, and this states that it is a program.",
                "Right: `ls -l` then shows `-rwxrwxr-x`, and `./run.sh` prints `report ready`.",
                True,
            ),
        ],
        """
Slides 18–19: there is no `x`. Nobody said this file is a program. A new file never gets execution permissions. `chmod +x run.sh` adds the `x` (for owner, group and others here), and the script runs. The distractors are the careless fixes: 777 (more than needed, and risky on a script others could then edit), recreating the file (it would be born without `x` again) and `sudo` (a bigger hammer for a problem that is one missing letter).
""",
    )
)

add(
    mcq(
        31,
        "core",
        ["read-tool-output", "concept"],
        8,
        "labs/09-terminal.md exercise 3 Q2; S9 slide 19",
        "lab",
        "run",
        """
```console
$ chmod +x run.sh
$ ./run.sh
report ready
$ run.sh
run.sh: command not found
```

Why does the last command fail when the one before it worked?
""",
        [
            opt(
                "`chmod +x` lasts for one run only, so the script needs it again.",
                "The `x` bit stays until someone changes it; `ls -l` would still show `-rwxrwxr-x`.",
            ),
            opt(
                "Without `./`, the shell only searches `PATH`, and this folder is not in it.",
                'Right: `./` means "this folder", so `./run.sh` names the file here.',
                True,
            ),
            opt(
                "`run.sh` and `./run.sh` are different files: the dot in front makes one of them hidden.",
                "A dot at the start of a name hides it; `./` is a path meaning this folder, not part of the name.",
            ),
            opt(
                "The shell runs `.sh` files only when you type `bash` in front of the name.",
                "`./run.sh` ran a moment earlier with no `bash` in front of it.",
            ),
        ],
        """
Lab 09 asks this directly: what does `./` in front of the name mean, and why does `run.sh` alone fail? `./` means "this folder", so `./run.sh` is a path to the file here. A bare name is looked up as a command in the folders listed in `PATH`, which is how `uv`, `git` and `ls` are found. The current folder is not in `PATH`, so the shell reports `command not found`. That protects you: a file lying in whatever folder you happen to be in does not run just because its name matches a command.
""",
    )
)

add(
    mcq(
        32,
        "exam",
        ["read-tool-output", "judgement"],
        8,
        "labs/09-terminal.md exercise 3 Q5; S5 ([project.scripts]); S9 slide 19",
        "lab",
        "run",
        """
```console
$ ls -l src/expense_tracker
-rw-rw-r-- 1 alice alice    0 Oct 13 10:12 __init__.py
drwxrwxr-x 2 alice alice 4096 Oct 13 10:20 __pycache__
-rw-rw-r-- 1 alice alice 1617 Oct 13 10:12 cli.py
-rw-rw-r-- 1 alice alice 2595 Oct 13 10:12 report.py
$ ls -l .venv/bin/expenses
-rwxrwxr-x 1 alice alice 332 Oct 13 10:20 .venv/bin/expenses
```

A teammate wants to run `chmod +x` on every `.py` file in `src/` "so the project runs properly". What is the best response?
""",
        [
            opt(
                "Yes: without `x`, `uv run expenses` cannot load `cli.py` and `report.py`.",
                "Importing a module only reads it, so `r` is enough; `uv run expenses` works today with exactly these permissions.",
            ),
            opt(
                "Yes, and make it `chmod 777`, so the rest of the group can also edit the modules.",
                "Editing needs `w`, not `x`, and 777 hands write access to every user; it is almost never the answer.",
            ),
            opt(
                "No: they are modules the package imports; the program is `expenses`, with `x`.",
                "Right: the one file meant to be run is `.venv/bin/expenses`, which uv built with the `x` bit already set.",
                True,
            ),
            opt(
                "No, because Linux never allows a `.py` file to have execute permission.",
                "Any file can be given `x`. The point is that these files should not have it.",
            ),
        ],
        """
Lab 09 asks: which of these files could you run directly, and why is that right for Python modules? None of them has `x`, and that is correct. `__init__.py`, `cli.py` and `report.py` are modules: Python imports them, and importing only needs read permission. The program is the `expenses` command that `[project.scripts]` declares (session 5); uv builds it into `.venv/bin` with the `x` bit, and `uv run expenses` runs it. `chmod +x` is a statement that a file is a program, so making it on modules would state something false.
""",
    )
)

add(
    mcq(
        33,
        "hard",
        ["judgement", "concept"],
        8,
        "S9 slide 20; labs/00-setup.md (work inside the Linux home)",
        "slides",
        "source",
        """
Ana works on WSL in `/mnt/c/Users/ana/code/flashcard-trainer`. In `ls -l`, every file there shows as `-rwxrwxrwx`, even `README.md`. She runs `chmod 644 README.md`, gets no error, and `ls -l` still shows `-rwxrwxrwx`. What is going on?
""",
        [
            opt(
                "`/mnt/c` is her Windows disk, where `chmod` silently does nothing; she should move the project to `~/code`.",
                "Right: slide 20 describes exactly this, and `pwd` should start with `/home/`, not `/mnt/`.",
                True,
            ),
            opt(
                "She is not the owner of `README.md`, so `chmod` was refused; she needs `sudo chmod`.",
                "A refused `chmod` prints an error, and this one was silent. The cause is where the file lives, not who she is.",
            ),
            opt(
                "Linux cannot reach Windows files by their drive letter, so she must give `chmod` the path `C:\\Users\\ana\\code` instead.",
                "There are no drive letters in the one tree: the C: drive simply is `/mnt/c`. `chmod` found the file; it just did nothing.",
            ),
            opt(
                "Nothing is wrong: `-rwxrwxrwx` is how Linux shows healthy files on any disk.",
                "In her Linux home a normal file is `rw-rw-r--`. Every file executable and writable by everyone is the `/mnt/c` symptom.",
            ),
        ],
        """
Slide 20: on WSL, a project under `/mnt/c` shows every file as `rwxrwxrwx`, and `chmod` silently does nothing. Keep your projects in your Linux home, `~/code/...`; it is also why `uv` and `git` are faster there (lab 00 says the same). The check is `pwd`: it should start with `/home/`, not `/mnt/`. The hard part of this question is the silence: no error does not mean success, and the listing on the next line is the evidence.
""",
    )
)

add(
    mcq(
        34,
        "beyond",
        ["read-tool-output", "judgement"],
        8,
        "S9 slide 20; expense-tracker check.yml (run steps)",
        "slides",
        "run",
        """
Your group adds a step `run: ./scripts/check.sh` to the workflow. On your laptop the script runs. On GitHub, the step fails with this line in its log:

```text
/home/runner/work/_temp/3f9d2c1e-7b4a-4e8f-9a61-2c5d8e0b7f14.sh: line 1: ./scripts/check.sh: Permission denied
```

Which fix makes CI green for the right reason?
""",
        [
            opt(
                "Rerun the job: a permission error on GitHub's machines is usually temporary.",
                "The same checkout gives the same file mode every time. Rerunning a red check and hoping for green is the careless move.",
            ),
            opt(
                "Add a step `chmod 777 scripts/check.sh` before it, since the problem only exists on GitHub.",
                "It hides the cause: every fresh clone, a marker's included, still gets a script without `x`, and 777 opens it to writing by anyone.",
            ),
            opt(
                "Run `chmod +x scripts/check.sh` in your Linux home, then commit and push the change.",
                "Right: CI checks out exactly what git recorded, so the `x` bit has to be in a commit, and git records it for every clone.",
                True,
            ),
            opt(
                "Delete `.venv` and run `uv sync` before pushing, so the tools are installed cleanly.",
                "The log names a script and a permission, not a package. Reinstalling is the reflex the course warns against.",
            ),
        ],
        """
Slide 20: Friday's `scripts/check.sh` needs the `x` bit in CI too, and git remembers it. CI does not use your laptop's files; it clones the repository, so the script has whatever mode git recorded. If it only looked executable on your machine (under `/mnt/c` everything shows `rwxrwxrwx`), or you ran `chmod +x` but never committed it, CI's copy has no `x`. The fix belongs in the repository: `chmod +x` in your Linux home, commit, push. `git diff` shows that change as `old mode 100644` / `new mode 100755`.
""",
    )
)

add(
    mcq(
        35,
        "beyond",
        ["read-diff", "judgement"],
        8,
        "S9 slides 20–21",
        "slides",
        "run",
        """
```console
$ git show --stat --format=%s HEAD
Make the check script executable

 scripts/check.sh | 0
 1 file changed, 0 insertions(+), 0 deletions(-)
$ git diff HEAD~1 HEAD
diff --git a/scripts/check.sh b/scripts/check.sh
old mode 100644
new mode 100755
```

A teammate reviewing the history says this commit is empty and should be dropped. What do you answer? (`old mode 100644` and `new mode 100755` are git's way of saying that the file's permissions changed from `rw-r--r--` to `rwxr-xr-x`.)
""",
        [
            opt(
                "Agree: not a single line of the script changed, so the commit has no effect on anyone else.",
                "Lines are not the only thing git records: the diff shows the file's mode changing.",
            ),
            opt(
                "Disagree: the mode went from 644 to 755, so every fresh clone gets a runnable script.",
                "Right: `100755` is git's record of an executable file, and it travels with the repository to every clone, CI's included.",
                True,
            ),
            opt(
                "Agree: file modes stay on each laptop, and git ignores them when it records a commit.",
                "Slide 20 says git remembers the `x` bit; this diff is that memory.",
            ),
            opt(
                "Disagree: `100755` tells CI to run the script with administrator rights from now on.",
                "755 is `rwxr-xr-x`: everyone may read and run it, only the owner may change it. Administrator rights do not come into it.",
            ),
        ],
        """
A diff can change something other than lines. `old mode 100644` / `new mode 100755` is git recording that `scripts/check.sh` became executable; the last three digits are slide 21's numbers (644 a normal file, 755 a script). `--stat` shows zero insertions and deletions, which is why the commit looks empty. Dropping it would bring "Permission denied" back in CI. Its message is a good one, too: it says what the change does.
""",
    )
)

add(
    open_q(
        36,
        "exam",
        ["read-tool-output", "concept"],
        8,
        "S9 slides 18–21; labs/09-terminal.md exercise 3",
        "lab",
        "run",
        """
A teammate who missed session 9 sends you this and asks what is wrong. Answer in 5–8 lines.

```console
$ cat run.sh
#!/usr/bin/env bash
echo "report ready"
$ ls -l run.sh
-rw-rw-r-- 1 alice alice 40 Oct 13 10:12 run.sh
$ ./run.sh
bash: ./run.sh: Permission denied
```
""",
        [
            part(
                "1",
                "Why does the shell refuse to run `run.sh`? Use the `ls -l` line in your answer.",
                2,
                "The permission string `-rw-rw-r--` has no `x` in any of the three groups: the file may be read and written but nobody may execute it. A new file never gets execute permission, whether it was made with `printf`, `touch` or an editor.",
                [
                    "Points to the missing `x` in `-rw-rw-r--` (no execute for owner, group or others)",
                    "Says a new file never gets execute permission: nobody has declared it a program",
                ],
                '"The script has a bug" misses that the shell never ran a line of it: the refusal comes first. "He does not have permission" is too vague, since he can read and write it; name the one missing letter. Blaming the `#!/usr/bin/env bash` line misses that it only matters once the file is allowed to run.',
            ),
            part(
                "2",
                "What does `chmod +x run.sh` do, and why is it `./run.sh` rather than `run.sh`?",
                2,
                "`chmod +x` adds the execute bit, so `ls -l` shows `-rwxrwxr-x`: it states that the file is a program. `./` means the file in this folder; without it the shell only searches the folders in `PATH`, where `run.sh` is not, and says command not found.",
                [
                    "`chmod +x` adds the `x` permission, marking the file as a program",
                    "`./` means this folder; without it the shell searches only `PATH`",
                ],
                '"`chmod` opens the file up" is vague: say which letter it adds and what that means. Many answers explain `chmod` and forget `./`, which is half of lab 09\'s question. "The dot hides the file" confuses a leading dot in a name with the path `./`.',
            ),
            part(
                "3",
                "He found `chmod 777` online. Why not use that?",
                1,
                "777 also gives every user write permission on the script. It makes the error go away and the problem worse, when only the `x` was missing.",
                [
                    "777 adds write permission for everyone else (the last group), which is much more than the missing `x`"
                ],
                '"777 is too much" without saying what extra it gives (write for everyone) earns nothing. "777 does not work" is false: it does silence the error, which is exactly the slide\'s warning: it makes the error go away and the problem worse.',
            ),
        ],
        """
The "explain to a teammate" shape. Part 1 is slides 18–19 in your own words: no `x`, nobody said this file is a program, a new file never gets execute permission. Part 2 needs both halves of lab 09's question: what `chmod +x` changes (an `x` appears, `-rwxrwxr-x`) and what `./` means. Part 3 is slide 21's warning about 777. A real run confirms each step: `Permission denied`, then `report ready` after `chmod +x`, and `command not found` without `./`.
""",
    )
)

add(
    open_q(
        37,
        "hard",
        ["read-tool-output", "judgement"],
        8,
        "S9 slide 20; labs/00-setup.md (Linux home, not /mnt/c)",
        "slides",
        "run",
        """
Ben works on WSL in `/mnt/c/Users/ben/code/flashcard-trainer`. He wrote `scripts/check.sh`; `ls -l` shows it as `-rwxrwxrwx`, and `./scripts/check.sh` runs on his laptop. He committed and pushed it. On GitHub, the new workflow step fails:

```text
/home/runner/work/_temp/3f9d2c1e-7b4a-4e8f-9a61-2c5d8e0b7f14.sh: line 1: ./scripts/check.sh: Permission denied
```
""",
        [
            part(
                "1",
                "Why does the script run for Ben but not in CI?",
                2,
                "Under `/mnt/c`, the Windows disk, every file shows as `rwxrwxrwx` and `chmod` silently does nothing, so the local run proves nothing. git cannot trust the `rwx` it sees there, so it recorded `check.sh` as a normal file (`100644`), and CI's fresh clone gets no `x`.",
                [
                    "Under `/mnt/c` every file shows `rwxrwxrwx` and `chmod` silently does nothing, so the local listing proves nothing",
                    "git stores the `x` bit; CI clones what git recorded, which has no `x`",
                ],
                '"GitHub\'s machines have different permissions" stops at the symptom. "The script has an error" ignores that the message is about permission, before any line ran. Answers that never mention `/mnt/c` miss why Ben\'s own listing misled him.',
            ),
            part(
                "2",
                "What should Ben do, step by step, in words?",
                2,
                "Clone the repository into his Linux home, under `~/code`, and check that `pwd` starts with `/home/`. There, run `chmod +x scripts/check.sh`, confirm the `x` with `ls -l`, then commit and push, so git records the mode and CI can run the script.",
                [
                    "Move or clone the project into `~/code` (`pwd` starting with `/home/`)",
                    "`chmod +x` there, then commit and push so git records the mode change",
                ],
                '"Run `chmod +x` again" in the same `/mnt/c` folder changes nothing, as slide 20 says. Moving the project without committing the mode change leaves CI exactly where it was. "Ask GitHub support" treats a repository problem as an outside one.',
            ),
            part(
                "3",
                "A teammate suggests adding a `chmod 777 scripts/check.sh` step to the workflow instead. Your verdict?",
                1,
                "No. It hides the cause: every other clone, a marker's included, would still get a script without `x`, and 777 also makes it writable by everyone.",
                [
                    "Rejects it: the repository still has no `x` (other clones fail) and/or 777 gives everyone write access"
                ],
                '"Fine, CI is green" accepts a patch on the referee instead of fixing the repository it checks. "777 is not allowed on GitHub" invents a rule: the real objections are the hidden cause and the write access for everyone.',
            ),
        ],
        """
Three statements from slide 20 form one chain: under `/mnt/c` every file shows `rwxrwxrwx` and `chmod` silently does nothing; keep projects in `~/code`; CI needs the `x` bit, and git remembers it. The local run proves nothing about what git recorded. A real run of the same step on a fresh clone without the bit produces the log line above; after `chmod +x` in a Linux folder and a commit, `git diff` shows `old mode 100644` / `new mode 100755`, and a fresh clone has the `x` bit. When git finds that `chmod` has no effect, as under `/mnt/c`, it sets `core.fileMode` to `false` and stops trusting the `x` bits it sees; a real run with that setting records a `rwxrwxrwx` file as `100644`.
""",
    )
)

# --- s9 ------------------------------------------------------------------
add(
    mcq(
        38,
        "exam",
        ["predict-output", "read-tool-output"],
        9,
        "labs/09-terminal.md exercise 3 Q3; S9 slide 21",
        "lab",
        "run",
        """
```console
$ chmod 600 run.sh
$ ls -l run.sh
-rw------- 1 alice alice 40 Oct 13 10:12 run.sh
```

Lab 09 asks what alice can now do. What happens with `./run.sh` and with `cat run.sh`?
""",
        [
            opt(
                "Both work: 600 only restricts the other users, never the owner.",
                "The owner's letters are `rw-`: no `x`, so even alice cannot run it.",
            ),
            opt(
                "Neither works: 600 locks the file completely until it is changed back.",
                "The owner keeps `r` and `w`, so reading and editing still work.",
            ),
            opt(
                "`./run.sh` says Permission denied; `cat run.sh` still prints the script.",
                "Right: 6 is `rw-` (4 + 2), with no 1 for execute, and alice kept `r`.",
                True,
            ),
            opt(
                "`./run.sh` works because alice owns it; `cat run.sh` fails because the group lost `r`.",
                "Owning a file does not make it runnable, and `cat` run by alice uses the owner's letters, which include `r`.",
            ),
        ],
        """
Turn the number back into letters per group of three: 6 = 4 + 2 = `rw-` for the owner, 0 = `---` for the group, 0 = `---` for everyone else. That is slide 21's private-key setting: only the owner can read and write. Without `x`, the shell refuses to run the script; with `r`, `cat` reads it. The real run shows `bash: ./run.sh: Permission denied`, then the two lines of the script from `cat`.
""",
    )
)

add(
    mcq(
        39,
        "hard",
        ["judgement"],
        9,
        "S9 slide 21",
        "slides",
        "source",
        """
After "Permission denied" on `scripts/check.sh`, a teammate ran `chmod 777 scripts/check.sh`, saw the script run, and wants to close the issue. Which review comment is right?
""",
        [
            opt(
                "Fine: 777 is the standard setting for scripts, so nothing else is needed here.",
                'The slide\'s setting for a script is 755; 777 is "almost never the answer".',
            ),
            opt(
                "Use 600 instead: a script should be private, like an SSH key.",
                "600 has no `x` at all: the script would be denied again, and CI could not run it.",
            ),
            opt(
                "Use 644 instead: scripts kept in a repository should never be executable.",
                "644 is a normal file with no `x`, so `./scripts/check.sh` would fail again.",
            ),
            opt(
                "Use 755: only `x` was missing, and 777 lets anyone rewrite what CI runs.",
                "Right: 755 is `rwxr-xr-x`, run by all, changed only by the owner; 777 gives every user write access to the script CI runs.",
                True,
            ),
        ],
        """
Slide 21: `chmod 777` makes the error go away and the problem worse. "Permission denied" meant one thing: no `x`. 777 adds it, and also lets every user on the machine change the very script that decides whether CI is green. The right number adds only what was missing: 755 (`rwxr-xr-x`), or simply `chmod +x`. The other two numbers are real settings for other kinds of file: 600 for a private key, 644 for a normal file.
""",
    )
)

add(
    mcq(
        40,
        "core",
        ["judgement"],
        9,
        "S9 slide 22; labs/09-terminal.md (work on a copy)",
        "slides",
        "source",
        """
In a teammate's script you meet `cp -p` and do not know what `-p` does. What does session 9 suggest?
""",
        [
            opt(
                "Read `man cp`, or the shorter `cp --help`: you look flags up when you need them.",
                "Right: slide 22 lists `man` and `--help`, and says such details are not examined as recall.",
                True,
            ),
            opt(
                "Run the script on your real project and see what changes.",
                "Lab 09's rule is to work on a copy; trying unknown commands on the original is how data gets lost.",
            ),
            opt(
                'Assume it means "path", since that is what `-p` means for most commands.',
                "The same letter means different things in different commands; guessing is what the manual saves you from.",
            ),
            opt(
                "Delete `-p` from the script, since a flag you do not know cannot matter much.",
                "Removing it changes what the script does, without knowing how.",
            ),
        ],
        """
Slide 22 lists a few more tools: `man ls` (the manual; `q` quits), `ls --help` (shorter), `whoami`, `date`, `uname -a`, `df -h`, `top` and `nano`. Its last line is the important one: you may look these up when they are needed; they are not examined as recall. The mid-term says the same: judgement, not memorised flags. What is examined is the judgement in this question: look it up, and never experiment on the original data.
""",
    )
)

add(
    sort_q(
        41,
        "exam",
        ["concept", "judgement"],
        9,
        "S9 slide 21; labs/00-setup.md (ssh-keygen)",
        "slides",
        "source",
        """
Sort each file or folder into the permissions it should have, using slide 21's typical uses.
""",
        [
            ("p644", "644 (`rw-r--r--`)"),
            ("p755", "755 (`rwxr-xr-x`)"),
            ("p600", "600 (`rw-------`)"),
        ],
        [
            ("`README.md`", "p644", "A normal file: you edit it, others read it, nobody runs it."),
            (
                "`scripts/check.sh`, which CI runs as `./scripts/check.sh`",
                "p755",
                "A script: everyone may run it, only the owner changes it.",
            ),
            (
                "`~/.ssh/id_ed25519`, your private SSH key",
                "p600",
                "A private key: nobody but you may even read it, and `ssh` refuses it otherwise.",
            ),
            (
                "`~/.ssh/id_ed25519.pub`, the key you pasted into GitHub",
                "p644",
                "The public half is meant to be shared, so others may read it.",
            ),
            (
                "The `src/` folder",
                "p755",
                "A folder needs `x` to be entered; 755 allows everyone in and only you to change it.",
            ),
            (
                "`expenses.csv`, the sample data",
                "p644",
                "Data, not a program: read by all, written by you.",
            ),
            (
                "`src/expense_tracker/report.py`",
                "p644",
                "A module the package imports, not a program, so no `x`.",
            ),
            (
                "The `tests/` folder",
                "p755",
                "Like every folder, it needs `x` so that you, and pytest, can enter it.",
            ),
        ],
        """
Slide 21 pairs each number with a typical use: 644 a normal file, 755 a script or a folder, 600 a private key, 777 almost never. For each item ask two questions. Does it run, or is it a folder? Then it needs `x`: 755. Must others not even read it? Then 600. Everything else is a normal file: 644. On Ubuntu your own files often show as `rw-rw-r--` (664) and folders as `rwxrwxr-x` (775), because your group is just you; the judgement is the same.
""",
    )
)

add(
    open_q(
        42,
        "beyond",
        ["read-tool-output", "judgement"],
        9,
        "S9 slide 21; labs/00-setup.md (ssh-keygen, SSH key)",
        "slides",
        "run",
        """
alice copies her SSH key from her old laptop with a USB stick. The next time she connects to GitHub, the output starts with these lines:

```text
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for '/home/alice/.ssh/id_ed25519' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/alice/.ssh/id_ed25519": bad permissions
```
""",
        [
            part(
                "1",
                "What is ssh complaining about? Write `0644` as letters and say who can do what.",
                2,
                "644 is `rw-r--r--`: alice can read and write the key, and her group and everyone else can read it. A private key is what proves she is alice, so ssh refuses to use one that other users can read.",
                [
                    "Translates 644 into `rw-r--r--` (owner read and write, group and others read)",
                    "Explains that others can read the private key, so ssh ignores it",
                ],
                '"The key is broken" ignores the message, which names the permissions. Translating 644 as "read, write, execute" mixes up the arithmetic: 6 is 4 + 2, read and write, and 4 is read only. "The permissions are wrong" without saying who can read the key misses the point of the warning.',
            ),
            part(
                "2",
                "Which permissions should the file have, as a number and in letters, and why not 755?",
                2,
                "600, `rw-------`: only alice can read and write it. Not 755: a key is not a program, so it needs no `x`, and 755 would still let everyone read it.",
                [
                    "600 / `rw-------` (owner only)",
                    "Rejects 755: a key needs no `x`, and 755 still allows group and others to read it",
                ],
                'Answering 700 or 755 "to be safe" adds an `x` that a key never needs, and 755 keeps it readable by others. Giving the number without the letters, or the letters without saying whom they apply to, earns half.',
            ),
            part(
                "3",
                'Her friend says: "just `chmod 777` it so ssh stops complaining". What happens?',
                1,
                "It makes things worse: with 777 everyone can read and change the key, and ssh still refuses it, now saying `Permissions 0777 ... are too open`.",
                [
                    "777 is more open, not less: ssh still refuses the key, and everyone could read and change it"
                ],
                '"777 gives ssh permission" misreads the warning: ssh refuses because others have access, so more access cannot fix it. This is slide 21\'s line in a new place: 777 makes the problem worse, and here it does not even make the error go away.',
            ),
        ],
        """
A small step beyond the slides, using only their table: slide 21 lists 600 as the typical use for a private key, and this is what happens when the rule is broken. `ssh-keygen` (lab 00) creates the key as 600 and the `.pub` file as 644; copying a key from a USB stick is a typical way to lose the 600. A real run shows this warning for 0644, the same refusal for 0777, and the key loading normally again after `chmod 600`.
""",
    )
)

# --- review additions ----------------------------------------------------
add(
    open_q(
        43,
        "exam",
        ["read-diff", "compare", "judgement"],
        8,
        "S9 slides 19–21; sample Q8 (compare shape)",
        "slides",
        "run",
        """
Before tagging v0.5, Ben runs `chmod +x scripts/check.sh` in the group repository, in his Linux home, and looks at what git sees:

```console
$ git status --short
 M scripts/check.sh
$ git diff
diff --git a/scripts/check.sh b/scripts/check.sh
old mode 100644
new mode 100755
```

He offers two commit messages:

- A: `fix ci`
- B: `Make scripts/check.sh executable so CI can run it`
""",
        [
            part(
                "1",
                "What does this change do, and why does git call the file modified when no line of it changed?",
                2,
                "It makes the script executable: git's record of the file goes from 644, a normal file, to 755, a script, so `./scripts/check.sh` can run. git records each file's mode as well as its lines, so the mode change is a modification, and every fresh clone, CI's included, gets it.",
                [
                    "Says the script becomes executable: mode 644 to 755, the `x` bit added, so `./scripts/check.sh` can run",
                    "Says git records the file mode as well as the content, so the change shows as modified and reaches every clone, CI's included",
                ],
                '"Nothing changed, the diff is empty" misses the two mode lines: the `x` bit is the change. "Now everyone can edit the script" misreads 755: only the owner has `w`. "It makes the script run as administrator" confuses execute permission with a different user. Saying only "it changes permissions", without naming the `x` bit or saying that git stores it, earns half.',
            ),
            part(
                "2",
                "Which message is better for someone reading the history six months later, and why?",
                2,
                "B. It names the file, the change and the reason, so a reader of `git log` knows what happened without opening the diff. A names neither file nor change, and the diff has no changed lines, so the commit could pass for empty.",
                [
                    "Chooses B because it says what changed (which file, made executable) and why (so CI can run it)",
                    "Says A is vague: no file and no change, so the reader must open the diff, where a mode-only change looks empty",
                ],
                '"B, because it is longer" gives no reason: the point is what the message tells the reader, not its length. "A is fine because the team knows what it means" forgets the reader six months later, who was not there. Choosing B without saying what A fails to tell the reader earns one mark.',
            ),
            part(
                "3",
                "Name one check, in words, that shows the change worked before you tag v0.5.",
                1,
                "Push and check that CI's step running `./scripts/check.sh` no longer says Permission denied, or clone the repository into a new folder and see the `x` with `ls -l`.",
                [
                    "A check on a fresh copy, not his own folder: the CI run on the pushed commit, or a fresh clone in the Linux home showing `x` on the script"
                ],
                '"Run it again on my laptop" proves nothing about what git recorded: his own copy already has the bit, committed or not. "Write a test for it" is too vague to mark: say what you would run and what you expect to see.',
            ),
        ],
        """
The compare shape of sample Q8, applied to session 9. A diff can change something other than lines: `old mode 100644` / `new mode 100755` is git recording that `scripts/check.sh` became executable, and the last three digits are slide 21's numbers (644 a normal file, 755 a script). Slide 20 says why it matters: in CI the script needs the `x` bit, and git remembers it. A good message says what the change does and why, which matters most when the diff itself looks empty. The check has to look at a fresh copy, because CI does not use your folder: it clones what git recorded. A real run gives the same `git status` and `git diff` output, and a fresh clone of the commit has the `x` bit.
""",
    )
)

add(
    sort_q(
        44,
        "hard",
        ["read-tool-output", "judgement"],
        4,
        "S9 slides 10–11, 14, 17–20; labs/09-terminal.md exercises 2–3",
        "lab",
        "run",
        """
Each line is the first error a student saw, with what they had just done. Sort each one by what is really wrong.
""",
        [
            ("wrongdir", "Wrong current directory"),
            ("nox", "No `x` permission"),
            ("notpath", "Not in `PATH`: `./` missing"),
            ("kind", "A file and a folder mixed up"),
        ],
        [
            (
                "`could not read expenses.csv`, just after `pwd` printed `/home/alice/code/expense-tracker/tests`",
                "wrongdir",
                "The relative name was read from `tests`; the file is in the project root.",
            ),
            (
                "`bash: cd: expense-tracker: No such file or directory`, just after `pwd` printed `/home/alice`",
                "wrongdir",
                "The project is inside `~/code`, so from home the relative name points nowhere.",
            ),
            (
                "`bash: ./run.sh: Permission denied`, where `ls -l run.sh` shows `-rw-rw-r--`",
                "nox",
                "No `x` in any group: nobody has said this file is a program.",
            ),
            (
                "`bash: cd: reports: Permission denied`, where `ls -ld reports` shows `drw-rw-r--`",
                "nox",
                "For a folder, `x` means enter it, and even the owner has none.",
            ),
            (
                "`/home/runner/work/_temp/3f9d2c1e-7b4a-4e8f-9a61-2c5d8e0b7f14.sh: line 1: ./scripts/check.sh: Permission denied`, in a CI log",
                "nox",
                "CI's clone has the mode git recorded, and nobody committed the `x` bit.",
            ),
            (
                "`run.sh: command not found`, right after `./run.sh` printed `report ready`",
                "notpath",
                "The file runs, so nothing is missing from it; without `./` the shell only searches the folders in `PATH`.",
            ),
            (
                "`cp: -r not specified; omitting directory 'reports'`",
                "kind",
                "`reports` is a folder, and plain `cp` copies files; a folder needs `cp -r`.",
            ),
            (
                "`bash: cd: reports/2025: Not a directory`, after `mv reports/notes.txt reports/2025`",
                "kind",
                "No folder `2025` existed, so `mv` renamed the file to `2025`, and `cd` was then asked to enter a file.",
            ),
        ],
        """
Session 9's errors fall into a few kinds, and each kind has its own fix. Two lines that both end in `Permission denied`, or two that both say a name is missing, can mean different things, so read the path in the error against what happened just before it: `pwd`, `ls -l`, or the previous command. Wrong folder: move, or give a path that is right from where you stand. No `x`: `chmod +x` in your Linux home, committed for CI, never 777. Not in `PATH`: type `./`. File and folder mixed up: `cp -r` for a folder, and `ls` before `mv`, which renames when the target folder does not exist. Every line here comes from a real run shown elsewhere in this module.
""",
    )
)

add(
    mcq(
        45,
        "beyond",
        ["read-tool-output", "concept"],
        8,
        "S9 slides 18–20; S3 slides 9 and 15, labs/00-setup.md (bash scripts/setup-check.sh)",
        "slides",
        "run",
        """
```console
$ ls -l run.sh
-rw-rw-r-- 1 alice alice 40 Oct 13 10:12 run.sh
$ ./run.sh
bash: ./run.sh: Permission denied
$ bash run.sh
report ready
```

A teammate concludes that the `x` bit is pointless, since `bash run.sh` works without it. What is the best reply?
""",
        [
            opt(
                "`bash` ignores permissions on every file, so it can even run scripts that nobody may read.",
                "`bash` still has to read the file. Once `r` is removed (`chmod 200 run.sh`, `--w-------`), `bash run.sh` is refused too: `bash: run.sh: Permission denied`.",
            ),
            opt(
                "`bash run.sh` runs `bash`, which only reads the file; `./run.sh` runs the file itself.",
                "Right: reading needs `r`, which alice has; running the file as a program needs `x`, which nobody has.",
                True,
            ),
            opt(
                "`bash run.sh` quietly adds the `x` bit for one run, then takes it away again afterwards.",
                "Nothing changes the mode: `ls -l` still shows `-rw-rw-r--`. Only `chmod` changes permissions.",
            ),
            opt(
                "He is right: in CI, `./scripts/check.sh` will also run without `x` if the file is readable.",
                "`./scripts/check.sh` asks to run the file itself, which needs `x` on every machine. That is why slide 20 says CI needs the bit and git remembers it.",
            ),
        ],
        """
Slide 19's rule, no `x`, no run, is about running a file as a program: `./run.sh` asks the operating system to start the file itself, and that needs `x`. `bash run.sh` starts a different program, `bash`, and gives it the file to read, which needs only `r`. It is also how session 3 and lab 00 run `bash scripts/setup-check.sh`, which works whether or not the file has `x`. The bit still matters whenever a script is run by its own name, as `./scripts/check.sh` is in CI. A real run confirms all of it: with `rw-rw-r--`, `./run.sh` is denied and `bash run.sh` prints `report ready`; after `chmod 200 run.sh`, `bash run.sh` is refused as well.
""",
    )
)

add(
    mcq(
        46,
        "core",
        ["concept", "judgement"],
        1,
        "S9 slide 6",
        "slides",
        "source",
        """
A teammate has to read a log file on a Linux server that the group rents. He connects with `ssh` and finds no desktop, no windows and no mouse, only a prompt. Which of session 9's reasons for the terminal explains why that prompt is all he gets?
""",
        [
            opt(
                "It composes: small programs joined by pipes can answer any question about a log.",
                "True of the terminal, but it does not explain why there is nothing else on the server. Composition is about how commands combine, not where they run.",
            ),
            opt(
                "It scripts: whatever you typed once, you can save and run again.",
                "Also true, and useful for a log you read every week. It does not explain why the server offers only a prompt.",
            ),
            opt(
                "It works over `ssh`: every server you will ever touch has a terminal, and nothing else.",
                "Right: slide 6 gives exactly this as one of its reasons. A server is managed from a command line because that is all it is guaranteed to have.",
                True,
            ),
            opt(
                "CI is a terminal: the check workflow is a list of commands another computer types.",
                "True, and the same idea (the machine at the other end has no screen to click). But the situation here is a server reached by `ssh`, which slide 6 names separately.",
            ),
        ],
        """
Slide 6 lists reasons why a 50-year-old interface survived: it composes, it scripts, it works over `ssh`, CI is a terminal, and "a GUI is for doing something once, a terminal for doing it a hundred times". They are all true; the question is which one fits the situation. A rented server, reached from your laptop, has to work with whatever every server has, which is a command line. That is the `ssh` reason, in the slide's words: "every server you will ever touch has one, and nothing else". Pipes and scripts then make that prompt worth having.
""",
    )
)

# ---------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------

EXAM_FOCUS = """
- A transcript with `pwd`, `cd` and an error such as `could not read expenses.csv`: say where the student is and what to type next (`pwd` first).
- A sequence of `cd` commands with `..`, `../..`, `~`, `cd -` or a plain `cd`: predict what `pwd` prints, or decide which of two paths names the same file.
- An `ls -l` or `ls -la` listing: which entries are folders, which are hidden, who can write, what can be run.
- The "permission denied" transcript: what is missing, what `chmod +x` states, why `./`, and why `chmod 777` is the wrong fix.
- Letters and numbers inside a judgement: 755 for `check.sh`, 600 for a private key, 644 for a normal file.
- Predicting what a careless `rm -r name *` removes, and naming the habits that prevent it.
- Linking the terminal to CI: the workflow is commands another computer types, `check.sh` needs its `x` bit committed (a diff with only `old mode 100644` / `new mode 100755`), and `/mnt/c` hides the problem.
- Not examined: flags as recall (`man`, `--help`, `whoami`, `df -h`, `top`, `nano`).
""".strip()

MODULE: dict[str, Any] = {
    "id": MID,
    "order": 9,
    "module": "M3",
    "title": "The terminal: paths, files and permissions",
    "sessions": [9],
    "predicted": False,
    "sources": [
        "slides-session-9",
        "labs/09-terminal.md",
        "labs/00-setup.md",
        "slides-session-3 (slide 12, terminal survival kit)",
        "expense-tracker v0.4 (cli.py, check.yml)",
    ],
    "summary_md": (
        "Session 9 opens Module 3 and turns the terminal you have used since session 3 into something you can reason about. "
        "It separates the terminal (the window), the shell (`bash` or `zsh`, which reads your line) and the operating system "
        "(which creates files and starts programs), and explains why a 50-year-old interface survived: it composes, it scripts, "
        "it works over `ssh`, and CI is a terminal. It then teaches the one tree under `/`, absolute and relative paths, and the "
        'rule that most "file not found" errors are the wrong current directory. It ends with managing files (`rm` is permanent) '
        "and permissions: no `x`, no run, and `chmod +x` is a statement that a file is a program."
    ),
    "exam_focus_md": EXAM_FOCUS,
    "sections": [{**sec, "body_md": sec["body_md"].strip()} for sec in SECTIONS],
    "terms": [{"term": t, "definition_md": d, "section_ref": s(n)} for t, d, n in TERMS],
    "traps": TRAPS,
    "flashcards": [
        {"id": f"{MID}-f{i:02d}", "front_md": f, "back_md": b, "kind": k, "section_ref": s(n)}
        for i, (f, b, k, n) in enumerate(FLASHCARDS, start=1)
    ],
    "questions": QUESTIONS,
}


def main() -> None:
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(MODULE, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {OUT} ({len(QUESTIONS)} questions)")


if __name__ == "__main__":
    main()
