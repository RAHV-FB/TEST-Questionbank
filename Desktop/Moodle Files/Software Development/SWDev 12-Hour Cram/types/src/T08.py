"""Cram exercise type T08: Paths, files and permissions.

Run: python3 types/src/T08.py   -> writes types/T08.json
The worked examples are copied verbatim from the verified bank (terminal-files) at build time.
"""

import json
from pathlib import Path

CRAM = Path(__file__).resolve().parent.parent.parent
SITE = CRAM.parent / "study-site"
BANK = {q["id"]: q for q in json.load(open(SITE / "content" / "terminal-files.json", encoding="utf-8"))["questions"]}
POOL = {q["id"] for q in json.load(open(CRAM / "pools.json", encoding="utf-8"))["pools"]["T08"]}


def bank_md(qid: str) -> str:
    """Stem plus options of a bank mcq, verbatim, in a–d order."""
    q = BANK[qid]
    lines = [q["stem_md"].rstrip(), ""]
    for letter, opt in zip("abcd", q["options"]):
        lines.append(f"- {letter}) {opt['text_md']}")
    return "\n".join(lines)


def correct_letter(qid: str) -> str:
    return "abcd"[[o["correct"] for o in BANK[qid]["options"]].index(True)]


basics = [
    {
        "id": "T08-b1",
        "heading": "Terminal, shell, operating system and the one tree",
        "body_md": """Three words get mixed up. Keep them apart.

| | What it is | Example |
|---|---|---|
| Terminal | The window. It shows text and sends your keystrokes | Windows Terminal, GNOME Terminal |
| Shell | The program inside it that reads a line and runs it | `bash`, `zsh` |
| Operating system | What creates files and starts programs | the Linux kernel |

Terminal and shell swap independently. Your scripts depend on the shell, not on the window. The shell also cuts your line into words at the spaces and turns `*` into a list of names before any program starts.

The terminal survived 50 years for four reasons. It composes (small programs joined by pipes). It scripts (type once, save, rerun). It works over `ssh` (every server has a prompt and nothing else). CI is a terminal. A GUI is for doing something once. A terminal is for doing it a hundred times.

Everything sits in one tree under `/`. There are no drive letters. Your home is `/home/alice` (`/Users/alice` on a Mac), written `~`. On WSL your Windows disk is `/mnt/c`, and projects belong in `~/code`.

```console
$ ls
LICENSE  README.md  expenses.csv  pyproject.toml  src  tests  uv.lock
$ ls -a
.  ..  .git  .github  .gitignore  .python-version  LICENSE  README.md  ...
```

`ls` hides names that start with a dot. That is why you never see `.git`, and why a missing `.git` does not mean a broken clone. `.` is the folder you are in and `..` is its parent. `find` does not skip dot names: from `.` it also walks into `.venv`.""",
    },
    {
        "id": "T08-b2",
        "heading": "Paths, cd and the wrong-folder error",
        "body_md": """A path names a file by the folders you pass through. The first character tells you which kind.

| Path | Kind |
|---|---|
| `/home/alice/code/expense-tracker` | Absolute. Starts at `/`. Same from anywhere |
| `src/expense_tracker/cli.py` | Relative. Starts here |
| `../tests` | Up one level, then down |
| `~/code` | Your home, then `code` |

"Here" is what `pwd` prints. A relative path is read from there, so the same text names different files in different places. `..` is one level up, `../..` is two. `cd -` goes back to where you just were. `cd` alone goes home. Tab completes a name; if it does not complete, the name is wrong or ambiguous. The project has a hyphen (`expense-tracker`), the package folder an underscore (`expense_tracker`).

The rule from slide 10: most "file not found" errors are the wrong current directory. Run `pwd` first. A program reads and writes its relative paths from where you stand, not from where its code lives.

```console
$ pwd
/home/alice/code/expense-tracker/tests
$ uv run expenses report expenses.csv
could not read expenses.csv
$ echo $?
1
```

The program ran and failed well: it named what it could not read and exited with 1. Nothing is broken. Go to the folder that holds the file, or give a path that is right from here, such as `../expenses.csv`. Reinstalling, `chmod 777` and editing the code are the careless answers. By the same rule, `expenses add` run in `tests` creates `tests/data/expenses.csv`.""",
    },
    {
        "id": "T08-b3",
        "heading": "Copy, move, remove, and the space before the star",
        "body_md": """Slide 14 runs six lines, using five commands.

```console
$ mkdir notes
$ touch notes/todo.txt
$ cp notes/todo.txt notes/todo-backup.txt
$ cp -r notes notes-old
$ mv notes/todo-backup.txt notes/old.txt
$ rm notes/old.txt
```

| Command | What it does |
|---|---|
| `mkdir`, `touch` | Make a folder, make an empty file |
| `cp`, `cp -r` | Copy a file; copy a folder and everything in it. Without `-r` a folder is skipped: `cp: -r not specified; omitting directory 'reports'` |
| `mv` | Move, and also rename |
| `rm` | Remove. It does not ask and there is no bin |

Afterwards `notes` holds `todo.txt`, and `notes-old` holds `todo-backup.txt` and `todo.txt`. Follow the files line by line, as they are at that moment. `mv` has one rule: if the target is an existing folder the file goes inside it, otherwise the target is the new name.

Slide 15 shows two lines that differ by one space.

```console
$ rm -r notes-old
$ rm -r notes-old/ *
```

The space makes `*` an argument of its own. The shell, not `rm`, turns `*` into every name in the current folder (dot names excluded) before `rm` starts, and `-r` removes the folders too. In `~/lab09`, where `ls` shows `reports  reports-copy`, the line `rm -r reports-copy *` reaches `rm` as `rm -r reports-copy reports reports-copy`. Both folders go. The only message is the complaint about the second `reports-copy`.

The habits: `ls` the exact path, press ↑, swap `ls` for `rm`. Use `rm -i` when tired. Never `rm -rf` with a variable you have not printed.""",
    },
    {
        "id": "T08-b4",
        "heading": "Permissions, chmod +x and why CI cares",
        "body_md": """```console
$ ls -l
-rw-rw-r-- 1 alice alice  1193 Oct 11 17:07 README.md
drwxrwxr-x 3 alice alice    60 Oct 11 17:07 src
```

Read the first ten characters. The first is the type: `-` file, `d` directory. Then three groups of three: owner, group, everyone else. `r` read, `w` write, `x` execute; for a folder, `x` means you may enter it. `README.md` can be changed by alice and her group, only read by everyone else, and run by nobody.

```console
$ ./hello.sh
bash: ./hello.sh: Permission denied
$ chmod +x hello.sh
$ ./hello.sh
hello
```

No `x`, no run. A new file never gets it. `chmod +x` states that the file is a program. `./` means this folder; without it the shell searches only `PATH` and says `command not found`. `bash hello.sh` needs only `r`, because it runs `bash` and hands it the file.

Numbers: r = 4, w = 2, x = 1, added per group.

| Number | Letters | Use |
|---|---|---|
| 644 | `rw-r--r--` | A normal file |
| 755 | `rwxr-xr-x` | A script or a folder |
| 600 | `rw-------` | A private key |
| 777 | `rwxrwxrwx` | Almost never the answer |

777 makes the error go away and the problem worse: only the `x` was missing, and now everyone can edit the file.

On WSL, a project under `/mnt/c` shows every file as `rwxrwxrwx` and `chmod` silently does nothing. CI clones what git recorded, so `scripts/check.sh` needs its `x` bit committed. The diff shows only `old mode 100644` and `new mode 100755`.""",
    },
]

