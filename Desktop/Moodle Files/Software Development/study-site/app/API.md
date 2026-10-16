# App API: the contract for view builders

The page is one HTML file. `tools/build.py` inlines `app/styles.css`, every `app/css/*.css`,
`app/shell.html`, the content data blob and the scripts listed in `app/js/ORDER`. There is no
bundler and no framework: each script is a plain browser script that adds one member to the
global namespace `SD` (declared in `sd.js`). Read `brief/APP.md` and `brief/DESIGN.md` first; this
file says how to plug a view into what exists.

## Adding a view (Exam, History, Terminal lab)

1. Create `app/js/view-<name>.js`. Wrap it in an IIFE and register its route:

   ```js
   (() => {
     const { h } = SD.dom;
     SD.router.register("exam", {
       render({ root, args, route }) {
         root.append(h("div", { class: "page" }, h("h1", { text: "Exam" })));
         return { title: "Exam" };
       },
     });
   })();
   ```

2. Add its file name to `app/js/ORDER` at the end of the views group (the build fails if a
   `.js` file is missing from ORDER or listed but absent). Pure logic used by the view goes in its
   own file in the first group of ORDER (after `data.js`), with no DOM access, so it can be
   unit-tested.
3. Every route the shell links now has its view (exam, history and labs included), so the
   placeholder file is gone; a route nobody registered shows "Nothing at this address".
4. Put the view's CSS in its own `app/css/<name>.css` (appended after `styles.css` in name
   order). Reuse the tokens and shared classes below; never redefine tokens.
5. The shell already links `#exam`, `#history` and `#labs` (top nav, phone tab bar, More page).
6. Run `uv run python tools/build.py --fixture`, `node --test tests/`, and look at the page.

### render(ctx) and what it returns

`ctx = {root, args, route}`: `root` is the emptied `<main>`, `args` the route tokens after the
view name (`#exam.paper-b` gives `["paper-b"]`), `route` the whole route text (`exam.paper-b`).
Return an object (every key optional):

| key | meaning |
|---|---|
| `title` | document title prefix |
| `resume` | label for Home's "Continue" button; the route is remembered as the last place |
| `onKey(event)` | single-key shortcuts; return `true` when the key was used (the router calls `preventDefault`) |
| `cleanup()` | runs before the next render: clear intervals, unsubscribe store listeners |
| `live` | `true` redraws the page in place when synced progress from another device replaces the state; only for pages without typing or a session in progress |

The router opens a page at the top (Back and Forward return to the scroll position the history
entry remembers, kept in `history.state`; where the viewer does not allow that, pages open at the
top), focuses the page's `h1` (every page needs exactly one), marks the nav, and catches render
errors (shown in the page, logged once). `main.js` passes keys to `onKey` only when the user is
not typing in a text field, and leaves Enter and Space alone on links, buttons and checkboxes;
Enter is also ignored while focus is on a page heading or a code block (where focus rests on
arrival), so a stray Enter never answers anything. `?` (shortcuts panel) and Escape are global.
Arrow keys that the page uses (previous/next) must give way to a focused scrollable region:
`if (SD.dom.inScroller(event)) return false`. If your view adds keys, add a line to the shortcuts
list in `app/shell.html`.

A view that moves focus after an action (a button that disappears) should move it to the result:
`SD.dom.reveal(el)` makes it focusable, focuses it and scrolls it into view.

## Routes

Hash routes are tokens joined by `.`; each token matches `[A-Za-z0-9_~-]+` (the Artifact viewer
passes nothing else). Never put user text in a route.

