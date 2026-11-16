#!/usr/bin/env python3
"""Build <package>/llms.md: one Markdown file an LLM can read to use a package.

The file is three parts:
  1. a hand-written orientation (PACKAGES[name]["intro"] below),
  2. the package README, verbatim,
  3. an API reference generated from the installed package: every public name,
     its signature and its full docstring.

The package must be importable (installed from PyPI or from a local clone):

    pip install granada                      # or: pip install -e ../bahamas
    python .github/scripts/build_llms.py granada --readme ../bahamas/README.md

Writes <name>/llms.md in the website root.
"""
import argparse
import importlib
import inspect
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://habrahamyan.github.io"

PACKAGES = {
    "granada": {
        "modules": ["granada", "granada.feynman", "granada.schwinger", "granada.decompose"],
        # granada.decompose has no __all__; these are its public entry points.
        "extra": {"granada.decompose": ["decompose", "Decomposition", "Structure"]},
        "intro": """\
granada is a Python library for **exact, symbolic** manipulation of
perturbation-theory integrands built from 3-vectors (cosmological
large-scale-structure perturbation theory in particular): from an integrand
written as on paper to a list of master integrals with rational coefficients,
with LaTeX/HTML and Mathematica output. Nothing in it is numerical.

## Quick facts

- Install: `pip install granada` (Python >= 3.10, depends only on sympy).
  `pip install "granada[notebook]"` adds IPython so `render()` shows inline in notebooks.
- Licence: MIT. Author: Hrach Abrahamyan.
- Human-readable overview: {page}

## How the package is organised

- **`granada`** (the core): vectors (`Vector`, `External`, `ref`), scalar products
  (`SP`, `mag`), spherical Bessels (`j`, `jprime`), kernels (`F2`, `G2`, ..., `PL`,
  `FKernel`, `GKernel`), reduction to masters (`reduce`, `align`, `fold`,
  `refAverage`, `refReduce`), tensor algebra (`g`, `peel`, `project`),
  `fullSimplify`, and output (`render`, `juxtapose`, `latex`, `wl`, `getTower`).
- **`granada.feynman`**: the Feynman pipeline. `feynmanReduce()` runs
  peel -> project -> average on a term with the axis z-hat; `evalTower()` evaluates the
  result at a master integral; plus `denominators`, `partialFraction`,
  `shiftBessel`, `toI25`.
- **`granada.schwinger`**: the Schwinger pipeline. `schwingerReduce()` writes
  Fourier-type loop integrals as Schwinger parameters acting on one Gaussian
  Z(A, J), and carries factorizing terms to closed forms (`getFinalExpression`).
- **`granada.decompose`**: `decompose(n, dim)` writes a rank-n tensor in
  products of delta_ij and rhat_i. Standalone; imports nothing else from granada.

The two pipelines import the core and never each other.

## Rules an assistant should follow when writing granada code

1. Write the integrand as it stands; **never call `.expand()`** yourself. `reduce()` expands.
2. Build each pipeline's input with **its own** dressed kernels: `granada.feynman.Fx`
   (phase in r) and `granada.schwinger.Fx` (phase in x) are different objects.
3. Exponents must be rational or **linear** in spectral indices (`n`, or several
   via `PL(k1, "n1")`); no `n**2`, no `1/n`, no irrational coefficients.
4. **One Bessel per term** (a sum of terms with different Bessels is fine).
   No Bessel in a denominator.
5. Odd powers of a compound magnitude such as `mag(k+p)` are genuine masters, not
   unfinished reductions. Write `mag(k+p)`, never a root of an expanded sum.
6. Pass external momenta as `frozen` to `reduce()` when a Bessel argument is compound.
7. Every call logs to stderr; `granada.verbose(False)` silences it.
8. If unsure about a function, check its entry in the API reference at the end of this file.

The full README follows, then the API reference.
""",
    },
}


def first_para(doc):
    return doc.split("\n\n", 1)[0].replace("\n", " ").strip() if doc else ""


def signature(obj):
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return "(...)"


def demote_headings(md, levels=1):
    """Push every Markdown heading down, skipping fenced code blocks."""
    out, fence = [], False
    for line in md.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and re.match(r"^#{1,5} ", line):
            line = "#" * levels + line
        out.append(line)
    return "\n".join(out)


def api_reference(cfg):
    parts = ["# API reference", "",
             "Generated from the installed package: every public name with its signature "
             "and docstring. Classes list their public methods.", ""]
    for modname in cfg["modules"]:
        mod = importlib.import_module(modname)
        names = list(getattr(mod, "__all__", None) or []) + cfg.get("extra", {}).get(modname, [])
        names = [n for n in dict.fromkeys(names) if not n.startswith("_")]
        parts += [f"## `{modname}`", ""]
        for name in names:
            obj = getattr(mod, name)
            if inspect.ismodule(obj):
                continue
            # Re-exports of the core (peel, project) are documented once, in the core.
            home = getattr(obj, "__module__", "") or ""
            if modname != "granada" and home and not home.startswith(modname) and modname != "granada.decompose":
                core = importlib.import_module("granada")
                if getattr(core, name, None) is obj:
                    parts += [f"### `{modname}.{name}`", "", f"Same object as `granada.{name}`.", ""]
                    continue
            if inspect.isclass(obj):
                parts += [f"### class `{modname}.{name}{signature(obj)}`", ""]
            elif callable(obj):
                parts += [f"### `{modname}.{name}{signature(obj)}`", ""]
            else:
                parts += [f"### `{modname}.{name}`", "", f"Constant: `{obj!r}`"[:300], ""]
                continue
            doc = inspect.getdoc(obj)
            parts += ["```text", doc, "```", ""] if doc else ["_No docstring._", ""]
            if inspect.isclass(obj):
                methods = []
                for mname, m in inspect.getmembers(obj):
                    if mname.startswith("_") or mname not in obj.__dict__:
                        continue
                    if callable(m) or isinstance(m, property):
                        sig = "" if isinstance(m, property) else signature(m)
                        desc = first_para(inspect.getdoc(m))
                        methods.append(f"- `{mname}{sig}`" + (f": {desc}" if desc else ""))
                if methods:
                    parts += ["Public methods and properties:", ""] + methods + [""]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package", choices=sorted(PACKAGES))
    ap.add_argument("--readme", required=True, type=Path)
    args = ap.parse_args()

    cfg = PACKAGES[args.package]
    pkg = importlib.import_module(args.package)
    version = getattr(pkg, "__version__", "unknown")
    page = f"{SITE}/{args.package}/"

    readme = args.readme.read_text()
    # Drop the README's own H1; this file has one.
    readme = re.sub(r"\A# [^\n]*\n+", "", readme)

    doc = "\n".join([
        f"# {args.package} {version}: reference for LLMs and coding assistants",
        "",
        f"> This file describes **{args.package} {version}** (generated {date.today().isoformat()}). "
        f"It is meant to be read in full by an AI assistant before writing code that uses "
        f"{args.package}. Canonical URL: {page}llms.md",
        "",
        cfg["intro"].format(page=page),
        "---",
        "",
        "# README",
        "",
        demote_headings(readme),
        "",
        "---",
        "",
        api_reference(cfg),
    ])
    out = ROOT / args.package / "llms.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(doc.rstrip() + "\n")
    print(f"Wrote {out.relative_to(ROOT)} ({len(doc) // 1024} KB)")


if __name__ == "__main__":
    main()
