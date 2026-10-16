<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Lab 07 — Refactor, then Turn on `--strict`

**Session 7 · Tuesday 6 October · Room 108**

Two parts, 45 minutes. **Part 1** (30 min, in pairs) you refactor a small piece of code you
did not write. **Part 2** (15 min, with your group) you switch on strict type checking in
your own project.

Refactoring means the structure gets better and the behaviour stays the same. The output of
your program must not change.

---

## Part 1 — The invoice code (30 min, pairs)

### Set up

```bash
mkdir invoice-lab && cd invoice-lab
uv init --bare --name invoice-lab
uv add --dev mypy ruff
```

Create three files. Copy them exactly as they are: the names are bad on purpose.

**`main.py`**

```python
from code import calc
from utils import x

print(calc([("pencil",10,5),("book",50,2)],0.21,0.1))
print(x([10,20,30]))
```

**`code.py`**

```python
def calc(c, i, d):
    t=0
    for p in c:
        t+=p[1]*p[2]
    if d>0:
        t=t-(t*d)
    if i>0:
        t=t+(t*i)
    return t
```

**`utils.py`**

```python
def x(l):
    s=0
    for i in l:
        s+=i
    return s/len(l)
```

Run it and write down what it prints. This is your **behaviour**: it has to be the same
when you finish.

```bash
uv run python main.py
```

```
163.35
20.0
```

### What to do

Work through these in order, and run `main.py` after **every** step. If the output changes,
you have not refactored: undo the last step.

1. **Rename.** What does `calc` calculate? What are `c`, `i`, `d`, `t`, `p`? Rename every
   function, parameter and variable so that no comment would be needed. (`code.py` is also
   a poor module name — Python already has a module called `code`.)
2. **Extract constants.** `0.21` and `0.1` are in `main.py` as bare numbers. Give them names.
3. **Replace the tuple with a type.** `p[1] * p[2]` means nothing. Make a small `@dataclass`
   for a line of the invoice with named fields, as you saw with `Expense` last Tuesday.
4. **Extract functions.** `calc` does three things: it sums the lines, applies a discount,
   and applies tax. Make each one a function with a name that says what it returns.
5. **Remove the duplication.** `x` re-implements a sum. Look for what the two files have in
   common and decide whether one can use the other, or Python's own `sum`.
6. **Add types** to every function.
7. **Check.**

```bash
uv run python main.py            # same two numbers as before
uv run ruff check .
uv run mypy --strict .
```

**Done** when the output is the same two numbers, `ruff check` passes, and `mypy --strict`
says `Success: no issues found`.

### Edge cases: name them, do not test them

Before you finish, write down — in a note or on paper —
**every input that would break your refactored code, or give a surprising answer**. Think
about:

- an empty list of values
- a discount above 100%, or below 0
- a negative quantity
- a price of zero

Do **not** write tests, and do **not** fix them yet. **Friday is testing**, and this list is
what you will turn into tests.

---

## Part 2 — Strict mode in your own repo (15 min, your group)

Your project's CI already runs `mypy src tests`. From today it is strict.

### 1. Switch it on

In `pyproject.toml`, replace

```toml
[tool.mypy]
python_version = "3.13"
check_untyped_defs = true
```

with

```toml
[tool.mypy]
python_version = "3.13"
strict = true
```

### 2. Run it and fix what it reports

```bash
uv run mypy src tests
```

Read the **first** error, fix it, run again. Later errors are often the same one repeating.
Every `def test_…()` needs `-> None`.

### 3. Mark where your project's I/O lives

Find every place your code reads or writes a file, calls `print`, or calls `sys.exit`
(typer's `raise typer.Exit` and `typer.echo` count too). Write a one-line list in your
README, or in a note in the repo. This is the *shell* of your project: next
week's tests will want everything else to be pure.

If the I/O is spread across many functions, say so. That is a finding, not a failure.

### 4. Push

```bash
uv run ruff format .
uv run ruff check .
uv run mypy src tests
uv run pytest
git add -A
git commit -m "Turn on strict type checking"
git push
```

Watch the Actions tab. CI must stay green. Checkpoint 2 is marked at the `v0.2` tag, so
strict mode has to be in before then.

---

## Troubleshooting

| Symptom | What it means |
|---|---|
| `Function is missing a return type annotation` in `tests/` | Add `-> None` to the test function |
| `Function is missing a type annotation for one or more parameters` | Write the hint on every parameter, and the return type |
| `Missing type arguments for generic type "dict"` | Write `dict[str, float]`, not `dict` (same for `list`, `tuple`) |
| `Returning Any from function declared to return "float"` | The value came from something untyped, such as `csv` or `json`. Convert it (`float(row[3])`) or annotate the variable |
| `Need type annotation for "totals"` | An empty `{}` or `[]` has no type yet. Write `totals: dict[str, float] = {}` |
| `Item "None" of "… \| None" has no attribute "…"` | Real bug: the value can be missing. Check for `None` first, or change the function so it cannot return it |
| `Untyped decorator makes function untyped` | A decorator without type hints. Usually fixed by upgrading the library: `uv lock --upgrade-package typer` |
| `Library stubs not installed for "…"` | `uv add --dev types-<name>` (the error message tells you the exact name) |
| CI red at **Types**, green locally | You ran `mypy src`, but CI runs `mypy src tests`. Run it exactly as CI does |

Still stuck at the end? Push what you have to `main` and say so. A repository
I can read is worth more than a perfect one I cannot see.