checks = [
    {
        "id": "T08-c1",
        "q_md": "A teammate says she \"runs her script in the terminal\". Which of these is the program that actually reads the line and runs it?",
        "options": ["Windows Terminal", "The Linux kernel", "`bash`"],
        "answer": 2,
        "why_md": "`bash` is the shell. Windows Terminal is only the window, and the kernel is the operating system, which creates files and starts programs once the shell asks.",
    },
    {
        "id": "T08-c2",
        "q_md": "In the expense-tracker folder, `ls` does not show `.gitignore`, but you know the file exists. Which command shows it?",
        "options": ["`ls -a`", "`ls -l`", "`cd ..`"],
        "answer": 0,
        "why_md": "`ls` hides names that start with a dot. `ls -a` shows them, plus `.` and `..`. `ls -l` lists the same visible names in long form.",
    },
    {
        "id": "T08-c3",
        "q_md": "`pwd` prints `/home/alice/code/expense-tracker/tests`. She types `cd ../..`. What does `pwd` print now?",
        "options": [
            "`/home/alice/code/expense-tracker`",
            "`/home/alice/code`",
            "`/home/alice`",
        ],
        "answer": 1,
        "why_md": "The first `..` goes from `tests` to `expense-tracker`, the second to `code`. Each `..` is one level up.",
    },
    {
        "id": "T08-c4",
        "q_md": "`ls` shows `draft.txt  notes`. You type `rm -r notes *`. What does `rm` receive?",
        "options": [
            "Only `notes`, because the space makes the shell ignore the star.",
            "`notes` and a file literally called `*`, which `rm` then looks for.",
            "`notes`, `draft.txt` and `notes` again, after the shell expanded the star.",
        ],
        "answer": 2,
        "why_md": "The space makes `*` a separate argument, and the shell replaces it with every name in the folder before `rm` runs. `rm` never sees the star. Both `draft.txt` and `notes` are removed.",
    },
    {
        "id": "T08-c5",
        "q_md": "Write `rwxr-xr-x` and `rw-------` as numbers. Which pair is right?",
        "options": ["755 and 600", "644 and 600", "755 and 700"],
        "answer": 0,
        "why_md": "`rwxr-xr-x` is 4+2+1, 4+1, 4+1 = 755. `rw-------` is 4+2, 0, 0 = 600. 700 would give the owner an `x` that a private key does not need.",
    },
]

