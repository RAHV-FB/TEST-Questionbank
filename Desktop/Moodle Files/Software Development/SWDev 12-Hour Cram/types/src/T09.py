#!/usr/bin/env python3
"""Generator for the cram exercise type T09: pipes, text wrangling and bash scripts.

Writes ../T09.json next to this script's parent folder (CRAM/types/T09.json).
All tool output quoted below is copied from the verified bank (pipes-bash, sample-paper)
or from the session 10 slides and labs.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "T09.json")

B1 = """Every program the shell starts has three streams of text.

| Stream | Number | Carries | By default |
|---|---|---|---|
| stdin | 0 | what the program reads | the keyboard |
| stdout | 1 | the result | the terminal |
| stderr | 2 | messages about problems | the terminal |

stdout and stderr share the screen, so they look like one thing. They are two channels. The expense-tracker writes its report to stdout and its complaint to stderr (`typer.echo(..., err=True)`).

Redirection tells the shell where a stream goes, before the program starts:

| You type | stdout goes to | stderr goes to |
|---|---|---|
| `cmd > f` | `f`, replacing it | the terminal |
| `cmd >> f` | the end of `f` | the terminal |
| `cmd 2> f` | the terminal | `f` |
| `cmd > f 2>&1` | `f` | wherever stdout goes: `f` |
| `cmd 2> /dev/null` | the terminal | discarded |

`<` feeds a file to the program's stdin: on the course file `wc -l expenses.csv` prints `421 expenses.csv`, and `wc -l < expenses.csv` prints `421`, because wc never learns the name.

Slide 5 shows `>`, `>>`, `|` and `2>`. `2>&1` goes one step past the slides: read it as "stderr joins stdout".

`>` empties the file before the command runs, even when the command then fails, so a failing command still costs you the old content:

```console
$ uv run expenses report nosuch.csv > out.txt
could not read nosuch.csv
```

The message is on the screen because it is on stderr, and `>` moves stdout only. `out.txt` is empty, because the shell emptied it before the program started. `/dev/null` hides text and never the exit code."""

B2 = """The pipe `|` sends the stdout of the left command into the stdin of the right one. Nothing is written to disk, and stderr does not travel through it. Each program does one small job, and you build the answer one stage at a time.

The course file `expenses.csv` has the header `date,merchant,category,amount` on line 1. The real one has 421 lines: a header and 420 expenses.

| Tool | What it does to the lines |
|---|---|
| `head -n 3`, `tail -n 3` | keep the first or last lines; `tail -n +2` starts at line 2, so it drops the header |
| `grep dining` | keep the lines that contain `dining` anywhere; `-v` keeps the others, `-c` counts them |
| `cut -d, -f3` | keep column 3 of a comma-separated file |
| `sort` | order the lines as text; `-n` numeric, `-r` reversed, `-t, -k4` by column 4 of a CSV |
| `uniq` | collapse equal neighbouring lines; `-c` counts them, `-d` keeps the repeated ones |
| `wc -l` | count the lines |

Slide 7 answers "which category has the most expenses?" stage by stage:

```console
$ tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c | sort -rn | head -n 3
    119 groceries
     86 dining
     76 transport
```

Drop the header, keep the category, sort so equal names sit together, count each group, put the biggest first, keep three.

Sample Q6 is the smallest pipeline: `grep "food" expenses.csv | wc -l`. grep prints the lines that contain `food`, the pipe sends them to wc, and wc prints one number: how many lines."""

B3 = """Every command leaves a number behind, and `echo $?` shows the last one. 0 means success and anything else means failure. `&&`, `set -e` and CI read that number, never the text on the screen.

grep uses three values:

```console
$ grep clothing expenses.csv
$ echo $?
1
$ grep dining nosuch.csv
grep: nosuch.csv: No such file or directory
$ echo $?
2
```

0 means a line matched, 1 means no line matched, 2 means trouble. To the shell, "no match" is still a failure.

