<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Lab 00 — The Developer's Starter Kit

**Session 3 · Friday 18 September · Room 108**

By the end of this lab you have a working development environment and you have pushed
your first file to your group repository, watched CI check it, and seen it go green.

---

## The contract

You are free to use any operating system and any editor. Two things are non-negotiable:

1. **Your work must pass the CI check** — the automated check that runs on GitHub every
   time you push. It runs `ruff`, `mypy` and `pytest`. It is the referee. "It works on my
   machine" is exactly the problem this course exists to solve, so the machine that decides
   is one none of us owns.
2. **The recommended path below is the only one supported live in the room.** If you go
   off-path, that is fine and allowed — but the time it costs is yours, not the class's, and
   off-path help is office hours, not the lab.

There is no target of sixty green laptops by 13:15. The realistic goal is: most of the room
running by the end, the rest diagnosed and finished before Tuesday. **Unfinished is a
ticket, not a crisis.**

---

## The recommended path

| Tool | What it is for |
|---|---|
| **WSL2** (Windows only) | A real Linux running inside Windows. The whole course assumes a Linux shell. |
| **VS Code** | Editor. On Windows it runs on Windows and edits files inside WSL. |
| **uv** | Installs Python and your project's dependencies, reproducibly. |
| **git** | Version control. Module 4 explains it; today you just need it working. |
| **GitHub** (SSH key) | Where your group repository lives. |
| **Docker Desktop** | Containers. Not needed until session 15 — installed at home, from [`02-docker-setup.md`](02-docker-setup.md). |

> **About Docker, today.** Docker Desktop is a ~600 MB download. **If you are on the ESADE
> wifi during the lab, do not start it** — sixty simultaneous downloads slow the room down
> for everyone, including people still installing the things that *are* on today's critical
> path. A red Docker line on your setup report is fine and expected.
>
> You install it at home instead, from [`02-docker-setup.md`](02-docker-setup.md), **any
> time before session 15 (Tuesday 10 November)** — the first session that runs containers
> in the room.

Find your operating system below and follow only that section.

---

## Windows

### 1. WSL2 + Ubuntu

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
```

Reboot when it asks. On the way back up it installs Ubuntu and asks you to pick a
username and password — this is your **Linux** account, unrelated to Windows.

> **The password looks like it is not being typed.** No asterisks, no dots, no cursor
> movement. That is normal on Linux, not a dead keyboard. Type it and press Enter.

Then, in the Ubuntu shell:

```bash
sudo apt update && sudo apt upgrade -y
```

> **Expected noise during the upgrade.** Lines like `Failed to get properties: Transport
> endpoint is not connected` or `Failed to connect to system scope bus via local
> transport: Connection refused` are harmless: WSL2 runs without the full `systemd`
> service manager those triggers expect. The packages upgraded fine.

- **WSL2, not WSL1.** `wsl --install` gives you WSL2 by default now. Check with
  `wsl -l -v` in PowerShell — the version column must say `2`. If it says `1`:
  `wsl --set-version Ubuntu 2`.
- **Work inside the Linux home directory** (`~`, which is `/home/you`), *not* under
  `/mnt/c/...`. Files on `/mnt/c` are on the Windows filesystem and every `git` and `uv`
  operation on them is several times slower. Clone your repositories into `~/`.
- **Everything from here on happens in the Ubuntu shell**, not in PowerShell and not in
  Git Bash. If you clone this course's repositories from the Windows side instead, you will
  hit the line-ending problem in troubleshooting §6.

### 2. VS Code + Remote-WSL

Install [VS Code](https://code.visualstudio.com/) on Windows — the normal Windows
installer. Then install the **WSL** extension, which is the one that belongs on the
Windows side.

Now, from your Ubuntu shell, in a project folder, run:

```bash
code .
```

VS Code opens on Windows but runs its language tools inside WSL; the first run also
downloads the VS Code Server into your Ubuntu. The bottom-left corner shows `WSL: Ubuntu`
when it is connected correctly.

**Only now** install the **Python** and **Ruff** extensions (`Ctrl Shift X`). Order
matters: extensions installed before you connect land on the Windows side, and an
extension on the Windows side does not run in a WSL window — Ruff will sit there linting
nothing and you will wonder why the editor never flags what CI rejects. Check each one
appears under the
**`WSL: Ubuntu — Installed`** heading in the Extensions pane; if it shows an
**Install in WSL: Ubuntu** button instead, click it.

### 3. uv

In the Ubuntu shell:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen the shell (the installer adds `uv` to your `PATH`). Then:

```bash
uv --version
uv python install 3.13
```

### 4. git and your SSH key

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use the email attached to your GitHub account. Then create an SSH key and add it to GitHub:

```bash
ssh-keygen -t ed25519 -C "you@example.com"      # press Enter at every prompt
cat ~/.ssh/id_ed25519.pub
```

Copy the printed line. On GitHub: **Settings → SSH and GPG keys → New SSH key**, paste,
save. Test it:

```bash
ssh -T git@github.com
```

You should see `Hi <your-username>! You've successfully authenticated`. (It also says
GitHub "does not provide shell access" — that is expected, not an error.)

