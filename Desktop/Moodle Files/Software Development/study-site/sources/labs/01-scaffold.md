<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Lab 01 — Scaffold Your Project

**Session 5 · Practice 1 · Friday 25 September · Room 108**

The goal for today is that your group repository stops being a template and instead it becomes the home for **your project**.
By the end of the session, you will tag the project as `v0.1` and push. That tag is what Checkpoint 1 is marked against.

Work on `main`, all four of you. There is no branch protection yet, so pushes will
collide — agree who pushes when, or work on one machine and swap the keyboard. Pair
programming is a legitimate answer for today.

---

## What "done" looks like

```bash
uv sync
uv run <your-app> --help
```

By running those two commands, on a machine that has never seen your project, you should see a print your CLI's help.

---

## 1. Get the repository

If you cloned it in session 3:

```bash
cd <your-repo>
git switch main
git pull
```

If you did not:

```bash
git clone git@github.com:esade-swdev-2026/<your-repo>.git
cd <your-repo>
```

Your repository is named after your **topic**; your group name is in its description.

---

## 2. Choose two names

You need two spellings of your project's name, and they are not interchangeable:

| | Form | Example | Used for |
|---|---|---|---|
| **Distribution name** | hyphens | `parking-lot` | the project, and the command you type |
| **Package name** | underscores | `parking_lot` | the folder under `src/`, and Python imports |

Python identifiers cannot contain hyphens, which is why there are two. Write both down
before you start — they appear six times between them, and a typo in any one of them
breaks the install.

---

## 3. Rename the template — all six places

The template ships as `app`. Replace it everywhere.

**a. The package folder**

```bash
git mv src/app src/<your_package>
```

**b. `pyproject.toml`** — three lines:

```toml
[project]
name = "<your-app>"

[project.scripts]
<your-app> = "<your_package>.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/<your_package>"]
```

**c. `src/<your_package>/__main__.py`** — one import:

```python
from <your_package>.cli import app
```

**d. `tests/test_cli.py`** — one import:

```python
from <your_package>.cli import app
```

Check you got them all:

```bash
grep -rnI "app" pyproject.toml src tests
```

The only `app` left should be the typer object itself — `app = typer.Typer(...)` in
`cli.py`, and the `.cli:app` / `import app` that refer to it. Anything mentioning
`src/app` or `app.cli` is a rename you missed.

---

## 4. Re-lock, then install

```bash
uv lock
uv sync
```

**Do not skip `uv lock`.** `uv.lock` records your project under its old name, and CI runs
`uv sync --locked`, which refuses to install when the lockfile and `pyproject.toml`
disagree. Skipping this is the single most likely reason your first push goes red. Commit
`uv.lock` along with everything else.

Check the command exists:

```bash
uv run <your-app> --help
```

---

## 5. Write one real command

Delete `greet` and `bye` from `src/<your_package>/cli.py` and write **one command of your
own** — the smallest useful thing your project does. It must have:

- at least one **argument** (a value the command needs), and one **option** (a flag with a
  default),
- a **non-zero exit** when the input makes no sense,
- type hints on every parameter: in typer, the type hints *are* the command-line
  specification.

Here is the *shape* that you should look for:

```python
import typer

app = typer.Typer(help="A terminal expense tracker.")


@app.callback()
def main() -> None:
    """A terminal expense tracker."""


@app.command()
def add(merchant: str, amount: float) -> None:
    if amount <= 0:
        typer.echo("amount must be positive", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Added {merchant}: {amount:.2f}")
```

`merchant` is the argument, `amount` the validated input, the callback and exit-code beats
below apply whatever your command turns out to be. **Your command has to be about your own
project** — what does the first real thing *your* four of you are building actually do? If
your command reads like this one with nouns swapped, it's not done: the point is translating
the pattern into your own domain, not the pattern itself.

**Keep the `@app.callback()`.** The template has two commands, so it does not need one. With
a *single* command, typer assumes the command *is* the program and drops its name: your
command stops being a word you type, `<your-app> <command> ...` fails with *"Got unexpected
extra argument(s)"*, and your tests fail with exit code 2. The empty callback tells typer
there will be more commands, so yours keeps its name. Delete it later if you ever want the
one-command form.

It does not have to store anything yet. It has to run, and it has to fail properly.