method = [
    "**Read the artefact as a story.** Each `$` line is a command and the lines under it are what happened. Find `pwd` (or the path in the prompt) first and write down where the student stands after every `cd`.",
    "**Turn paths into absolute ones on paper.** Start from `pwd`, apply each `..` and each name. Identical text from two folders is two different files.",
    "**Name the kind of error before you pick a fix.** `No such file or directory` or `could not read` usually means the wrong folder (read the path against `pwd`). `Permission denied` on a script means no `x`. `command not found` after a successful `./run.sh` means no `./`. `-r not specified` means a folder went to `cp`. `Not a directory` after a `mv` means `mv` renamed the file instead of moving it.",
    "**For `cp`, `mv` and `rm`, follow the files, not the commands.** Write the folder contents after each line. Expand `*` yourself, as the shell does: every name here, dot names excluded.",
    "**For `ls -l`, read the first character, then owner, group, everyone else.** Answer only what the question asks: who can change it, can it run, can it be entered.",
    "**Choose the smallest fix that matches the evidence.** Reject the careless reflexes: reinstall, delete `.venv`, clone again, `chmod 777`, edit working code. In an open answer write evidence from the transcript, then the rule, then the fix, in the course's words.",
]

w1 = "terminal-files-q12"
w2 = "terminal-files-q30"

worked = [
    {
        "title": "Worked 1: the file is there, the program cannot find it",
        "question_md": bank_md(w1),
        "steps_md": [
            "Read the story. `pwd` says alice is in `tests`. She ran the report command with the relative name `expenses.csv`. The program printed its own message and `echo $?` gave 1.",
            "The program printed a message of its own, so it started and its packages loaded. That already rules out option a, the reinstall. It also says it failed well: it named what it could not read.",
            "The question tells you the file is in the project root. The program looks for a relative name in the folder you stand in, so it looked for `tests/expenses.csv`. Diagnosis: wrong current directory.",
            "Check the other two. b treats a missing file as a permission problem, and 777 is almost never the answer. d fixes working code by hard-coding alice's home folder, which breaks on every other machine.",
        ],
        "answer_md": f"**{correct_letter(w1)}) Go up to the project root with `cd ..` (or pass `../expenses.csv`) and run the same command again.** Most file-not-found errors are the wrong current directory, so you read the path in the error against `pwd`. Nothing needs reinstalling, loosening or rewriting.",
    },
    {
        "title": "Worked 2: Permission denied on a new script",
        "question_md": bank_md(w2),
        "steps_md": [
            "Read the `ls -l` line first. `-rw-rw-r--` has an `r` and a `w` in the owner and group groups, and no `x` anywhere.",
            "A new file never gets execute permission, whether it comes from `printf`, `touch` or an editor. Nobody has said this file is a program. The refusal comes before a single line of the script runs, so the script itself is fine.",
            "The fix adds the one missing bit. That is `chmod +x run.sh`, and `ls -l` then shows `-rwxrwxr-x`.",
            "Check the others. a, 777, adds the `x` and gives everyone write permission too. b recreates the file, and the new copy is born without `x` again. c, `sudo`, changes who runs it, but the problem is that the file is not marked as a program.",
        ],
        "answer_md": f"**{correct_letter(w2)}) `chmod +x run.sh`.** The file has no `x`, and `chmod +x` states that it is a program. Add what is missing and nothing more: 777 makes the error go away and the problem worse.",
    },
]

