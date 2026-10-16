<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Lab 09 — The Terminal on Your Own Project

**Session 9 · Tuesday 13 October · Room 108**

You will move around, manage files and fix a "permission denied", all on the project you
already have. Work in pairs.

**Where to work.** Your projects must live in your home folder, `~/code/...`. On Windows that means the Linux home inside WSL, never `/mnt/c`. Please make sure you are in the right folder before you start entering commands.

---

## What "done" looks like

You can answer these without looking anything up:

1. Where am I, and what is in this folder, including hidden files?
2. What is the absolute path of `report.py`, and the relative path to it from the project root?
3. Why did a script say "permission denied", and what fixed it?

Exercises 1–3 are the lab. Exercise 4 is for anyone who finishes early.

---

## Setup

```bash
mkdir -p ~/code
cd ~/code
git clone https://github.com/esade-swdev-2026/expense-tracker.git
cd expense-tracker
pwd
```

`pwd` should print your home folder followed by `/code/expense-tracker`:

| System | Home folder | `pwd` prints |
|---|---|---|
| macOS | `/Users/<you>` | `/Users/<you>/code/expense-tracker` |
| Linux, WSL | `/home/<you>` | `/home/<you>/code/expense-tracker` |

`~` and `$HOME` mean your home folder on every system. Your own group repo should sit next
to it in `~/code`. If it does not, clone it there now.

On macOS, `ls -l` may show an `@` after the permission letters (`-rw-r--r--@`). That marks
extended attributes; ignore it.

---

## Exercise 1 — Navigate

Run each command and read what it says before moving on.

```bash
pwd
ls
ls -a
ls -l
ls -la
```

1. Which entries appear in `ls -a` but not in `ls`? Why do they start with a dot?
2. In `ls -l`, which entries are folders? How can you tell from the first character?

Now move around **using relative paths only**:

```bash
cd src/expense_tracker
pwd
ls -l
cd ../../tests
pwd
cd ..
pwd
```

Then with **absolute paths and shortcuts**:

```bash
cd ~/code
cd "$HOME/code/expense-tracker/src"
cd -
cd
pwd
```

3. Where did `cd` with no argument take you? And `cd -`?
4. What does `echo $HOME` print? Compare it with the output of `pwd` right after a plain `cd`.
5. From `~`, write the relative path to `code/expense-tracker/src/expense_tracker/report.py`.

Use **Tab** for every name you type. If Tab does not complete it, the name is wrong.

Repeat `ls -la` in **your group repo**. Find where the CI workflow lives:

```bash
cd ~/code/<your-group-repo>
ls -la .github/workflows
```

---

## Exercise 2 — Manage files

You will work in a sandbox so nothing in a real project is touched. Never edit
`expenses.csv` in place: it is a fixture the course relies on. Copy it.

```bash
mkdir -p ~/lab09/reports/2025 ~/lab09/reports/archive
cp ~/code/expense-tracker/expenses.csv ~/lab09/reports/
touch ~/lab09/reports/notes.txt
cd ~/lab09
ls -R reports
```

Now do each of these. Write down the command you used.

1. Copy `expenses.csv` into `reports/archive/` under the name `expenses-backup.csv`
2. Move `notes.txt` into `reports/2025/`
3. Rename `reports/2025/notes.txt` to `reports/2025/summary.txt`
4. Copy the whole `reports` folder to `reports-copy`
5. Check the result with `ls -R`

Then the part with no undo:

```bash
ls reports-copy
rm -r reports-copy
ls reports-copy
```

6. What did the last `ls` say? Is there a bin to get it back from?
7. You type `rm -r reports-copy *` by mistake, with a space before the `*`. What does it remove?
   (Do **not** run it. Reason it out.)

---

## Exercise 3 — Permissions

Create a script:

```bash
cd ~/lab09
printf '#!/usr/bin/env bash\necho "report ready"\n' > run.sh
cat run.sh
ls -l run.sh
./run.sh
```

1. What does `./run.sh` print? Which character is missing from `ls -l run.sh`?

Fix it and run it:

```bash
chmod +x run.sh
ls -l run.sh
./run.sh
```

2. What changed in `ls -l`? What does `./` in front of the name mean? Try without it:
   `run.sh`. Why does it fail?

Numbers:

```bash
chmod 600 run.sh
ls -l run.sh
./run.sh
chmod 755 run.sh
ls -l run.sh
```

3. After `chmod 600`, can you run it? Can you still read it with `cat`?
4. Write `rwxr-xr-x` and `rw-------` as three-digit numbers.

Now look at the real project:

```bash
cd ~/code/expense-tracker
ls -l src/expense_tracker
```

5. Which of these files could you run directly? Why is that right for Python modules?

---

## Exercise 4 — Stretch: find things

`find` searches a tree. It is how you answer "where did I put that?"

```bash
cd ~/code/expense-tracker
find src tests -name "*.py"
find . -name "*.csv"
find . -name "test_*" -type f
find src -name "*.py" -type f | wc -l
```

1. How many Python files are in `src` and `tests` together?
2. Find every file in your **group repo** whose name contains `check`. Where is it?
3. Find every folder named `tests` in `~/code`. Why are there several?

---

## Clean up

```bash
rm -r ~/lab09
```

---

## Self-check

You are done when you can do all of this with no notes:

- Print where you are, and list everything in the folder, hidden files included
- Go from the project root to `tests` and back, once with relative paths and once absolute
- Copy, move, rename and delete a file, and say what `rm` will not let you undo
- Read `-rwxr-xr-x` aloud, and fix a script that says "permission denied"

**Next session** uses the same terminal: pipes and text wrangling on `expenses.csv`, then
bash scripts. Bring this sandbox habit with you: copy the data, never edit the original.