```bash
uv run <your-app> <your-command> <a-valid-argument>
uv run <your-app> <your-command> <an-invalid-argument>
echo $?          # 1, not 0
```

---

## 6. Update the tests

`tests/test_cli.py` still tests `greet` and `bye`, which no longer exist. Rewrite it for
your command — one test for the normal case, one for the failure. Following the shape above:

```python
def test_add_reports_the_merchant() -> None:
    result = runner.invoke(app, ["add", "Bar Ramon", "12.50"])
    assert result.exit_code == 0
    assert "Bar Ramon" in result.stdout


def test_add_rejects_a_non_positive_amount() -> None:
    result = runner.invoke(app, ["add", "Bar Ramon", "0"])
    assert result.exit_code == 1
```

Write your own two, against your own command and your own valid/invalid inputs — not these,
renamed.

Testing properly is session 8. Today, two tests that pass are enough.

---

## 7. README and LICENSE

**`README.md`** — delete the "rename `app`" banner at the top, then make sure it says:

- what the program does and who it is for, in one or two sentences,
- how to install it: `uv sync`,
- how to run it, with at least one real example, copy-pasteable.

Write it for a stranger. A stranger will mark it.

**`LICENSE`** — replace the copyright holder with your group's names:

```
Copyright (c) 2026 <your names>
```

It currently names the lecturer, which is wrong: the work is yours.

---

## 8. Run the same checks CI runs

```bash
uv run ruff format .        # fixes formatting in place
uv run ruff check .         # lint
uv run mypy src tests       # types
uv run pytest               # tests
```

These four commands are exactly what `.github/workflows/check.yml` runs. If they pass
here, they pass there. Run them **before** you push, not after.

---

## 9. Commit, push, tag

```bash
git add -A
git commit -m "Scaffold the project"
git push
```

Then give that commit a name:

```bash
git tag -a v0.1 -m "Scaffolded project"
git push origin v0.1
```

A **tag** is a permanent name for one commit. `v0.1` is the version I mark Checkpoint 1
against, so a missing tag means there is nothing to mark. Tags are explained properly in
module 4; today, those are the two commands.

Watch the Actions tab. It should go green.

---

## 10. Check yourself against Checkpoint 1

CP1 is three binary items, marked at your `v0.1` tag:

1. `uv sync && uv run <your-app> --help` works **from a clean clone**
2. `src/` layout, with the package importable
3. README says what the program does and how to run it

Prove item 1 and 2 to yourself the way I will:

```bash
cd /tmp && rm -rf cp1 && git clone git@github.com:esade-swdev-2026/<your-repo>.git cp1
cd cp1 && git checkout v0.1
uv sync
uv run <your-app> --help
uv run python -c "import <your_package>; print('import OK')"
```

A clean clone has no `.venv`, no caches and nothing you forgot to commit. That is the
whole point of the check: it catches the file that only exists on your laptop.

---

## Troubleshooting

| Symptom | What it means |
|---|---|
| `The lockfile at uv.lock needs to be updated, but --locked was provided` | You renamed the project but did not run `uv lock`. Run it, commit `uv.lock`, push |
| `Cannot find implementation or library stub for module named "app.cli"` | `__main__.py` still imports the old name. It is the rename everyone forgets — pytest does not catch it, mypy does |
| `ModuleNotFoundError: No module named '<your_package>'` | The folder under `src/` and the name in `pyproject.toml` disagree, or you have not run `uv sync` since renaming |
| `error: Failed to spawn: '<your-app>'` | `[project.scripts]` does not match the command you typed, or `uv sync` has not been run since you changed it |
| CI red at **Formatting**, green locally | You ran `ruff format .` after committing. Run it, then commit the result |
| `! [rejected] ... non-fast-forward` on push | A teammate pushed first. `git pull` and try again — merging is module 4, so for today, coordinate who pushes |
| `--help` prints your argument as an option instead of taking a value positionally | A parameter with a default becomes an *option* in typer. Drop the default, or use `typer.Argument(...)` |
| `Got unexpected extra argument(s)`, and `--help` shows no command names | You have one command and no `@app.callback()`. Add the empty callback from §5, and use your command's own name in place of `<your-command>` |

Still stuck at 13:00? Push whatever you have, on `main`, and say so. A repository I can
read is worth more than a perfect one I cannot see.