twists = [
    {
        "twist_md": "The same failure shows with different wording: `zsh: permission denied: ./run.sh`, or a Mac listing with an `@` after the letters, such as `-rw-r--r--@`.",
        "how_md": "The message belongs to the shell (`bash` or `zsh`), the cause and the fix are unchanged: no `x`, so `chmod +x`. The `@` marks extended attributes on a Mac. Ignore it and read the ten letters.",
    },
    {
        "twist_md": "`cd reports` says `Permission denied`, and `ls -ld reports` shows `drw-rw-r--`. The owner has `r` and `w`.",
        "how_md": "For a folder, `x` means permission to enter it, and without it even the owner cannot go in or reach the files. Add the `x`, for example `chmod 755 reports`. This is why slide 21 gives 755 for a script or a folder.",
    },
    {
        "twist_md": "`mv reports/notes.txt reports/2025` when only `reports/2026` exists. Afterwards `cd reports/2025` says `Not a directory`.",
        "how_md": "`mv` is also rename. With no folder called `2025`, the target became the new name, so `notes.txt` is now a file called `2025`. Writing `reports/2025/` with a trailing slash would have made `mv` refuse instead.",
    },
    {
        "twist_md": "Compare `rm -r notes-old/*` with `rm -r notes-old/ *` in a folder showing `draft.txt  notes  notes-old`.",
        "how_md": "Count the arguments after the shell has expanded. `notes-old/*` is one argument and only empties `notes-old`. `notes-old/ *` is two: the folder, then every name here, so `draft.txt`, `notes` and `notes-old` all go.",
    },
    {
        "twist_md": "A clean-up script runs `rm -rf \"$REPORT_DIR/\"*`. You print the path first and `echo \"$REPORT_DIR/\"` shows only `/`.",
        "how_md": "The shell replaces the variable before `rm` runs, as it does the star. The variable is empty, so the line is `rm -rf /*`. Do not run it. Never `rm -rf` with a variable you have not printed.",
    },
    {
        "twist_md": "Ben works under `/mnt/c`, every file shows `-rwxrwxrwx`, `./scripts/check.sh` runs for him, and the CI log says `Permission denied`.",
        "how_md": "Under `/mnt/c`, `chmod` silently does nothing, so his listing proves nothing about what git recorded. Clone into `~/code`, check that `pwd` starts with `/home/`, run `chmod +x scripts/check.sh`, then commit and push. A `chmod 777` step in the workflow hides the cause.",
    },
    {
        "twist_md": "A teammate says a commit is empty. It shows `scripts/check.sh | 0` and a diff with only `old mode 100644` and `new mode 100755`.",
        "how_md": "Lines are not the only thing git records. It stores the mode, and 644 to 755 means the file became executable. Every fresh clone, CI's included, gets a runnable script. Dropping the commit brings back `Permission denied`.",
    },
    {
        "twist_md": "`./run.sh` is denied, but `bash run.sh` prints `report ready`. A teammate concludes the `x` bit is pointless.",
        "how_md": "`bash run.sh` starts `bash` and hands it the file to read, which needs only `r`. `./run.sh` asks to run the file itself, which needs `x`. CI runs `./scripts/check.sh`, so the bit matters there.",
    },
]

traps = [
    "\"The terminal runs my script.\" The terminal is only the window. The shell (`bash`, `zsh`) reads and runs the line, and the operating system creates files and starts programs.",
    "\"There is no `.git`, so the clone is broken.\" `ls` hides names that start with a dot. `ls -a` shows `.git`.",
    "\"File not found, so reinstall or clone again.\" Most file-not-found errors are the wrong current directory. Run `pwd` first, then read the path in the error against it.",
    "\"The program looks in the folder where its code lives.\" It reads and writes relative paths from where you stand. `expenses add` run in `tests` creates `tests/data/expenses.csv`.",
    "\"`cd -`, `cd` and `cd ..` are the same.\" `cd -` goes back to where you just were, `cd` alone goes home, `cd ..` goes up one level. Track `pwd` line by line.",
    "\"`rm -r old *` only removes `old`, and I can get it back from the bin.\" The space makes `*` an argument, the shell expands it to every name here, and `rm` has no bin.",
    "\"Permission denied, so `chmod 777`.\" Only the `x` was missing. 777 also lets everyone edit the file. Owning a file does not make it runnable either.",
    "\"It runs on my laptop, and `chmod` gave no error, so CI is fine.\" Under `/mnt/c`, `chmod` silently does nothing, and CI runs what git recorded. The `x` bit has to be committed.",
]

