"""Generate CRAM/types/T10.json: Process: lifecycle, Agile and Scrum.

Run: python3 "types/src/T10.py"   (standard library only; writes ../T10.json next to this folder)

The worked examples copy their question text verbatim from the verified bank (SITE/content/*.json),
so no stem or option is retyped by hand. Every practice id is checked against pools.json["pools"]["T10"].
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRAM = HERE.parent.parent
SITE = CRAM.parent / "study-site"
OUT = HERE.parent / "T10.json"

bank: dict[str, dict] = {}
for module in ("sdlc-agile", "scrum"):
    for q in json.loads((SITE / "content" / f"{module}.json").read_text())["questions"]:
        bank[q["id"]] = q


def mcq_text(qid: str) -> str:
    q = bank[qid]
    lines = [q["stem_md"].strip(), ""]
    for letter, opt in zip("abcd", q["options"]):
        lines.append(f"- {letter}) {opt['text_md']}")
    return "\n".join(lines)


def open_text(qid: str) -> str:
    q = bank[qid]
    lines = [q["stem_md"].strip(), ""]
    for part in q["parts"]:
        lines.append(f"{part['label']}. {part['prompt_md']}")
    return "\n".join(lines)


B1 = """Session 1 defines software engineering as "the systematic process of designing, developing, testing, and maintaining computer software". Writing code is one part. The course uses seven phases, shown on the expense tracker.

| Phase | Decided or done there |
|---|---|
| Idea | Who uses it, what problem it solves |
| Analysis | Everything it will do: the feature table (add, list, summary by category) |
| Design | How the pieces connect, how a user moves through it |
| Development | The build, from the design |
| Testing | A checklist against the analysis, run every time, not once |
| Deployment | Someone who is not the author can use it |
| Maintenance | Fix, improve, keep running. Forever |

Development comes late: three phases happen before anyone types code. Analysis is what the app does. Design is how the pieces connect.

Four kinds of change send the cycle back to Design.

| Change | How to tell |
|---|---|
| Bug | Behaviour nobody intended, found later |
| Feature | New behaviour: users can do something they could not before |
| Refactor | The inside changes, what users get stays the same |
| Tech debt | A weaker solution chosen on purpose, with the cost known |

Session 1 words the refactor as software that connects to new components that replace old ones, or runs on a different device. Session 7 gives the test: change the structure, keep the behaviour.

Session 1's slide 8 pairs each failure with its answer. No shared plan: Agile, Scrum. Unreadable or silently breaking code: clean code, testing, TDD. A teammate's change breaks the build: version control, review, CI. "Works on my machine": containers, automatic deployment.

Slide 20 lines the modules up with the phases: M1 Starting a project (Idea, Analysis); M2 Clean code and M3 Terminal (Design, Development); M2 Testing and TDD (Development, Testing); M4 Git, review, CI (Testing, Deployment); M5 Docker (Deployment, Maintenance)."""

B2 = """Waterfall runs five phases once, in order, each finished before the next begins. Requirements gives a signed specification, Design architecture documents, Implementation code, Testing a test report, Deployment and maintenance a running system. The gate between phases is a document that gets approved.

It works when requirements are known and stable: bridges, aircraft, fixed-scope fixed-price contracts, regulation that demands documentation. Software breaks Waterfall's assumptions in three ways. Requirements change (normal, not a failed analysis). Feedback arrives too late, because testing is near the end. Integration risk piles up, because parts are first combined at the end.

Agile (2001) answers with short cycles: Plan, Build, Review with user, Learn. The same phases happen in every cycle, on a small slice. Change is expected, testing is in every cycle, users are involved often.

The Manifesto has four values: individuals and interactions over processes and tools; working software over comprehensive documentation; customer collaboration over contract negotiation; responding to change over following a plan. The closing line says there is value on the right and the left is valued more. It ranks; it bans nothing. The twelve principles fall in four groups: deliver value continuously; expect change and collaborate; trust people and keep a sustainable pace; keep improving.

