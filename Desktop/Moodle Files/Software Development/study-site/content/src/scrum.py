"""Generate content/scrum.json: Scrum, the backlog and the Definition of Done (session 4, first half).

Run from the study-site folder:
    uv run python content/src/scrum.py
Every tool output shown below was produced by a real run (see the module's report for the evidence files).
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

MID = "scrum"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


def T(s: str) -> str:
    """Dedent and strip a Markdown block."""
    return textwrap.dedent(s).strip("\n").rstrip()


def sid(n: int) -> str:
    return f"{MID}-s{n}"


def qid(n: int) -> str:
    return f"{MID}-q{n:02d}"


def fid(n: int) -> str:
    return f"{MID}-f{n:02d}"


def mcq(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    correct: tuple[str, str],
    wrong: list[tuple[str, str]],
    pos: str,
    explanation: str,
    section: int,
    source: str,
    origin: str = "slides",
    verified: str = "source",
) -> dict[str, Any]:
    assert len(wrong) == 3
    opts: list[dict[str, Any]] = [
        {"text_md": T(t), "correct": False, "why_md": T(w)} for t, w in wrong
    ]
    opts.insert("abcd".index(pos), {"text_md": T(correct[0]), "correct": True, "why_md": T(correct[1])})
    return {
        "id": qid(n),
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": T(stem),
        "options": opts,
        "explanation_md": T(explanation),
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }


def sort(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
    section: int,
    source: str,
    origin: str = "slides",
    verified: str = "source",
) -> dict[str, Any]:
    return {
        "id": qid(n),
        "type": "sort",
        "level": level,
        "skills": skills,
        "stem_md": T(stem),
        "categories": [{"id": c, "label": label} for c, label in categories],
        "items": [{"text_md": T(t), "category": c, "why_md": T(w)} for t, c, w in items],
        "explanation_md": T(explanation),
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }


def part(label: str, prompt: str, marks: int, model: str, rubric: list[str], weak: str) -> dict[str, Any]:
    return {
        "label": label,
        "prompt_md": T(prompt),
        "marks": marks,
        "model_answer_md": T(model),
        "rubric": [T(r) for r in rubric],
        "weak_answers_md": T(weak),
    }


def open_q(
    n: int,
    level: str,
    skills: list[str],
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    section: int,
    source: str,
    lines: str = "6–8",
    origin: str = "slides",
    verified: str = "source",
) -> dict[str, Any]:
    return {
        "id": qid(n),
        "type": "open",
        "level": level,
        "skills": skills,
        "stem_md": T(stem),
        "parts": parts,
        "lines": lines,
        "explanation_md": T(explanation),
        "section_ref": sid(section),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }


# --------------------------------------------------------------------------------------------
# Real artefacts (runs kept in $SCRATCH/work/scrum/; paths rewritten to what a student sees)
# --------------------------------------------------------------------------------------------

# r1: git log on a clone of the expense-tracker (terminal decorations shown, as in a terminal)
GITLOG_V01 = T(
    """
    $ git log --oneline v0.1
    89afbe1 (tag: v0.1) Add a README and the MIT licence
    bc9ef3d Add an add command that writes to data/
    2ecad20 Move the report into the package behind a typer CLI
    a953d05 Turn the script into a uv package
    c746d38 (tag: v0.0) Print the largest expense
    6efdf9d Filter by category and ignore small amounts
    3e0834f Add a script that totals expenses by category
    """
)

# r2: parking-lot project committed without src/parking_lot/pricing.py, then cloned clean into cp1.
# The run's venv sat at a long scratch path, so uv wrote a 3-line /bin/sh trampoline and the import
# landed on line 6. At /tmp/cp1 uv writes a one-line shebang and the import is on line 4
# (evidence: work/scrum-fix/q36_entry_script_lines.txt), so the shown frame says line 4.
CP1_FAIL = T(
    """
    $ uv sync && uv run parking --help
    Using CPython 3.13.15
    Creating virtual environment at: .venv
    Resolved 9 packages in 3ms
    Installed 8 packages in 7ms
    Traceback (most recent call last):
      File "/tmp/cp1/.venv/bin/parking", line 4, in <module>
        from parking_lot.cli import app
      File "/tmp/cp1/src/parking_lot/cli.py", line 3, in <module>
        from parking_lot.pricing import price_for
    ModuleNotFoundError: No module named 'parking_lot.pricing'
    """
)

# r3: library-inventory overdue_fine without the cap; pytest 9.1.1 (trimmed)
PYTEST_FINES = T(
    """
    tests/test_fines.py ...F                                                 [100%]

    E       assert 15.0 == 10.0
    E        +  where 15.0 = overdue_fine(30)

    FAILED tests/test_fines.py::test_fine_is_capped - assert 15.0 == 10.0
    ========================= 1 failed, 3 passed in 0.01s ==========================
    """
)

# r4: gradebook report.py with unformatted line; ruff 0.16.9
RUFF_FORMAT = T(
    """
    $ uv run ruff format --check .
    unformatted: File would be reformatted
     --> src/gradebook/report.py:3:17
      |
    2 |     total_weight = sum(weights)
      -     return sum(m*w for m,w in zip(marks, weights, strict=True)) / total_weight
    3 +     return sum(m * w for m, w in zip(marks, weights, strict=True)) / total_weight
      |

    1 file would be reformatted, 2 files already formatted
    """
)

# r5: expense-tracker at v0.1, fresh clone (trimmed: uv's build lines and package list removed)
CP1_PASS = T(
    """
    $ uv sync && uv run expenses --help
    Using CPython 3.13.15
    Creating virtual environment at: .venv
    Resolved 9 packages in 4ms
    Installed 8 packages in 6ms

     Usage: expenses [OPTIONS] COMMAND [ARGS]...

     A terminal expense tracker.

    ╭─ Options ────────────────────────────────────────────────────────────────────╮
    │ --install-completion          Install completion for the current shell.      │
    │ --show-completion             Show completion for the current shell, to copy │
    │                               it or customize the installation.              │
    │ --help                        Show this message and exit.                    │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────────╮
    │ report                                                                       │
    │ add                                                                          │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    """
)

# f1: gym-logger stand-in (copy of the sandbox project) with "rich>=13" added to pyproject.toml and the
# old uv.lock, as CI sees the pushed commit; uv 0.12.16
SYNC_LOCKED = T(
    """
    Using CPython 3.13.15
    Creating virtual environment at: .venv
    Resolved 20 packages in 5ms
    error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

    hint: To update the lockfile, run `uv lock`.
    """
)

# f1b: the clone is in ~/fare-calculator, the terminal is in the home folder; uv 0.12.16
WRONG_FOLDER = T(
    """
    $ pwd
    /home/ana
    $ uv run fares --help
    error: Failed to spawn: `fares`
      cause: No such file or directory (os error 2)
    """
)

# f2: fare-calculator, [tool.mypy] strict = true; mypy 2.4.0 run as CI's Types step (mypy src tests)
FARES_PY = T(
    """
    PEAK_SURCHARGE = 0.50
    ZONE_FARES = {1: 2.40, 2: 2.90, 3: 3.60}


    def find_fare(zone: int) -> float | None:
        return ZONE_FARES.get(zone)


    def peak_fare(zone: int) -> float:
        return find_fare(zone) + PEAK_SURCHARGE


    def parse_zone(text):
        return int(text)
    """
)
MYPY_FARES = T(
    """
    src/fare_calculator/fares.py:10: error: Unsupported operand types for + ("None" and "float")  [operator]
    src/fare_calculator/fares.py:10: note: Left operand is of type "float | None"
    src/fare_calculator/fares.py:13: error: Function is missing a type annotation  [no-untyped-def]
    Found 2 errors in 1 file (checked 3 source files)
    """
)

# Shown artefact -> raw run output, relative to $SCRATCH/work/
ARTEFACTS = {
    "scrum/r1_gitlog.out": GITLOG_V01,
    "scrum/r2_cp1.out": CP1_FAIL,
    "scrum/r3_pytest.out": PYTEST_FINES,
    "scrum/r4_ruff.out": RUFF_FORMAT,
    "scrum/r5_cp1_pass.out": CP1_PASS,
    "scrum-fix/q50_sync_locked.out": SYNC_LOCKED,
    "scrum-fix/q52/fare-calculator/src/fare_calculator/fares.py": FARES_PY,
    "scrum-fix/q52_mypy.out": MYPY_FARES,
}


def fence(lang: str, body: str) -> str:
    return f"```{lang}\n{body}\n```"


# --------------------------------------------------------------------------------------------
# Sections
# --------------------------------------------------------------------------------------------

S1 = T(
    """
    Session 2 showed why Waterfall fails for software, and session 4 opens by naming the problem Scrum answers: **"A year-long plan, written before anything is built, on estimates nobody can make."** Requirements change once the customer sees a first version, feedback arrives too late, and integration problems pile up until the end. Agile's answer is short cycles, working software and feedback: build a small slice, show it, learn, adjust.

    Scrum is a framework for doing exactly that. In the slide's words it is "the most used way of doing that" and "also, the most commonly misapplied". Session 1 had already matched it to a problem: "No shared plan, four people build four corners" is answered by Agile and Scrum.

    Scrum organises the work into **Sprints**: fixed-length cycles, each ending with something working that people can look at. The slides size every meeting for a two-week Sprint. Inside that cycle Scrum gives you three things, which the rest of this module takes in order:

    | Scrum gives you | What they are |
    |---|---|
    | Accountabilities | Product Owner, Scrum Master, Developers |
    | Artifacts | Product Backlog, Sprint Backlog, Increment, each with a commitment |
    | Ceremonies | Refinement, Sprint Planning, Daily, Sprint Review, Sprint Retrospective |

    Why "most misapplied"? The visible parts (a fifteen-minute standing meeting, a board, someone called Scrum Master) are easy to copy. The parts that make it work are not: a working Increment every Sprint, honest feedback that changes the plan, and a team that decides how to do its own work. A company can rename its weekly status meeting "Daily Scrum", keep its eighteen-month plan, and believe it does Scrum. Slide 14 calls this "mocking the Scrum ceremonies", and section 8 comes back to it: "Scrum organises the work; it does not do it."

    Session 2 also placed Scrum among other Agile methods (Kanban, XP, Lean) and said the course borrows from more than one: Scrum vocabulary for the project, XP's engineering practices (TDD, CI, small commits) as the technical spine, and a Kanban board to track the group's work. "It is not about picking one methodology and following blindly."
    """
)

S2 = T(
    """
    A Scrum team has three accountabilities. The slide's table, titled "The Agile team", gives each one a line:

    | Role | Accountable for |
    |---|---|
    | **Product Owner** (PO) | The value of the product. Owns and orders the Product Backlog. One person, not a committee |
    | **Scrum Master** | Ensures the process works. Removes impediments; coaches. Not a manager |
    | **Developers** | Building the Increment. Cross-functional, self-managing |

    **Product Owner.** The PO decides what is worth building and in what order, because the PO answers for the value the product delivers. It is one person so that there is one order and one place where every request ends up. A committee that votes on the order each week produces compromises and leaves nobody accountable when the order is wrong.

    **Scrum Master.** The Scrum Master looks after the process, not other people's tasks. An **impediment** is anything blocking the Developers: an access right that never arrives, a stakeholder who keeps interrupting, a problem nobody inside the team can fix. The Scrum Master removes it, and coaches the team on how Scrum works. "Not a manager" means the Scrum Master does not hand out work, does not collect status reports and does not decide whether an item is done.

    **Developers.** Everyone who builds the **Increment**, the working product a Sprint adds to. **Cross-functional** means that between them they have every skill needed to finish an item (code, tests, documentation) without waiting for another department. **Self-managing** is the subject of the next section.

    Two more lines on the slide set the shape of the team:

    - The team should ideally consist of **ten people or fewer**. The Daily alone shows why: at about a minute per developer, a team of twenty could not fit it into fifteen minutes.
    - **Hierarchy stays as horizontal as possible.** There is no lead who assigns tickets. The PO decides what, the Developers decide how, the Scrum Master protects the process.

    In the course the mapping is simple: the Product Owner is the lecturer and the Developers are your group (section 9).
    """
)

S3 = T(
    """
    Slide 7 spells out what "self-managing" means in three lines:

    1. **The team decides how the work is done, and who does what.**
    2. **The Product Owner decides what is worth doing, and in what order.**
    3. **Nobody outside decides how much goes into a Sprint.**

    Each line removes a familiar habit. The first removes the manager who assigns tickets to named people and prescribes the technique. If Ana is better at pricing rules and Pol at the command-line interface, the Developers arrange that themselves, and they choose how to build it.

    The second keeps the decision about value in one place. The PO does not tell the team how to build an item, but the PO alone puts the items in order. "Weighted averages is next" is the PO's call. "Joan should do it with a dictionary" is not: that is who and how, which belong to the Developers. Careful reading matters here, because both can be said in one sentence.

    The third protects the Sprint. At Sprint Planning the team agrees what will be delivered by the end of the Sprint. If a director outside the team can push extra work in halfway through, the Sprint Goal stops meaning anything and the team's own plan stops counting. A new request does not vanish: it goes to the Product Owner, who places it in the Product Backlog, where it competes on value with everything else and can be picked at the next Sprint Planning.

    A worked example. Halfway through a two-week Sprint, the head of sales stops by:

    > "Add CSV export and a monthly chart to this Sprint, and have Marc do the chart tonight."

    Three rules are broken. Someone outside the team is deciding how much goes into the Sprint; someone outside is deciding who does what; and the request skipped the PO, who decides what is worth doing and in what order. The Scrum Master's job is to make the process work: send the request to the PO and keep the Sprint intact. Only the PO can cancel a Sprint, and that almost never happens.

    Self-managing is not "no rules". The team still works to a Sprint Goal it agreed, inside time-boxes, to a Definition of Done. It is the freedom to decide how to meet them.
    """
)

S4 = T(
    """
    Scrum has three artifacts. Each exists to make something visible, and each has a **commitment**: the thing it is measured against.

    | Artifact | What it makes visible | Commitment |
    |---|---|---|
    | **Product Backlog** | Everything the product might need, in order | **Product Goal** |
    | **Sprint Backlog** | What this Sprint will deliver, and the plan for it | **Sprint Goal** |
    | **Increment** | The working product built so far | **Definition of Done** |

    The slide's line to remember: **"Without its commitment, it is just a list."**

    - A Product Backlog without a Product Goal (the longer-term objective the product works towards) is a wish list with no reason to say no to anything.
    - A Sprint Backlog without a Sprint Goal is a pile of tickets. The Daily asks "Are we on track for the Sprint Goal?"; with no goal nobody can answer, and every item looks equally urgent.
    - An Increment without a Definition of Done is "it works on my laptop". Nobody can say whether it is finished, so nobody can say whether it ships.

    **The Product Backlog** gets its own slide: **"Ordered. Emergent. Never finished."**

    - **Ordered by the Product Owner, top = next.** Position is a decision, not an accident.
    - **Emergent, never finished.** New items appear as people use the product and learn; old ones change or disappear. A backlog that is "complete" is a requirements document in disguise.
    - **Items are outcomes, not tasks.** The slide's example: "a returning user can log in with an email link". Section 5 shows how to write them.
    - **Refined continuously, in detail only near the top.** The items you will build next get the detail; the rest stay rough.

    Why only near the top? Because the bottom will change before anyone builds it: **"Estimating item 40 precisely is waste: it will change before it is built."** The backlog brief applies this to your group: only the top three items need detail, because "the rest will change, and detailing them now is wasted work". It is session 2's lesson again: a plan written in full detail before anything is built is the Waterfall assumption that software keeps breaking.
    """
)

S5 = T(
    """
    The backlog brief (the session 4 workshop) defines an item: **"an outcome a user gets, not a task you perform. It is small enough to finish in a sitting, and you can tell when it is done."** It gives the shape:

    > `As a <kind of user>, I can <do something>, so that <benefit>.`

    The **"so that"** is, in the brief's words, "the part that stops you building something nobody needs". It names the benefit, so the Product Owner can weigh the item against others, and so the team notices when an item has no benefit at all.

    The brief's three worked examples come from the expense tracker, and each became real code:

    | Item | What it became |
    |---|---|
    | As a user, I can see a total per category, so that I know where the money went | The first thing it ever did |
    | As a user, I can report on one category only, so that I can look at dining without the noise | `--category` |
    | As a user, I can add an expense from the command line, so that I do not edit a CSV by hand | `expenses add` |

    And three that are **not** usable as items:

    - **"Do the CSV part"**: a task, not an outcome. Nobody can tell when it is done.
    - **"Make the code good"**: not checkable. Quality belongs in the Definition of Done.
    - **"Write tests"**: every item is tested, so it is a standard, not a backlog entry. It belongs in the Definition of Done too.

    Slide 30 gives rewrites. Instead of "Do the CSV part", write "A user can add an expense and see it in the next report". Instead of "Make it good", write "Invalid input prints a message and exits non-zero". Both can be checked by running the program.

    Finally, **ordered by value, not by what is easiest to start**. For the parking-lot topic, coloured output is easy and pleasant to build first, but nobody gets anything until a ticket can be issued and a stay priced. A sensible top three:

    1. As an attendant, I can issue a ticket for a plate number, so that I know which car is in which space.
    2. As a driver, I can see the price of my stay when I leave, so that I pay the right amount.
    3. As an attendant, I can see how many spaces are free, so that I can turn cars away before the barrier.

    Those three get detail. The other five or more stay one line each until they move up.
    """
)

S6 = T(
    """
    The **Definition of Done** (DoD) is, in slide 10's words, "the quality bar every Increment meets", "decided once, applied to everything". It is not a checklist written fresh for each item: it is one list, the same for every item, every Sprint.

    The slide names the classic contents: **compiles · tested · reviewed · documented · deployable**. Two rules follow:

    - **"Done except for tests" is not admissible.** There is no partly done. The item meets the bar or it does not.
    - **"An item that misses the Definition of Done is not done, and does not ship."** It is not presented as finished at the Review and it does not go into the Increment.

    The backlog brief says how to write one: **"Write it as things you can check, not things you can hope."** Compare:

    | A hope | Something you can check |
    |---|---|
    | The code is clean | The CI check is green |
    | We test thoroughly | There is at least one test for the new behaviour |
    | It is easy to use | The README says how to use the new behaviour |
    | It handles errors well | Bad input prints a message and exits non-zero |
    | We work as a team | Another member of the group has read the change |

    Every line on the right can be answered yes or no by someone who was not in the room; they come from the brief's starter list, which also has "The code runs from a clean clone: `uv sync && uv run <your-app> --help`". The brief says to edit that list, not copy it.

    Two lines from the course are worth knowing by heart:

    - **"A Definition of Done with six items you ignore is worse than three you keep."** An ignored line is worse than no line: the list then claims a standard the work does not meet, and everyone learns that the DoD is decoration. "Cut what you will not honour."
    - **"A Definition of Done you cannot check yourself is a wish."**

    Why "Write tests" belongs here and not in the backlog: tests are not something a user gets; they are part of what "done" means for every item. "Make the code good" is the same kind of thing. The backlog holds outcomes; the DoD holds the standard each outcome is built to.

    When he set the backlog task (slide 29), the lecturer added: "I hold you to your own Definition of Done in November." The one line that is not yours to choose is the green CI check (section 9).
    """
)

S7 = T(
    """
    Scrum's ceremonies are meetings scheduled within each Sprint. Each is **time-boxed**: it has a maximum length, sized to the Sprint. Slide 11 gives the time-boxes for a two-week Sprint and the question each ceremony answers:

    | Ceremony | Time-box (2-week Sprint) | Question |
    |---|---|---|
    | Refinement | ~4h | The PO and Developers discuss implementation details for increments |
    | Sprint Planning | 1h | Agree on what will be delivered at the end of the Sprint |
    | Daily | 15 min | Are we on track for the Sprint Goal? |
    | Sprint Review | 1h | What was built; what should change |
    | Sprint Retrospective | 1h | How the team worked, and what to improve |

    The time-boxes scale: **shorter Sprint, proportionally shorter events; longer Sprint, proportionally longer events**. A one-week Sprint gets a Review of about thirty minutes. Books and websites on Scrum give other maximums and treat Refinement as an activity rather than a meeting; for this course, and this exam, use the slide's table.

    Separate the two meetings at the end carefully. The **Review** looks at the product: what was built, and what should change in the backlog. The **Retrospective** looks at the team: how it worked, and what it will do differently.

    Slide 12 says what the ceremonies are **not**:

    - **The Daily Scrum is not a status report to a manager.** It is fifteen minutes, for the Developers. The PO can join but is not expected to participate. Each developer takes about a minute to state their latest work, what they intend to work on next, and whether they have any blockers. A long technical discussion does not fit in that minute; a blocker that needs outside help is an impediment for the Scrum Master.
    - **The Review is not a demo for applause.** Stakeholders come to give feedback and change the backlog. A Review where everybody claps and the backlog stays the same has inspected nothing.
    - **The Retrospective is not blame.** It is a team discussion of what worked, what did not, and what changes can be introduced accordingly. "Whose push broke CI?" is the wrong question; "what change stops a broken push reaching `main`?" is the right one.
    - **The PO retains the power to cancel the Sprint**, for instance when its goal no longer makes sense. This almost never happens.

    Refinement is where the top of the backlog gets its detail (section 4). Sprint Planning is where the team, not someone outside, agrees what the Sprint will deliver (section 3).
    """
)

S8 = T(
    """
    Scrum rests on three **pillars**: **transparency · inspection · adaptation**. Make the real state of the work visible, look at it regularly, and change course when what you see calls for it. Each ceremony is an inspection point: the Daily inspects progress towards the Sprint Goal, the Review inspects the Increment, the Retrospective inspects how the team works.

    It names five **values**: **commitment · focus · openness · respect · courage**.

    Slide 13 links them in two lines worth quoting exactly:

    - **"Inspection without transparency inspects a fiction."** If the board says an item is done while its tests fail, the Review inspects the board, not the product. Everyone is pleased, and nothing true was learned.
    - **"Adaptation without courage produces the same Sprint, twelve times."** If the Retrospective names the same problem every Sprint and nobody is willing to change anything (tell a teammate, tell the PO the goal was too big), the team repeats the same Sprint until the project ends.

    **What Scrum does not give you.** Slide 14 is blunt:

    - No requirements document.
    - No promise about what is in version 1.0, a year out.
    - No architecture, no testing strategy, no engineering practices at all.

    **"Scrum organises the work; it does not do it."** The slide warns of two opposite mistakes: imitating Agile by mocking the Scrum ceremonies, and the "equally dangerous tendency" to believe that following the ceremonies is enough to get real work done. A team can hold every Daily on time, run a cheerful Review and a polite Retrospective, and still ship nothing that installs, passes its tests or runs on another machine. Ceremonies performed for their own sake, with nothing working at the end, are sometimes called **cargo-cult** Scrum: the form without the substance.

    This is why the course pairs Scrum with XP's engineering practices (TDD, CI, small commits) and why its Definition of Done is a check a machine runs. Scrum supplies the rhythm, the roles and the ordered backlog; the tests, the type checker and the CI check do the part Scrum leaves out.
    """
)

S9 = T(
    """
    The course runs the group project with Scrum's vocabulary. Slide 16's mapping:

    | Scrum | This course |
    |---|---|
    | Sprint | The stretch between two checkpoints |
    | Sprint Goal | The checkpoint's deliverable |
    | Definition of Done | A green CI check, the same one for all groups |
    | Product Owner | The lecturer |
    | Developers | Your group of four |
    | Sprint Review | Practice sessions, and Demo Day |

    In practice the lecturer, as Product Owner, sets each Sprint Goal (the checkpoint's deliverable); inside that goal, the backlog brief asks your group to write and order its own backlog by value.

    So the stretch ending at CP1 (Friday 25 September) was a Sprint, and its Sprint Goal was CP1's deliverable: the template turned into your project, with one real command, tagged `v0.1`.

    **The green CI check is the line of the DoD that is not yours to choose.** The project brief calls it "the referee, not the judge": the automated `ruff` + `mypy` + `pytest` run on every push "is not marked itself, but a red check means the submission is not mechanically valid". The backlog brief adds that it is the same check for every group and "runs on a machine none of us owns", so "it works on my laptop" does not count. The partial-submission rubric makes it concrete: if CI is red on the `v0.5` commit, the Tests criterion is capped at 1.

    **CP1 as a Definition of Done.** Slide 17 calls it "public, binary and checkable before you submit":

    1. `uv sync && uv run <your-app> --help` works from a clean clone
    2. `src/` layout, package importable
    3. README says what the program does and how to run it (session 5's slide 14: what it does, how to install, how to run)

    and adds: **"A Definition of Done you cannot check yourself is a wish."** The scaffold lab shows how to check item 1 the way the marker does: clone into an empty folder and run the commands there. A clean clone "has no `.venv`, no caches and nothing you forgot to commit", so it catches the file that only exists on your laptop. On the expense tracker at `v0.1`, in a fresh clone, the check passes (uv's build lines and package list trimmed):

    CP1_PASS_BLOCK

    Your own Definition of Done adds lines on top of the green check, such as a test for the new behaviour, a README line, a teammate who has read the change. The lecturer holds each group to its own.
    """
).replace("CP1_PASS_BLOCK", fence("console", CP1_PASS))

sections = [
    {
        "id": sid(1),
        "heading": "The problem Scrum answers",
        "body_md": S1,
        "key_points": [
            "Scrum answers \"a year-long plan, written before anything is built, on estimates nobody can make\".",
            "A Sprint is a fixed-length cycle that ends with something working; the slides size every meeting for two weeks.",
            "The most used Agile framework, and the most commonly misapplied: the ceremonies are easy to copy, working software is not.",
        ],
        "exam_note_md": "Expect a scenario where the vocabulary is present and the substance missing. The judgement is that renamed meetings on top of a fixed long plan are not Scrum.",
        "source_ref": "S4 slides 5, 14; S2 slides 7, 10, 13–15; S1 slides 6, 8",
        "check": [qid(1), qid(2)],
    },
    {
        "id": sid(2),
        "heading": "Three accountabilities",
        "body_md": S2,
        "key_points": [
            "Product Owner: the value of the product; owns and orders the Product Backlog; one person, not a committee.",
            "Scrum Master: ensures the process works, removes impediments, coaches. Not a manager.",
            "Developers: build the Increment; cross-functional and self-managing.",
            "Ten people or fewer; hierarchy as horizontal as possible.",
        ],
        "exam_note_md": "Questions describe a behaviour (assigning tasks, voting on the order, collecting status) and ask whose job it is, or what is wrong with who is doing it.",
        "source_ref": "S4 slide 6",
        "check": [qid(3), qid(4), qid(5)],
    },
    {
        "id": sid(3),
        "heading": "Self-managing: who decides what",
        "body_md": S3,
        "key_points": [
            "How the work is done and who does what: the Developers.",
            "What is worth doing and in what order: the Product Owner.",
            "Nobody outside decides how much goes into a Sprint; outside requests go to the PO and the Product Backlog.",
        ],
        "exam_note_md": "The classic scenario is an outsider adding work mid-Sprint. The harder version mixes a legitimate PO decision with an overstep in one sentence.",
        "source_ref": "S4 slide 7; S4 slide 12 (cancelling a Sprint)",
        "check": [qid(6), qid(7)],
    },
    {
        "id": sid(4),
        "heading": "Three artifacts, three commitments",
        "body_md": S4,
        "key_points": [
            "Product Backlog → Product Goal; Sprint Backlog → Sprint Goal; Increment → Definition of Done.",
            "\"Without its commitment, it is just a list.\"",
            "The Product Backlog is ordered, emergent and never finished; ordered by the PO, top = next.",
            "Detail only near the top: \"estimating item 40 precisely is waste\".",
        ],
        "exam_note_md": "Matching artifact to commitment is a core question; the exam version shows a team without a Sprint Goal or with a fully estimated backlog and asks what is wrong.",
        "source_ref": "S4 slides 8–9; backlog brief (moodle/project-pages.md)",
        "check": [qid(8), qid(9), qid(47)],
    },
    {
        "id": sid(5),
        "heading": "Writing a usable backlog item",
        "body_md": S5,
        "key_points": [
            "`As a <kind of user>, I can <do something>, so that <benefit>.` The \"so that\" stops you building something nobody needs.",
            "An item is an outcome a user gets, small enough to finish in a sitting, and you can tell when it is done.",
            "Tasks (\"Do the CSV part\") are not items; standards (\"Make the code good\", \"Write tests\") go in the Definition of Done.",
            "Ordered by value, not by what is easiest to start.",
        ],
        "exam_note_md": "You will judge candidate items. Name the reason precisely: task rather than outcome, standard that belongs in the DoD, or not checkable.",
        "source_ref": "Backlog brief (moodle/project-pages.md); S4 slides 9, 29–30",
        "check": [qid(13), qid(11), qid(14)],
    },
    {
        "id": sid(6),
        "heading": "The Definition of Done",
        "body_md": S6,
        "key_points": [
            "The quality bar every Increment meets, decided once and applied to everything.",
            "Compiles · tested · reviewed · documented · deployable. \"Done except for tests\" is not done.",
            "An item that misses the DoD is not done and does not ship.",
            "Write lines you can check, not hope. Six ignored lines are worse than three you keep.",
        ],
        "exam_note_md": "Tool output can be the evidence: a red CI step or a failing test means the item is not done, whatever its author says. Candidate DoD lines are judged as checkable or a wish.",
        "source_ref": "S4 slides 10, 17; backlog brief (moodle/project-pages.md)",
        "check": [qid(23), qid(17), qid(18)],
    },
    {
        "id": sid(7),
        "heading": "The ceremonies, and what they are not",
        "body_md": S7,
        "key_points": [
            "Two-week Sprint: Refinement ~4h, Sprint Planning 1h, Daily 15 min, Review 1h, Retrospective 1h; scale with Sprint length.",
            "Daily: for the Developers; latest work, next work, blockers, about a minute each. Not a status report to a manager.",
            "Review looks at the product and changes the backlog; Retrospective looks at how the team worked. Not applause, not blame.",
            "The Product Owner retains the power to cancel a Sprint; it almost never happens.",
        ],
        "exam_note_md": "A meeting is described in a few lines and you say which rule it breaks. Read Review versus Retrospective carefully: one looks at the product, the other at the team.",
        "source_ref": "S4 slides 11–12",
        "check": [qid(24), qid(46), qid(26)],
    },
    {
        "id": sid(8),
        "heading": "Pillars, values, and what Scrum does not give you",
        "body_md": S8,
        "key_points": [
            "Pillars: transparency, inspection, adaptation. Values: commitment, focus, openness, respect, courage.",
            "\"Inspection without transparency inspects a fiction.\"",
            "\"Adaptation without courage produces the same Sprint, twelve times.\"",
            "\"Scrum organises the work; it does not do it\": no requirements document, no v1.0 promise, no engineering practices.",
        ],
        "exam_note_md": "A likely open question: a team runs every ceremony and ships nothing that works. Answer with slide 14, then name what is missing (the DoD, engineering practices).",
        "source_ref": "S4 slides 13–14; S2 slides 13–15",
        "check": [qid(30), qid(31), qid(32)],
    },
    {
        "id": sid(9),
        "heading": "Scrum in this course",
        "body_md": S9,
        "key_points": [
            "Sprint = the stretch between two checkpoints; Sprint Goal = the checkpoint's deliverable.",
            "Definition of Done = a green CI check, the same for all groups: the referee, not the judge.",
            "Product Owner = the lecturer; Developers = your group; Sprint Review = practice sessions and Demo Day.",
            "CP1: three binary items you can check yourself, from a clean clone.",
        ],
        "exam_note_md": "The exam can lean on the project pages: the CI check as referee, CI green at the tag, and why a clean clone is the honest test of \"done\".",
        "source_ref": "S4 slides 16–17; S5 slide 14; labs/01-scaffold.md §10; project brief; partial rubric",
        "check": [qid(34), qid(36), qid(37)],
    },
]

# --------------------------------------------------------------------------------------------
# Terms
# --------------------------------------------------------------------------------------------

terms = [
    ("Scrum", "A framework for Agile work: fixed-length Sprints, three accountabilities, three artifacts with commitments, and time-boxed ceremonies. The most used way of working in short cycles, and the most commonly misapplied.", 1),
    ("Sprint", "A fixed-length cycle that ends with a working Increment; the slides size the ceremonies for a two-week Sprint. In the course, the stretch between two checkpoints.", 1),
    ("Product Owner", "The one person accountable for the value of the product, who owns and orders the Product Backlog: what is worth doing, and in what order. Not a committee. In the course, the lecturer.", 2),
    ("Scrum Master", "Ensures the process works: removes impediments (anything blocking the Developers) and coaches the team. Not a manager: does not assign work or collect status reports.", 2),
    ("Impediment", "Anything blocking the Developers that they cannot remove themselves, such as an access right that never arrives or a stakeholder who keeps interrupting. Removing it is the Scrum Master's job.", 2),
    ("Developers", "The people who build the Increment. Cross-functional (between them, every skill needed to finish an item) and self-managing. In the course, your group.", 2),
    ("Self-managing", "The team decides how the work is done and who does what; the Product Owner decides what and in what order; nobody outside decides how much goes into a Sprint.", 3),
    ("Product Backlog", "The ordered, emergent, never-finished list of outcomes the product might deliver. Ordered by the Product Owner (top = next), detailed only near the top. Its commitment is the Product Goal, the longer-term objective it works towards.", 4),
    ("Product Goal", "The longer-term objective the product works towards: the Product Backlog's commitment. Without it the backlog is a wish list with no reason to say no to anything.", 4),
    ("Sprint Backlog", "The items picked for the current Sprint at Sprint Planning, with the plan for delivering them. Its commitment is the Sprint Goal.", 4),
    ("Sprint Goal", "What the Sprint will deliver, agreed at Sprint Planning; the Daily asks whether the team is on track for it. In the course, the checkpoint's deliverable.", 4),
    ("Increment", "The working product built so far, which the Developers add to every Sprint. Its commitment is the Definition of Done.", 4),
    ("Backlog item", "An outcome a user gets, not a task you perform; small enough to finish in a sitting, and you can tell when it is done. Shape: `As a <kind of user>, I can <do something>, so that <benefit>`.", 5),
    ("Definition of Done", "The quality bar every Increment meets, decided once and applied to everything: compiles, tested, reviewed, documented, deployable. An item that misses it is not done and does not ship. In the course, a green CI check plus each group's own checkable lines.", 6),
    ("Time-box", "The maximum length of a ceremony, sized to the Sprint: for two weeks, Refinement ~4h, Planning 1h, Daily 15 min, Review 1h, Retrospective 1h, scaled proportionally for shorter or longer Sprints.", 7),
    ("Refinement", "Ceremony (~4h per two-week Sprint) where the Product Owner and Developers discuss implementation details of upcoming items; where the top of the backlog gets its detail.", 7),
    ("Sprint Planning", "Ceremony (1h per two-week Sprint) where the team agrees what will be delivered at the end of the Sprint.", 7),
    ("Daily Scrum", "Fifteen minutes, for the Developers: are we on track for the Sprint Goal? Each developer states latest work, next work and blockers in about a minute. Not a status report to a manager.", 7),
    ("Sprint Review", "Ceremony (1h per two-week Sprint): what was built and what should change. Stakeholders give feedback and change the backlog; not a demo for applause. In the course, practice sessions and Demo Day.", 7),
    ("Sprint Retrospective", "Ceremony (1h per two-week Sprint): how the team worked and what to improve. Not blame.", 7),
    ("Cargo-cult Scrum", "Performing the ceremonies for their own sake while nothing working ships: the form without the substance. Answered by \"Scrum organises the work; it does not do it\".", 8),
    ("Referee, not the judge", "The project brief's description of the CI check: it gives no marks, but a red check means the submission is not mechanically valid. The same check for every group, on a machine none of you owns.", 9),
]

# --------------------------------------------------------------------------------------------
# Traps
# --------------------------------------------------------------------------------------------

traps = [
    "**\"The Scrum Master is the team's manager.\"** No: the Scrum Master ensures the process works, removes impediments and coaches. The Developers decide who does what; nobody hands out tasks.",
    "**\"A committee can be the Product Owner.\"** The slide says one person, not a committee: one person owns and orders the Product Backlog, so there is one order and one place for requests to go.",
    "**\"A senior manager can add urgent work to the running Sprint.\"** Nobody outside the team decides how much goes into a Sprint. The request goes to the Product Owner and into the Product Backlog.",
    "**\"A good backlog is fully detailed and estimated up front.\"** Only the top needs detail (the top three, in the brief); estimating item 40 precisely is waste because it will change before it is built.",
    "**\"Write tests\" and \"Make the code good\" are backlog items.** They are standards every item meets, so they belong in the Definition of Done. Backlog items are outcomes a user gets.",
    "**\"Done except for tests\" is nearly done.** It is not admissible: an item that misses the Definition of Done is not done and does not ship.",
    "**A longer Definition of Done is a stricter one.** Six lines you ignore are worse than three you keep, and a line you cannot check yourself is a wish.",
    "**The Daily is where developers report status to the manager or the PO.** It is fifteen minutes for the Developers, about the Sprint Goal: latest work, next work, blockers. The PO can join but is not expected to participate.",
    "**The Sprint Review is a demo to show off the work.** Stakeholders come to give feedback and change the backlog; applause with an unchanged backlog means nothing was inspected.",
    "**Holding all the ceremonies means you are doing Scrum, and working software will follow.** Scrum organises the work; it does not do it. It gives no requirements document, no testing strategy and no engineering practices.",
]

# --------------------------------------------------------------------------------------------
# Flashcards
# --------------------------------------------------------------------------------------------

cards = [
    ("What problem does Scrum answer, according to session 4?", "\"A year-long plan, written before anything is built, on estimates nobody can make.\" Agile replaces it with short cycles, working software and feedback; Scrum is the most used way of doing that.", "concept", 1),
    ("Why does the slide call Scrum \"the most commonly misapplied\"?", "Its visible parts (meetings, a board, a Scrum Master) are easy to copy without the substance: a working Increment every Sprint, feedback that changes the plan, a team that decides how to work.", "concept", 1),
    ("What is the Product Owner accountable for?", "The value of the product. Owns and orders the Product Backlog. One person, not a committee.", "recall", 2),
    ("What is the Scrum Master accountable for?", "Ensures the process works. Removes impediments; coaches. Not a manager.", "recall", 2),
    ("What are the Developers accountable for, and how big should the team be?", "Building the Increment; cross-functional and self-managing. Ideally ten people or fewer, with hierarchy as horizontal as possible.", "recall", 2),
    ("Self-managing: who decides how, who decides what, who decides how much?", "The team decides how the work is done and who does what. The PO decides what is worth doing and in what order. Nobody outside decides how much goes into a Sprint.", "distinction", 3),
    ("Mid-Sprint, the head of sales wants a feature added now. Where does the request go?", "To the Product Owner, who orders it in the Product Backlog; it can be picked at the next Sprint Planning. Only the PO could cancel the Sprint, which almost never happens.", "concept", 3),
    ("Match each artifact to its commitment.", "Product Backlog → Product Goal. Sprint Backlog → Sprint Goal. Increment → Definition of Done.", "recall", 4),
    ("\"Without its commitment, it is just a list.\" Give an example.", "A Sprint Backlog with no Sprint Goal: the Daily cannot answer \"are we on track for the Sprint Goal?\", and every item looks equally urgent.", "concept", 4),
    ("The three words on the Product Backlog slide?", "Ordered. Emergent. Never finished. Ordered by the PO, top = next; refined continuously, in detail only near the top.", "recall", 4),
    (
        "CI on the item's commit ends like this, and its author says \"done apart from one test\". What does it mean for the item?\n\n"
        + fence("text", "E       assert 15.0 == 10.0\nE        +  where 15.0 = overdue_fine(30)\n\nFAILED tests/test_fines.py::test_fine_is_capped - assert 15.0 == 10.0"),
        "The fine is not capped: `overdue_fine(30)` returns 15.0 where the test expects 10.0. CI is red, so the item misses the Definition of Done: it is not done, does not ship, and is not shown as finished at the Review.",
        "reading",
        6,
    ),
    ("The shape of a backlog item in the brief?", "`As a <kind of user>, I can <do something>, so that <benefit>.` An outcome a user gets, small enough to finish in a sitting, and you can tell when it is done.", "recall", 5),
    ("What does the \"so that\" part of an item do?", "It names the benefit: \"the part that stops you building something nobody needs\". It also gives the PO something to order by.", "concept", 5),
    ("Why is \"Do the CSV part\" not a usable item?", "A task, not an outcome: nobody can tell when it is done. Rewrite: \"A user can add an expense and see it in the next report\".", "distinction", 5),
    ("Why are \"Make the code good\" and \"Write tests\" not backlog items?", "They are standards every item meets, so they belong in the Definition of Done. \"Make the code good\" is also not checkable.", "distinction", 5),
    ("How is the Product Backlog ordered?", "By value, not by what is easiest to start. The top is what you build next.", "concept", 5),
    ("What is the Definition of Done, and its classic contents?", "The quality bar every Increment meets, decided once, applied to everything. Compiles · tested · reviewed · documented · deployable.", "recall", 6),
    ("An item meets everything except its tests. Is it done?", "No. \"Done except for tests\" is not admissible. An item that misses the DoD is not done and does not ship.", "concept", 6),
    ("A DoD line you can check versus a wish: one example of each.", "Check: \"The CI check is green\", \"Bad input prints a message and exits non-zero\". Wish: \"The code is clean\". A DoD you cannot check yourself is a wish.", "distinction", 6),
    ("Why is a DoD with six ignored items worse than three you keep?", "Ignored lines claim a standard the work does not meet and teach everyone the DoD is decoration. \"Cut what you will not honour.\"", "concept", 6),
    ("Time-boxes for a two-week Sprint?", "Refinement ~4h · Sprint Planning 1h · Daily 15 min · Sprint Review 1h · Sprint Retrospective 1h. Shorter Sprint, proportionally shorter events; longer, longer.", "recall", 7),
    ("What does each developer say at the Daily, and to whom?", "About a minute each, to the other Developers: latest work, what they intend to work on next, any blockers. Not a status report to a manager.", "concept", 7),
    ("Sprint Review versus Sprint Retrospective?", "Review: the product. What was built and what should change; stakeholders give feedback and change the backlog. Retrospective: the team. How it worked and what to improve; not blame.", "distinction", 7),
    ("Who can cancel a Sprint?", "The Product Owner. It almost never happens.", "recall", 7),
    ("Scrum's three pillars and five values?", "Pillars: transparency, inspection, adaptation. Values: commitment, focus, openness, respect, courage.", "recall", 8),
    ("\"Inspection without transparency inspects a fiction.\" What does it mean in practice?", "If the real state is hidden (items shown as done while CI is red), the Review inspects a story, not the product, and nothing true is learned.", "concept", 8),
    ("\"Adaptation without courage produces the same Sprint, twelve times.\" What does it mean in practice?", "The Retrospective names the same problem every Sprint, but nobody dares change anything, so the team repeats the same Sprint.", "concept", 8),
    ("What does Scrum not give you?", "No requirements document; no promise about v1.0 a year out; no architecture, testing strategy or engineering practices. \"Scrum organises the work; it does not do it.\"", "concept", 8),
    ("The course mapping: Sprint, Sprint Goal, DoD, PO, Developers, Sprint Review?", "The stretch between two checkpoints; the checkpoint's deliverable; a green CI check, the same for all groups; the lecturer; your group; practice sessions and Demo Day.", "recall", 9),
    ("CP1's three binary items, and why check them from a clean clone?", "`uv sync && uv run <your-app> --help` works from a clean clone; `src/` layout, package importable; README says what it does and how to run it. A clean clone has nothing you forgot to commit.", "recall", 9),
]

flashcards = [
    {"id": fid(i), "front_md": f, "back_md": b, "kind": k, "section_ref": sid(s)}
    for i, (f, b, k, s) in enumerate(cards, start=1)
]

# --------------------------------------------------------------------------------------------
# Questions
# --------------------------------------------------------------------------------------------

Q: list[dict[str, Any]] = []

# ---- s1 -------------------------------------------------------------------------------------
Q.append(mcq(
    1, "core", ["concept"],
    """
    Session 1 matched each way working code fails to the method or tool that answers it, and session 4 opened with "the problem Scrum answers". Which problem is Scrum the answer to?
    """,
    ("A long plan made up front, on estimates nobody can make",
     "The slide's own problem: \"a year-long plan, written before anything is built, on estimates nobody can make\". Scrum replaces it with short Sprints that each end in working software and feedback."),
    [
        ("Code that runs on one developer's laptop and on no other machine",
         "That is \"works on my machine\", answered by a standard setup, the lockfile and containers, not by a way of organising work."),
        ("Code that nobody can read six months after it was written",
         "Unreadable code is answered by clean code, testing and TDD (module 2). Scrum says nothing about how code is written."),
        ("A teammate's change that silently breaks the build",
         "That is answered by version control, code review and CI. Scrum gives no engineering practices."),
    ],
    "b",
    """
    Session 4's first Scrum slide states the problem: "A year-long plan, written before anything is built, on estimates nobody can make." Agile moves to short cycles, working software and feedback, and Scrum is the most used way of doing that. Session 1's mapping agrees: "No shared plan → Agile, Scrum". The other three are real problems, but each has its own answer in the course: a standard setup and containers for "works on my machine", clean code and tests for code nobody can read, version control and CI for broken builds. Scrum organises the work; it does not fix the code.
    """,
    1, "S4 slide 5; S1 slides 6, 8",
))

Q.append(mcq(
    2, "exam", ["judgement", "concept"],
    """
    A logistics company announces it "has gone Scrum". The weekly status meeting is renamed the Daily Scrum; it still takes an hour, with each person reporting to the department head, who now has the title Scrum Master. The eighteen-month plan signed off in January is unchanged, and nothing is shown to users until it is complete. Which description fits best?
    """,
    ("Scrum's names on top of a Waterfall plan: no short cycles, no feedback",
     "It copies the ceremonies and keeps the long plan written before anything is built, which is exactly the problem Scrum answers. Renaming the meetings leaves it untouched: no short cycles, no working software, no feedback."),
    [
        ("It is Scrum: it now has a Daily, a Scrum Master and a plan the team follows",
         "Having the names is not doing Scrum. This is the \"most commonly misapplied\" case: roles and meetings without short cycles of working software."),
        ("It is Kanban, because the work is not split into Sprints and nothing is time-boxed",
         "Kanban is a board with a limit on work in progress, pulling items when there is capacity; none of that is here. The label misses the real problem."),
        ("It is a fair use of Scrum for a large company, where a longer Daily is normal",
         "Time-boxes scale with Sprint length, not with company size, and the Daily is never a status report to a manager."),
    ],
    "d",
    """
    Session 4 calls Scrum the most used way of working in short cycles, and the most commonly misapplied. This company shows how: the vocabulary changed, the plan did not. An eighteen-month plan signed off up front, with no user feedback until the end, is Waterfall. The "Daily" breaks two rules from slide 12 (it is a status report to a manager, and it runs four times its fifteen minutes), and the "Scrum Master" is a manager, which slide 6 says the role is not. Slide 14 names the mistake: imitating Agile by mocking the Scrum ceremonies.
    """,
    1, "S4 slides 5, 6, 12, 14; S2 slides 5, 13",
))

# ---- s2 -------------------------------------------------------------------------------------
Q.append(sort(
    3, "core", ["concept"],
    "Sort each statement into the accountability it describes.",
    [("po", "Product Owner"), ("sm", "Scrum Master"), ("dev", "Developers")],
    [
        ("Accountable for the value of the product", "po",
         "Value is the PO's accountability: deciding what is worth building."),
        ("Owns and orders the Product Backlog; top = next", "po",
         "One person owns and orders the backlog, so there is one order."),
        ("Can cancel the Sprint, though this almost never happens", "po",
         "Slide 12: the PO retains the power to cancel the Sprint, though this almost never happens."),
        ("Ensures the process works", "sm",
         "The first words of the Scrum Master's row on slide 6."),
        ("Removes impediments, such as a missing access right or a stakeholder who keeps interrupting", "sm",
         "Removing what blocks the Developers is the Scrum Master's job, without managing them."),
        ("Coaches the team on how Scrum works, without being its manager", "sm",
         "Coaching, not managing: the slide says \"Not a manager\"."),
        ("Builds the Increment", "dev",
         "The Developers are accountable for building the Increment."),
        ("Has, between its members, every skill needed to get an item done", "dev",
         "That is what cross-functional means."),
        ("Decides how the work is done and who does what", "dev",
         "Self-managing: how and who belong to the team (slide 7)."),
    ],
    """
    Slide 6 gives each accountability one line: the PO is accountable for the value of the product and owns and orders the Product Backlog; the Scrum Master ensures the process works, removes impediments and coaches, and is not a manager; the Developers build the Increment and are cross-functional and self-managing. Two items test details from elsewhere in session 4: deciding how and who belongs to the self-managing team (slide 7), and the power to cancel a Sprint belongs to the PO (slide 12).
    """,
    2, "S4 slides 6, 7, 12",
))

Q.append(mcq(
    4, "core", ["concept"],
    "Which statement about the Scrum Master matches session 4?",
    ("Ensures the process works, removes impediments and coaches the team",
     "The slide's own row: \"Ensures the process works. Removes impediments; coaches. Not a manager.\""),
    [
        ("Assigns the Sprint's tasks to Developers and checks they are finished",
         "That is a manager's job, and the slide says the Scrum Master is not a manager. The Developers decide who does what."),
        ("Owns the Product Backlog and decides which item comes next",
         "Owning and ordering the backlog is the Product Owner's accountability."),
        ("Collects a status report from each developer at the Daily",
         "The Daily is fifteen minutes for the Developers, not a status report to anyone."),
    ],
    "c",
    """
    Slide 6's row for the Scrum Master: "Ensures the process works. Removes impediments; coaches. Not a manager." Each wrong option turns the role into something it is not: a manager who assigns tasks (slide 7 gives "who does what" to the team), the Product Owner (who owns and orders the backlog), or a manager receiving status reports (slide 12: the Daily "is not a status report to a manager"). An impediment is anything blocking the Developers, and removing it serves the team rather than directing it.
    """,
    2, "S4 slides 6, 7, 12",
))

Q.append(mcq(
    5, "exam", ["judgement"],
    """
    A bank sets up a Scrum team for a new savings app. Instead of one Product Owner, a steering group of five department heads meets every Monday and votes on the order of the Product Backlog; ties are carried over to the next week. According to session 4, what is the problem?
    """,
    ("The Product Owner must be one person, who owns and orders the backlog",
     "The slide: \"One person, not a committee\", accountable for the value of the product. One person gives one order and someone accountable for it."),
    [
        ("None: a weekly vote among five heads is fairer than one person's opinion",
         "Fairness is not the point. With a committee nobody is accountable for the value of the product, and the order shifts with every vote."),
        ("The Scrum Master should own the order, so it stays neutral between departments",
         "The Scrum Master ensures the process works; ordering the backlog is the Product Owner's accountability."),
        ("The Developers should join the vote, so the order reflects what is easiest to build",
         "Developers decide how, not what, and the backlog is ordered by value, not by what is easiest to start."),
    ],
    "b",
    """
    Slide 6 says the Product Owner is "one person, not a committee". One person owns and orders the backlog, so there is one order, one place where requests go, and someone accountable when the order turns out to be wrong. A weekly vote with carried-over ties means the team often has no clear top item, which is exactly what "top = next" is meant to give it. The wrong options move the decision to roles that do not own it, or reorder by ease instead of value.
    """,
    2, "S4 slides 6, 9, 30",
))

# ---- s3 -------------------------------------------------------------------------------------
Q.append(mcq(
    6, "exam", ["judgement"],
    """
    Day 6 of a two-week Sprint. The marketing director, who is not on the team, emails two developers: "Please add PDF export to this Sprint, it's for a client meeting on Friday." The Sprint Goal does not include export. What does session 4 say should happen?
    """,
    ("It goes to the Product Owner, who decides where it sits in the Product Backlog",
     "Slide 7: nobody outside decides how much goes into a Sprint, and the PO decides what is worth doing and in what order."),
    [
        ("The developers add it to the Sprint, because the request comes from someone senior",
         "Seniority outside the team does not change the rule: nobody outside decides how much goes into a Sprint."),
        ("The Scrum Master decides whether the Sprint has room for it",
         "The Scrum Master makes the process work; here the process says the request goes to the PO."),
        ("The developers work evenings to fit it in without touching the Sprint Goal",
         "Extra hours hide the problem and the request still bypasses the PO. Session 2's principles also ask for a pace sustainable indefinitely."),
    ],
    "a",
    """
    Slide 7: "Nobody outside decides how much goes into a Sprint", and "The Product Owner decides what is worth doing, and in what order." The director's request is legitimate input, but it goes to the PO, who places it in the Product Backlog where it competes on value with everything else and can be picked at the next Sprint Planning. If it really cannot wait, that is the PO's decision to take, up to cancelling the Sprint, which almost never happens.
    """,
    3, "S4 slides 7, 12; S2 slide 12",
))

Q.append(mcq(
    7, "hard", ["judgement"],
    """
    At Refinement, the Product Owner of a school-software team says: "Weighted averages is the next item. Joan should do it, and she should store the weights in a dictionary." Which part of this oversteps the Product Owner's role?
    """,
    ("Naming Joan and prescribing a dictionary: who and how belong to the Developers",
     "Slide 7: the team decides how the work is done and who does what. Saying which item is next stays the PO's call."),
    [
        ("Saying which item is next, since the Developers decide the order",
         "Ordering is exactly the PO's job: \"what is worth doing, and in what order\"."),
        ("Only prescribing the dictionary; naming Joan is fine, since the PO knows who is free",
         "Who does what is also the team's decision (slide 7). Knowing who is free does not make it the PO's call."),
        ("Only naming Joan; prescribing the dictionary is fine, since the PO owns the item",
         "Owning the item means deciding what it must achieve and where it sits in the order, not how it is built."),
    ],
    "d",
    """
    Slide 7 splits the decisions. "The Product Owner decides what is worth doing, and in what order": saying weighted averages comes next is the PO's call. "The team decides how the work is done, and who does what": who takes the item and which data structure to use are the Developers' decisions. The PO can say what the item must achieve (a correct average with weights per assignment); the Developers decide how to deliver it. The two halves of one sentence get different answers, which is why this needs careful reading.
    """,
    3, "S4 slides 7, 11",
))

# ---- s4 -------------------------------------------------------------------------------------
Q.append(mcq(
    8, "core", ["concept"],
    "Each Scrum artifact has a commitment. Which pairing is correct?",
    ("Increment → Definition of Done",
     "The DoD is the quality bar every Increment meets."),
    [
        ("Product Backlog → Sprint Goal",
         "The Product Backlog commits to the Product Goal; the Sprint Goal belongs to the Sprint Backlog."),
        ("Sprint Backlog → Definition of Done",
         "The Sprint Backlog commits to the Sprint Goal; the DoD is the Increment's bar."),
        ("Increment → Product Goal",
         "The Product Goal is what the whole Product Backlog works towards, not the quality bar of one Increment."),
    ],
    "a",
    """
    Slide 8: Product Backlog → Product Goal; Sprint Backlog → Sprint Goal; Increment → Definition of Done. One way to remember it: each commitment answers the question you would ask of that artifact. Of the whole backlog: where is it heading? (Product Goal). Of this Sprint's plan: what is it for? (Sprint Goal). Of the working product: is it good enough to ship? (Definition of Done). "Without its commitment, it is just a list."
    """,
    4, "S4 slide 8",
))

Q.append(mcq(
    9, "hard", ["judgement", "concept"],
    """
    The habit-tracker group starts a Sprint with nine items taken from the Product Backlog and no Sprint Goal. At the Daily on day 5, three items are half finished and two have not been started. Someone asks whether the Sprint is going well, and nobody can say. In session 4's terms, what is missing?
    """,
    ("The Sprint Backlog's commitment: without a Sprint Goal it is just a list",
     "The Daily's question is \"Are we on track for the Sprint Goal?\"; with no goal there is nothing to be on track for."),
    [
        ("More items in the Sprint Backlog, so nobody runs out of work",
         "A longer list does not tell anyone whether the Sprint is on track; it makes the problem worse."),
        ("A longer Daily, so every item can be discussed in detail",
         "The Daily is time-boxed to fifteen minutes; more talk does not supply the missing goal."),
        ("A Definition of Done, since half-finished items show the bar is missing",
         "The DoD says when one item is done; it cannot say whether the Sprint as a whole is succeeding."),
    ],
    "c",
    """
    Slide 8 pairs the Sprint Backlog with the Sprint Goal and warns that "without its commitment, it is just a list." The Daily's question is "Are we on track for the Sprint Goal?" With no goal, nine items are just nine items: nobody can tell which matter most, which could be dropped, or whether the Sprint is succeeding. A Sprint Goal such as "a user can record a habit and see this week's record" would let the team answer at once and focus the half-finished work on it.
    """,
    4, "S4 slides 8, 11",
))

Q.append(mcq(
    10, "exam", ["judgement"],
    """
    A start-up's product manager asks the team to spend Refinement writing detailed specifications and hour estimates for all 35 items in the Product Backlog, so that she can tell customers when the last of them will ship. What does session 4 say?
    """,
    ("Detail only the items near the top: the lower ones will change before they are built",
     "Slide 9: estimating far-down items precisely is waste, because they will change before they are built. Slide 14 adds that Scrum makes no promise about version 1.0 a year out."),
    [
        ("A good use of Refinement: precise estimates for every item make the delivery dates reliable",
         "That is Waterfall's assumption: a plan written in detail before anything is built, on estimates nobody can make."),
        ("Fine, provided it fits within Refinement's four-hour time-box",
         "The time-box limits the meeting; it does not make detailing the bottom of the backlog useful. The work is waste at any length."),
        ("The Scrum Master should write the estimates, so the Developers can keep building",
         "Moving the waste to another person does not remove it: the bottom items will still change before they are built."),
    ],
    "d",
    """
    Slide 9: the Product Backlog is "refined continuously, in detail only near the top", and "estimating item 40 precisely is waste: it will change before it is built." Slide 14 adds that Scrum gives "no promise about what is in version 1.0, a year out". The backlog is emergent: by the time the last items reach the top, the team and its users will have learned things that change them. The backlog brief applies the same rule to your group: only the top three items need detail.
    """,
    4, "S4 slides 9, 14; backlog brief",
))

# ---- s5 -------------------------------------------------------------------------------------
Q.append(mcq(
    11, "core", ["concept"],
    """
    The backlog brief asks for items in the shape `As a <kind of user>, I can <do something>, so that <benefit>`. What job does the "so that" part do?
    """,
    ("It states the benefit, which stops you building something nobody needs",
     "The brief's own words: the \"so that\" is \"the part that stops you building something nobody needs\"."),
    [
        ("It tells the Developers how to implement the item",
         "How is the Developers' decision; an item describes an outcome, not an implementation."),
        ("It names the test that will prove the item is done",
         "Tests are part of the Definition of Done for every item; the \"so that\" says why a user wants it."),
        ("It is optional wording that makes the item sound more professional",
         "The brief singles it out as the part that stops you building something nobody needs; without a benefit nobody can judge the item's value or its place in the order."),
    ],
    "b",
    """
    The brief: "The 'so that' is the part that stops you building something nobody needs." Writing the benefit forces the question "who gains what?" If you cannot finish the sentence, the item probably has no value. It also helps the Product Owner order the backlog by value, because the benefit is written next to each item. Example from the expense tracker: "As a user, I can add an expense from the command line, so that I do not edit a CSV by hand."
    """,
    5, "Backlog brief (moodle/project-pages.md)",
))

Q.append(mcq(
    12, "exam", ["judgement"],
    """
    A group's backlog starts with "Do the CSV part". According to the backlog brief, why is this not usable as an item?
    """,
    ("It is a task, not an outcome, so nobody can tell when it is done",
     "The brief's exact reason for this example."),
    [
        ("It is too small to deserve its own entry in the backlog",
         "Size is not the problem: items should be small enough to finish in a sitting. This one is vague, not small."),
        ("It names a file format, which belongs in the design, not in the backlog",
         "Nothing in the brief keeps formats out of items; its own example \"so that I do not edit a CSV by hand\" names one. The problem is that it is a task."),
        ("Reading and writing files belongs in the Definition of Done",
         "The DoD holds standards every item meets (a green check, a test, a README line), not a piece of functionality."),
    ],
    "c",
    """
    The brief lists "Do the CSV part" as its first non-item: "A task, not an outcome. Nobody can tell when it is done." An item says what a user can do afterwards. Which part of the CSV: reading, writing, validating? Slide 30's rewrite answers that: "A user can add an expense and see it in the next report." That version can be checked by running the program: add an expense, run the report, see it there.
    """,
    5, "Backlog brief; S4 slide 30",
))

Q.append(sort(
    13, "exam", ["judgement"],
    """
    The parking-lot group (topic: spaces, tickets, duration-based pricing) drafts its Product Backlog. Sort each line into what it is.
    """,
    [("item", "Usable backlog item"), ("task", "A task, not an outcome"), ("dod", "A standard: belongs in the Definition of Done")],
    [
        ("As an attendant, I can issue a ticket for a plate number, so that I know which car is in which space", "item",
         "An outcome a user gets, with a benefit, and you can check it by issuing a ticket."),
        ("As a driver, I can see the price of my stay when I leave, so that I pay the right amount", "item",
         "A user, an action, a benefit, and a result you can check by running the program."),
        ("As a manager, I can see today's takings, so that I can close the till without counting tickets by hand", "item",
         "An outcome for a real user of a parking lot, with its benefit stated."),
        ("Do the database part", "task",
         "Work the team does, not something a user can do afterwards; nobody can tell when it is done."),
        ("Set up the pricing module", "task",
         "Describes code to write, not the outcome. The outcome is a driver seeing the right price."),
        ("Refactor `cli.py`", "task",
         "A refactoring changes structure without changing behaviour, so no user gets anything new from it."),
        ("Write tests", "dod",
         "The brief's own example: every item is tested, so it is a standard, not a backlog entry."),
        ("Make the code good", "dod",
         "Not checkable as an item; quality is the bar every item meets, to be written in the DoD as something checkable."),
        ("The README is updated for every new command", "dod",
         "A rule for every item; the brief's starter DoD has \"The README says how to use the new behaviour\"."),
    ],
    """
    The brief's test for an item: an outcome a user gets, small enough to finish in a sitting, and you can tell when it is done, in the shape `As a <kind of user>, I can <do something>, so that <benefit>`. Tasks describe work the team does ("Do the database part", "Set up the pricing module", "Refactor `cli.py`"); they may be steps inside an item, but they are not items. Standards that apply to every item ("Write tests", "Make the code good", README updated) belong in the Definition of Done.
    """,
    5, "Backlog brief (moodle/project-pages.md); S4 slide 30",
))

Q.append(mcq(
    14, "exam", ["judgement"],
    """
    The gradebook group's backlog, top first:

    1. As a teacher, I can see the output in colour, so that it looks nicer
    2. As a teacher, I can export grades to PDF, so that I can print them
    3. As a teacher, I can compute a student's weighted average, so that I can give a final grade
    4. As a teacher, I can set grade boundaries, so that averages turn into letter grades

    They put colour first "because it is the quickest to get working". What is wrong with the order?
    """,
    ("The weighted average should go first: value decides the order, not ease",
     "Slide 30: ordered by value, not by what is easiest to start. The weighted average is the core value; the other items depend on it."),
    [
        ("Nothing: quick wins first build momentum for the harder items",
         "The slide rules this out explicitly. Momentum on colour gives the teacher nothing they need."),
        ("PDF export belongs at the top, because printing is what teachers do with grades",
         "Export of what? There are no averages to print until item 3 exists; its value depends on the core."),
        ("Grade boundaries belong at the top, because they are needed before any average",
         "Boundaries turn an average into a letter; without averages they have nothing to work on."),
    ],
    "d",
    """
    Session 4, slide 30: "Ordered by value, not by what is easiest to start." The top of the backlog is what you build next, so it should be the item that gives a user the most value soonest. For a gradebook, that is computing the weighted average: without it, colour, PDF export and grade boundaries have nothing to show, print or convert. Colour is not wrong to want; it is wrong to build first.
    """,
    5, "S4 slides 9, 30; backlog brief",
))

Q.append(mcq(
    15, "exam", ["judgement", "concept"],
    """
    Slide 30 replaces the item "Make it good" with "Invalid input prints a message and exits non-zero". The brief's starter Definition of Done has a similar line: "Bad input prints a message and exits non-zero". What do these versions have that "Make it good" lacks?
    """,
    ("They can be checked: run it with bad input, then read the message and exit code",
     "Both describe one observable behaviour with a yes-or-no answer."),
    [
        ("They name the person in the group who is responsible for the quality of the code",
         "Neither names anyone; the self-managing team decides who does what."),
        ("They describe how the error handling should be implemented with typer in the code",
         "They say nothing about how. They describe what a user sees, which leaves the implementation to the Developers."),
        ("They promise the program never crashes, which is what \"good\" means",
         "They promise one specific behaviour, not the absence of all problems; \"never crashes\" would be a wish again."),
    ],
    "b",
    """
    "Make it good" is not checkable: nobody can run anything and answer yes or no. "Invalid input prints a message and exits non-zero" is: run `uv run <your-app>` with bad input, read the message, then `echo $?` shows a number other than 0. Session 5 explains why that number matters: "A program that prints an error and exits 0 is a program that lies." The brief's rule for the Definition of Done ("things you can check, not things you can hope") is the same rule that makes an item usable.
    """,
    5, "S4 slide 30; backlog brief; S5 slide 9",
))

Q.append(mcq(
    16, "exam", ["read-tool-output", "judgement"],
    f"""
    The backlog brief's third worked example is "As a user, I can add an expense from the command line, so that I do not edit a CSV by hand." On a clone of the expense tracker you run:

    {fence("console", GITLOG_V01).replace(chr(10), chr(10) + "    ")}

    Which commit delivered that item?
    """,
    ("`bc9ef3d`, because after it a user can run `expenses add` instead of editing the file",
     "The brief says this item \"Became `expenses add`\", and this commit adds the `add` command."),
    [
        ("`a953d05`, because packaging the script made a command-line program possible",
         "That commit changed no code; it made the script installable. No user could add anything after it."),
        ("`2ecad20`, because it put a typer command-line interface in front of the program",
         "That commit moved the existing report behind typer. A user could report, but still had to edit the CSV by hand to add an expense."),
        ("`3e0834f`, because the first commit created the CSV that the item depends on",
         "That commit is the brief's first worked example, a total per category. It reads the CSV; it does not add to it."),
    ],
    "c",
    """
    The brief says the third item "Became `expenses add`". In the history that is `bc9ef3d Add an add command that writes to data/`, which adds an `add` command to `cli.py`. The item is the outcome a user gets; the commit is how it was delivered. The earlier commits were work that made it possible (packaging in `a953d05`, a typer CLI in `2ecad20`), but after them a user still edited the CSV by hand. That is also why "package the script" would not be a backlog item: nobody gets anything from it alone.
    """,
    5, "Backlog brief; S4 slide 25; expense-tracker bc9ef3d",
    origin="history", verified="run",
))

# ---- s6 -------------------------------------------------------------------------------------
Q.append(mcq(
    17, "core", ["concept"],
    "Slide 10 lists five words: compiles · tested · reviewed · documented · deployable. What are they the contents of?",
    ("The Definition of Done: one quality bar, applied to every Increment",
     "Slide 10: the quality bar every Increment meets, decided once and applied to everything. These five words are its classic contents."),
    [
        ("A checklist the Product Owner writes for each item, saying when that item is finished",
         "That is per item. The DoD is one list, decided once, applied to every item, and the brief asks the group to write it."),
        ("The five stages every item passes through, in order, on the team's board",
         "They are not steps in sequence but conditions an item meets together; a board tracks the work, it is not the quality bar."),
        ("The Sprint Goal the team agrees at Sprint Planning",
         "The Sprint Goal is what this Sprint delivers, the Sprint Backlog's commitment; it changes every Sprint."),
    ],
    "c",
    """
    Slide 10 defines the Definition of Done as "the quality bar every Increment meets", "decided once, applied to everything", with the classic contents "compiles · tested · reviewed · documented · deployable". The point is that it does not change per item or per Sprint: the same bar for every item is what makes "done" mean the same thing every time. The backlog brief says the same: "One list, applied to everything." An item that misses any part of it is not done.
    """,
    6, "S4 slide 10; backlog brief",
))

Q.append(mcq(
    18, "exam", ["read-tool-output", "judgement"],
    f"""
    The library-inventory group's Sprint Review is tomorrow, and their Definition of Done includes "The CI check is green". Dani pushes the overdue-fines item and says: "It's done apart from one test. I'll fix the cap next Sprint; we can show it tomorrow." The CI log's Tests step shows (trimmed):

    {fence("text", PYTEST_FINES).replace(chr(10), chr(10) + "    ")}

    What follows from the Definition of Done?
    """,
    ("The item is not done and does not ship; it is not presented as finished tomorrow",
     "An item that misses the DoD is not done, and \"done except for tests\" is not admissible."),
    [
        ("The item is done: three of four tests pass, and the failing one is an edge case",
         "There is no \"mostly done\". The cap is a rule the item must get right, and a red check means the DoD is not met."),
        ("Mark the failing test as skipped so the check goes green, then present it as done",
         "The check would be green and the item still wrong, so the Review would inspect a fiction. Silencing the test defeats the bar."),
        ("Re-run the CI job until it passes, since a single failure may be a fluke",
         "The failure is not random: `overdue_fine(30)` returns 15.0, not the capped 10.0. Re-running gives the same red."),
    ],
    "d",
    """
    Slide 10: "An item that misses the Definition of Done is not done, and does not ship", and "done except for tests" is not admissible. The group's DoD says the CI check is green; it is red. The output says what is wrong: for 30 days late the function returns 15.0 where the test expects the cap, 10.0, so fines are not capped. At the Review the group should say plainly that the item is not done. Whether the test or the function is wrong is a separate question (check what the rule is meant to be), but either way the item is not done today.
    """,
    6, "S4 slide 10; backlog brief",
    verified="run",
))

Q.append(mcq(
    19, "exam", ["judgement", "compare"],
    """
    Two groups hand in their Definition of Done. Group A has nine lines, including "every change is reviewed by two people" and "every function has a docstring"; by their own account they check three of them. Group B has three lines (green CI, a test for the new behaviour, README updated) and checks all three on every item. Which does the backlog brief prefer, and why?
    """,
    ("Group B: three lines kept are worth more than nine lines mostly ignored",
     "The brief: six items you ignore are worse than three you keep. A DoD is worth what you actually check, and ignored lines teach everyone the list is decoration."),
    [
        ("Group A, because a longer list sets a higher standard for every item",
         "A standard nobody meets is not a standard; it only claims one."),
        ("Group A, as long as the ignored lines are all checked before Demo Day",
         "The DoD applies to every item, every time; checking it once at the end is \"done except for\" by another name."),
        ("Neither: the Product Owner should write the Definition of Done, not the group",
         "The brief asks the group to write it (\"written by you\"), and the lecturer holds each group to its own."),
    ],
    "a",
    """
    The brief: "Cut what you will not honour. A Definition of Done with six items you ignore is worse than three you keep." An ignored line is worse than a missing one because the list then claims a standard the work does not meet: anyone reading it is misled, and the team learns that the DoD does not mean what it says. Group B's three lines are checkable and kept, so "done" means something. Group A should cut to what it will honour, or start checking the rest.
    """,
    6, "Backlog brief; S4 slide 29",
))

Q.append(mcq(
    20, "hard", ["judgement"],
    """
    The movie-watchlist group's Definition of Done includes "Another member of the group has read the change". On the morning of a checkpoint, one item is finished and CI is green, but nobody has read it yet. Maria says: "Just this once, we count it as done; the DoD is for normal weeks." What does session 4 imply?
    """,
    ("Not done until someone reads it: the DoD is applied to every item, every time",
     "The DoD is decided once and applied to everything. No exceptions per item or per deadline; that is what \"applied to everything\" means."),
    [
        ("It is done, because a green CI check is the course's Definition of Done",
         "The green check is the line every group must have, not the whole of this group's DoD. Their own list has a review line, and they are held to it."),
        ("It is done, provided the Product Owner agrees to make an exception this one time",
         "The DoD is not waived item by item, by anyone; the PO decides what and in what order, not the quality bar."),
        ("It is done, and the reading can happen at the Retrospective instead",
         "The Retrospective is about how the team worked, not where code gets read; \"done except for review\" is the same as \"done except for tests\"."),
    ],
    "c",
    """
    Slide 10: the DoD is "decided once, applied to everything", and an item that misses it "is not done, and does not ship". A deadline is exactly when the DoD matters: if it bends under pressure, it was never a bar. The green CI check is the line every group shares, but each group adds its own, and the lecturer said "I hold you to your own Definition of Done". If the group finds a line it cannot honour, the place to cut it is a Retrospective, openly, not a quiet exception on a deadline morning.
    """,
    6, "S4 slides 10, 29; backlog brief",
))

Q.append(mcq(
    21, "beyond", ["judgement"],
    """
    A group's Definition of Done has the line "The code is clean". Which rewrite best turns it into a line anyone in the group can answer yes or no, for every item, with the course's tools?
    """,
    ("`uv run ruff check .` and `uv run ruff format --check .` both pass, as in CI",
     "Two commands with a yes-or-no result, both about cleanliness (lint and formatting), and both run on every push as part of the CI check."),
    [
        ("`uv run pytest` passes on the author's laptop before every push",
         "A useful line, but it checks behaviour, not the cleanliness this line was about, and only on one laptop."),
        ("`uv run ruff check .` passes on the whole project once, the day before each Review",
         "Once per Sprint is not \"applied to everything\": an item pushed mid-Sprint is never checked, and the formatting half of \"clean\" is left out."),
        ("The Scrum Master reads each change and signs off that the code is clean",
         "The Scrum Master is not an approver, and \"clean\" in one person's opinion is still not a yes-or-no check."),
    ],
    "a",
    """
    The brief: "Write it as things you can check, not things you can hope", and session 4: "A Definition of Done you cannot check yourself is a wish." Session 6 gave you the tools that turn "clean" into a check: `ruff check` reports lint problems and `ruff format --check` reports unformatted files, and both already run in the course's CI check on every push. The other rewrites each lose something: the tests check behaviour, not cleanliness; a check once per Sprint is not applied to every item; a sign-off is still one person's opinion. A tool cannot judge every name, so a line such as "another member has read the change" can sit beside it.
    """,
    6, "Backlog brief; S4 slide 17; S3 CI referee; S6 ruff check/format",
))

Q.append(mcq(
    22, "hard", ["read-tool-output", "judgement"],
    f"""
    Joan finished the gradebook's weighted-average item. Before pushing she ran `uv run ruff check .` and `uv run pytest`, and both passed. The CI check is red at the Formatting step. You run that step's command locally:

    {fence("console", RUFF_FORMAT).replace(chr(10), chr(10) + "    ")}

    The group's Definition of Done starts with "The CI check is green". Joan says the item is done because "it passes on my machine". What is the right call?
    """,
    ("Not done: run `ruff format`, commit and push, and wait for a green check",
     "The referee says red, and the output names the file and line to fix. The item counts as done once the check is green."),
    [
        ("Done: `ruff check` passed on Joan's machine, so the red check is GitHub's problem",
         "Joan ran a different command. CI also runs `ruff format --check`, and it fails on her machine too, as shown."),
        ("Done: spacing around `*` is cosmetic, so it is not part of the quality bar",
         "The group chose a green check as its bar; whether one step feels cosmetic does not matter. Red means not done."),
        ("Re-run the CI job until it goes green, then count it as done",
         "The file really is unformatted, so every run gives the same red. Only changing the file fixes it."),
    ],
    "a",
    """
    The course's Definition of Done is a green CI check, "the referee": the same steps for every group, on a machine none of you owns. Here it is red, so the item is not done, whatever passed on Joan's laptop. The output says exactly why: `ruff format --check` would reformat line 3 of `src/gradebook/report.py` (spaces around `*` and after the comma). Joan ran the linter, `ruff check`, but not the formatter's check. The scaffold lab's troubleshooting table gives the same fix for a red Formatting step: run `ruff format`, then commit the result.
    """,
    6, "S4 slides 10, 16; S3 slide 3; labs/01-scaffold.md troubleshooting",
    verified="run",
))

Q.append(sort(
    23, "core", ["judgement"],
    "The meal-planner group drafts its Definition of Done. Sort each line.",
    [("check", "Checkable DoD line"), ("wish", "A wish: rewrite or cut"), ("item", "Not a DoD line: a backlog item")],
    [
        ("The CI check is green", "check",
         "Yes or no on the Actions tab; the line every group must have."),
        ("`uv sync && uv run meal-planner --help` works from a clean clone", "check",
         "Anyone can run it in an empty folder and see the result."),
        ("There is at least one test for the new behaviour", "check",
         "You can point at the test, or not."),
        ("Another member of the group has read the change", "check",
         "A fact about each change that the group can verify."),
        ("Bad input prints a message and exits non-zero", "check",
         "Run it with bad input and look at the message and the exit code."),
        ("The code is clean and easy to read", "wish",
         "Nobody can answer yes or no; it needs rewriting as something checkable (for example, ruff passes)."),
        ("We try our best to test edge cases", "wish",
         "\"Try our best\" can never be false, so it checks nothing."),
        ("The program is user-friendly", "wish",
         "Friendly to whom, measured how? A hope, not a check."),
        ("As a cook, I can scale a recipe to six servings, so that I buy the right amounts", "item",
         "An outcome a user gets: it belongs in the Product Backlog and must meet the DoD."),
        ("As a cook, I can get a shopping list for the week, so that I shop once", "item",
         "Another outcome for a user, so a backlog item, not part of the quality bar."),
    ],
    """
    A DoD line must apply to every item and be answerable yes or no by someone who was not in the room. The five checkable lines here come from the brief's starter list. "Clean", "try our best" and "user-friendly" are hopes: nobody can check them, and "a Definition of Done you cannot check yourself is a wish". The two "As a cook" lines are outcomes a user gets: they belong in the Product Backlog, and the DoD is the bar each of them must meet.
    """,
    6, "Backlog brief; S4 slides 10, 17",
))

# ---- s7 -------------------------------------------------------------------------------------
Q.append(sort(
    24, "core", ["concept"],
    "Sort each statement into the ceremony it belongs to.",
    [("ref", "Refinement"), ("plan", "Sprint Planning"), ("daily", "Daily"),
     ("review", "Sprint Review"), ("retro", "Sprint Retrospective")],
    [
        ("The PO and the Developers discuss implementation details of the items near the top", "ref",
         "Refinement's question on slide 11; it is where the top of the backlog gets its detail."),
        ("The team agrees what will be delivered at the end of the Sprint", "plan",
         "Sprint Planning's question on slide 11."),
        ("The team picks the items for the Sprint and agrees its Sprint Goal", "plan",
         "What the Sprint will deliver is settled at Planning, by the team."),
        ("Are we on track for the Sprint Goal?", "daily",
         "The Daily's question, asked every day."),
        ("Each developer: latest work, what next, any blockers", "daily",
         "Slide 12's shape for the Daily, about a minute each."),
        ("Stakeholders see what was built and give feedback that changes the backlog", "review",
         "The Review is about the product: what was built, what should change."),
        ("At the end of the Sprint, stakeholders who tried the report say it confuses them, and the PO moves a fix up the backlog", "review",
         "Feedback changing the backlog is the point of the Review."),
        ("How did the team work, and what should it improve?", "retro",
         "The Retrospective's question on slide 11."),
        ("The team agrees to run the four checks locally before every push from now on", "retro",
         "A change to how the team works is a Retrospective outcome."),
    ],
    """
    Slide 11 gives each ceremony its question: Refinement, the PO and Developers discuss implementation details; Sprint Planning, agree what will be delivered; Daily, are we on track for the Sprint Goal; Review, what was built and what should change; Retrospective, how the team worked and what to improve. The two end-of-Sprint ceremonies need the most care: anything about the product and the backlog is the Review; anything about the team's way of working is the Retrospective.
    """,
    7, "S4 slides 11–12",
))

Q.append(mcq(
    25, "exam", ["concept"],
    """
    Session 4 gives time-boxes for a two-week Sprint. A team moves to one-week Sprints. Roughly how long should its Sprint Review be?
    """,
    ("About 30 minutes, half of the two-week time-box",
     "Shorter Sprint, proportionally shorter events: half the Sprint, about half the Review."),
    [
        ("One hour, since time-boxes do not depend on Sprint length",
         "The slide says the opposite: events scale with the Sprint."),
        ("About two hours, since shorter Sprints need more feedback each time",
         "Shorter Sprints get feedback more often, in shorter Reviews, not longer ones."),
        ("Fifteen minutes, the same time-box as the Daily",
         "The Daily's fifteen minutes is a different ceremony; halving one hour gives about thirty."),
    ],
    "a",
    """
    Slide 11: Sprint Review 1h for a two-week Sprint, and "Shorter Sprint → proportionally shorter events. Longer Sprint → proportionally longer events." Half the Sprint length gives about half the Review: thirty minutes. The time-box is a maximum sized to how much there is to inspect, and a one-week Sprint produces about half as much. The same rule gives a one-week Sprint about two hours of Refinement and half-hour Planning and Retrospective.
    """,
    7, "S4 slide 11",
))

DAILY = T(
    """
    > **Head of IT** (not on the team): Right, status reports please, one by one.
    >
    > **Ana:** Yesterday I finished the `add` command. Today I start on due dates. No blockers.
    >
    > **Pol:** I'm stuck: CI fails on the lockfile and I can't push.
    >
    > **Head of IT:** Explain the lockfile issue in detail so I can decide who fixes it.
    >
    > *(twenty-five minutes of discussion between Pol and the Head of IT)*
    >
    > **Head of IT:** Good. Marc, you fix Pol's problem today; the rest of you carry on.
    """
)

Q.append(mcq(
    26, "hard", ["judgement"],
    "Read this Daily Scrum of the task-manager group (two-week Sprint):\n\n"
    + DAILY
    + "\n\nWhich statement identifies what is wrong, in session 4's terms?",
    ("It turned into a status report to an outsider who assigned work, and it overran its 15 minutes",
     "Three rules broken at once: the Daily is not a status report to a manager, who does what belongs to the team, and the time-box is fifteen minutes."),
    [
        ("The Scrum Master, not the Head of IT, should have collected the reports and picked who helps Pol",
         "That only swaps one manager for another. The Daily is not a status report to anyone, and who does what belongs to the team."),
        ("Pol should not have raised a blocker in front of someone senior",
         "Blockers are one of the three things every developer states; hiding them breaks transparency."),
        ("Nothing serious: when a real blocker comes up, the Daily is where the team should solve it",
         "A blocker is stated in a sentence at the Daily; solving it happens afterwards, with whoever the team chooses. The Daily is time-boxed to fifteen minutes."),
    ],
    "c",
    """
    Slide 12: "Daily Scrum is not a status report to a manager. Fifteen minutes, for the Developers." Here an outsider runs it, asks for "status reports", and then decides who fixes Pol's problem, which breaks slide 7 too: "The team decides how the work is done, and who does what." Twenty-five minutes on the lockfile blows the time-box. The right shape is Ana's: latest work, next work, blockers. Pol's blocker should take one sentence, then be solved afterwards by whoever the team chooses, with the Scrum Master removing the impediment if it needs outside help.
    """,
    7, "S4 slides 7, 11, 12",
))

Q.append(mcq(
    27, "exam", ["judgement"],
    """
    At the Sprint Review, the vending-machine group runs a polished demo of change-making. The stakeholders clap, say "great job" and leave after ten minutes. Nobody comments on the product, and the Product Backlog is exactly as it was. What does session 4 say is missing?
    """,
    ("Feedback from the stakeholders that changes what is in the Product Backlog",
     "Slide 12: the Review is not a demo for applause; stakeholders come to give feedback and change the backlog."),
    [
        ("A longer demo, so that the stakeholders see every feature",
         "A longer show is still a show; what is missing is the stakeholders' feedback."),
        ("A discussion of how the team worked during the Sprint",
         "That is the Retrospective's question; the Review is about the product."),
        ("The stakeholders' formal sign-off that the Increment meets the Definition of Done",
         "The DoD is a checkable bar the team applies itself (with the CI check), not something stakeholders approve at the Review."),
    ],
    "b",
    """
    Slide 12: "Review is not a demo for applause. Stakeholders come to give feedback and change the backlog." Slide 11's question for the Review has two halves: "What was built; what should change". This Review answered the first half and skipped the second. A Review that leaves the backlog untouched wastes the one meeting where users and stakeholders can redirect the product. Asking them what confused them, or what they want next, is the point of the meeting.
    """,
    7, "S4 slides 11–12",
))

Q.append(mcq(
    28, "exam", ["judgement", "concept"],
    """
    At the end of a Sprint, the parking-lot group realises that pushes collided all Sprint because nobody had agreed who pushes when. They agree a rule: announce in the group chat before pushing to `main`. In which ceremony does this conversation belong?
    """,
    ("The Sprint Retrospective: it is about how the team works and what to change",
     "Slide 11's question for the Retrospective: how the team worked, and what to improve."),
    [
        ("The Sprint Review, because it happens at the end of the Sprint",
         "Both end-of-Sprint ceremonies happen then. The Review is about the product and the backlog, not the team's way of working."),
        ("The Daily, because colliding pushes are a blocker that the developers must raise",
         "A collision on one day is a blocker to mention at the Daily; a rule changing how the team works from now on is a Retrospective outcome."),
        ("Refinement, because it changes how items will be implemented",
         "Refinement details backlog items with the PO; a push rule is not about any item."),
    ],
    "d",
    """
    Slide 11: the Retrospective answers "How the team worked, and what to improve", and slide 12 adds that it is about "what worked and what did not, and what changes can be introduced accordingly". A push rule is a change to how the team works. The Review asks a different question, "What was built; what should change", about the product. Notice also the absence of blame: the problem is framed as a missing agreement, not as whose push broke things. The scaffold lab gave the same advice: agree who pushes when.
    """,
    7, "S4 slides 11–12; labs/01-scaffold.md",
))

Q.append(mcq(
    29, "core", ["concept"],
    "Which description of the shape of a Scrum team matches session 4?",
    ("Ideally ten people or fewer, with hierarchy kept as horizontal as possible",
     "Both lines are on slide 6, under the table of accountabilities."),
    [
        ("Any size, as long as a team lead assigns work to each specialist",
         "A lead handing out work breaks two rules: hierarchy stays horizontal, and the team decides who does what."),
        ("At least fifteen people, so that every skill is covered inside the team",
         "Cross-functional, yes, but ideally ten people or fewer; a bigger group needs splitting, not growing."),
        ("A Scrum Master at the top, managing the Product Owner and the Developers",
         "The Scrum Master is \"not a manager\": the role ensures the process works and coaches."),
    ],
    "d",
    """
    Slide 6, under the table of accountabilities: "The team should ideally consist of ten people or fewer. Hierarchy stays as horizontal as possible." The three accountabilities sit side by side: the PO decides what and in what order, the Developers decide how and who, and the Scrum Master ensures the process works without managing anyone. Cross-functional means the skills to finish an item are inside the team, which is a reason to choose people well, not to grow the team past ten.
    """,
    2, "S4 slides 6–7",
))

# ---- s8 -------------------------------------------------------------------------------------
Q.append(mcq(
    30, "exam", ["judgement"],
    """
    The task-manager group's board shows every item of the Sprint in the Done column. At the Sprint Review everyone looks at the board and is pleased. In fact half the items fail the CI check, and the group knew. Which pillar has failed, and what does the Review end up doing?
    """,
    ("Transparency: the board hides the real state, so the Review inspects a fiction, not the product",
     "The Review inspected a board that hid the real state of the product. Slide 13: \"Inspection without transparency inspects a fiction.\""),
    [
        ("Adaptation: the group saw a problem and did not change course, so the next Sprint repeats this one",
         "Nothing was changed because nothing was shown. The problem never reached the Review, so there was no inspection to adapt to. (Slide 13's line for this: \"Adaptation without courage produces the same Sprint, twelve times.\")"),
        ("The Definition of Done: it could not be checked, so nobody knew which items failed",
         "Their Definition of Done was checkable: CI told them the items failed, and they knew. The board hid what the check said. (Slide 10: \"A Definition of Done you cannot check yourself is a wish.\")"),
        ("Estimation: the items were planned too precisely and so could not meet the check",
         "The story is about hiding the state of finished work, not about planning future work in too much detail."),
    ],
    "b",
    """
    Scrum's pillars are transparency, inspection and adaptation, in that order for a reason: you can only inspect what is visible, and only adapt to what you inspected. A board that says Done while the CI check is red makes the Review inspect the board, not the product. Session 4's line names it: "Inspection without transparency inspects a fiction." The Definition of Done exists to prevent exactly this: an item that fails it is not done and should never reach the Done column.
    """,
    8, "S4 slides 10, 13",
))

Q.append(mcq(
    31, "exam", ["judgement"],
    """
    For four Sprints in a row, the habit-tracker group's Retrospective notes the same problem: people push without running the tests, and CI goes red. Everyone agrees it is a problem. Nobody proposes a change, because it would mean telling two teammates that their habit has to stop. Which value is missing, according to session 4?
    """,
    ("Courage: the problem is seen and named, but nobody acts on it",
     "Slide 13: adaptation without courage produces the same Sprint, twelve times. The problem is seen and named; acting on it needs courage."),
    [
        ("Focus: the team is spread across too many items to fix anything",
         "Nothing suggests the team works on too much at once; the problem is seen and named, then not acted on."),
        ("Openness: the team hides the problem from itself",
         "The problem is raised openly at every Retrospective. What is missing is the will to act on it."),
        ("Respect: the team should not comment on teammates' habits",
         "Respect does not mean avoiding hard conversations; a Retrospective is about what changes, not blame, and that requires saying it."),
    ],
    "a",
    """
    Session 4: "Adaptation without courage produces the same Sprint, twelve times." The team inspects (the Retrospective names the problem) but never adapts, because adapting means an uncomfortable conversation. Courage is the value that turns an observation into a change, for example agreeing that everyone runs `ruff`, `mypy` and `pytest` locally before pushing. Because the Retrospective is not blame, the change can be framed as a team rule rather than an accusation.
    """,
    8, "S4 slides 12–13",
))

Q.append(mcq(
    32, "core", ["concept"],
    "A client asks what adopting Scrum will give her project. Which one of these does Scrum actually provide?",
    ("Short time-boxed Sprints, each ending with an Increment to inspect",
     "That is the organisation Scrum supplies: rhythm, roles, an ordered backlog, a working Increment."),
    [
        ("A requirements document agreed before development starts",
         "Slide 14 lists it first under what Scrum does not give you; the backlog is emergent instead."),
        ("A testing strategy and engineering practices for the code",
         "Scrum gives \"no architecture, no testing strategy, no engineering practices at all\"; the course takes those from XP."),
        ("A promise of what will be in version 1.0, a year out",
         "Explicitly not given: the backlog changes as everyone learns."),
    ],
    "d",
    """
    Slide 14: no requirements document; no promise about what is in version 1.0, a year out; no architecture, no testing strategy, no engineering practices at all. "Scrum organises the work; it does not do it." What it does give is the organisation: three accountabilities, an ordered backlog, Sprints with time-boxed ceremonies, and an Increment meeting a Definition of Done at the end of each. How the code is built well (tests, CI, clean code) has to come from elsewhere.
    """,
    8, "S4 slide 14",
))

Q.append(mcq(
    33, "hard", ["compare", "judgement"],
    """
    A student says: "The course isn't real Scrum. It uses Scrum's words, but the engineering comes from XP (TDD, CI, small commits) and we track work on a Kanban board." Which reply fits sessions 2 and 4 best?
    """,
    ("Scrum gives no engineering practices, so borrowing XP's fills that gap",
     "Session 4 names the gap; session 2 names the principle of borrowing the practices that help you iterate fast and deliver value."),
    [
        ("True, so the project should drop the XP practices and keep to the ceremonies",
         "Ceremonies alone are the mistake slide 14 warns about: following them is not enough to get real work done."),
        ("True, so the course should pick one methodology and follow it exactly",
         "Session 2 says the opposite: it is not about picking one methodology and following blindly."),
        ("Not true: Scrum already includes TDD and CI, so the course is plain Scrum",
         "Slide 14: Scrum gives no engineering practices at all. TDD and CI come from XP (session 2), which is why the course borrows them."),
    ],
    "a",
    """
    Session 4, slide 14: Scrum gives "no architecture, no testing strategy, no engineering practices at all". Something has to fill that gap, and session 2 named it: "XP's engineering practices are the technical spine: TDD, CI, small commits", with a Kanban board to track the group's work. Session 2's closing principle: "It is not about picking one methodology and following blindly, but borrowing the practices that will help you iterate fast and deliver value."
    """,
    8, "S4 slide 14; S2 slides 13–15",
))

# ---- s9 -------------------------------------------------------------------------------------
Q.append(mcq(
    34, "core", ["concept"],
    "Session 4 mapped Scrum onto the course. Which pairing is right?",
    ("Sprint Review → practice sessions and Demo Day",
     "Where the working product is shown and gets feedback, as in a Review."),
    [
        ("Product Owner → your group's most experienced member",
         "The PO in the course is the lecturer; your group are the Developers."),
        ("Sprint → one Tuesday or Friday session",
         "A Sprint is the stretch between two checkpoints, which spans several sessions."),
        ("Definition of Done → the lecturer's view of your code",
         "The DoD is a green CI check, the same for every group: a referee, not an opinion."),
    ],
    "c",
    """
    Slide 16's table: Sprint = the stretch between two checkpoints; Sprint Goal = the checkpoint's deliverable; Definition of Done = a green CI check, the same one for all groups; Product Owner = the lecturer; Developers = your group; Sprint Review = practice sessions and Demo Day. The practice sessions and Demo Day are where the working product is shown and gets feedback, which is what a Review is for.
    """,
    9, "S4 slide 16; S2 slide 14",
))

Q.append(mcq(
    35, "exam", ["concept", "judgement"],
    "Using session 4's mapping, what was the Sprint Goal of the Sprint that ended on Friday 25 September (session 5)?",
    ("Checkpoint 1's deliverable: the scaffold with one real command, at `v0.1`",
     "The Sprint Goal is the checkpoint's deliverable, and CP1 was marked at the `v0.1` tag."),
    [
        ("Attending the practice session and getting feedback from the lecturer",
         "The practice session is where the Review happens; the goal is what the Sprint delivers."),
        ("Writing at least eight backlog items and a Definition of Done for the topic",
         "That was the session 4 workshop, handed in the same day; the Sprint's deliverable was the scaffold at `v0.1`."),
        ("A finished program a stranger can run from the container image",
         "That is the final submission and Demo Day; the first Sprint's goal was much smaller."),
    ],
    "b",
    """
    Slide 16 maps the Sprint to "the stretch between two checkpoints" and the Sprint Goal to "the checkpoint's deliverable". CP1 was marked at the `v0.1` tag on 25 September: in session 5's words, the repository "stops being a template and becomes the home for your project", with one command of your own. Its Definition of Done was CP1's three binary items: the clean-clone `--help` check, the `src/` layout with an importable package, and a README that says what the program does and how to run it.
    """,
    9, "S4 slides 16–17; S5 slides 2, 14",
))

Q.append(mcq(
    36, "hard", ["read-tool-output", "judgement"],
    f"""
    On Marta's laptop, `uv run parking --help` works. Before tagging `v0.1`, the group checks CP1 item 1 the way the scaffold lab says: they clone the repository into an empty folder, `/tmp/cp1`, and run there:

    {fence("console", CP1_FAIL).replace(chr(10), chr(10) + "    ")}

    What should the group conclude?
    """,
    ("`pricing.py` is missing from the repository: commit and push it before item 1 counts",
     "The clone has every pushed file and nothing else, so a module missing there is missing from the repository."),
    [
        ("The clean clone is at fault: it works on Marta's laptop, so item 1 is already met",
         "Item 1 says \"from a clean clone\" because the laptop is not the test. It works there only because the file exists there."),
        ("Delete `.venv` and run `uv sync` again, since the environment did not install the module",
         "The environment installed fine. No reinstall can create a file the repository does not have."),
        ("Add `parking_lot.pricing` to the dependencies in `pyproject.toml` and sync again",
         "It is the group's own module, not a package from PyPI; dependencies are for other people's code."),
    ],
    "b",
    """
    The clean clone did its job. `uv sync` worked, but `cli.py` imports `parking_lot.pricing` and the clone has no such module. On Marta's laptop the file exists, so everything runs there. `git status` on her machine says which mistake it was: `src/parking_lot/pricing.py` under "Untracked files" (never committed), or a branch "ahead of 'origin/main'" (committed, never pushed). The lab explains why CP1 is checked this way: a clean clone "has no `.venv`, no caches and nothing you forgot to commit", so it catches the file that only exists on your laptop. Until the file is committed and pushed, item 1 of this binary Definition of Done is not met.
    """,
    9, "S4 slide 17; S5 slide 14; labs/01-scaffold.md §10",
    verified="run",
))

Q.append(mcq(
    37, "exam", ["concept"],
    "The project brief calls the automated CI check \"the referee, not the judge\". What does that mean for a checkpoint submission?",
    ("Red means not mechanically valid; the checklist or rubric gives the marks",
     "The brief: \"it is not marked itself, but a red check means the submission is not mechanically valid\". The marks come from the checklist or the rubric."),
    [
        ("The check gives the mark, so a green check on the tag means full marks",
         "The check is not marked itself. Green makes a submission valid; it does not make it good."),
        ("The check is advisory, so a red check is ignored if the lecturer likes the code",
         "Red means not mechanically valid; for the partial, red at `v0.5` caps Tests at 1."),
        ("The check only runs on the lecturer's own machine on the deadline day",
         "It runs on GitHub on every push, on a machine none of you owns, so you can see it before submitting."),
    ],
    "a",
    """
    The project brief: an automated check runs on every push and must be green; "it is not marked itself, but a red check means the submission is not mechanically valid. Think of it as the referee, not the judge." A referee enforces the same rules for everyone; the judge (the checklist or rubric, applied by the lecturer) decides how good the work is. That is why the course's Definition of Done is a green check: public, binary, the same for all groups and checkable before you submit.
    """,
    9, "Project brief (moodle/project-pages.md); partial rubric; S4 slides 16–17",
))

Q.append(mcq(
    38, "exam", ["judgement"],
    """
    The gradebook group tags `v0.5` on Sunday at 21:00; CI on that commit is red at the Types step. At 23:00 they push a fix to `main`, CI goes green on the new commit, and they go to bed without touching the tag. What does the marker look at after the 23:59 deadline?
    """,
    ("The red commit at the tag, so the Tests criterion is capped at 1",
     "The partial is marked at the `v0.5` tag, and the CI gate looks at that commit: that Increment misses the Definition of Done."),
    [
        ("The green commit, because `main` is what counts at the deadline",
         "The rubric marks `main` at the `v0.5` tag, which still points at the red commit."),
        ("The red commit, but CI results are not considered for the partial",
         "The rubric's CI gate says the opposite: red at `v0.5` caps the Tests criterion at 1."),
        ("Nothing at all, because the tag became invalid when `main` moved on",
         "A tag is a permanent name for one commit; it is still there, pointing at the wrong commit."),
    ],
    "c",
    """
    The rubric: the partial is "marked against your group repo's main at the `v0.5` tag", the check must be green on that commit, and "a fix pushed after the tag does not count: move the tag, or tag again as `v0.5` before the deadline." The scaffold lab defines a tag as "a permanent name for one commit". In Scrum terms, the Increment the group submitted is the one at the tag, and it misses the Definition of Done. Moving the tag onto the green commit before 23:59 would have made the green Increment the one that counts.
    """,
    9, "Partial rubric; labs/01-scaffold.md; S4 slide 16",
))

# ---- open questions -------------------------------------------------------------------------
Q.append(open_q(
    39, "exam", ["judgement"],
    """
    The parking-lot group (topic: "spaces, tickets, duration-based pricing") hands in this Product Backlog, top first:

    1. Make the output look good with colours
    2. Do the database part
    3. Write tests for pricing
    4. Pricing
    5. As an attendant, I can issue a ticket for a plate number, so that I know which car is in which space
    6. Make the code good
    """,
    [
        part(
            "1",
            "Pick two lines other than 5 and say, for each, why it is not usable as a backlog item.",
            2,
            "\"Do the database part\" is a task, not an outcome: nobody can tell when it is done. \"Write tests for pricing\" is a standard every item meets, so it belongs in the Definition of Done.",
            [
                "Identifies a line as a task or topic rather than an outcome (2 or 4) and says nobody can tell when it is done or no user gets anything",
                "Identifies a line as a standard for every item (3 or 6) that belongs in the Definition of Done",
                "Identifies a line as not checkable or with no stated benefit (1 or 6)",
            ],
            "\"They are too vague\" or \"badly written\" without the reason scores nothing: name it (task not outcome, standard not item, not checkable). Saying \"Write tests for pricing\" should be deleted misses that tests still matter: they move to the Definition of Done. Saying \"Pricing\" is too short misses the real issue: it names a topic, not what a user can do.",
        ),
        part(
            "2",
            "Rewrite two of the lines, in words, as usable items in the brief's shape.",
            2,
            "Line 4: \"As a driver, I can see the price of my stay when I leave, so that I pay the right amount.\" Line 2: \"As an attendant, I can reopen the program and still see today's tickets, so that no car is lost overnight.\"",
            [
                "Each rewrite follows the shape `As a <kind of user>, I can <do something>, so that <benefit>`, with a real user of a parking lot (driver, attendant, manager)",
                "Each rewrite is an outcome you can check by running the program, with a real benefit in the \"so that\"",
            ],
            "A rewrite that keeps the task (\"As a developer, I can set up the database, so that data is stored\") only changes the wording: the user is the team itself and nothing is checkable from outside. Dropping the \"so that\" loses the part that stops you building something nobody needs. Rewriting \"Write tests\" as an item misses that it belongs in the DoD.",
        ),
        part(
            "3",
            "Which item should be at the top, and why? Why do only the top three need detail?",
            2,
            "Issuing a ticket goes first: it is the parking lot's core value, and colours give nobody anything; order by value, not ease. Only the top three need detail because the rest will change before they are built.",
            [
                "Puts a core outcome first (issuing a ticket or pricing a stay) and justifies it by value, not ease",
                "Says the lower items will change before they are built, so detailing or estimating them now is waste",
            ],
            "Keeping colours first \"because it is quick\" is the mistake slide 30 names: ordered by value, not by what is easiest to start. Saying the top three get detail \"because the PO says so\" or \"to save time\" misses the reason: the backlog is emergent and the rest will change before anyone builds it.",
        ),
    ],
    """
    The brief's test for an item is an outcome a user gets, small enough to finish in a sitting, that you can tell is done, written as `As a <kind of user>, I can <do something>, so that <benefit>`. Lines 2 and 4 are a task and a topic, lines 3 and 6 are standards for the Definition of Done, and line 1 has no real benefit for a parking lot and should not be first: order by value, not by what is easiest to start. Only line 5 survives as it is. The order follows value: a parking lot exists to issue tickets and price stays.
    """,
    5, "Backlog brief (moodle/project-pages.md); S4 slides 9, 29–30",
))

Q.append(open_q(
    40, "exam", ["judgement"],
    """
    The gradebook group's Definition of Done:

    1. The code is clean and readable
    2. The CI check is green
    3. We test as much as we can
    4. `uv sync && uv run gradebook --help` works from a clean clone
    5. The program is fast
    6. Every function has a docstring and a test, and the whole team reviews every change
    7. The README says how to use the new behaviour

    By their own account, the group checks lines 2, 4 and 7 on every item and has never checked the others.
    """,
    [
        part(
            "1",
            "Pick two lines that are wishes rather than checks and explain why each fails as a DoD line.",
            2,
            "Lines 1 and 3. Nobody can answer yes or no to \"clean and readable\" or \"as much as we can\"; they are hopes, and a Definition of Done you cannot check yourself is a wish.",
            [
                "Names two of lines 1, 3 and 5 as wishes",
                "Explains that they cannot be answered yes or no by someone else, so they are hopes, not checks",
            ],
            "Picking line 6 as a wish is a misreading: it is checkable, just ignored. Answers that say a line is \"too vague\" without saying why (no yes-or-no answer, nobody outside could check it) get half the marks at most.",
        ),
        part(
            "2",
            "Rewrite one of your two lines, in words, as something the group can check.",
            1,
            "Line 3 becomes \"There is at least one test for the new behaviour, and the tests pass in CI\".",
            [
                "The rewrite has a yes-or-no answer someone outside the group could check (a test exists, a tool passes, a measured time)",
            ],
            "\"We test thoroughly\" or \"we really try to keep it clean\" changes the words, not the problem: it is still a hope. A good rewrite names something you can point at or run.",
        ),
        part(
            "3",
            "Line 6 is checkable, but the group never checks it. What does the brief advise, and why?",
            2,
            "Cut it, or cut it to what they will honour, such as \"another member has read the change\". Six ignored lines are worse than three kept: the list claims a bar the work does not meet.",
            [
                "Says to cut what they will not honour, or reduce it to a part they will keep",
                "Explains that an ignored line is worse than none: the list claims a standard that is not met and loses its meaning",
            ],
            "\"Keep it, it shows ambition\" is the trap the brief warns about. \"Check it before Demo Day\" misses that the DoD applies to every item, every time, not once at the end.",
        ),
        part(
            "4",
            "Which line can the group not remove, and why?",
            1,
            "Line 2, the green CI check: the same check for every group, on a machine none of them owns.",
            [
                "Names line 2 and says it is required of every group (the course's DoD, the referee)",
            ],
            "Naming line 4 confuses CP1's items with the DoD line the brief says is \"not yours to choose\". Saying \"because the lecturer likes it\" misses the reason: one public, binary check for everyone.",
        ),
    ],
    """
    The brief's rules for a DoD: "the bar every item meets. One list, applied to everything. Write it as things you can check, not things you can hope", and "Cut what you will not honour. A Definition of Done with six items you ignore is worse than three you keep." Session 4 adds that a DoD you cannot check yourself is a wish. The green CI check is the one line that is not yours to choose.
    """,
    6, "Backlog brief (moodle/project-pages.md); S4 slides 10, 17",
))

Q.append(open_q(
    41, "hard", ["judgement", "concept"],
    """
    The text-adventure group is proud of its Scrum: a Daily every morning, always under fifteen minutes; Sprint Planning, Review and Retrospective on schedule; a tidy board. At the partial submission, `uv sync` fails from a clean clone, there are two tests, and CI has been red for a week. Every Retrospective concluded that "communication went well".
    """,
    [
        part(
            "1",
            "Using session 4's slide on what Scrum does not give you, explain how a team can run every ceremony and still ship nothing that works.",
            2,
            "Scrum organises the work; it does not do it. It gives no architecture and no testing strategy, so following the ceremonies is not enough: the code still needs tests, a lockfile that installs and a green check.",
            [
                "States or paraphrases \"Scrum organises the work; it does not do it\"",
                "Says Scrum provides no engineering practices or testing strategy, so ceremonies alone do not produce working software",
            ],
            "\"They did Scrum wrong\" without saying what is missing scores little. Blaming the time-boxes or the Daily misses the point: the ceremonies ran fine, and that is exactly the slide's warning. What was absent is the engineering: tests, an install that works, a green check.",
        ),
        part(
            "2",
            "Which part of Scrum itself did they still get wrong? Name the commitment they ignored and one pillar or value missing.",
            2,
            "No Increment met the Definition of Done (a green CI check), so nothing was done, whatever the board said. The Reviews inspected a fiction (no transparency), and the Retrospectives lacked the courage to name the red check.",
            [
                "Names the Definition of Done (the Increment's commitment) as not met: red CI means not done",
                "Names transparency (inspecting a fiction) or courage (the same Sprint again), linked to the story",
            ],
            "Naming a value without linking it to the story (\"they lacked respect\") gets no mark. Missing that a red CI check for a week means no item was done is the central gap.",
        ),
        part(
            "3",
            "Name two changes for the next Sprint.",
            2,
            "Treat the green check as the bar: nothing moves to Done while CI is red, and fixing it comes first. Adopt the XP practices the course borrows: a test for each new behaviour, the four checks run before pushing, a clean-clone check before tagging.",
            [
                "A change that enforces the Definition of Done (no item counts as done with CI red; fix CI first)",
                "A concrete engineering practice (tests per behaviour, local checks before push, clean-clone check, small commits)",
            ],
            "\"Have longer Retrospectives\" or \"add another ceremony\" repeats the mistake: more organisation, no more engineering. Vague answers (\"work harder\", \"communicate better\") are not changes anyone can check. A good change is one you could verify at the next Review: CI green, a test for each item.",
        ),
    ],
    """
    Slide 14 warns of the tendency "to believe that following the ceremonies around Scrum is enough to get real work done". Scrum organises the work; the engineering practices (tests, CI, a lockfile that installs) do it, and the course takes them from XP. This group also broke Scrum itself: with CI red for a week no item met the Definition of Done, so the board and the Reviews inspected a fiction, and the Retrospectives lacked the courage to say so.
    """,
    8, "S4 slides 10, 13–14, 16; S2 slide 14",
))

Q.append(open_q(
    42, "exam", ["judgement"],
    """
    Two scenes from the end of the flashcard-trainer group's Sprint.

    **Review.** The group shows its Leitner-box feature to two classmates acting as users. The classmates say "nice". Nobody asks them anything, and the Product Backlog is unchanged afterwards.

    **Retrospective.** Forty minutes are spent establishing that Iker's push broke CI on Wednesday. The meeting ends when Iker apologises. Nothing else is decided.
    """,
    [
        part(
            "1",
            "What is each of these ceremonies for, according to session 4?",
            2,
            "The Review asks what was built and what should change: stakeholders come to give feedback and change the backlog. The Retrospective asks how the team worked and what to improve.",
            [
                "Review: what was built and what should change; feedback that changes the backlog",
                "Retrospective: how the team worked and what to improve",
            ],
            "Swapping them (the Review discusses how the team worked) is the classic confusion. \"The Review is to show the work\" gets half: it leaves out the feedback and the backlog change.",
        ),
        part(
            "2",
            "What went wrong in each scene?",
            2,
            "The Review became a demo for applause: no feedback was asked for, so the backlog could not change. The Retrospective became blame: it found a culprit instead of discussing what worked, what did not and what to change.",
            [
                "Review treated as a demo for applause: no feedback, backlog unchanged",
                "Retrospective turned into blame, with no change agreed",
            ],
            "\"The Review was too short\" misses the point; a long demo is still a demo. \"Iker should be more careful\" repeats the blame instead of naming it as the problem.",
        ),
        part(
            "3",
            "Suggest one concrete change for each meeting.",
            2,
            "At the Review, ask the users what confused them and what they want next, and let the Product Owner reorder the backlog from their answers. At the Retrospective, ask why a broken push could reach `main` and agree a team rule, such as running the four checks locally before every push.",
            [
                "A Review change that produces feedback or a backlog change (ask users questions; the PO reorders)",
                "A Retrospective change about the process, not a person (a rule such as local checks before pushing)",
            ],
            "\"Iker should not push any more\" is still blame, aimed at a person instead of the process. \"Invite more people to the Review\" does not help if nobody asks them anything, and \"make the demo better\" keeps the Review a show.",
        ),
    ],
    """
    Slide 11 gives the questions: the Review, "What was built; what should change"; the Retrospective, "How the team worked, and what to improve". Slide 12 adds what they are not: the Review is not a demo for applause (stakeholders give feedback and change the backlog), and the Retrospective is not blame (the team discusses what worked, what did not, and what changes to introduce).
    """,
    7, "S4 slides 11–12",
))

Q.append(open_q(
    43, "hard", ["judgement"],
    """
    A software company runs two-week Sprints. On day 4, the sales director, who is not on the team, walks in: "A client wants a monthly-summary report by Friday. Put it in this Sprint. Laura, you do it tonight; skip the tests, we can add them later."
    """,
    [
        part(
            "1",
            "Name three things in this request that break session 4's rules, and the rule each one breaks.",
            3,
            "He decides how much goes into the Sprint, but nobody outside does. He decides who does the work, but the team decides who does what. \"Skip the tests\" produces an item that misses the Definition of Done, and \"done except for tests\" is not admissible.",
            [
                "An outsider deciding how much goes into the Sprint (nobody outside decides)",
                "An outsider deciding who does what or how (that belongs to the self-managing team)",
                "Skipping tests: the item would miss the Definition of Done, so it is not done",
                "The request bypasses the Product Owner, who decides what is worth doing and in what order",
            ],
            "Naming only the urgency (\"Friday is too soon\") misses the rules. \"He is rude\" is not a Scrum rule. Many answers find the outsider and the tests but forget that \"Laura, you do it\" is a decision that belongs to the team.",
        ),
        part(
            "2",
            "What should happen to the request instead?",
            2,
            "It goes to the Product Owner, who decides whether it is worth doing and where it goes in the Product Backlog. If it is urgent, the PO can put it at the top for the next Sprint Planning; only the PO could cancel the current Sprint, which almost never happens.",
            [
                "The request goes to the Product Owner and into the Product Backlog, ordered by value",
                "It is picked up at the next Sprint Planning (or, rarely, the PO cancels the Sprint)",
            ],
            "\"The team says no\" is incomplete: the request is not rejected, it is routed to the person who orders the work. \"The Scrum Master decides\" gives the decision to the wrong role.",
        ),
        part(
            "3",
            "What is the Scrum Master's part in this?",
            1,
            "To make the process work: send the director to the PO and protect the Sprint from the interruption, treating it as an impediment to remove.",
            [
                "The Scrum Master protects the process, removing the impediment by redirecting the request to the PO, without deciding on the request",
            ],
            "\"The Scrum Master assigns it to someone with time\" makes the Scrum Master a manager, which the slide says the role is not. \"The Scrum Master tells the director no\" is closer but incomplete: the request is not rejected, it is sent to the Product Owner.",
        ),
    ],
    """
    Slide 7: the team decides how the work is done and who does what; the PO decides what is worth doing and in what order; nobody outside decides how much goes into a Sprint. Slide 10: "done except for tests" is not admissible. Slide 6: the Scrum Master ensures the process works and removes impediments, and is not a manager. Slide 12: the PO retains the power to cancel the Sprint, and this almost never happens.
    """,
    3, "S4 slides 6, 7, 10, 12",
))

Q.append(open_q(
    44, "beyond", ["judgement", "concept"],
    """
    The meal-planner group's Definition of Done:

    1. The CI check is green
    2. There is at least one test for the new behaviour
    3. The README says how to use the new behaviour

    Nico pushes a new `scale` command (recipes scaled by servings) and a README line. CI is green: all 9 existing tests pass. He adds no test and says: "CI is green, and the course's Definition of Done is a green CI check, so it's done."
    """,
    [
        part(
            "1",
            "Is the item done? Explain using the group's Definition of Done.",
            2,
            "No. Lines 1 and 3 are met but line 2 is not: no test covers `scale`. The DoD is one list applied to everything, and an item that misses any line is not done and does not ship.",
            [
                "Says not done because line 2 (a test for the new behaviour) is not met",
                "Says the whole DoD applies to every item; missing one line means not done",
            ],
            "\"Done, because CI is green\" accepts Nico's argument. \"Nearly done\" is \"done except for tests\", which session 4 says is not admissible. Answers that quote line 1 and stop there miss that the DoD is the whole list, applied to every item.",
        ),
        part(
            "2",
            "How can CI be green while the new behaviour is untested?",
            2,
            "CI only runs the tests that exist. With no test for `scale`, nothing checks it, so nothing about it can fail: green says the existing tests pass, not that the new code is right.",
            [
                "CI runs only the existing tests; with no test for `scale`, nothing about it can fail",
                "A green check is necessary, not sufficient: it does not show that the new behaviour works",
            ],
            "\"CI must be broken\" misreads it: CI did exactly its job. Answers that say \"the tests are wrong\" miss that the problem is a test that does not exist. A check can only fail on what it checks.",
        ),
        part(
            "3",
            "How does the course's Definition of Done relate to the group's own?",
            1,
            "The green CI check is the line every group must have; each group adds its own checkable lines, and the lecturer holds each group to its own Definition of Done.",
            [
                "Green CI is the shared minimum, not theirs to choose; the group's own lines add to it and bind them too",
            ],
            "\"The course's DoD replaces the group's\" is Nico's mistake. \"The group's DoD replaces CI\" is the opposite mistake: the green check is not optional. The two stack: the shared minimum, plus the group's own lines.",
        ),
    ],
    """
    The course maps the Definition of Done to a green CI check, the line that is not yours to choose; the backlog brief asks each group to add its own checkable lines, and the lecturer said "I hold you to your own Definition of Done". A green check only shows that the tests that exist pass. That is why the brief's starter list adds "There is at least one test for the new behaviour": without it, new code can arrive with nothing that could ever turn the check red.
    """,
    9, "Backlog brief; S4 slides 10, 16, 29",
    lines="5–8",
))

Q.append(open_q(
    45, "hard", ["compare", "judgement"],
    """
    A client wants a gym-workout logger for her chain of gyms. She asks for a signed requirements document before any code is written, and a fixed promise of what version 1.0 will contain in twelve months. You propose Scrum instead.
    """,
    [
        part(
            "1",
            "What is she asking for that Scrum does not give?",
            2,
            "Scrum gives no requirements document and no promise about what is in version 1.0 a year out. The Product Backlog is emergent: it is reordered and refined as everyone learns, and only the top is detailed.",
            [
                "No requirements document and no fixed promise for version 1.0 a year out",
                "The backlog is emergent: it changes as the team learns, and only the top is detailed",
            ],
            "\"Scrum is faster\" does not answer the question. Saying Scrum gives a requirements document \"in the backlog\" misses that the backlog is never finished and only detailed near the top, so there is nothing to sign off up front.",
        ),
        part(
            "2",
            "What does she get instead?",
            2,
            "A working Increment every Sprint that meets the Definition of Done, a Sprint Review where she gives feedback and changes the backlog, and one Product Owner who orders the work by value.",
            [
                "Frequent working Increments that meet the Definition of Done",
                "Feedback at each Review that changes the backlog, with the PO ordering by value",
            ],
            "\"Flexibility\" alone is too vague to score. Promising that Scrum delivers everything she wanted, sooner, is the over-sell session 2 warned about: Agile is not free. Name what she sees and when: a working Increment every Sprint, and a Review where her feedback changes the plan.",
        ),
        part(
            "3",
            "Name one real cost of the switch for her, as session 2's workshop asked.",
            2,
            "Less up-front certainty about the final scope, so it is harder to agree a fixed price for a fixed scope. She also has to spend time at Reviews giving feedback.",
            [
                "Names a real downside: less certainty about final scope, a harder fixed price, or her time needed at Reviews",
                "Explains why it follows (scope emerges Sprint by Sprint; feedback needs her)",
            ],
            "\"No downside\" contradicts the workshop, which asked for at least one. A downside that does not follow from Scrum (\"developers are lazier\") scores nothing. The workshop asked for a real cost precisely because switching is never free.",
        ),
    ],
    """
    Slide 14: Scrum gives no requirements document and no promise about version 1.0 a year out; Scrum organises the work. Session 2 explains why: Waterfall's assumption of stable, known requirements fails for software, and Agile replaces it with short cycles of working software and feedback. The session 2 workshop asked groups to name what switching costs (less up-front certainty, a harder fixed price, more coordination): Agile is not free.
    """,
    8, "S4 slides 5, 9, 14; S2 slides 6–8; session 2 workshop brief",
))

# ---- added after review: coverage gaps --------------------------------------------------------
Q.append(mcq(
    46, "core", ["concept"],
    """
    The movie-watchlist group books its meetings for a two-week Sprint (the Daily stays at 15 minutes). Which booking matches session 4's time-boxes?
    """,
    ("Refinement ~4h · Planning 1h · Review 1h · Retrospective 1h",
     "Slide 11's time-boxes for a two-week Sprint."),
    [
        ("Refinement 1h · Planning ~4h · Review 1h · Retrospective 1h",
         "This swaps the two planning meetings. On slide 11 Refinement is the long one (~4h); Sprint Planning only has to agree what the Sprint will deliver, in 1h."),
        ("Refinement ~4h · Planning 1h · Review ~4h · Retrospective 1h",
         "The Review is 1h for a two-week Sprint, the same as Planning and the Retrospective. The long meeting is Refinement."),
        ("No Refinement · Planning 1h · Review 1h · Retrospective 1h",
         "Slide 11 lists Refinement as a ceremony of about four hours: it is where the items near the top of the backlog get their detail."),
    ],
    "d",
    """
    Slide 11, for a two-week Sprint: Refinement ~4h, Sprint Planning 1h, Daily 15 min, Sprint Review 1h, Sprint Retrospective 1h, and "Shorter Sprint → proportionally shorter events". The long meeting is Refinement, where the Product Owner and the Developers work through the items near the top of the backlog. With those items already detailed, Sprint Planning only has to agree what the Sprint will deliver, in an hour. Books and websites about Scrum give other maximums; the exam follows the slide.
    """,
    7, "S4 slide 11",
))

Q.append(mcq(
    47, "exam", ["judgement"],
    """
    In its first week, a team building a habit-tracking app writes 25 backlog items. The Product Owner and the Developers sign the list and agree that nothing new goes in until all 25 are built. In week 5, users trying the first Increment keep asking for a daily reminder. What does session 4 say should happen to the reminder?
    """,
    ("It goes into the Product Backlog, where the PO orders it by value",
     "Ordered, emergent, never finished: new items appear as people use the product, and the PO decides where they go."),
    [
        ("It waits until all 25 signed items are built, so that the agreed plan holds",
         "That treats the backlog as a signed specification, the Waterfall gate from session 2. Slide 9: the Product Backlog is emergent and never finished."),
        ("It goes on a separate list of new ideas, so that the signed backlog stays stable",
         "Two lists means two orders and no single place where every request competes on value. The PO owns and orders one Product Backlog."),
        ("It goes at the bottom of the backlog, since items are built in the order they arrive",
         "Position is a decision about value, not about arrival. Top = next because the PO put it there."),
    ],
    "c",
    """
    Slide 9: the Product Backlog is "Ordered. Emergent. Never finished." New items appear as people use the product and learn, which is why Agile puts working software in front of users early. A backlog that is signed and closed is a requirements document in disguise, and slide 14 says Scrum does not give you one. The reminder goes into the one Product Backlog, and the Product Owner decides its place. If users keep asking for it, it may well go near the top.
    """,
    4, "S4 slides 9, 14",
))

Q.append(mcq(
    48, "exam", ["judgement"],
    """
    The fare-calculator group checks Checkpoint 1 before tagging `v0.1`. From a clean clone, `uv sync && uv run fares --help` works and lists their command, and the package `fare_calculator` imports without errors. The whole README is one sentence: "A fare calculator for zones and travelcards." Which CP1 item is not met?
    """,
    ("The README item: it says what the program is, but not how to install and run it",
     "The item is binary: the README tells a stranger how to run the program, or it does not. This one does not."),
    [
        ("None: the README says what the program does, and both commands work",
         "The README item asks for what it does and how to run it; session 5's version adds how to install. A stranger cannot get from this README to a first run."),
        ("The clean-clone item: it works, but only for someone who already knows the command",
         "The clean-clone item is the command working from a clean clone, and it does. Telling people which command to type is the README's job."),
        ("The layout item: a README must describe the `src/` layout before the package counts",
         "The layout item is the `src/` layout with the package importable, and both are true here. It says nothing about the README."),
    ],
    "b",
    """
    CP1 is a Definition of Done in miniature: three binary items, "checkable before you submit". Items 1 and 2 are met: the commands work from a clean clone and the package imports. Item 3 is "README says what the program does and how to run it" (session 5's slide: what it does, how to install, how to run). This README stops after the first part, so a stranger cannot get from the clone to a first result. Two more lines, `uv sync` and one real `uv run fares` example, would meet it.
    """,
    9, "S4 slide 17; S5 slide 14; labs/01-scaffold.md §10",
))

Q.append(sort(
    49, "core", ["concept", "judgement"],
    "Each situation shows one pillar or value of Scrum at work. Sort it by the one it shows best.",
    [("transparency", "Transparency"), ("inspection", "Inspection"), ("adaptation", "Adaptation"), ("courage", "Courage")],
    [
        ("The board shows the real state: an item that fails the CI check stays in \"In progress\"", "transparency",
         "The real state of the work is visible to everyone, so there is something true to inspect."),
        ("The Sprint Backlog is open to the whole team and updated every day", "transparency",
         "Making the work visible is the first pillar; a hidden plan cannot be inspected."),
        ("At the Review the team runs the product and compares it with the Sprint Goal", "inspection",
         "Looking at the actual work at regular points, not at a report about it."),
        ("Before the Review the Scrum Master asks the team to check that every Done item meets the Definition of Done", "inspection",
         "Checking the work against the agreed bar before showing it is inspection."),
        ("After the Retrospective the group adds \"README updated\" to its Definition of Done", "adaptation",
         "Changing how the team works because the inspection showed a gap."),
        ("The Product Owner reorders the backlog after the Review shows users want a different feature first", "adaptation",
         "Changing course because of what was inspected."),
        ("A developer tells the Daily that her item will not be finished, although she knows it is bad news", "courage",
         "Saying something unwelcome is the value slide 13 ties to adaptation. Without it, nothing changes."),
        ("The Product Owner removes her favourite item from the backlog because the evidence says it is not worth doing", "courage",
         "Acting on evidence against your own idea takes courage; the other values do not cover it."),
    ],
    """
    Slide 13: pillars are transparency, inspection and adaptation; the values include courage. The pillars are a sequence (make it visible, look at it, change course), and the slide's two lines tie them to the values: "Inspection without transparency inspects a fiction. Adaptation without courage produces the same Sprint, twelve times." Courage is what turns a visible problem into a changed Sprint. To remember the plain list, use the flashcard.
    """,
    8, "S4 slide 13",
))

Q.append(mcq(
    50, "beyond", ["read-tool-output", "judgement"],
    f"""
    The fare-calculator group's Checkpoint 1 says `uv sync && uv run fares --help` must work from a clean clone. Ana clones the repository to `~/fare-calculator` to check it, and in the same terminal types:

    {fence("console", WRONG_FOLDER).replace(chr(10), chr(10) + "    ")}

    She writes to the group: "The first CP1 item fails from a clean clone. We cannot tag `v0.1`." What is the right reading?
    """,
    ("She ran the command in her home folder, not in the clone; check again from inside `~/fare-calculator` before judging the item",
     "`pwd` shows `/home/ana`. uv finds the project from the current folder and its parents, so outside the clone there is no `fares` to start. The check was run in the wrong place."),
    [
        ("The item fails: `[project.scripts]` does not match the command, so rename the entry and tag again",
         "`Failed to spawn` can mean that, but only after the check is run inside the project. From her home folder every project command fails the same way."),
        ("The item fails because `uv sync` was not run; running it from her home folder first would fix it",
         "`uv sync` also needs a project: from `/home/ana` it prints `No `pyproject.toml` found`. We ran it."),
        ("The item is met: a clean clone only has to exist, and the command is checked later at the tag",
         "Checkpoint 1 is three binary items \"checkable before you submit\", and the first is the command working from a clean clone. It is checked inside the clone."),
    ],
    "a",
    """
    A Definition of Done is only useful if the check is run properly (slide 10: one you cannot check yourself is a wish). Ana's red is a false red. Read the prompt: `pwd` prints `/home/ana`, not the clone, so `uv run fares` looks for the project in the wrong place and fails with the same `Failed to spawn` message a real mismatch gives. The lab's table lists that message with causes inside the project, so the reading needs the folder as well as the error. `cd ~/fare-calculator && uv sync && uv run fares --help` is the real check. Real run: the same command in a folder without a project printed the error shown.
    """,
    9, "S4 slides 10, 17, 23; S5 slide 13; labs/01-scaffold.md troubleshooting",
    verified="run",
))

Q.append(open_q(
    51, "exam", ["compare", "judgement"],
    """
    The fare-calculator group (topic: zones, travelcards, the cheapest way to cover a week) disagrees about the top of its Product Backlog. Two candidates:

    - **A:** "Write `zones.py` with a dictionary of fares and one function per travelcard"
    - **B:** "As a commuter, I can enter the trips I make in a week and see the cheapest ticket or travelcard for them, so that I do not overpay"
    """,
    [
        part(
            "1",
            "In one sentence each, what does A describe and what does B describe?",
            1,
            "A describes work the team would do, and how it would build it; B describes what a commuter can do with the program, and why they want it.",
            [
                "Says A is a task (code to write) rather than something a user gets, and B is an outcome for a user with its benefit",
            ],
            "\"A is technical and B is not\" is only half the point: name A as a task (work you do) and B as an outcome (what a user gets). \"B is longer\" or \"B uses the template\" describes the form, not the difference, which is that B says who gains what.",
        ),
        part(
            "2",
            "Which one belongs in the Product Backlog, and why? Answer from the point of view of whoever has to order the backlog.",
            2,
            "B. It names a user and a benefit, so it can be ordered by value against other items, and anyone can tell when it is done by running the program. A is a task nobody can tell is finished, and it decides how (a dictionary), which is the Developers' call.",
            [
                "Chooses B because it is an outcome with a stated benefit that can be ordered by value",
                "Says A is a task (nobody can tell when it is done) or prescribes how, which belongs to the Developers",
            ],
            "\"B, because it follows the template\" gets half at most: say what the template gives (a user, a benefit, something you can check). Choosing A \"because it is more concrete\" confuses precise with checkable: A is precise about code but says nothing a user gets, so nobody can order it by value or say when it is done.",
        ),
        part(
            "3",
            "Describe in words one check that would show B is done, and the line of a Definition of Done it satisfies.",
            2,
            "A test: a week with many zone-1 trips gets the travelcard, and a week with one trip gets a single ticket. It meets \"there is at least one test for the new behaviour\", and it runs inside the green CI check.",
            [
                "A concrete check in words, with an input and the expected result",
                "Links it to a Definition of Done line: a test for the new behaviour, or the CI check being green",
            ],
            "\"Test that it works\" names no input and no expected result, so it checks nothing. A check on A's dictionary (\"it has every zone\") tests the shape of the code, not what the commuter gets. A check without the DoD line, or the line without a check, gets half.",
        ),
    ],
    """
    This is the teacher's compare shape applied to the backlog: two candidates, which is better for the person who has to use it, and one check in words. The brief defines an item as "an outcome a user gets, not a task you perform", small enough to finish in a sitting and something you can tell is done, written as `As a <kind of user>, I can <do something>, so that <benefit>`. B fits; A is a task, and it also decides how the work is done, which slide 7 gives to the Developers. The check in part 3 is what makes B done under a Definition of Done written as "things you can check, not things you can hope".
    """,
    5, "Backlog brief (moodle/project-pages.md); S4 slides 7, 9, 30; sample Q8 shape",
    lines="5–8",
))

Q.append(open_q(
    52, "hard", ["read-tool-output", "judgement"],
    f"""
    The fare-calculator group's Definition of Done starts with "The CI check is green". Iker pushes the peak-fare item the evening before the Sprint Review. CI is red at the Types step, which runs `uv run mypy src tests`:

    {fence("text", MYPY_FARES).replace(chr(10), chr(10) + "    ")}

    The file it points at, `src/fare_calculator/fares.py`:

    {fence("python", FARES_PY).replace(chr(10), chr(10) + "    ")}
    """,
    [
        part(
            "1",
            "Is the peak-fare item done? Answer in terms of the group's Definition of Done.",
            1,
            "No. CI is red, so the item misses the Definition of Done: it is not done, does not ship, and is not shown as finished tomorrow.",
            [
                "Says not done because CI is red and the DoD requires green, so the item does not ship",
            ],
            "\"Nearly done, only the types are wrong\" is \"done except for...\", which session 4 says is not admissible. \"Done, because the tests pass\" ignores that the Types step is part of the same check, and the check is the line in the DoD.",
        ),
        part(
            "2",
            "Which error could crash the program for a real user, and how? What kind of error is the other one?",
            2,
            "Line 10: a zone that is not in the table, such as 4, makes `find_fare` return `None`, and adding 0.50 to `None` raises a `TypeError`: None not handled. Line 13 is a missing annotation; it crashes nothing by itself.",
            [
                "Names line 10 and the input that crashes it: an unknown zone makes `find_fare` return None, and None + 0.50 fails",
                "Classifies line 13 as a missing annotation that does not crash by itself",
            ],
            "\"Line 13, because the function has no types\" confuses a missing hint with a crash: Python runs it fine. Saying line 10 is wrong \"because of the types\" without naming the input that triggers it (a zone not in the table) misses the user's view: the crash happens at run time, for a real zone number.",
        ),
        part(
            "3",
            "Iker proposes adding `# type: ignore` to both lines so CI is green for the Review, and fixing them next Sprint. Do you accept? Give your reasoning in session 4's terms.",
            3,
            "No. CI would go green but zone 4 would still crash, so the Review would inspect a fiction and the Definition of Done would mean nothing. Fix both tonight (handle the unknown zone with a clear message, add the hint) or say at the Review that the item is not done.",
            [
                "Rejects it: silencing the check leaves the crash for an unknown zone in place",
                "Uses session 4: a green check that hides a known bug makes the Review inspect a fiction (transparency), or the DoD becomes decoration",
                "Gives the honest alternative: fix both errors, or present the item as not done",
            ],
            "\"Yes, if they fix it next Sprint\" ships a known crash and calls it done. \"No, ignores are bad style\" gives no reason anyone can act on: say what stays broken (zone 4 still crashes) and what the Review would then be looking at. Changing `find_fare` to return `float` does not help either: mypy then flags the line that can return `None`, because the missing zone is still possible.",
        ),
    ],
    """
    This is the teacher's read-tool-output shape with a Scrum ending. Line 10 is the None-not-handled kind: an unknown zone makes `find_fare` return `None`, and adding the surcharge to `None` raises `TypeError`, session 7's "crash at 2 a.m.". Line 13 is a missing annotation. Under the group's Definition of Done the item is not done while CI is red. With `# type: ignore` on both lines mypy reports no issues, yet `peak_fare(4)` still crashes: the check would be green and false. The Review would then inspect a fiction, which is what the transparency pillar exists to prevent.
    """,
    6, "S4 slides 10, 13; S7 slides 8–10; sample Q9 shape",
    verified="run",
))

Q.append(mcq(
    53, "hard", ["judgement"],
    """
    At the habit-tracker group's Daily, the Product Owner joins. After the first developer speaks, she starts discussing which items should be dropped from the Sprint and asks each developer to justify their progress to her. The Daily ends after forty minutes. In session 4's terms, what went wrong?
    """,
    ("She may join but is not expected to take part; the Daily became a report to her",
     "Slide 12: the PO can join but is not expected to participate. Turning the Daily into a report to her also broke its fifteen-minute time-box."),
    [
        ("Nothing: the PO orders the work, so the Daily is the natural place to re-plan it",
         "The PO orders the Product Backlog, but the Daily is fifteen minutes for the Developers to check progress towards the Sprint Goal, not a planning meeting."),
        ("The PO should not have come: the Daily is for the Developers, and she has no place there",
         "Slide 12 says the PO can join. What went wrong is what she did once she was there, not that she came."),
        ("The Scrum Master should have collected the reports instead, so the PO could leave early",
         "The Scrum Master is not a manager either; the Daily is not a status report to anyone."),
    ],
    "d",
    """
    Slide 12: "Daily Scrum is not a status report to a manager. Fifteen minutes, for the Developers. PO can join but not expected to participate." Here the PO turns the Daily into a report to her and a re-planning session, and it runs to forty minutes. Each developer should take about a minute: latest work, what they will work on next, any blockers. Her being there is allowed; her taking over is not. If she thinks the Sprint's scope is wrong, she can raise it with the Developers after the Daily; in the extreme, the PO retains the power to cancel the Sprint.
    """,
    7, "S4 slides 7, 12",
))

Q.append(mcq(
    54, "exam", ["concept", "judgement"],
    """
    The task-manager group has forty well-written backlog items, ordered by the Product Owner, and a Definition of Done. At the Review a visitor asks what the product as a whole is for. Three team members give three different answers. Which commitment is missing?
    """,
    ("The Product Goal: the Product Backlog's commitment, what the whole backlog is heading towards",
     "Slide 8: Product Backlog → Product Goal. Without it, the backlog is \"just a list\" and nobody can say what the product is for."),
    [
        ("The Sprint Goal: the commitment that says what the current Sprint is for",
         "The Sprint Goal belongs to the Sprint Backlog and covers one Sprint. The visitor asked about the product as a whole."),
        ("The Definition of Done: the quality bar every Increment has to meet",
         "The group has one. It says how good finished work must be, not what the product is for."),
        ("More backlog items: with another forty the purpose would become clear",
         "More items do not answer the question. Slide 8: \"Without its commitment, it is just a list.\""),
    ],
    "a",
    """
    Slide 8 gives each artifact a commitment: Product Backlog → Product Goal, Sprint Backlog → Sprint Goal, Increment → Definition of Done. Each exists to make something visible, and "without its commitment, it is just a list". The group has a good list and a quality bar, but nothing that says where the list is heading, so the team members each supply their own purpose. A Product Goal is one sentence that every backlog item can be tested against. The Sprint Goal is the smaller version for one Sprint.
    """,
    4, "S4 slide 8",
))

module: dict[str, Any] = {
    "id": MID,
    "order": 2,
    "module": "M1",
    "title": "Scrum, the backlog and the Definition of Done",
    "sessions": [4],
    "predicted": False,
    "sources": [
        "slides-session-4 (slides 1–17, 28–30)",
        "moodle/project-pages.md (backlog brief, project brief)",
        "slides-session-5 (CP1)",
        "slides-session-2 (Agile methods, what the course uses)",
        "slides-session-7 (mypy's three kinds of error, for one cross-session question)",
        "labs/01-scaffold.md (checking CP1 from a clean clone)",
        "partial-rubric",
        "expense-tracker v0.0..v0.1",
    ],
    "summary_md": T(
        """
        Session 4 opened with Scrum, the most used way of working in short cycles and, in the lecturer's words, the most commonly misapplied. This module teaches that first half from zero: the three accountabilities and who decides what in a self-managing team; the three artifacts and the commitment that stops each one being just a list; how to write a backlog item that is an outcome rather than a task; and the Definition of Done as the quality bar every Increment meets. It covers the five ceremonies, their time-boxes and what they are not, the pillars and values, and what Scrum does not give you: "Scrum organises the work; it does not do it." It ends with how the course maps Scrum onto the group project, where a green CI check is the Definition of Done and Checkpoint 1 is three binary items you can check yourself.
        """
    ),
    "exam_focus_md": T(
        """
        - Short "who decides?" scenarios: a manager adding work mid-Sprint, a Scrum Master who assigns tasks, a Product Owner committee, a PO who prescribes how an item is built.
        - Candidate backlog items or Definition of Done lines to judge: outcome or task, checkable or a wish, backlog or Definition of Done.
        - A meeting described in a few lines (a Daily turned status report, a Review treated as applause, a Retrospective turned into blame) and which rule it breaks.
        - Matching: artifact to commitment, ceremony to the question it answers or its time-box, Scrum term to its meaning in the course.
        - Tool output as evidence about "done": a red CI step, a failing pytest line, a clean-clone check that breaks. The judgement is whether the item meets the Definition of Done, not how to silence the tool.
        - Open answers in 5–8 lines: rewrite a weak backlog in words and justify the order; compare a task with an outcome as a backlog item; evaluate a team's Definition of Done; read a red CI step and decide whether `# type: ignore` makes an item done; explain why a team that runs every ceremony still ships nothing that works.
        """
    ),
    "sections": sections,
    "terms": [{"term": t, "definition_md": d, "section_ref": sid(s)} for t, d, s in terms],
    "traps": traps,
    "flashcards": flashcards,
    "questions": Q,
}


def main() -> None:
    OUT.write_text(json.dumps(module, ensure_ascii=False, indent=1) + "\n")
    print(f"wrote {OUT} ({len(Q)} questions)")


if __name__ == "__main__":
    main()
