# PHYG 2026 — Phylogénie et génomique comparative

## Setting up your machine

You need to do this **once**, before TME1. Ten minutes, mostly download time.

Everything in this course runs from a single tool, `pixi`. You do **not** need
Anaconda, you do not need `pip install`, and you never have to edit your `PATH`
or your `.bashrc`.

---

## Step 0 — Windows only: install WSL2 first

**Read this before installing anything else.**

This course uses compiled bioinformatics tools — PHYLIP, Clustal Omega, samtools,
bedtools, mosdepth. **None of them has a Windows build**. Five of the seven sessions need them,
starting with TME1.

So install WSL2 (Windows Subsystem for Linux) **now**, and do the whole course
inside it. Installing on Windows first and switching later means installing
everything twice.

In PowerShell **as administrator**:

```powershell
wsl --install
```

Reboot, let Ubuntu finish its first-run setup (it asks for a username and
password), then open the **Ubuntu** terminal from the Start menu. Everything from
Step 1 on happens in that terminal, not in PowerShell.

From WSL's point of view you are running Linux, so the rest of this page applies
to you unchanged.

> **Your files.** Work inside the Linux home directory (`~/`), not under
> `/mnt/c/`. Cross-filesystem access is slow, and TME7 handles large files.
> You can reach that folder from Windows Explorer by typing `\\wsl$` in the
> address bar.

> **No administrator rights on your machine?** Come and talk to us before TME1 —
> do not wait. There is no way to run this course natively on Windows.

**macOS and Linux users** — including Apple Silicon — have nothing to do here. The
tools install natively. Go to Step 1.

> **Intel Macs** (`osx-64`) are covered by the lock file but have **not been tested**.
> They should work; if not, tell us.

---

## Step 1 — Install pixi

In a terminal — on Linux, macOS, or inside WSL2:

```sh
curl -fsSL https://pixi.sh/install.sh | sh
```

Close the terminal, open a new one, and check:

```sh
pixi --version
```

<details>
<summary>Already have conda, brew or winget? You can also install pixi with one of these commands</summary>

```sh
conda install -c conda-forge pixi     # any platform
brew install pixi                     # macOS
```
</details>

## Step 2 — Get the course material

```sh
git clone https://github.com/leonfaure/PHYG2026.git
cd PHYG2026
```

## Step 3 — Check that everything works

```sh
pixi run selftest
```

The first run downloads the environment (a few minutes, once). The check then
takes a few seconds and ends with `All ... checks passed` when your machine is
ready. If any line says `FAIL`, send us the whole output (see the last section).

## Step 4 — Start working

```sh
pixi run lab
```

JupyterLab opens in your browser. If it does, you are done: the material for each
session will be added to this repository before the session — update it with
`git pull`.

That is the whole setup. `pixi run lab` is the only command you need, for every
session of the course — there is no environment to choose or switch between.

---

## What `pixi run lab` actually does

`lab` is a named task defined in `pixi.toml`; it runs `jupyter lab`. The `pixi run`
part is what matters:

1. it reads `pixi.lock` and makes sure the environment on disk matches it exactly,
   installing it the first time and doing nothing on later runs;
2. it runs the command *inside* that environment — the right `python`, the right
   `jupyter`, the right PHYLIP binaries on `PATH` — without permanently changing
   your shell.

There is no `activate` step and no environment to remember to switch into. When the
command exits, your shell is exactly as it was. The environment itself lives in a
`.pixi/` folder **inside the project**: it touches nothing else on your system, and
deleting that folder removes every trace of it.

## Already using conda?

You can keep conda for your other work — pixi does not interfere with it, and you
do not need to deactivate anything. For this course, use pixi anyway.

The reason is what gets pinned. A conda `environment.yml` lists the packages you
*asked for*; the exact versions are worked out again on each machine, so your
environment can quietly differ from your teammate's and from the one we grade in.
`pixi.lock` is part of this repository and records the exact build of all ~245
packages, resolved for Linux, macOS Intel and Apple Silicon together.
Everyone gets the same environment by construction.

It also means you never install PHYLIP by hand. No `phylip-3.697.tar.gz`, no
`export PATH=...` in your `.bashrc`: `protdist`, `neighbor`, `pars` and the rest
are simply there when `pixi run` starts.

The two also live in different places: conda environments sit in a central folder
shared by every project (`~/miniconda3/envs/`), while a pixi environment sits in
`.pixi/` inside this project and disappears completely when you delete that folder.


## Windows: the install fails with DNS errors, or the Wi-Fi drops

Only if `pixi install` (or the first `pixi run lab`) fails with
`dns error … Try again`, or your Wi-Fi disconnects while it downloads. WSL2's
default network setup can overload some Wi-Fi adapters and routers. Switch WSL to
*mirrored* networking (Windows 11 22H2 or later). In PowerShell:

```powershell
@"
[wsl2]
networkingMode=mirrored
dnsTunneling=false
autoProxy=false
"@ | Set-Content -Path "$env:USERPROFILE\.wslconfig" -Encoding ascii
wsl --update
wsl --shutdown
```

Reopen Ubuntu and run `pixi install` again. It resumes where it stopped. To undo,
delete `%USERPROFILE%\.wslconfig` and run `wsl --shutdown`.

On Windows 10, or if that does not help, do the first `pixi install` from a phone
hotspot or over Ethernet. It is only the one-time download that is heavy; afterwards
everything is in `.pixi/` and `pixi run lab` needs no network.

---

## If something goes wrong

```sh
pixi clean && pixi install     # rebuild the environment from scratch
```

If that does not fix it, send the **full** error message — the whole traceback, not
a screenshot of the last line — along with the output of `pixi info`.