| Approach | Prescribes | Best when |
|---|---|---|
| Scrum | Sprints, three roles, planning, daily, review, retrospective | Feature work, team of 10 or fewer |
| Kanban | Board, work-in-progress limit, pull when free | Steady stream of varied requests |
| XP | Pair programming, TDD, CI, small releases | Quality and change rate both high |
| Lean | Eliminate waste, decide late | Cutting cycle time end to end |

The course uses Scrum words (checkpoints are Sprints), XP practices and a Kanban board. Borrow what helps; follow no method blindly."""

B3 = """Scrum is the most used way of working in short cycles, and the most commonly misapplied. It answers a year-long plan, written before anything is built, on estimates nobody can make.

| Role | Accountable for |
|---|---|
| Product Owner | The value of the product. Owns and orders the Product Backlog. One person, not a committee |
| Scrum Master | Ensures the process works, removes impediments, coaches. Not a manager |
| Developers | Building the Increment. Cross-functional, self-managing |

Ideally ten people or fewer, with hierarchy as horizontal as possible. The team decides how the work is done and who does what. The Product Owner decides what is worth doing, and in what order. Nobody outside decides how much goes into a Sprint.

Each artifact makes something visible and has a commitment. Without it, it is just a list.

| Artifact | Commitment |
|---|---|
| Product Backlog | Product Goal |
| Sprint Backlog | Sprint Goal |
| Increment | Definition of Done |

The Product Backlog is ordered, emergent and never finished. Top is next, ordered by value, detailed only near the top, because estimating item 40 precisely is waste. An item is an outcome, not a task: `As a <kind of user>, I can <do something>, so that <benefit>`. "Do the CSV part" is a task. "Write tests" is a standard.

The Definition of Done is the quality bar every Increment meets, decided once, applied to everything. An item that misses it is not done and does not ship. "Done except for tests" is not admissible. Write it as things you can check. In the course it is a green CI check."""

B4 = """Time-boxes for a two-week Sprint. A shorter Sprint means proportionally shorter events.

| Event | Time-box | Question |
|---|---|---|
| Refinement | ~4h | PO and Developers discuss implementation details of items near the top |
| Sprint Planning | 1h | What will be delivered at the end of the Sprint? |
| Daily | 15 min | Are we on track for the Sprint Goal? |
| Sprint Review | 1h | What was built; what should change? |
| Retrospective | 1h | How did the team work; what to improve? |

What they are not. The Daily is not a status report to a manager: fifteen minutes, for the Developers, each stating latest work, next work and blockers. The PO may join but is not expected to take part. The Review is not a demo for applause: stakeholders give feedback and change the backlog. The Retrospective is not blame: what worked, what did not, what to change. The PO can cancel a Sprint; it almost never happens.

Pillars: transparency, inspection, adaptation. Values: commitment, focus, openness, respect, courage. Inspection without transparency inspects a fiction. Adaptation without courage produces the same Sprint, twelve times.

Scrum gives no requirements document, no promise about version 1.0, and no architecture, testing strategy or engineering practices. Scrum organises the work; it does not do it.

In the course: Sprint = stretch between checkpoints. Sprint Goal = the checkpoint's deliverable. Definition of Done = a green CI check, the referee. PO = the lecturer. Developers = your group. Review = practice sessions and Demo Day."""


