"""Build content/sdlc-agile.json: M1, sessions 1 and 2 (the lifecycle, Waterfall and Agile).

Run from the study-site folder:
    uv run python content/src/sdlc-agile.py
    uv run python tools/validate.py content/sdlc-agile.json

Artefacts that show real tool output (q06, q07, q38, q50 and the section s9 transcript) were produced by
running them; the raw runs are kept in the scratch work folders (work/sdlc-agile/ and, for the review
pass, work/sdlc-agile-fix/).
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

MID = "sdlc-agile"
OUT = Path(__file__).resolve().parent.parent / f"{MID}.json"


ARTEFACTS: dict[str, str] = {}


def md(text: str) -> str:
    out = textwrap.dedent(text).strip()
    for token, block in ARTEFACTS.items():
        out = out.replace(token, block.strip())
    return out


def sid(n: int) -> str:
    return f"{MID}-s{n}"


def qid(n: int) -> str:
    return f"{MID}-q{n:02d}"


def opt(text: str, why: str, ok: bool = False) -> dict[str, Any]:
    return {"text_md": md(text), "correct": ok, "why_md": md(why)}


def mcq(
    n: int,
    level: str,
    skills: list[str],
    sec: int,
    source: str,
    stem: str,
    options: list[dict[str, Any]],
    explanation: str,
    origin: str = "slides",
    verified: str = "source",
) -> dict[str, Any]:
    return {
        "id": qid(n),
        "type": "mcq",
        "level": level,
        "skills": skills,
        "stem_md": md(stem),
        "options": options,
        "explanation_md": md(explanation),
        "section_ref": sid(sec),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
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
    sec: int,
    source: str,
    stem: str,
    parts: list[dict[str, Any]],
    explanation: str,
    origin: str = "slides",
    verified: str = "source",
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
        "section_ref": sid(sec),
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
    stem: str,
    categories: list[tuple[str, str]],
    items: list[tuple[str, str, str]],
    explanation: str,
    origin: str = "slides",
    verified: str = "source",
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
        "section_ref": sid(sec),
        "source_ref": source,
        "origin": origin,
        "verified_by": verified,
    }


# ---------------------------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------------------------

SECTIONS: list[dict[str, Any]] = [
    {
        "id": sid(1),
        "heading": "Software engineering, and the ways working code still fails",
        "body_md": md(
            """
            Software engineering, in the course's definition, is "the systematic process of designing, developing, testing, and maintaining computer software using scientific and engineering principles". It goes beyond writing code: it is the structured approach that keeps a program **reliable, secure, efficient, and easy to maintain over time**.

            That is why session 1 says this is **not a Python course**. Syntax is assumed (loops, functions, types, one completed Python course), and new constructs arrive "as design tools, not language tourism". The goal is what happens to the little program you wrote **once three teammates get involved** and it has to run reliably, be easy to change, and be trustworthy.

            Slide 6 lists the ways working code still fails once other people and time are involved (its title says six; it lists the five below). Slide 8 puts a methodology or a tool against each:

            | What goes wrong | What it looks like | The course's answer |
            |---|---|---|
            | "Works on my machine", and nowhere else | It runs for its author; on a teammate's laptop or a server it does not | Containerisation, automatic deployment |
            | A teammate's code change breaks the build | One person's change lands and the shared project stops passing its checks | Version control, code reviews, CI |
            | Six months on, nobody can read it, not even its author | Names like `d`, `r`, `x`; the comment on slide 7 admitting that only god now knows how the routine works | Clean code, testing, TDD |
            | Change one thing, three others break, silently | A small edit quietly breaks behaviour somewhere else and nothing tells you | Clean code, testing, TDD |
            | No shared plan, four people build four corners | Each member builds the part they imagined; the parts never add up to one product | Agile, Scrum |

            Slide 8 groups the two middle failures as "unreadable, breaks silently". The tools are "a curated, opinionated selection": pytest, git, GitHub, Docker. Session 3 adds that "works on my machine" is "the single problem this whole course is built to solve", which is why uv installs the same versions for everyone from the very first lab.

            Read the table as the map of the term: every later session is one of these answers. When an exam story describes a team in trouble, first name the failure, then the practice that prevents it.
            """
        ),
        "key_points": [
            "Software engineering is a systematic process (design, develop, test, maintain) that keeps software reliable, secure, efficient and easy to maintain.",
            "Not a Python course: it is about what happens to code once teammates are involved.",
            "No shared plan → Agile, Scrum. Unreadable, breaks silently → clean code, testing, TDD. Change breaks the build → version control, code reviews, CI. Works on my machine → containerisation, automatic deployment.",
            "Name the failure first, then the practice that answers it.",
        ],
        "exam_note_md": "Expect a short team story: you name the failure from slide 6 and the answer from slide 8. Keep the pairings exact; vague answers such as \"better teamwork\" score nothing.",
        "source_ref": "S1 slides 5–8, 10; S3 slide 3",
        "check": [qid(3), qid(5), qid(7)],
    },
    {
        "id": sid(2),
        "heading": "The SDLC: seven phases on the expense tracker",
        "body_md": md(
            """
            The **software development lifecycle (SDLC)** is the sequence of phases software goes through: **Idea, Analysis, Design, Development, Testing, Deployment, Maintenance**. Following it, "we build and protect the software *before* users get to it". One sentence sets up session 2: "The methodology lies in how we transition from one phase to the next."

            Session 1 walks through the phases with one example, an app to track expenses:

            - **Idea**: "We discover the mission: what do we want to create?" Who will use it? What problem does it solve? What should it do?
            - **Analysis**: "We explore the terrain and gather tools." Everything it will do, pinned down before the build starts:

            | Feature | What it does |
            |---|---|
            | Add an expense | Record its amount, category and date |
            | List expenses | Show everything recorded |
            | Summary by category | Total the spending in each category |

            - **Design**: the structure. How the pieces connect, how someone moves through it, how the software behaves.
            - **Development**: build it, from the design. Implement add, list and summarise, then wire them up.
            - **Testing**: verify it does what the analysis said. "A checklist, run every time, not once."
            - **Deployment**: publish it, "so someone who is not its author can actually use it".
            - **Maintenance**: fix bugs, improve what is slow or ugly, keep it running. "Forever."

            Three lessons follow. First, **development arrives comparatively late**: three phases happen before anyone types code, so there is a lot of thinking about the code before writing it.

            Second, testing is not a one-off event. A check you run once tells you about one moment. The same checklist, run after every change, tells you whether the last change broke something. In this course that checklist is the CI check (ruff, mypy and pytest) that runs on every push.

            Third, deployment has a precise test: it is done when someone other than the author can use the program. A program that runs only on your laptop has not been deployed.
            """
        ),
        "key_points": [
            "Idea, Analysis, Design, Development, Testing, Deployment, Maintenance.",
            "Three phases happen before anyone types code: development arrives late.",
            "Testing is \"a checklist, run every time, not once\".",
            "Deployed means someone who is not the author can use it.",
        ],
        "exam_note_md": "A question may describe a decision or an artefact (a feature table, a sketch of the structure, a checklist) and ask for its phase. Analysis pins down what it will do; Design decides how the pieces connect.",
        "source_ref": "S1 slides 15–18",
        "check": [qid(9), qid(10), qid(11)],
    },
    {
        "id": sid(3),
        "heading": "Software is living: bugs, features, refactors and tech debt",
        "body_md": md(
            """
            Maintenance is the phase that never ends. "Most software is maintained far longer than it is written." The course treats software as **living and evolving**: the lifecycle is not a finite set of steps that ends in a perfect program which then runs forever unchanged. "The only software that does not change is the one that stays forgotten on a shelf, without ever running."

            Slide 19 names four reasons the cycle goes on. Learn the distinctions precisely, because exam stories hinge on them:

            | Kind of change | Session 1's words | How to recognise it |
            |---|---|---|
            | **Bug** | We discover unintended behaviours | The program does something nobody meant it to do; the fix changes behaviour to what was intended |
            | **Feature** | We have to add new behaviour | Users can do something they could not do before |
            | **Refactor** | The software must connect to new components that replace old ones, or run on a different device | The inside changes; what users get stays the same |
            | **Tech debt** | We *willingly* leave something implemented in a way that is not the best possible solution, knowing we will need to improve it | A known, chosen shortcut; nothing is broken yet |

            In every case, "we start the cycle again, **back to the Design phase**".

            Two contrasts trip people up. A bug is **unintended and discovered**; tech debt is **deliberate and known in advance**. A feature **adds** behaviour; a refactor **keeps** it. Session 7 states the refactor test: "change the structure, keep the behaviour. If the output changes, it was not a refactoring." That is how to read the teacher's sample question 2: renaming variables and splitting a long function "with every test still passing unchanged" is the refactoring, while adding a `--month` option is a feature and fixing a skipped last expense is a bug fix. Its fourth option, replacing the CSV file with a JSON file, is not a refactoring either: every user's existing CSV file stops working, so what users do and see changes. Read slide 19's "new components that replace old ones" as parts inside the program that users never see, such as swapping an unmaintained library for its replacement while the report and the tests stay the same.

            The expense-tracker history shows each kind. `Add an add command that writes to data/` (`bc9ef3d`) is a feature. `Replace magic numbers with named constants` (`5e9466d`) and `Rename calculate_totals to total_by_category` (`f3bb801`) are refactors: the report they print is the same as before.
            """
        ),
        "key_points": [
            "Most software is maintained far longer than it is written.",
            "Bug: unintended, discovered. Tech debt: deliberate, known.",
            "Feature adds behaviour; refactor changes the structure and keeps the behaviour.",
            "All four send the cycle back to Design.",
        ],
        "exam_note_md": "The classic shape is four short changes and \"which one is the refactoring?\" (sample Q2). Ask of each: did the behaviour change, and was the current behaviour intended? Check every option against the output test, including options that only swap a component.",
        "source_ref": "S1 slides 18–19; S7 slide 5; expense-tracker bc9ef3d, 5e9466d, f3bb801",
        "check": [qid(13), qid(14), qid(15)],
    },
    {
        "id": sid(4),
        "heading": "The course on the lifecycle, and the card sort",
        "body_md": md(
            """
            Slide 20 maps the course's five modules onto the phases. They are "ordered by SDLC phase rather than by the problem each removes":

            | Phases | Module |
            |---|---|
            | Idea · Analysis | M1 Starting a project: Agile, Scrum |
            | Design · Development | M2 Clean code · M3 Terminal |
            | Development · Testing | M2 Testing and TDD |
            | Testing · Deployment | M4 Git, review, CI |
            | Deployment · Maintenance | M5 Docker, registries, delivery |

            Each row pairs two neighbouring phases, and M2 appears in two rows (Design to Testing): practices rarely belong to a single phase. The mid-term covers M1, M2 and M3 (sessions 1–10), so it sits on the phases from Idea to Testing.

            The session 1 **card sort** ("The coffee shop") made the same point by hand. Each group had a stakeholder brief, three constraint cards, the seven phases and fourteen decision cards, and dragged every card under "the phase where that decision actually gets made". Then two questions:

            1. Which decisions affect **more than one phase**?
            2. Which **trade-offs** only become visible once the whole board is laid out?

            The coffee-shop deck itself is not available, so here is the idea on the expense tracker. "Total the spending in each category" is decided in Analysis. "Keep reading the file, computing the totals and printing the report in separate functions" is a Design decision. "Store expenses in a CSV file that people can also edit by hand" is made once, in Design, but it reaches almost every later phase: Development (the code that reads it), Testing (the sample files the tests need), Deployment (where the file lives on someone else's machine) and Maintenance (what to do with a broken row). Because so much depends on a decision like that, it is costly to change late.

            Trade-offs appear only on the full board. Skipping automated tests makes Development look faster; the cost lands in Testing and Maintenance, columns you were not looking at when you decided. The point of laying out every phase at once is to see where a decision is paid for, not only where it is made.
            """
        ),
        "key_points": [
            "M1 Idea·Analysis; M2 Design to Testing; M3 Design·Development; M4 Testing·Deployment; M5 Deployment·Maintenance.",
            "Place a decision where it is actually made, then ask which other phases it touches.",
            "The card sort asks which decisions affect more than one phase; so much depends on them that they are costly to change late.",
        ],
        "exam_note_md": "A sort question can hand you decisions to place under phases, or ask which decision affects more than one phase. Justify by naming the phases it reaches.",
        "source_ref": "S1 slides 20, 27–28; Moodle card-sort activity",
        "check": [qid(16), qid(17), qid(18)],
    },
    {
        "id": sid(5),
        "heading": "Waterfall: five phases, five documents",
        "body_md": md(
            """
            Session 2 is "project management, not project work": how a team moves from one phase to the next, not how the code gets written. And the answer "changed completely between 1995 and 2005".

            The way it used to be done is **Waterfall**: linear, sequential phases, each one finished before the next begins. Software project management in the late 1990s looked like this:

            - Requirements fixed early; changing them is costly and discouraged.
            - Long cycles: months or years before delivery.
            - The customer involved mostly at the start and the end.
            - Heavy documentation, up front.

            Waterfall has five phases, and each produces a defined output:

            | Phase | What happens | Output |
            |---|---|---|
            | Requirements | Gather everything the system must do | A signed specification |
            | Design | Decide the structure before any code | Architecture documents |
            | Implementation | Build strictly from the design | Code |
            | Testing | Verify against the specification | A test report |
            | Deployment & maintenance | Ship it; fix what breaks | A running system |

            The key line on slide 5: **"The gate between phases is a document that gets approved."** You leave Requirements when the specification is signed, not when someone has tried a working version. The workshop brief turns this into a rule of the game: once a phase is done it is signed off, and you may not go back and change an earlier phase without a formal change request.

            Compare this with session 1's seven phases. Waterfall is not a different set of activities. It is one particular way of moving between them: once, in order, with an approved document at each gate, and with the customer seeing the result near the end.
            """
        ),
        "key_points": [
            "Waterfall: linear, sequential; each phase finished before the next begins.",
            "Outputs: signed specification, architecture documents, code, test report, running system.",
            "The gate between phases is an approved document, not working software.",
            "Going back to an earlier phase needs a formal change request.",
        ],
        "exam_note_md": "Watch for options that give Waterfall an Agile feature, such as a user trying working software between phases. In Waterfall the customer is involved mostly at the start and the end.",
        "source_ref": "S2 slides 2, 4–5; Moodle workshop brief (15 Sep)",
        "check": [qid(19), qid(20), qid(49)],
    },
    {
        "id": sid(6),
        "heading": "Where Waterfall works, and why it fails for software",
        "body_md": md(
            """
            Waterfall assumes the requirements are **known in advance and stable**. When that is true, it works. Slide 6 gives three situations:

            - **Bridges, buildings, aircraft, cars.** The requirements really are known up front, changing them mid-build really is ruinously expensive, and regulation demands the documentation.
            - **Projects where predictability matters more than speed**: you know early roughly what the finished thing looks like and what it costs.
            - **Contracts with a fixed scope and a fixed price.**

            Software breaks all three of Waterfall's assumptions:

            1. **Requirements change.** The customer sees the first version and understands what they actually wanted. "This is normal, not a failure of analysis."
            2. **Feedback arrives too late.** Testing is done near the end, so a wrong assumption made early in the project is only found close to the end.
            3. **Integration risk piles up.** Four people build four parts in isolation; they are first combined at the end, and then nothing fits.

            Session 2's slide 8 pairs each Waterfall disadvantage with Agile's answer:

            | Waterfall disadvantage | Agile's answer |
            |---|---|
            | Inflexible to change | Iterative: change is expected at any stage |
            | Problems found late | Continuous feedback finds them early |
            | Testing delayed to the end | Testing integrated into every short cycle |
            | Poor fit for evolving requirements | Built for evolving requirements |
            | Focus on the plan, not the user | Frequent user involvement drives the product |

            Keep both halves in mind. "Waterfall is always wrong" is as weak an exam answer as "Agile is always right". A good way to apply slides 6 and 7 is to ask four questions: how much is known up front, how costly change is, whether a fixed price or a regulator is involved, and how soon you need feedback from real users.

            Notice the echoes of session 1, and the difference. "Four people build four parts in isolation" sounds like "four people build four corners", but in Waterfall there *is* a shared plan, the signed specification; the parts still fail to fit because nobody combines them until the end. That is why continuous integration (XP, and this course's CI) matters even when the plan is good. And "feedback arrives too late" is what happens when testing is a phase at the end instead of "a checklist, run every time".
            """
        ),
        "key_points": [
            "Waterfall works when requirements are known and stable: bridges, predictability over speed, fixed scope and fixed price, regulation.",
            "Software breaks its assumptions: requirements change, feedback arrives too late, integration risk piles up.",
            "Changing requirements after the first version is normal, not a failure of analysis.",
        ],
        "exam_note_md": "Scenario questions ask which approach fits a project. Argue from the conditions on session 2's slide 6 and the failures on its slide 7.",
        "source_ref": "S2 slides 6–8",
        "check": [qid(8), qid(22), qid(23)],
    },
    {
        "id": sid(7),
        "heading": "Agile and the Manifesto, read correctly",
        "body_md": md(
            """
            **Agile** was formalised in **2001** by practitioners reacting to Waterfall's failures on software. It is **iterative, incremental, adaptable**: build a small working slice, show it, learn, adjust. It delivers working software frequently: weeks, not years. Each cycle goes Plan, Build, Review with user, Learn, and back to Plan.

            The phases from session 1 do not disappear. "The same lifecycle phases still happen; they just happen in every cycle, on a small slice, instead of once across the whole project." Incremental means the product grows slice by slice; iterative means you go round the same loop again and improve what is there.

            The **Agile Manifesto** states four values. "We have come to value":

            | Valued more | over | Valued less |
            |---|---|---|
            | Individuals and interactions | over | processes and tools |
            | Working software | over | comprehensive documentation |
            | Customer collaboration | over | contract negotiation |
            | Responding to change | over | following a plan |

            Then the sentence most people skip: **"While there is value in the items on the right, we value the items on the left more."** It is a ranking, not a ban. Agile teams still document, still plan and still sign contracts; when the two sides compete, the left side wins. "Agile means no documentation" and "Agile means no plan" are misreadings, and every Agile cycle starts with Plan.

            The twelve principles come in four groups:

            | Group | Principles |
            |---|---|
            | Deliver value continuously | Early and continuous delivery; deliver working software often; working software = progress |
            | Expect change; collaborate | Welcome changing requirements; business and developers, daily |
            | Trust people; sustainable pace | Motivated individuals, trusted; face-to-face conversation; a pace sustainable indefinitely; self-organising teams |
            | Keep improving | Technical excellence; simplicity: maximise work *not* done; reflect and adjust, regularly |

            Simplicity is the one people misread. The aim is to maximise the work you do **not** do: no feature nobody asked for, no detail planned for an item that will change before it is built.
            """
        ),
        "key_points": [
            "Agile (2001): iterative, incremental, adaptable; working software in weeks, not years.",
            "Plan, build, review with user, learn: the same phases, in every cycle, on a small slice.",
            "\"There is value in the items on the right\": the values are a ranking, not a ban.",
            "Four principle groups: deliver value continuously; expect change, collaborate; trust people, sustainable pace; keep improving.",
        ],
        "exam_note_md": "The usual trap is a teammate quoting the Manifesto to drop documentation or planning. Quote the closing sentence and say what the value actually ranks.",
        "source_ref": "S2 slides 10–12",
        "check": [qid(25), qid(26), qid(29)],
    },
    {
        "id": sid(8),
        "heading": "Scrum, Kanban, XP, Lean, and what the course borrows",
        "body_md": md(
            """
            Agile is a set of values and principles. Several methodologies turn it into practice, and each prescribes something different:

            | Approach | What it actually prescribes | Best when |
            |---|---|---|
            | Scrum | Fixed-length sprints; roles (Product Owner, Scrum Master, Developers); planning, daily, review, retrospective | Feature work with a team of 10 or fewer |
            | Kanban | A board of columns; a limit on work in progress; pull the next item when you have capacity | A steady stream of varied requests |
            | XP (Extreme Programming) | Engineering practices: pair programming, test-driven development, continuous integration, small releases | Code quality and change rate are both high |
            | Lean | Eliminate waste; optimise the whole flow; decide as late as responsibly possible | Cutting cycle time end to end |

            Notice what kind of thing each one prescribes. Scrum organises time and roles. Kanban organises the flow of work on a board. XP prescribes how the code itself is written and integrated: **XP is where TDD comes from**, which you meet in M2. Lean removes waste from the whole process.

            **What this course uses** (slide 14):

            - Scrum vocabulary for the project: **checkpoints are sprints**, **the Definition of Done is a green CI check**, **the Product Owner is the lecturer**.
            - XP's engineering practices as the technical spine: **TDD, CI, small commits**.
            - A **Kanban board** to track your group's work.

            Session 4 makes the Definition of Done more precise: the green CI check is on every group's list, next to checkable items such as a README.

            Slide 15 names what most teams get wrong: "It is not about picking one methodology and following blindly, but borrowing the practices that will help you iterate fast and deliver value." The course is itself the example: words from Scrum, practices from XP, a board from Kanban.

            The opposite mistake is to copy the ceremonies and skip the work. A team that holds every Scrum meeting but never tests, pushes one huge commit a week and lives with a red CI check has the vocabulary without the practices. Session 4 makes the same warning: following the Scrum ceremonies is not enough to get real work done.
            """
        ),
        "key_points": [
            "Scrum: sprints and roles. Kanban: board, WIP limit, pull. XP: engineering practices. Lean: cut waste, decide late.",
            "XP is where TDD comes from.",
            "The course: Scrum words (checkpoints = sprints, Definition of Done = green CI, PO = lecturer), XP practices (TDD, CI, small commits), a Kanban board.",
            "Borrow practices; do not follow one methodology blindly.",
        ],
        "exam_note_md": "Expect a situation (a support desk, a feature team, a codebase that changes daily) and a choice of approach. Match it to the \"best when\" column and say what that approach prescribes.",
        "source_ref": "S2 slides 13–15; S4 slide 14",
        "check": [qid(30), qid(31), qid(34)],
    },
    {
        "id": sid(9),
        "heading": "Plan, then re-plan: the workshop and the real costs of Agile",
        "body_md": md(
            """
            The session 2 workshop took one idea (a bill-splitting app, a student club website, vending machine software, a game) and planned it twice.

            **Part 1, as Waterfall.** Five phases, start to finish; for each, two or three bullets on what the group does and what document or artefact it produces. Rule of the game: once a phase is done it is signed off, and going back needs a formal change request.

            **Part 2, as Agile.** The same idea, re-planned as short iterations:

            1. What is the **smallest version a real person could actually use**? Not a prototype, but something that works, even if it does almost nothing. That is iteration one.
            2. The next two or three iterations, each a small usable improvement.
            3. Where do you show the work to a user and get feedback?
            4. What did switching cost you?

            The brief insists on question 4: "Name at least one real downside; Agile is not free." It suggests three: **less up-front certainty about the final scope**, **a fixed price is harder to quote**, and **more coordination overhead**. Then the groups compared: where did the two plans diverge first, and which would you rather be running in month six?

            They diverge at the very first step. Waterfall's first output is a signed specification of everything; Agile's first output is a small program a user can try. By month six the Agile team has had several rounds of feedback, while the Waterfall team may not yet have shown anyone working software.

            The expense tracker grew this way. Its very first commit, `Add a script that totals expenses by category` (`3e0834f`), already printed a usable report:

            ```console
            $ python tracker.py
            Expense report for expenses.csv
            ----------------------------------------
            groceries              6401.78
            utilities              3474.15
            home                   3442.26
            dining                 3345.66
            transport              2928.81
            health                 1928.13
            education              1780.66
            entertainment          1395.58
            ----------------------------------------
            TOTAL                 24697.03
            ```

            Filtering by category, the largest expense, packaging and the `add` command arrived in later commits. The backlog brief calls the category total "the first thing it ever did".
            """
        ),
        "key_points": [
            "Iteration one is the smallest version a real person could actually use, not a prototype.",
            "Every plan needs a place where a user sees the work and gives feedback.",
            "Agile is not free: less certainty about final scope, harder to quote a fixed price, more coordination.",
            "The two plans diverge at the first output: a signed specification versus a usable slice.",
        ],
        "exam_note_md": "Open questions ask you to compare the two plans for a given idea and to name one real downside of Agile. A first iteration must be usable software, and a downside must be real.",
        "source_ref": "S2 slides 16–17; Moodle activity brief (15 Sep); expense-tracker 3e0834f; backlog brief (22 Sep)",
        "check": [qid(35), qid(36), qid(37)],
    },
]

# ---------------------------------------------------------------------------------------------
# Terms
# ---------------------------------------------------------------------------------------------

TERMS: list[tuple[str, str, int]] = [
    ("Software engineering", "The systematic process of designing, developing, testing and maintaining software using scientific and engineering principles, so that it is reliable, secure, efficient and easy to maintain over time. It goes beyond writing code.", 1),
    ("Works on my machine", "Code that runs for its author and nowhere else, because something it needs exists only on that machine. Session 3 calls it \"the single problem this whole course is built to solve\".", 1),
    ("SDLC (software development lifecycle)", "The seven phases software goes through: Idea, Analysis, Design, Development, Testing, Deployment, Maintenance.", 2),
    ("Analysis", "The SDLC phase that pins down everything the software will do before the build starts, such as the expense tracker's feature table (add, list, summary by category).", 2),
    ("Deployment", "Publishing the software so that someone who is not its author can actually use it.", 2),
    ("Maintenance", "Fixing bugs, improving what is slow or ugly and keeping the software running, \"forever\". Most software is maintained far longer than it is written.", 3),
    ("Bug", "Unintended behaviour that is discovered in the software. Fixing it changes the behaviour to what was intended.", 3),
    ("Feature", "New behaviour added on purpose: users can do something they could not do before.", 3),
    ("Refactor", "A change to the inside of the software (for example to connect to a new component that replaces an old one) that keeps its behaviour. \"If the output changes, it was not a refactoring.\"", 3),
    ("Tech debt", "A part willingly left implemented in a way that is not the best possible solution, knowing it will need improving later.", 3),
    ("Waterfall", "A linear, sequential way to run a project: each phase finished before the next begins, requirements fixed early, long cycles, heavy documentation up front, and an approved document as the gate between phases.", 5),
    ("Integration risk", "The risk that parts built in isolation do not fit when they are first combined. In Waterfall it piles up until the end.", 6),
    ("Agile", "A way of organising software work, formalised in 2001: iterative, incremental and adaptable, delivering working software in weeks, not years.", 7),
    ("Agile Manifesto", "Four values that rank individuals and interactions, working software, customer collaboration and responding to change above processes and tools, comprehensive documentation, contract negotiation and following a plan, while still valuing the latter.", 7),
    ("Scrum", "An Agile methodology with fixed-length sprints, three roles (Product Owner, Scrum Master, Developers) and planning, daily, review and retrospective. Best for feature work with a team of 10 or fewer.", 8),
    ("Kanban", "An Agile methodology built on a board of columns, a limit on work in progress, and pulling the next item when there is capacity. Best for a steady stream of varied requests.", 8),
    ("XP (Extreme Programming)", "An Agile methodology that prescribes engineering practices: pair programming, test-driven development, continuous integration, small releases. XP is where TDD comes from.", 8),
    ("Lean", "An approach that eliminates waste, optimises the whole flow and decides as late as responsibly possible. Best for cutting cycle time end to end.", 8),
    ("Definition of Done", "The checkable bar every item must meet before it counts as done. The slides map it to \"a green CI check\", the same for every group; each group writes its own list, which must include that check. CP1's listed three checks: `uv sync && uv run <app> --help` works from a clean clone, the `src/` layout, and a README.", 8),
    ("Smallest usable version", "The first Agile iteration in the workshop: something a real person can actually use, even if it does almost nothing. Not a prototype.", 9),
]

# ---------------------------------------------------------------------------------------------
# Traps
# ---------------------------------------------------------------------------------------------

TRAPS: list[str] = [
    "**\"Agile means no documentation.\"** The Manifesto ranks working software above comprehensive documentation and adds \"while there is value in the items on the right\". Agile teams keep the documentation that helps; your CP1 needs a README.",
    "**\"Agile means no plan.\"** Every Agile cycle starts with Plan. \"Responding to change over following a plan\" means changing the plan when you learn something, not having none.",
    "**\"Agile skips phases.\"** The same lifecycle phases happen in every cycle, on a small slice, instead of once across the whole project.",
    "**\"Waterfall is always wrong.\"** It genuinely works when requirements are known and stable: bridges and aircraft, fixed-scope and fixed-price contracts, regulation that demands documentation.",
    "**\"If the requirements changed, the analysis failed.\"** The customer sees the first version and understands what they actually wanted: \"This is normal, not a failure of analysis.\"",
    "**\"Tech debt is another word for bugs.\"** A bug is unintended and discovered; tech debt is a shortcut taken willingly, knowing it must be improved later.",
    "**\"Any change to the code is a refactor.\"** A refactor changes the structure and keeps the behaviour. A new option is a feature; correcting wrong output is a bug fix.",
    "**\"Testing is a phase you do once, at the end.\"** Session 1: \"a checklist, run every time, not once\". In this course the CI check runs on every push.",
    "**\"It runs on my laptop, so it is deployed.\"** Deployment means someone who is not its author can actually use it; \"works on my machine\" is the failure, not the goal.",
    "**\"Holding the Scrum meetings makes us Agile.\"** Slide 15: borrow the practices that help you iterate fast and deliver value. Without tests, CI and small commits, the ceremonies change nothing.",
]

# ---------------------------------------------------------------------------------------------
# Flashcards
# ---------------------------------------------------------------------------------------------

CARDS: list[tuple[str, str, str, int]] = [
    ("What is software engineering, in the course's definition?", "The systematic process of designing, developing, testing and maintaining software using scientific and engineering principles. It goes beyond writing code: it keeps programs reliable, secure, efficient and easy to maintain over time.", "concept", 1),
    ("Why is this \"not a Python course\"?", "Syntax is assumed. The course is about what happens to a little program once three teammates get involved and it must run reliably, be easy to change and be trustworthy.", "concept", 1),
    ("Session 1, slide 8: what answers \"no shared plan, four people build four corners\"?", "Agile, Scrum.", "recall", 1),
    ("Session 1, slide 8: what answers \"unreadable, breaks silently\"?", "Clean code, testing, TDD.", "recall", 1),
    ("Session 1, slide 8: what answers \"a code change breaks the build\"?", "Version control, code reviews, CI.", "recall", 1),
    ("Session 1, slide 8: what answers \"works on my machine\"?", "Containerisation, automatic deployment. In the course so far, uv installs the same versions for everyone.", "recall", 1),
    ("The seven SDLC phases, in order?", "Idea, Analysis, Design, Development, Testing, Deployment, Maintenance.", "recall", 2),
    ("Idea vs Analysis?", "Idea discovers the mission: who will use it, what problem it solves. Analysis pins down everything it will do before the build starts (the feature table: add, list, summary by category).", "distinction", 2),
    ("What does \"development arrives comparatively late\" mean?", "Three phases (Idea, Analysis, Design) happen before anyone types code: there is a lot of thinking about the code before writing it.", "concept", 2),
    ("\"A checklist, run every time, not once\": which phase, and why every time?", "Testing. A check run once tells you about one moment; repeated after every change, it tells you whether the last change broke something. In the course: CI on every push.", "concept", 2),
    ("When is software deployed?", "When someone who is not its author can actually use it.", "concept", 2),
    ("Why does maintenance last \"forever\"?", "Software is living: bugs, features, refactors and tech debt keep sending it back to Design. Most software is maintained far longer than it is written.", "concept", 3),
    ("Bug vs tech debt?", "A bug is unintended behaviour that is discovered. Tech debt is a shortcut left in place willingly, knowing it will need improving.", "distinction", 3),
    ("Feature vs refactor?", "A feature adds behaviour users can see. A refactor changes the structure and keeps the behaviour: if the output changes, it was not a refactoring.", "distinction", 3),
    ("Where does the cycle start again after a bug, a feature, a refactor or tech debt?", "Back at the Design phase.", "recall", 3),
    ("Slide 20: which module covers Idea and Analysis?", "M1 Starting a project: Agile, Scrum.", "recall", 4),
    ("Card sort, question 1: which decisions does it ask you to find, and why do they matter?", "Those that affect more than one phase, such as storing expenses in a hand-editable CSV file (it reaches Development, Testing, Deployment and Maintenance). Because so much depends on them, they are costly to change late.", "concept", 4),
    ("Waterfall's five phases and their outputs?", "Requirements: a signed specification. Design: architecture documents. Implementation: code. Testing: a test report. Deployment and maintenance: a running system.", "recall", 5),
    ("What is the gate between Waterfall phases?", "A document that gets approved. Going back to an earlier phase needs a formal change request.", "concept", 5),
    ("Where does Waterfall genuinely work?", "When requirements are known and stable: bridges, buildings, aircraft, cars; when predictability matters more than speed; fixed-scope, fixed-price contracts; when regulation demands documentation.", "concept", 6),
    ("Three reasons Waterfall fails for software?", "Requirements change (normal, not a failure of analysis); feedback arrives too late; integration risk piles up.", "recall", 6),
    ("How do you read \"working software over comprehensive documentation\"?", "\"While there is value in the items on the right, we value the items on the left more.\" A ranking, not a ban.", "reading", 7),
    ("The four groups of the twelve Agile principles?", "Deliver value continuously; expect change, collaborate; trust people, sustainable pace; keep improving.", "recall", 7),
    ("Scrum vs Kanban: best when?", "Scrum: feature work with a team of 10 or fewer, in fixed-length sprints. Kanban: a steady stream of varied requests, pulled from a board with a work-in-progress limit.", "distinction", 8),
    ("Where does TDD come from?", "XP (Extreme Programming), along with pair programming, continuous integration and small releases.", "recall", 8),
    ("What does the course take from Scrum, XP and Kanban?", "Scrum vocabulary (checkpoints are sprints, the Definition of Done is a green CI check, the Product Owner is the lecturer), XP's practices (TDD, CI, small commits) and a Kanban board.", "recall", 8),
    ("What is the first iteration in the Agile re-plan?", "The smallest version a real person could actually use: not a prototype, something that works even if it does almost nothing.", "concept", 9),
    ("Three real costs of switching to Agile, from the workshop brief?", "Less up-front certainty about the final scope; a fixed price is harder to quote; more coordination overhead.", "recall", 9),
    ("The Agile Manifesto's four values: what is valued more, over what?", "Individuals and interactions over processes and tools; working software over comprehensive documentation; customer collaboration over contract negotiation; responding to change over following a plan. \"While there is value in the items on the right, we value the items on the left more.\"", "recall", 7),
    ("What is Agile's cycle, and what happens to the seven SDLC phases inside it?", "Plan, build, review with user, learn, then plan again. The same lifecycle phases still happen in every cycle, on a small slice, instead of once across the whole project.", "concept", 7),
]

# ---------------------------------------------------------------------------------------------
# Real artefacts (runs kept in the scratch work folder; paths rewritten to the student's view)
# ---------------------------------------------------------------------------------------------

Q06_RUN = """
```console
$ uv run expenses report
Traceback (most recent call last):
  File "/home/marta/expense-tracker/.venv/bin/expenses", line 4, in <module>
    from expense_tracker.cli import app
  File "/home/marta/expense-tracker/src/expense_tracker/cli.py", line 6, in <module>
    from tabulate import tabulate
ModuleNotFoundError: No module named 'tabulate'
```
"""

Q07_DIFF = """
```diff
-@dataclass(frozen=True)
+@dataclass
 class Expense:
     date: str
     merchant: str
```
"""

Q07_RUN = """
```console
$ uv run pytest -q
FAILED tests/test_duplicates.py::test_expenses_without_duplicates_are_unchanged - TypeError: unhashable type: 'Expense'
FAILED tests/test_duplicates.py::test_an_exact_duplicate_is_removed_and_the_first_one_kept - TypeError: unhashable type: 'Expense'
FAILED tests/test_duplicates.py::test_same_merchant_on_another_day_is_not_a_duplicate - TypeError: unhashable type: 'Expense'
FAILED tests/test_duplicates.py::test_many_copies_of_one_expense_collapse_to_one - TypeError: unhashable type: 'Expense'
4 failed, 20 passed in 0.05s
```
"""

Q38_RUN = """
```console
$ git log --oneline --reverse v0.1
3e0834f Add a script that totals expenses by category
6efdf9d Filter by category and ignore small amounts
c746d38 (tag: v0.0) Print the largest expense
a953d05 Turn the script into a uv package
2ecad20 Move the report into the package behind a typer CLI
bc9ef3d Add an add command that writes to data/
89afbe1 (tag: v0.1) Add a README and the MIT licence
```
"""

ARTEFACTS.update({
    "@@Q06_RUN@@": Q06_RUN,
    "@@Q07_DIFF@@": Q07_DIFF,
    "@@Q07_RUN@@": Q07_RUN,
    "@@Q38_RUN@@": Q38_RUN,
})

# ---------------------------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------------------------

Q: list[dict[str, Any]] = []

# ---- s1: software engineering, failure modes -------------------------------------------------

Q.append(mcq(
    1, "core", ["concept"], 1, "S1 slide 5",
    """
    A classmate says: "Software engineering is just a fancier name for programming." Which statement matches the course's definition and shows why the classmate is wrong?
    """,
    [
        opt("Choosing the best programming language and framework for each new project the team starts",
            "That is one decision inside Design. The definition is about a process that runs across the whole life of the software, not a choice of language."),
        opt("Writing code quickly enough to meet the client's deadline, with as few bugs as possible",
            "Speed is not in the definition. It is about software that stays reliable and easy to maintain over time, long after the deadline."),
        opt("A systematic process of designing, developing, testing and maintaining software that stays reliable over time",
            "This is slide 5's definition: programming (developing) is only one part of a structured approach that also covers design, testing and maintenance.", True),
        opt("Managing a team's budget, deadlines and meetings so that every software project finishes on time and on budget",
            "That is project management, the subject of session 2. Software engineering includes the technical work of design, testing and maintenance."),
    ],
    """
    Slide 5 defines software engineering as "the systematic process of designing, developing, testing, and maintaining computer software using scientific and engineering principles", and adds that it "goes beyond just writing code". The aim is software that is reliable, secure, efficient and easy to maintain over time. Programming is one activity inside that process (Development). Picking a language and meeting a deadline are decisions within it, and budgets and meetings belong to project management, which session 2 separates from "project work".
    """,
))

Q.append(mcq(
    2, "core", ["concept"], 1, "S1 slide 10",
    """
    Session 1 insists that this is "not a Python course". Which statement best describes what the course is about instead?
    """,
    [
        opt("What happens to your code once teammates get involved and it must run reliably and be easy to change",
            "This is the goal on slide 10, almost word for word: the code you can already write, once three teammates get involved.", True),
        opt("Learning Python syntax properly, from loops and functions up to classes, decorators and the standard library",
            "Syntax is assumed: the prerequisites are loops, functions, types and a completed Python course. New constructs arrive \"as design tools, not language tourism\"."),
        opt("Building web and mobile front ends with graphical interfaces that business users can click through",
            "The project is a terminal program with no web or graphical interface; the brief says removing the interface leaves the parts the course is actually about."),
        opt("Choosing the best web framework for a business application and learning it in depth",
            "The course teaches no framework: the project is a terminal program, and the tools serve teamwork on code, not the choice of technology."),
    ],
    """
    Slide 10 sets the prerequisites (loops, functions, types, a completed course of basic Python) and states that "syntax is assumed". The goal: "what happens to that little program you wrote once three teammates get involved and it is supposed to run reliably, be easy to change, and trustworthy". The syllabus says the same: the course "is concerned with what happens to code once other people work on it". Every tool that follows (uv, ruff, mypy, pytest, git, Docker) serves that goal, not the learning of more Python.
    """,
))

Q.append(mcq(
    3, "exam", ["concept", "judgement"], 1, "S1 slides 6–8",
    """
    Laia wrote her group's CSV loader in February. In August she opens it to add a currency column and loses an afternoon working out what `d`, `r` and `x` hold, and why one line multiplies by `0.79`. Nothing is broken; she just cannot follow it. Which failure from session 1 is this, with the answer slide 8 gives for it?
    """,
    [
        opt("No shared plan, four people build four corners; Agile and Scrum",
            "The problem is not what the group agreed to build. Laia cannot read code that already exists."),
        opt("\"Works on my machine\", and nowhere else; containerisation and automatic deployment",
            "Nothing suggests the code runs on one machine only. Laia's difficulty is understanding it."),
        opt("A teammate's code change breaks the build; version control, code reviews and CI",
            "Nobody else changed anything, and the story says nothing is broken."),
        opt("Six months on, nobody can read it, not even its author; clean code, testing, TDD",
            "Cryptic names and an unexplained number are exactly what makes code unreadable months later, even to the person who wrote it.", True),
    ],
    """
    Slide 6's third failure is "six months on, nobody can read it, not even its author", illustrated on slide 7 by the comment admitting that only god now knows how a routine works. Slide 8 groups it with breaking silently: "unreadable, breaks silently → clean code, testing, TDD". In session 6 terms, `d`, `r` and `x` need real names and `0.79` needs a named constant that says what it is. The other options are real failures, but each needs a different story: a disagreement about what to build, a program that runs only on one laptop, or a shared build that a teammate broke.
    """,
))

Q.append(mcq(
    4, "exam", ["concept", "judgement"], 1, "S1 slides 6–8",
    """
    On Thursday night Pau pushes his change straight to the group's `main` branch. On Friday morning the other three pull, and the project no longer passes its checks for anyone, Pau included. Nobody read his change before it landed and nothing ran automatically when he pushed. Which pair from session 1 fits this story?
    """,
    [
        opt("Six months on, nobody can read it, not even its author; clean code, testing, TDD",
            "Nobody is struggling to read old code here. The problem is how a change got into the shared project unchecked."),
        opt("A teammate's code change breaks the build; version control, code reviews, CI",
            "One person's change landed in the shared code with no review and no automatic check, and broke it for everyone.", True),
        opt("\"Works on my machine\", and nowhere else; containerisation, automatic deployment",
            "It fails for everyone, Pau included, so this is not a program that runs on one laptop only."),
        opt("No shared plan, four people build four corners; Agile and Scrum",
            "The group may agree perfectly on what to build. What failed is the path a change takes into the shared code."),
    ],
    """
    Slide 6 lists "a teammate's code change breaks the build" and slide 8 answers it with "version control, code reviews, CI". The story contains the two missing safeguards: nobody reviewed the change, and no automatic check ran on the push. In this course the CI check (ruff, mypy, pytest) runs on every push precisely so that a broken change is visible before the others build on it. Because the project fails for everyone, including the author, "works on my machine" does not fit.
    """,
))

Q.append(mcq(
    5, "exam", ["concept", "judgement"], 1, "S1 slides 6–8",
    """
    Four friends start the Habit tracker project. Nobody writes down what the program should do first. Two weeks later one has built a streak calendar, one a statistics report, one a login system and one an export to Excel. Each part runs, but nobody can record a habit yet. Which failure is this, and what does session 1 put against it?
    """,
    [
        opt("No shared plan, four people build four corners; Agile and Scrum",
            "Nobody agreed what to build or in what order, so four people built four parts that do not add up to a product.", True),
        opt("A teammate's code change breaks the build; version control, code reviews and CI",
            "Nothing is broken: each part runs. The problem is which parts were chosen."),
        opt("Change one thing, three others break, silently; clean code, testing and TDD",
            "No change is breaking other parts. The parts are simply the wrong ones."),
        opt("Works on my machine; containerisation and automatic deployment",
            "Nobody reports a part that runs only on its author's laptop."),
    ],
    """
    Slide 6's last failure, "no shared plan, four people build four corners", is answered on slide 8 by "Agile, Scrum". Each member made a reasonable part, but without an agreed, ordered plan nobody built the one thing a user needs first: recording a habit. In this course the shared plan is an ordered Product Backlog with the most valuable usable item on top (session 4), and the workshop's first Agile question is "what is the smallest version a real person could actually use?".
    """,
))

Q.append(mcq(
    6, "exam", ["read-tool-output", "judgement"], 1, "S1 slides 6, 8; S3 slides 3, 5; S4 slide 24",
    """
    Last week Jordi made the report print as a neat table. On his laptop `uv run expenses report` works. Marta clones the repository, `uv sync` finishes without errors, and then:

    @@Q06_RUN@@

    Jordi replies: "It works on my laptop, so the problem is on your side." What can you conclude?
    """,
    [
        opt("Jordi is right: the code is fine, so Marta should install `tabulate` by hand on her laptop and carry on",
            "That makes it work on two laptops instead of one. CI and every other teammate still fail, because the project itself does not say it needs `tabulate`."),
        opt("It is \"works on my machine\": the code needs a package Jordi has but the project never declares",
            "`uv sync` installed everything the project declares and `tabulate` is still missing, so the dependency exists only on Jordi's machine.", True),
        opt("The lockfile is damaged: delete `uv.lock` and `.venv`, then run `uv sync` again to rebuild everything",
            "`uv sync` succeeded, so the lockfile was read correctly. Deleting it changes nothing, because `tabulate` is not in it."),
        opt("Marta's Python is too new for this project, so she needs to install an older version of Python first",
            "The last line reports a missing module, not a Python version problem; uv already chose the version the project asks for."),
    ],
    """
    Read the last line first: the module `tabulate` is missing on Marta's machine. `uv sync` installs exactly what `pyproject.toml` and `uv.lock` declare, and it finished cleanly, so the repository Marta cloned never declares `tabulate`. On Jordi's laptop it is installed, either by hand or through a change to `pyproject.toml` and `uv.lock` that he never committed; either way it runs only there. That is the first failure on slide 6, "works on my machine, and nowhere else", which session 3 calls "the single problem this whole course is built to solve". The fix belongs in the project (declare the dependency, for example with `uv add`, and commit the lockfile) so that everyone, CI included, gets the same versions. Slide 8's longer-term answer is containerisation and automatic deployment.
    """,
    verified="run",
))

Q.append(mcq(
    7, "hard", ["read-tool-output", "read-diff", "judgement"], 1, "S1 slides 6, 8; S8 (dict.fromkeys, frozen)",
    """
    You remove `frozen=True` from `Expense` so that a typo in an amount can be corrected in place:

    @@Q07_DIFF@@

    `uv run expenses report` still prints the report and exits with 0. You have not pushed, and nobody else has changed anything. Then you run the tests (output trimmed to the summary):

    @@Q07_RUN@@

    In session 1's terms, what did the test suite just do?
    """,
    [
        opt("It caught a \"works on my machine\" problem: the tests fail only because of something in your local setup",
            "The failures follow directly from your edit; nothing about the machine changed, and CI would fail in exactly the same way."),
        opt("It caught a teammate's change breaking the build: someone else broke `remove_duplicates`",
            "Nobody else changed anything and nothing has reached the shared project. The change is yours."),
        opt("It made \"change one thing, others break, silently\" visible: your edit broke a function you never touched",
            "One edit in `Expense` broke four tests of a different function, while the program itself still looked fine.", True),
        opt("It found a bug in `remove_duplicates`: all four failures are its tests, so fix that function",
            "`remove_duplicates` did not change, and its tests passed before your edit. The failures show where the break surfaces; your change to `Expense` is where it was made."),
    ],
    """
    You changed one line in `Expense`. Four tests in `tests/test_duplicates.py`, a file you never opened, now fail, and the report still runs and exits with 0. Without the tests nothing would have looked wrong until someone called `remove_duplicates`: the textbook case of "change one thing, three others break, silently". Slide 8's answer is "clean code, testing, TDD", and here testing turned a silent break into a red line. The cause is session 8's: `dict.fromkeys` needs hashable items, and `frozen=True` is what made `Expense` hashable. Changing `remove_duplicates` to make the red lines go away would treat the symptom. No teammate or machine is involved, so the other failure modes do not fit.
    """,
    verified="run",
))

# ---- s2: the seven phases -----------------------------------------------------------------------

Q.append(mcq(
    9, "exam", ["concept"], 2, "S1 slides 16–17",
    """
    Before writing any code for the expense tracker, the team writes this table and agrees that it is complete:

    | Feature | What it does |
    |---|---|
    | Add an expense | Record its amount, category and date |
    | List expenses | Show everything recorded |
    | Summary by category | Total the spending in each category |

    In which SDLC phase does this table belong?
    """,
    [
        opt("Idea, because it says what the app should do and who it is for",
            "Idea asks the broad questions, including \"what should it do?\". A complete, agreed list of features with what each one does is Analysis (slide 16 shows this very table there), and nothing in it says who the app is for."),
        opt("Design, because it decides how the app will be built and structured",
            "The table says what each feature does, not how the pieces connect or how a user moves through it; that structure is Design."),
        opt("Testing, because every row of it can be checked against the finished app",
            "Testing uses this table (\"verify it does what the analysis said\") but does not produce it."),
        opt("Analysis, because it pins down all the app will do before the build",
            "Slide 16 shows this very table under Analysis: \"everything it will do, pinned down before the build starts\".", True),
    ],
    """
    Slide 16 puts the feature table under Analysis, with the line "Everything it will do, pinned down before the build starts." Idea asks the broad questions (who will use it, what problem does it solve, what should it do); Analysis turns the answers into a complete list of features with what each one does. Design then decides the structure that delivers them, and Testing later checks the program against this table. A useful habit: Analysis is about *what*, Design is about *how the pieces connect*.
    """,
))

Q.append(mcq(
    10, "exam", ["concept", "judgement"], 2, "S1 slide 17; S3 slide 3",
    """
    A group tests their Gradebook by hand the night before CP1: they try ten inputs, all work, and they tick "tested" on their plan. Over the next three weeks they make forty commits and never repeat the check. What is wrong with this, in session 1's terms?
    """,
    [
        opt("Testing is a checklist run every time, not once; it says nothing about the forty commits since",
            "Session 1's exact point: one run tells you about one moment, and every later change can break what was checked.", True),
        opt("Ten inputs are too few; testing is only finished when every possible input has been tried at least once",
            "No checklist covers every input. The flaw is not the size of the check but that it was run once and never again."),
        opt("Testing belongs after Deployment, so it should wait until the final submission",
            "Testing comes before Deployment in the lifecycle, and Agile integrates it into every short cycle rather than pushing it to the end."),
        opt("Testing by hand is acceptable only when the person who wrote the code does it",
            "Who runs the check does not fix the problem: a check that is never repeated cannot catch what the next commit breaks."),
    ],
    """
    Slide 17 defines Testing as "verify it does what the analysis said. A checklist, run every time, not once." A one-off check proves only that the program worked on that night. After forty commits, any of which could have broken something, the tick on the plan means nothing. This is why the course automates the checklist: the CI check runs ruff, mypy and pytest on every push, the referee that runs whether or not anyone remembers. The repeated check is also how "change one thing, three others break, silently" stops being silent.
    """,
))

Q.append(mcq(
    47, "core", ["concept", "judgement"], 2, "S1 slides 16–17; S2 slide 10",
    """
    One week after topics are settled, group A has 300 lines of code and no agreed list of what the program should do. Group B has a feature table and a sketch of how the pieces connect, and no code yet. A member of group A says group B is "behind". In session 1's terms, which comment is right?
    """,
    [
        opt("Group A is ahead: Development produces the program, so starting it early saves time",
            "Session 1 says development arrives comparatively late. Code written before anyone agreed what it should do risks being thrown away, or becoming four corners."),
        opt("Group A is ahead, provided it writes the feature table afterwards to describe its code",
            "Analysis pins down what the app will do before the build starts. A table written afterwards describes the code; it cannot guide it."),
        opt("Neither is ahead: an Agile team starts by coding and works out the plan as it goes",
            "Every Agile cycle starts with Plan, and the same phases happen in each cycle on a small slice. Agile repeats the phases and keeps their order."),
        opt("Group B is on track: three phases come before code, and development arrives late",
            "Slide 17: \"Development arrives comparatively late. Three phases happen before anyone types code.\" Group B has outputs from Analysis and Design.", True),
    ],
    """
    Slide 17: "Development arrives comparatively late. Three phases happen before anyone types code. Notice how there is a lot of thinking about the code prior to writing the code itself." Group B has an Analysis output (the feature table, as on slide 16) and a Design output (how the pieces connect), so its code will be built from something agreed. Group A skipped both, which is how "no shared plan, four people build four corners" begins. Agile does not change this: each short cycle still plans, analyses and designs a small slice before building it.
    """,
))

Q.append(sort_q(
    11, "core", ["concept"], 2, "S1 slides 15–18, 28",
    """
    Card sort on the expense tracker: place each decision under the phase where it actually gets made.
    """,
    [("idea", "Idea"), ("analysis", "Analysis"), ("design", "Design"), ("testing", "Testing"), ("deployment", "Deployment")],
    [
        ("Decide that the app is for people who want to see where their money goes each month", "idea",
         "Who will use it and what problem it solves: the mission, discovered in Idea."),
        ("Agree on the problem it solves: nobody in the flat knows where the shared money goes", "idea",
         "What problem does it solve? The mission comes first, before any feature is pinned down."),
        ("\"Summary by category\" totals the spending in each category", "analysis",
         "A row of the feature table: what the app will do, pinned down before the build."),
        ("Adding an expense records its amount, category and date", "analysis",
         "Another row of the analysis table; it says what a feature does, not how it is built."),
        ("Reading the file, computing the totals and printing the report are separate functions", "design",
         "How the pieces connect is the structure, which Design decides."),
        ("Sketch how a user moves through the program: which command they type and what the screen shows next", "design",
         "Slide 17: Design covers how someone moves through it and how the software behaves."),
        ("Turn the feature table into a checklist to verify the finished program against: each feature does what the table says", "testing",
         "Verifying the program against what the analysis said is Testing."),
        ("Run the same checklist again after every change, not only before release", "testing",
         "\"A checklist, run every time, not once.\""),
        ("Publish it so a classmate who is not its author can install and run it", "deployment",
         "Deployment means someone who is not the author can actually use it."),
        ("Write install steps in the README so a stranger can run it without help", "deployment",
         "Making it usable by someone other than its author is the point of Deployment."),
    ],
    """
    Idea finds the mission (who, what problem). Analysis pins down everything it will do, feature by feature. Design decides the structure: how pieces connect and how a user moves through it. Testing verifies the program against the analysis, every time. Deployment makes it usable by someone who is not its author. When a card seems to fit two columns, ask where the decision is actually *made*; the card-sort follow-up then asks which other phases it affects.
    """,
    verified="reasoning",
))

# ---- s3: living software, kinds of change ----------------------------------------------------------

Q.append(mcq(
    12, "core", ["concept", "judgement"], 3, "S1 slide 18",
    """
    A start-up plans its expense app: four months of building, the launch, and then the app's budget drops to zero because "it will be finished". Which idea from session 1 most directly challenges this plan?
    """,
    [
        opt("Development arrives comparatively late, so four months of building before launch is too long",
            "That point is about the phases before code. It says nothing about what happens after launch, which is where this plan goes wrong."),
        opt("Deployment means someone who is not its author can use it, so the launch will fail",
            "Nothing suggests the launch fails. The flaw is assuming nothing comes after it."),
        opt("Maintenance goes on forever: most software is maintained far longer than it is written",
            "The plan ends the lifecycle at launch, but bugs, features, refactors and tech debt keep arriving afterwards.", True),
        opt("The methodology lies in how a team moves from one phase to the next",
            "True, but it is about transitions between phases; the plan's flaw is dropping the last phase altogether."),
    ],
    """
    Slide 18: Maintenance is "fix bugs. Improve what is slow or ugly, keep it running. Forever." and "Most software is maintained far longer than it is written." The course treats software as living: "the lifecycle is not a finite set of steps that lead to a perfect program that will run forever without being changed". After launch, bugs are discovered, features are requested, components are replaced and tech debt comes due, and each one sends the cycle back to Design. A budget that stops at launch plans for software that "stays forgotten on a shelf, without ever running".
    """,
))

Q.append(mcq(
    13, "exam", ["concept", "judgement"], 3, "S1 slide 19",
    """
    Two days before CP1, the team hard-codes the file name `expenses.csv` instead of letting the user choose a file. They add a backlog item: "Let the user choose the file; the hard-coded name will get in the way when we add a second data file." In session 1's terms, the hard-coded name is:
    """,
    [
        opt("Tech debt: a known, deliberate shortcut that will need improving later",
            "They chose it willingly and wrote down that it must be improved: slide 19's definition of tech debt.", True),
        opt("A bug: the program does something that nobody on the team intended it to do",
            "The program does exactly what the team decided. Nothing unintended has been discovered."),
        opt("A refactor: the structure changed while the behaviour stayed the same",
            "Nothing was restructured; this is a choice about how to build it now, not a reshaping of existing code."),
        opt("A feature: it adds new behaviour that users of the program can see and use",
            "Reading one fixed file gives users nothing new; it is a limitation accepted to save time."),
    ],
    """
    Slide 19: "Sometimes we will willingly leave things implemented in a way which is not the best possible solution, knowing that at some point we will need to make an improvement (tech debt)." Both conditions are in the story: the shortcut is deliberate (to hit CP1) and known (the backlog item). That separates it from a bug, which is unintended and discovered later. When the team later allows users to choose the file, that change will add behaviour (a feature) and pay the debt back, and like every such change it starts again at Design.
    """,
))

Q.append(mcq(
    14, "exam", ["concept", "judgement"], 3, "S1 slide 19; S7 slide 5; sample Q2",
    """
    The library your loader uses to read files is no longer maintained, so you switch to its replacement. Users run the same commands on the same files and see exactly the same report, and every test passes unchanged. In session 1's terms, which kind of change is this?
    """,
    [
        opt("A feature, because the code now depends on a new library it did not use before",
            "A feature is new behaviour for users. Users can do nothing they could not do before."),
        opt("A bug fix, because the old library might have failed one day and broken the report",
            "No unintended behaviour was discovered: nothing was failing."),
        opt("Tech debt, because working code was changed even though nobody had asked for it",
            "Tech debt is a shortcut left in place on purpose. This change removes a risk; it does not create a shortcut."),
        opt("A refactor: an old component is replaced inside, and the behaviour stays the same",
            "Slide 19 names exactly this case, and the unchanged tests show the behaviour stayed the same.", True),
    ],
    """
    Slide 19 describes refactoring as making sure "the software can connect to new components that replace old components, or run on a different device". Session 7 gives the test: "change the structure, keep the behaviour. If the output changes, it was not a refactoring." Both hold here: a new component inside, the same report outside, and every test passing unchanged, which is also what marks the refactoring in the teacher's sample question 2. Using a new library is invisible to users, so it is not a feature, and nothing unintended was found, so it is not a bug fix.
    """,
))

Q.append(sort_q(
    15, "exam", ["concept", "judgement"], 3, "S1 slide 19; S7 slide 5; expense-tracker 6efdf9d, 2ecad20, bc9ef3d, 5e9466d, f3bb801",
    """
    Sort each change into the kind of change session 1 describes. The changes with a commit hash in their explanation are real commits from the expense-tracker history; the others are practice examples.
    """,
    [("bug", "Bug"), ("feature", "Feature"), ("refactor", "Refactor"), ("debt", "Tech debt")],
    [
        ("On a teammate's branch, `report --min 20` leaves out an expense of exactly 20.00, although the help text says it ignores amounts *below* the minimum", "bug",
         "Unintended behaviour: the program does not do what it says it does."),
        ("The report crashes on an empty file instead of printing a total of 0.00", "bug",
         "Nobody meant it to crash; the behaviour is discovered, not chosen."),
        ("Users can now ask for one category only, such as `dining`, and leave out small amounts", "feature",
         "New behaviour users could not get before (commit `6efdf9d`; the category and the minimum were plain command-line arguments until `2ecad20` made them `--category` and `--min`)."),
        ("A new `add` command writes an expense to `data/expenses.csv`", "feature",
         "Users can do something new: record an expense from the command line (commit `bc9ef3d`)."),
        ("`calculate_totals` is renamed `total_by_category` and `d`, `e`, `r` get real names; the report prints exactly as before", "refactor",
         "The structure changed and the behaviour stayed the same (commit `f3bb801`). There were no tests yet, so the evidence is an identical report."),
        ("Bare numbers such as `40` and `row[3]` become named constants such as `RULE_WIDTH` and `AMOUNT`; the report prints exactly as before", "refactor",
         "Session 7's extract-constant move: new names, same output (commit `5e9466d`)."),
        ("To finish CP1, the team keeps every command in one file, `cli.py`, and adds a backlog item to split it once it passes 300 lines", "debt",
         "Not the best structure, chosen on purpose and written down for later: tech debt. Nothing is broken yet."),
        ("The team knowingly loads every expense into memory, aware it will be slow for huge files, and notes it for later", "debt",
         "Not the best possible solution, chosen on purpose and recorded for later improvement."),
    ],
    """
    Two questions sort any change. Did the behaviour change? If not, it is a refactor. If it did, was the old behaviour intended? Unintended and discovered means a bug; deliberately new means a feature. Tech debt is different in kind: it is the decision to leave something below the best solution, knowing it will need improving. All four send the cycle back to Design.
    """,
    origin="history",
))

# ---- s4: modules and the card sort -------------------------------------------------------------

Q.append(mcq(
    16, "core", ["concept"], 4, "S1 slides 8, 20",
    """
    Your group cannot agree on what the program should do first or how to split the work. According to slide 20, which module of the course covers the phases where this gets settled?
    """,
    [
        opt("M2 Clean code, which sits on Design and Development",
            "M2 is about how code is written once you know what to build."),
        opt("M4 Git, review and CI, which sits on Testing and Deployment",
            "M4 protects shared code once it exists; it does not decide what to build first."),
        opt("M1 Starting a project: Agile and Scrum, which sits on Idea and Analysis",
            "Deciding what to build and in what order is Idea and Analysis work, and M1 covers it.", True),
        opt("M5 Docker, registries and delivery, which sits on Deployment and Maintenance",
            "M5 is about running the finished program elsewhere and keeping it delivered."),
    ],
    """
    Slide 20 orders the modules "by SDLC phase rather than by the problem each removes": Idea and Analysis go with M1 Starting a project (Agile, Scrum); Design and Development with M2 Clean code and M3 Terminal; Development and Testing with M2 Testing and TDD; Testing and Deployment with M4 Git, review, CI; Deployment and Maintenance with M5 Docker. Slide 8 gives the same answer from the problem side: "no shared plan → Agile, Scrum".
    """,
))

Q.append(mcq(
    17, "exam", ["concept", "judgement"], 4, "S1 slide 28",
    """
    In a card sort for the expense tracker, a group places the card "Store expenses in a CSV file that people can also edit by hand" under Design. Which comment about this card is best?
    """,
    [
        opt("Move it to Analysis: how the expenses are stored is part of what the app must do",
            "The analysis table lists what the app does (add, list, summarise). How the data is stored is a choice about structure, made in Design."),
        opt("It is made in Design but reaches Development, Testing, Deployment and Maintenance too",
            "The reading code, the test files, where the file lives and how broken rows are handled all depend on it.", True),
        opt("Move it to Development: whoever writes the code that reads the file will settle the format",
            "Development builds from the design. Leaving a choice that every later phase depends on to whoever codes first is how four people build four corners."),
        opt("Leave it in Design and move on: the later phases follow the chosen format at no extra cost",
            "Design is the right column, but the cost is not zero: the reading code, the test files, where the file lives and how broken rows are handled all depend on it."),
    ],
    """
    The card sort's first follow-up question is "Which decisions affect more than one phase?". Storing data as a hand-editable CSV is decided once, in Design, but Development writes the code that reads it, Testing needs sample files, Deployment has to put the file somewhere on someone else's machine, and Maintenance deals with the broken rows people will type. Moving the card, or treating it as free for the later phases, misses that reach, which is what the exercise was designed to make visible. Decisions with that reach are the ones worth getting right early.
    """,
    verified="reasoning",
))

Q.append(mcq(
    18, "hard", ["judgement"], 4, "S1 slides 17, 28",
    """
    The card sort's second question asks: "Which trade-offs only become visible once the whole board is laid out?" A group has placed the card "Skip automated tests to reach CP1 sooner" under Development. Which observation answers that question for this card?
    """,
    [
        opt("The time saved shows under Development; the cost lands under Testing and Maintenance",
            "This is a trade-off between columns, visible only with the whole board laid out: one phase looks cheaper because another pays.", True),
        opt("Move the card to Testing, since a decision about tests is made in the Testing phase",
            "Moving the card does not answer the question, and the decision to skip tests is made while building. The question is where it is paid for."),
        opt("The trade-off stays inside Development: faster coding now, slower coding later on",
            "The cost leaves Development: it lands in Testing and Maintenance, which is why it appears once the full board is laid out."),
        opt("The trade-off is between Idea and Analysis, because tests are part of what the app does",
            "Tests check what the analysis said; they are not features, and the cost does not land in those phases."),
    ],
    """
    A trade-off that "only becomes visible once the whole board is laid out" is one whose benefit and cost sit in different columns. Skipping tests makes Development look faster. The bill arrives in Testing (session 1: "a checklist, run every time, not once", which now does not exist) and in Maintenance (every later change can break something silently). Looking at a single column, the decision seems free; looking at the whole board, you see who pays. Relocating the card misses the question, which is about consequences across phases.
    """,
    verified="reasoning",
))

# ---- s5: Waterfall -------------------------------------------------------------------------------

Q.append(mcq(
    19, "core", ["concept"], 5, "S2 slide 4",
    """
    Which description matches Waterfall as session 2 presents it?
    """,
    [
        opt("Short cycles in which the customer reviews working software at the end of each one",
            "That is Agile's plan, build, review with user, learn. In Waterfall the customer is involved mostly at the start and the end."),
        opt("A board of columns from which the team pulls the next item when it has capacity",
            "That is Kanban, one of the methodologies that follow Agile principles."),
        opt("Phases that overlap freely, with requirements refined as the team learns",
            "Waterfall fixes requirements early and finishes each phase before the next begins."),
        opt("Linear, sequential phases, each finished before the next begins",
            "Slide 4's definition; the requirements are also fixed early.", True),
    ],
    """
    Slide 4: "Waterfall: linear, sequential phases. Each one finished before the next begins." Its characteristics: requirements fixed early, and changing them is costly and discouraged; long cycles of months or years before delivery; the customer involved mostly at the start and the end; heavy documentation up front. The other options describe Agile's short review cycles, Kanban's board, and an iterative refinement of requirements, which is exactly what Waterfall avoids.
    """,
))

Q.append(mcq(
    20, "exam", ["concept"], 5, "S2 slide 5; Moodle workshop brief",
    """
    A Waterfall team has finished Design for a parking-lot system. What has to happen before Implementation may start?
    """,
    [
        opt("The architecture documents are approved: the gate is a signed-off document",
            "Slide 5: \"The gate between phases is a document that gets approved.\" Design's output is the architecture documents.", True),
        opt("A user tries a working version of the design and gives feedback on what to change",
            "That is Agile's review with the user. Waterfall has no working software at this point, and the customer is involved mostly at the start and the end."),
        opt("The CI check goes green on the branch where the design documents are kept",
            "CI checks code, and there is no code yet. A green CI check is this course's Definition of Done, not Waterfall's gate."),
        opt("The Product Owner reorders the backlog and the team plans the next sprint",
            "Product Owner, backlog and sprint are Scrum vocabulary. Waterfall makes one pass with document gates."),
    ],
    """
    Each Waterfall phase has an output: a signed specification, architecture documents, code, a test report, a running system. "The gate between phases is a document that gets approved." Implementation must then "build strictly from the design", so the design has to be signed off first. The workshop's rule of the game follows from this: once a phase is signed off, going back needs a formal change request. Options that mention users trying software, CI or sprints import practices from Agile and from this course.
    """,
))

Q.append(sort_q(
    49, "core", ["concept"], 5, "S2 slides 4–5",
    """
    A Waterfall project builds a loans system for a city library. Put each activity or document under the Waterfall phase where it belongs.
    """,
    [("requirements", "Requirements"), ("design", "Design"), ("implementation", "Implementation"),
     ("testing", "Testing"), ("deployment", "Deployment & maintenance")],
    [
        ("Interview every department to gather everything the system must do", "requirements",
         "Gathering everything the system must do is Requirements."),
        ("A 60-page specification, signed by the library before design starts", "requirements",
         "A signed specification is Requirements' output, and its approval is the gate into Design."),
        ("Approved diagrams of the modules and how they connect, drawn before any code", "design",
         "Design decides the structure before any code; its output is the architecture documents."),
        ("Decide the database tables and how the modules share them, for the whole system at once", "design",
         "Deciding the structure of everything up front, before any code, is Waterfall's Design."),
        ("Developers write the loans module strictly from the approved architecture", "implementation",
         "Implementation builds strictly from the design, and its output is code."),
        ("Check each requirement in the signed specification against the finished system", "testing",
         "Waterfall's Testing verifies against the specification, near the end."),
        ("A report listing which requirements passed and which failed", "testing",
         "A test report is the Testing phase's output."),
        ("The system goes live in every library branch, and a team fixes what breaks", "deployment",
         "Ship it; fix what breaks. The output is a running system."),
    ],
    """
    Slide 5 gives each phase an output, and "the gate between phases is a document that gets approved". Requirements gathers everything the system must do and ends with a signed specification. Design decides the structure before any code and produces architecture documents. Implementation builds strictly from the design and produces code. Testing verifies against the specification and produces a test report. Deployment and maintenance ships it and fixes what breaks, leaving a running system. Of the five outputs, the running system is the first a user can try, and it comes last.
    """,
))

# ---- s6: where Waterfall works / fails -------------------------------------------------------------

Q.append(mcq(
    8, "core", ["concept", "compare"], 6, "S2 slide 8",
    """
    Session 2's slide 8 pairs each Waterfall disadvantage with Agile's answer to it. Which pairing is the one on the slide?
    """,
    [
        opt("Inflexible to change → a signed specification that fixes the scope early",
            "A signed, fixed specification is Waterfall's own method and the cause of the inflexibility. Agile's answer is iteration: change is expected at any stage."),
        opt("Testing delayed to the end → testing integrated into every short cycle",
            "This row is on the slide: each short cycle includes its own testing, so nothing waits for the end.", True),
        opt("Focus on the plan, not the user → a longer Requirements phase with more interviews",
            "More up-front analysis is still a focus on the plan. Agile's answer is frequent user involvement throughout."),
        opt("Problems found late → a larger test team brought in for the final months",
            "A bigger test at the end still finds problems at the end. Agile's answer is continuous feedback that finds them early."),
    ],
    """
    The table on slide 8: inflexible to change → iterative, change is expected at any stage; problems found late → continuous feedback finds them early; testing delayed to the end → testing integrated into every short cycle; poor fit for evolving requirements → built for evolving requirements; focus on the plan, not the user → frequent user involvement drives the product. Each wrong option answers a Waterfall weakness with more Waterfall: a firmer specification, a longer Requirements phase, a bigger test at the end. Agile's answers share one move: do the thing earlier and more often, in short cycles, with the user involved.
    """,
))

Q.append(mcq(
    21, "exam", ["judgement", "compare"], 6, "S2 slides 6, 13",
    """
    Which of these projects does session 2 suggest Waterfall genuinely fits?
    """,
    [
        opt("A start-up's first app for an untested market, where the idea changes every few weeks",
            "Requirements are unknown and moving: the case Agile is built for."),
        opt("An IT help desk handling a steady stream of small, varied requests from all departments",
            "That is Kanban's \"best when\" on slide 13: a steady stream of varied requests."),
        opt("A fixed-price, fixed-scope system for a regulator that demands full documentation",
            "Known, stable requirements, a fixed scope and price, and regulation that demands documentation: slide 6's conditions.", True),
        opt("A student club website whose committee changes its mind after every single meeting",
            "Evolving requirements are \"a poor fit\" for Waterfall; Agile is \"built for evolving requirements\"."),
    ],
    """
    Slide 6: "Waterfall assumes the requirements are known in advance and stable. When that is true, it works." It names bridges and buildings (requirements known up front, change ruinously expensive, regulation demands documentation), projects where predictability matters more than speed, and "contracts with a fixed scope and a fixed price". The regulated, fixed-price system ticks every condition. The start-up and the club have moving requirements, and the help desk is a stream of varied requests, Kanban's best case.
    """,
))

Q.append(mcq(
    22, "exam", ["concept", "judgement"], 6, "S2 slides 7–8",
    """
    After nine months, a client sees the first version of their booking system and says: "Now that I see it, what we actually need is something different." The project manager concludes: "Our analysis failed. Next time we spend longer on Requirements." What does session 2 say?
    """,
    [
        opt("The manager is right: a complete enough specification, written with more care, prevents later changes",
            "Session 2 rejects this: no amount of up-front analysis stops a customer learning what they want from a real version."),
        opt("Requirements changing after a first version is normal, not a failed analysis; show software sooner",
            "Slide 7's own words, and Agile's answer: frequent user involvement, weeks rather than nine months.", True),
        opt("The client is at fault: once the specification is signed, the requirements are fixed for good",
            "The contract may say so, but the slide's point is that this is how software requirements behave. Leaning on the contract is contract negotiation over collaboration."),
        opt("The problem was integration risk: the parts were built separately and combined too late",
            "Integration risk is about parts built in isolation not fitting. Here the client's understanding of what they need changed."),
    ],
    """
    Slide 7 lists "requirements change" as the first reason Waterfall fails for software: "The customer sees the first version and understands what they actually wanted. This is normal, not a failure of analysis." Spending longer on Requirements treats a normal event as a mistake. The answer on slide 8 is structural: frequent user involvement and short cycles, so the first version a client sees arrives after weeks, when a change is cheap, rather than after nine months.
    """,
))

Q.append(mcq(
    23, "hard", ["concept", "judgement"], 6, "S2 slide 7",
    """
    In month 1 of a Waterfall project, the signed specification assumes that every bank export has four columns. The test team starts in month 10 and finds that real exports have five, so importing fails on every real file. Rewriting the import delays the launch by two months. Which explanation fits best?
    """,
    [
        opt("Requirements change: the customer changed their mind about the file format halfway through",
            "Nobody changed their mind. The assumption was wrong from the very start."),
        opt("Integration risk piles up: parts built in isolation do not fit when they are combined",
            "The mismatch is between the program and real data, not between parts built by different people."),
        opt("The gate failed: the specification should never have been signed off in month 1",
            "The specification was signed as the process requires. What went wrong is how late anything tested it."),
        opt("Feedback arrives too late: an early wrong assumption is only found by testing near the end",
            "A month-1 mistake surfaced in month 10, because Waterfall's testing waits for the end.", True),
    ],
    """
    Slide 7's second reason: "Feedback arrives too late. Testing is done near the end, so a wrong assumption early in the project is only found close to the end." Every detail fits: the assumption dates from month 1, the first test against real data happens in month 10, and the fix now costs two months. Requirements change would need someone to change their mind; integration risk would need separately built parts that fail to fit. Agile's answer from session 2's slide 8 is "testing integrated into every short cycle": one real bank file in the first iteration would have exposed the fifth column within weeks.
    """,
))

Q.append(mcq(
    46, "hard", ["concept", "judgement"], 6, "S2 slides 7–8, 13; S1 slide 6",
    """
    A Waterfall team builds a parking-lot system from a signed specification that everyone has read. For six months each of the four developers works alone on one part: tickets, pricing, payments and reports. In month 7 they combine the parts for the first time. Tickets record the stay in hours, pricing expects minutes, and the reports read a file that no other part writes. Which explanation fits best?
    """,
    [
        opt("Requirements changed: the client saw the system and realised it wanted something else",
            "The client has not seen anything yet and nobody changed the specification. The clash is between the parts themselves."),
        opt("\"Works on my machine\": each part runs for its author and nowhere else",
            "Each part may run anywhere. The trouble is that the parts do not fit each other once combined, and no machine fixes that."),
        opt("Integration risk piled up: parts built in isolation were first combined at the end",
            "Slide 7's third reason: four parts built separately for six months meet in month 7 and do not fit.", True),
        opt("No shared plan: four people built four corners because nobody agreed what to build",
            "There is a shared plan, the signed specification, and each developer built the agreed part. What was missing was combining the parts early and often."),
    ],
    """
    Slide 7: "Integration risk piles up. Four people build four parts in isolation; they are first combined at the end, and then nothing fits." It sounds like session 1's "four people build four corners", and that is the trap: there the team has no shared plan, while here the plan exists and is signed. The parts still clash because a specification cannot pin down every detail two parts must agree on (hours or minutes, which file), and nobody checks until month 7. A longer specification would not have saved them; combining the parts every day would. That is why XP's continuous integration, and this course's CI check on every push, matter even when the plan is good.
    """,
))

# ---- s7: Agile and the Manifesto ----------------------------------------------------------------------

Q.append(mcq(
    24, "core", ["concept"], 7, "S2 slide 10",
    """
    Which statement about Agile matches session 2?
    """,
    [
        opt("The lifecycle phases still happen, in every short cycle, on a small slice of the product",
            "Slide 10: the same phases \"just happen in every cycle, on a small slice, instead of once across the whole project\".", True),
        opt("Agile drops the Design and Testing phases so that the team can deliver working code faster",
            "Nothing is dropped; slide 8 says testing is integrated into every short cycle."),
        opt("Agile was formalised in the late 1990s as a stricter, documented form of Waterfall",
            "It was formalised in 2001 by practitioners reacting against Waterfall's failures; the late 1990s is when Waterfall dominated."),
        opt("Agile replaces the seven lifecycle phases with four new ones: plan, build, review, learn",
            "Plan, build, review with user, learn is the loop each cycle goes round; inside it the same lifecycle phases still happen, on a small slice."),
    ],
    """
    Slide 10 defines Agile: formalised in 2001 by practitioners reacting to Waterfall's failures on software; iterative, incremental, adaptable ("build a small working slice, show it, learn, adjust"); working software delivered frequently, in weeks rather than years. The cycle is Plan, Build, Review with user, Learn. The key sentence is that "the same lifecycle phases still happen". Agile changes how often you go through them and on how much of the product.
    """,
))

Q.append(mcq(
    25, "exam", ["concept", "judgement"], 7, "S2 slide 11; S4 slide 17",
    """
    Your teammate says: "The Agile Manifesto values working software over comprehensive documentation, so we can skip the README." What is the best reply?
    """,
    [
        opt("Agreed: in Agile, the working code itself is all the documentation a project really needs",
            "This reads \"over\" as \"instead of\". The Manifesto never says documentation has no value."),
        opt("Agreed for now: documentation belongs at the very end, once all the code is finished",
            "That moves documentation to the end, which the Manifesto never says. It ranks values; it does not schedule documents."),
        opt("No: the right side still has value; working software is only ranked above it",
            "The closing sentence: \"while there is value in the items on the right, we value the items on the left more\".", True),
        opt("No: the Manifesto actually puts documentation first, ahead of working software",
            "This reverses the value. Working software is on the left, the side valued more."),
    ],
    """
    The four values end with: "While there is value in the items on the right, we value the items on the left more." It is a ranking, not a ban: when writing a 40-page specification competes with shipping working software, working software wins, but useful documentation stays. A README is exactly the documentation that helps: the project brief's bar is that a stranger can install and run the program with no help from you, and CP1's Definition of Done required a README saying what the program does and how to run it.
    """,
))

Q.append(mcq(
    26, "exam", ["concept", "judgement"], 7, "S2 slides 10–11",
    """
    A manager announces: "We are Agile now, so no more planning. We respond to change." Which reading of "responding to change over following a plan" is correct?
    """,
    [
        opt("Plans are waste in Agile, so the team should decide each morning what to build",
            "Every Agile cycle begins with Plan. Deciding afresh each morning invites \"four people build four corners\"."),
        opt("The team still plans, but changes the plan when it learns something new",
            "The value ranks adapting above sticking to the plan; it does not remove the plan.", True),
        opt("Plans are only allowed when the client insists on a fixed-price contract up front",
            "No such rule exists. Agile teams plan every cycle, whatever the contract."),
        opt("The plan is written once at the start, and only its dates may move later",
            "That is still following a fixed plan. Agile re-plans the content after each review with the user."),
    ],
    """
    Slide 10's cycle is Plan, Build, Review with user, Learn, and back to Plan: planning happens in every cycle. The fourth value says the team values responding to change more than following a plan, and the closing sentence keeps value in the plan itself. What Agile drops is the single, fixed, up-front plan that must be followed to the end. A team with no plan at all is not more Agile; it is the "no shared plan" failure from session 1.
    """,
))

Q.append(mcq(
    27, "exam", ["concept", "judgement"], 7, "S2 slide 11",
    """
    A new team spends its first three weeks comparing project-management tools and configuring boards, labels, automations and rules for how tickets move between columns. The four members have not yet sat down together to talk about the product. Which Manifesto value are they getting backwards?
    """,
    [
        opt("Customer collaboration over contract negotiation",
            "No customer or contract appears in the story."),
        opt("Responding to change over following a plan",
            "Nothing has changed yet, and they have not made a product plan to follow."),
        opt("Working software over comprehensive documentation",
            "They have written no product documentation either. What they over-invest in is tooling and process."),
        opt("Individuals and interactions over processes and tools",
            "Three weeks on tools and process rules, and no conversation between the people: the right-hand side put first.", True),
    ],
    """
    The first value reads "individuals and interactions over processes and tools". This team has done the reverse: it has invested everything in tools and in rules for how work moves, before the people have even talked about what to build. The tools may be useful later (there is value on the right), but session 2's point is that the conversation comes first. The other values concern customers and contracts, plans versus change, and documents versus software, none of which is what this team over-values.
    """,
))

Q.append(mcq(
    28, "hard", ["concept", "judgement"], 7, "S2 slide 12; backlog brief (22 Sep)",
    """
    On the Fortune Cookie project, the basic `fortune` command already works. Nil then spends a week building a plugin system "so that any future kind of fortune can be added without touching the code". Nobody has asked for other kinds of fortune. He says this follows the principle "welcome changing requirements". Which principle is he actually breaking?
    """,
    [
        opt("Face-to-face conversation",
            "Talking more might have stopped him, but the principle his work contradicts is about the work itself."),
        opt("Welcome changing requirements",
            "Welcoming change means adapting when a real change arrives. He is building for an imagined one, and this is the principle he cites, not the one he breaks."),
        opt("Simplicity: maximise work not done",
            "A week on a feature nobody asked for is exactly the work this principle says to avoid.", True),
        opt("A pace sustainable indefinitely",
            "One week on one feature is not a pace problem; nobody is overworking."),
    ],
    """
    The "keep improving" group includes "simplicity: maximise work *not* done". Building flexibility for requests that do not exist is work that could have stayed undone; if a new kind of fortune is ever requested, the team can change the code then. The trap is the principle Nil cites: "welcome changing requirements" is about responding to changes that have arrived; Nil is predicting one. The backlog brief makes the same point from another angle: only the top items need detail, because "the rest will change, and detailing them now is wasted work".
    """,
))

Q.append(sort_q(
    29, "exam", ["concept", "judgement"], 7, "S2 slide 12",
    """
    Each story shows one of the Agile principles at work. Sort it into the principle's group on slide 12.
    """,
    [("deliver", "Deliver value continuously"), ("change", "Expect change; collaborate"),
     ("trust", "Trust people; sustainable pace"), ("improve", "Keep improving")],
    [
        ("The team shows a working version to users every two weeks instead of one big release at the end", "deliver",
         "Early and continuous delivery; deliver working software often."),
        ("Progress is reported as \"features a user can run\", not as \"percentage of the design document written\"", "deliver",
         "Working software = progress."),
        ("Halfway through, the client asks for a new report, and the team adds it to the plan instead of refusing", "change",
         "Welcome changing requirements."),
        ("A person from the business side answers the developers' questions every day, so no decision waits a week", "change",
         "Business and developers, daily."),
        ("The team stops planning weekend work before deadlines, because tired people ship bugs", "trust",
         "A pace sustainable indefinitely."),
        ("The developers, not a manager, decide who takes which task", "trust",
         "Self-organising teams; motivated individuals, trusted."),
        ("Every few weeks the team discusses what to change in how it works, and changes it", "improve",
         "Reflect and adjust, regularly."),
        ("The team drops a planned \"export to PDF\" feature that no user has asked for", "improve",
         "Simplicity: maximise the work not done."),
    ],
    """
    The four groups on slide 12: deliver value continuously (early and continuous delivery, working software often, working software as the measure of progress); expect change and collaborate (welcome changing requirements, business and developers daily); trust people and keep a sustainable pace (motivated individuals, face-to-face conversation, a pace sustainable indefinitely, self-organising teams); keep improving (technical excellence, simplicity, reflect and adjust). Match each story to the principle it shows, then to its group.
    """,
    verified="reasoning",
))

# ---- s8: methodologies and what the course uses ------------------------------------------------------

Q.append(mcq(
    30, "exam", ["judgement", "compare"], 8, "S2 slide 13",
    """
    After launch, a two-person team maintains a university's room-booking tool. Requests arrive every day and vary widely: a broken link, a new report, a question about permissions, a calendar bug. Fixed two-week sprints have proved pointless, because priorities change daily. Which approach from slide 13 fits best?
    """,
    [
        opt("Scrum, because fixed-length sprints keep the team focused on one shared goal",
            "Scrum's \"best when\" is feature work with a team; daily-changing small requests keep breaking the sprint plan, as the team found."),
        opt("XP, because pair programming and test-driven development fix bugs faster",
            "XP prescribes engineering practices for writing code; it does not organise a stream of incoming requests."),
        opt("Waterfall, because each request can be fully specified and signed off first",
            "A signed specification for every small request turns minutes of work into weeks of paperwork."),
        opt("Kanban, because work is pulled from a board when there is capacity",
            "Slide 13: Kanban (a board, a work-in-progress limit, pull when there is capacity) is best for \"a steady stream of varied requests\".", True),
    ],
    """
    Slide 13 lists what each approach prescribes and when it is best. Kanban: "a board of columns; a limit on work-in-progress; pull the next item when you have capacity", best for "a steady stream of varied requests". That is this team: no natural sprint goal, priorities that change daily, and items of very different sizes. Scrum's fixed-length sprints suit feature work by a team of ten or fewer; XP prescribes how code is written; Lean targets cycle time end to end.
    """,
))

Q.append(mcq(
    31, "exam", ["concept"], 8, "S2 slides 14–15; S4 slide 16",
    """
    Which statement describes how this course uses Agile methodologies for the group project?
    """,
    [
        opt("It follows Scrum by the book, with every ceremony and role, and nothing from other methods",
            "The course deliberately mixes methods; slide 15 warns against following one methodology blindly."),
        opt("Scrum vocabulary, XP's practices (TDD, CI, small commits) and a Kanban board",
            "Slide 14, item by item: checkpoints are sprints, the Definition of Done is a green CI check, the lecturer is the Product Owner.", True),
        opt("Waterfall, with each checkpoint as a gate passed only when an approved document is handed in",
            "Checkpoints are sprints, and the Definition of Done is a green CI check, not an approved document."),
        opt("Kanban only: no sprints and no Definition of Done, just a shared board of tasks to pull from",
            "The course uses sprints (checkpoints) and a Definition of Done (a green CI check) as well as the board."),
    ],
    """
    Slide 14: "Scrum vocabulary for the project: checkpoints are sprints, Definition of Done is a green CI check, Product Owner is me. XP's engineering practices are the technical spine: TDD, CI, small commits. Kanban board is how you will track your group's work." It is the course practising what slide 15 preaches: borrow the practices that help you iterate fast and deliver value, rather than following one methodology blindly. Note the Waterfall trap: a checkpoint is a git tag that the CI check must pass, not a signed document.
    """,
))

Q.append(mcq(
    32, "hard", ["judgement"], 8, "S2 slides 14–15; S4 slide 14",
    """
    Group 7 holds sprint planning, a fifteen-minute daily, a sprint review and a retrospective every sprint, exactly by the book. They have no tests, push one large commit a week, and their CI check has been red for nine days. They describe themselves as "fully Agile". Which judgement fits the course best?
    """,
    [
        opt("They are Agile: the events are in place, and tests can be added in a later sprint",
            "Every item must meet the Definition of Done when it is finished. With no tests and a red CI check, nothing from the last nine days is done, and \"later\" keeps moving."),
        opt("They should switch from Scrum to Kanban, because the meetings are their problem",
            "The meetings are not what is missing. A different board adds no tests and turns no check green."),
        opt("They copied the ceremonies and skipped the practices: tests, green CI, small commits",
            "XP's practices (TDD, CI, small commits) are the course's technical spine, and they are exactly what this group skipped. Session 4 calls the belief that following the ceremonies is enough an \"equally dangerous tendency\".", True),
        opt("Their work is done: every sprint ended with a review, as the Definition of Done asks",
            "The course's Definition of Done is a green CI check, and theirs has been red for nine days. A review is a Scrum event; it is not the bar an item must meet."),
    ],
    """
    Slide 15: "It is not about picking one methodology and following blindly, but borrowing the practices that will help you iterate fast and deliver value." Slide 14 names those practices for this course: TDD, CI and small commits, with a green CI check as the Definition of Done. By that definition, nothing Group 7 has done in nine days is done. Session 4 adds that following the Scrum ceremonies is not enough to get real work done. Holding the events does not make work done, and changing method, to Kanban for example, leaves the real gap untouched.
    """,
))

Q.append(mcq(
    33, "beyond", ["judgement"], 8, "S2 slides 13–14",
    """
    Your group's Kanban board two weeks before the partial submission: **To do**: 6 cards, **In progress**: 9 cards, **Done**: 1 card. There are four of you. Which change does Kanban, as slide 13 describes it, point to?
    """,
    [
        opt("Add an \"Almost done\" column so that the progress becomes visible",
            "Another column relabels the same unfinished work; it finishes nothing."),
        opt("Move every card back to To do and plan a fresh two-week sprint",
            "That swaps methods. Kanban's own tool for this board is the limit on work in progress."),
        opt("Set a work-in-progress limit and finish cards before pulling new ones",
            "Nine cards in progress for four people is the problem a WIP limit and pulling only with capacity exist to fix.", True),
        opt("Split each in-progress card into smaller cards so that more of them can start",
            "Smaller cards can help, but starting more of them raises the work in progress further."),
    ],
    """
    Slide 13 says Kanban prescribes "a board of columns; a limit on work-in-progress; pull the next item when you have capacity". This board breaks the last two: nine cards in progress for four people means everyone is juggling two or three things, and only one has reached Done. A WIP limit (for example, one or two cards per person) forces the group to finish before starting, so cards actually reach Done. That matters most before a deadline, when a finished, tested feature is worth more than three half-built ones.
    """,
    verified="reasoning",
))

Q.append(sort_q(
    34, "core", ["concept"], 8, "S2 slide 13",
    """
    Which approach on slide 13 prescribes each practice, or is described as best in each situation?
    """,
    [("scrum", "Scrum"), ("kanban", "Kanban"), ("xp", "XP"), ("lean", "Lean")],
    [
        ("Fixed-length sprints, with planning, daily, review and retrospective", "scrum",
         "Scrum organises work into time-boxed sprints and their events."),
        ("A Product Owner, a Scrum Master and Developers", "scrum",
         "Scrum's three roles."),
        ("Best for feature work with a team of 10 or fewer", "scrum",
         "Scrum's \"best when\" on slide 13."),
        ("A board of columns with a limit on work in progress; pull the next item when you have capacity", "kanban",
         "Kanban organises the flow of work on a board and keeps work in progress under a limit."),
        ("Best for a steady stream of varied requests", "kanban",
         "Kanban's \"best when\": no sprint goal, just the next most important request."),
        ("Pair programming, test-driven development, continuous integration, small releases", "xp",
         "XP prescribes engineering practices; it is where TDD comes from."),
        ("Best when code quality and change rate are both high", "xp",
         "XP's \"best when\": its practices keep code safe to change often."),
        ("Eliminate waste and optimise the whole flow", "lean",
         "Lean's focus is waste across the whole process."),
        ("Decide as late as responsibly possible", "lean",
         "Lean delays decisions until the information to make them exists."),
        ("Best for cutting cycle time end to end", "lean",
         "Lean's \"best when\" on slide 13."),
    ],
    """
    Each approach prescribes a different kind of thing. Scrum organises time and roles (sprints; Product Owner, Scrum Master, Developers; planning, daily, review and retrospective) and suits feature work by a team of ten or fewer. Kanban organises flow (a board, a WIP limit, pull when there is capacity) and suits a steady stream of varied requests. XP prescribes how code is written and integrated (pair programming, TDD, CI, small releases) for when quality and change rate are both high. Lean removes waste across the whole flow, decides as late as responsibly possible, and targets cycle time end to end.
    """,
))

Q.append(mcq(
    48, "exam", ["judgement", "compare"], 8, "S2 slides 13, 15; S4 slide 14; S1 slides 6, 8",
    """
    A team of six already works in two-week Scrum sprints on a payments program. It adds features every day and releases often. Each release breaks something that used to work, and nobody dares to change the oldest parts of the code. Which approach from session 2's slide 13 should the team borrow from to target this problem?
    """,
    [
        opt("Scrum: tighter fixed-length sprints and clearer roles to keep the team focused",
            "They already run Scrum and the breaks continue. Session 4: \"Scrum organises the work; it does not do it\", with \"no engineering practices at all\"."),
        opt("XP: test-driven development, continuous integration, small releases, pairing",
            "XP prescribes engineering practices and is best when code quality and change rate are both high, which describes this team.", True),
        opt("Kanban: a board with a work-in-progress limit, pulling items as capacity allows",
            "Kanban organises the flow of requests. It says nothing about how the code is written or checked."),
        opt("Lean: eliminate waste and decide late, so that the end-to-end cycle time falls",
            "Lean speeds up the whole flow. This team's problem is changes that break old behaviour, and a faster flow would spread them sooner."),
    ],
    """
    Slide 13: XP prescribes "engineering practices: pair programming, test-driven development, continuous integration, small releases", and is best when "code quality and change-rate are both high". This team changes code daily and keeps breaking old behaviour, session 1's "change one thing, three others break, silently". Tests written first and run on every integration turn those silent breaks into red checks before release. Scrum, Kanban and Lean organise the work or its flow; none of them prescribes how the code is written or checked. Session 4 says it of Scrum directly: "Scrum organises the work; it does not do it." Slide 15's advice fits: borrow the practices that help, whatever the framework.
    """,
))

# ---- s9: the workshop ---------------------------------------------------------------------------------

Q.append(mcq(
    35, "exam", ["concept", "judgement"], 9, "S2 slide 17; Moodle activity brief (15 Sep)",
    """
    In the workshop, a group re-plans a bill-splitting app as Agile. Which first iteration fits the brief's "smallest version a real person could actually use"?
    """,
    [
        opt("Type in who paid what for one shared dinner and see who owes whom",
            "It works and solves a real sliver of the problem, even though it does almost nothing else.", True),
        opt("A clickable mock-up of every screen, to show the client the full vision",
            "A mock-up is a prototype; the brief says \"not a prototype but something that works\"."),
        opt("The complete database design for every feature planned for the year",
            "A design document is Waterfall's Design output. Nobody can use it."),
        opt("The first half of every feature, so all of them can be finished together later",
            "Half-features cannot be used. That is a layer across the whole product, not a slice."),
    ],
    """
    The brief's first Agile question is: "What is the smallest version a real person could actually use? (Not a prototype but something that works, even if it does almost nothing.) That is your first iteration." Splitting one dinner works end to end: input, calculation, result. A user can try it and say what is missing, which is the point of the review step in plan, build, review with user, learn. Mock-ups, design documents and half-built features all postpone the first moment a real person uses the software.
    """,
))

Q.append(mcq(
    36, "core", ["concept"], 9, "Moodle activity brief (15 Sep)",
    """
    The workshop's last Agile question is "What did switching cost you?". Which answer names a real downside that the brief expects?
    """,
    [
        opt("Users see working software later than they would have in the Waterfall plan",
            "The reverse is true: Agile puts working software in front of users within weeks."),
        opt("Testing has to wait until the final iteration, when everything has been built",
            "The reverse again: testing is integrated into every short cycle."),
        opt("Requirements can no longer change once the first iteration has started",
            "Agile is built for evolving requirements; change is expected at any stage."),
        opt("A fixed price is harder to quote, since the final scope is not pinned down",
            "One of the three costs the brief lists, alongside less up-front certainty and more coordination.", True),
    ],
    """
    The brief asks: "What did switching cost you? (Less up-front certainty about final scope? Harder to quote a fixed price? More coordination overhead?) Name at least one real downside; Agile is not free." Because the scope is discovered cycle by cycle, nobody can promise on day one exactly what the finished product contains, which makes a fixed price harder to quote. Each wrong option names a Waterfall weakness and pins it on Agile.
    """,
))

Q.append(mcq(
    37, "hard", ["compare", "judgement"], 9, "S2 slides 5, 10, 17; Moodle activity brief (15 Sep)",
    """
    Two groups plan the same vending machine program, one as Waterfall and one as Agile. Where do the two plans first diverge?
    """,
    [
        opt("At Testing: the Agile plan tests every iteration, while Waterfall tests near the end",
            "A real difference, but not the first: long before Waterfall reaches its Testing phase, the plans' very first outputs are different kinds of thing."),
        opt("At the first output: a signed specification versus a small program a user can try",
            "From day one the plans produce different kinds of thing: Waterfall a document, Agile working software.", True),
        opt("Nowhere: the Agile plan is simply the same Waterfall plan cut into two-week pieces",
            "Agile does not slice a fixed plan; each cycle is re-planned after the review with the user."),
        opt("At Design: the Agile plan skips architecture and starts coding on the first day",
            "Agile keeps the phases: each cycle plans and designs a small slice before building it (slide 10)."),
    ],
    """
    The workshop asks "where did the two plans diverge first?". Waterfall's first phase, Requirements, produces "a signed specification" of everything the system must do, and nothing usable exists until the end. Agile's first iteration is "the smallest version a real person could actually use", so the first output is working software in front of a user. The Testing option names a real difference, but not the first one. The option that cuts the Waterfall plan into two-week pieces is the subtle trap: Agile is not a fixed plan chopped into sprints. What a later cycle builds depends on what the team learned from the review of the earlier one.
    """,
))

Q.append(mcq(
    38, "beyond", ["read-tool-output", "judgement"], 9, "expense-tracker v0.0–v0.1; S1 slide 16; S4 slide 25; backlog brief (22 Sep)",
    """
    Session 1's analysis table lists three features for the expense tracker: add an expense, list expenses, summary by category. This is how the demo project was actually built:

    @@Q38_RUN@@

    What does this history show about how it was built?
    """,
    [
        opt("A usable slice (the category summary) came first; other behaviour arrived in later commits",
            "The first commit already totals by category; filtering, the largest expense and `add` follow one at a time.", True),
        opt("All three analysed features were built together in one commit, as in Waterfall's Implementation phase",
            "Behaviour arrives over several separate commits, and `add` appears only in the sixth."),
        opt("The features were built in the order of the analysis table: add first, then list, then the summary",
            "The summary came first and `add` sixth; no list command appears in this range."),
        opt("Nothing anyone could use existed until the project became a package in `a953d05`",
            "The first commit was already a script that printed a full report by category."),
    ],
    """
    Read the messages oldest first. `3e0834f` adds a script that totals expenses by category: run as `python tracker.py`, it prints a complete report, so it is usable on day one. Filtering (`6efdf9d`), the largest expense (`c746d38`), packaging (`a953d05`, `2ecad20`) and the `add` command (`bc9ef3d`) follow, each a small step. The backlog brief describes the category total as "the first thing it ever did" and says the `add` item "became expenses add". The analysis said what the app would do; the history shows it delivered slice by slice.
    """,
    origin="history",
    verified="run",
))

# ---- open questions ------------------------------------------------------------------------------------

Q.append(open_q(
    39, "core", ["concept"], 2, "S1 slides 15–19",
    """
    A friend who missed session 1 asks you to explain the software development lifecycle using the expense tracker.
    """,
    [
        part("1", "Which three phases come before Development, and what does each one decide for the expense tracker?", 2,
             "Idea: who it is for and what problem it solves (knowing where your money goes). Analysis: everything it will do, pinned down before the build: add an expense, list expenses, a summary by category. Design: the structure, how the pieces connect and how a user moves through it.",
             ["Idea, with who will use it or what problem it solves",
              "Analysis, with the feature table (add an expense, list expenses, summary by category) pinned down before the build",
              "Design, with the structure: how the pieces connect or how a user moves through it"],
             "Listing the three names without saying what each decides earns one mark at most. A common mix-up puts the feature table in Idea or in Design: slide 16 places it under Analysis, \"everything it will do, pinned down before the build starts\"."),
        part("2", "What does \"testing is a checklist, run every time, not once\" mean, and how does this course do it?", 2,
             "Testing checks the program does what the analysis said. One run describes one moment; the same checklist after every change shows whether the latest change broke something. Here ruff, mypy and pytest run in CI on every push.",
             ["Testing verifies the program against what the analysis said",
              "The same checks are repeated after every change, not done once at the end",
              "Names the course's mechanism: the CI check (ruff, mypy, pytest) on every push"],
             "\"Test it at the end\" is the opposite of the point. \"Test it thoroughly once\" misses \"every time\". Naming pytest without saying when it runs misses the idea of repetition, which is what catches a change that silently breaks something else."),
        part("3", "Why does the course say Maintenance lasts \"forever\"?", 1,
             "Most software is maintained far longer than it is written: bugs, new features, replaced components and tech debt keep sending the cycle back to Design.",
             ["States that software keeps changing after release (bugs, features, refactors, tech debt) and is maintained far longer than it is written"],
             "\"Because there are always bugs\" is only part of it: it misses features, refactors and tech debt, and the idea that software is living and only stops changing when nobody runs it."),
    ],
    """
    This is the lesson of slides 15 to 19 in one answer. The strong version uses the expense-tracker example for each phase, keeps Analysis (what it will do) apart from Design (how the pieces connect), explains why repeating the checklist matters, and ties Maintenance to the four reasons the cycle goes on.
    """,
))

Q.append(open_q(
    40, "exam", ["concept", "judgement"], 1, "S1 slides 6–8; S3 slides 3, 5",
    """
    Read this account from a group working on the Library manager project:

    > "In week 2 each of us picked a part to build without agreeing on an order: Marc did fines, Júlia did search, Arnau did reports and I did a login. On Friday Arnau pushed straight to `main`, and from then on nobody's copy passed the checks. When we finally got it running, Júlia's search only worked on her laptop: it needed a package she had installed by hand."
    """,
    [
        part("1", "Name the three failures from session 1 in this story, each with the sentence that shows it.", 3,
             "No shared plan, four people build four corners: each picked a part with no agreed order. A teammate's change breaks the build: Arnau's push to `main` broke the checks for everyone. Works on my machine, and nowhere else: the search needed a package installed only on Júlia's laptop.",
             ["No shared plan / four people build four corners, tied to the parts picked without an agreed order",
              "A teammate's change breaks the build, tied to Arnau's push to `main`",
              "Works on my machine, tied to the package installed by hand on Júlia's laptop"],
             "\"Bad teamwork\" or \"bugs\" is too vague: use the session 1 names. Calling Arnau's push \"works on my machine\" confuses two failures: the build broke for everyone, which is the shared-build failure. Each failure must be tied to the sentence that shows it."),
        part("2", "For each failure, name the answer slide 8 gives and say in a few words how it would have helped.", 3,
             "No shared plan: Agile and Scrum, an ordered plan so everyone builds the most useful item first. Broken build: version control with review and CI, so a broken change is caught on push. Works on my machine: containerisation and automatic deployment; so far in the course, declaring every package in `pyproject.toml` and committing `uv.lock`.",
             ["No shared plan → Agile, Scrum (a shared, ordered plan)",
              "Broken build → version control, code reviews, CI (checks run on every push, or someone reads the change before it lands)",
              "Works on my machine → containerisation and automatic deployment, or dependencies declared so uv installs the same versions for everyone"],
             "Answering \"testing\" for every failure ignores the slide-8 pairings. \"Communicate more\" is not a course practice. For the package problem, \"install it on everyone's laptop\" only spreads the problem: the project itself has to declare what it needs."),
    ],
    """
    This mirrors the exam's "name the problem, name the practice" shape. Full marks need the exact session 1 names, each tied to its evidence, and the slide-8 answer for each with a short reason. The most common slip is mixing up "works on my machine" (one machine only) with "a teammate's change breaks the build" (broken for everyone).
    """,
))

Q.append(open_q(
    41, "exam", ["concept", "judgement"], 3, "S1 slide 19; S7 slide 5",
    """
    Three changes in a Gym workout logger repository:

    - **A.** To finish CP1, the team stores personal bests in a plain text file and adds a backlog note: "Move to a CSV with dates; the text file will make the history report hard."
    - **B.** A user reports that the app crashes for a member who has not logged any workout yet, instead of saying "no record".
    - **C.** The team replaces the text file with a CSV file, converts the existing logs, and the app now also shows the date of each personal best.
    """,
    [
        part("1", "Classify A, and say what makes it that kind of change.", 1,
             "A is tech debt: a shortcut taken willingly to hit CP1, knowing it will need improving; the backlog note shows they knew.",
             ["Tech debt, justified by the deliberate and known shortcut (the backlog note)"],
             "Calling A a bug misses that nothing unintended happened: the team chose the text file and recorded the cost in the backlog. Calling it a feature misses what makes A special: a weaker solution chosen on purpose, with the cost written down, which is what tech debt means."),
        part("2", "Classify B.", 1,
             "B is a bug: unintended behaviour that a user discovered; the app should say \"no record\", not crash.",
             ["Bug, because the behaviour is unintended and was discovered by a user"],
             "\"A feature request\" is wrong: saying \"no record\" is what the program was always meant to do. \"Tech debt\" is wrong too: nobody chose this behaviour; a user discovered it."),
        part("3", "Is C a refactor? Explain using the course's test.", 2,
             "No. C pays back the debt from A, but the app now shows dates, which is new behaviour, so it counts as a feature. A refactor changes the structure and keeps the behaviour; if the output changes, it was not a refactoring.",
             ["Says C is not a refactor because the output changes: dates are now shown",
              "States the test: refactoring changes structure and keeps behaviour (if the output changes, it was not a refactoring)",
              "Notes that C pays back the tech debt from A"],
             "\"Refactor, because the storage changed\" looks only at the inside and ignores that users now see something new. The deciding question is whether the behaviour changed: here it did, because dates now appear on screen."),
        part("4", "Where does the cycle start again for all three?", 1,
             "At the Design phase, as slide 19 says.",
             ["Design"],
             "\"Development\" skips deciding how the change fits the existing structure, and \"Idea\" would restart the whole project. Slide 19 is explicit that bugs, features, refactors and tech debt all go back to Design."),
    ],
    """
    The four kinds of change from slide 19, tested on one story. The marks are for the reasons: deliberate and known (tech debt), unintended and discovered (bug), behaviour changed (a feature, even though it also pays the debt back), and the restart point (Design). Change C is the hard part: a change can repay debt and add behaviour at the same time.
    """,
))

Q.append(open_q(
    42, "exam", ["compare", "judgement"], 9, "S2 slides 4–8, 10; Moodle activity brief (15 Sep)",
    """
    A chain of gyms wants a terminal tool for its front desk to log members' workouts and show personal bests. The manager is not yet sure which reports the trainers will want. She asks you to compare Waterfall and Agile for this project.
    """,
    [
        part("1", "How would a Waterfall plan run this project, and what moves it from one phase to the next?", 2,
             "Requirements, Design, Implementation, Testing and Deployment run once, each finished before the next. A phase ends only when its document is approved (signed specification, architecture documents). The manager sees the tool mostly at the start and the end.",
             ["Phases run once, in order, each finished before the next begins",
              "The gate between phases is an approved document (signed specification, architecture documents)",
              "The customer is involved mostly at the start and the end"],
             "Listing the five phases without saying what moves the project between them misses the key idea: the gate is an approved document, not working software. \"Waterfall has no testing\" is wrong: it has a Testing phase, near the end."),
        part("2", "Why does Agile fit this client better? Say what you would build first.", 2,
             "She does not know which reports trainers want, so requirements will change once she sees a first version, which is normal. Agile builds a small working slice, shows it, learns and adjusts. First iteration: log a workout and show that member's personal best; trainers try it and say which report comes next.",
             ["Links the choice to this client's uncertain or changing requirements",
              "Describes short cycles with feedback from real users (plan, build, review with user, learn)",
              "Names a first iteration a real person can use (for example, log a workout and see a personal best), not a prototype or a document"],
             "\"Agile is faster\" or \"Agile is modern\" earns nothing: the argument must come from this client's uncertainty. A first iteration such as \"design the database\" or \"a mock-up of all screens\" is not usable software."),
        part("3", "Name one real downside of choosing Agile here.", 1,
             "Less certainty up front: we cannot promise the final scope or a fixed price, and the trainers must give time to regular reviews.",
             ["Names a genuine cost from the workshop: less up-front certainty about final scope, a fixed price harder to quote, or more coordination overhead"],
             "\"No downsides\" contradicts the brief, which says \"Agile is not free\". \"Users see the software later\" or \"testing happens at the end\" are Waterfall's problems, not Agile's, so they earn nothing here."),
    ],
    """
    The comparison question from the workshop, applied to a new client. A strong answer describes Waterfall fairly (document gates, customer at start and end), argues for Agile from this client's uncertainty rather than from fashion, names a genuinely usable first slice, and admits one real cost.
    """,
))

Q.append(open_q(
    43, "hard", ["compare", "judgement"], 6, "S2 slides 6–7, 13–15",
    """
    Your consultancy bids for a fixed-price contract to build an expense-claims system for a public hospital. The scope is written in a tender document, the price is fixed, and an auditor requires full documentation of requirements and tests before the system goes live.
    """,
    [
        part("1", "Which approach does session 2 suggest fits this contract, and why? Use the conditions from the slides.", 2,
             "Waterfall: the requirements are known up front and stable (written in the tender), the contract has a fixed scope and a fixed price, and regulation demands the documentation that Waterfall produces at every gate. Predictability matters more than speed.",
             ["Chooses Waterfall (a plan-driven approach with document gates)",
              "Justifies it with at least two slide-6 conditions: known and stable requirements, fixed scope and fixed price, documentation demanded by regulation, predictability over speed"],
             "\"Agile is always better for software\" ignores slide 6. Choosing Waterfall without the conditions earns one mark at most: the marks are for matching this project to where Waterfall genuinely works."),
        part("2", "Which reason Waterfall fails for software is still a risk here? Say what would show it.", 1,
             "Feedback arrives too late: testing happens near the end, so a wrong assumption in the specification (say, about how claims are approved) would only appear in the Testing phase, months later.",
             ["Names one slide-7 risk (requirements change, feedback too late, integration risk) and ties it concretely to this project"],
             "\"Nothing can go wrong because the scope is fixed\" misses the point: a fixed scope reduces changing requirements, but testing still comes near the end, so a wrong early assumption is still found late, and parts are still combined late."),
        part("3", "Name two practices you would borrow from Agile methodologies even inside this contract, and what each protects against.", 2,
             "XP's test-driven development, so each part is checked as it is built rather than only in the final Testing phase. Continuous integration with small commits, so parts built by different developers are combined and checked on every push and integration risk does not pile up.",
             ["A concrete practice (TDD, CI, small commits, pair programming) with what it protects against",
              "A second practice with its benefit (for example CI against integration risk, TDD against late feedback)",
              "Links to slide 15: borrow practices instead of following one methodology blindly"],
             "\"Use Scrum\" is not a practice to borrow inside a fixed-scope contract, and naming a ceremony (a daily meeting) without saying what it protects against earns little. Slide 15's point is to borrow the practices that help, whatever the overall plan."),
    ],
    """
    A worst-case comparison: the project is one where Waterfall genuinely fits, so the reflex answer "Agile" loses marks. Full marks need the slide-6 conditions, one slide-7 risk that remains, and two engineering practices borrowed from XP with what each protects against.
    """,
))

Q.append(open_q(
    44, "hard", ["concept", "judgement"], 7, "S2 slides 10–11; S1 slides 6, 8",
    """
    A new team lead reads the Agile Manifesto and announces three decisions:

    - **A.** "No more README or documentation: working software over documentation."
    - **B.** "No more planning: we respond to change."
    - **C.** "No more contract with the client: collaboration over contracts."
    """,
    [
        part("1", "What does the sentence at the end of the four values say, and what does it mean for all three decisions?", 2,
             "\"While there is value in the items on the right, we value the items on the left more.\" The values are a ranking, not a ban: documentation, plans and contracts keep their value, and the left side wins only when the two compete. So all three decisions misread the Manifesto.",
             ["Quotes or paraphrases the closing sentence: there is value on the right; the left is valued more",
              "Concludes it is a ranking, not a ban, so none of the right-hand items is thrown away"],
             "Reading \"over\" as \"instead of\" is exactly the lead's mistake. Agreeing with any one decision (\"documentation is optional in Agile\") loses the point that the right side keeps its value."),
        part("2", "Choose two of the decisions and say what an Agile team actually does instead.", 2,
             "Planning: every Agile cycle starts with Plan; the team plans, then changes the plan after reviewing with the user. Documentation: the team keeps what helps, such as a README that tells a stranger how to install and run the program, but skips heavy specifications up front.",
             ["Planning still happens every cycle (plan, build, review with user, learn); what is learned updates the plan",
              "Documentation stays where it adds value (for example a README so a stranger can install and run the program)",
              "The contract still exists, but the team works with the customer rather than negotiating every change against it"],
             "Restating the value (\"responding to change is good\") without saying what the team does earns nothing. \"Plan less\" is vague: say when planning happens (every cycle) and what changes the plan (feedback from the user)."),
        part("3", "Which failure from session 1 does decision B invite?", 1,
             "No shared plan, four people build four corners.",
             ["No shared plan / four people build four corners"],
             "\"Change one thing, three others break\" is about code that breaks silently, not about the absence of a plan. Without planning, each member decides alone what to build: that is four people building four corners."),
    ],
    """
    Misreadings of the Manifesto are a natural exam question on session 2. The closing sentence answers all three decisions at once; the marks then go to saying concretely what Agile teams still do (plan every cycle, keep useful documentation, keep the contract but collaborate) and to linking "no planning" back to session 1's failure.
    """,
))

Q.append(open_q(
    45, "beyond", ["judgement", "compare"], 9, "Moodle activity brief (15 Sep); S2 slides 6, 10",
    """
    A client offers your agency a fixed price for the bill-splitting app, and also asks for "a demo every two weeks, after which we will tell you what to change".
    """,
    [
        part("1", "Using the workshop's list of costs, explain the tension in what the client is asking for.", 2,
             "A fixed price assumes a scope known up front, the condition under which Waterfall works. Fortnightly demos with changes are Agile, which gives up certainty about the final scope. The workshop names this cost directly: with Agile a fixed price is harder to quote.",
             ["A fixed price assumes a fixed, known scope (where Waterfall works)",
              "Demos followed by changes mean the scope will move (Agile: less up-front certainty about final scope)",
              "Names the workshop cost: a fixed price is harder to quote"],
             "\"Agile and fixed prices cannot coexist\" with no reason earns nothing. The marks are for naming why: a fixed price needs a known scope, and changes every two weeks mean the scope moves."),
        part("2", "Suggest a way to keep both, and say what the client gives up.", 2,
             "Fix the price and the number of two-week iterations, but not the exact feature list. Keep the work ordered by value, so the most useful slice (split one dinner) ships first and each demo decides what comes next. The client gives up a guarantee that every feature imagined today is in the final version.",
             ["Fixes price and time but allows the scope to vary",
              "Orders the work by value so the most useful usable slices come first and each review reorders the rest",
              "States what the client gives up: not every feature imagined today is guaranteed"],
             "\"Charge more\" or \"refuse the demos\" avoids the question. Promising a fixed price, a fixed scope and unlimited changes is the contradiction the question asks you to spot, not a solution."),
    ],
    """
    One step past the workshop. The slides say Waterfall suits fixed-scope, fixed-price contracts and that Agile makes a fixed price harder to quote; a client who wants both forces a choice about which of price, time and scope may move. Fixing time and price and letting the scope flex, with the work ordered by value, is the natural consequence of those two slides. It is reasoning from the slides; the course states no such rule.
    """,
    verified="reasoning",
))

Q.append(open_q(
    50, "hard", ["read-tool-output", "judgement"], 1,
    "S1 slides 6, 8; S8 (dict.fromkeys, frozen); sample Q9 part 3",
    """
    Your teammate removed `frozen=True` from `Expense` so that a typo in an amount can be corrected in place:

    @@Q07_DIFF@@

    `uv run expenses report` still prints the report and exits with 0. Before anything is pushed, you run the tests (output trimmed to the summary):

    @@Q07_RUN@@

    Your teammate says: "The report works, so these tests are out of date. Delete `tests/test_duplicates.py` and push; CI will be green."
    """,
    [
        part("1", "In one sentence, what does this output tell you?", 1,
             "Four tests of `remove_duplicates` now fail because `Expense` is no longer hashable, while 20 tests still pass: the one-line edit broke a function it never touched.",
             ["States that the four failures are all tests of `remove_duplicates`, a function the edit did not touch, while 20 tests pass, and reads the cause from the message: `Expense` is now unhashable"],
             "\"Four tests failed\" only repeats the summary line. Say which function the four tests check, and read the cause from the message, `unhashable type: 'Expense'`, which appeared after the edit. Blaming `remove_duplicates` misses that it did not change: the failures show where the break surfaces, and the edit to `Expense` is where it was made."),
        part("2", "Which failure from session 1 did the tests just expose, and which answer from slide 8 caught it?", 2,
             "\"Change one thing, three others break, silently\": the report still runs, so nothing looked wrong. Testing, from slide 8's \"clean code, testing, TDD\", made the break visible before the push.",
             ["Names \"change one thing, three others break, silently\", tied to the report still working",
              "Names testing (slide 8: clean code, testing, TDD) as what made the break visible before the push"],
             "\"Works on my machine\" is wrong: CI would fail in the same way, because the cause is the edit. \"A teammate breaks the build\" describes what would happen after a push; here the tests caught it first. Naming the failure without saying why it is silent (the report still runs) loses a mark."),
        part("3", "Do you accept deleting the tests to get CI green? Give your reasoning.", 2,
             "No. The tests pin behaviour the program still promises: duplicates dropped, first copy kept. Deleting them hides the break until someone calls `remove_duplicates`, and a green check that runs no tests proves nothing. Fix the cause: restore `frozen=True` and correct a typo by building a corrected `Expense` instead.",
             ["Refuses, because the tests describe behaviour the program still needs (duplicates removed, first copy kept)",
              "Says deleting them hides the break: the crash reaches whoever next calls `remove_duplicates` instead of being caught by CI",
              "Proposes fixing the cause: restore `frozen=True` (revert the edit) and correct typos another way"],
             "\"Yes, the report works\" judges the program by one command and ignores the behaviours the tests pin. \"No, tests are important\" is too vague to score: say what the tests protect and what deleting them would let through. It is the same judgement as refusing `# type: ignore` to get CI green in sample Q9."),
    ],
    """
    This is the teacher's "read tool output" shape (sample Q9) applied to session 1. Read the summary lines first: all four failures are tests of `remove_duplicates`, all with the same `TypeError`, and 20 other tests pass, so a single cause outside that function is the likely story. Session 8 supplies it: `dict.fromkeys` needs hashable items, and `frozen=True` is what made `Expense` hashable. In session 1's terms this is the silent break that testing exists to catch. Deleting the tests would turn CI green by removing the evidence, which is the shortcut the sample paper asks you to refuse.
    """,
    verified="run",
))


# ---- added by the calibration pass ------------------------------------------------------------------
Q.append(mcq(
    51, "exam", ["judgement", "concept"], 8, "S2 slide 13",
    """
    A group writes a detailed ticket for all forty items of its backlog in week 1, with estimates. By week 5 the client has changed their mind and half of the tickets have to be rewritten. Which approach on slide 13 gives the advice that would have saved that work?
    """,
    [
        opt("Kanban: limit the work in progress and pull the next item when there is capacity",
            "Kanban limits how many items are open at once. It says nothing about when to write the details of the items that are not open yet."),
        opt("Lean: eliminate waste and decide as late as responsibly possible",
            "Detailing forty items early, then rewriting half, is waste. Deciding as late as responsibly possible means writing a ticket when the item is about to be built, with the most recent knowledge.", True),
        opt("XP: pair programming, test-driven development, continuous integration and small releases",
            "XP governs how code is written and integrated. The problem here is planning detail that goes stale, not engineering practice."),
        opt("Waterfall: finish the requirements in full before design starts, so that nothing changes later",
            "That is the habit that caused the problem: it assumes the requirements stay put once written. Slide 13 lists Waterfall nowhere among the approaches that follow Agile principles."),
    ],
    """
    Slide 13 lists four approaches that follow Agile principles, and each gives different advice. Lean's is to eliminate waste, optimise the whole flow, and decide as late as responsibly possible. Writing and estimating forty tickets in week 1 is the opposite: detail is created early, when the least is known, and half of it is thrown away. The Product Backlog works the same way (session 4): items near the top are detailed, items near the bottom are left rough, because "estimating item 40 precisely is waste". Kanban and XP are real answers to other problems.
    """,
))

Q.append(mcq(
    52, "exam", ["concept", "judgement"], 7, "S2 slide 12",
    """
    The client of a fortune-cookie app is reachable only through a weekly email. The developers have three questions about how a fortune should be formatted. They wait five days for an answer, guess, and half of the guesses turn out to be wrong. Which principle on slide 12 is the group not following?
    """,
    [
        opt("Technical excellence",
            "The guesses went wrong because nobody answered the questions, not because the code was poorly built."),
        opt("Business and developers, daily",
            "Slide 12, \"expect change; collaborate\": the people who decide and the people who build talk every day, so a question waits hours, not a week.", True),
        opt("Self-organising teams",
            "The developers can organise their own work. The missing thing is the client's answers."),
        opt("Simplicity: maximise work not done",
            "The guessed work was done and wasted, but the cause is the missing conversation, not the amount of work."),
    ],
    """
    Slide 12 groups the twelve principles in four. Under "expect change; collaborate" are "welcome changing requirements" and "business and developers, daily". A weekly email makes every question cost five days, and the team fills the gap with guesses; each wrong guess is rework. The principle names the remedy: daily contact between the people who know what is needed and the people who build it. The course's own set-up points the same way: slide 14 says the Product Owner is the lecturer.
    """,
))

Q.append(mcq(
    53, "core", ["concept"], 4, "S1 slide 20",
    """
    Your group has working code but no tests, and wants to learn how to write the tests that catch a break before users do. According to slide 20, which module is that, and which phases does it sit on?
    """,
    [
        opt("M1 Starting a project, on Idea and Analysis",
            "M1 settles what to build and in what order. The tests come after something exists."),
        opt("M2 Testing and TDD, on Development and Testing",
            "Slide 20 puts testing and TDD with Development and Testing, in the module on clean code and tests.", True),
        opt("M3 Terminal, on Design and Development",
            "M3 is about working in the terminal. It does not teach how to write tests."),
        opt("M5 Docker, on Deployment and Maintenance",
            "M5 is about running the finished program elsewhere. Tests are written well before that."),
    ],
    """
    Slide 20 orders the modules by SDLC phase: Idea and Analysis go with M1 Starting a project; Design and Development with M2 Clean code and M3 Terminal; Development and Testing with M2 Testing and TDD; Testing and Deployment with M4 Git, review and CI; Deployment and Maintenance with M5 Docker. Writing tests is the Development and Testing pair. M4 appears next, because it is where the tests are run on every push, but writing them is M2's job.
    """,
))

Q.append(mcq(
    54, "core", ["concept", "judgement"], 1, "S1 slide 5",
    """
    Two students hand in a program that prints the right dining total today. Ana's is one file with no tests, and works only on her laptop. Bo's is a project with a `pyproject.toml`, a lockfile, tests and a check that runs on every push. Using slide 5's definition of software engineering, what do you say?
    """,
    [
        opt("Bo's has more of what the definition asks for: software that stays reliable and easy to maintain over time",
            "Slide 5 says the aim goes \"beyond just writing code\": programs that are reliable and easy to maintain over time. A shared environment, tests and a check on every push are how that is done.", True),
        opt("Ana's is better engineered, because a single file is the simplest thing that works",
            "Simple is good, but slide 5's aim is reliability and maintainability over time. One file that works on one laptop is neither."),
        opt("They are equal, because the program prints the same total",
            "The same output today says nothing about next month, a new teammate or a different laptop. The definition looks past the first run."),
        opt("Bo's is better only if it has more features than Ana's",
            "Features are not part of the definition. It asks for a systematic process and software that lasts."),
    ],
    """
    Slide 5 defines software engineering as "the systematic process of designing, developing, testing, and maintaining computer software using scientific and engineering principles", and says it "goes beyond just writing code": programs that are reliable, secure, efficient and easy to maintain over time. Both programs print the same total, so the difference is everything around the code. Bo's project can be installed from the lockfile by anyone, has tests that notice a break, and is checked on every push. Ana's can only be judged by running it on her laptop today.
    """,
))

# ---------------------------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------------------------

MODULE: dict[str, Any] = {
    "id": MID,
    "order": 1,
    "module": "M1",
    "title": "The lifecycle, Waterfall and Agile",
    "sessions": [1, 2],
    "predicted": False,
    "sources": [
        "slides-session-1",
        "slides-session-2",
        "slides/image-only-slides.md",
        "moodle/project-pages.md (workshop brief, card sort, backlog brief)",
        "slides-session-4 (Definition of Done, what Scrum does not give you)",
        "expense-tracker v0.0..v0.2 (3e0834f–f3bb801)",
        "sandbox at v0.4 (runs for q06, q07, q50)",
    ],
    "summary_md": md(
        """
        Sessions 1 and 2 set the frame for the whole course. Software engineering is a systematic process, not just writing code, and this is "not a Python course": it is about what happens to a program once teammates are involved. You learn the ways working code still fails and the practice that answers each, the seven phases of the software development lifecycle on the expense tracker, and why software is maintained far longer than it is written. Session 2 then compares Waterfall and Agile: where each genuinely works, how to read the Agile Manifesto correctly, what Scrum, Kanban, XP and Lean prescribe, and which parts this course borrows.
        """
    ),
    "exam_focus_md": md(
        """
        - A short team story: name the failure from session 1's slide 6 and the answer from its slide 8 (Agile and Scrum; clean code, testing, TDD; version control, review, CI; containers and automatic deployment).
        - Four changes to a program: which one is the refactoring, the bug fix, the feature or the tech debt (the shape of sample Q2).
        - A decision or artefact (a feature table, a sketch of the structure, a checklist): which SDLC phase it belongs to, and which decisions reach more than one phase.
        - A project scenario (a regulated fixed-price contract, a start-up, a support desk): which approach fits and why, argued from session 2's slides 6, 7 and 13.
        - A teammate's reading of the Agile Manifesto ("so we skip the README"): what the values actually rank.
        - Open, 5–8 lines: compare Waterfall and Agile for a given project, including a usable first iteration and one real downside of Agile.
        - Combined with later sessions: a pytest or uv transcript in which you name the session 1 failure it shows.
        """
    ),
    "sections": SECTIONS,
    "terms": [{"term": t, "definition_md": d, "section_ref": sid(s)} for t, d, s in TERMS],
    "traps": TRAPS,
    "flashcards": [
        {"id": f"{MID}-f{i:02d}", "front_md": f, "back_md": b, "kind": k, "section_ref": sid(s)}
        for i, (f, b, k, s) in enumerate(CARDS, start=1)
    ],
    "questions": Q,
}


def main() -> None:
    with OUT.open("w", encoding="utf-8") as fh:
        json.dump(MODULE, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    mcqs = [q for q in Q if q["type"] == "mcq"]
    pos = [next(i for i, o in enumerate(q["options"]) if o["correct"]) for q in mcqs]
    counts = {letter: pos.count(i) for i, letter in enumerate("abcd")}
    levels: dict[str, int] = {}
    for q in Q:
        levels[q["level"]] = levels.get(q["level"], 0) + 1
    print(f"wrote {OUT.name}: {len(Q)} questions, correct positions {counts}, levels {levels}")


if __name__ == "__main__":
    main()
