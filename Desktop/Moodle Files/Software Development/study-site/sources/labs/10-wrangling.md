<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Lab 10 — Text Wrangling on `expenses.csv`

**Session 10 · Friday 16 October · Room 108**

The expense tracker reads one file, `expenses.csv`. You will now ask that file questions
using nothing but small programs joined by pipes. Every question below has **one pipeline**
as its answer.

Work in a sandbox. Never edit the original `expenses.csv`: other sessions use it as it is.

```bash
mkdir -p ~/lab10
cp ~/code/expense-tracker/expenses.csv ~/lab10/
cd ~/lab10
```

---

## What "done" looks like

You answer these with one pipeline each, and can say what every `|` in it is doing:

1. How many expenses are in the file?
2. Which category has the most rows?
3. How many distinct merchants are there?
4. Which are the five biggest expenses?
5. Which rows are exact duplicates?

---

## The tools

| Command | What it does | Example |
|---|---|---|
| `head -n 3` / `tail -n 3` | First / last lines | `head -n 3 expenses.csv` |
| `tail -n +2` | Everything **from line 2** (skips the header) | `tail -n +2 expenses.csv` |
| `wc -l` | Count lines | `wc -l expenses.csv` |
| `cut -d, -f3` | Take column 3 of a comma-separated file | `cut -d, -f3 expenses.csv` |
| `grep PATTERN` | Keep lines that match. `-v` inverts, `-c` counts | `grep -c ',dining,' expenses.csv` |
| `sort` | Sort lines. `-r` reverse, `-n` numeric, `-t, -k4` sort on column 4 | `sort -t, -k4 -rn` |
| `uniq` | Collapse **adjacent** equal lines. `-c` count, `-d` only duplicated | `sort \| uniq -c` |
| `>` / `>>` | Write output to a file (overwrite / append) | `... > result.txt` |

`uniq` only sees **neighbours**. That is why it is always `sort | uniq`, never `uniq` alone.

---

## Exercise 1 — Look at the file

```bash
head -n 3 expenses.csv
wc -l expenses.csv
tail -n +2 expenses.csv | wc -l
```

1. What are the four columns?
2. The first count and the second differ by one. Why? Which is the number of expenses?

---

## Exercise 2 — Count by category

```bash
tail -n +2 expenses.csv | cut -d, -f3
tail -n +2 expenses.csv | cut -d, -f3 | sort
tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c
tail -n +2 expenses.csv | cut -d, -f3 | sort | uniq -c | sort -rn
```

Run the four lines **one at a time**, and read each output before adding the next stage.

1. What does each added stage do to the output?
2. Which category has the most rows? Which has the fewest?
3. Add one more stage so that only the top three categories are shown.
4. Remove the `sort` in the middle and run it again. What breaks, and why?

---

## Exercise 3 — Distinct merchants

Merchants are column 2.

1. How many **distinct** merchants are there? (Hint: `sort -u`, or `sort | uniq`, then `wc -l`.)
2. Which three merchants appear most often?
3. How many rows are there for the merchant `Repsol`? Which category are they all in?

---

## Exercise 4 — Filter rows

```bash
grep ',dining,' expenses.csv | head -n 3
grep -c ',dining,' expenses.csv
grep '^2025-09' expenses.csv | wc -l
```

1. How many dining rows are there?
2. How many expenses were made in September 2025? (`^` means "at the start of the line".)
3. How many dining expenses were made in December 2025? Chain two `grep`s.
4. Which month has the most expenses? Build it from `cut -c1-7` (the first seven characters
   of each line), then `sort | uniq -c`.

---

## Exercise 5 — The five biggest

```bash
tail -n +2 expenses.csv | sort -t, -k4 -rn | head -n 5
```

1. Which five expenses are the biggest? What do they have in common?
2. What happens if you drop `-n` from `sort`? Try it and explain the order you see.
3. Show only the **merchant and amount** of those five. Add one stage.

---

## Exercise 6 — Duplicates

```bash
tail -n +2 expenses.csv | sort | uniq -d
```

1. Which rows are duplicates? How many are there?
2. Remove the duplicates, keep one copy of each, and write the result to `clean.csv`
   (header included):

```bash
head -n 1 expenses.csv > clean.csv
tail -n +2 expenses.csv | sort -u >> clean.csv
wc -l clean.csv
```

3. How many rows does `clean.csv` have? Explain the difference from the original.
4. What is the difference between `>` and `>>`, and what would happen to `clean.csv` if the
   second line used `>` instead?

---

## Exercise 7 — Two tools, one answer

How much was spent on groceries? Ask the tracker, then ask the shell.

```bash
cd ~/code/expense-tracker
uv run expenses report --category groceries

cd ~/lab10
grep ',groceries,' expenses.csv | cut -d, -f4 | paste -sd+ | bc
```

1. Do the two answers agree? What does `paste -sd+` do to the column of numbers?
2. Does the tracker count the duplicate rows? Does your pipeline?

---

## Stretch — one `awk` line

`awk` is a small language for columns. You do not need to write it; read it:

```bash
awk -F, 'NR>1 {sum[$3]+=$4} END {for (c in sum) printf "%s %.2f\n", c, sum[c]}' expenses.csv | sort -k2 -rn
```

1. What is `-F,`? What is `NR>1`? What is `$3` and what is `$4`?
2. Which category costs the most? Does it match the category with the most **rows**?
3. Change it to show the **average** amount per category.

---

## Clean up

```bash
rm -r ~/lab10
```

**Next:** the second half of today turns pipelines like these into a **script** with
arguments, a condition and a loop, and ends with `scripts/check.sh` for your own project.