type_file = {
    "tid": "T10",
    "name": "Process: lifecycle, Agile and Scrum",
    "shape_md": (
        "The nine sample questions contain none on process, yet the teacher lists \"starting a project\" first among the topics of the paper. "
        "Expect a short scenario about a team with four options (a Scrum meeting gone wrong, a backlog, a Definition of Done, a Waterfall plan), "
        "or a part of an open answer in 5–8 lines."
    ),
    "minutes": 40,
    "one_md": (
        "Match the story to the course's own term (a lifecycle phase, a Waterfall or Agile reason, a Scrum role, event or commitment) "
        "and judge the team by that term's rule, however professional it sounds."
    ),
    "spot_md": (
        "- The story is about people and meetings, not code: a group, a client, a bank, a Daily that overran. It carries a number (15 minutes, forty items, day 6 of a two-week Sprint) or a quoted belief.\n"
        "- The question reads \"which description fits best\", \"what is wrong, in session 4's terms\", \"which failure from session 1\", \"what follows from the Definition of Done\" or \"which approach from slide 13\".\n"
        "- The options swap neighbours: Product Owner and Scrum Master, Review and Retrospective, Refinement and Planning, Analysis and Design, Scrum and Kanban or XP.\n"
        "- A manager or teammate states the wrong belief (\"it's done apart from one test\", \"we are Agile, so no planning\"). You judge the belief.\n"
        "- The open version has 2–4 parts: name the problem, say which rule it breaks, say what to do instead."
    ),
    "basics": [
        {"id": "T10-b1", "heading": "The seven phases and the four kinds of change", "body_md": B1},
        {"id": "T10-b2", "heading": "Waterfall, Agile and the four approaches", "body_md": B2},
        {"id": "T10-b3", "heading": "Scrum: roles, artifacts, the backlog and Done", "body_md": B3},
        {"id": "T10-b4", "heading": "Scrum events, pillars and what Scrum leaves out", "body_md": B4},
    ],
    "checks": [
        {
            "id": "T10-c1",
            "q_md": "Which of these is tech debt?",
            "options": [
                "The report crashes on a CSV with a blank line, and nobody had noticed",
                "The long `report` function is split in two, with the same output and every test unchanged",
                "Personal bests go in a text file to reach CP1, with a backlog note to move them to CSV",
                "A new `--month` option lets users report on just one month of spending",
            ],
            "answer": 2,
            "why_md": "Tech debt is a weaker solution chosen on purpose, with the cost known and written down. The crash is a bug, the split a refactor, `--month` a feature.",
        },
        {
            "id": "T10-c2",
            "q_md": "Session 1 says that three phases happen before anyone types code. Which three?",
            "options": [
                "Idea, Analysis and Design",
                "Analysis, Design and Development",
                "Idea, Design and Testing",
                "Design, Development and Testing",
            ],
            "answer": 0,
            "why_md": "Idea, Analysis and Design are phases 1 to 3. Development is the fourth, so it arrives comparatively late: a lot of thinking comes before the code itself.",
        },
        {
            "id": "T10-c3",
            "q_md": "A Waterfall project has just finished Requirements. What lets it move into Design?",
            "options": [
                "A user tries a first working version and gives feedback",
                "The specification is approved and signed off",
                "The CI check turns green",
                "The Product Owner reorders the backlog",
            ],
            "answer": 1,
            "why_md": "In Waterfall the gate between phases is a document that gets approved. User feedback on a working version, CI and a reordered backlog are Agile, XP and Scrum ideas.",
        },
        {
            "id": "T10-c4",
            "q_md": "A group's Definition of Done starts with \"The CI check is green\". Rosa's item passes every test on her laptop, but the Types step of CI is red. What follows?",
            "options": [
                "Done: every test passes, and the Types step is only a style check",
                "Done, if the Product Owner agrees to an exception this once",
                "Not done: the check is red, so the item misses the Definition of Done",
                "Re-run CI until it turns green, then count the item as done",
            ],
            "answer": 2,
            "why_md": "An item that misses the Definition of Done is not done and does not ship. The Types step is part of the same check, and re-running gives the same red because the cause is in the code.",
        },
        {
            "id": "T10-c5",
            "q_md": "Which sentence about the Daily Scrum matches session 4?",
            "options": [
                "It is a weekly status report from each developer to the head of department",
                "It is the hour in which stakeholders try the product and give feedback",
                "It is where the Product Owner reorders the backlog for the next Sprint",
                "It is a fifteen-minute check by the Developers on the Sprint Goal",
            ],
            "answer": 3,
            "why_md": "The Daily is fifteen minutes, for the Developers, and it is not a status report to a manager. Feedback belongs to the Review, backlog order to the Product Owner.",
        },
    ],
    "method": [
        "Read the last sentence first, then the story. Mark the one fact that carries the weight: a role (who spoke), a number (15 minutes, forty items, day 6), a red CI check, or a quoted belief.",
        "Name the course term the story is about: a lifecycle phase, one of session 1's failures, a Waterfall reason (requirements change, feedback too late, integration risk), a Manifesto value, an approach from slide 13, or a Scrum role, artifact, event or pillar.",
        "Recall that term's one-line rule from the slides. Test the story against it: who decided what, how long it took, what was shown, what was checked.",
        "Cross out the careless moves: swapping neighbours (Product Owner and Scrum Master, Review and Retrospective, Analysis and Design), blaming the wrong thing, or treating the symptom (silencing the check, re-running CI, adding a meeting).",
        "If the story is about \"done\", apply the Definition of Done literally. Red CI means not done. \"Done except for tests\" is not admissible.",
        "In an open answer, give each part three things in order: the course term, the sentence in the story that shows it, and what to do instead. Stay within 5–8 lines.",
    ],
    "worked": [
        {
            "title": "Scenario judgement: Scrum in name only",
            "question_md": mcq_text("scrum-q02"),
            "steps_md": [
                "Last sentence first: \"Which description fits best?\" You are naming what the company is really doing.",
                "Collect the facts. The weekly status meeting is renamed the Daily, still takes an hour, and each person reports to the department head. The head is now called Scrum Master. The eighteen-month plan from January is unchanged. Nothing is shown to users until it is complete.",
                "Test each fact against session 4. The Daily is fifteen minutes, for the Developers, and not a status report to a manager. The Scrum Master is not a manager. A long plan written before anything is built, with no feedback until the end, is the problem Scrum answers.",
                "Test the options. Option a counts the names as Scrum. Option b says Kanban, but there is no board and no work-in-progress limit. Option c says a longer Daily is normal in a large company, but time-boxes scale with Sprint length, not company size, and the Daily is never a status report to a manager. Option d says Scrum's names on top of a Waterfall plan.",
            ],
            "answer_md": (
                "**d.** Only the vocabulary changed. There are no short cycles, no working software and no feedback, so the plan is still Waterfall. "
                "Session 4 calls Scrum the most commonly misapplied way of working in short cycles, and slide 14 names the tendency to imitate Agile by mocking the Scrum ceremonies."
            ),
        },
        {
            "title": "Open answer: two scenes from a Sprint",
            "question_md": open_text("scrum-q42") + "\n\nAnswer in 5–8 lines.",
            "steps_md": [
                "Part 1 asks for definitions, so write each ceremony's question from slide 11: Review, \"what was built; what should change\"; Retrospective, \"how the team worked, and what to improve\".",
                "Part 2 asks what went wrong, so use the slide 12 labels: the Review is not a demo for applause, the Retrospective is not blame. Tie each label to the sentence that shows it (\"Nobody asks them anything\", \"ends when Iker apologises\").",
                "Part 3 asks for a change, so give one that could be checked at the next Sprint. The Review change must produce feedback or a backlog change. The Retrospective change must be about the process, not a person.",
                "Count the lines. Three parts at two lines each fit inside 5–8.",
            ],
            "answer_md": (
                "1. The Review asks what was built and what should change: stakeholders give feedback that changes the backlog. The Retrospective asks how the team worked and what to improve.\n"
                "2. The Review became a demo for applause: nobody asked for feedback, so the backlog could not change. The Retrospective became blame: it found a culprit, got an apology and decided nothing.\n"
                "3. Review: ask the users what confused them and what they want next, and let the Product Owner reorder the backlog from the answers. "
                "Retrospective: ask why a broken push could reach `main`, and agree a team rule, such as running ruff, mypy and pytest before every push."
            ),
        },
    ],
    "twists": [
        {
            "twist_md": "A Daily where a manager runs the meeting, or the Product Owner takes over, or it runs for forty minutes.",
            "how_md": "The Daily is fifteen minutes, for the Developers: latest work, next work, blockers, about a minute each. It is not a status report to a manager. The PO may join but is not expected to take part. A blocker gets one sentence at the Daily. Solving it takes longer than a one-minute turn, so it happens afterwards, with whoever the team chooses. Name every rule broken: the report, the time-box and who decides who does what.",
        },
        {
            "twist_md": "The Sprint length changes: one week or four weeks instead of two. How long is the Review or Planning?",
            "how_md": "Start from the two-week row and scale. Shorter Sprint, proportionally shorter events. A one-week Review is about 30 minutes, a four-week one about two hours.",
        },
        {
            "twist_md": "CI is red but the item is \"basically finished\", or someone proposes `# type: ignore`, skipping a test, or re-running CI until it passes.",
            "how_md": "Red CI means the Definition of Done is not met: the item is not done and does not ship. Silencing the check makes it green and false, so the Review inspects a fiction (no transparency). The honest options are to fix the code or to say at the Review that the item is not done.",
        },
        {
            "twist_md": "A backlog line is a task, a standard or a wish: \"Do the database part\", \"Write tests\", \"Make it good\". You are asked why it is not an item, or to rewrite it.",
            "how_md": "An item is an outcome a user gets, small enough to finish in a sitting, and you can tell when it is done. A task becomes what a user can do. A standard for every item (tests, README) goes to the Definition of Done. A wish becomes something checkable: slide 30 turns \"Make it good\" into \"Invalid input prints a message and exits non-zero\". Keep the \"so that\": it stops you building something nobody needs.",
        },
        {
            "twist_md": "A client wants a signed requirements document, a fixed price and a promise of what version 1.0 contains. Which approach, and what does each side give up?",
            "how_md": "Waterfall fits known, stable requirements, fixed scope and price, and regulation that demands documentation. Scrum gives no requirements document and no promise about 1.0, because the backlog is emergent. Name a real cost of Agile: less certainty about final scope, a harder fixed price, more coordination. Whichever the team picks, session 2's advice holds: borrow the practices that help, and follow no method blindly.",
        },
        {
            "twist_md": "A team holds every ceremony and keeps a tidy board, yet has no tests, a red CI and an install that fails.",
            "how_md": "Scrum organises the work; it does not do it, and it gives no engineering practices. Say what is missing: no Increment met the Definition of Done, the Reviews inspected a fiction (transparency), the Retrospectives lacked courage. The fix is to borrow XP: a test for each behaviour, CI, small commits, and nothing counted as done while CI is red.",
        },
        {
            "twist_md": "Someone quotes the Manifesto to drop documentation, planning or contracts.",
            "how_md": "Quote the closing line: there is value in the items on the right, and the items on the left are valued more. It ranks; it bans nothing. Then say what the team still does: plans in every cycle, keeps a README that lets a stranger run the program, keeps the contract but works with the customer.",
        },
        {
            "twist_md": "A story must be placed among the twelve principles, such as a client reachable only by weekly email, or a week spent on a plugin system nobody asked for.",
            "how_md": "The four groups are: deliver value continuously; expect change and collaborate; trust people and keep a sustainable pace; keep improving. The weekly email breaks \"business and developers, daily\". The plugin system breaks \"simplicity: maximise work not done\", even if the author cites \"welcome changing requirements\", which is about changes that have arrived.",
        },
    ],
    "traps": [
        "**\"The Scrum Master is a manager who assigns tasks, collects reports or approves work.\"** The role ensures the process works, removes impediments and coaches. It is not a manager.",
        "**\"The Product Owner is a committee, or decides who builds an item and how.\"** It is one person who decides what is worth doing and in what order. The Developers decide how and who.",
        "**\"The Review and the Retrospective are the same meeting.\"** Both come at the end of the Sprint. The Review is about the product (what was built, what should change, the backlog). The Retrospective is about how the team worked.",
        "**\"In the Manifesto, over means instead of.\"** The right-hand items keep their value. Agile still plans in every cycle, still documents what helps, still has contracts.",
        "**\"Every team failure is works on my machine.\"** That means it runs on one machine only. A change that breaks the build for everyone is \"a teammate's change breaks the build\", answered by version control, review and CI.",
        "**\"Done except for tests, nearly done or green on my laptop counts as done.\"** An item that misses the Definition of Done is not done and does not ship.",
        "**\"Scrum gives a team its engineering.\"** It gives no requirements document, no promise about version 1.0, no architecture, no testing strategy and no engineering practices. The course takes those from XP.",
        "**\"The feature table belongs under Design.\"** The feature table is Analysis (what the app does). Design is how the pieces connect and how a user moves through it.",
    ],
    "say_md": (
        "- Scrum organises the work; it does not do it.\n"
        "- Product Owner: one person, not a committee. Owns and orders the Product Backlog. Decides what is worth doing, and in what order.\n"
        "- The Developers are cross-functional and self-managing: they decide how the work is done and who does what.\n"
        "- Scrum Master: ensures the process works, removes impediments, coaches. Not a manager.\n"
        "- Nobody outside decides how much goes into a Sprint.\n"
        "- Commitments: Product Backlog → Product Goal; Sprint Backlog → Sprint Goal; Increment → Definition of Done.\n"
        "- Definition of Done: the quality bar every Increment meets, decided once, applied to everything. An item that misses it is not done and does not ship. Things you can check, not things you can hope.\n"
        "- In this course the Definition of Done is a green CI check: the referee, not the judge.\n"
        "- Daily: fifteen minutes, for the Developers, not a status report to a manager. Review: feedback that changes the backlog, not a demo for applause. Retrospective: how the team worked and what to improve, not blame.\n"
        "- Transparency, inspection, adaptation. Inspection without transparency inspects a fiction. Adaptation without courage produces the same Sprint, twelve times.\n"
        "- Waterfall: linear, sequential phases; the gate between phases is an approved document. It fails for software: requirements change, feedback arrives too late, integration risk piles up.\n"
        "- Agile: iterative, incremental, adaptable. Plan, build, review with user, learn. The same phases happen in every cycle, on a small slice.\n"
        "- While there is value in the items on the right, we value the items on the left more.\n"
        "- Bug: unintended. Feature: new behaviour. Refactor: change the structure, keep the behaviour. Tech debt: a deliberate shortcut, with the cost known.\n"
        "- Borrow the practices that help you iterate fast and deliver value; do not follow one methodology blindly."
    ),
    "practice": [
        "sdlc-agile-q11",
        "scrum-q03",
        "scrum-q46",
        "sdlc-agile-q15",
        "sdlc-agile-q26",
        "scrum-q06",
        "scrum-q13",
        "scrum-q30",
        "sdlc-agile-q48",
        "sdlc-agile-q42",
        "sdlc-agile-q23",
        "sdlc-agile-q07",
        "scrum-q26",
        "scrum-q52",
    ],
}

pool = {q["id"] for q in json.loads((CRAM / "pools.json").read_text())["pools"]["T10"]}
missing = [i for i in type_file["practice"] if i not in pool]
assert not missing, f"not in pools['T10']: {missing}"
assert len(set(type_file["practice"])) == len(type_file["practice"]), "duplicate practice id"

OUT.write_text(json.dumps(type_file, ensure_ascii=False, indent=1) + "\n")
print(f"wrote {OUT}")