| route | owner |
|---|---|
| `#home`, `#plan`, `#glossary`, `#more` | foundation |
| `#learn`, `#learn.<module>`, `#learn.<module>.s<n>`, `#learn.<module>.end` | foundation |
| `#practice`, `#practice.<mode>[.<scope>[.<type>]]`, `#q.<question id>`, `#q.<question id>.review` | foundation (`.review` is the question's explanation, read-only) |
| `#cards`, `#cards.<module>` | foundation |
| `#exam`, `#exam.<paper id>`, `#exam.sample`, `#exam.bank`, `#exam.attempt.<attempt id>` | Exam (plan and Home link `#exam`, `#exam.sample`, `#exam.paper-a` … `#exam.paper-d`). `#exam.<paper>` is the rules screen; `#exam.attempt.<id>` is one sitting: the answer paper while it runs, its results once handed in |
| `#history`, `#history.<hash>`, `#history.guess`, `#history.guess.<hash>` | History view (plan links `#history`) |
| `#labs`, `#labs.pipes`, `#labs.pipes.<pipeline id>`, `#labs.perms`, `#labs.paths`, `#labs.chains`, `#labs.lab10` | Terminal lab (plan links `#labs`); `#labs.lab10` is "Lab 10, solved", the wrangling lab answered step by step on the real `expenses.csv` |

Practice modes: `next10`, `weak`, `new`, `sample`; scope: `all`, a module id or a section id;
type: `any`, `mcq`, `open`, `sort`. Example: `#practice.weak.testing-tdd.open`.

- `SD.route.parse(hash)` → `{view, args, route}`, `null` for a hash with other characters.
- `SD.route.build(...tokens)` → `"learn.scrum.s2"` (throws `TypeError` on a bad token);
  `SD.route.href(...tokens)` → `"#learn.scrum.s2"`.
- `SD.router.go(route)` navigates (hash write in try/catch; the route is also kept in memory);
  `SD.router.refresh()` re-renders the current route (use it to step through a session).

## Content: `SD.data`

Built by `SD.indexContent(raw)` from the build's blob. Content arrives as in `brief/SCHEMA.md`
with these changes made by the build and the index:

- every `*_md` key is replaced by `*_html` (trusted build-time HTML, code already highlighted);
  `key_points`, `traps` and each part's `rubric` are lists of HTML strings; sections also have
  `heading_html` and terms `term_html`;
- each section gets `mid` (module id), `index` (0-based), `token` (`"s3"`) and `plain` (its heading
  without the backtick code marks, for titles, tooltips and option text);
- each question gets `mid` (its module, or `module_ref` for a paper question) and, in a paper,
  `paper` (the paper id); each flashcard gets `mid`;
- a predicted module's title loses a trailing "(predicted)": show `SD.ui.chip("predicted", "warn")`.

| accessor | returns |
|---|---|
| `SD.data.meta` | `{exam: {date, minutes, room, weight, sessions}, built, fixture}` |
| `SD.data.modules` | modules in course order |
| `SD.data.module(id)`, `.section(id)`, `.question(id)`, `.card(id)`, `.paper(id)` | the object or `null` |
| `SD.data.bank` | every module question, course order (paper questions excluded) |
| `SD.data.allQuestions` | bank, then every paper question |
| `SD.data.cards` | every flashcard, course order |
| `SD.data.papers` | mock papers (`content/papers.json`), each `{id, title, kind, minutes, intro_html, questions}` |
| `SD.data.plan` | plan days `{id, date, label, when, title, note_html, items: [{id, label, link}]}` |
| `SD.data.glossary` | `[{term, term_html, definition_html, mid, section_ref}]`, A–Z |
| `SD.data.sectionQuestions(sectionId)` | ids of bank and paper questions on that section |
| `SD.data.sectionRoute(sectionId)` | `"learn.<module>.s<n>"` or `null` |

Module extras (only on those modules):

- `history`: `commits[]` = `{hash, tag, message, kind, summary_html, concepts_html, message_html,
  section_ref, git}` with `git = {date (ISO), body (full message), stat (git --stat text),
  files: [{path, old_path, status: added|modified|deleted|renamed, added, removed, lines,
  collapsed (diff over 150 lines: show it closed), html (a .code diff block)}], hidden: [{path,
  added, removed}] (uv.lock and expenses.csv, left out of the diff; counts are numbers),
  tag_note (a tagged commit only: the tag's annotation from git)}`. Oldest first. Each diff line
  is a `.dline` span whose code is highlighted from the whole old or new file (Python, TOML,
  YAML; other files plain), so strings that span lines come out right. The build fails if a
  commit's `tag` is not where git puts that tag.
- `pipes-bash`: `sample_files` (`{name: text}`) and `pipelines[]` = `{id, title, goal_html,
  stages: [{cmd, output, explain_html}], takeaway_html}`. `cmd` and `output` are plain text:
  put them in the DOM with `text`, never `html`.
- `pipes-bash` also has `lab_walkthrough` (labs/10-wrangling.md solved on the real file, shown at
  `#labs.lab10`): `{id, title, source, file_note_html, summary_intro_html,
  summary_steps[], exercises: [{id, title, intro_html, steps[]}]}`. A step is `{id, prompt_html,
  pipeline, pipeline_html, output, answer_html}`: `pipeline` is the command text (one or more
  lines), `pipeline_html` the same lines highlighted as Bash at build time (a list with one HTML
  string per line, the page puts `$ ` before each), `output` the real output as plain text (put it
  in the DOM with `text`; a long one keeps its first and last lines and has a line `(… N more lines)`
  between). `tools/validate.py` checks the shape and the GNU output conventions.
- `sample-paper`: originals have `origin: "teacher-sample"` (ids `sample-paper-q01` … `q09`, in
  paper order) and `dissection_html`; variants have `origin: "teacher-variant"` and `variant_of`.

## Progress: `SD.store`

One state object, saved to localStorage under `swdev-midterm-v1` (every access guarded; with
storage blocked the page still works and the footer says progress is not being saved), and
synced to `data/users/<id>/progress` and `.../work` when the page runs as a claude.ai Artifact
with the `db` and `user` capabilities. Shape (`v: 1`):

Several tabs can be open on one device. Every save reads what is stored and merges it with the tab's
own state item by item (the newer `last` of each item wins; preferences changed in this tab win,
the rest come from storage), and the browser's `storage` event brings another tab's changes in, so
a tab that was only reading never erases work done in another (a running exam, answers, drafts).
`SD.makeStore({storage})` builds a store over any storage object (tests give it a fake);
`SD.store` is the page's own.

| key | shape |
|---|---|
| `q` | `{[questionId]: {a: attempts, c: correct, last: ts, ok: bool, conf: "sure"|"unsure"|"guess"|null}}` |
| `fc` | `{[cardId]: {box: 1..5, due: ts, last: ts, n: reviews}}` |
| `sec` | `{[sectionId]: ts last opened}` |
| `exams` | `[exam records]`, see below |
| `drafts` | `{[key]: {v: any JSON, last: ts}}`; open-answer drafts use `open.<qid>.<label>`; `history.guess` is `{[hash]: "right" \| "wrong" \| "written"}`, `labs.perms` / `labs.paths` / `labs.chains` are `{right, total}`, `labs.pipes` is `{[pipelineId]: ts}`, `labs.lab10.<step id>` is `{s: answer shown, p: the prediction typed}` (one draft per step, so two devices only clash over the same step) |
| `plan` | `{[planItemId]: {done: bool, last: ts}}` (per item, so two devices merge cleanly) |
| `prefs` | device-local settings: `theme`, `timerHidden`, `practice`, `cardsLength`, … |
| `last` | `{route, label, ts}` for Home's "Continue" |

Do not add top-level keys: `SD.progress.normalise` drops unknown keys on load. Keep a view's own
small state in `drafts` under a namespaced key (`labs.perms`), which syncs, or in `prefs`,
which stays on the device.

| method | does |
|---|---|
| `get()` | the live state object (read only; change it through the methods) |
| `update(kind, fn)` | the generic setter: `fn(state)` mutates, then listeners run and a save is queued (300 ms). `kind` names the key changed |
| `subscribe(fn)` | `fn(state, kind)` after every change; returns an unsubscribe function (call it in `cleanup`) |
| `recordAnswer(qid, ok, conf = null)` | one more attempt at a question (feeds statuses and weak spots) |
| `amendAnswer(qid, ok)` | correct the latest attempt's verdict without counting a new attempt |
| `reviewCard(cardId, "again"|"good"|"easy", examStart?)` | Leitner review; `examStart` (a timestamp) cuts long waits short so the card is back before the exam |
| `mergeRemote(remote)` | merge a copy from another device (sync) into the live state; `true` when something changed |
| `attach(window, document)` | save when the page is hidden or left, and follow the `storage` event (called once by `main.js`) |
| `flush()` | save now instead of in 300 ms |
| `markSection(sectionId)` | section opened |
| `draft(key)` / `setDraft(key, value)` | read / write a draft value |
| `setPlanItem(id, done)`, `setPref(key, value)`, `setLast(route, label)` | |
| `saveExam(record)` | insert or replace the exam record with this `id` (stamps `last`) |
| `storageMode()` | `"local"` or `"memory"` |

### Exam records (`state.exams`)

Written by the Exam view (`exam.js` builds and marks them); Home reads the fields marked *. One
record per sitting, saved with `saveExam` on every change, so a reload resumes with the right
time left (the clock runs from `started`, not from the page):

```js
{
  id: "paper-b-1760600000000",   // * unique per sitting, also its route token
  paper: "paper-b",              // paper id, "sample", or "bank"
  title: "Paper B",              // *
  minutes: 60,                   // time allowed (the sample paper: 30)
  status: "running" | "done" | "discarded",  // * Home shows the latest "done" one
  started: ts, ended: ts | null, // * ended (at 0:00, ended = started + minutes)
  used_ms: 3130000,              // * time used
  timed_out: false,              // handed in automatically at 0:00
  questions: ["paper-b-q01", ...],
  answers: { [qid]: mcqOptionIndex | {[partLabel]: text} | [categoryId|null per item] },
  flags: ["paper-b-q04"],
  paper_answers: ["paper-b-q13"],  // open questions the student wrote on paper (count as answered)
  recorded: ["paper-b-q01", ...],  // questions hand-in already recorded in progress
  ticks: { [qid]: {[partLabel]: [rubricIndex, ...]} },  // self-marking as last ticked
  marks: { [qid]: 3 },           // open answers: the mark recorded with "Record my mark"
  passed: 14, failed: 3, to_mark: 2,   // * pytest line (an open answer passes only at full marks)
  score: 21, max: 30,            // * marks; an open answer counts 0 until its mark is recorded
}
```

Handing in records every multiple-choice question (and every blank open question that was not
written on paper) with `SD.progress.record`, so wrong and blank ones become weak spots; an
answered open question, typed or written on paper, is recorded when its mark is first recorded and
amended when it is recorded again (`recorded` says which questions hand-in already counted, so
claiming a blank answer as written on paper later corrects that attempt instead of adding one). A
sitting with nothing answered, handed in or timed out, or thrown away with "Discard this sitting",
records nothing and is kept only as a stub `{id, paper, title, minutes, started, ended, status:
"discarded"}` that the lists hide (so a synced copy cannot bring it back). A sitting whose time ran
out while the page was closed is handed in when the page opens (`SD.examPaper.settle()`, also run
every half minute).

While a sitting is open the shell adds `is-sitting` to `<html>`: the rail, nav, countdown and tab
bar are hidden and only "Leave the paper" remains; on every other page a note in `#sitting-chip`
names the paper and the time left.

## Pure logic (unit-tested; safe to use anywhere)

- `SD.util`: `MINUTE`; `plural(n, one, many?)` → `"3 lines"`; `percent(part, whole)`;
  `hashString(text)` (FNV-1a); `seededRandom(seed)` → `() => [0, 1)`; `shuffled(list, seed)`
  (stable); `lineEstimate(text)` (handwritten lines, ~60 chars each); `parseRange("5–8")` →
  `{lo, hi}`; `countdown(ms)` → `"7 d 18 h"`; `clock(ms)` → `"60:00"`, `"59:59"` (minutes past
  the hour, as an exam clock; rounds up: `0:00` means time is up); `duration(ms)` → `"52m10s"`; `dayLabel(ts)` →
  `"Thu 22 Oct"`; `dateTimeLabel(ts)` → `"Thu 22 Oct, 14:00"`; `dateKey(ts)` → `"2026-10-22"`
  (each takes an optional time zone: the exam and the plan run on `SD.util.EXAM_TZ`,
  `"Europe/Madrid"`, whatever zone the browser is in); `addDays(ts, n)` → local midnight;
  `plain(text)` (backticks removed); `truncate(text, max)` (cut at a word, ends in `…`);
  `lead(text, max)` (first sentence if it fits, else truncated); `pick(random, list)`.
- `SD.progress`: `record`, `amend`, `isWeak(entry)` (wrong, or right but guessed),
  `sectionStatus(qids, state.q)` → `{status: "pass"|"fail"|"part"|"none", answered, correct, total}`
  (pass ≥ 80% right with 3 answered, or all of them in a section with fewer than 3 questions; fail
  < 60% with 2 answered, or the one question of a one-question section; `part` = answered but not
  judged yet; `none` = not tried), `moduleStatus(statuses)` → `{status, pass, fail, part, total}`
  (fail if any section fails, pass if all pass, `part` for work in between),
  `weakSpots(qids, state.q)` (oldest first), `notTried(qids, state.q)`, `mergeState`,
  `stableJson`, `blankState`, `normalise` (also repairs damaged exam records).
- `SD.scoring`: `openScore(q, ticks)` → `{score, max, parts, full}` (a part
  scores `min(marks, ticked points)`); `sortScore(q, answers)`; `pytestSummary({passed, failed,
  toMark, ms})` → segments for `SD.ui.pytestLine`.
- `SD.select`: `filter(questions, {scope, type, levels})`, `pick(mode, pool, state.q, n)`,
  `sampleOrder(pool)`, `optionOrder(qid, attempt)`.
- `SD.leitner`: `GRADES`, `review(entry, grade, now, examStart?)` (a wait is cut short so the card
  is back before the exam eve, never sooner than tomorrow), `waitDays(entry, grade, now?,
  examStart?)`, `isDue`, `queue(ids, fc, now, limit, newCards = true)` (`newCards: false`: only
  what is due), `counts`.
- `SD.planner`: `todayIndex(days, dateKey)`, `dayProgress(day, state.plan)`, `missed(days,
  state.plan, index)` (unticked items of earlier days), `hint(link, {sections, lastExam})` ("3 of 9
  sections read", "last 14/27").
- `SD.exam`: `catalogue(SD.data)` (the sample paper, the mock papers, the bank paper; the bank's
  `questions` is `null` until drawn), `buildBank(bank, state.q, seed, shape?)` (12 mcq + 3 open,
  one per module per round, weak spots then not tried first, never two of one question family),
  `start(paper, questions, now)`, `questionsOf(record, lookup)`, `deadline`, `timeLeft`,
  `expired`, `warning(msLeft)` → `0 | 10 | 5`, `finish(record, now, timedOut)`,
  `answerState(q, answer, onPaper?)` → `"blank" | "partial" | "full"` (an open answer written on
  paper counts as full), `mark(questions, record)` →
  `{results, passed, failed, toMark, score, max, modules, sections}`, `lostBySection(results)`
  (sections ranked by marks lost, for "Revise first"), `withTotals`, `marksOf(q)`, `typeCounts`,
  `resit(originals, variants, state.q, seed)` (the teacher's paper sat again: each question swapped
  for an unseen variant of its type), `untouched(record, questions)`, `discard(record, now)`,
  `running(exams)`, `newestFirst` (leaves out discarded ones), `lastDone(exams, paperId)`,
  `firstDone(exams, paperId)` (the baseline).
- `SD.marking`: `request(plainQuestion, answers)` and `parse(reply, plainQuestion)` for Claude
  marking (used through `SD.claude.mark`).
- `SD.history`: `groups(commits)` (by tag), `statRows(stat)`, `touched(commit)`,
  `candidates(commits, hash, seed)` (the real message and three close ones, shuffled),
  `ifApplied(message)`, `next(commits, record, random, current)`, `tally(commits, record)`.
- `SD.pipes`: `upTo(stages, i)` (the command line so far), `lines(text)`,
  `compare(predicted, actual)` → `{exact, matched, total, rows}` (a line diff, spacing ignored).
- `SD.lab10`: `groups(walk)` (the checklist, then each exercise: `{id, title, short, intro_html,
  steps}`), `steps(walk)` (every step in page order with its block and number), `draftKey(stepId)`,
  `read(stored)` / `write({shown, prediction})` (what the store holds for a step; damaged values
  read as not shown), `tally(walk, readStep)` and `tallyText` ("7 of 35 answers shown"),
  `isTrimmed(output)` (a `(… N more lines)` line is in it, so it cannot be compared with a
  prediction), `stepLabel`.
- `SD.perms`: `toOctal`, `parseOctal`, `toLetters`, `toLs(mode, type)`, `parseLetters`, `has`,
  `toggle`, `sum(mode, who)` (`"7 = 4 + 2 + 1"`), `rights`, `common`, `task(random, previous)`,
  `check(task, answer)`; `COMMON` holds slide 21's 644 / 755 / 600 / 777.
- `SD.paths`: the fixed tree (`kind`, `children`, `treeLines`), `words(line)`, `cd(state, word)`
  → `{ok, state, out, err, from, target, steps, failed}` with bash's messages, `exec(state, line)`
  (cd, pwd, ls [-a], echo $PWD / $OLDPWD / $HOME), `relative`, `task(random)`, `run`,
  `checkPrediction`, `explain(before, word, result)`.
- `SD.chains`: `parse(text)` (lists joined by `;` or new lines, `&&` / `||` inside, `set -e`
  lines as settings), `evaluate(parsed, statuses)`, `explain`, `errexitNote`, `grouped`,
  `finalNote`, `drill(mode, random)`, `check(result, answer)`; `EXAMPLES` are the course's cases.
  Tests replay generated drills in a real bash and dash and compare.

## Question components: `SD.q`

`SD.q.mount(container, question, opts)` appends a question sheet and returns a controller
`{el, done(), key(event)}` (open questions also have `answers()`). Pass `controller.key` to the
view's `onKey` while the question is current.

| opt | applies to | meaning |
|---|---|---|
| `mode` | all | `"practice"` (default: answer, check, full feedback, attempt recorded), `"exam"` (answer only, no feedback, nothing recorded), `"review"` (read-only answer with every why, explanation and Revise link; open questions open their marking) |
| `number` | all | text for the margin, e.g. `"Q7"` |
| `meta` | all | `false` hides the type · level · module line (exam papers) |
| `omit` | all | `"module"` or `"section"`: what the page above already names, left out of the meta line (a practice session on one module or section) |
| `answer` | all | restore an answer: mcq option index (original order), open `{label: text}`, sort `[categoryId|null per item]` |
| `ticks` | open review | restore self-marking `{label: [rubric indexes]}` |
| `onChange(answer)` | exam | every change, same shape as `answer` (save it in the exam record) |
| `onAnswer(result)` | practice | after checking: mcq `{qid, type, ok, choice, conf}`, sort `{qid, type, ok, answers}`, open `{qid, type, ok, score, max, parts, full, ticks}` |
| `onMark(score)` | open review | after each tick: `{score, max, parts, full, ticks}` |
| `onAnswer` + `recorded` | open review | with `onAnswer`, review mode also shows "Record my mark" (pass `record: false` and record progress yourself); `recorded: true` starts it as "Recorded x/y" |
| `record` | practice | `false` to leave progress untouched |
| `shuffle` | mcq practice | `false` keeps a–d order (options never shuffle outside practice) |
| `revise` | all | `false` hides the "Revise: <section>" link |
| `verdict` | mcq | `false` leaves the verdict line out (the explanation page, where nothing was answered) |
| `markable` | open review | `false` shows the model answer and rubric but no ticking or recording (an answer left blank) |
| `onPaper` | open review | the answer was written on paper: the empty box says so |

`done()` is true once feedback shows (open in practice: once the mark is recorded). Keys: a–d or
1–4 choose an mcq option, Enter checks (practice); sort items take 1–5 and ↑/↓. The keys work
once focus is inside the question (click or Tab into it) when a page holds several. After an mcq
or sort is checked the verdict line appears under the stem and takes focus (`SD.q.verdictSlot()`),
so the result is where the student is looking; "Show model answer" focuses the marking.
"Mark my answer with Claude" appears by itself on open questions in practice and review when the
`sample` capability resolves; nothing is sent before the click.

Also: `SD.q.sheet(q, opts, stemId)`, `SD.q.feedback(q, opts)` (explanation, dissection, Revise link)
and `SD.q.verdictSlot()` build the frame and the pieces if a view needs a variant.

## Shared UI: `SD.dom`, `SD.ui`, `SD.stats`, `SD.claude`

- `SD.dom.h(tag, props, ...children)`: props `class`, `text`, `html` (content HTML from the build
  only, never user text), `on<event>` handlers, `dataset`, booleans, other attributes. Children
  are nodes or strings (strings become text nodes). Also `append(el, children)`,
  `fill(el, ...children)` (replace the children; null and false are skipped, lists flattened),
  `announce(text)` (polite live region: verdicts, timer warnings), `isTyping(event)`,
  `svg(tag, props, ...children)`, `reveal(el)` (focus a result and scroll it into view),
  `inScroller(event)` (the key comes from a focused region that scrolls sideways),
  `excerpt(html, max, sentence?)` (plain text without code blocks, cut at a word, or at the end of
  the first sentence when `sentence` is true).
- `SD.ui`: `button(label, {kind, onClick, ...attrs})` (`kind`: `primary`, `secondary`, `quiet`),
  `linkButton(label, href, kind)`, `chip(text, kind)` (`pass`, `fail`, `warn`, `none`),
  `statusChip(status, text?)`, `statusMark(status, label?)` (a drawn ✓ ✗ ○ or half circle, with
  screen-reader words; status `pass`, `fail`, `part`, `none`), `mark(kind)` (just the shape),
  `verdict(ok, text)` (the coloured verdict line with its shape), `moduleCode(mod)` (`"M2"`, or
  `""` for the course-wide modules),
  `dots(statuses)`, `pytestLine(SD.scoring.pytestSummary(...))`, `progress(done, total, label)`
  (the `7/10` bar), `crumbs([[text, href], ..., [current]])`, `note(label, html, kind)` (`plain`,
  `exam`, `model`, `warn`), `foldNote(label, html, kind)` (the same in a `<details>` that starts
  open), `reviseLink(q)`, `predictedNote()`, `empty(title, text, action)`,
  `planItems(items)` (a checklist: the tick box is its own control, the item's words are the link,
  a small hint says how far the student got; an item with a `dayLabel` shows it first),
  `moduleGroups()`, `groupLabel(code)`.
- `SD.labs` (`labs-ui.js`, the Terminal lab's shared pieces; each `lab-*.js` adds its page as
  `SD.labs.<id>` with `render(root, args)`, and `LABS` lists them for the switch and the index):
  `head(current, title, crumbs?)` (lab switch and `h1`), `term(lines)` (a `$` transcript;
  `{cmd}` may hold nodes), `outputBlock(text)` (command output as plain text, or "(no output)"),
  `comparison(prediction, output)` (the verdict and line diff of a typed prediction),
  `codeText`, `tally` / `count` / `tallyText`, `random`.
- `SD.stats`: `module(id)` → `{status, pass, fail, part, total, sections}`, `section(id)`, `weakIds()`,
  `cards(moduleId?)`, `lastExam()`, `exam()` (before / during / after the real exam).
- `SD.claude`: `capability(name)` (memoised, resolves `null` when absent or never answered),
  `canMark()`, `mark(q, answers)` → `{result}` or `{error, hide}`.

## CSS: tokens and classes to reuse

Tokens (light and dark are both defined in `styles.css`; use the variables, never raw colours):
`--paper` `--sheet` `--ink` `--ink-2` `--ink-3` `--rule` `--rule-strong` `--control-edge` (the border
of any control or option row: 3:1 against both surfaces; `--rule*` are hairlines only) `--signal`
`--signal-ink` `--signal-hover` `--signal-bg` `--pass` `--pass-bg` `--fail` `--fail-bg` `--warn`
`--warn-bg` `--code-bg` `--code-ink` `--add-bg` `--del-bg` `--tok-*` `--font-body` `--font-head`
`--font-mono` `--radius` (6px) `--top-h` `--tab-h` `--line` (one ruled answer line) `--pad-s`
`--pad-m` `--pad-l` (the three paddings of a boxed surface) `--sticky-extra` (height of a sticky bar
below the header; the exam bar sets it, and the page's `scroll-padding` follows).

Type: sizes are in `rem` from this scale only: 12 (labels, chips, keys), 13 (mono meta), 15
(secondary text, controls), 17 body (16 on phones), 20, 24 (h2; 22 on phones), 32 (h1; 28 on
phones). Status marks are SVG (`.mk`), not font glyphs.

| class | use |
|---|---|
| `.page`, `.page-wide` | the reading column (46rem) and the wide one (60rem) |
| `.lead`, `.fine`, `.label`, `.meta-line` | intro text, secondary 15px text, mono uppercase label, mono meta line |
| `.btn .btn-primary/.btn-secondary/.btn-quiet`, `.actions` | buttons and a row of them |
| `.chip .chip-pass/-fail/-warn/-none/-tag`, `.mark .mark-*`, `.mk` | status chips, status marks (`mark-pass/-fail/-part/-none`) and the drawn shape inside them |
| `.qsheet`, `.q-verdict`, `.practice-bar`, `.progress` | a question sheet; the verdict line under its stem; the bar above a session (label, `7/10`, end button) |
| `.checks` + `.check-row`, `.result-list` + `.result-item` + `.result-row`, `.link-list`, `.revise-list` | hairline lists with a status column; a list of sections to go back to |
| `.link-line` | a line holding one or more stand-alone links (44px high on touch) |
| `.fold` | a `<details>` note the student can fold (`SD.ui.foldNote`); folding blocks share one drawn triangle |
| `.note`, `.note-exam`, `.note-warn`, `.empty`, `.notice` | labelled boxes, empty states, an inline warning |
| `.pytest` + `.py-pass/-fail/-warn` | the pytest summary line |
| `.code` (+ `.code-lang`), `.dline .d-add/.d-del/.d-hunk/.d-meta`, `.table-wrap` | code, diff lines and tables (they scroll inside themselves) |
| `.seg` + `.seg-btn[aria-pressed]` | segmented choices (confidence, sort categories) |
| `.field`, `.filters`, `.choice-list` + `.choice` | form fields, a grid of filters, radio rows |
| `.lined` | a ruled answer area |
| `.vh` | visually hidden, still read aloud |

Rules from `brief/DESIGN.md`: radius 6px, 40px controls (44px on touch), no shadows or
gradients, colour never the only signal, no modals or toasts, transitions ≤ 150 ms and none under
`prefers-reduced-motion`, no horizontal page scroll at 360px.

## Tests

Pure logic gets a `tests/<name>.test.mjs` run by `node --test tests/`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { perms } = load("perms.js"); // sd.js loads first; list the files it depends on too
test("755 is rwxr-xr-x", () => assert.equal(perms.toLs(0o755), "-rwxr-xr-x"));
```

`load(...files)` runs the scripts in this realm and returns `SD`; `fixture()` returns the parsed
`content/_fixture.json`. `tests/build.test.mjs` builds into a temporary folder and checks the
Artifact rules; extend it if your view adds build data.