### 5. Docker Desktop — at home, not in the lab

Skip it today; a red Docker line in your report is expected. Install it at home before
session 15, following [`02-docker-setup.md`](02-docker-setup.md), which has the WSL
integration step that everybody forgets.

Then jump to **Run the check**.

---

## macOS

You already have a Unix shell, so there is no step equivalent to WSL. Your shell is **zsh**,
which matters in step 3.

### 1. Command line tools and git

Open **Terminal** (`⌘ Space`, type "Terminal") and run:

```bash
git --version
```

If git is missing, macOS pops up a dialog offering to install the command line developer
tools — accept it, wait for it to finish, and run `git --version` again. If no dialog
appears:

```bash
xcode-select --install
```

Apple Silicon (M1/M2/M3/M4) needs nothing special anywhere in this lab. Neither does Intel.

### 2. VS Code

Download [VS Code](https://code.visualstudio.com/), then **drag it out of `~/Downloads`
and into `/Applications`** before you open it. A browser download leaves the app in
Downloads, and the `code`-command step below then fails with a permission error that does
not say what it wants.

Install the **Python** and **Ruff** extensions. You do **not** need the WSL extension —
that is a Windows-only thing; you are already native.

To get the `code` command in your terminal: open VS Code, press `⌘ Shift P`, type
`Shell Command: Install 'code' command in PATH`, and run it.

### 3. uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The installer edits your **zsh** startup files, not bash's. **Close the Terminal window and
open a new one**, then:

```bash
uv --version
uv python install 3.13
```

If `uv --version` says "command not found" in the new window, see troubleshooting §4.

### 4. git identity and your SSH key

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use the email attached to your GitHub account. Then:

```bash
ssh-keygen -t ed25519 -C "you@example.com"      # press Enter at every prompt
cat ~/.ssh/id_ed25519.pub
```

Copy the printed line. On GitHub: **Settings → SSH and GPG keys → New SSH key**, paste,
save. Test it:

```bash
ssh -T git@github.com
```

You want `Hi <your-username>! You've successfully authenticated`.

### 5. Docker Desktop — at home, not in the lab

Skip it today; a red Docker line in your report is expected. Install it at home before
session 15, following [`02-docker-setup.md`](02-docker-setup.md), which covers the Apple
Silicon / Intel choice and Gatekeeper.

Then jump to **Run the check**.

---

## Linux

### 1. Shell, git and VS Code

You are already where the course lives. Install `git` and VS Code from your distribution's
package manager — on Debian/Ubuntu:

```bash
sudo apt update && sudo apt install -y git curl
```

Install VS Code from [code.visualstudio.com](https://code.visualstudio.com/) or your
distribution's store, plus the **Python** and **Ruff** extensions. No WSL extension.

### 2. uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen the shell, then:

```bash
uv --version
uv python install 3.13
```

### 3. git identity and your SSH key

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

ssh-keygen -t ed25519 -C "you@example.com"      # press Enter at every prompt
cat ~/.ssh/id_ed25519.pub
```

Paste the printed line into GitHub under **Settings → SSH and GPG keys → New SSH key**,
then test with `ssh -T git@github.com`.

### 4. Docker — at home, not in the lab

Skip it today. You want Docker Engine, not Docker Desktop; the steps are in
[`02-docker-setup.md`](02-docker-setup.md), to do at home before session 15.

---

## Run the check

Clone the course materials and run the setup check:

```bash
cd ~
git clone git@github.com:esade-swdev-2026/software-development-course-materials.git
cd software-development-course-materials
bash scripts/setup-check.sh
```

It prints a report, writes `setup-report.md`, and then prints the exact commands for the
next step **with your own GitHub username already filled in**. Every line of the report is
pass or fail with a fix.

---

## Push your first file

Your group repository already exists — it was created for you before this session.

**You each push to your own branch.** Four or five of you are pushing to the same
repository within the same twenty minutes; if you all push to `main`, the first one
succeeds and the rest are rejected. A branch per person means nobody collides, and it is
how you will work for the rest of the term anyway.

```bash
cd ~
git clone git@github.com:esade-swdev-2026/<your-group>.git
cd <your-group>

git switch -c setup/<your-github-username>

mkdir -p setup-reports
cp ~/software-development-course-materials/setup-report.md \
   setup-reports/<your-github-username>.md

git add setup-reports/
git commit -m "add setup report"
git push -u origin setup/<your-github-username>
```

Replace `<your-group>` with your group's repository name and
`<your-github-username>` with your GitHub username — or just copy the commands the check
script printed, which already have the username in them.

**Push even if lines in the report are red.** Then open your repository on GitHub, click
the **Actions** tab, and watch the `check` workflow run on your branch. Green means the
referee accepts the repository. Red on the report but green on Actions is fine — the report
is a to-do list for you; Actions checks the repository.

---

## Troubleshooting — the ones that actually happen

Search this table for the text your machine actually printed, not for what you think the
problem is.

| What you see | Where |
|---|---|
| `wsl --install` fails, or Ubuntu never appears | §1 |
| "This app can't run on your PC" when you open Ubuntu | §9 |
| `Failed to connect to system scope bus` during `apt upgrade` | not an error — Windows step 1 |
| `docker: command not found` inside WSL | [`02-docker-setup.md`](02-docker-setup.md) §1 |
| `permission denied ... unix:///var/run/docker.sock` | [`02-docker-setup.md`](02-docker-setup.md) §2 |
| "Docker Desktop cannot be opened because the developer cannot be verified" | [`02-docker-setup.md`](02-docker-setup.md) §3 |
| `Are you sure you want to continue connecting (yes/no/[fingerprint])?` | §10 |
| `Permission denied (publickey)`, or `git push` asks for a password | §3 |
| `uv: command not found` | §4 |
| Permission errors from the `uv` installer, but `uv` then works | §4 |
| Everything times out — VPN, proxy, managed laptop | §5 |
| `$'\r': command not found`, or `bash\r: No such file or directory` | §6 |
| `! [rejected] ... (non-fast-forward)` | §8 |

### 1. `wsl --install` fails, or Ubuntu never installs *(Windows)*

Virtualization is disabled in your BIOS/UEFI. Reboot, enter firmware setup (usually `F2`,
`F10`, `Del` or `Esc` during boot), and enable **Intel VT-x** / **AMD-V** /
**SVM Mode** / **Virtualization Technology**. Also ensure "Virtual Machine Platform" is on
in Windows: `wsl --install --no-distribution` after enabling it in *Turn Windows features
on or off*.

This entry is for `wsl --install` itself failing. If the install *succeeded* but Ubuntu
will not open, see §9.

### 2. `docker: command not found` inside WSL, but Docker Desktop is running *(Windows)*

Moved, with the rest of the Docker material, to
[`02-docker-setup.md`](02-docker-setup.md) §1.

### 3. `git push` asks for a username and password, or `Permission denied (publickey)`

Your SSH key is not on GitHub, or you cloned with an `https://` URL instead of `git@`.
Check the remote: `git remote -v`. If it starts with `https://`, switch it:

```bash
git remote set-url origin git@github.com:esade-swdev-2026/<your-group>.git
```

Then re-run `ssh -T git@github.com` and fix the key until it greets you by name.

### 4. `uv: command not found` after installing it

The installer added `uv` to your shell's startup file, but this shell started before that.
**Close the terminal and open a new one.** If it still fails, the installer wrote to a
startup file your shell does not read:

```bash
echo $SHELL                       # which shell are you actually running?
source $HOME/.local/bin/env       # works for this session, in any shell
```

To make it permanent, add `export PATH="$HOME/.local/bin:$PATH"` to the right file:
`~/.bashrc` if `$SHELL` says bash (WSL2 Ubuntu, most Linux), `~/.zshrc` if it says zsh
(**every recent macOS**). The `Login shell` line in your setup report is the same
information.

**A related but harmless case.** The installer may print permission errors for
`~/.bash_profile` or `~/.config/fish/conf.d` — startup files for shells you do not use. If
`uv --version` then works in a **new** terminal, those two messages are finished business
and nothing needs fixing. This is the exception, not the rule: everywhere else in this
course, red text means something is wrong and you read it.

### 5. Everything times out — corporate laptop, VPN, or proxy

A managed device or an always-on VPN can block `astral.sh`, `pypi.org`, `github.com:22`, or
Docker's registries. The `PyPI reachable` line in your report is the one that catches this.
Try: GitHub over HTTPS port 443 instead of SSH (`ssh -T -p 443 git@ssh.github.com` and set
`~/.ssh/config` accordingly); disconnect the VPN for the install; or, if the device is
locked down so hard that nothing installs, use a **lab machine** or **pair with a
neighbour** for today and finish your own setup before Tuesday. Nothing downstream is
blocked on any one laptop.

### 6. `$'\r': command not found`, or `/usr/bin/env: 'bash\r': No such file or directory` *(Windows)*

You cloned the repository with Git for Windows on the Windows side instead of from inside
the Ubuntu shell. Git for Windows rewrites line endings to CRLF, and a Linux shell cannot
run a script with carriage returns in it. Delete the clone and re-clone it **from the
Ubuntu shell**, into your Linux home:

```bash
cd ~
rm -rf software-development-course-materials
git clone git@github.com:esade-swdev-2026/software-development-course-materials.git
```

### 7. "Docker Desktop cannot be opened because the developer cannot be verified" *(macOS)*

Moved to [`02-docker-setup.md`](02-docker-setup.md) §3.

### 8. `! [rejected] ... (non-fast-forward)` when you push

You are pushing to `main`, and a teammate pushed first. Do not try to merge — switch to
your own branch and push that instead:

```bash
git switch -c setup/<your-github-username>
git push -u origin setup/<your-github-username>
```

### 9. "This app can't run on your PC", or Ubuntu will not start after the reboot *(Windows)*

`wsl --install` finished, but the Start menu entry is a placeholder Windows created before
the Ubuntu image finished downloading. From **PowerShell as Administrator**:

```powershell
wsl --update
wsl --install -d Ubuntu
```

Then open Ubuntu again. If instead `wsl --install` itself is the command that failed, you
have the other problem — see §1.

### 10. `Are you sure you want to continue connecting (yes/no/[fingerprint])?`

```
The authenticity of host 'github.com (140.82.121.3)' can't be established.
ED25519 key fingerprint is SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

This is the first time your machine has ever talked to `github.com`, and SSH is asking you
to confirm you trust the server. It is not an error and it says nothing about your key.
Type `yes` — the whole word — and press Enter. You will not be asked again.

It happens on **every** operating system, at the `ssh -T git@github.com` step. The setup
check script never shows it to you, because it accepts new hosts on its own.

### 11. `permission denied while trying to connect to the Docker daemon socket`

Moved to [`02-docker-setup.md`](02-docker-setup.md) §2.