say_md = """- Terminal: "the window that shows text and sends keystrokes". Shell: "the program that reads a line and runs it" (`bash`, `zsh`). Operating system: "creates files and starts programs".
- "Terminal and shell swap independently. Scripts depend on the shell."
- "A GUI is for doing something once, a terminal for doing it a hundred times." "CI is a terminal."
- "`ls` hides names that start with a dot; `ls -a` shows them."
- "An absolute path starts at `/` and names the same file from anywhere. A relative path starts here."
- "Most file-not-found errors are the wrong current directory. Run `pwd` first."
- "A relative path is read from the folder you are standing in, not from where the code is."
- "`rm` has no bin. What it removes is gone."
- "The shell expands `*` before `rm` runs, and the space makes it a separate argument."
- "`ls` the exact path first, then ↑ and swap `ls` for `rm`." "`rm -i` asks first."
- Read `-rw-rw-r--` aloud: "a file; the owner and the group can read and write; everyone else can only read; nobody can execute it."
- "No `x`, no run. `chmod +x` states that this file is a program."
- "`./` means this folder; without it the shell only searches `PATH`."
- "For a folder, `x` means permission to enter it."
- "644 a normal file, 755 a script or a folder, 600 a private key. 777 makes the error go away and the problem worse."
- "Under `/mnt/c`, `chmod` silently does nothing. Keep projects in `~/code`."
- "CI clones what git recorded, so the `x` bit must be committed: `old mode 100644`, `new mode 100755`."
"""

practice = [
    "terminal-files-q05",  # core  mcq  hidden .git
    "terminal-files-q09",  # core  mcq  relative path from tests
    "terminal-files-q31",  # core  mcq  ./ and PATH
    "terminal-files-q02",  # exam  mcq  terminal, shell, OS swap
    "terminal-files-q07",  # exam  mcq  cd - and cd .. (predict pwd)
    "terminal-files-q14",  # exam  mcq  Tab does not complete
    "terminal-files-q21",  # exam  mcq  rm -r reports-copy *
    "terminal-files-q28",  # exam  mcq  folder without x
    "terminal-files-q16",  # exam  open wrong folder, twice
    "terminal-files-q29",  # exam  open ls -la reading and check.sh
    "terminal-files-q20",  # hard  mcq  mv renames
    "terminal-files-q39",  # hard  mcq  777 vs 755 review
    "terminal-files-q37",  # hard  open /mnt/c and CI
    "terminal-files-q35",  # beyond mcq mode-only diff
]

out = {
    "tid": "T08",
    "name": "Paths, files and permissions",
    "shape_md": "The teacher's sample paper has no question on session 9, so this type mirrors the form of sample Q1 (a `$` transcript, then \"what next?\") applied to the terminal. It can appear as multiple choice (what does the last command print, why does it fail, what can ben do) and as a 5–8 line open answer built on one transcript with 2–3 parts.",
    "minutes": 30,
    "one_md": "A terminal transcript tells you where you stand and what each file allows, so read the path against `pwd` and the letters against the question, then choose the smallest fix.",
    "spot_md": """- A short `console` block with `$` prompts: `pwd`, `ls`, `cd`, `ls -l`, `rm`, `mv`, `chmod`, ending in an error such as `could not read expenses.csv` or `Permission denied`.
- Question wording: "What should alice do next?", "Why does the last command fail?", "What does the last one print?", "What did `rm` remove?", "Which entries are folders?", "What can ben do with this file?".
- Letters and numbers inside a judgement: `-rw-rw-r--`, `rwxrwxrwx`, 755, 600.
- A CI log line ending in `Permission denied`, or a diff with only `old mode 100644` and `new mode 100755`.
- The open version is \"explain to a teammate\" or \"read tool output\": 2–3 parts, evidence from the transcript, the rule, then the fix.""",
    "basics": basics,
    "checks": checks,
    "method": method,
    "worked": worked,
    "twists": twists,
    "traps": traps,
    "say_md": say_md,
    "practice": practice,
}

# Self-checks
missing = [i for i in practice if i not in POOL]
assert not missing, f"practice ids not in pools[T08]: {missing}"
assert len(set(practice)) == len(practice)
assert w1 not in practice and w2 not in practice

dest = CRAM / "types" / "T08.json"
with open(dest, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write("\n")
print("wrote", dest)
