"""S6 (sample Q6): what does this command print? Writes ../S6.json.

Facts from sessions 9-10 slides and labs/09, labs/10. Outputs come from the bank (pipes-bash, run on the
sample file and on the real expenses.csv). Practice ids are mcq only, core or exam.
"""

import json
from pathlib import Path

S6 = {
    "tid": "S6",
    "name": "What does this command print?",
    "minutes": 15,
    "shape_md": (
        "Sample Q6: a short `grep ... | wc -l` on `expenses.csv` and four candidate outputs. "
        "Variants change the pipe, the flag, the file or the redirection."
    ),
    "one_md": (
        "Run the pipeline in your head one stage at a time, because each program does one job on the lines "
        "it receives and `wc -l` counts lines."
    ),
    "sample": {
        "qnum": "Q6",
        "kind": "mcq",
        "question_md": (
            "`expenses.csv` has one expense per line, and each line includes its category. "
            "What does this command print?\n\n"
            "```bash\n"
            "grep \"food\" expenses.csv | wc -l\n"
            "```"
        ),
        "options": [
            "The number of lines that contain the word food",
            "The number of times food appears in the whole file",
            "Every line that contains food",
            "The number of words in the file",
        ],
        "answer": 0,
        "his_answer_md": (
            "**a.** grep keeps the lines that contain food. `wc -l` counts lines. Two matches on one line count "
            "once, so (b) is wrong. grep alone would give (c)."
        ),
        "decoded_md": (
            "- **The pattern.** A short pipeline on the course's file and four outputs. They differ in what is "
            "counted (lines, occurrences, words) and in whether a number or the lines come out.\n"
            "- **Why a.** Go stage by stage. grep keeps the lines that contain `food`. The pipe hands them to "
            "`wc -l`, which counts lines and prints one number.\n"
            "- **Why b tempts.** \"Count\" sounds like occurrences. His correction: two matches on one line "
            "count once, because `wc -l` counts lines.\n"
            "- **Why c and d tempt.** c is what grep alone would print; with the pipe, the lines go to `wc` and "
            "only the number reaches the screen. d: `wc` only sees what grep sent, not the whole file.\n"
            "- **Level.** One sentence per stage. No flags beyond `grep` and `wc -l`, and every answer is "
            "tied to the command shown."
        ),
    },
    "spot_md": (
        "- A command or a short pipeline, often on `expenses.csv`, and \"What does this command print?\".\n"
        "- Options differ in the unit (lines, occurrences, words) and in number versus lines.\n"
        "- Variants: `grep -c`, `grep -v`, `cut -d, -f3 | sort | uniq -c`, `>` and `>>`, `&&` and `||`.\n"
        "- The data hides a trap: the header is a line, and the pattern may sit in another column."
    ),
    "basics": [
        {
            "id": "S6-b1",
            "heading": "Read a pipeline one stage at a time",
            "body_md": (
                "`|` sends the stdout of the left command into the stdin of the right one. Nothing is written "
                "to disk. Each tool does one small job on lines of text.\n\n"
                "| Tool | What it does to the lines |\n|---|---|\n"
                "| `grep dining` | keeps the lines that contain `dining` anywhere; `-v` keeps the others, `-c` counts them |\n"
                "| `wc -l` | counts the lines it receives |\n"
                "| `cut -d, -f3` | keeps column 3 of a comma-separated file |\n"
                "| `sort`, `uniq -c` | order the lines; collapse equal neighbours and count them |\n"
                "| `head -n 3`, `tail -n +2` | the first three lines; everything from line 2, which drops the header |\n\n"
                "Slide 7's pipeline on the real file:\n\n"
                "```console\n"
                "$ tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c | sort -rn | head -n 3\n"
                "    119 groceries\n"
                "     86 dining\n"
                "     76 transport\n"
                "```"
            ),
        },
        {
            "id": "S6-b2",
            "heading": "Three traps in the data",
            "body_md": (
                "grep knows nothing about columns, and the header is a line too. On the sample file (a header and "
                "18 expenses):\n\n"
                "```console\n"
                "$ grep home expenses.csv | wc -l\n"
                "3\n"
                "$ grep -v dining expenses.csv | wc -l\n"
                "14\n"
                "```\n\n"
                "The first prints 3, not 2: `Sushi at home` is a dining expense whose merchant contains the word. "
                "The second prints 14, not 13: the header has no `dining`, so `-v` keeps it.\n\n"
                "`>` replaces a file and `>>` appends, so `grep -c dining expenses.csv > counts.txt` prints nothing: "
                "the number went into the file. Messages about problems go to stderr, which skips the pipe: "
                "`uv run expenses report nosuch.csv | wc -l` shows the message on the screen and then prints `0`, "
                "because `wc` received nothing."
            ),
        },
    ],
    "checks": [
        {
            "id": "S6-c1",
            "q_md": "In `grep dining expenses.csv | wc -l`, what does `wc` receive?",
            "options": [
                "The file name `expenses.csv`",
                "Only the lines that contain `dining`",
                "The whole file",
            ],
            "answer": 1,
            "why_md": "The pipe sends grep's stdout to wc's stdin. wc never opens the file, so it never sees a name.",
        },
        {
            "id": "S6-c2",
            "q_md": "A line contains `food` twice. How often does `grep food expenses.csv | wc -l` count that line?",
            "options": [
                "Once",
                "Twice",
                "Not at all",
            ],
            "answer": 0,
            "why_md": "grep sends the line once and `wc -l` counts lines, so two matches on one line count once.",
        },
    ],
    "method": [
        "Cover the pipe. What does the first command print? grep keeps every line that contains the text, anywhere in the line.",
        "Feed those lines to the next stage. Each stage sees only what the one before printed.",
        "Check the unit. `wc -l` counts lines, so you get a number of lines, not occurrences or words, and the lines themselves do not reach the screen.",
        "Ask about the data: is the header in the count? Does the pattern also match another column?",
        "For `>` and `>>`: the output goes into the file and the screen stays empty. `>` replaces, `>>` appends.",
    ],
    "worked": [
        {
            "title": "Same shape, other topic: counting categories",
            "question_md": (
                "On the course's `expenses.csv` (a header and 420 expenses), what does this command print?\n\n"
                "```bash\n"
                "tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq | wc -l\n"
                "```\n\n"
                "- a) 420, the number of expenses\n"
                "- b) The number of different categories\n"
                "- c) The number of expenses in the first category after sorting\n"
                "- d) The different category names, one per line"
            ),
            "steps_md": [
                "`tail -n +2` drops the header. `cut -d, -f3` turns every expense into its category name.",
                "`sort` puts equal names together and `uniq` leaves one line for each name.",
                "`wc -l` counts those lines, so the screen shows one number: the count of different names.",
            ],
            "answer_md": (
                "**b.** `cut` keeps the category of every expense, `sort` and `uniq` leave one line per category, and "
                "`wc -l` counts those lines. On the course file it prints 8. (d) would be the same pipeline without `wc -l`."
            ),
        }
    ],
    "twists": [
        {
            "twist_md": "`grep -c dining expenses.csv` instead of the pipe.",
            "how_md": "The same number. `-c` counts the matching lines inside grep, and `grep dining expenses.csv | wc -l` counts them in wc.",
        },
        {
            "twist_md": "`grep -v dining expenses.csv | wc -l`, \"how many expenses are not dining?\"",
            "how_md": "One too many: the header has no `dining`, so `-v` keeps it. Any count over the whole file must ask whether the header is in it.",
        },
        {
            "twist_md": "The word also sits in another column, such as `grep home` and a merchant called `Sushi at home`.",
            "how_md": "grep matches anywhere in the line, so it counts 3 lines for 2 home expenses. Say what the command counts: lines that contain the word.",
        },
        {
            "twist_md": "`>` twice, or `>>` after `>`, and then `cat` on the file.",
            "how_md": "The screen stays empty while the commands run. `>` replaces what was there, `>>` adds to the end. Read the file line by line.",
        },
        {
            "twist_md": "`uv run expenses report nosuch.csv && echo \"report ok\" || echo \"report failed\"`.",
            "how_md": "`&&` runs only after success, `||` only after failure. The report fails, so you see the message and then `report failed`.",
        },
    ],
    "traps": [
        "\"It counts how many times food appears.\" `wc -l` counts lines. Two matches on one line count once.",
        "\"It prints the matching lines.\" Those go into the pipe. The screen shows only the number from `wc`.",
        "\"grep understands columns.\" It matches anywhere in the line, so `home` also matches `Sushi at home`.",
        "\"The header is not in the count.\" It is a line like any other. `grep -v` and `wc -l` on the whole file keep it.",
    ],
    "say_md": (
        "- `grep` keeps the lines that contain the text, and `wc -l` counts the lines it receives. Two matches on one line count once.\n"
        "- The pipe sends the stdout of the left command to the stdin of the right one. stderr skips the pipe.\n"
        "- `>` replaces the file and `>>` appends. The header is a line too.\n"
        "- `&&` runs the next command only after success, `||` only after failure."
    ),
    "practice": [
        "pipes-bash-q09",
        "pipes-bash-q46",
        "pipes-bash-q21",
        "pipes-bash-q08",
        "pipes-bash-q10",
        "pipes-bash-q50",
        "sample-paper-q26",
    ],
    "short_answers": {},
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "S6.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(S6, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {out}")
