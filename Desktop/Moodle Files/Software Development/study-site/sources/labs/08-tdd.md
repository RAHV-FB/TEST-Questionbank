<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Lab 08 — Test-Drive the Core of Your Project

**Session 8 · Practice 2 · Friday 9 October · Room 108**

The goal for today is that the core of your project is covered by tests that pass in CI.
By the end of the session you will tag the project as `v0.2` and push. That tag is what
Checkpoint 2 is marked against, and **the deadline is 13:15**. A repository without the tag
has nothing to mark.

Work on `main`, all of you. Agree who pushes when. Split the modules between you: each
person takes different functions, so you do not edit the same file.

---

## What "done" looks like

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

All four pass, the **check** workflow is green on the Actions tab **at the tagged commit**,
and `uv run pytest` reports at least 8 passed.

---

## 1. Find what to test (10 min)

Open your source and list the **pure functions that decide something**: a total, a score, a
next state, a price, a validation. Functions that take values and return a value, with no
`print`, no `open`, no network.

If the logic you want to test is tangled up with `print` or `open`, **split it first**:
move the decision into a function that takes data and returns data, and leave the printing or
reading in a thin function around it. That is refactoring, and the first test you write is
your safety net for it.

Write the list in a note. Aim for five or six functions.

## 2. Red, green, refactor (50 min)

For each function on your list:

1. **Red.** Write a test for the behaviour you want. If the function does not exist yet,
   write a stub that returns something wrong. Run `uv run pytest` and **read the failure**.
2. **Green.** Write the smallest code that passes.
3. **Refactor.** Clean it up. Run the tests again: they must still pass.

Put tests in `tests/`, in files named `test_<something>.py`. Every test is a function whose
name says what it checks, with a return type:

```python
def test_empty_basket_costs_nothing() -> None:
    assert basket_total([]) == 0.0
```

### Choose edge cases on purpose

Before writing a test, ask:

| Ask | Example |
|---|---|
| **Empty**: nothing in? | an empty list, an empty string |
| **Zero**: the boundary? | a value exactly equal to the threshold |
| **Negative**: nonsense? | a refund, a negative quantity |
| **Duplicate**: twice? | the same item appearing twice |
| **Missing**: not there? | a category nobody used |

Last Tuesday you wrote down the inputs that could break your invoice code. This is where they
become tests.

Use `pytest.approx` to compare floats, a **fixture** for data several tests share, and
`@pytest.mark.parametrize` when the only difference between tests is the numbers.

## 3. One or two tests at the edge (15 min)

Your program does touch the outside world somewhere: a file, the command line, an environment
variable. Test **that** place on purpose, once or twice:

- `tmp_path` for a file: build the file inside the test, in the fresh directory pytest gives you
- `CliRunner` for the command line: check the exit code and the output
- `monkeypatch` for the working directory or an environment variable

Never read a file that lives on your laptop only (such as `data/expenses.csv`): the test would
pass for you and fail in CI.

**One or two** is the target. A suite where every test needs a file is the opposite of what we
practised.

The template came with tests in `tests/test_cli.py` that use `CliRunner`. They count towards
your 8, but they are I/O tests, so they count against "mostly pure". Keep one or two, rewrite
them for your own commands, and delete the rest once you have pure tests to replace them.

## 4. Check, tag, push (last 10 min)

```bash
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest -q
git add -A
git commit -m "Add tests for the core"
git push
```

Wait for the green check on the Actions tab. Then, from the commit that is green:

```bash
git tag -a v0.2 -m "Checkpoint 2: tested core"
git push origin v0.2
```

Not finished by 13:05? Push what you have, tag it and say so. A repository I can read is worth
more than a perfect one I cannot see.

---

## Demo examples

The demo repository, [`expense-tracker`](https://github.com/esade-swdev-2026/expense-tracker),
is at the same stage at tag `v0.4`. Look at its `tests/` folder if you want an example, but
your domain is different: your tests should be about **your** functions.

---

## Troubleshooting

| Symptom | What it means |
|---|---|
| `no tests ran`, exit code 5 | pytest found no test: file not in `tests/`, or not named `test_*.py`, or function not named `test_*` |
| `Function is missing a return type annotation` in `tests/` | Add `-> None` to the test function. `pytest` alone passes; CI runs mypy too |
| `ModuleNotFoundError` for your package | Run `uv sync`, and use `uv run pytest`, not bare `pytest` |
| A test passes locally and fails in CI | It reads a file that is only on your laptop. Build the data inside the test |
| `assert 0.30000000000000004 == 0.3` | Floats. Use `pytest.approx(0.3)` |
| The test passes but you did not see it fail | You skipped red. Break the code on purpose once and watch the test notice |
| `fixture 'tmp_path' not found` | A typo in the argument name; pytest matches fixtures by name |
| CI is green but `git tag` points at an older commit | Tag the commit CI approved: `git log --oneline` and tag that hash |
