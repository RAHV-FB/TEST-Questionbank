<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Lab 10b — Bash Scripts: Arguments, Conditions, Loops

**Session 10 · Friday 16 October** · optional self-study after the session's script block

A script is a pipeline you wanted to run twice. Work through these in order; each one adds a
single idea. Keep everything in a sandbox:

```bash
mkdir -p ~/lab10-bash
cd ~/lab10-bash
```

**Two things to remember throughout.** A new script has no `x` (session 9), so run
`chmod +x name.sh` once. And **quote your variables**: write `"$file"`, not `$file`.

---

## Exercise 1 — A first script

```bash
cat > hello.sh <<'SCRIPT'
#!/usr/bin/env bash
echo "Hello from $(whoami), running in $(pwd)"
SCRIPT
chmod +x hello.sh
./hello.sh
```

1. What does the first line (the *shebang*) tell the system?
2. What does `$(...)` do?
3. Run `bash hello.sh` without `chmod`. Why does that work?

---

## Exercise 2 — Arguments and exit codes

```bash
cat > greet.sh <<'SCRIPT'
#!/usr/bin/env bash
if [ "$#" -ne 1 ]; then
  echo "usage: $0 NAME" >&2
  exit 2
fi
echo "Hello, $1"
SCRIPT
chmod +x greet.sh
./greet.sh
echo "exit code: $?"
./greet.sh Alice
echo "exit code: $?"
```

1. What are `$0`, `$1` and `$#`?
2. What does `>&2` do? Run `./greet.sh 2>/dev/null` and see what is left.
3. Why `exit 2` and not `exit 0` on the usage error? Who reads that number?

---

## Exercise 3 — Conditions

Write `ensure-data.sh`: if a folder called `data` exists, print `Folder exists`. If not,
create it and print `Folder created`.

```bash
if [ -d data ]; then
  echo "Folder exists"
else
  mkdir data
  echo "Folder created"
fi
```

Run it twice. Then answer:

1. What would `-f` test instead of `-d`? And `-e`?
2. Change the script to take the folder name as `$1`, with a usage error when it is missing.

---

## Exercise 4 — Loops

```bash
for file in ~/code/expense-tracker/*.md ~/code/expense-tracker/*.csv; do
  echo "Processing $file"
done

counter=1
while [ "$counter" -le 5 ]; do
  echo "Counter: $counter"
  counter=$((counter + 1))
done
```

1. Change the `for` loop to print **how many lines** each file has.
2. Print the numbers 1 to 10 with a `while` loop.
3. Use `counter=$((counter + 1))` and not `((counter++))`. Why? Try this:

```bash
cat > trap.sh <<'SCRIPT'
#!/usr/bin/env bash
set -e
counter=0
((counter++))
echo "reached"
SCRIPT
chmod +x trap.sh
./trap.sh
echo "exit code: $?"
```

Nothing is printed and the exit code is 1. `((counter++))` evaluates to the **old** value,
`0`, and `0` counts as "false" to `set -e`.

---

## Exercise 5 — The three letters of `set -euo pipefail`

Each letter turns one silent failure into a loud one. Make each fail on purpose.

**`-e`: stop at the first failing command**

```bash
cat > e.sh <<'SCRIPT'
#!/usr/bin/env bash
set -e
echo before
false
echo after
SCRIPT
chmod +x e.sh
./e.sh
echo "exit code: $?"
```

**`-u`: an unset variable is an error**

```bash
cat > u.sh <<'SCRIPT'
#!/usr/bin/env bash
set -u
echo "hello $NAME"
SCRIPT
chmod +x u.sh
./u.sh
```

**`-o pipefail`: a pipeline fails if *any* stage fails**

```bash
cat > p.sh <<'SCRIPT'
#!/usr/bin/env bash
set -o pipefail
grep nothing /nonexistent | sort
echo "pipeline exit code: $?"
SCRIPT
chmod +x p.sh
./p.sh
```

1. Run `p.sh` again after deleting the `set -o pipefail` line. What exit code does the
   pipeline report now, and why is that dangerous in CI?
2. Which of the three letters would have caught `rm -rf "$BUILD_DIR/"` with `BUILD_DIR`
   misspelled?

---

## Exercise 6 — A script on the real data

Write `top.sh FILE [N]`: print the `N` categories with the most rows in a CSV (default 3).

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: $0 FILE [N]" >&2
  exit 2
fi

file="$1"
top="${2:-3}"

if [ ! -f "$file" ]; then
  echo "error: $file is not a file" >&2
  exit 1
fi

tail -n +2 "$file" | cut -d, -f3 | sort | uniq -c | sort -rn | head -n "$top"
```

```bash
chmod +x top.sh
./top.sh ~/code/expense-tracker/expenses.csv
./top.sh ~/code/expense-tracker/expenses.csv 5
./top.sh nofile; echo "exit code: $?"
./top.sh; echo "exit code: $?"
```

1. What does `"${2:-3}"` mean?
2. Why are the two errors different exit codes?
3. Add an option so that it prints the **top merchants** instead (column 2).

---

## Exercise 7 — Arrays and functions

```bash
#!/usr/bin/env bash
numbers=(4 8 15 16 23)
total=0
for number in "${numbers[@]}"; do
  total=$((total + number))
done
echo "all: ${numbers[@]}"
echo "count: ${#numbers[@]}"
echo "first: ${numbers[0]}"
echo "sum: $total"
```

1. Run it. Now write `$numbers[0]` without braces. What do you get?
2. Write a function `square` that prints the square of its first argument, and call it three
   times:

```bash
square() {
  echo $(($1 * $1))
}
square 3
```

---

## A note for macOS

The macOS `/bin/bash` is version 3.2, from 2007. It lacks `${name,,}` and `${name^}`
(lowercase and capitalise). The scripts in this lab avoid them. If you need them, use
`tr '[:upper:]' '[:lower:]'`, which works everywhere.

---

## Clean up

```bash
rm -r ~/lab10-bash
```
