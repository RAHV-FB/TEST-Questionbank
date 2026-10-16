# Moodle pages for the group project (verbatim text)

## Instructions — Project Brief

What you are building
A terminal program, written in Python, built by a group of four, over eleven weeks.
No web app. No graphical interface. No mobile. That is not a limitation to work around - it is the point. Stripping away the interface leaves the parts this course is actually about: does it install, does it hold together, can four people change it at once, does it run on a machine that is not yours.

The bar is not "does it work on my laptop". It is:
- A stranger can install and run it, from your repository, with no help from you
- A type checker accepts it
- It has tests, and they pass on a machine none of you owns
- Four people edited it all term without breaking each other's work
- It runs inside a container on a computer with no Python installed

Topics: None of the fifteen topics below is hard to *write*. The point is to implement the above, to bring the code to that standard.
Mini Bingo; Fortune Cookie Generator; Text Adventure; Dice Dungeon; Task manager; Habit tracker; Vending machine (stock, coins, change-making); Parking lot (spaces, tickets, duration-based pricing); Gradebook (weighted assignments, grade boundaries); Library inventory manager (checkouts, due dates, overdue fines); Flashcard trainer (Leitner-box spaced repetition); Meal planner (recipes scaled by servings, shopping list); Gym workout logger (personal bests); Public transport fare calculator (zones, travelcards, cheapest way to cover a week); Movie watchlist.
During the course, the teacher builds an expense tracker in parallel as an example project.

Choosing well: Topics 7, 8, 9, 10 and 14 have rules in them - change-making, pricing bands, weighted averages, fare zones. Rules are easy to get subtly wrong and easy to test, which makes them generous when we get to testing in module 2.

Your repository is public. Three reasons: a portfolio piece; it makes copying visible rather than tempting; it makes the tooling free (automated checks and container hosting cost nothing on public repositories). Beware: do not ever put anything personal in the repository. No credentials, no keys, no data about real people. "I deleted the file" does not remove it from a repository's history.

How it is marked: CP1 scaffold and CLI (S5, 5%), CP2 tests (S8, 5%), Partial submission (S10, 30%), CP3 branches (S12, 5%), CP4 review and pull requests (S14, 5%), Final submission + demo (S18–19, 50%). Checkpoints are a three-item checklist, scored 0, 2.5 or 5. Every checkpoint is a git tag in your repository. An automated check runs on every push and must be green — it is not marked itself, but a red check means the submission is not mechanically valid. "Think of it as the referee, not the judge." Submitting is mandatory. Late is zero.

Demo day: Session 19. Nine minutes per group. Your program runs on my machine, pulled from the container image your repository published. Nothing is built on the day and nothing is installed by hand. If it only runs on your laptop, it does not run.

## 2026-09-22 Brief: Product Backlog and Definition of Done

1. Product Backlog — at least eight items, ordered.
An item is an outcome a user gets, not a task you perform. It is small enough to finish in a sitting, and you can tell when it is done.
Order them by value: the top of the list is what you build next. Only the top three need detail — the rest will change, and detailing them now is wasted work.
The shape: As a <kind of user>, I can <do something>, so that <benefit>.
The "so that" is the part that stops you building something nobody needs.

Three worked examples, from the expense tracker:
1. As a user, I can see a total per category, so that I know where the money went — "The first thing it ever did"
2. As a user, I can report on one category only, so that I can look at dining without the noise — "Became --category"
3. As a user, I can add an expense from the command line, so that I do not edit a CSV by hand — "Became expenses add"

And three that are not usable as items:
- "Do the CSV part" — A task, not an outcome. Nobody can tell when it is done
- "Make the code good" — Not checkable. Quality belongs in the Definition of Done
- "Write tests" — Same: every item is tested, so it is a standard, not a backlog entry

2. Definition of Done. The bar every item meets. One list, applied to everything. Write it as things you can check, not things you can hope.
Starter list (edit it, do not copy it):
- The code runs from a clean clone: uv sync && uv run <your-app> --help
- The CI check is green
- There is at least one test for the new behaviour
- Bad input prints a message and exits non-zero
- The README says how to use the new behaviour
- Another member of the group has read the change
Cut what you will not honour. A Definition of Done with six items you ignore is worse than three you keep.
The one that is not yours to choose: A green CI check is in every group's Definition of Done. It is the same check for all fourteen groups, it runs on a machine none of us owns, and it is the referee all term.

## 2026-09-15 Activity: plan, then re-plan (session 2 workshop)

Pick an idea (bill-splitting app, student club website, vending machine software, a game).
Part 1 — plan it as Waterfall: five phases (Requirements, Design, Implementation, Testing, Deployment & Maintenance); for each phase 2–3 bullets: what the group would do and what document or artefact it produces. Rule of the game: once a phase is "done", it is signed off. You are not allowed to go back and change an earlier phase without a formal change request.
Part 2 — re-plan it as Agile: 1. What is the smallest version a real person could actually use? (Not a prototype but something that works, even if it does almost nothing.) That is your first iteration. 2. The next two or three iterations, each a small usable improvement. 3. Where do you show the work to a user and get feedback? 4. What did switching cost you? (Less up-front certainty about final scope? Harder to quote a fixed price? More coordination overhead?) Name at least one real downside; Agile is not free.
Present: where did the two plans diverge first? Which one would you rather be running in month six, and why?

## Session 1 activity: card sort ("The coffee shop")
Small groups get a stakeholder brief, three constraint cards, the seven SDLC phases, and fourteen decision cards. Drag every card under the phase where that decision actually gets made. Then answer: 1. Which decisions affect more than one phase? 2. Which trade-offs only become visible once the whole board is laid out? (The deck itself is on SharePoint and not available to us.)
