<!-- TARGET REPO: software-development-course-materials (PUBLIC). Student-facing. -->

# Lab 02 — Docker, installed at home

**Deadline: before session 15, Tuesday 10 November.** Session 15 runs containers in the
room; session 16 containerises your project. Both assume `docker` works on your machine.

This is the final part of the setup lab we deliberately left out on 18 September.

It requires a bit of time for the download and budget around **4 GB of disk**.

---

## What "done" looks like

```bash
docker run --rm hello-world
```

It prints *"Hello from Docker!"*. If you see it, you are finished;
skip to **Tell the check script** at the bottom.

---

## Before you start, on any machine

- **4 GB of free disk**, more once you start building images.
- **Virtualization enabled in the BIOS/UEFI.** On most laptops it already is. If Docker or
  WSL complains about it, see troubleshooting §4.
- A **managed or locked-down laptop** may refuse the install outright. That is not a
  disaster — read *If you genuinely cannot install it* at the end, and let the lecturer know early.

---

## Windows

You installed WSL2 and Ubuntu in session 3. Docker Desktop plugs into that, and you keep
typing `docker` in the **Ubuntu** shell, never in PowerShell.

1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) **on Windows itself — not inside Ubuntu.**
   Accept the default **WSL 2 based engine**; do not choose Hyper-V.
2. Start Docker Desktop and leave it running. The whale icon in the system tray must say
   *running* — the `docker` command is only a client, and it talks to that.
3. **Settings → Resources → WSL integration** → turn on your Ubuntu distro →
   **Apply & restart**. This step is the one everybody forgets.
4. Open a **new** Ubuntu shell and test:

```bash
docker run --rm hello-world
```

Docker Desktop must be running whenever you use `docker`. It does not start with Windows
unless you tell it to, under **Settings → General → Start Docker Desktop when you sign in**.

---

## macOS

1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) —
   the **Apple Silicon** build for M1/M2/M3/M4 machines, the **Intel** build otherwise. The
   wrong one will not run.
2. Drag it to Applications and open it **once from Applications** so macOS lets it run. If
   Gatekeeper refuses, see troubleshooting §3.
3. Leave it running, then in your terminal:

```bash
docker run --rm hello-world
```

**A lighter alternative**: [Colima](https://github.com/abiosoft/colima) (`brew install
colima docker`, then `colima start`) gives you the same `docker` command without Docker
Desktop. Everything in this course works with it. Choose it if Docker Desktop's resource
use bothers you — and know that you are then off the supported path, as per the contract
in Lab 00.

---

## Linux

You do not need Docker Desktop. Install **Docker Engine** from your distribution — on
Debian or Ubuntu, follow Docker's own repository instructions rather than `apt install
docker.io`, which ships an old version:

<https://docs.docker.com/engine/install/>

Then let your user talk to the daemon without `sudo`:

```bash
sudo usermod -aG docker $USER
```

Log out and back in — a new terminal is not enough — and test:

```bash
docker run --rm hello-world
```

---

## Tell the check script

Re-run the setup check from the course materials repository. Its Docker line should now be
green:

```bash
cd ~/software-development-course-materials
git pull
bash scripts/setup-check.sh
```

You do not need to push a new report. If the Docker line is still red and the table below
does not explain why, bring it to office hours **before** session 15.

---

## Troubleshooting

| What you see | Where |
|---|---|
| `docker: command not found` in Ubuntu, Docker Desktop running | §1 |
| `permission denied ... /var/run/docker.sock` | §2 |
| "Docker Desktop cannot be opened because the developer cannot be verified" | §3 |
| "Virtualization support is disabled", or WSL2 refuses to start | §4 |
| `Cannot connect to the Docker daemon` | §5 |
| The download crawls, or `docker pull` times out | §6 |
| "no space left on device" | §7 |

### 1. `docker: command not found` inside WSL, but Docker Desktop is running *(Windows)*

Docker Desktop is not sharing itself with your WSL distro. Docker Desktop → **Settings →
Resources → WSL integration** → enable your Ubuntu distro → **Apply & restart**. Open a new
Ubuntu shell.

If `docker` is found but refuses with *permission denied*, that is §2.

### 2. `permission denied while trying to connect to the Docker daemon socket`

```
docker: permission denied while trying to connect to the Docker daemon socket
at unix:///var/run/docker.sock
```

Your Linux user is not in the `docker` group:

```bash
sudo usermod -aG docker $USER
```

On **Linux**, log out and back in. On **Windows**, opening a new shell is not enough — stop
the whole WSL virtual machine from PowerShell:

```powershell
wsl --shutdown
```

Then reopen Ubuntu and run `docker run --rm hello-world` again.

### 3. "Docker Desktop cannot be opened because the developer cannot be verified" *(macOS)*

Gatekeeper. **System Settings → Privacy & Security**, scroll to the bottom, and click
**Open Anyway** next to the Docker message. Or right-click the app in Applications and
choose **Open** rather than double-clicking it.

### 4. "Virtualization support is disabled" *(Windows, and some Linux laptops)*

Reboot into the firmware setup (usually F2, F10 or Del at power-on) and enable
**Intel VT-x** / **AMD-V** / **SVM**, depending on the chip. It is often under *Advanced*
or *Security*. Save and reboot. The same setting is what WSL2 needs, so if session 3 worked
this is unlikely to be your problem.

### 5. `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?`

The client is installed and the engine is not running.

- **Windows / macOS**: start Docker Desktop and wait until it says *running*.
- **Colima**: `colima start`.
- **Linux**: `sudo systemctl start docker`, and `sudo systemctl enable docker` so it comes
  back after a reboot.

### 6. The download crawls, or `docker pull` times out

A VPN, a corporate proxy or TLS interception, exactly as in Lab 00 §5. Disconnect the VPN
for the install, or do it on a different network. Docker Hub also rate-limits anonymous
pulls: if you see `toomanyrequests`, wait an hour or sign in with a free Docker Hub account
(`docker login`).

### 7. "no space left on device"

Images are large and Docker never cleans up on its own:

```bash
docker system df          # what is using the space
docker system prune -a    # delete everything not currently in use
```

`prune -a` removes every image you are not running. It is safe here — nothing in this
course is stored inside an image — and it is the standard fix.

---

## If you genuinely cannot install it

Some laptops are locked down hard enough that none of this works. Say so before session 15,
and you will pair with someone in your group for the in-class labs.

You will not lose marks for it: from session 16 your Dockerfile is built by CI, on GitHub's
machines, and that build is what is marked. Docker on your own laptop makes the work far
more comfortable — it is not the thing being assessed.
