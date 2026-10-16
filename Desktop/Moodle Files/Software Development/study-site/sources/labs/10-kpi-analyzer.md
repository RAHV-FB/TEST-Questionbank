<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Homework 10 — Project Reports and KPI Analyzer

**Session 10 · optional · not marked** · uses everything from `10-wrangling.md` and `10-bash.md`

**Scenario.** You work in a business administration office. Each month, departments drop
reports into one shared folder: project plans, KPI reports, budgets, and everything else.
Your job is to automate the first sorting pass with a Bash script.

---

## The task

Write `project_organizer.sh`:

```bash
./project_organizer.sh /path/to/reports
./project_organizer.sh -r /path/to/reports
```

### 1. Arguments and errors

| Situation | Behaviour | Exit code |
|---|---|---|
| Wrong number of arguments | Print `usage: ... [-r] DIRECTORY` **to stderr** | `2` |
| Directory does not exist | Print an error **to stderr** | `1` |
| Success | Print the summary lines (below) | `0` |

An error that exits `0` is a bug: a script that calls yours cannot tell it failed.

### 2. Create four folders inside the directory, if they do not exist

`project_plans` · `kpi_reports` · `budgets` · `misc`

### 3. Move each file by name, **case-insensitively**

| Filename contains | Goes to |
|---|---|
| `plan` | `project_plans` |
| `kpi` | `kpi_reports` |
| `budget` | `budgets` |
| anything else | `misc` |

Check them in that order: a file called `budget_plan.xlsx` is a plan. `KPI_TeamA.txt` is a
KPI report. Without `-r`, only the files directly inside the directory are moved. With `-r`,
files in subfolders are moved too, but **never** files already inside the four folders, and
never `organizer.log`.

### 4. Log every move to `organizer.log`, one line per file

```
[2026-10-16 12:30] MOVED project_plan_q3.pdf -> project_plans
```

### 5. Never overwrite: number the duplicates *before the extension*

If `project_plans/plan.pdf` already exists, the next one becomes `plan(1).pdf`, then
`plan(2).pdf`. For a name with no extension, `notes` becomes `notes(1)`.

### 6. Write a `summary.txt` into each folder

```
Files: 6
Total size: 1843201 bytes (1.8 MB)
Most recent file: project_plan_q3.pdf
Average lines (text files): 12.5
```

- *Files* does not count `summary.txt` itself.
- *Most recent* means the **newest modification time**, not the last one the loop saw.
- *Average lines* is over text files only. A binary file (a `.xlsx`, a `.pdf`) is ignored. If
  there are no text files, print `n/a`.

Also print one line per folder on screen:

```
project_plans: 6 files, 1.8 MB, latest project_plan_q3.pdf
kpi_reports: 4 files, 1.2 MB, latest KPI_teamA.txt
budgets: 3 files, 0.9 MB, latest budget_departmentX.xlsx
misc: 2 files, 0.3 MB, latest notes.docx
```

### 7. Run it twice

Running it again on an already-organised folder must not fail, duplicate anything or
re-count `summary.txt`.

---

## Build a test folder first

Do not test on real data. This makes a messy folder of fake reports, with names that contain
spaces, upper case, duplicates in a subfolder, and one binary file:

```bash
mkdir -p ~/kpi-test/sub
cd ~/kpi-test
printf 'a\nb\nc\n' > project_plan_q3.txt
printf 'x\n'       > KPI_teamA.txt
head -c 3000 /dev/urandom > budget_x.xlsx
printf 'n\n'       > notes.docx
printf 'dup\n'     > sub/project_plan_q3.txt
printf 'dup2\n'    > sub/plan.txt
printf 'z\n'       > sub/other.pdf
touch "my budget 2025.txt"
```

Expected after `-r`: three files in `project_plans`, one in `kpi_reports`, two in `budgets`, two
in `misc`, and `project_plan_q3(1).txt` in `project_plans`.

---

## Hints

- `find "$dir" -maxdepth 1 -type f` lists files without descending.
- Read file names with `while IFS= read -r -d '' file; do ... done < <(find ... -print0)`.
  A plain `for file in $(find ...)` breaks on a file called `my budget 2025.txt`.
- `${name%.*}` is the name without its last extension; `${name##*.}` is the extension.
- `[ "$file" -nt "$other" ]` is true if `$file` is newer.
- `grep -qI '' "$file"` succeeds for a text file and fails for a binary one.
- `awk -v a="$x" -v b="$y" 'BEGIN { printf "%.1f", a / b }'` does the division.
- `tr '[:upper:]' '[:lower:]'` lowercases, and works on macOS's old bash too.
- Start from `set -euo pipefail`, and use the exit code of your own script to check it.

## Check your own work

```bash
./project_organizer.sh /nonexistent; echo $?     # 1
./project_organizer.sh;              echo $?     # 2
./project_organizer.sh -r ~/kpi-test; echo $?    # 0
./project_organizer.sh -r ~/kpi-test              # again: no errors, same counts
cat ~/kpi-test/organizer.log
cat ~/kpi-test/project_plans/summary.txt
```

Stretch: run `shellcheck project_organizer.sh` if it is installed, and fix what it says.

