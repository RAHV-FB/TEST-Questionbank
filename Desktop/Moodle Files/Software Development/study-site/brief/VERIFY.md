# How to verify (every artefact is real)

Paths (quote them; they contain spaces):
- SITE = `/Users/russell/Desktop/Moodle Files/Software Development/study-site`
- SCRATCH = `/private/tmp/claude-501/-Users-russell-Desktop-Moodle-Files/e1a90d70-a42e-4cd3-8ca7-4c165e7f3a1d/scratchpad`
- Sandbox project (expense-tracker at v0.4 with the course's exact toolchain: Python 3.13, typer, ruff 0.16.9, mypy 2.4.0, pytest): `$SCRATCH/sandbox`
- The expense-tracker git repo (read-only, do not modify): `/Users/russell/Desktop/Moodle Files/Software Development/_repos/expense-tracker`
- Course labs: `$SITE/sources/labs/`, slide text: `$SITE/sources/slides/`, Moodle pages: `$SITE/sources/moodle/`, the full commit-by-commit patch of the expense-tracker: `$SITE/sources/expense-tracker-history.patch`

## Your own work folder
Make `$SCRATCH/work/<your module id>/` and keep every snippet, script and output there. Never write into another module's folder, the sandbox source tree, or the `_repos` folder.

## Running the course tools on a snippet
```bash
W="$SCRATCH/work/<id>"; mkdir -p "$W"
cat > "$W/q07.py" <<'PY'
...code exactly as shown in the question...
PY
cd "$W"
uv run --project "$SCRATCH/sandbox" mypy --strict --cache-dir "$W/.mypy_cache" q07.py
uv run --project "$SCRATCH/sandbox" ruff check --no-cache q07.py
uv run --project "$SCRATCH/sandbox" python q07.py
```
- For pytest output, create a mini project folder in `$W` (e.g. `$W/q12/src/...` + `tests/...`), or put the code under test and the test in one folder and run `uv run --project "$SCRATCH/sandbox" pytest -q -p no:cacheprovider <folder>`; copy the real output, then trim (keep the lines the student needs: the `FAILED ... - assert ...` summary line, the `E` lines, the `N failed, M passed` line). Show paths as they would look in a project (`tests/test_totals.py`), which may mean naming your folders that way.
- For a historical state of the expense-tracker, clone it into your folder: `git clone -q "/Users/russell/Desktop/Moodle Files/Software Development/_repos/expense-tracker" "$W/et" && cd "$W/et" && git checkout -q v0.1 && uv sync -q` then run its tools (`uv run mypy --strict src`, `uv run ruff check .`, `uv run pytest`).
- For uv behaviour (lockfile mismatch, TOML parse errors, `uv sync --locked`), make a throwaway copy of the sandbox project in `$W` and break it on purpose. uv here is 0.12.x; the error wording is what students see. Do not use `--offline` tricks that change messages.
- If a tool's output contains your scratch path, rewrite only the path prefix to the project-relative path the student would see.

## Shell commands (session 9/10 questions)
You run macOS (BSD userland, zsh). The course runs bash on Ubuntu/WSL (GNU coreutils). Run the command on a sample file to get the content, then present it **in GNU format**:
- `wc -l < file` and `cmd | wc -l` print just the number on GNU (`12`); macOS pads with spaces (`      12`). Show `12`.
- `wc -l file` on GNU prints `12 file`.
- `uniq -c` on GNU right-aligns the count in a 7-wide field: `      3 dining`. Show that format.
- `ls -l` on GNU: `-rw-rw-r-- 1 alice alice  1193 Oct 11 17:07 README.md` (no trailing `@`, owner and group both shown). Use the slides' format.
- `sort` order: use `LC_ALL=C sort` when computing so plain byte order is used, and avoid questions whose answer depends on locale collation or on exact column padding.
- `cut -d, -f4`, `grep`, `head`, `tail`, `sort -n`, `sort -rn`, `uniq`, `tr`, `find` behave the same for the simple cases the course uses. `grep -c` counts lines.
- Run bash scripts with `bash script.sh` (macOS ships bash 3.2; avoid bash 4+ only features unless you only reason about them).
- `echo $?` after a failing command prints the exit status; `cmd1 && cmd2` runs cmd2 only if cmd1 exits 0; `cmd1 || cmd2` only if it exits non-zero; with `set -e` a failing command stops the script (except in conditions, `&&`/`||` lists other than the last, and pipelines unless `pipefail`).
- Never run anything destructive outside `$W` (no `rm -r` on anything but files you created in `$W`).

## Evidence
Keep, per question that needed a run, the input and raw output in `$W` (e.g. `q07.py`, `q07.out`). Your final report lists which questions were run and confirms the shown output matches the run.