- `a && b`: b runs only if a exited 0.
- `a || b`: b runs only if a exited non-zero.
- `a ; b`: b runs whatever happened.

A pipeline has one exit code, the last command's. `grep clothing expenses.csv | wc -l` prints `0` and exits 0, because wc counted fine.

In a script, three switches turn silent failures into loud ones:

| Switch | Without it | With it |
|---|---|---|
| `set -e` | the script carries on and exits with the last command's code | it stops at the first non-zero exit |
| `set -u` | a misspelt `$NAME` is empty text | `unbound variable`, and it stops |
| `set -o pipefail` | the pipeline's code is its last stage's | it fails if any stage fails |"""

B4 = """A script is a pipeline you wanted twice: a text file of commands, run from top to bottom.

```bash
#!/usr/bin/env bash
set -euo pipefail
file="$1"
tail -n +2 "$file" | cut -d, -f3 | sort | uniq -c | sort -rn | head -n 3
```

| Piece | Meaning |
|---|---|
| `#!/usr/bin/env bash` | the shebang: which program runs this file |
| `chmod +x` | the x bit; `./top.sh` needs it, `bash top.sh` does not |
| `"$1"`, `$#`, `$0` | the first argument, how many arguments, the script's own name |
| `"$file"` | always quote it, or `Moodle Files/expenses.csv` splits at the space |
| `[ ! -f "$1" ]` | true when the argument is not a regular file |
| `>&2`, `exit 2` | message to stderr, exit code to the caller |

The slides use `exit 2` for a call made wrongly and `exit 1` for a job that failed. Both are failures.

`scripts/check.sh` is the rubric's four checks, one per line, each named by an `echo "==> ..."`: `ruff check`, `ruff format --check`, `mypy src tests`, `pytest`. With `set -euo pipefail` the first failing check stops the script and it exits 1. That 1 is the red cross on GitHub.

CI is a terminal: each step of `check.yml` is a command typed on a fresh machine, a failed step skips the ones after it, and exit code 0 is green. Run `check.sh` before `git tag -a v0.5`."""

W1_QUESTION = """`expenses.csv` has one expense per line, and each line includes its category. What does this command print?

```bash
grep "food" expenses.csv | wc -l
```

- a) The number of lines that contain the word food
- b) The number of times food appears in the whole file
- c) Every line that contains food
- d) The number of words in the file"""

W2_QUESTION = """A teammate wants the three largest amounts in `expenses.csv`, which contains 250.83 and 137.97:

```console
$ cut -d, -f4 expenses.csv | sort -r | head -n 3
amount
91.60
9.80
```

