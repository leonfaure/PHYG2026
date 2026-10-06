"""PHYG 2026 — environment self-test.   Run with:  pixi run selftest

Checks that the packages import and that the command-line tools of the course
actually run on a tiny example. Takes a few seconds, needs no data file, and
writes nothing outside a temporary directory.
"""
import importlib, platform, shutil, subprocess, sys, tempfile
from pathlib import Path

results = []


def check(name, fn):
    try:
        detail = fn()
        results.append((name, True))
        print("  ok    %-28s %s" % (name, detail or ""))
    except Exception as exc:                      # report, never crash
        results.append((name, False))
        print("  FAIL  %-28s %s" % (name, str(exc).strip().splitlines()[-1] if str(exc).strip() else type(exc).__name__))


def run(cmd, cwd=None, stdin=None):
    return subprocess.run(cmd, cwd=cwd, input=stdin, text=True, capture_output=True, timeout=120)


# ---- Python packages -------------------------------------------------------
def pkg(name):
    def f():
        return getattr(importlib.import_module(name), "__version__", "")
    return f


# ---- command-line tools ----------------------------------------------------
def on_path(tool):
    def f():
        path = shutil.which(tool)
        if not path:
            raise RuntimeError("'%s' not found — is `pixi run` being used?" % tool)
        return ""
    return f


def version(tool, flag="--version"):
    def f():
        on_path(tool)()
        out = run([tool, flag])
        text = (out.stdout + out.stderr).strip().splitlines()
        if out.returncode != 0 or not text:
            raise RuntimeError("'%s %s' failed" % (tool, flag))
        return text[0][:40]
    return f


PROTEINS = {
    "A": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    "B": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVA",
    "C": "MKTAYIAKQRQLSFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    "D": "MKSAYIAKQRQISFVKTHFSRQLDERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVRVKALPDAQFEVV",
}


def clustal():
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in.fa", Path(tmp) / "out.fa"
        src.write_text("".join(">%s\n%s\n" % kv for kv in PROTEINS.items()))
        out = run(["clustalo", "-i", str(src), "-o", str(dst), "--outfmt=fasta", "--force"])
        if out.returncode != 0 or dst.read_text().count(">") != 4:
            raise RuntimeError("clustalo did not align the 4 test sequences")
    return "aligned 4 sequences"


def phylip():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        n, length = len(PROTEINS), len(next(iter(PROTEINS.values())))
        (tmp / "infile").write_text(
            " %d %d\n" % (n, length)
            + "".join("%-10s%s\n" % ("SEQ000000" + k, s) for k, s in PROTEINS.items()))
        run(["protdist"], cwd=tmp, stdin="Y\n")
        if not (tmp / "outfile").exists():
            raise RuntimeError("protdist produced no distance matrix")
        (tmp / "infile").unlink(); (tmp / "outfile").rename(tmp / "infile")
        run(["neighbor"], cwd=tmp, stdin="Y\n")
        tree = tmp / "outtree"
        if not tree.exists() or tree.read_text().count("SEQ") != 4:
            raise RuntimeError("neighbor produced no tree")
    return "protdist + neighbor built a 4-leaf tree"


def plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with tempfile.TemporaryDirectory() as tmp:
        plt.plot([0, 1], [0, 1]); plt.savefig(Path(tmp) / "x.png"); plt.close()
        if not (Path(tmp) / "x.png").stat().st_size:
            raise RuntimeError("empty figure")


def kernel():
    out = run([sys.executable, "-m", "jupyter", "kernelspec", "list"])
    if out.returncode != 0 or "python3" not in out.stdout:
        raise RuntimeError("no python3 Jupyter kernel found")


print("PHYG 2026 self-test — Python %s on %s %s\n" % (platform.python_version(), platform.system(), platform.machine()))
print("Python packages")
for p in ("numpy", "scipy", "pandas", "matplotlib", "Bio", "toytree", "ipywidgets", "jupyterlab"):
    check(p, pkg(p))
check("matplotlib draws a figure", plot)
check("Jupyter kernel", kernel)

print("\nTools used in TME1")
check("clustalo", version("clustalo"))
check("protdist", on_path("protdist"))
check("neighbor", on_path("neighbor"))
check("clustalo aligns", clustal)
check("PHYLIP runs", phylip)

print("\nTools used in later sessions")
for t in ("samtools", "bedtools", "mosdepth"):
    check(t, version(t))
check("igv", on_path("igv"))

bad = [n for n, ok in results if not ok]
print()
if bad:
    print("%d check(s) FAILED: %s" % (len(bad), ", ".join(bad)))
    print("If almost everything failed, you probably ran `python selftest.py` directly:")
    print("use `pixi run selftest` instead.")
    print("Send us this whole output, plus the output of `pixi info`.")
    sys.exit(1)
print("All %d checks passed — your environment is ready." % len(results))
