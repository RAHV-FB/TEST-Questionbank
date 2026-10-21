"""S1 (sample Q1): a tool error, what do you do next? Writes ../S1.json.

Real tool output is copied from the bank (project-anatomy-q35, sample-paper-q10) and the
teacher's sample files. Practice ids are mcq only, level core or exam.
"""

import json
from pathlib import Path

PARSE_ERROR = (
    "$ uv sync\n"
    "Using CPython 3.13.1\n"
    "error: Failed to parse `pyproject.toml`\n"
    "  TOML parse error at line 7, column 12"
)

LOCK_ERROR = (
    "$ uv sync --locked\n"
    "Using CPython 3.13.15\n"
    "Creating virtual environment at: .venv\n"
    "Resolved 20 packages in 5ms\n"
    "error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.\n"
    "\n"
    "hint: To update the lockfile, run `uv lock`."
)

S1 = {
    "tid": "S1",
    "name": "Tool error: what do you do next?",
    "minutes": 15,
    "shape_md": (
        "Sample Q1: a few lines of `uv` output and \"What should you do next?\". On the paper it is one "
        "multiple-choice question: one careful reading and three careless moves."
    ),
    "one_md": (
        "Read what the message names (a file, a line, a folder) and act there, "
        "never on something the message does not mention."
    ),
    "sample": {
        "qnum": "Q1",
        "kind": "mcq",
        "question_md": (
            "You run `uv sync` in a fresh clone of your group's repo and see:\n\n"
            "```console\n" + PARSE_ERROR + "\n```\n\n"
            "What should you do next?"
        ),
        "options": [
            "Delete `.venv` and run `uv sync` again",
            "Open `pyproject.toml` at line 7 and look for the syntax mistake",
            "Run `uv sync --upgrade` to refresh the packages",
            "Reinstall uv",
        ],
        "answer": 1,
        "his_answer_md": (
            "**b.** The error names the file and the line. Read it and fix the syntax. "
            "Deleting `.venv`, upgrading or reinstalling uv can't fix a malformed file."
        ),
        "decoded_md": (
            "- **The pattern.** Tool output, then \"what next?\". The output already names the place: "
            "`pyproject.toml`, line 7, column 12. The right option goes there.\n"
            "- **Why b is enough for full marks.** He gives the clue (file and line), the cause (a malformed "
            "file) and the action (fix the syntax). On an open version you would write those three.\n"
            "- **Why the others tempt.** a) feels like a reset, but uv stopped while reading the file and "
            "never built the environment. c) `--upgrade` changes package versions, which uv never reached. "
            "d) blames the tool that has just told you the line.\n"
            "- **What earns the because.** \"Deleting `.venv`, upgrading or reinstalling can't fix a malformed "
            "file.\" Each careless move fails for a reason you can state in one clause.\n"
            "- **Level.** Three sentences. No flags, no theory of virtual environments."
        ),
    },
    "spot_md": (
        "- A few lines of terminal output with a `$` prompt: `uv sync`, `uv run`, `git commit`, `git push`.\n"
        "- The question says \"What should you do next?\", \"What is the problem?\" or \"What does this show?\".\n"
        "- Three options are careless moves: delete `.venv`, reinstall, `--upgrade`, rerun and hope.\n"
        "- The clue is a file and a line, a `pwd` line, a command name, or a state such as `Untracked files`."
    ),
    "basics": [
        {
            "id": "S1-b1",
            "heading": "Find what the message names",
            "body_md": (
                "Every error in this shape names one thing. Find it, then act on it.\n\n"
                "| The output names | What you do |\n|---|---|\n"
                "| a file and a line (`Failed to parse pyproject.toml`, line 7) | open that file at that line and fix it |\n"
                "| a folder (`No pyproject.toml found`, and `pwd` shows `/home/alice`) | go to the cloned project folder |\n"
                "| a command (`Failed to spawn: expense`) | compare with `[project.scripts]`: the command is `expenses` |\n"
                "| a git state (`Untracked files`) | `git add`, then `git commit`, then `git push` |\n"
                "| two files that disagree (`.python-version` 3.12, `requires-python` `>=3.13`) | fix the file that changed |\n"
                "| `uv --version` says the command is not found, right after installing | open a new terminal |\n\n"
                "The skill is reading the message, not knowing uv."
            ),
        },
        {
            "id": "S1-b2",
            "heading": "Why the careless moves fail",
            "body_md": (
                "`.venv` is a product. The recipe is `pyproject.toml` plus `uv.lock`, and both live in git. "
                "Delete `.venv` and `uv sync` builds the same thing back. An error about reading "
                "`pyproject.toml` happens before uv touches the environment, so a rebuilt `.venv` changes nothing.\n\n"
                "`--upgrade` upgrades packages, not syntax and not the Python request. Reinstalling uv replaces a "
                "tool that is working: it ran, read the file and told you the line.\n\n"
                "Plain `uv sync` quietly rewrites `uv.lock`. CI runs `uv sync --locked`, which refuses a stale "
                "lockfile and prints the command that fixes it. The worked example below shows the output."
            ),
        },
    ],
    "checks": [
        {
            "id": "S1-c1",
            "q_md": "`uv sync` stops with `Failed to parse pyproject.toml ... line 14`. What was uv doing when it stopped?",
            "options": [
                "Building `.venv`",
                "Reading `pyproject.toml`",
                "Downloading packages",
            ],
            "answer": 1,
            "why_md": (
                "It could not read the file, so it did nothing else. `.venv` and `uv.lock` were never touched, "
                "which is why deleting `.venv` cannot help."
            ),
        },
        {
            "id": "S1-c2",
            "q_md": "You delete `.venv` by accident. What gives you the same environment back?",
            "options": [
                "Installing each package by hand",
                "`uv sync`, because `pyproject.toml` and `uv.lock` hold the recipe",
                "Cloning the repository again to get the old `.venv`",
            ],
            "answer": 1,
            "why_md": "`.venv` is built from the recipe and is listed in `.gitignore`, so even a clone does not contain it.",
        },
    ],
    "method": [
        "Read the output before the options. Write down what it names: a file, a line, a folder, a state.",
        "Say in one sentence what is wrong: \"uv could not read the file\", \"I am in the wrong folder\".",
        "Cross out the options that act on something the message never mentions: `.venv`, reinstall, `--upgrade`, rerun.",
        "Pick the option that acts on the named place.",
        "If it is open: clue, cause, fix in words, and why the careless move cannot work. Two or three sentences.",
    ],
    "worked": [
        {
            "title": "Same shape, other topic: a red CI step",
            "question_md": (
                "A teammate added a dependency to `pyproject.toml`, ran `uv sync` on their laptop (everything "
                "worked) and pushed. The CI step *Install dependencies from the lockfile* is red:\n\n"
                "```console\n" + LOCK_ERROR + "\n```\n\n"
                "What should happen next?\n\n"
                "- a) Run `uv lock` locally, commit the updated `uv.lock` and push it\n"
                "- b) Change the CI step to plain `uv sync` so it can update the lockfile itself\n"
                "- c) Delete `uv.lock` from the repository so there is nothing to disagree with\n"
                "- d) Re-run the CI job, since the lockfile check sometimes fails"
            ),
            "steps_md": [
                "The message names `uv.lock` and `--locked`, and its last line gives the command: `uv lock`.",
                "Plain `uv sync` on the laptop rewrote the lockfile quietly. Only `pyproject.toml` was pushed.",
                "b) changes the referee, c) leaves nothing to read, d) reruns a comparison that gives the same answer every time.",
            ],
            "answer_md": (
                "**a.** The error names the lockfile and its hint says `uv lock`. The new lockfile stayed on one "
                "laptop, so CI sees `pyproject.toml` and `uv.lock` disagree. Commit both."
            ),
        }
    ],
    "twists": [
        {
            "twist_md": "`.python-version` says 3.12 while `requires-python` says `>=3.13`, and uv stops with \"incompatible\".",
            "how_md": (
                "Two files ask for different Pythons. Put the one that changed back to 3.13, because uv installs "
                "Python itself. Deleting `.venv` changes nothing: uv stopped before it built anything."
            ),
        },
        {
            "twist_md": "A `git commit` that says `nothing added to commit but untracked files present`.",
            "how_md": "Name the state: the folder is untracked. `git add` stages it, then commit, then push.",
        },
        {
            "twist_md": "`uv --version` says \"not found\" in the same terminal window that ran the installer.",
            "how_md": "The shell started before the installer edited its startup file. Open a new terminal. Reinstalling does nothing.",
        },
        {
            "twist_md": "`No pyproject.toml found in current directory or any parent directory`, with `pwd` showing `/home/alice`.",
            "how_md": "She is not in the clone. Go to the folder that holds `pyproject.toml`. `uv init` would start a new, empty project.",
        },
        {
            "twist_md": "The open version: \"What does this output show, and what do you do?\"",
            "how_md": "Name the clue, give the cause in the course's words, describe the fix, then say why one careless option fails.",
        },
    ],
    "traps": [
        "\"Delete `.venv` and sync again\" feels like action. If the error is about a file uv could not read, the environment was never the problem.",
        "\"Reinstall uv.\" uv just ran and told you the line. The tool works and the file is wrong.",
        "\"`--upgrade` refreshes everything.\" It upgrades packages. It does not fix syntax, a folder or a Python request.",
        "\"Rerun it, maybe it was a glitch.\" A malformed file, a missing folder and a stale lockfile give the same output every time.",
    ],
    "say_md": (
        "- uv could not read `pyproject.toml`. The error names the file and the line, so I open it there and fix the syntax.\n"
        "- `.venv` is built from `pyproject.toml` and `uv.lock`. Deleting it rebuilds the same thing and cannot fix a malformed file.\n"
        "- The message names X, so the fix acts on X. The other options act on something it never mentions.\n"
        "- The new lockfile never left one laptop. `uv lock`, then commit `uv.lock` with `pyproject.toml`."
    ),
    "practice": [
        "project-anatomy-q09",
        "project-anatomy-q15",
        "project-anatomy-q35",
        "project-anatomy-q34",
        "sample-paper-q50",
        "sample-paper-q11",
    ],
    "short_answers": {},
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "S1.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(S1, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {out}")