1. Say in words what each of the three stages does.
2. Give the two reasons the result is wrong.
3. Describe in words how you would fix each problem."""

module = {
    "tid": "T09",
    "name": "Pipes, text wrangling and bash scripts",
    "shape_md": (
        "Mirrors sample Q6, `grep \"food\" expenses.csv | wc -l` and \"what does this command print?\", and "
        "extends it to the rest of session 10: redirection, exit codes, a short bash script and `scripts/check.sh`. "
        "It appears as a command or script plus a transcript, with a multiple-choice question or a 5–8 line open answer."
    ),
    "minutes": 45,
    "one_md": (
        "Read a pipeline or a script one stage at a time and say what text flows through each `|`, "
        "where each stream ends up and what exit code the line leaves behind."
    ),
    "spot_md": "\n".join([
        "- A command with `|`, `>`, `>>`, `2>` or `&&`, and the question \"What does this print?\" or \"What is in the file now?\"",
        "- `expenses.csv` shown in the question, with a trap built in: a merchant such as `Sushi at home`, a header line, amounts with different numbers of digits.",
        "- A transcript where a message still appears on the screen after a redirect, or a count that is one too high, or `0`.",
        "- A short script (`#!/usr/bin/env bash`, `\"$1\"`, `set -euo pipefail`) with its run and `echo $?`.",
        "- `scripts/check.sh` or `check.yml` with a red run: \"which steps ran?\", \"what do you conclude?\", \"do you accept this change?\"",
    ]),
    "basics": [
        {"id": "T09-b1", "heading": "Streams and redirection", "body_md": B1},
        {"id": "T09-b2", "heading": "The pipe and the text tools", "body_md": B2},
        {"id": "T09-b3", "heading": "Exit codes, chaining and set -e", "body_md": B3},
        {"id": "T09-b4", "heading": "Scripts and check.sh", "body_md": B4},
    ],
    "checks": [
        {
            "id": "T09-c1",
            "q_md": (
                "In an empty folder you run these three commands. What does `cat f.txt` print?\n\n"
                "```bash\necho one > f.txt\necho two > f.txt\necho three >> f.txt\n```"
            ),
            "options": [
                "`one`, `two` and `three`, one per line",
                "`three`",
                "`two` and `three`, one per line",
                "`one` and `three`, one per line",
            ],
            "answer": 2,
            "why_md": "The second `>` replaces the file, so `one` is gone. `>>` then adds `three` at the end.",
        },
        {
            "id": "T09-c2",
            "q_md": (
                "`nosuch.csv` does not exist. You run:\n\n"
                "```console\n$ grep dining nosuch.csv 2> /dev/null\n$ echo $?\n```\n\n"
                "What appears on the screen?"
            ),
            "options": [
                "`grep: nosuch.csv: No such file or directory`, then `2`",
                "Only `2`",
                "Nothing, because `/dev/null` hides the exit code too",
                "Only `0`, because the error was thrown away",
            ],
            "answer": 1,
            "why_md": "The error message is on stderr, so `2> /dev/null` discards it. The exit code is a separate thing: grep exits 2 when the file is missing, and `echo $?` shows it.",
        },
        {
            "id": "T09-c3",
            "q_md": "Three lines reach `uniq`: `food`, `transport`, `food`. What does plain `uniq`, with no flags, print?",
            "options": [
                "`food` and `transport`, one per line",
                "`2 food` and `1 transport`",
                "Nothing, because `uniq` prints only repeated lines",
                "`food`, `transport` and `food`, one per line",
            ],
            "answer": 3,
            "why_md": "uniq collapses only equal neighbouring lines, and no two neighbours are equal here. With `sort` first the two `food` lines sit together and become one.",
        },
        {
            "id": "T09-c4",
            "q_md": "`false` is a command that exits 1. What does this line print?\n\n```bash\nfalse && echo yes || echo no\n```",
            "options": [
                "`yes`",
                "`yes` and then `no`",
                "`no`",
                "Nothing",
            ],
            "answer": 2,
            "why_md": "`false` exits 1, so `&&` skips `echo yes`. The `||` runs `echo no` because the last command that ran failed.",
        },
        {
            "id": "T09-c5",
            "q_md": "`./hello.sh` prints `bash: ./hello.sh: Permission denied`, but `bash hello.sh` works. What is missing?",
            "options": [
                "The x bit: `chmod +x hello.sh`",
                "The shebang line at the top of the file",
                "A `.sh` ending in the file name",
                "Administrator rights: run it with `sudo`",
            ],
            "answer": 0,
            "why_md": "`./hello.sh` asks the system to run the file as a program, which needs the x bit. `bash hello.sh` only asks bash to read the file, which needs the r bit.",
        },
    ],
    "method": [
        "**Write down what the first command prints.** Use the file in the question and go line by line. Mark the header, and any line that matches by accident, such as a merchant called `Sushi at home` or `Superfood Market`.",
        "**At each `|`, write the text that flows through.** Copy the lines that survive each stage. A pipe carries stdout only, so an error message never reaches the next stage.",
        "**Say what the last stage prints.** `wc -l` prints a number of lines, `uniq -c` puts a count in front of each group of neighbours, `head -n 3` keeps three lines. Ask whether the header is still in the data.",
        "**For redirection, name the stream and the operator.** `>` replaces the file and `>>` appends; `2>` moves stderr. Then state what the file holds and what is still on the screen.",
        "**For exit codes, write the code after each command.** 0 is success and anything else is failure. `&&` continues after 0, `||` after non-zero, `;` always. A script without `set -e` goes on and exits with its last command's code. A pipeline's code is its last stage's unless `pipefail` is on.",
        "**Check against a number you know, then write the answer.** The sample file has 18 expenses and 19 lines; the real file has 420 and 421, with six duplicate rows. In an open answer give the stage, the cause and the fix in words.",
    ],
    "worked": [
        {
            "title": "Sample Q6: what does the pipeline print?",
            "question_md": W1_QUESTION,
            "steps_md": [
                "Read it left to right and ask at each `|` what text flows through.",
                "Stage 1: `grep \"food\" expenses.csv` prints every line of the file that contains the letters `food`, wherever they are in the line.",
                "The pipe: those lines do not reach the screen. They become the stdin of `wc -l`.",
                "Stage 2: `wc -l` counts the lines it receives and prints one number.",
                "Test the options against that. (c) is what stage 1 prints on its own. (b) counts occurrences, but wc counts lines. (d) counts words in the whole file, but wc never sees the whole file.",
            ],
            "answer_md": (
                "**a)** The number of lines that contain the word food.\n\n"
                "One precision for harder variants: grep matches the letters anywhere in the line. If three expenses are in the food category and a fourth is at a shop called `Superfood Market`, "
                "the command prints `4`, because the `Superfood Market` line contains `food` too. The command counts lines that contain the text, which is not always the number of food expenses. "
                "A pattern that pins the column, such as `,food,`, counts only the category."
            ),
        },
        {
            "title": "Open answer: the three largest amounts",
            "question_md": W2_QUESTION,
            "steps_md": [
                "Part 1: read the stages in order. `cut -d, -f4` keeps the fourth field, the amount, of every line, so the header word `amount` comes along. `sort -r` reverses the order of the lines. `head -n 3` keeps the first three lines it receives.",
                "Part 2: look for clues in the output. The word `amount` is in it, so the header is still in the data. `91.60` and `9.80` come before `250.83`, so sort compared text, and `9` comes after `2`. (The order of `91.60` and `9.80` can swap on a machine with other language settings. The cause does not change.)",
                "Part 3: tie each fix to its cause. Start at line 2 with `tail -n +2`. Sort numerically with `-n`, largest first with `-r`.",
                "Keep to 5–8 lines: one line for part 1, two for part 2, one or two for part 3.",
            ],
            "answer_md": (
                "1. `cut` takes the amount column of every line, header included. `sort -r` puts the lines in reverse order. `head -n 3` keeps the first three lines.\n"
                "2. sort compares text character by character, so `9.80` and `91.60` come before `250.83`. The header `amount` is still in the data, and letters sort after digits, so it comes first in a reversed sort.\n"
                "3. Drop the header by starting at line 2 (`tail -n +2`), and sort as numbers, largest first (`sort -rn`). Then head prints 250.83, 137.97 and 91.60.\n\n"
                "Fixing only one bug still leaves a wrong list, which is why the question asks for two reasons."
            ),
        },
    ],
    "twists": [
        {
            "twist_md": "The pattern is a word that also sits in the header: `grep amount expenses.csv | wc -l`. Or the question asks for the expenses of one month.",
            "how_md": "grep reads every line, the header included, and knows nothing about columns. On the sample file `grep amount expenses.csv | wc -l` prints `1`, and the one line is the header. Pin the pattern to the column when you mean the column, such as `,dining,`, and pin a date to the start of the line with `^`: `grep '^2025-09' expenses.csv | wc -l` counts the expenses of September 2025 (67 on the real file, slide 8).",
        },
        {
            "twist_md": "`grep -v` instead of `grep`: \"how many expenses are not dining?\"",
            "how_md": "`-v` keeps every line without the text, and the header has no `dining`. With 18 expenses and 5 of them dining, `grep -v dining expenses.csv | wc -l` prints `14`, not 13. Any count over the whole file has to ask whether the header is in there. `tail -n +2` first gives `13`.",
        },
        {
            "twist_md": "Lab 10, exercise 4: which month has the most expenses? `cut -c1-7` keeps the first seven characters of each line.",
            "how_md": "The pipeline is `tail -n +2 expenses.csv | cut -c1-7 | sort | uniq -c | sort -rn | head -n 1`, and on the real file it prints `2025-11` with 85 rows. Skip the `tail -n +2` and the header turns up as a month called `date,me`. Skip the `sort` and `uniq -c` counts short runs of neighbours instead of whole months.",
        },
        {
            "twist_md": "The first stage fails: `uv run expenses report nosuch.csv | wc -l` prints the message and then `0`.",
            "how_md": "The message is on stderr, which skips the pipe, so it reaches the screen and wc receives an empty stdout. A message together with a count of 0 means the first stage failed. `2>&1` joins stderr to stdout before the pipe, and then wc prints `1`.",
        },
        {
            "twist_md": "A second `>` where `>>` was meant, or one file used for input and output: `sort expenses.csv > expenses.csv`.",
            "how_md": "`>` empties the file before the command runs. In the clean-copy recipe of slide 9, `head -n 1 expenses.csv > clean.csv` and then `tail -n +2 expenses.csv | sort -u >> clean.csv`, a second `>` overwrites the header: `clean.csv` has 414 lines and the first is an expense. `sort expenses.csv > expenses.csv` leaves an empty file, because the shell emptied it before sort read it. Write to a new file name and never edit the original `expenses.csv`.",
        },
        {
            "twist_md": "A script with `set -euo pipefail` stops halfway, with exit code 1 and no message.",
            "how_md": "Look for a command that exited non-zero for a normal reason. grep exits 1 when nothing matches, and in `x=$(grep -c word \"$file\")` the assignment takes that code, so `set -e` stops the script before the next line. With `| wc -l` on the end it is `pipefail` that reports grep's 1. `((counter++))` evaluates to the old value 0 and stops the script too (slide 19); use `counter=$((counter + 1))`. `set -e` did its job. Keep it and let that one line fail harmlessly, for example with `|| true`.",
        },
        {
            "twist_md": "A check script with no `set -e` that ends with `echo \"Ready to tag\"`, or with the checks joined by `;`. A test fails and the script exits 0.",
            "how_md": "Every line runs, and the exit code is the last command's. pytest exits 1, then `echo` runs and exits 0, so the script prints a message that is false and reports success. With `;` a lint error followed by passing tests also ends in 0. `set -e` or `&&` stops at the first failure and exits non-zero. To test the fix, break a check on purpose and read the exit code as well as the screen.",
        },
        {
            "twist_md": "CI is red at one step of `check.yml`, and a teammate suggests adding `|| true` to the command. Or CI fails at \"Install dependencies from the lockfile\" after you changed the version.",
            "how_md": "A step that exits non-zero turns red, and the steps after it are skipped. So every step up to and including the red one ran, and the result of the later ones is unknown. Reject `|| true`: it makes the step exit 0 whatever the tool finds. Run `./scripts/check.sh`, fix, push, wait for green, then move the tag. The lockfile failure happens because `check.sh` never runs `uv sync --locked` and the updated `uv.lock` was not committed. Commit it.",
        },
    ],
    "traps": [
        "**\"`grep dining expenses.csv | wc -l` counts how many times the word appears.\"** It counts lines that contain it; `grep -c dining` prints the same number.",
        "**\"grep looks in the category column.\"** It looks anywhere in the line, so `grep home` also finds `Sushi at home`. Match `,home,` when you mean the field.",
        "**\"`uniq` removes all duplicate lines.\"** It only compares a line with the one just before it, so the habit is `sort | uniq`. On the real file `uniq -d` finds 5 of the 6 duplicates.",
        "**\"`sort` puts amounts in order.\"** By default it compares text, so `9.80` comes after `250.83`. Use `sort -rn` and drop the header first.",
        "**\"`> report.txt` captures the error message, and a failed command leaves the old file alone.\"** It captures stdout only, so stderr still reaches the screen, and the shell empties the file before the command starts.",
        "**\"grep exiting 1 means something broke.\"** It means no line matched; 2 means trouble. Under `set -e`, a 1 still stops the script, with no message.",
        "**\"A script stops at the first error by itself, so `;` and `&&` do the same job.\"** Without `set -e` it runs every line and exits with the last command's code, so a failed check followed by an `echo` ends in 0.",
        "**\"An unquoted `$file` is harmless.\"** With a path such as `Moodle Files/expenses.csv`, bash splits it at the space and the command receives two words that are not the file. Write `\"$file\"`.",
    ],
    "say_md": "\n".join([
        "- \"`grep` prints the lines that contain the text, and `wc -l` counts the lines it receives.\"",
        "- \"`|` sends the stdout of the left command to the stdin of the right one. stderr skips the pipe.\"",
        "- \"`>` replaces the file, and the shell empties it before the command runs. `>>` appends.\"",
        "- \"The message went to stderr, and `>` redirects only stdout, so it still reached the screen.\"",
        "- \"`uniq` only compares neighbouring lines, so you sort first.\"",
        "- \"`sort` compares text unless told otherwise, and the header is still in the data.\"",
        "- \"0 means success and anything else is failure. CI reads the exit code.\"",
        "- \"Without `set -e` the script carries on and exits with the last command's code.\"",
        "- \"`set -e` stops at the first non-zero exit, `-u` makes an unset variable an error, `pipefail` makes a pipeline fail if any stage fails.\"",
        "- \"Quote `\"$1\"`, because paths contain spaces.\"",
        "- \"No x bit, no run: `chmod +x`, and commit it.\"",
        "- \"CI is a terminal: each step is a command, a non-zero exit turns it red, and the steps after it are skipped.\"",
        "- \"A program that prints an error and exits 0 is a program that lies.\"",
    ]),
    "practice": [
        "pipes-bash-q42",
        "pipes-bash-q69",
        "pipes-bash-q21",
        "pipes-bash-q50",
        "pipes-bash-q43",
        "pipes-bash-q57",
        "pipes-bash-q33",
        "pipes-bash-q35",
        "pipes-bash-q39",
        "pipes-bash-q73",
        "sample-paper-q25",
        "pipes-bash-q18",
        "pipes-bash-q26",
        "pipes-bash-q38",
    ],
}

# Sanity checks before writing.
CRAM = os.path.dirname(os.path.dirname(HERE))
pools = json.load(open(os.path.join(CRAM, "pools.json"), encoding="utf-8"))["pools"]["T09"]
pool_ids = {q["id"]: q for q in pools}
missing = [i for i in module["practice"] if i not in pool_ids]
assert not missing, missing
assert len(set(module["practice"])) == len(module["practice"])
assert 10 <= len(module["practice"]) <= 14
for c in module["checks"]:
    assert 0 <= c["answer"] < len(c["options"])

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(module, f, ensure_ascii=False, indent=1)
    f.write("\n")

mix = {}
for i in module["practice"]:
    q = pool_ids[i]
    mix.setdefault((q["type"], q["level"]), 0)
    mix[(q["type"], q["level"])] += 1
print("wrote", OUT)
print("basics", len(module["basics"]), "checks", len(module["checks"]), "twists", len(module["twists"]),
      "traps", len(module["traps"]), "practice", len(module["practice"]))
print(mix)
for b in module["basics"]:
    print(b["id"], len(b["body_md"].split()), "words")
