# granada 0.1.0: reference for LLMs and coding assistants

> This file describes **granada 0.1.0** (generated 2026-11-16). It is meant to be read in full by an AI assistant before writing code that uses granada. Canonical URL: https://habrahamyan.github.io/granada/llms.md

granada is a Python library for **exact, symbolic** manipulation of
perturbation-theory integrands built from 3-vectors (cosmological
large-scale-structure perturbation theory in particular): from an integrand
written as on paper to a list of master integrals with rational coefficients,
with LaTeX/HTML and Mathematica output. Nothing in it is numerical.

## Quick facts

- Install: `pip install granada` (Python >= 3.10, depends only on sympy).
  `pip install "granada[notebook]"` adds IPython so `render()` shows inline in notebooks.
- Licence: MIT. Author: Hrach Abrahamyan.
- Human-readable overview: https://habrahamyan.github.io/granada/

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

---

# README

Formal 3-vector algebra for perturbation-theory integrands, with LaTeX and
Mathematica output, and two independent pipelines that carry an integrand to
master integrals:

* the **Feynman pipeline**, `granada.feynman`, takes a term with the axis
  $\hat{\boldsymbol z}$, $\Phi\prod_a g(\boldsymbol v_a)$, through
  peel → project → average to scalar integrands sorted by powers of
  $\nu=\hat{\boldsymbol z}\cdot\hat{\boldsymbol r}$, and from there to the
  tower at your master integral (`evalTower`), the propagator structures,
  partial fractions and the five-propagator two-loop integral;
* the **Schwinger pipeline**, `granada.schwinger`, writes every term of a
  Fourier-type integral as Schwinger parameters acting on one Gaussian,
  $Z(A,J)$, and carries the terms that factorize to closed forms.

Both stand on one core: the vectors and scalar products, the kernels,
$g(\boldsymbol v)$ and the tensor algebra that takes the axis off, the
average over the direction of $\boldsymbol r$, the reduction to masters and the
renderer. The pipelines import the core and never each other, so each gives
exactly the results it gave on its own. What they share is the notation the
input is written in and the page the output is read on.

A third module, **`granada.decompose`**, writes a rank-$n$ tensor as a sum over
every product of $\delta_{ij}$ and $\hat r_i$, with coefficients
$c=G^{-1}t$ from its full contractions. The core's `project()` stands on it,
but it imports nothing from granada, and is useful on its own:

```python
from granada.decompose import decompose
dec = decompose(4, dim=3)       # dec.structures, dec.coefficients, dec.to_latex()
```

`python -m granada.decompose 4` writes the same as an HTML page.

Each of the three loads only what it needs: `import granada.feynman` never
loads the Schwinger pipeline, and `import granada.schwinger` never loads the
Feynman one.

Nothing here is numerical. A vector is a name, a scalar product is a pair of
names, and an exponent is a rational or a linear form in the spectral index
`n`, or in several independent ones, `PL(k1, "n1") * PL(k2, "n2")`. The point is to get from an integrand as you would write it on paper to
a list of masters with rational coefficients, without hand algebra.

Every vector is an integration variable, except the reference vector `ref`,
the bold $\boldsymbol r$ whose magnitude $r$ every Bessel carries, and, in the
Schwinger pipeline, the external positions $\boldsymbol x$ and $\boldsymbol y$
(`External`).

### Layout

```
src/granada/
  __init__.py         the core's names; the pipelines as granada.feynman and granada.schwinger

  # the core — notation, algebra, tensor algebra, rendering — shared by both pipelines
  scaffold.py         vectors, External x and y, scalar products, Puiseux polynomials (no rendering)
  bessel.py           j_ell(|v| r), terms, sums over Bessel structures
  functions.py        sin, cos, cexp, I  (opaque, above the Bessels)
  kernels.py          F2, G2, F3, G3, F4, G4, PL, the spectral index N and spectralIndex();
                      FKernel, GKernel of any order
  written.py          how an expression was typed, for display
  reduction.py        reduce() — expand, shift, expand
  symmetry.py         fold(), align() — what the integral allows, not the algebra
  refaverage.py       refAverage() — the average over the direction of ref
  pipeline.py         refReduce() — refAverage, reduce, align, fold, render
  mathematica.py      wl(), getTower()
  fullsimplify.py     fullSimplify() — a sum of Gamma functions of spectral indices, as short as it goes
  tensor.py           g, GString, AxialIntegrand, AxialSum; peel() and project() — the tensor algebra
  decompose.py        decompose() — a rank-n tensor in delta and rhat; stands on its own
  dressed.py          G — the dressed velocity kernel, the same in both pipelines
  tex.py              render(), juxtapose(), latex()
  page.py             the HTML page render() writes: cards and sections, typeset as they are read
  _stage.py           the marker of every stage object, and the gate that refuses them
  _log.py             the terminal logs, verbose()

  feynman/            the Feynman pipeline
    dressed.py        Fx, Fy with their phase in r; G
    stages.py         average(), feynmanReduce() — Average, Entry, Ledger, LedgerSum
    propagators.py    denominators() — the propagator structures, genuine and n-dependent
    partialfraction.py  partialFraction() — every term down to independent propagators
    shiftbessel.py    shiftBessel() — every Bessel on one momentum, term by term
    fiveline.py       toI25() — outer k1 integral times the five-propagator integral
    evaltower.py      evalTower(), master() — the tower at your master integral, simplified

  schwinger/          the Schwinger pipeline
    dressed.py        Fx, Fy with their phase in x and y; G
    ledger.py         SchwingerTerm, SchwingerLedger — the input, one term per product
    generators.py     getFamily(), getGenerators() — F(T), P and D of one term
    braid.py          getBraid(), assemblePartitionFunction() — (A, J), Z(A, J), det A over the blocks
    calculus.py       the derivatives of Z, in M = A^-1 and w = A^-1 J
    form.py           getSchwingerForm(), schwingerReduce() — the whole pipeline
    final.py          getFinalExpression(), master() — fully factorized terms as master integrals
    _poly.py          exact sparse polynomials and their LaTeX

tests/
  helpers.py          plain-float vectors, spherical Bessels and LaTeX checks, for every suite
  core/               the kernels, spectral indices, fullSimplify
  feynman/            the Feynman pipeline, its stages 1 and 2, its tools, and the renderer
  schwinger/          the Schwinger pipeline

examples/
  both_pipelines.py   the shared notation, each pipeline's tools and one renderer, in one script
  refaverage_examples.py  a gallery of terms and their refAverage
```

The dependency runs one way. In the core, `scaffold` knows nothing about
Bessels, and neither knows anything about output. Nothing in the core
imports a pipeline, and neither pipeline imports the other.

**What the pipelines share, and what they do not.** Everything in the core is
imported from `granada` and is the same object in both pipelines. The names
both pipelines have are reached through the pipeline, because they mean
different things in each:

| name | `granada.feynman` | `granada.schwinger` |
|---|---|---|
| `Fx(k1, ..., kn)` | $F_n\,e^{-i\boldsymbol k\cdot\boldsymbol r/2}$ | $F_n\,e^{i\boldsymbol k\cdot\boldsymbol x}$ |
| `Fy(k1, ..., kn)` | $F_n\,e^{+i\boldsymbol k\cdot\boldsymbol r/2}$ | $F_n\,e^{i\boldsymbol k\cdot\boldsymbol y}$ |
| `G(k1, ..., kn)` | $G_n\,g(\boldsymbol k)$ | the same object |
| `master(...)` | your $M(\ell,a_1,\dots;r)$, for `evalTower` | $\mathcal M(e;Q)=\int_0^\infty dz\,z^e e^{-Q/(4z)}$, derived |

with $\boldsymbol k=\boldsymbol k_1+\dots+\boldsymbol k_n$. The Feynman pipeline
writes its phases at $\boldsymbol x=-\boldsymbol r/2$, $\boldsymbol y=\boldsymbol r/2$
from the start; the Schwinger pipeline keeps $\boldsymbol x$ and $\boldsymbol y$
apart unless asked (`midpoint=True`). `peel` and `project` are the core's;
`granada.feynman` re-exports them beside `average`, its own stage 3.

### Install

```bash
pip install granada
```

It needs Python 3.10 or later and sympy. `pip install "granada[notebook]"` adds
IPython, for `render()` to show its page inline in a notebook.

To work on granada itself, install it from a clone, with the test
dependencies, and run the tests:

```bash
pip install -e ".[test]"
```

```bash
python -m pytest
```

`python -m pytest tests/feynman` (or `tests/schwinger`, `tests/core`) runs one
suite. See [Tests](#tests).

### Sixty seconds

The core alone, from an integrand to a Mathematica file:

```python
from granada import Vector, SP, mag, G2, PL, jprime, reduce, fold, render, getTower

k, p = Vector("k"), Vector("p")
family = [k, p, k + p]          # D_1, D_2, D_3 — the Bessel rides on D_1

Q = (SP(k, p) / SP(k+p, k+p)**2 * G2(k, p)
     * (-2*jprime(k)*SP(k, p)/mag(k) - 2*jprime(k)*mag(k)
        + jprime(k+p)*mag(k+p))
     * PL(k)/SP(k, k) * PL(p)/SP(p, p))

t = fold(reduce(Q), k, family)
render(t, by_exponents=True, legend=True)
getTower(t, "run1.m", basis=family)
```

Write the integrand as it stands — no `.expand()` anywhere.

#### Both pipelines in one script

```python
from granada import Vector, External, SP, G2, PL, g, sin, cexp, render, juxtapose
from granada import feynman, schwinger

k1, k2 = Vector("k1"), Vector("k2")
x, y = External("x"), External("y")

L = feynman.feynmanReduce(G2(k1, k2) * PL(k1) * PL(k2) * g(k1) * g(k2) * g(k1 + k2))
R = schwinger.schwingerReduce(G2(k1, k2) * PL(k1) * PL(k2) / SP(k1 + k2, k1 + k2)
                              * sin(SP(k1, x - y) / 2) * cexp(SP(k1, x) + SP(k2, y)),
                              evaluateDescendants=True)
render([L, R.final], path="both.html")      # one page, each item under its name
juxtapose(L, R.final, path="side.html")     # the same two, side by side
```

Each call writes its own page as well. `examples/both_pipelines.py` does the
same with each pipeline's dressed kernels, `denominators` and `evalTower`.

### Part I — the shared core

Everything here is imported from `granada` itself, and is the same object
whichever pipeline uses it.

#### Building expressions

| you want | you write |
|---|---|
| a vector | `k = Vector("k")` |
| a combination | `k + p`, `2*k - p` (kept unexpanded) |
| a scalar product | `SP(k, p)` |
| a square | `SP(k, k)` |
| a magnitude | `mag(k)`, `mag(k+p)` |
| a power | `SP(k, k)**Fraction(3, 2)`, `mag(k)**3`, `mag(k)**N` |
| the linear power spectrum | `PL(k)` — the same as `mag(k)**N` |
| one with an index of its own | `PL(k1, "n1")` — $k_1^{n_1}$; see [Several spectral indices](#several-spectral-indices) |
| the second-order kernels | `F2(k, p)` (density), `G2(k, p)` (velocity divergence) |
| the third-order kernels | `F3(k, p, q)`, `G3(k, p, q)` — symmetrised |
| the fourth-order kernels | `F4(k, p, q, s)`, `G4(k, p, q, s)` — symmetrised |
| the kernels of any order | `FKernel(k1, ..., kn)`, `GKernel(k1, ..., kn)` — $n$ the number of momenta |
| the dressed kernels | `feynman.Fx(...)`, `schwinger.Fx(...)`, `Fy`, `G`, any order likewise — see [Feynman](#dressed-kernels-phases-in-r), [Schwinger](#dressed-kernels-phases-in-x-and-y) |
| an external position (Schwinger) | `x, y = External("x"), External("y")` |
| the Bessel factor | `jprime(k)` — this is `j_0'(|k| r)` |
| a scaled Bessel | `j(k, 1, Fraction(1, 2))` — this is `j_1(|k| r / 2)` |

Exponents must be `int`, `Fraction`, or `Lin`. Floats are refused on purpose:
write `Fraction(1, 2)`, not `0.5`.

A coefficient may be typed as a fraction, `1/2 * F2(k, p)`. Python turns `1/2`
into the float `0.5` before granada sees it, and it is read back as the exact
fraction it was typed as: the $p/q$ with $q\le10^6$ that gives exactly that
float again, so `1/2` is $\tfrac12$, `2/3` is $\tfrac23$ and `0.1` is $\tfrac1{10}$. A float
that is no such fraction (`math.pi`) is refused. `Fraction(1, 2) * ...` and
`... / 2` work as before.

**Vectors and magnitudes are different objects.** Anything with a direction
takes the `Vector` — `SP(k, p)`, `jprime(k)`, `k + p`. Anything scalar takes
the magnitude — `mag(k)**N`, `1/mag(k)**2`. To keep the paper's notation,
bind the vector to one name and the scalar to another:

```python
kv, pv = Vector("k"), Vector("p")
k, p, kp = mag(kv), mag(pv), mag(kv + pv)
Q = 1/k**2 * 1/p**2 * 1/kp**2 * SP(kv, pv) * G2(kv, pv) * k**N * p**N
```

##### The kernels

`F2` and `G2` are the closed forms. `F3`, `G3`, `F4` and `G4` come from the
standard SPT recursion (Goroff et al. 1986), with $F_1=G_1=1$,

$$F_n=\sum_{m=1}^{n-1}\frac{G_m(\boldsymbol q_1,\dots,\boldsymbol q_m)}{(2n+3)(n-1)}\Big[(2n+1)\,\alpha(\boldsymbol k_1,\boldsymbol k_2)\,F_{n-m}(\boldsymbol q_{m+1},\dots,\boldsymbol q_n)+2\,\beta(\boldsymbol k_1,\boldsymbol k_2)\,G_{n-m}(\boldsymbol q_{m+1},\dots,\boldsymbol q_n)\Big],$$

$G_n$ the same with $3\,\alpha\,F_{n-m}+2n\,\beta\,G_{n-m}$, where
$\boldsymbol k_1=\boldsymbol q_1+\dots+\boldsymbol q_m$,
$\boldsymbol k_2=\boldsymbol q_{m+1}+\dots+\boldsymbol q_n$ and

$$\alpha(\boldsymbol k_1,\boldsymbol k_2)=\frac{(\boldsymbol k_1+\boldsymbol k_2)\cdot\boldsymbol k_1}{k_1^2},\qquad
\beta(\boldsymbol k_1,\boldsymbol k_2)=\frac{|\boldsymbol k_1+\boldsymbol k_2|^2\,(\boldsymbol k_1\cdot\boldsymbol k_2)}{2k_1^2k_2^2}.$$

Each is averaged over the orderings of its arguments, so every kernel is
symmetric. The lower orders on the right are already symmetric, so the
average is a sum over which arguments go left, $1/\binom nm$ each. Nothing
is expanded: the squares of every pair and triple of arguments,
$(\boldsymbol k_1+\boldsymbol k_2)^2$ and so on, stay as they are. `F3` and
`G3` reproduce the $P_{13}$ kernels of the density and the velocity
divergence (`tests/core/test_kernels.py`).

`FKernel(k1, ..., kn)` and `GKernel(k1, ..., kn)` are $F_n$ and $G_n$ at any
order, the order being the number of momenta: `FKernel(k)` is $F_1=1$,
`FKernel(k1, k2)` is `F2`, `GKernel(k1, k2, k3)` is `G3`, and on, by the
same recursion. The tests check them against an independent numerical
recursion and against the collinear limit $F_n=G_n=k^n/(n!\,q_1\cdots q_n)$
(`tests/core/test_kernels.py`, and in each pipeline's suite).

**Partial sums that vanish.** In `F3(k, q, -q)` the recursion meets
$\boldsymbol k_1=\boldsymbol q-\boldsymbol q=0$ and a factor $1/k_1^2$.
Its $G_m$ vanishes like $k_1^2$, so the term goes to zero, and it is left
out. The same holds for $\boldsymbol k_2=0$. The kernel is then its limit,
finite and free of any zero vector, as $P_{13}$ and $P_{24}$ need. A
kernel whose arguments add up to zero is $0$. Both pipelines use these
kernels, so an input written with them is the same expression in each.

#### Several spectral indices

`PL(k)` is $k^n$, with one spectral index $n$ for every power spectrum. Each
may have its own instead:

```python
PL(k1, "n1") * PL(k2, "n2")      # k1^(n1) k2^(n2): n1 and n2 independent
PL(k, "n_s")                     # k^(n_s)
PL(k, N - 1), PL(k, -2)          # any exponent linear in indices, or a number
spectralIndex("n1")              # the index n1 as an exponent: mag(k)**spectralIndex("n1")
```

An index is named `n` or `m`, or either with a subscript, digits (`n1`, `m2`) or
after an underscore (`n_s`, `n_eff`); `PL(k, "n")` is `PL(k)`. Indices of
different names are independent, and an exponent is linear in all of them
together: `Lin` is $a+\sum_i b_i n_i$ (`.parts`, `.coeff("n1")`; `.b`, the
coefficient of $n$, for a form in $n$ alone). The amplitude $A$ of
$P_L=Ak^n$ is a constant and comes out of every integral as it is.

Both pipelines carry the indices through unchanged: an exponent that depends
on any index is treated as one in $n$ always was. The results are in the
sympy symbols of the same names, `n1`, `n_s` (real in `evalTower`,
`evaltower.index("n1")`), and LaTeX shows them as $n_{1}$, $n_{s}$;
`PL(k, "n1")` is written back as $P_L(k, n_1)$. In a Mathematica file
`n1` stays `n1` and `n_s` is `Subscript[n, s]`.

Two things to know:

* **`fullSimplify` works in every index at once**, with a $\Gamma$ of
  $\alpha\cdot\boldsymbol n+\beta$ in place of one of $\alpha n+\beta$ (see
  [fullSimplify](#fullsimplify-a-sum-of-gamma-functions-simplified)). The
  README tower with $P_L(k,n_1)\,P_L(p,n_2)$ comes out as two terms in nine
  $\Gamma$'s, where $n$ alone has two terms in four: what is one $\Gamma$ of
  $n$ is often two, one of $n_1$ and one of $n_2$, that no identity joins.
* **Symmetric terms are no longer symmetric.** $k_1\leftrightarrow k_2$ is a
  symmetry of $P_L(k_1)P_L(k_2)$ but not of $P_L(k_1,n_1)P_L(k_2,n_2)$, unless
  $n_1\leftrightarrow n_2$ too. A sum written symmetric by hand, such as
  `1/2 * (sigma_1 + sigma_2)`, needs its indices exchanged with its momenta.
  The library itself only relabels integration variables, which is always
  allowed, so terms that are equal only for $n_1=n_2$ are kept apart.

#### Reduction: reduce, align, fold

```
reduce  ->  align  ->  fold  ->  getTower      (the tower, for Mathematica)
                             ->  evalTower     (the tower at your master, simplified: Feynman)
```

`reduce()` is algebra and is always needed. `align` and `fold` are facts
about the *integral* rather than the algebra, so they are separate calls you
make on purpose.

##### reduce()

```python
reduce(obj, frozen=(), prefer=None, check=True)
```

Expands, shifts if a Bessel demands it, and expands again — in that order,
which matters: expanding first lets the shift collapse a square that would
otherwise survive as an independent one. Accepts anything the algebra can
build, including a `list`, whose `(label, object)` pairs keep their labels.

`prefer` names the variable to eliminate in the shift; otherwise it is chosen
alphabetically. `frozen` bars vectors from being shifted — of no use here,
since nothing is external. `check=False` skips the diagnosis of factors that
cannot reach D-form.

##### align() and fold()

Both live in `symmetry.py` and both rest on the variables being dummy.

```python
align(obj, target)          # put every piece's Bessel on the same vector
fold(obj, flip, basis)      # reflect monomials into the target family
relabel(obj, mapping)       # permute names by hand
```

`align` transposes names so that pieces of a `TermSum` differing only in
which dummy carries the Bessel become one `Term` — one coefficient list
instead of several blocks.

`fold` uses `k -> -k`, under which `D_{k-p}` and `D_{k+p}` exchange while
`D_k` and `D_p` are fixed. It rewrites a monomial only when that strictly
reduces the number of factors outside `basis`, so it is idempotent. Call it
*after* the final expansion; anything expanded afterwards re-manufactures the
wrong half of the pair.

Both require the Bessel to be atomic, since `j_0'(|k|r)` is invariant but
`j_0'(|k+p|r)` is not. `reduce()` has already arranged that.

##### When a term will not land on three propagators

```python
diagnose(t, k, family)      # prints a per-piece report
stranded(t, k, family)      # the monomials no reflection can move
```

A monomial carrying **both** `(k+p)^2` and `(k-p)^2` is fixed by neither
orientation: reflection swaps them. Those are genuine four-propagator
integrals and `fold` leaves them alone. If they arose because `expand()`
manufactured the wrong half inside otherwise-fine monomials, aim the
expansion instead:

```python
e.expand(basis=[k, p, k-p])
```

`Expr.expand(basis=...)` chooses between `a.b = ((a+b)^2 - a^2 - b^2)/2` and
`a.b = (a^2 + b^2 - (a-b)^2)/2` per dot product, picking whichever lands
inside the family. With no basis it uses the sum, as it always did.

#### Mathematica output

```python
getTower(obj, path="masters.m", basis=None, name="granada", head="M",
         r="r", n="n", denominator=True, propagators=3)
wl(obj, ...)                # the same, as a string
labels(obj, ...)            # the data: basis, Bessel, (coefficient, label) pairs
```

Emits a flat list of `{coefficient, {exponents}}` — data, not code — plus one
line assembling it under `head`:

```mathematica
(* D1 := k^2 *)
granadaCoefficients = {{15/28, {-1/2*n - 1, 0, 1}}, ...};
granada = Total[First[#] (M @@ Append[Last[#], r]) & /@ granadaCoefficients];
```

Read it with `Get["run1.m"]` once `M` is defined.

* **`denominator=True`** negates the exponents, because `M` is defined with
  its propagators downstairs: `M(a,b,c;r) = int j_0'(k_1 r) / (D_1^a D_2^b D_3^c)`.
* **`propagators=3`** refuses a basis of any other size. A wrong-arity `M` is
  legal Wolfram input that matches no definition and silently never
  evaluates, so the check belongs on the Python side.
* **`basis=`** fixes which vector is `D_1`. Pass the same list you passed to
  `fold`; this is the one joint where the two halves can disagree unnoticed.

A `TermSum` becomes one numbered block per Bessel structure, each with its
own legend, plus a line summing them. `align` first if you would rather have
one.

##### Several expressions in one file

```python
getTower([A1tower, A2tower], "towers.m", basis=family, dropScaleless=True)
```

A list writes one file in which each expression is defined on its own, under
the name of the variable that holds it, with nothing summed across them:

```mathematica
(* ===== A1tower ===== *)
A1towerCoefficients = {...};
A1tower = Total[...];

(* ===== A2tower ===== *)
...
```

An expression with several blocks gets `A2towerPart1`, `A2towerPart2`, ... and
`A2tower` as their sum. Names are looked up where `getTower` (or `wl`) is
called. A name that cannot be told is refused, not guessed: an expression
written inline in the list, one held by two variables, or one that would
clash. Pass `("name", expr)` for any entry, or a dict `{"name": expr}`,
to choose names yourself. Names become Mathematica symbols (`A1_tower ->
A1Tower`). Protected one-letter symbols (`C`, `D`, `E`, `I`, `K`, `N`, `O`) and
the master's own `M`, `r`, `n` are refused.

#### The reference vector and refAverage

```python
from granada import Vector, SP, ref, cexp, sin, cos, I, refAverage

k = Vector("k")
a = refAverage(SP(k, ref) * cexp(SP(k, ref)))   # I * |k| r j_1(|k| r)
a.im                                            # the TermSum |k| r j_1(|k| r)
```

`ref` is the one reference vector, rendered as bold `r`. Its magnitude is
the `r` that every Bessel carries, so `mag(ref)` is `r` and `SP(ref, ref)` is
`r^2`. It is not an integration variable, and the shift in `reduce()` never
moves it. The name `"r"` is reserved, so `Vector("r")` raises.

`sin(x)`, `cos(x)` and `cexp(x) = exp(i x)` take a scalar expression and are
opaque: no vector algebra reaches inside them. `I` is the imaginary unit.
Anything containing them is an `FSum`. Once no function factors are left,
`.re` and `.im` give plain `TermSum`s for `reduce()`.

`render()` and `latex()` take an `FSum` directly, so a `refAverage` result
can be typeset as it comes, e.g. `render(a, path="ref.html")`. Function
arguments are always shown in vector notation; `cexp(x)` prints as `e^{i x}`,
and `cexp(-x)` as `e^{-i x}`.

A coefficient in the exponent, as in `cexp(Fraction(1, 2) * SP(k, ref))`, is
the value its `lambda` takes at the end, since the identity holds for any
`lambda`. The end point `K = sum_j c_j q_j` is written `s V`, with `V` a vector
with coprime integer coefficients and `s` rational, so the result carries
`j_m(s |V| r)`. A Bessel accepts that scale directly as `j(k, ell, scale)`.
LaTeX prints it as `j_1(1/2 k r)`, and the Mathematica export passes
`(1/2) r` as the last argument of `M`. That is the same master evaluated at
`r/2`.

The coefficients `refAverage` generates are expanded bilinearly over the
atoms (`k1.k2`, `k1^2`, ...). It is the only form in which equal pieces collect
and vanishing ones cancel: after Euler, the same atoms reach the derivatives
through several different vectors, and `(k1+k2).k2 - k1.k2 - k2^2` would
otherwise survive as three symbols. Factors you wrote yourself that do not
depend on `ref` are kept as written.

`refAverage` averages over the direction of `ref` using

    int dOmega/(4pi) [prod_i (k_i.r)^(n_i)] e^{i sum_i lambda_i k_i.r}
        = (1/i)^(sum n_i) [prod_i (d/dlambda_i)^(n_i)] j_0(|sum_i lambda_i k_i| r)

at `lambda_i = 1` for the vectors in the exponential and `lambda_i = 0` for
vectors that appear only in the prefactor (a prefactor vector that is not in
the exponential is the same as one that is, with `lambda_i = 0`). The derivatives are written in the `j_ell` basis with
Rayleigh's formula, `d^m/du^m j_0(r sqrt(u)) = (-1)^m r^m j_m(|K| r) / (2^m |K|^m)`
with `u = K^2`. So far it reads `cexp` arguments of the form
`sum_j c_j (q_j.ref)` with rational `c_j`, together with prefactors `(q.ref)^n`
for any `q` free of `ref`. In both, `ref` may stand in either slot and be
negated or scaled by an integer: `SP(-ref, q)` is read as `((-q).ref)`.
With no exponential at all, `K = 0` and the
derivatives are taken at `u = 0`, where `d^m/du^m j_0 = (-1)^m m! r^(2m) / (2m+1)!`,
so for example `refAverage(SP(k, ref)**2)` is `k^2 r^2 / 3`. Any part of a `cexp` argument that does not
depend on the direction of `ref` (for example `SP(k, p)` or `SP(ref, ref)`)
is split off as its own factor, `e^{i(a+b)} = e^{ia} e^{ib}`, and passes
through; so do functions that depend on `ref` only through `r`. A `sin` or
`cos` that depends on the direction of `ref` is first rewritten by Euler's
formula, `sin x = (e^{ix} - e^{-ix})/(2i)`, `cos x = (e^{ix} + e^{-ix})/2`, so
for example `refAverage(cos(SP(k, ref)))` is `j_0(|k| r)`. Anything else
that depends on the direction of `ref` is refused by name.

##### refAverage, reduce, align and fold in one call: refReduce()

```python
T = refReduce(B, family=[k1, k2, k1 + k2], flip=k1, dropScaleless=True)
getTower(T, "run.m", basis=[k1, k2, k1 + k2], dropScaleless=True)
```

`refReduce(expr, family, flip)` runs `refAverage -> reduce -> align -> fold`
and renders every stage: the input, the result of each step in vector
notation, then the final result in D-notation against `family`, numbered and
with a legend. It returns the final expression.

* `family` and `flip` are required. They are facts about the integral, the
  same ones `fold(obj, flip, family)` and `getTower(..., basis=family)` take.
  The `align` target is not asked for: it is `family[0]`, because the
  exporter puts the Bessel on `D_1`.
* `frozen=` and `prefer=` are passed to `reduce()`; `path=` and
  `open_browser=` work as in `render()`. `dropScaleless=True` leaves the
  pieces without a `j_l` out of the page *and* out of the returned result, so
  what comes back is what the page shows and `getTower()` takes it as it is.
  What it left out of the result is shown last, under *result: left out by
  dropScaleless*, in the same D-notation, or *no scaleless terms*.
* `cleanInput=True` shows the input line exactly as you typed it. Kernels
  appear as calls, `F_2(k1, k2)`, `G_2`, `P_L(k1)`, `j_0'(|k| r)`, and sums,
  products, quotients and powers keep the grouping you gave them. The default,
  `False`, shows the evaluated, expanded form. The arithmetic you type records
  how it was written (`written.py`); arithmetic inside the library does not,
  so this is display only and costs nothing in a reduction.
* If a step fails, the error names it: `refReduce, step 'reduce': ...`.
* An integrand without `ref` goes through too: `refAverage` leaves it as it is.

##### Reducing an averaged expression

The output of `refAverage` goes through the same pipeline as anything else:

```python
a = refAverage(SP(k, ref) * cexp(SP(k + p, ref)) * G2(k, p) / SP(k, k) / SP(p, p))
t = fold(reduce(a), k, family)
render(t, by_exponents=True, legend=True)
getTower(t, "run2.m", basis=family)
```

* **sin, cos and cexp are refused** by `reduce`, `is_reduced`, `masters`,
  `align`, `fold`, `relabel`, `stranded`, `diagnose`, `labels`, `wl` and
  `getTower`, with a message to call `refAverage()` first. So is a scalar
  product `(q.ref)` that still depends on the direction of `ref`. One that
  survives `refAverage` depends on `ref` only through `r`, or not at all, and
  has no D label either.
* **r is a prefactor, never a propagator.** It is not integrated over, so
  powers of `r` (from `SP(ref, ref)` and `mag(ref)`) ride along with each master:
  `render(by_exponents=True)` writes them as `r^2` beside the D labels, and the
  exporter emits one block per power, prefixed in its sum line, as in
  `granada1 = I*r*Total[...]`. `labels()` returns one block, so it refuses an
  expression with several powers of `r` and points to `wl()`.
  `masters()`/`by_exponents()` give `r^2` a slot only if you put `ref` in the
  basis.
* **i is carried by an `FSum`.** Without a factor of `i`, an averaged
  expression is just a `TermSum`, and every call returns one. With one, the
  real and imaginary parts are reduced, folded, aligned and relabelled
  separately and recombined. The exporter marks the imaginary blocks with
  `I*`. `masters()`, `stranded()` and `diagnose()` work on `.re` and `.im`
  one at a time.
* **ref is never moved:** the shift never picks it, and `fold`, `relabel`
  and `align` refuse it.
* **A piece without a Bessel**, such as `refAverage(SP(k, ref)*SP(p, ref))`
  `= (k.p) r^2/3`, reduces like any other, but it is not an `M` integral, so the
  exporter refuses it, as it always has. Pass `dropScaleless=True` to
  `render`, `latex`, `wl` or `getTower` to leave such pieces out: every piece
  without a `j_l` (and without a `sin`, `cos` or `cexp` still to be averaged) is
  omitted, and the exported file says how many were.
* **What is left out is shown, not lost.** Every page made with
  `dropScaleless=True` shows the pieces it left out: `render()` right after
  each item (*T: left out by dropScaleless*, with the number of terms),
  `juxtapose()` under each side, `refReduce()` after the result, `evalTower()`
  after the result and its check (`V.left` holds them). They are in the
  item's own notation, or in vector notation when they leave its basis, as a
  piece without a Bessel may. What is kept and what is shown add up to what
  was given. When nothing was left out, the same place says so: *no
  scaleless terms*. So does the Mathematica file, which otherwise counts the
  pieces it left out. An object `dropScaleless` does not look inside (a
  string, a sympy value, a stage object) gets neither; `latex()` returns
  only the kept pieces.

#### fullSimplify: a sum of Gamma functions, simplified

```python
fullSimplify(expr)          # in every spectral index of expr: n, n1, n_s, m, ...
fullSimplify(expr, n)       # n first, then every other index of expr
fullSimplify(expr, [n1])    # in exactly these: a Gamma of any other is opaque
```

A tower evaluates to a sum of products of $\Gamma(\alpha n+\beta)$, with
$\alpha$ and $\beta$ rational, times powers of 2, $\pi$ and $r$ and rational
functions of $n$ — or, with [several indices](#several-spectral-indices), of
$\Gamma(\alpha\cdot\boldsymbol n+\beta)$, $\alpha$ a rational vector with one
entry per index and $\boldsymbol n=(n_1,n_2,\dots)$. sympy's own `simplify()` turns such a sum into reflection
formulas ($\sin$, $\cos$, $\pi^{35}$). `fullSimplify` takes four steps
instead, each an identity:

1. **shift**: arguments that differ by an integer are one class, and every
   $\Gamma$ of a class is written as the one of smallest argument times a
   rational function, $\Gamma(z+k)=(z)_k\,\Gamma(z)$;
2. **collect**: terms with the same $\Gamma$'s and the same powers of 2,
   $\pi$, $r$ (up to integer exponents) are one term, their rational
   functions added over one denominator and factored;
3. **merge**: terms whose $\Gamma$'s differ by Gauss's multiplication
   formula, $\Gamma(mz)=(2\pi)^{(1-m)/2}m^{mz-1/2}\prod_k\Gamma(z+k/m)$, are
   merged the same way, written with the fewest $\Gamma$'s among the terms' own
   forms and the one with partners $\Gamma(z)\Gamma(z+\tfrac12)$ paired into
   $\Gamma(2z)$. The formula relates arguments whose $\alpha$'s are parallel
   only, so it is applied along each direction of $\alpha$ on its own:
   $\Gamma(2n_1+2n_2)$ joins $\Gamma(n_1+n_2)\Gamma(n_1+n_2+\tfrac12)$, never a
   $\Gamma$ of $n_1-n_2$;
4. **absorb**: a linear factor next to a $\Gamma$ of the matching argument is
   taken into it, $z\,\Gamma(z)=\Gamma(z+1)$, $\Gamma(z)/(z-1)=\Gamma(z-1)$,
   the factor any rational multiple of $z$ or $z-1$:
   $(2n_1+2n_2)\,\Gamma(n_1+n_2)=2\,\Gamma(n_1+n_2+1)$.

What the terms share (powers, $\Gamma$'s, a number) is then pulled out in
front. The reflection formula is never used, so no $\sin$ or $\cos$ appears
that was not there. A factor of $i$ keeps real and imaginary parts apart.
Anything else, such as a hypergeometric function or a $\sin$ of your own,
passes through as an opaque factor and is matched exactly. The tests check
it on random sums of $\Gamma$'s for the value at 40 digits, and that the
result never has more $\Gamma$ factors than the input.

`evalTower` (Feynman) and `getFinalExpression` (Schwinger) both simplify with it.

#### The axis and its tensor algebra: g, peel, project

`tensor.py` handles integrands that carry a preferred direction, the axis
$\hat{\boldsymbol z}$, through factors

$$g(\boldsymbol v)=\frac{2v_z}{v^2}\sin\frac{\boldsymbol v\cdot\boldsymbol r}{2}.$$

It is the part of the work both pipelines share. The Feynman pipeline runs
its two stages, **peel → project**, and then averages
([stage 3](#stage-3-average)). The Schwinger pipeline runs the same two
stages on an input with $g$'s, at the midpoint, and parametrizes the probes
they leave ([Dressed kernels: phases in x and y](#dressed-kernels-phases-in-x-and-y)).

The stages work on a single term

$$\mathcal I=\Phi(\{k\})\prod_{a=1}^{n}g(\boldsymbol v_a).$$

A sum of such terms with different $g$'s, as the diagrams of one observable,
is an `AxialSum`; each pipeline takes its terms one by one.

$\Phi$ is built from kernels (`FKernel`, `GKernel`, `F2`, `G2`, ...), $P_L$
and scalar products of integration momenta. It may also carry one of two
kinds of phase, never both:

* phases in $\boldsymbol r$ and factors of $i$, for the Feynman pipeline: a
  `cexp`, `sin` or `cos` of $\sum_jc_j\,(\boldsymbol q_j\cdot\boldsymbol r)$ with
  rational $c_j$, typed or from `feynman.Fx`, `feynman.Fy` (see
  [Phases](#phases));
* the phases $e^{i\boldsymbol k\cdot\boldsymbol x}$, $e^{i\boldsymbol k\cdot\boldsymbol y}$
  of `schwinger.Fx`, `schwinger.Fy`, for the Schwinger pipeline at the
  midpoint. `peel()` refuses them: the Feynman pipeline cannot average them.

It has no Bessel and no `ref` outside a phase. $n$ is the *axial rank*.

**Stage 1, peel.** $v_z=\hat z_i v_i$, so

$$\mathcal I=\hat z_{i_1}\cdots\hat z_{i_n}\,T_{i_1\dots i_n},\qquad
T=E\,v_{1i_1}\cdots v_{ni_n},\qquad
E=\Phi\prod_a\frac{2\sin(\boldsymbol v_a\cdot\boldsymbol r/2)}{v_a^2}.$$

$E$ is the *envelope* and the $\boldsymbol v_a$ are the *legs*.

**Stage 2, project.** By the isotropy lemma (below),

$$\int T=\sum_S c_S\,S,\qquad c_S=\sum_{S'}W_{SS'}\int(S'\cdot T),$$

where the *brackets* $S$ are the $\delta$/$\hat r$ structures of
`granada.decompose` (formerly
[tensor-algebra](https://github.com/habrahamyan/tensor-algebra)) and $W=G^{-1}$ are the
*Weingarten weights*, with $d=3$ fixed and the pseudo-inverse used from rank 6
on. The *probe*

$$S'\cdot T=E\prod_{\text{pairs}}\boldsymbol v_a\cdot\boldsymbol v_b
\prod_{\text{singles}}\frac{\boldsymbol v_a\cdot\boldsymbol r}{r}$$

is a scalar integrand, written with `SP(v, ref)` and `mag(ref)`. Contracting
the $\hat z$'s back gives $\hat z\cdots\hat z\cdot S=\nu^{s(S)}$, where $s(S)$
is the number of $\hat r$ slots of $S$. So

$$\int\mathcal I=\sum_{s\equiv n\,(2)}\nu^s A_s,\qquad
A_s=\sum_{S:\,s(S)=s}\;\sum_{S'}W_{SS'}\int S'\cdot T.$$

The result is grouped by the power of $\nu$, not by bracket. The $A_s$ are
unique even where the brackets are linearly dependent (rank 6 and up in
$d=3$), and the individual $c_S$ are not.

**Isotropy lemma.** Stage 2 is not an identity point by point in the
integrand. It holds after integration, because every vector is integrated
over, the measure is isotropic, and $\Phi$ carries no $\hat{\boldsymbol z}$ (a
phase depends on $\boldsymbol r$, or on $\boldsymbol x$ and $\boldsymbol y$,
never on $\hat{\boldsymbol z}$). (Pointwise in the momenta, the bracket sum is
the projection of $T$ onto what survives rotations about $\hat{\boldsymbol r}$.)

| Object | Type | Produced by |
|---|---|---|
| product of g's | `GString` | `g(v)`, `*`, `**` |
| $\Phi$ · GString | `AxialIntegrand` (`envelopeScalar`, `gstring`, `rank`) | `Phi * g(k) * g(p)` |
| a sum of terms with different g's | `AxialSum` (`terms`) | `I1 + I2` |
| $\hat z\cdots\hat z\,T$ | `AxialTensor` (`legs`, `envelope`, `rank`, `indices`) | `peel(AxialIntegrand)` |
| $\delta$/$\hat r$ structure | `Bracket` (`structure`, `nuPower`) | part of a `Projection` |
| $(C, Q)$ | `Channel` (`weight`, `probe`) | part of a `Projection` |
| stage-2 result | `Projection` (`tensor`, `brackets`, `gram`, `weights`, `channels`) | `project(AxialTensor)` |

Each stage takes exactly one type and returns exactly one type; anything
else raises a `TypeError` that names the stage the object belongs to. The
lower layers (`refAverage`, `reduce`, `align`, `fold`, `wl`, `getTower`,
`labels`) refuse every stage object, of the tensor algebra or of either
pipeline, and say where it belongs. `render` and `latex` take them all.

#### Rendering

```python
render(items, by_exponents=False, basis=None, symbol="D", numbered=False,
       legend=False, path=None, open_browser=False)
```

`by_exponents=False` gives vector notation — `k^2`, `(k+p)^2`, `|k+p|`.
`by_exponents=True` gives D-notation — `D_{k}`, `D_{k+p}^{n/2-1}`. Pass a
list of `(label, object)` pairs to stack several lines against one shared
basis, `legend=True` to print the definitions, `numbered=True` for `D_1`,
`D_2`. `latex(obj, ...)` returns the string instead of displaying it, and
`set_tex("kp", r"\boldsymbol{k}'", "k'")` overrides the LaTeX for one atom.

In a notebook `render` typesets; outside one it writes `out.html`.

##### Render anything, labelled as you typed it

`render` takes everything: the algebra's types, every stage object of both
pipelines and every field inside one, `Labels`, sympy numbers and matrices,
and plain numbers. A string is taken as LaTeX. Pass one object or a list of
them. Each item is shown under what you typed for it in the call, and then
its LaTeX:

```python
from granada.feynman import average                    # stage 3 is the Feynman pipeline's

I = G2(k, p) * PL(k) * g(k) * g(p)
T = peel(I); P = project(T); L = average(P)

render([I, T, P, L])                                  # input, every step, output
render([T.envelope, P.channels[1][0].probe, refAverage(P.channels[1][0].probe)])
render(L.entries[1][0].integrand)
steps = [I, T]; render(steps)                         # labelled I and T
T.render(path="t.html")                               # labelled T
```

The labels above read `I`, `T`, `P`, `L`, `T.envelope`,
`P.channels[1][0].probe`, `refAverage(P.channels[1][0].probe)`, and so on.
For a list held in a variable, each item gets the name of the variable that
holds it. A `("label", obj)` pair keeps its own label. Where the source
cannot be read (a plain `python` prompt), the label is the name of the
variable holding the item, and an item written inline gets no label.
`latex(obj)` returns the LaTeX alone, for any of the same objects.

The stage objects are always shown in their own notation, so
`by_exponents` and `basis` apply to the algebra's types in the list only.

##### Two results side by side: juxtapose

```python
juxtapose(A, B)                                   # A on the left, B on the right
juxtapose(V, S.final, path="both.html")           # one result of each pipeline
juxtapose(("Feynman", V), ("Schwinger", S.final)) # labels of your own
```

`juxtapose` takes exactly two results, positionally, and shows them side by
side where `render` would show them one after the other. Each side is shown
as `render` shows one item: anything `render` takes, labelled with what you
typed for it (or the name of its variable), or a `("label", obj)` pair, whose
label is kept whole. A list on one side is refused; `render([A, B, C])` puts
several in sequence.

The keywords are `render`'s (`by_exponents`, `basis`, `symbol`, `numbered`,
`legend`, `dropScaleless`, `path`, `open_browser`). A shared basis is derived
from both results, and `legend=True` puts its definitions above them. On a
page the two are two cards in two columns, each with its own arrow, and one
above the other again on a screen narrower than 860 px. In a notebook they
are the two columns of one display, unless they are too large to typeset
inline, in which case the page is written instead and its path returned, as
for `render`.

##### The page

Every block is a card with an arrow that shows and hides it. A row of links
at the top jumps to each section (the first 40), and "expand all" /
"collapse all" open or close every section and card. Formulas are typeset as
they come into view; anything behind a closed arrow waits until it is opened.

* **Sections.** A label written `"group › title — note"` puts its card under
  the heading *group*, which has its own arrow. Cards of one group are gathered
  where the group first appears, and the note is shown small beside the title.
  With more than 8 sections, only the first two start open. The Schwinger page
  has a section per term; the Feynman page one per stage (Input, Peel,
  Project, Average, Result), or one per term of a sum and per name of a dict.
* **Closed on request.** A block can ask to start closed whatever its size:
  `evalTower` does so for its towers and masters, so that its page opens on
  the result.
* **Long sums** (`page.Terms`): up to 24 terms are one formula, one to three a
  row by how wide they are. A longer sum is split into groups of 20 terms, each
  behind an arrow ("terms 21–40 of 86"), the first open.
* **Lists of terms** (`page.Items`): one row per term, its head always in view
  and its detail behind its own arrow. Up to 4 rows start open, more start
  closed, with "expand all" / "collapse all" for the card.

Both are strs holding the same LaTeX as one formula, so `latex()` and a
notebook show them as before. Exponentials and coefficients are written
$e^{-\frac i2\boldsymbol k\cdot\boldsymbol r}$ and $\frac i2$, not
$e^{i\,(-\frac12\boldsymbol k\cdot\boldsymbol r)}$ and $i\,\frac12$, and a
linear form in $n$ as $1-\frac n2$.

##### Large results

A page stays light however large the result is. That matters: the rank-4
example of the Feynman pipeline gives about 13,500 entries, and a browser asked to typeset all
of them at once runs out of memory.

* Every long formula is split into displays of 25 rows. An expression without
  rows is broken at its top-level `+` and `-` first. The rows are those of
  `latex()`, in the same order.
* A display is typeset only when it scrolls into view, and released again
  once it is far off screen, keeping its height. Memory follows what is on
  screen, about 50 MB for the rank-4 example, not everything ever looked at.
* A card of more than 300 rows starts closed, with its size beside its title.
  `evalTower` starts its towers and masters closed whatever their size, so
  its page opens on the result.
* MathJax's right-click menu and accessibility extras are off on these pages.
  Each kept its formula's whole internal tree alive, about 100 MB per display.
  `.latex()` still gives the source.

In a notebook, a result of more than 200,000 characters of LaTeX is not
typeset inline, because the notebook would typeset it all at once and
freeze. `render(...)` writes the same page to `out.html` (or `path=`)
instead and returns its path. Displaying such an object as the last line
of a cell shows its short text form and a hint in the log.

Every object also renders itself: `e.latex()` (keywords as for `latex()`),
`e.render(path=...)` and, in a notebook, just `e`.

### Part II — the Feynman pipeline

```python
from granada.feynman import (Fx, Fy, G, feynmanReduce, peel, project, average,
                             evalTower, master, denominators, partialFraction,
                             shiftBessel, toI25)
```

`granada.feynman` turns one term $\Phi\prod_ag(\boldsymbol v_a)$, or a sum of
them, into a list of rational numbers times scalar integrands that `reduce()`
understands, sorted by powers of
$\nu=\hat{\boldsymbol z}\cdot\hat{\boldsymbol r}$. It runs three stages,
**peel → project → average**: the first two are the core's
[tensor algebra](#the-axis-and-its-tensor-algebra-g-peel-project), the third
its own. `feynmanReduce()` runs them and renders every stage. For a term of
two momenta, `evalTower()` takes the `Ledger` it returns and does the rest:
reduce, align, fold, and evaluate at your master (see
[Straight from feynmanReduce](#straight-from-feynmanreduce)). The other tools
take the `Ledger` too: `denominators`, `shiftBessel`, `toI25` and
`partialFraction`.

#### Stage 3, average

$$\int\mathcal I=\sum_{s\equiv n\,(2)}\nu^s A_s,\qquad
A_s=\sum_{S:\,s(S)=s}\;\sum_{S'}W_{SS'}\int S'\cdot T.$$

Each $\int(S'\cdot T)$ is a rotation-invariant scalar that depends only on
$r$. By the isotropy lemma it equals the integral of its average over the
direction of $\hat{\boldsymbol r}$, which is what `refAverage` computes. The
averaged probes are weighted, merged and collected into a `Ledger`,
$A_s=\sum C'\,Q'$, each $Q'$ an ordinary `Term`. Like stage 2, stage 3 holds
after integration, not point by point.

#### Sixty seconds

```python
from granada import Vector, G2, PL, g
from granada.feynman import feynmanReduce

k, p = Vector("k"), Vector("p")
L = feynmanReduce(G2(k, p) * PL(k) * PL(p) * g(k) * g(p) * g(k + p), path="feynman.html")

L.entries[1]          # [Entry, ...]: A_1 = sum of coefficient * integrand
e = L.entries[1][0]
e.coefficient         # a sympy rational (times i if need be)
e.integrand           # a Term: monomial * r^p * j_l(...), coefficient 1
```

The page has one block per stage, for checking against a calculation by
hand:

1. the input as typed ($G_2(\boldsymbol k,\boldsymbol p)\,P_L(k)\,P_L(p)\,g(\boldsymbol k)\cdots$), then with each $v_z$ written out;
2. the peel: $\hat z_i\hat z_j\hat z_l\,T_{ijl}$, and $T$ written out with its envelope;
3. the projection: the bracket Ansatz, the Gram matrix $G$ and the weights
   $W$ as tables (up to ten brackets), every $c_S$ as weights times
   contractions, then for each power of $\nu$, $A_s=\sum C\int Q$, with $Q$
   both as a contraction label ($T_{aa\hat r}$, $T_{\hat r\hat r\hat r}$, …)
   and evaluated;
4. the average: for each power of $\nu$, first every probe's own average
   $\langle Q\rangle_{\hat r}$ before weighting and merging, then
   $A_s=\sum C'\,Q'$;
5. the assembled result $\int\mathcal I=\sum_s\nu^sA_s$.

#### Phases

A field at $\boldsymbol x\pm\boldsymbol r/2$ brings a phase
$e^{\pm i\boldsymbol q\cdot\boldsymbol r/2}$, where $\boldsymbol q$ is its total momentum.
`F2`, `G2`, `G3` and `PL` carry no phase. The [dressed kernels](#dressed-kernels-phases-in-r)
`Fx` and `Fy` include it. Otherwise you write it next to its kernel with `cexp`.
A bar is a minus sign, $\bar{\boldsymbol k}=-\boldsymbol k$:

```python
from granada import Vector, SP, ref, cexp, F2, PL, g
from granada.feynman import feynmanReduce

k1, k2, k3 = Vector("k1"), Vector("k2"), Vector("k3")
I = (F2(-k1, k3) * cexp(SP(k3 - k1, ref) / 2)       # F_{k1bar k3} e^{ i (k3 - k1).r/2}
     * F2(-k3, k2) * cexp(-SP(k2 - k3, ref) / 2)    # F_{k3bar k2} e^{-i (k2 - k3).r/2}
     * g(-k2) * g(k1) * PL(k1) * PL(k2) * PL(k3))
L = feynmanReduce(I, path="feynman.html")
```

* A phase is a `cexp`, `sin` or `cos` of $\sum_j c_j\,(\boldsymbol q_j\cdot\boldsymbol r)$,
  with rational $c_j$ and $\boldsymbol q_j$ free of `ref`. That is exactly what
  `refAverage` reads. `SP(-ref, k3 - k1)` and `SP(k3 - k1, ref)` are both fine,
  since `ref` may sit in either slot, negated or scaled by an integer. Any other
  function is refused at the input, by name:
  `sin(SP(k, p))`, `cexp(SP(k, ref) + SP(k, p))` (its direction-free part would
  survive the average, and an `Entry` has no room for a function), or
  `cexp(SP(k, ref)**2)`.
* `ref` outside a phase is still refused, as in `SP(k, ref) * g(k)`.
* $\Phi$ may also carry $i$ (`I`). With a phase or $i$, `envelopeScalar` is an
  `FSum`. Without one, it is an `Expr`, as before.
* The average turns the phases, together with the sines of the $g$'s, into
  Bessels of $|\boldsymbol K|r$, where $\boldsymbol K$ sums the phase momenta
  and the half-legs. `denominators(L)` lists the combinations. For the example
  above there are six propagator structures: the genuine denominators
  $(\boldsymbol k_1-\boldsymbol k_3)^2$, $(\boldsymbol k_2-\boldsymbol k_3)^2$ and
  $(\boldsymbol k_1+\boldsymbol k_2-\boldsymbol k_3)^2$, and the $n$-dependent
  $k_1^2$, $k_2^2$, $k_3^2$.
* Under $\hat{\boldsymbol r}\to-\hat{\boldsymbol r}$ the sines and the
  contraction together are even, and each phase is conjugated. So flipping the
  sign of every phase at once leaves the result unchanged, and a real
  $\Phi$ times phases gives real $A_s$.

#### Dressed kernels: phases in r

Every $F$ comes with its phase and every $G$ with its $g$, so they are
written together. For momenta $\boldsymbol k_1,\dots,\boldsymbol k_n$ with total
$\boldsymbol k=\boldsymbol k_1+\dots+\boldsymbol k_n$, the order $n$ is the number of
momenta, as for the bare kernels:

| you write | it is | type |
|---|---|---|
| `Fx(k1, ..., kn)` | $F^x=F_n(\boldsymbol k_1,\dots,\boldsymbol k_n)\,e^{-i\boldsymbol k\cdot\boldsymbol r/2}$ | `FSum` |
| `Fy(k1, ..., kn)` | $F^y=F_n(\boldsymbol k_1,\dots,\boldsymbol k_n)\,e^{+i\boldsymbol k\cdot\boldsymbol r/2}$ | `FSum` |
| `G(k1, ..., kn)` | $G=G_n(\boldsymbol k_1,\dots,\boldsymbol k_n)\,g(\boldsymbol k)$ | `AxialIntegrand`, rank 1 |
| `FKernel(k1, ..., kn)`, `GKernel(k1, ..., kn)` | the bare $F_n$, $G_n$ | `Expr` |

So `Fx(k)` is the phase $e^{-i\boldsymbol k\cdot\boldsymbol r/2}$ alone ($F_1=1$),
`G(k)` is $g(\boldsymbol k)$, `Fx(k1, k2)` carries $F_2$ and `G(k1, k2, k3)` carries $G_3$.

```python
from granada import Vector, PL
from granada.feynman import Fx, Fy, G, feynmanReduce

k1, k2, k3, k4 = (Vector(f"k{i}") for i in range(1, 5))
I = Fx(k1, k3) * Fy(-k3, k2) * G(-k1, -k2) * G(k3, k4) * PL(k1) * PL(k2) * PL(k3) * PL(k4)
L = feynmanReduce(I, path="feynman.html")
```

* These are the Feynman pipeline's `Fx` and `Fy`, written at the midpoint
  from the start; the Schwinger pipeline's write $e^{i\boldsymbol k\cdot\boldsymbol x}$
  and $e^{i\boldsymbol k\cdot\boldsymbol y}$ instead. `G` is the same in both.
* The bare kernels are the standard recursion,
  $F_n=\sum_{m=1}^{n-1}\frac{G_m(\boldsymbol q_1..\boldsymbol q_m)}{(2n+3)(n-1)}\big[(2n+1)\alpha(\boldsymbol k_1,\boldsymbol k_2)F_{n-m}+2\beta(\boldsymbol k_1,\boldsymbol k_2)G_{n-m}\big]$,
  and $G_n$ with $3\alpha F_{n-m}+2n\beta G_{n-m}$, symmetrised. The closed forms
  `F2` and `G2` are used at $n=2$. $F_n$ has 36 terms at $n=3$, 576 at $n=4$
  and 12,960 at $n=5$ (about 3 s). The tests check it against an independent
  numerical recursion and against the collinear limit $F_n=G_n=k^n/(n!\,q_1\cdots q_n)$.
* A product of them is an `AxialIntegrand` whose axial rank is the number of
  `G`'s, plus any `g`'s you write yourself. The `Fx`'s and `Fy`'s go into
  $\Phi$ with their phases.
* The input block shows the integrand as typed, $F^x(\boldsymbol k_1,\boldsymbol k_3)\,F^y(-\boldsymbol k_3,\boldsymbol k_2)\,G(-\boldsymbol k_1,-\boldsymbol k_2)\cdots$,
  then with every dressed kernel written out,
  $F_2(\boldsymbol k_1,\boldsymbol k_3)\,e^{-i(\boldsymbol k_1+\boldsymbol k_3)\cdot\boldsymbol r/2}\cdots G_2(-\boldsymbol k_1,-\boldsymbol k_2)\,g(-\boldsymbol k_1-\boldsymbol k_2)\cdots$,
  then with each $v_z$ written out. A first-order kernel is written out as its
  phase or its $g$ alone, since $F_1=G_1=1$. From the peel on, the stages show
  the phases and sines themselves.
* They mix freely with everything else: `Fx(k1, k2) * F2(k1, k3) * g(k1)` is
  a valid integrand.

#### Sums of terms

An observable is often several diagrams, each a term with its own g's. Add
them, and `feynmanReduce` runs each term on its own and adds the results:

```python
I = (G2(k1, k2) * PL(k1) * PL(k2) * g(-k2) * g(k1)
     + F2(k1, k2) * PL(k1) * PL(k2) * g(k1) * g(k2))       # an AxialSum
L = feynmanReduce(I)                                        # a LedgerSum
S = evalTower(L, M, basis=[k1, k2, k1 + k2], flip=k1)     # each A_s summed over terms
```

* Terms with the same g's still add their $\Phi$'s into one term, as before;
  only different g's make an `AxialSum`. `sum([I1, I2, I3])` works, and so
  do `-`, a number or a scalar times the sum, and `/`.
* Each term goes through peel, project and average on its own. The
  `LedgerSum` then adds the terms' entries power by power of $\nu$: equal
  integrands are merged and what cancels is dropped, so
  $A_s=\sum_{\text{terms}}A_s^{(t)}$. Each term's own `Ledger` stays in
  `L.ledgers`.
* The page shows the sum as typed, then every term's stages in its own
  section, *Term 1*, *Term 2*, ..., then the summed entries (*Sum of the 2
  terms*) and the result.
* A `LedgerSum` is a `Ledger`, so `evalTower`, `toI25`, `denominators`,
  `partialFraction` and `shiftBessel` take it. `evalTower` evaluates each
  summed $A_s$ as one tower and simplifies it as a whole, so cancellations
  between diagrams show.
* `upTo="peel"` or `"project"` returns the list of each term's object, since
  only Ledgers add. `peel()` and the stages after it take one term,
  `I.terms[i]`.
* A sum inside the dict, `feynmanReduce({"observable": I1 + I2, ...})`, gives a
  `LedgerSum` for that name.

#### Checking by hand: everything renders

Every object you can reach renders as LaTeX. In a notebook it typesets itself
(`_repr_latex_`). Anywhere, `.latex()` returns the source and
`.render(path="x.html")` writes a page. This covers the stage objects, their
fields and the containers inside them, so you can display any intermediate
step on its own:

```python
L = average(project(peel(I)))
P = L.projection
P.tensor.envelope          # the envelope E, an FSum
P.brackets                 # the brackets S
P.gram, P.weights          # G and W (sympy matrices)
P.matrixTex("weights")     # W as a table labelled by brackets and contractions
P.coefficientsTex()        # every c_S as weights times contractions of T
P.channels[1]              # A_1 = sum C int Q, as labels and evaluated
P.channels[1][0].probe     # one probe Q, written out in full
L.averages[1]              # each <Q> over rhat, before weighting and merging
L.entries[1]               # A_1 = sum C' Q'
L.entries[1][0].integrand  # one Q', a Term
```

The core algebra types (`Vector`, `SP`, `Expr`, `Lin`, `SphBessel`, `Term`,
`TermSum`, `Func`, `FSum`) and `Labels` have the same three methods, so a
`refAverage` or `reduce` result displays without wrapping it in `render()`.
In a notebook, block captions such as "ν^2" or "c_S" are typeset in math
mode, where a bare `_` or `^` would otherwise be a TeX error.

The stages can also be run one at a time:

```python
I = G2(k, p) * PL(k) * PL(p) * g(k) * g(p) * g(k + p)   # AxialIntegrand
T = peel(I)                                              # AxialTensor
P = project(T)                                           # Projection
L = average(P)                                           # Ledger
P.render(path="projection.html")                         # every stage object renders
```

Several terms go on one page by passing a dict. Each is run on its own, in a
section of the page under its name, and the result is `{name: Ledger}`:

```python
Ls = feynmanReduce({"term 1": I1, "term 2": I2}, path="terms.html")
Ls["term 2"].entries[2]
```

`feynmanReduce(expr, upTo="project")` stops after the projection and returns the
`Projection`. `upTo` is one of `"peel"`, `"project"` and `"average"`. The stages
are a list in `feynman.STAGES`, so adding `reduce`, `align`, `fold` and `export`
later means adding one entry each, plus its type. If a stage fails, the error
names it: `feynmanReduce, stage 'peel': ...`.

#### Types

Each stage takes exactly one type and returns exactly one type:

| Object | Type | Produced by |
|---|---|---|
| product of g's | `GString` | `g(v)`, `*`, `**` |
| $\Phi$ · GString | `AxialIntegrand` (`envelopeScalar`, `gstring`, `rank`) | `Phi * g(k) * g(p)` |
| $\hat z\cdots\hat z\,T$ | `AxialTensor` (`legs`, `envelope`, `rank`, `indices`) | `peel(AxialIntegrand)` |
| $\delta$/$\hat r$ structure | `Bracket` (`structure`, `nuPower`) | part of a `Projection` |
| $(C, Q)$ | `Channel` (`weight`, `probe`) | part of a `Projection` |
| stage-2 result | `Projection` (`tensor`, `brackets`, `gram`, `weights`, `channels`) | `project(AxialTensor)` |
| $\langle Q\rangle_{\hat r}$ | `Average` (`channel`, `average`) | part of a `Ledger` |
| $(C', Q')$ | `Entry` (`coefficient`, `integrand`) | part of a `Ledger` |
| stage-3 result | `Ledger` (`entries`, `averages`) | `average(Projection)` |
| a sum of terms with different g's | `AxialSum` (`terms`) | `I1 + I2` |
| the terms' Ledgers added | `LedgerSum`, a `Ledger` (`entries`, `ledgers`) | `feynmanReduce(AxialSum)` |

The type rules:

* `peel` takes only an `AxialIntegrand`, `project` only an `AxialTensor` and
  `average` only a `Projection`. Anything else raises a `TypeError` that names
  the stage the object belongs to and where it should go instead. Nothing is
  coerced.
* **A bare `GString` is refused, not wrapped.** It has no $\Phi$. Write
  `1 * g(k) * g(p)` for $\Phi=1$.
* `AxialIntegrand` refuses a $\Phi$ that contains a Bessel, a sin/cos/cexp
  that is not a phase (in $\boldsymbol r$, or the Schwinger pipeline's in
  $\boldsymbol x$ and $\boldsymbol y$, which `peel` then refuses), or `ref` outside a phase (including `mag(ref)`). Phases
  and factors of $i$ are allowed. Terms with the same g's add up:
  `2*g(k) + 3*g(k) == 5*g(k)`. Terms with different g's, such as
  `SP(k, k)*g(k) + SP(p, p)*g(p)`, make an `AxialSum`, which
  `feynmanReduce` takes (and `schwingerReduce(..., midpoint=True)`); a term
  with no g at all is refused.
* `refAverage`, `reduce`, `align`, `fold`, `wl`, `getTower` and `labels`
  refuse every object of the pipeline (`GString`,
  `AxialIntegrand`, `AxialTensor`, `Bracket`, `Projection`, `Channel`,
  `Average`, `Entry`, `Ledger`, and the containers inside them) and say which stage it belongs to. A `Ledger` is pointed to `evalTower()`, which takes it. In particular,
  `refAverage` accepts only scalars. The pipeline hands it `Channel.probe`,
  never a tensor.
* `render` and `latex` take every object of the pipeline, alone or in a list
  with anything else, e.g. `render([I, T, P, L])`. Stage objects also render
  themselves with `.latex()`, `.render(path=..., openBrowser=False)` and
  `_repr_latex_`.
* **Like terms are collected.** Within each power of $\nu$, channels with
  equal probes are merged into one and their weights summed. This happens
  when legs repeat: for $g(\boldsymbol k)^3$, $T_{a\hat ra}$ and $T_{\hat raa}$
  are the same probe. Entries with equal integrands are merged into one and
  their coefficients summed. Zeros are dropped. Each $A_s$ reads
  "number × integrand" with no integrand repeated. To make that possible,
  the averaged coefficients are expanded bilinearly over the atoms, as in
  `refAverage`.

#### Glossary

The first entries, up to `Projection`, are the core's tensor algebra; the
rest are the Feynman pipeline's.

* **axis**: the fixed unit vector $\hat{\boldsymbol z}$ that the $v_z$ in $g$ are taken along.
* **axial rank** $n$: the number of g factors, which is the rank of $T$.
* **`GString`**: a product $g(\boldsymbol v_1)\cdots g(\boldsymbol v_n)$, built with `g()`, `*` and `**`. It commutes.
* **`AxialIntegrand`**: one term $\Phi\cdot$`GString`, the input of the pipeline. $\Phi$ (`envelopeScalar`) is the scalar factor, made of kernels, $P_L$, scalar products, phases and $i$.
* **phase**: a `cexp`, `sin` or `cos` in $\Phi$ whose argument is $\sum_j c_j\,(\boldsymbol q_j\cdot\boldsymbol r)$ with rational $c_j$, such as $e^{i(\boldsymbol k_3-\boldsymbol k_1)\cdot\boldsymbol r/2}$. It is the only way `ref` enters $\Phi$.
* **dressed kernel**: `feynman.Fx`, `feynman.Fy` or `G` of $n$ momenta, a kernel times what it always comes with: $F_n$ times its phase $e^{\mp i\boldsymbol k\cdot\boldsymbol r/2}$, $G_n$ times $g(\boldsymbol k)$, with $\boldsymbol k$ the total momentum. The bare kernels are `FKernel` and `GKernel`.
* **envelope** $E$: the scalar left after the axis comes off, $\Phi\prod_a 2\sin(\boldsymbol v_a\cdot\boldsymbol r/2)/v_a^2$. It is stored as an `FSum` with $\Phi$'s phases and the real `sin(SP(v, ref)/2)` factors.
* **legs**: the momenta $\boldsymbol v_a$ of the g's. Each leg carries one free index of $T$.
* **peel**: stage 1. It writes each $v_z$ as $\hat z_i v_i$ and pulls the $\hat z$'s off, $\mathcal I=\hat z\cdots\hat z\,T$.
* **`AxialTensor`**: the result of the peel: legs, envelope, rank and the free index names.
* **`Bracket`**: one $\delta$/$\hat r$ structure $S$ of the tensor Ansatz. Its `nuPower` $s(S)$ is its number of $\hat r$ slots, so $\hat z\cdots\hat z\cdot S=\nu^{s(S)}$.
* **Weingarten weights** $W$: the inverse of the Gram matrix $G_{S'S}=S'\cdot S$ of the brackets in $d=3$ (the pseudo-inverse once they are dependent, from rank 6 on). They turn contractions of $T$ into Ansatz coefficients.
* **probe** $Q=S'\cdot T$: a full contraction of $T$ with a bracket. It is a scalar integrand, $E$ times $\boldsymbol v_a\cdot\boldsymbol v_b$ per $\delta$ and $(\boldsymbol v_a\cdot\boldsymbol r)/r$ per $\hat r$.
* **project**: stage 2. It expands $\int T$ in brackets and regroups by the power of $\nu$, $\int\mathcal I=\sum_s\nu^sA_s$ with $A_s=\sum C\int Q$.
* **`Channel`**: one term $C\int Q$ of an $A_s$. `weight` $C$ is a rational (the Weingarten weights summed over the brackets of that power of $\nu$ and over the $S'$ that share the probe). `probe` $Q$ is a scalar `FSum`.
* **`Projection`**: the result of stage 2: the tensor, the brackets, the Gram matrix `gram`, the weight matrix `weights` and `channels`, `{power of ν: [Channel]}`.
* **ν**: $\hat{\boldsymbol z}\cdot\hat{\boldsymbol r}$, the cosine between the axis and $\boldsymbol r$. Only its powers $s\equiv n \pmod 2$ appear.
* **average**: stage 3. Each probe is replaced by its average over the direction of $\hat{\boldsymbol r}$ (`refAverage`), which equals it under the integral.
* **`Entry`**: one term $C'\,Q'$ of an averaged $A_s$. `coefficient` $C'$ is a rational with its power of $i$. `integrand` $Q'$ is a `Term` with coefficient 1: a monomial times $r^p$ times one $j_\ell$ or none (also available as `monomial`, `rPower`, `bessel`).
* **`Average`**: one probe and its average $\langle Q\rangle_{\hat r}$ (`refAverage(channel.probe)`), before the weight is applied and like terms are merged. It is there to be checked.
* **`Ledger`**: the result of stage 3: `entries`, `{power of ν: [Entry]}`, with no integrand repeated within a power, and `averages`, `{power of ν: [Average]}`.
* **`AxialSum`**: a sum of `AxialIntegrand`s with different g's, `terms`, as the diagrams of one observable. `feynmanReduce` takes it, and so does `schwingerReduce(..., midpoint=True)`.
* **`LedgerSum`**: the `Ledger`s of an `AxialSum`'s terms added, `entries` per power of ν; a `Ledger` itself, so whatever takes a `Ledger` takes it. Each term's own `Ledger` is in `ledgers`.
* **`feynmanReduce`**: the driver. It runs the stages up to `upTo`, renders one page and returns the last object.
* **isotropy lemma**: stages 2 and 3 hold after integration, not point by point, because every vector is integrated over, the measure is isotropic and $\Phi$ has no $\hat{\boldsymbol z}$.

#### Evaluating the tower: evalTower

`getTower()` writes the tower for Mathematica, where you define `M`, sum the
tower and `FullSimplify` it. `evalTower()` does that last step here. It
evaluates the same tower at your master integral, adds it up, simplifies the
sum, renders every stage and returns the result.

```python
from granada.feynman import evalTower, master

M = master("""M[l_, a_, b_, c_, r_] := 1/(16 Pi^3)
    Gamma[3/2 - b] Gamma[3/2 - c] Gamma[b + c - 3/2]/(Gamma[b] Gamma[c] Gamma[3 - b - c])
    r^(2 (a + b + c) - 6) 2^(4 - 2 (a + b + c))
    Gamma[(l + 6 - 2 (a + b + c))/2]/Gamma[(l - 3 + 2 (a + b + c))/2]""")

V = evalTower(t, M, basis=family, path="tower.html")   # t, family as in Sixty seconds
V.value                    # the result: a sympy expression in V.n and V.r
getTower(t, "run1.m", basis=family)                    # unchanged: the same tower, as a file
```

This `M` is $\int\!\frac{d^3k\,d^3p}{(2\pi)^6}\,j_\ell(kr)\,k^{-2a}p^{-2b}|\boldsymbol k+\boldsymbol p|^{-2c}$,
the bubble in $\boldsymbol p$ and then the $k$ integral of a power times $j_\ell$.
For the sixty-seconds example the page ends with

$$\frac{2^{2n}r^{-2n-1}\,\Gamma^2\!\left(\tfrac n2+\tfrac12\right)}{896\pi^3\,\Gamma\!\left(2-\tfrac n2\right)}
\left[\frac{7n^2-6n+8}{(2n-1)\,\Gamma\!\left(2-\tfrac n2\right)}
-\frac{2^{n+1}(n^2+8n-14)\,\Gamma\!\left(\tfrac12-\tfrac n2\right)}{(n+2)(n+4)\,\Gamma\!\left(\tfrac32-n\right)}\right]$$

where 6 of the 24 masters vanish (a $1/\Gamma$ at a pole: a scaleless bubble).
The two $\Gamma$ structures are not related by any identity except
reflection, which brings in trigonometric functions, so they stay apart.

* **The tower is `getTower()`'s.** `evalTower` takes the same objects and the
  same keywords (`basis`, `denominator`, `propagators`, `dropScaleless`) and
  evaluates exactly the blocks, coefficients and labels the file would hold:
  each block is $i^k r^p\sum c\,M(\ell, a_1, \dots, a_P, s\,r)$, with the
  labels denominator powers unless `denominator=False`, the order $\ell$ first
  and the Bessel's scale $s$ in the last argument.
* **The master is yours**, in either of two forms:
  * a Mathematica definition, as a string, pasted from your notebook, such as
    `M[l_, a_, b_, c_, r_] := ...`. Line breaks, comments `(* *)`, a closing
    `;`, `=` instead of `:=` and pattern heads (`l_Integer`, `b_?NumericQ`)
    are all fine. `Gamma`, `Beta`, `Binomial`, `Factorial` (`x!`),
    `Pochhammer`, `Sqrt`, `Exp`, `Log`, `Sin`, `Cos`, `Abs`,
    `Hypergeometric2F1` and `HypergeometricPFQ` are understood. Anything else
    is refused by name, and so are a condition `/;`, a definition for
    particular values (`M[l_, 0, b_, c_, r_] := 0`) and two statements. A bare
    right-hand side needs `args=("l", "a", "b", "c", "r")`.
  * a Python function `M(l, a, b, c, r)` returning a sympy expression. It is
    called with sympy numbers and expressions in $n$, so it may branch on its
    arguments, e.g. return 0 for a scaleless label.
* **Write a negative exponent in parentheses**: `x^(-1)/2` or `x^(-1/2)`.
  sympy's reader takes `x^-1/2` for $x^{-1/2}$ and `x^-1 y` for $x^{-y}$,
  where Mathematica reads $x^{-1}/2$ and $y/x$, so `x^-` followed by anything
  but `(` is refused rather than guessed.
* **The arity is checked**, as for `getTower`: the tower calls
  `M[l, <P exponents>, r]`, and a master taking any other number of arguments
  is refused.
* **$n$ and $r$** are the sympy symbols `V.n` (real) and `V.r` (positive).
  Any symbol named `n` or `r` in your master other than its own arguments is
  taken to be them. For numbers, `V.value.subs({V.n: -1.5, V.r: 2})`. An
  index of its own, `PL(k, "n1")`, is the real symbol `index("n1")`
  (`granada.feynman.evaltower.index`), in the labels and in your master alike.
* **A singular label is refused**, with the rows it occurs in. That is a
  $\Gamma$ at a pole that nothing cancels, where Mathematica would give
  `ComplexInfinity` or `Indeterminate`. Treat it in the master. A label at
  which the master vanishes is fine, and the page counts them.
* **The result is checked.** The simplified value is compared with the tower
  as evaluated, numerically at 50 digits at a generic $n$ and $r$, and a
  disagreement raises. `V.checked` says where and to how many digits.
  Several indices are checked apart from one another, so a result that
  confuses $n_1$ and $n_2$ does not pass; the page lists the value of each.
  `check=False` skips it. `simplify=False` returns the sum as evaluated.
* **`V.wl()`** gives the result as Mathematica input, to compare with your
  own `FullSimplify` while you still have both.
* **Several expressions** at once, a list `[A1, A2]` or a dict `{"A1": A1}`,
  are evaluated each on its own and named as `getTower` names them. The
  result is then `{name: TowerValue}`, and the master is shown once at the
  top of the page.
* **A `Ledger` goes straight in**, for a term of two momenta: see
  [Straight from feynmanReduce](#straight-from-feynmanreduce).

The page opens on the result. Everything it took to get there follows,
for checking by hand:

1. the result, simplified;
2. the check;
3. the master integral, as read;
4. the tower, collapsed: the legend $D_i:=\dots$, the definition of
   $M_\ell$, then $\sum c\,M_\ell(a_1,a_2,a_3;\,s\,r)$, one master per row;
5. each master evaluated, collapsed: $M_\ell(\dots) = \dots$, and in the
   caption how many vanish.

The tower and the masters start collapsed whatever their size, and open
with a click; nothing in them is typeset until then. `V.render(path=...)`
writes the same page. In a notebook, which cannot collapse what it
typesets, `V` shows the result, the check and the master, and names the
collapsed blocks, with a pointer to `V.render(path=...)` for them.
`V.latex()` is the source of all of it.

`V.blocks` holds each block with its `labels` (the `Labels` of `labels()`),
its `rows` `(coefficient, label, value)` and its unsimplified `value`. `V.raw`
is their sum, and `V.master` is the `Master`, which you can also call
yourself, with sympy values: `V.master(1, 1 - V.n/2, 1, 1, V.r)`.

##### Straight from feynmanReduce

For a term of two momenta, the `Ledger` that `feynmanReduce()` returns goes
straight in:

```python
from granada import Vector, G2, PL, g
from granada.feynman import feynmanReduce, evalTower

k, p = Vector("k"), Vector("p")
L = feynmanReduce(G2(k, p) * PL(k) * PL(p) * g(k) * g(p) * g(k + p))
S = evalTower(L, M, basis=[k, p, k + p], flip=k)

S[1].value        # A_1, simplified
S.value           # int I = sum_s nu^s A_s, in S.nu, S.n, S.r
```

For each power of $\nu$, the entries $C'Q'$ are added up into $A_s$ (a
coefficient's $i$ as `I`). $A_s$ is then reduced, aligned onto `basis[0]`,
aimed, and folded under `flip` $\to$ `-flip` onto `basis`, as `refReduce()`
does, and evaluated as any tower is. Aiming fixes what `fold` alone cannot.
`reduce()` writes $\boldsymbol k_1\cdot\boldsymbol k_2$ with $(k_1+k_2)^2$ upstairs,
so a sub-term whose propagators are those of the mirror family
$[k_1,k_2,k_1-k_2]$ (one from $g(\boldsymbol k_1-\boldsymbol k_2)$, say) carries
both halves of the mirror pair, and reflecting only swaps them. Each
sub-term's numerator is therefore re-expanded in the family its propagators
lie in, with $(k_1+k_2)^2=2k_1^2+2k_2^2-(k_1-k_2)^2$. That is the README's
`e.expand(basis=[k, p, k-p])`, done per sub-term. Only numerator powers
change, an identity at every point, and the fold then finishes. Each $A_s$ is checked against its own tower.
The result is a `TowerSeries`: `{power of ν: TowerValue}`, each named `A_s`,
with `.value` $=\sum_s\nu^sA_s$. The page opens on the assembled result, one
power of $\nu$ per row, then each $A_s$ and its check, then the master. Every
$A_s$'s towers and masters follow, collapsed, each captioned with its power
of $\nu$.

For the example above, each of $A_1$ and $A_3$ is 89 masters in three blocks
($j_1$, $j_2$, $j_3$), 30 of which vanish, and each simplifies to two $\Gamma$
structures.

* **`basis=` and `flip=` are required**, as for `refReduce()`: they are facts
  about the integral, not the algebra. `flip=` is for a `Ledger` only.
  Anything else you fold yourself, as for `getTower()`.
* **A sum of diagrams** goes in as one: `feynmanReduce(I1 + I2)` returns a
  `LedgerSum`, the terms' entries added power by power of $\nu$, and
  `evalTower` evaluates each summed $A_s$ as one tower, simplified together
  (see [Sums of terms](#sums-of-terms)).
* **The dict** `feynmanReduce({"term 1": I1, "term 2": I2})` returns goes in
  too, and gives `{name: TowerSeries}` on one page, each on its own.
* **Two momenta only.** A `Ledger` in $k_1, k_2, k_3$ is refused: its masters
  are an outer integral times the five-line two-loop integral (see
  [toI25](#the-five-propagator-two-loop-integral-toi25)), not
  $M(\ell; a, b, c)$.
* **Pieces without a Bessel** appear where the sines cancel ($\boldsymbol K=0$),
  as in $F^x(\boldsymbol k_1)F^y(\boldsymbol k_2)G(\boldsymbol k_1)G(\boldsymbol k_2)$.
  They are scaleless, and the error says to pass `dropScaleless=True`; the
  page then shows them under each $A_s$ (*ν^s: left out by dropScaleless*),
  or says *no scaleless terms* for an $A_s$ without any, and `S[s].left`
  holds them.
* **Not every two-momentum term lands on the family.** A Bessel can sit on a
  combination such as $\boldsymbol k+\boldsymbol p/2$: from a phase, as in
  $F^x(\boldsymbol k,\boldsymbol p)\,G(\boldsymbol k)$, or from $g(\boldsymbol k+\boldsymbol p)$
  next to $g(\boldsymbol k)$. The only shift that puts it on one momentum,
  $\boldsymbol p\to\boldsymbol p-2\boldsymbol k$, brings in
  $(\boldsymbol k-2\boldsymbol p)^2$, which lies in neither $[k,p,k+p]$ nor its
  mirror, so no master of the family evaluates it. That $A_s$ is refused,
  with how many of its sub-terms are affected and which propagators they
  keep.
* Everything else (`denominator`, `propagators`, `dropScaleless`,
  `simplify`, `check`, `path`) works as for any tower.

#### Denominators: which propagators appear

Every momentum combination that stands as a propagator is classified. A
propagator is *genuine*, a negative rational power $1/(v^2)^e$, or
*$n$-dependent*, a power $(v^2)^{a+bn}$ such as $P_L(k)/k^4=k^{n-4}$. Both
kinds count as propagator structures.

```python
rep = denominators(L)          # L = average(project(peel(I))); any expression works
rep                            # typesets the report; render([rep]) writes it to a page
rep.propagators                # {v: Usage}: every propagator structure, of either kind
rep.propagators[v].kind        # "genuine", "n-dependent" or "both"
rep.genuine                    # {v: Usage}: every v with 1/(v^2)^e, e rational
rep.nDependent                 # {v: Usage}: every v with an n-dependent power
rep.dotProducts                # {u.v: Usage}: should be empty, flagged if not
rep.termsWith(k1 + k2)         # which terms carry it: (nu power, index) in a Ledger
rep.structures                 # [Structure]: the distinct structures of the sub-terms
```

The summary table counts, for each momentum combination, the sub-terms it
appears in. It says nothing about which combinations appear *together*, so
underneath it the report lists **every distinct structure of the sub-terms,
each once**: the set of propagators one sub-term has, exponents aside, with
the momentum its Bessel sits on (underlined on the page, `*` in the text),
how many propagators that is and how many sub-terms have it. For term 3 of
the six-term example, before any shift:

```
  4 distinct structures of the sub-terms (* the Bessel's momentum; a family has 6):
    {(k1)^2, (k2)^2, (k3)^2*, (k1-k2)^2} 4 [160]
    {(k1)^2, (k2)^2, (k3)^2, (k1-k2)^2, (k1-k3)^2*} 5 [272]  BESSEL ON A COMBINATION
    {(k1)^2, (k2)^2, (k3)^2, (k1-k2)^2, (k2-k3)^2*} 5 [256]  BESSEL ON A COMBINATION
    {(k1)^2, (k2)^2, (k3)^2, (k1-k2)^2, (k1-k2+k3)^2*} 5 [320]  BESSEL ON A COMBINATION
```

A structure is flagged when it has more than $N=L(L+1)/2$ propagators, when
they are linearly dependent, or when its Bessel sits on a combination of
momenta rather than on one. The seven structures of the summary never occur
together: no sub-term has more than five.

For the rank-4 example of the Feynman pipeline (13,495 terms, read in 0.3 s):

```
DenominatorReport: 13495 terms, 7 propagator structures
  genuine denominators: (k1+k2)^2 [1908], (k1+k3)^2 [2304], (k2+k3)^2 [1908], (k1+k2+k3)^2 [13495]
  n-dependent: (k1)^2 [13495], (k2)^2 [13495], (k3)^2 [13495]
  dot products in a denominator: none
```

A term is one summand: one `Entry` of a `Ledger`, or one monomial of an
expression. Every term is read. Each `Usage` says in how many terms the
structure occurs, with which exponents, and at which powers of $\nu$.

* **Only the momentum combination counts.** $1/(v^2)$, $1/|v|$ and
  $1/(v^2)^2$ all report $v$; the exponents seen are kept for reference.
* **$v$ and $-v$ are one combination**, written with its first atom positive.
* **An $n$-dependent power is a propagator too.** $P_L(k)/k^4$ is stored as one
  factor $k^{n-4}$, whose sign is not known. Its combination is a propagator
  structure of kind `"n-dependent"`, listed in `propagators` and in
  `nDependent`. A combination seen both ways, say $1/k^2$ in one term and
  $k^{n-4}$ in another, is one structure of kind `"both"`. `termsWith(v)`
  finds the terms carrying $v$ in either way.
* **A scalar product $u\cdot v$ in a denominator is flagged** with a warning.
  So is a $(q\cdot r)$ still depending on the direction of $\hat r$. $r$
  itself is not a momentum and is skipped.

Nothing can be missed, by construction. The algebra cannot hold $1/(a+b)$
(`Expr._inverse` refuses a sum), so every denominator in a term is a power of
one scalar product, an exponent in the term's monomial. Expansion never
touches a negative or fractional power. Reading every exponent of every term
finds every denominator, and the tests check exactly that against an
independent scan of the same terms.

#### Shifting every Bessel onto one momentum

```python
S = shiftBessel(L)                 # L = average(project(peel(I))); any expression works
S = shiftBessel(L, prefer=[k3])    # which momentum to shift when there is a choice
denominators(S)                    # the structures, every Bessel on one momentum
```

A sub-term whose Bessel sits on $\boldsymbol K=\sum_bc_b\boldsymbol k_b$ is
shifted by $\boldsymbol k_a\to c_a\big(\boldsymbol k_a-\sum_{b\ne a}c_b\boldsymbol k_b\big)$
for one momentum with $c_a=\pm1$, which turns $\boldsymbol K$ into
$\boldsymbol k_a$. The Jacobian is 1 and every sub-term is its own integral
over all the momenta, so each is shifted by its own substitution, and every
other factor of it goes along: its propagators and $n$-dependent powers move
too. It is `Term.shift`, the shift `reduce()` makes. Numerator scalar
products are expanded over the momenta again and equal sub-terms merged, so
the number of sub-terms changes.

* When several momenta have $c=\pm1$, the first in `prefer` is shifted, else
  the first by name. Different choices give different structures: for term 3,
  `prefer=[k3]` puts every Bessel on $\boldsymbol k_3$, each structure
  $\{k_1^2,k_2^2,\underline{k_3^2},(\boldsymbol k_1-\boldsymbol k_2)^2\}$ plus
  at most one more.
* A $\boldsymbol K$ with no momentum of coefficient $\pm1$, such as
  $2\boldsymbol k_1+3\boldsymbol k_3$, admits no shift of unit Jacobian by one
  momentum. Its sub-terms are left as they are, logged, and flagged by
  `denominators()`.
* The result equals the input under the integral, not point by point. The
  tests check each shift as what it is, a change of variables: every shifted
  sub-term at $\boldsymbol k$ equals the original at the substituted momenta.
* It is not a stage of the pipeline. For the six-term example every sub-term
  then has at most 6 independent propagators, its Bessel on one momentum.

#### The five-propagator two-loop integral: toI25

```python
rep = toI25(L, k1, k2, k3)     # L = average(project(peel(I))); k1 outer, k2 and k3 inner
rep.flagged                    # [Flag]: the terms that cannot be put in this form, and why
rep.integrals                  # {power of nu: [I25]}
rep.mappings                   # per structure: the change of variables and the line of each propagator
```

Every term becomes an outer integral over $\boldsymbol k_1$, which carries the
Bessel, times the two-loop integral of Bierenbaum and Weinzierl,

$$\hat I^{(2,5)}(\nu_1,\dots,\nu_5)=c_\Gamma^{-2}\,(-p^2)^{\nu_{12345}-D}
\int\!\frac{d^D\ell_1}{i\pi^{D/2}}\int\!\frac{d^D\ell_2}{i\pi^{D/2}}
\prod_{i=1}^5\frac1{(-\ell_i^2)^{\nu_i}},$$

with external momentum $\boldsymbol p=\boldsymbol k_1$, $D=3$ ($m=3/2$,
$\varepsilon=0$) and the lines

| line | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| momentum | $\boldsymbol\ell_1$ | $\boldsymbol\ell_2$ | $\boldsymbol\ell_2-\boldsymbol p$ | $\boldsymbol\ell_1-\boldsymbol p$ | $\boldsymbol\ell_2-\boldsymbol\ell_1$ |

Each term is one integral over $\boldsymbol k_1,\boldsymbol k_2,\boldsymbol k_3$
and is mapped by its own change of variables
$(\boldsymbol k_1,\boldsymbol k_2,\boldsymbol k_3)\to(\boldsymbol p,\boldsymbol\ell_1,\boldsymbol\ell_2)$
with Jacobian 1:

1. The Bessel's momentum $\boldsymbol K$ becomes $\boldsymbol p$. A momentum of
   $\boldsymbol K$ with coefficient $\pm1$ is traded for it, $\boldsymbol k_1$
   first; when $\boldsymbol K$ does not involve $\boldsymbol k_1$ this renames
   the momenta, so the Bessel is always on $\boldsymbol k_1$ in the output.
2. Every propagator becomes $p^2$ or one of the five lines: the inner momenta
   are $\boldsymbol\ell_1=\boldsymbol a$, $\boldsymbol\ell_2=\boldsymbol b$ for
   some $\boldsymbol a,\boldsymbol b$ made of the other two momenta and
   $\boldsymbol p$, searched with coefficients up to $\pm2$.
3. Numerator scalar products are written in the lines and $p^2$, through
   $\boldsymbol\ell_1\cdot\boldsymbol p=\tfrac12(L_1+p^2-L_4)$,
   $\boldsymbol\ell_2\cdot\boldsymbol p=\tfrac12(L_2+p^2-L_3)$ and
   $\boldsymbol\ell_1\cdot\boldsymbol\ell_2=\tfrac12(L_1+L_2-L_5)$, so a term
   becomes a short sum of integrals with integer-shifted indices.

Each `I25` is $c\,r^{p}\,(k_1^2)^{e}\,j_\ell(s|\boldsymbol k_1|r)\,\hat I^{(2,5)}(\nu_1,\dots,\nu_5)$:
`nu` holds the power of each line in the denominator, $n$-dependent where a
$P_L$ sits, possibly negative; `outer` is the power $e$ of $k_1^2$ in the term
itself, and `outerTotal` adds the $(k_1^2)^{D-\nu_{12345}}$ the inner integral
brings. The constants of the normalisation ($c_\Gamma$, $\pi$, the signs of
$-k^2$) are left to you. Like integrals are merged.

**Flags come first.** A term that cannot be put in the form is listed, with
its propagators and the reason, and left out of `integrals`: no Bessel, a
Bessel whose momentum has no coefficient $\pm1$, no five-line mapping within
coefficients $\pm2$, or a scalar product in a denominator. For the six-term
example nothing is flagged:

| term | sub-terms | integrals | flagged |
|---|---|---|---|
| 1 | 672 | 2,612 | 0 |
| 2 | 5,350 | 5,494 | 0 |
| 3 | 1,008 | 2,310 | 0 |
| 4 | 944 | 2,128 | 0 |
| 5 | 6,436 | 6,016 | 0 |
| 6 | 6,436 | 5,962 | 0 |

It takes the `Ledger` as `average` returns it; `shiftBessel` is not needed
first. The tests check every mapping as the change of variables it is: each
term at the momenta the map gives equals the sum of its integrands
$\prod_iL_i^{-\nu_i}(p^2)^e j_\ell(s|\boldsymbol p|r)$, at random momenta, $r$
and $n$.

#### Partial fractions: down to independent propagators

```python
rep = partialFraction(L)       # L = average(project(peel(I))); any expression works
rep                            # typesets the report; render([rep]) writes it to a page
rep.result                     # the same expression, every term on independent propagators
rep.structures                 # the propagator structures that can appear in it
rep.families                   # {frozenset: terms}: the maximal sets of propagators
rep.irreducible                # {frozenset: terms}: what partial fractions cannot reduce
partialFraction(L, keep=[k1 + k2])   # which propagators to keep when one has to go
```

`partialFraction` is not a stage of the pipeline. It takes a `Ledger` (or its
`entries`, one `A_s`, or anything that lifts to an `FSum`) and returns a
report whose `result` is the same expression, rewritten. For a `Ledger` that
is a `Series` of `Entry`s per power of $\nu$. For `1 * g(k) * g(p) / SP(k - p, k - p)`:

```
PartialFractionReport: 2 loop momenta (k, p), at most 3 independent propagators
  before: 24 terms, 4 propagator structures of rank 3; 6 terms with dependent propagators
  after: 36 terms; 0 irreducible
  structures that can appear: (k)^2, (p)^2, (k+p)^2, (k-p)^2
  families (maximal sets of independent propagators):
    {(k)^2, (p)^2, (k+p)^2} [6 terms; Bessel on k+p]
    {(k)^2, (p)^2, (k-p)^2} [12 terms; Bessel on k-p]
    {(k)^2, (k+p)^2, (k-p)^2} [10 terms; Bessel on k+p]
    {(p)^2, (k+p)^2, (k-p)^2} [8 terms; Bessel on k+p]
```

**The count.** With $L$ loop momenta and nothing external, a propagator
$D_v=v^2$ is a quadratic form in the $\boldsymbol k_i\cdot\boldsymbol k_j$, so at
most $L(L+1)/2$ of them are linearly independent. A term's propagators are
those of [`denominators()`](#denominators-which-propagators-appear), genuine
and $n$-dependent, plus the momentum of its Bessel, which the masters put on
$D_1$. A term whose propagators are dependent satisfies $\sum_v c_vD_v=0$.

**The reduction.** Partial fractioning uses
$1=-\frac1{c_j}\sum_{i\ne j}c_i\,D_i/D_j$: each new term has one power less of
some $D_i$ and one more of $D_j$, and it is repeated until every term's
propagators are independent.

* Only a whole power can be brought to zero. A genuine propagator with an
  integer power can be removed. An $n$-dependent power ($P_L(k)/k^4$) or a
  half-integer one ($1/|\boldsymbol v|$) cannot, and neither can the Bessel's
  momentum: these are kept.
* A relation that involves two or more kept propagators cannot be used. So
  $P_L(k)\,P_L(p)/\big((k+p)^2(k-p)^2\big)$ is **irreducible**: its four
  propagators are dependent, but two of them carry $n$-dependent powers. Such
  terms are left as they are and listed under `irreducible`, with a warning
  on the page.
* Among the propagators that can be removed, those in `keep=` stay first,
  in its order, then those with fewer momenta, then by name. Each step lowers
  a power of lower priority and raises one of higher priority, so the
  reduction ends.
* It is algebra, true at every value of the momenta: no shift and no
  relabelling. The tests check every result numerically against its input,
  at random momenta, $r$ and $n$.
* A term that needs nothing is passed through as the same object. The
  four-momentum example of [Dressed kernels](#dressed-kernels-phases-in-r), 41,348 terms
  with 10 independent structures, takes about 5 s.

### Part III — the Schwinger pipeline

```python
from granada.schwinger import (Fx, Fy, G, SchwingerLedger, schwingerReduce,
                               getFinalExpression, master)
```

`schwingerReduce()` takes three-loop (any $L\le9$) Fourier-type integrals in
$d=3$,

$$I=\int \frac{d^3k_1}{(2\pi)^3}\cdots\frac{d^3k_L}{(2\pi)^3}\;R(K)\;e^{\,i\sum_i(\rho_i\,\boldsymbol x\cdot\boldsymbol k_i+\sigma_i\,\boldsymbol y\cdot\boldsymbol k_i)},$$

always with the measure $d^3k/(2\pi)^3$ for every loop,

and writes each term as generators acting on one closed-form Gaussian, the
**partition function**

$$Z(A,J)=\int \frac{d^{3L}K}{(2\pi)^{3L}}\,e^{-K^TAK+iJ\cdot K}=(4\pi)^{-3L/2}(\det A)^{-3/2}\exp\Big(-\frac{J^T(\operatorname{adj}A)J}{4\det A}\Big),\qquad J_i=\rho_i\boldsymbol x+\sigma_i\boldsymbol y,$$

where $(4\pi)^{-3L/2}=\pi^{3L/2}/(2\pi)^{3L}$ is the measure's constant
(`braid.normalization(L)`, the one place it is set).

Only the denominators become Schwinger integrals. Everything else, the
numerators, the linear factors and the sines, is a derivative or a shift
acting on $Z$.

**Two readings.** By default (`midpoint=False`) $\boldsymbol x$ and
$\boldsymbol y$ stay apart throughout, $J_i=\rho_i\boldsymbol x+\sigma_i\boldsymbol y$,
and the descendants act on $\rho$ and $\sigma$: a linear factor in
$\boldsymbol y$ is a derivative in $\sigma$, a sine of $\boldsymbol y\cdot\boldsymbol k$
shifts $\sigma$. $\boldsymbol x-\boldsymbol y$ is written and shown as it is.

**At the midpoint.** With `midpoint=True` (on `SchwingerLedger`,
`SchwingerTerm` or `schwingerReduce`) every term is first evaluated at
$\boldsymbol x=-\boldsymbol r/2$, $\boldsymbol y=\boldsymbol r/2$, before
anything else, and the descendants are built from that. The only external
vector left is $\boldsymbol r$ (written `ref`; it may also be typed directly),
so

$$J_i=\rho_i\,\boldsymbol r,\qquad \rho_i=\tfrac12(\sigma^{xy}_i-\rho^{xy}_i),\qquad
Z(A,J)=(4\pi)^{-3L/2}(\det A)^{-3/2}\exp\Big(-\frac{P\,r^2}{4\det A}\Big),\quad P=\rho^T\operatorname{adj}A\,\rho,$$

with $\rho^{xy},\sigma^{xy}$ the coefficients of $\boldsymbol x$ and $\boldsymbol y$
as typed. A linear factor $\boldsymbol q\cdot(a\boldsymbol x+b\boldsymbol y)$ is
$\frac{b-a}{2}\,\boldsymbol q\cdot\boldsymbol r$, a derivative in $\rho$ alone;
a sine of $\sum_jc_j\boldsymbol q_j\cdot(a_j\boldsymbol x+b_j\boldsymbol y)$ shifts
$\rho$ alone; no derivative in $\sigma$ is ever taken. The result is the
general pipeline's, evaluated at the midpoint: $x^2=y^2=r^2/4$,
$\boldsymbol x\cdot\boldsymbol y=-r^2/4$. The tests check this against the
original formulas, and against the full pipeline's integrand taken at the
midpoint (`tests/schwinger/test_midpoint.py`). A product that vanishes there, e.g. one with
$\boldsymbol k\cdot(\boldsymbol x+\boldsymbol y)$ or $\sin(\boldsymbol k\cdot(\boldsymbol x+\boldsymbol y))$,
is set aside with its number (`ledger.vanished`), and $\cos(0)=1$. The page
shows each term as typed and at the midpoint.

Below, the general formulas are kept; at the midpoint read $\boldsymbol x\to\boldsymbol r$,
$\sigma\to0$, $P_{xx}\to P$, $P_{xy}=P_{yy}=0$.

```python
R  = schwingerReduce(I, evaluateDescendants=True)                  # in x and y
Rm = schwingerReduce(I, midpoint=True, evaluateDescendants=True)   # at x = -r/2, y = r/2
Rm.ledger.vanished                                                 # what vanishes there
```

A ledger passed to `schwingerReduce` keeps its own reading unless `midpoint`
says otherwise, in which case its terms are read again from what was typed.

#### Sixty seconds

```python
from granada import Vector, External, SP, G2, PL, sin, cexp
from granada.schwinger import schwingerReduce

k1, k2 = Vector("k1"), Vector("k2")
x, y = External("x"), External("y")

I = (G2(k1, k2) * PL(k1) * PL(k2) / SP(k1 + k2, k1 + k2)
     * sin(SP(k1, x - y) / 2) * cexp(SP(k1, x) + SP(k2, y)))
R = schwingerReduce(I, evaluateDescendants=True, path="schwinger.html")

R.forms[0]                    # the SchwingerForm of term 1
R.forms[0].F                  # its evaluated derivatives, a polynomial (see below)
R.forms[0].factorizes         # does it factorize over the blocks of its family?
R.flagged                     # the terms that go no further, with the reason
```

The steps can be run one at a time, each taking exactly the type the
previous one returns:

```python
from granada.schwinger import (SchwingerLedger, getFamily, getGenerators, Generators,
                               getBraid, assemblePartitionFunction, getSchwingerForm)

T = SchwingerLedger(I)[0]
F, D = getFamily(T), getGenerators(T)      # F(T) with P, and D
G = Generators(F, D)                        # G = P u D
B = getBraid(F, D)                          # (A, J); B.flagged for a degenerate term
Z = assemblePartitionFunction(B)            # det A, adj A, the exponent, Z
S = getSchwingerForm(G, Z, evaluateDescendants=True)
S.integrand()                               # the whole integrand in sympy, for small cases
```

#### Notation

| symbol | code | meaning |
|---|---|---|
| $\mathcal F(T)$ | `F.FF` | the propagator family: the primaries $1/D_b^{\alpha_b}$, $D_b=(c_b\cdot K)^2$ |
| $\mathcal P$ | `F.PP` | the primary generators, one per element of $\mathcal F(T)$ |
| $\mathcal D$ | `D.DD` | the descendant generators: quadratic, linear and shift |
| $\mathcal G$ | `G.GG` | $\mathcal P\cup\mathcal D$, every generator with its `.type` |
| $\alpha_1,\alpha_{12},\bar\alpha_{12},\alpha_{123}$ | `p.alphaTex` | the power of $k_1^2$, $(k_1+k_2)^2$, $(k_1-k_2)^2$, $(k_1+k_2+k_3)^2$ |
| $\alpha_{1-2-3-4},\alpha_{1+2-3},\alpha_{1+2\,2}$ | `p.alphaTex` | the power of $(k_1-k_2-k_3-k_4)^2$, $(k_1+k_2-k_3)^2$, $(k_1+2k_2)^2$ |
| $z_1,z_{12},\bar z_{12},z_{1-2-3-4}$ | `p.name`: `z1`, `z12`, `zb12`, `z1m2m3m4` | the Schwinger variable, labelled like its power |
| $\mathcal U_B$, $\delta$ | `split.U`, `split.delta` | $\det A=\delta\prod_B\mathcal U_B$ over the blocks $B$ of the family (`split.groups`) |

Powers are written $1/D^\alpha$, so $\alpha>0$ is a denominator and
$(k_1^2)^n$ upstairs is $\alpha_1=-n$. $\alpha_b$ names the **net** power of the
structure; $\mathcal F(T)$ gives its value, e.g. $\alpha_{12}=n-1$.

#### The input: SchwingerTerm and SchwingerLedger

A `SchwingerTerm` is one product, written with the algebra. Its factors may be,
and nothing else:

| factor | written | becomes |
|---|---|---|
| $C$ | a rational, times `I` | the coefficient |
| $(q^2)^e$, $q=c\cdot K$ | `SP(q, q)**e`, $e$ an integer or $a+bn$ | a primary or a quadratic descendant |
| $(\boldsymbol u\cdot\boldsymbol v)^m$, $u\ne\pm v$ | `SP(u, v)**m`, $m=0,1,2,\dots$ | a quadratic descendant |
| $(\boldsymbol q\cdot(a\boldsymbol x+b\boldsymbol y))^m$ | `SP(q, x)`, `SP(q, x - y)`, ... | a linear descendant |
| $\sin$, $\cos$ of $\sum_j c_j\,\boldsymbol q_j\cdot(a_j\boldsymbol x+b_j\boldsymbol y)$ | `sin(SP(q, x - y) / 2)` | a shift descendant |
| $e^{i\sum_i\boldsymbol k_i\cdot J_i}$ | `cexp(...)`, several multiply | $\rho_i$, $\sigma_i$ |

Everything else is refused by name: a Bessel, `ref` (allowed at the midpoint), a factor in
$\boldsymbol x$ and $\boldsymbol y$ alone, a scalar product $u\cdot v$ or a
linear factor in a denominator or under a symbolic power, and a net power
that is a non-integer rational ($|q|$, $1/|q|$).

An input with `G`'s or `g`'s, which carry the axis $z$, is read at the
midpoint, its $z$'s projected out first: see [Dressed kernels: phases in x and y](#dressed-kernels-phases-in-x-and-y).

Nothing is expanded. $(k_1+k_2)^2$ stays one structure. $q$ and $-q$ are one
structure (first nonzero coefficient positive), and the same structure
upstairs and downstairs is one structure with its net power. That is the
only cancellation: $k_1\cdot k_2$ over $(k_1+k_2)^2$ is not rewritten.

| net power $\alpha$ | the structure is |
|---|---|
| $n$-dependent, or a positive integer | a **primary**: a denominator, with its Schwinger variable |
| a negative integer $-m$ | a numerator: the quadratic descendant $(c\cdot K)^{2m}$ |
| $0$ | dropped |

Every primary is labelled by its momenta. A sum is their numbers side by
side, $\alpha_{12}$, $\alpha_{123}$, and a difference of two is barred,
$\bar\alpha_{12}$. Anything else, a minus sign among three or more momenta
or a coefficient other than $\pm1$, has its signs written out, as the
subscripts of $\boldsymbol w_u$ and $M_{uv}$ are: $\alpha_{1-2-3-4}$ for
$(k_1-k_2-k_3-k_4)^2$, $\alpha_{1+2-3}$, $\alpha_{1+2\,2}$ for $(k_1+2k_2)^2$.
Its Schwinger variable is $z_{1-2-3-4}$, named `z1m2m3m4` in sympy (`m` for
$-$, `p` for $+$, `2x` for a coefficient 2).

`SchwingerLedger(expr)` splits an expression into its products, one term
each, numbered from 1; a list keeps its order. The momenta are every vector
that is not $\boldsymbol x$ or $\boldsymbol y$, in natural order, unless you
pass `momenta=`. Every term is read when the ledger is built, and every
refusal is reported in one error, before any further work.

#### Dressed kernels: phases in x and y

Every $F$ comes with its phase and every $G$ with its $g$, so they are
written together. For momenta $\boldsymbol k_1,\dots,\boldsymbol k_n$ with total
$\boldsymbol k=\boldsymbol k_1+\dots+\boldsymbol k_n$, the order $n$ is the number of
momenta, as for the bare kernels:

| you write | it is | type |
|---|---|---|
| `Fx(k1, ..., kn)` | $F^x=F_n(\boldsymbol k_1,\dots,\boldsymbol k_n)\,e^{i\boldsymbol k\cdot\boldsymbol x}$ | `FSum` |
| `Fy(k1, ..., kn)` | $F^y=F_n(\boldsymbol k_1,\dots,\boldsymbol k_n)\,e^{i\boldsymbol k\cdot\boldsymbol y}$ | `FSum` |
| `G(k1, ..., kn)` | $G=G_n(\boldsymbol k_1,\dots,\boldsymbol k_n)\,g(\boldsymbol k)$, $g(\boldsymbol v)=\frac{2v_z}{v^2}\sin\frac{\boldsymbol v\cdot\boldsymbol r}{2}$ | `AxialIntegrand`, rank 1 |
| `FKernel(k1, ..., kn)`, `GKernel(k1, ..., kn)` | the bare $F_n$, $G_n$ | `Expr` |

A field at $\boldsymbol x$ brings its phase $e^{i\boldsymbol k\cdot\boldsymbol x}$, at
$\boldsymbol y$ $e^{i\boldsymbol k\cdot\boldsymbol y}$; at the midpoint these are the Feynman
pipeline's $e^{-i\boldsymbol k\cdot\boldsymbol r/2}$ and $e^{+i\boldsymbol k\cdot\boldsymbol r/2}$.
So `Fx(k)` is the phase alone ($F_1=1$), `G(k)` is $g(\boldsymbol k)$,
`Fx(k1, k2)` carries $F_2$ and `G(k1, k2, k3)` carries $G_3$.

```python
from granada import Vector, PL
from granada.schwinger import Fx, Fy, G, schwingerReduce

k1, k2, k3 = Vector("k1"), Vector("k2"), Vector("k3")
I = Fx(-k2) * Fy(-k3) * G(-k1) * G(k1, k2, k3) * PL(k1) * PL(k2) * PL(k3)
R = schwingerReduce(I, midpoint=True, evaluateDescendants=True, path="schwinger.html")
R.ledger.projections[0]       # the axis projected out: A_s, the probes and their terms
```

* **Without a `G`** a product is an `FSum` like any other input, read in
  $\boldsymbol x$ and $\boldsymbol y$ or at the midpoint: `Fx(k1) * Fy(k2)` gives
  $\rho=(1,0)$, $\sigma=(0,1)$.
* **With `G`'s** it is an `AxialIntegrand` of rank the number of `G`'s (plus
  any `g`'s written out), and it carries the axis $z$. It is read at the
  midpoint only (`midpoint=True`; in $\boldsymbol x$, $\boldsymbol y$ it is refused by
  name). The $\hat z$'s come off and the tensor algebra projects them out, by
  the core's [peel and project](#the-axis-and-its-tensor-algebra-g-peel-project) (`SchwingerProjection`):
  $$\mathcal I=\hat z_{i_1}\cdots\hat z_{i_n}T_{i_1\dots i_n},\qquad
  \int\mathcal I=\sum_s\nu^sA_s,\qquad A_s=\sum_jC_{s,j}\,r^{-s_j}\int\tilde Q_j,\qquad \nu=\hat{\boldsymbol z}\cdot\hat{\boldsymbol r},$$
  with $C_{s,j}$ the Weingarten weights and
  $\tilde Q_j=\mathcal E\prod\boldsymbol v_a\cdot\boldsymbol v_b\prod\boldsymbol v_a\cdot\boldsymbol r$
  the probe $S'_j\cdot T$ with its $s_j$ factors $1/r$ taken out, since they do
  not depend on the momenta; $\mathcal E=\Phi\prod_a2\sin(\boldsymbol v_a\cdot\boldsymbol r/2)/v_a^2$.
  Only $\boldsymbol k\cdot\boldsymbol r$ and scalar products of momenta are left, no $z$.
  The products of every $\tilde Q_j$ are the ledger's terms, and the
  Schwinger pipeline runs on each.
* The page has a section per such input before the terms: the input as typed,
  then with every dressed kernel written out
  ($F_2(\boldsymbol k_1,\boldsymbol k_3)\,e^{i(\boldsymbol k_1+\boldsymbol k_3)\cdot\boldsymbol x}\cdots G_2(\dots)\,g(\dots)$),
  then with each $v_z$ written out; the peel and project cards of the tensor
  algebra; and $A_s$ in the $\tilde Q_j$, each $\tilde Q_j$ as its terms $T_t$.
* **Sums.** Terms with different `G`'s add up into an `AxialSum` (terms with
  the same $g$'s add into one), and each term is projected on its own, as
  its own input section of the page:
  ```python
  sigma_NLO_1 = 1/2 * Fx(-k1, k2) * G(-k2) * G(k1) * PL(k1) * PL(k2)
  sigma_NLO_2 = 1/2 * Fx(-k2) * G(k1) * G(-k1, k2) * PL(k1) * PL(k2)
  R = schwingerReduce(sigma_NLO_1 + sigma_NLO_2, midpoint=True, evaluateDescendants=True)
  ```
  This is the same as `schwingerReduce([sigma_NLO_1, sigma_NLO_2], midpoint=True)`.
  A term without a $g$ cannot join such a sum; put it beside them in a list.
  Every term of one ledger is integrated over the same momenta, so terms of
  different loop orders go in separate calls: a one-loop term in a two-loop
  ledger has no denominator in $k_2$ and is flagged as degenerate.
* The Feynman pipeline (`peel`, `feynmanReduce`) refuses the phases in
  $\boldsymbol x$ and $\boldsymbol y$; it averages over $\hat{\boldsymbol r}$, which they
  cannot go through. Its own `Fx` and `Fy` are written in $\boldsymbol r$.
* The tests check the projection pointwise in the momenta: $\sum_s\nu^sA_s/\mathcal E$,
  each $\tilde Q_j$ summed over its terms as the ledger reads them, is the
  average over $O(2)$ about $\hat{\boldsymbol r}$ of $\prod_a(R\boldsymbol v_a)\cdot\hat{\boldsymbol z}$
  (`tests/schwinger/test_dressed.py`).

#### The generators

| type | factor | operator on $Z$ |
|---|---|---|
| primary | $1/D_b^{\alpha_b}$ | $\mathcal P_b=\frac{1}{\Gamma(\alpha_b)}\int_0^\infty dz_b\,z_b^{\alpha_b-1}$; $z_b$ enters $A$ |
| quadratic | $(K^TBK)^m$ | $\big(-\sum_{i\le j}B_{ij}\partial_{a_{ij}}\big)^m$: $k_i^2\leftrightarrow-\partial_{a_{ii}}$, $k_i\cdot k_j\leftrightarrow-\frac12\partial_{a_{ij}}$ |
| linear | $(\boldsymbol q\cdot(a\boldsymbol x+b\boldsymbol y))^m$ | $\big(-i\sum_i q_i(a\,\partial_{\rho_i}+b\,\partial_{\sigma_i})\big)^m$ |
| shift | $\sin(\dots)$, $\cos(\dots)$ | $\mathcal S^{\sin}[\delta]f=\frac{1}{2i}(f\vert_{+\delta}-f\vert_{-\delta})$, $\mathcal S^{\cos}$ with $+$ and $\frac12$ |

$A$ is a generic symmetric matrix with independent $a_{ii}$, $a_{ij}$ ($i<j$),
$K^TAK=\sum_ia_{ii}k_i^2+2\sum_{i<j}a_{ij}k_i\cdot k_j$, and $B=cc^T$ for
$(c\cdot K)^2$, $B=\frac12(uv^T+vu^T)$ for $u\cdot v$. A shift moves $\rho$
and $\sigma$ by the coefficients of $\boldsymbol x$ and $\boldsymbol y$ in the
sine's argument: $\sin(\frac12(\boldsymbol x-\boldsymbol y)\cdot\boldsymbol k_2)$
is $\rho_2\to\rho_2\pm\frac12$, $\sigma_2\to\sigma_2\mp\frac12$.

#### (A, J) and Z

`getBraid(F, D)` builds $A(z)=\sum_{b\in\mathcal P}z_b\,c_bc_b^T$ and $J$, and
checks two things:

* $K^TA(z)K=\sum_bz_bD_b$, with the $D_b$ expanded by the algebra;
* that the $c_b$ span $\mathbb R^L$, by the exact rank of the integer matrix
  $C$ of the $c_b$. By Cauchy–Binet,
  $\det A(z)=\sum_{|S|=L}\det(C_S)^2\prod_{b\in S}z_b$, so this is the same as
  $\det A(z)\not\equiv0$.

A term that fails the second is **flagged**: some direction of $K$ has no
denominator, the Gaussian does not exist, and the term is a contact or
scaleless term. So is a term with no exponential and no sine, where $J=0$
leaves no scale. A flagged term goes no further and is listed with its reason.

`assemblePartitionFunction(B)` gives $\det A$ and $\operatorname{adj}A$ as
polynomials in the $z_b$. The exponent is

$$\frac{J^T(\operatorname{adj}A)J}{4\det A}=\frac{P_{xx}\,x^2+2P_{xy}\,\boldsymbol x\cdot\boldsymbol y+P_{yy}\,y^2}{4\det A},\qquad P_{xx}=\rho^T\operatorname{adj}A\,\rho,\ P_{xy}=\rho^T\operatorname{adj}A\,\sigma,\ P_{yy}=\sigma^T\operatorname{adj}A\,\sigma.$$

With quadratic descendants it also gives $\det A$ and $\operatorname{adj}A$
for the generic $A=(a_{ij})$, with the substitution $A\to A(z)$. Everything
that depends on the family alone is computed once and shared.

#### The Schwinger form

$$\mathcal I(T)=C\Big[\prod_{b\in\mathcal P}\mathcal P_b\Big]\Big[\prod\mathcal D\Big]Z(A,J)\Big|_{A=A(z),\ \rho=\rho^{(T)},\ \sigma=\sigma^{(T)}}.$$

Unevaluated, every generator stands as an operator and the evaluation point
is shown. With `evaluateDescendants=True` the descendants are evaluated in
this order:

1. **The derivatives, on the generic $Z$.** Every derivative of $Z$ is
   $F\cdot Z$, $F$ a polynomial in
   $$M_{uv}=u^TA^{-1}v,\qquad \boldsymbol w_u\cdot\boldsymbol w_v,\qquad \boldsymbol e\cdot\boldsymbol w_u,\qquad \boldsymbol e\cdot\boldsymbol e',\qquad \boldsymbol w_u=u^TA^{-1}J,$$
   for the momentum combinations $u,v$ and the $\boldsymbol x$, $\boldsymbol y$
   combinations $\boldsymbol e$ the descendants carry. The rules
   ($M=A^{-1}$) are:
   $$-\partial_BM_{st}=\tfrac12(M_{su}M_{vt}+M_{sv}M_{ut}),\quad -\partial_B\boldsymbol w_s=\tfrac12(M_{su}\boldsymbol w_v+M_{sv}\boldsymbol w_u),\quad -\partial_B\log Z=\tfrac32M_{uv}-\tfrac14\boldsymbol w_u\cdot\boldsymbol w_v,$$
   $$D_{q,\boldsymbol e}\boldsymbol w_s=M_{sq}\,\boldsymbol e,\qquad D_{q,\boldsymbol e}\log Z=-\tfrac12\,\boldsymbol e\cdot\boldsymbol w_q,$$
   with $D(FZ)=(DF+F\,D\log Z)Z$. So $k_i\cdot k_j$ gives
   $\big[\frac32(A^{-1})_{ij}-\frac14(A^{-1}J)_i\cdot(A^{-1}J)_j\big]Z$. In
   these quantities each descendant is one rank-one rule and $F$ stays small,
   where the same $F$ over the unit directions, or in the $z_b$, runs to
   thousands of terms. $F$ is cached per set of descendants.
2. **$A\to A(z)$:** $M_{uv}=u^T\operatorname{adj}A\,v/\det A$ and
   $\boldsymbol w_u=u^T\operatorname{adj}A\,J/\det A$.
3. **The shifts:** one branch per choice of signs, $J^{(s)}=(\rho^{(s)},\sigma^{(s)})$.
4. **$\rho$, $\sigma$ at the term's values.**
5. **Simplified:** branches with equal $J^{(s)}$ are merged, cancelled ones
   dropped, and the constants collected into
   $\kappa=C(-i)^{m}(2i)^{-\#\sin}2^{-\#\cos}$.

The result is an integrand in the $z_b$, with the primaries unevaluated:

$$\mathcal I(T)=\kappa\Big[\prod_b\mathcal P_b\Big](4\pi)^{-3L/2}(\det A)^{-3/2}\sum_s\varepsilon_s\,F\big|_{\boldsymbol w=\boldsymbol w^{(s)}}\,e^{-Q^{(s)}},\qquad Q^{(s)}=\frac{P^{(s)}_{xx}x^2+2P^{(s)}_{xy}\,\boldsymbol x\cdot\boldsymbol y+P^{(s)}_{yy}y^2}{4\det A}.$$

$M_{uv}$ and $\boldsymbol w_u$ are the covariance and the mean of the Gaussian
$Z$: $\langle k_u^ak_v^b\rangle_{\rm c}=\frac12M_{uv}\delta^{ab}$ and
$\langle\boldsymbol k_u\rangle=\frac i2\boldsymbol w_u$, with
$\boldsymbol k_u=u\cdot K$, so $F$ is Wick's theorem for the numerator.

The page writes $F$ once, then $\det A$ and every $M_{uv}$ of $F$ at $A(z)$,
$M_{uv}=0$ included, then for each branch its $J^{(s)}$, its $F^{(s)}$ and its
$P^{(s)}$'s. $F^{(s)}$ is $F$ with $\boldsymbol w^{(s)}$ put in: $M_{uv}$
stays a symbol, every $\boldsymbol w^{(s)}_u$ is written in the $z_b$, and a
term with an $M_{uv}$ or a $\boldsymbol w^{(s)}_u$ that vanishes is dropped,
so is a branch whose $F^{(s)}$ vanishes. Each term stays one product: a
polynomial of more than four terms, and a vector $U\boldsymbol x+V\boldsymbol y$
that is not a polynomial times a fixed direction, is named
$\omega^{(s)}_u$, $\boldsymbol\omega^{(s)}_u$ and written out once below.
When $F$ has more than 500 terms it is not written out per branch, which
would repeat it once for every branch: $F^{(s)}=F\big|_{\boldsymbol w=\boldsymbol w^{(s)}}$
with the $\boldsymbol w^{(s)}_u$ instead.

`writeUpTo` (on `schwingerReduce`, `getSchwingerForm`; 2000 by default) is
the most terms a polynomial is written out with: $F$, $\det A$, an $M_{uv}$,
a $P^{(s)}$. A longer one is written as its first 50 terms and
$\dots\;(N\text{ terms, the first 50 shown})$; the form keeps it whole
(`S.F`). Four loops with a $G_4$ give $F$ of hundreds of thousands of
terms, 200 bytes of LaTeX each, and written out they would make a page of
gigabytes that no browser opens. `writeUpTo=None` writes every term.

A branch with $J^{(s)}=0$, e.g. $\sin(\frac12\boldsymbol y\cdot\boldsymbol k)\,e^{\frac i2\boldsymbol y\cdot\boldsymbol k}$,
has no scale; it is kept and marked. `S.integrand()` gives everything in
sympy (symbols `z1`, `z12`, `zb12`, `z1m2m3`, ..., `xx`, `xy`, `yy`, `n`, or at the
midpoint `rr` for $r^2$), for checking small cases by hand; `S.branchF(b)`
is $F^{(s)}$ alone, and `S.explicitF(b)` the $F^{(s)}$ the page writes.

#### The assembled form

When it is short, every term is also written as one formula, the *Assembled*
card: $M_{uv}$ and $\boldsymbol w^{(s)}_u$ put in at $A(z)$, each branch's
$F^{(s)}$ over one power of $\det A$, and $\kappa$ and $\varepsilon_s$ folded
into one rational per branch,

$$\mathcal I(T)=i^{p}\int_0^\infty\prod_b dz_b\,\frac{z_b^{\alpha_b-1}}{\Gamma(\alpha_b)}\;(4\pi)^{-3L/2}(\det A)^{-3/2}\sum_sc_s\,\frac{N^{(s)}}{d^{(s)}}\,e^{-Q^{(s)}},$$

$N^{(s)}$ a polynomial in the $z_b$ and $r^2$ (or $x^2$, $\boldsymbol x\cdot\boldsymbol y$,
$y^2$) with coprime integer coefficients. When $\det A$ is a monomial, as
when every primary is a single $k_i^2$, the largest monomial dividing both
is cancelled, $d^{(s)}$ is a monomial in the $z_b$, and $Q^{(s)}$ is written
term by term; otherwise $d^{(s)}$ is a power of $\det A$, as low as divides.
For the midpoint term $4F_2(-\boldsymbol k_1,\boldsymbol k_2)\,k_1^{n-2}k_2^n\,(\boldsymbol y-\boldsymbol x)\cdot\boldsymbol k_1\cdots$,
the part with $\boldsymbol k_1\cdot\boldsymbol k_2/k_1^2$ is

$$\mathcal I(T_1)=\int_0^\infty dz_1\,dz_2\,\frac{z_1^{1-\frac n2}z_2^{-\frac n2-1}}{\Gamma(2-\frac n2)\Gamma(-\frac n2)}\,\pi^3(z_1z_2)^{-3/2}\Big[-\frac{r^2}{4z_1z_2}\,e^{-\frac{r^2}{4z_2}}+\frac{2z_1r^2-r^4}{8z_1^2z_2}\,e^{-\frac{r^2}{4}\left(\frac1{z_2}+\frac1{z_1}\right)}\Big].$$

`assembleUpTo` (on `schwingerReduce`, `getSchwingerForm`; 200 by default, 0
for never) is the most terms an $N^{(s)}$ may have; a numerator of more than
four terms is written below as $N^{(s)}$. A bound on the size of $N^{(s)}$,
taken before anything is expanded, rules out the long ones at once: for the
three-loop families with seven primaries $N^{(s)}$ runs to thousands of
terms, and those terms keep the evaluated card alone. `S.assembled()` is the
form or `None`, and `S.assembledIntegrand()` it in sympy.

#### The factorized form

A term **factorizes** when its family splits into blocks, or is a single
$z_b$: a one-loop term with one denominator is one integral already, the
trivial product. Only a family that is one block of several $z_b$ does not
factorize. By Cauchy–Binet,
$\det A(z)=\sum_{|S|=L}\det(C_S)^2\prod_{b\in S}z_b$ has degree at most one in
each $z_b$, so it factors only by splitting the $z_b$ into groups: the
*blocks*, groups of primaries whose $c_b$ span complementary subspaces. Then

$$\det A=\delta\prod_B\mathcal U_B,\qquad \frac{J^T\operatorname{adj}A\,J}{\det A}=\sum_B\frac{Q_B}{\mathcal U_B},\qquad \delta=\big(\gcd_S\det C_S\big)^2,$$

with $\mathcal U_B$ and $Q_B$ in the block's $z_b$ alone: in suitable momenta
$A$ is block diagonal, and $Z(A,J)$ is a product over the blocks. A linear
relation among the $c_b$ ties every primary in it into one block, so a block
of one $z_b$ ($\mathcal U_B=z_b$) is a primary in no relation. Every $z_b$ is
one when $\det A$ is a monomial, as for $F_2$, $G_2$ and $P_L$ alone. With
$1/(\boldsymbol k_2+\boldsymbol k_3)^2$ on top of $k_1^2,k_2^2,k_3^2$, as in
$F_3$, $\det A=z_1\,\mathcal U_2$ and
$\mathcal U_2=z_2z_3+z_2z_{23}+z_3z_{23}$: a one-loop factor and a two-loop
block. The blocks are found from the relations: a basis is picked among the
$c_b$, every other $c_e$ is a combination of it, and $e$ goes in one block with
the basis vectors that combination uses. The split is checked by multiplying
it out; `familyData(F).split` (or `S.Z.data.split`) has its `groups`, `U`,
`delta`.

The *det A and adj A* card of every term gives the check: one block of
several $z_b$ ($\det A$ does not factor, nor does the term), one block of one
$z_b$ (a single integral, factorized as it is), $L$ blocks of one $z_b$ each, or
$\det A=z_1\,\mathcal U_2$ with each $\mathcal U_B$ written out. The overview
says which terms factorize.

With `evaluateDescendants=True`, a term that factorizes and has an assembled
form also gets the *Factorized* card, the Schwinger integral as products of
integrals over the blocks, every constant in front:

$$\mathcal I(T)=\frac{c\,i^p\,X}{(4\pi)^{3L/2}\prod_b\Gamma(\alpha_b)}\sum_tc_tX_t\prod_B\int_0^\infty\prod_{b\in B}dz_b\,z_b^{e_{b}}\;N_{t,B}\,\mathcal U_B^{-3/2-k}\,e^{-Q_B/(4\,\mathcal U_B)}.$$

$i$, $(4\pi)^{-3L/2}$, the $\Gamma(\alpha_b)$, $\delta^{-3/2}$, the rationals and
$r^2$ (or $x^2$, $\boldsymbol x\cdot\boldsymbol y$, $y^2$) are outside every
integral: $X$, common to all products, in front of the sum, the rest $c_tX_t$
in front of each product. Each integral holds its block's $z_b$ and nothing
else:

* $N^{(s)}$ is written out in monomials over every block but one. The block
  of several $z_b$ whose polynomial gives the fewest products keeps it, as
  $N_{t,B}$, with its content in front. A block of one $z_b$ is a single power
  $z_b^{e_b}$ and its exponential, $\int_0^\infty dz\,z^{s-1}e^{-a/z}=a^s\Gamma(-s)$.
* Products equal up to their constant are merged, so branches with the same
  Gaussian add up, e.g. $J$ and $-J$ from a sine.
* A block whose integral is the same in every product stands once, in front
  of the sum.
* A numerator or exponent of more than four terms is named $N_m$ or
  $Q_{B,m}$, written once below.
* An integral without an exponential has no scale and is marked: it is
  homogeneous in its $z_b$. This is where the zero-lag pieces sit.

For the midpoint term of the assembled form above,

$$\mathcal I(T_1)=-\frac{\pi^3r^2}{8\,\Gamma(2-\frac n2)\Gamma(-\frac n2)}\Big(\int_0^\infty dz_2\,z_2^{-\frac n2-\frac72}e^{-\frac{r^2}{4z_2}}\Big)\Big[2\int_0^\infty dz_1\,z_1^{-\frac n2-\frac32}-2\int_0^\infty dz_1\,z_1^{-\frac n2-\frac32}e^{-\frac{r^2}{4z_1}}+r^2\int_0^\infty dz_1\,z_1^{-\frac n2-\frac52}e^{-\frac{r^2}{4z_1}}\Big],$$

the first $z_1$ integral without scale. `S.factorizes` says whether a term
factorizes, `S.factorized()` is the form or `None` (one block of several
$z_b$, or no assembled form), and `S.factorizedIntegrand()` it in sympy, every integrand
multiplied out.

#### The page

`schwingerReduce` writes the page with `render()`: an Overview section, then
for an input with `G`'s its own section (see [Dressed kernels: phases in x and y](#dressed-kernels-phases-in-x-and-y)),
then one section per term, *Term n*, with a card for each step, each behind its own
arrow.

The Overview opens with a summary, then **Factorization**: which terms
factorize over the blocks of their family and which do not, as lists of term
numbers ($T_1\dots T_8$ for a run), the flagged terms beside them, and then
every term on its own with its blocks, e.g. $\{z_1\},\{z_2\}$, and, for a term of
an input with `G`'s, the input and probe it came from. The same lists are
`R.factorizing` and `R.notFactorizing`, and `R.flagged`.

Each term's section has:

* the term, as typed, and at the midpoint also at $\boldsymbol x=-\boldsymbol r/2$, $\boldsymbol y=\boldsymbol r/2$;
* $\mathcal F(T)$ with its labels and values;
* $\mathcal G$, split into $\mathcal P$ and $\mathcal D$;
* $A(z)$ and $J$ with the checks;
* $\det A$, $\operatorname{adj}A$ and $Z$;
* the Schwinger form unevaluated, and evaluated with `evaluateDescendants=True`;
* with `evaluateDescendants=True`, the assembled form, when it is short (`assembleUpTo`);
* and then the factorized form, when the term factorizes.

Flagged terms have their own section, FLAGGED terms, with the reason. A ledger of more than
`termsPerPage` terms (500) is written as an index page at `path`, with links
to `path-0001.html`, ... and the flagged terms, and pages of `termsPerPage`
terms each, every term section complete.

Every display typesets in MathJax at any length. MathJax refuses a display
longer than 5 KB once a command in it expands as a string macro, and the
control space `\ ` is one. The pipeline writes `\;` instead, and writes
fractions as `{\textstyle\frac{p}{q}}`.

#### The final expression

With `evaluateDescendants=True`, every term that **fully factorizes** is
carried through to a closed form, `R.final` (`schwinger/final.py`). A term fully
factorizes when every block of its family is a single $z_b$; a one-loop term
does too. Its factorized form is then a sum of products of one-dimensional
integrals, each the **master integral**

$$\mathcal M(e;\,Q)=\int_0^\infty dz\;z^{e}\,e^{-Q/(4z)}=\Gamma(-1-e)\Big(\frac Q4\Big)^{1+e},$$

so

$$\mathcal I(T)=\frac{i^p\,c\,X}{(4\pi)^{3L/2}\prod_b\Gamma(\alpha_b)}\sum_t c_tX_t\prod_B\mathcal M(e_{t,B};\,Q_{t,B}).$$

* **The master is derived, not typed in.** sympy integrates
  $\int_0^\infty dz\,z^{a-1}e^{-c/z}$ for a symbol $a$ and $c>0$, once, and the
  branch where it converges ($\operatorname{Re}a<0$) is taken and continued
  analytically in $n$. `master(e, Q)` is that at $a=e+1$, $c=Q/4$.
* **Scaleless pieces are `const`.** A product with a block whose $Q$ is $0$
  has no scale and is not evaluated. Neither are the flagged terms (scaleless
  or contact). All of them are written as one $\text{const}$ in the result.
* **Only complete sums.** A term that does not fully factorize is not
  evaluated, and an input or total it belongs to is reported as not complete,
  with the terms that are missing. For an input with `G`'s, once all of its
  terms are evaluated or const,
  $\int\mathcal I=\text{const}+\sum_s\nu^sA_s$ with
  $A_s=\sum_jC_{s,j}\,r^{-s_j}\sum_{t\in j}\mathcal I(T_t)$.
* **Full simplification.** Every term and every $A_s$ goes through
  `fullSimplify()` (`fullsimplify.py`, in the core; see [fullSimplify](#fullsimplify-a-sum-of-gamma-functions-simplified)): Gammas shifted
  to one argument per class, terms with the same Gammas collected, Gauss's
  multiplication formula, linear factors absorbed, $z\,\Gamma(z)=\Gamma(z+1)$.
  Every step is an identity, and the reflection formula is never used. Each
  $Q=qP$ is written $(q/4)^aP^a$ first, so the powers of one $P$, say
  $|\boldsymbol x-\boldsymbol y|^2$, are collected as one base.
* At the midpoint $r^2$ is `r**2`, with `r` positive. In $\boldsymbol x$ and
  $\boldsymbol y$, $x^2$, $\boldsymbol x\cdot\boldsymbol y$ and $y^2$ are `x**2`, `xy`
  and `y**2`. $n$ is `Symbol("n")` (`granada.schwinger.final.n`, `.r`, `.nu`),
  and an index of its own, `PL(k, "n1")`, is `Symbol("n1")`.

```python
R = schwingerReduce(sigma_NLO_1 + sigma_NLO_2, midpoint=True, evaluateDescendants=True)
R.final.inputs[0].simplified   # {0: A_0, 2: A_2} of the first input, when it is complete
R.final.values[1].simplified   # one term, I(T_1), without its const
R.final.total                  # {s: A_s} over everything; None while a term is missing
R.final.totalExpr()            # const + sum_s nu^s A_s, in sympy
R.final.missing                # {term: why it is not evaluated}
```

Every one of these shows itself, alone or in a list, in a notebook too:
`render(R.final)` is the whole Result section, and
`render([R.final.inputs[0].simplified, R.final.totalExpr(), R.final.missing])` writes
each as rows. `.simplified` and `.total` stay dicts, `{power of nu: A_s}`, with
`.expr()` giving the sum in sympy.

The page opens with a **Result** section, after the Overview: the master as
sympy derived it, the total (or what keeps it from being complete), and each
input with `G`'s. Every evaluated term ends with a **Masters** card, its
factorized form as products of $\mathcal M$ and then simplified.

The tests check the master against quadrature, whole terms against the
Fourier transform
$\int\frac{d^3k}{(2\pi)^3}\,e^{i\boldsymbol k\cdot\boldsymbol x}(k^2)^{-a}=\frac{\pi^{3/2}2^{3-2a}}{(2\pi)^3}\frac{\Gamma(3/2-a)}{\Gamma(a)}|\boldsymbol x|^{2a-3}$
(one loop, two, and through $(\boldsymbol k_1+\boldsymbol k_2)^2$), every term against
the numerical integral of its whole integrand over the $z_b$, which comes
before the factorization and knows nothing of the masters, and the simplified
forms against the sums as they come (`tests/schwinger/test_final.py`).

#### Checks

* $K^TA(z)K=\sum_bz_bD_b$ and the rank, for every family.
* `check=True` (the default, with `evaluateDescendants=True`) compares each
  distinct set of derivatives with finite differences of $Z$ at a random
  point, once, at 30 digits. Mixed derivatives are taken by polarization, so
  a set of 7 costs about half a second.
* The tests check the expected results, with $\int=\int\frac{d^3k}{(2\pi)^3}$: $\int\frac{\boldsymbol y\cdot\boldsymbol k}{k^2}e^{i\boldsymbol x\cdot\boldsymbol k}=\frac{i}{4\pi}\frac{\boldsymbol x\cdot\boldsymbol y}{|x|^3}$,
  $\int\frac{\sin(\frac12\boldsymbol y\cdot\boldsymbol k)}{k^2}e^{i\boldsymbol x\cdot\boldsymbol k}=\frac{1}{8\pi i}\big(\frac{1}{|x+y/2|}-\frac{1}{|x-y/2|}\big)$
  (the $z$-integral done in the test), the two- and three-loop $\det A$ and
  $J^TA^{-1}J$, the quadratic descendant, exact-match cancellation and a
  degenerate term. They also compare the calculus with sympy
  differentiating the explicit generic $Z$.
* The $F^{(s)}$ the page writes is checked against $F$ at the branch, exactly,
  and the assembled form against `S.integrand()`, in both readings
  (`tests/schwinger/test_assembled.py`): diagonal and mixed families, $\det A$ a
  monomial with and without a coefficient, cosines, $i$ in $\kappa$, a branch
  without scale, no descendants, three loops.
* Every family's split $\det A=\delta\prod_B\mathcal U_B$ is multiplied out
  and compared, and every $Q^{(s)}=\delta\sum_BQ_B\prod_{B'\ne B}\mathcal U_{B'}$
  is put back together, each time. The tests compare the factorized form with
  the assembled form in both readings, and the blocks with sympy factoring
  $\det A$ for every family of a four-loop $G_4$ term
  (`tests/schwinger/test_factorized.py`).

#### Scale

A ledger of 12,000 three-loop terms with up to seven primaries, two sines and
seven derivatives reads in 4.5 s. It runs in about 50 s unevaluated, writing
25 files of about 6 MB each. With `evaluateDescendants=True` and the checks
it takes about 90 s, writing 25 files of up to 11 MB. Memory stays under
0.6 GB, and the terminal gets about 30 lines.

On four three-loop terms with seven primaries, two sines and two to seven
derivatives, writing $F^{(s)}$ per branch (and $\det A$, the $M_{uv}$) makes
the evaluated page 7% larger at the midpoint and 17% larger in $x$ and $y$;
the bound rules out the assembled form for all four before anything is
expanded.

#### Not detected

A scaleless sub-integral with $\det A\ne0$ is not flagged. For example,
$k_2$ only in $1/(k_1+k_2)^2$ with $J_2=0$ gives $\det A=z_1z_{12}$, but no
scale for $z_{12}$.

### Terminal logs

Every function you call says in the terminal when it starts, when it is done,
how big its input and output are, and how long it took. The long loops also
report progress, so a slow run shows where it is:

```
[granada 17:12:54] average(Projection(rank 4: nu^0: 10 channels, ...)) ...
[granada 17:12:54]   average: probe 1 of 10 (FSum, 1 pieces, 16 terms) ...
[granada 17:12:57]   average: probe 1 of 10 done in 2.5 s -> FSum, 22 pieces, 2685 terms
...
[granada 17:13:00]   average: nu^0: 10 channels collected into 4541 entries in 392 ms
[granada 17:13:00] average done in 6.0 s -> Ledger(nu^0: 4541 entries, ...)
[granada 17:13:00] render(4 item(s)) ...
[granada 17:13:00]   render: item 1 of 4 (I) ...
```

This covers `peel`, `project`, `average`, `feynmanReduce` (stage by stage),
`refAverage`, `reduce`, `masters`, `align`, `fold`, `relabel`, `render`,
`latex`, `labels`, `wl`, `getTower`, `refReduce` (step by step), `evalTower`,
`fullSimplify` and the Schwinger pipeline's entry points, `schwingerReduce`
above all. A call
made from inside another one is logged only at debug level, so you see the
calls you made. A `refAverage` that runs for more than five seconds without
a line also reports which piece it is on.

```python
from granada import verbose
verbose(False)      # silence
verbose(True)       # the default
verbose("debug")    # nested calls too
```

The logger is the standard `logging.getLogger("granada")`, writing to
stderr.

### Things that will not work, and why

**Odd powers of a compound magnitude never reduce.** `mag(k+p)` is a genuine
root; only even powers are polynomials in the atoms. `D_{k+p}^{1/2}` in the
output is a real master, not an unfinished reduction.

**A root or reciprocal of a dot product has no D-label.** `SP(k,p)**Fraction(1,2)`
and `1/SP(k,p)` survive expansion untouched, and `reduce()` says so by name.

**A root of a sum is not representable.** Write `mag(k+p)` and leave the
vector unexpanded.

**No irrational coefficients.** `(2*SP(k,k))**Fraction(1,2)` raises rather
than manufacture a `sqrt(2)`.

**No `n**2` and no `1/n`.** Exponents are linear in the spectral indices by
construction; `n1*n2` raises as `n**2` does. An `n`-dependent exponent is
never split into whole and fractional parts — the parity of `n` is not ours
to know.

**One Bessel per term.** `jprime(k)*jprime(p)` raises, as does a Bessel in a
denominator. A *sum* over distinct Bessels is fine — that is `TermSum`, and
each piece is shifted separately.

**Relabelling must be a permutation.** Sending both `k` and `p` to `k` merges
two integrations rather than renaming them, and `relabel` refuses.

**One pipeline's phases in the other's input.** `feynman.Fx` writes its
phase in $\boldsymbol r$ and `schwinger.Fx` in $\boldsymbol x$; the Feynman
pipeline refuses $e^{i\boldsymbol k\cdot\boldsymbol x}$ (it cannot average
it), and the Schwinger pipeline reads a phase in $\boldsymbol r$ only at the
midpoint. Build each pipeline's input with its own dressed kernels.

### Tests

```bash
pip install -e ".[test]"
python -m pytest                  # every suite
python -m pytest tests/core       # the kernels, spectral indices, fullSimplify
python -m pytest tests/feynman    # the Feynman pipeline, its stages 1 and 2, its tools, the renderer
python -m pytest tests/schwinger  # the Schwinger pipeline
```

`pyproject.toml` puts `src` and `tests` on the path, so the suites also run
from a checkout without installing. Each pipeline's suite tests that
pipeline alone: neither is checked against the other.


---

# API reference

Generated from the installed package: every public name with its signature and docstring. Classes list their public methods.

## `granada`

### class `granada.Lin(a=0, b=0)`

```text
A linear form a + b_1 n_1 + ... + b_m n_m in spectral indices, rational a and b_i.

    Lin(a, b)                       a + b n, n the spectral index
    Lin(a, {"n1": b1, "n2": b2})    a + b1 n1 + b2 n2

Each index is a name (_INDEX_NAME): n is the one PL(k) uses, and
PL(k1, "n1") * PL(k2, "n2") carries two that are independent of each
other. parts holds the (name, b) pairs with b != 0, sorted by name.

Exponents in this algebra are only ever added to one another or scaled
by a rational, and both operations preserve this shape, so the form is
closed under everything that can happen to it. Anything that would
manufacture n^2, n1 n2 or 1/n raises rather than silently degrading.

A form with no index left is collapsed back to a plain Fraction on the
way in, so a Lin living in a Monomial always carries genuine dependence on
an index — and is therefore never an integer power, which is what makes
expand() leave it alone.
```

Public methods and properties:

- `b`: The coefficient of n, for a form in n alone: a + b n.
- `coeff(self, name='n')`: The coefficient of the index name, 0 if the form does not depend on it.
- `indices`: The names of the indices the form depends on, sorted.
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().

### class `granada.Monomial(powers=None)`

```text
A product of scalar products with rational exponents.

The empty monomial is the constant 1, which is what lets an Expr carry
a plain number as a term.
```

Public methods and properties:

- `degree`
- `exponents(self, basis)`: Exponent tuple over an ordered basis of squared vectors.
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `powers`
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().

### class `granada.SP(v1, v2)`

```text
Scalar product of two vectors, kept unexpanded.
```

Public methods and properties:

- `atomize(self)`: Canonical form: bilinear expansion into SPs of atoms only.
- `expand(self, basis=None)`: Rewrite into squares of atoms and of atom pairs.
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().
- `squares(self)`: The vectors appearing squared, or None if this is a dot product.

### class `granada.Expr(data=None)`

```text
A rational-power polynomial in scalar products.

Terms are collected on construction and zero coefficients dropped. Keys
may be given as SPs for convenience; they are coerced to Monomials.
```

Public methods and properties:

- `atomize(self)`: Expand every integer-power factor bilinearly into SPs of atoms.
- `by_exponents(self, basis=None)`: Collect into {exponent tuple: coefficient} over an ordered basis.
- `degree`
- `expand(self, basis=None)`: Rewrite into squares of atoms and of atom pairs.
- `items(self)`
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().
- `same_form(self, other)`: Structural equality: written the same way, not merely equal.
- `split_ref(self)`: {power of r: Expr free of ref}, the coefficient sorted by r.
- `squares(self)`: The distinct vectors appearing squared, or None if any factor is a genuine dot product.

### class `granada.External(name)`

```text
An external position vector, x or y: never integrated over.

The Schwinger pipeline reads sum_i k_i . (rho_i x + sigma_i y) in a cexp,
and tells the momenta k_i from x and y by this type. x and y are kept
apart throughout; a combination such as x - y is written and shown as
it is. Identity is by name, as for every Vector, so a momentum must not
be called x or y.
```

### class `granada.Vector(name)`

```text
A named 3D vector. No components — the name is the whole identity.
```

Public methods and properties:

- `atoms`: Mapping of atom -> integer multiplicity. An atom is itself, once.
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().

### class `granada.VectorSum(atoms)`

```text
An integer linear combination of vectors, kept unexpanded.
```

Public methods and properties:

- `atoms`: Mapping of atom -> integer multiplicity. An atom is itself, once.

### `granada.mag(v)`

```text
The magnitude |v|, i.e. SP(v, v) raised to the power one half.
```

### `granada.ref`

Constant: `r`

### class `granada.SphBessel(v, ell, scale=1)`

```text
j_ell(s |v| r), an opaque function of one magnitude. r is a scalar.

s is a positive rational scale, 1 unless given. It is there because an
average over ref can produce j_ell(|k| r / 2), and |k/2| written as a
vector would be a new propagator rather than half of an old one.

The order is a non-negative Python int and has no default. Defaulting it
would let a call site that meant one order silently mean another, and the
failure would only surface on the Mathematica side as an M that matches no
definition and quietly never evaluates.
```

Public methods and properties:

- `is_atomic`: True when the argument depends on a single vector.
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().
- `subs(self, mapping)`
- `with_vector(self, u)`: The same order on a new argument.

### class `granada.Term(coeff=1, bessel=None)`

```text
An Expr coefficient times at most one Bessel factor.
```

Public methods and properties:

- `atomize(self)`
- `by_exponents(self, basis=None)`
- `expand(self)`
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().
- `shift(self, frozen=(), prefer=None)`: Change integration variables so the Bessel argument is one vector.
- `squares(self)`

### class `granada.TermSum(terms=())`

```text
A sum of Terms, at most one per distinct Bessel factor.

An integrand is rarely a single Bessel structure: the angular reduction
leaves j_ell(|k|r) and j_ell(|k+p|r) side by side, each with its own
coefficient. They cannot be added, because they are different functions,
and they should not be forced apart by hand, because the whole point of
a driver is that the caller writes the integrand as it stands.

The pieces are kept in a dict keyed by Bessel — None included, for the
Bessel-free part — and the key is the argument together with the order,
so j_0(|k|r) and j_2(|k|r) stay apart while two copies of either collect
on the way in. Like structures collect on the way in and each
piece can later be shifted on its own. Collecting on the way in is what
makes the whole thing worthwhile: two pieces that started with different
arguments may end up sharing one after their shifts, and then they merge
into a single coefficient. That is legitimate for the same reason the
shift is — under the integral the variable is dummy — and it is the
point of doing the shift at all.
```

Public methods and properties:

- `atomize(self)`
- `by_exponents(self, basis=None)`: {Bessel: {exponent tuple: coefficient}}, over a shared basis.
- `expand(self)`
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().
- `shift(self, frozen=(), prefer=None)`: Shift each piece separately — one change of variables per Bessel.
- `squares(self)`: Union of the squared vectors across the pieces, or None.
- `terms`: The pieces, as Terms. Bessel-free first, then by argument, order.

### `granada.j(v, ell, scale=1)`

```text
The factor j_ell(scale |v| r).
```

### `granada.jprime(v)`

```text
j_0'(|v| r), written in the j_ell basis: j_0' = -j_1.

Kept so integrands typed against the old convention still run. It returns
a Term rather than a Bessel, because the identity carries a sign, and that
sign is written here and nowhere else.
```

### `granada.subs(e, mapping)`

```text
Apply a linear change of variables to an Expr.

Exponents are untouched, so Lin rides through unchanged. Two distinct
factors may collide onto one after substitution, so exponents are
accumulated rather than assigned.
```

### `granada.N`

Constant: `n`

### `granada.F2(v1, v2)`

```text
The second-order density kernel, unexpanded.

    F2 = 5/7 + (k1.k2)/(2 k1 k2) (k1/k2 + k2/k1) + 2/7 (k1.k2)^2/(k1^2 k2^2)

The middle term is (k1.k2)/2 (1/k2^2 + 1/k1^2), which is how it is
written here, as in G2: no odd powers of a magnitude appear.
```

### `granada.G2(v1, v2)`

```text
The second-order velocity divergence kernel, unexpanded.

G2 = 3/7 + (k1.k2)/2 (1/k1^2 + 1/k2^2) + 4/7 (k1.k2)^2/(k1^2 k2^2)
```

### `granada.F3(v1, v2, v3)`

```text
The third-order density kernel, symmetrised, unexpanded.

The standard recursion at n = 3 (_kernels),

    F3 = 1/18 [ 7 alpha(k1, k23) F2(k2, k3) + 2 beta(k1, k23) G2(k2, k3)
              + G2(k1, k2) (7 alpha(k12, k3) + 2 beta(k12, k3)) ]

averaged over the orderings of its arguments, with k12 = k1 + k2 and
k23 = k2 + k3. The compound squares (k1+k2)^2, (k2+k3)^2, (k1+k3)^2 that
the recursion brings in are kept as they are.
```

### `granada.G3(v1, v2, v3)`

```text
The third-order velocity divergence kernel, symmetrised, unexpanded.

The standard recursion at n = 3 (_kernels),

    G3 = 1/18 [ 3 alpha(k1, k23) F2(k2, k3) + 6 beta(k1, k23) G2(k2, k3)
              + G2(k1, k2) (3 alpha(k12, k3) + 6 beta(k12, k3)) ]

averaged over the orderings of its arguments, as F3.
```

### `granada.F4(v1, v2, v3, v4)`

```text
The fourth-order density kernel, symmetrised, unexpanded.

The standard recursion at n = 4 (_kernels), from F2, G2, F3 and G3,

    F4 = 1/33 sum_m G_m(q_1..q_m) [9 alpha(k_1, k_2) F_{4-m} + 2 beta(k_1, k_2) G_{4-m}],

averaged over the orderings of its arguments. The compound squares of
every pair and triple of arguments are kept as they are.
```

### `granada.G4(v1, v2, v3, v4)`

```text
The fourth-order velocity divergence kernel, symmetrised, unexpanded.

The standard recursion at n = 4 (_kernels),

    G4 = 1/33 sum_m G_m(q_1..q_m) [3 alpha(k_1, k_2) F_{4-m} + 8 beta(k_1, k_2) G_{4-m}],

averaged over the orderings of its arguments, as F4.
```

### `granada.PL(v, n=None)`

```text
The linear matter power spectrum P_L(k) = k^n, amplitude omitted.

k is the magnitude of v, so this is (v^2) raised to the power n/2.

    PL(k)                  k^n, n the spectral index N
    PL(k1, "n1")           k1^(n1): a power spectrum with an index of its own
    PL(k, N - 1)           any exponent linear in indices (a Lin)
    PL(k, -2)              a number: int or Fraction, not a float

n is a name (spectralIndex), a Lin or a rational. Each name is an index
independent of every other, so PL(k1, "n1") * PL(k2, "n2") carries two.
The amplitude A of P_L = A k^n is a constant and comes out of every
integral as it is.
```

### `granada.FKernel(*momenta)`

```text
The density kernel F_n(k_1, ..., k_n), symmetrised, unexpanded.

The order n is the number of momenta: FKernel(k) is F_1 = 1,
FKernel(k1, k2) is F2(k1, k2), FKernel(k1, k2, k3) is F_3, and so on,
by the standard recursion (_kernels).
```

### `granada.GKernel(*momenta)`

```text
The velocity divergence kernel G_n(k_1, ..., k_n), symmetrised, unexpanded.

The order n is the number of momenta: GKernel(k) is G_1 = 1,
GKernel(k1, k2) is G2(k1, k2), GKernel(k1, k2, k3) is G_3, and so on,
by the standard recursion (_kernels).
```

### `granada.spectralIndex(name='n')`

```text
The spectral index of that name, as an exponent: n (= N), n1, n2, n_s, m, ...

A name is n or m, or either with a subscript, digits (n1) or after an
underscore (n_s). Two indices of different names are independent:
PL(k1, "n1") * PL(k2, "n2") is k1^(n1) k2^(n2).
```

### `granada.as_term(obj)`

```text
Whatever was written, as a Term.

Python has already done the parsing: an arithmetic expression built from
these types evaluates to one object, and every such object is either a
Term or something a Term can carry. The job here is only to name which.
```

### `granada.is_reduced(obj)`

```text
True when obj is already in D-form: atomic Bessels, squares only.
```

### `granada.masters(obj, basis=None, frozen=(), prefer=None)`

```text
The master-integral map of a raw expression: {exponent tuple: coeff}.

reduce() followed by by_exponents(), for when the labels are wanted as
data rather than as typeset output.

Powers of r have no D label unless ref is in basis. For an expression
with an imaginary part, call this on .re and .im separately.
```

### `granada.reduce(obj, frozen=(), prefer=None, check=True)`

```text
Expand, shift if a Bessel demands it, expand again.

    Q = 1/ks * 1/ps * 1/kps * SP(k, p) * G2(k, p) * PL(k) * PL(p) * j(k, 2)
    render(reduce(Q), by_exponents=True)

frozen names the vectors that may not be shifted — the external momenta.
Pass them whenever the Bessel argument is compound, or the choice of
integration variable to eliminate is made alphabetically and may well
land on an external leg. prefer names one to eliminate if it is eligible.

A list is reduced elementwise, and (label, object) pairs keep their
labels, so the result drops straight into render().
```

### `granada.align(obj, target)`

```text
Put every piece's Bessel on the same vector, then add them up.

Pieces of a TermSum that differ only in which dummy carries the Bessel
are the same master family written two ways. Transposing the names maps
one onto the other, after which the terms share a Bessel factor and can
simply be summed — one coefficient list instead of several blocks.

Only pieces of the same order merge. Transposing names moves j_2(|p|r)
onto j_2(|k|r), but it cannot turn it into j_0(|k|r) — those are two
functions, not two spellings — so a sum over several orders stays a
TermSum with one piece per order, which is what the exporter wants.

Returns a Term when everything lands on target at a single order, and a
TermSum otherwise (several orders, or a piece whose Bessel argument
involves target already and so cannot be transposed onto it).
```

### `granada.diagnose(obj, flip, basis)`

```text
Print why a reduction is not landing on basis. Returns nothing.

A TermSum is reported piece by piece, since each has its own Bessel and
the fold applies to each separately.
```

### `granada.fold(obj, flip, basis)`

```text
Reflect whichever monomials the symmetry moves into the basis.

A monomial is replaced by its mirror image when that strictly reduces
the number of factors lying outside basis, and left alone otherwise, so
the operation is idempotent and never makes things worse.

A monomial carrying both halves of a mirror pair — (k+p)^2 and (k-p)^2
at once — is fixed by neither orientation. That term genuinely needs
four propagators and belongs to a different family; it is left as it is,
and the arity check in the exporter will name it.
```

### `granada.relabel(obj, mapping)`

```text
Rename integration variables. Only a permutation is allowed.

Renaming is free because the variables are dummy, but only if the map
is a bijection on atoms: sending both k and p to k would collapse two
independent integrations into one, which is not a change of variables
at all. The Jacobian of a permutation is one, so nothing else changes.

The expression must be expanded — a permutation is linear, so it acts
on squares by renaming alone, and there is no sign to track.
```

### `granada.stranded(obj, flip, basis)`

```text
The monomials that no reflection can move into basis.

A monomial escapes the family under fold() unless it carries both halves
of a mirror pair at once, in which case reflecting swaps them and leaves
it just as far outside. Those are the only genuine four-propagator terms;
everything else the fold handles.

Returns a list of (coefficient, monomial, offending factors).
```

### `granada.latex(obj, basis=None, by_exponents=False, symbol='D', numbered=False, dropScaleless=False)`

```text
LaTeX string for a Vector, SP, Monomial, Expr, Lin, Term, TermSum or FSum.

basis=None, by_exponents=False   vector notation
otherwise                        D-notation, ordered by the basis

dropScaleless=True leaves out every piece without a j_ell (and without a
sin, cos or cexp still to be averaged) — the ones proportional to 1.
```

### `granada.render(items, by_exponents=False, basis=None, symbol='D', numbered=False, legend=False, path=None, open_browser=False, dropScaleless=False, _frame=None)`

```text
Display one or more expressions, each under the name of its variable.

    render(e)                          vector notation
    render(e, by_exponents=True)       D-notation
    render([I, T, P, L])               input, steps, output: one block each
    render([("before", a), ("after", b)])

Anything renders: the algebra's types, the stage objects of both
pipelines and their fields, sympy numbers and matrices, plain numbers, and strings
(taken as LaTeX). Each item is labelled with the name of the variable
that holds it where render() was called; an item written inline has no
name and gets no label, and a ("label", obj) pair keeps its own label.
The stage objects are always shown in their own notation.

A shared basis is derived from all the items together, so the same
symbol means the same thing across every line. In a notebook this
returns a typeset object; otherwise it writes an HTML page and opens
it. Passing path= forces the file route either way.

dropScaleless=True leaves out, on every line, the pieces without a j_ell
(and without a sin, cos or cexp still to be averaged), and shows what it
left out of each line right after it (_leftOut), or that there were no
scaleless terms to leave out.
```

### `granada.juxtapose(a, b, /, *, by_exponents=False, basis=None, symbol='D', numbered=False, legend=False, path=None, open_browser=False, dropScaleless=False)`

```text
Display two results side by side, each under the name of its variable.

    juxtapose(A, B)                                A on the left, B on the right
    juxtapose(V, S.final, path="both.html")        one result of each pipeline
    juxtapose(("Feynman", V), ("Schwinger", S.final))

It takes exactly two results, positionally. Each is shown as render()
shows one item: anything render() takes, labelled with what was typed for
it in the call (or the name of its variable), or a ("label", obj) pair
with its own label. A plain list is not one result, and is refused: put
several items in sequence with render().

The keywords are render()'s. A shared basis is derived from both results,
and legend=True shows its definitions above them. With dropScaleless=True
what was left out of each side is shown under it, or that it had no
scaleless terms. On a page the two
results are two cards side by side, one above the other again on a narrow
screen; in a notebook they are the two columns of one display. This
returns what render() returns: a typeset object in a notebook, otherwise
the path of the page written (out.html, or path=).
```

### `granada.set_tex(name, vector_form, magnitude_form=None)`

```text
Register custom LaTeX for an atom, e.g.

set_tex("kp", r"\boldsymbol{k}'", "k'")
```

### class `granada.Labels(basis, bessel, terms, rpower=0, imaginary=False, denominator=True)`

```text
A reduction reduced to data: a basis, a Bessel, and labelled rationals.

terms is a list of (coefficient, label), where label is the tuple of D
exponents *as they appear in M*, i.e. already negated. The order is not
in the label — it is carried on bessel, one for the whole block.

rpower and imaginary are the block's prefactor, i^imaginary r^rpower,
shared by every row in the same way the Bessel is. r is not integrated
over, so its powers are never a D label; and keeping both out of the
rows keeps every coefficient rational. They are 0 and False unless the
expression came out of refAverage.
```

Public methods and properties:

- `ell`
- `latex(self)`: The block as LaTeX: the legend, then prefactor * sum c M_ell(labels; s r).
- `render(self, path=None, openBrowser=False)`

### `granada.from_mapping(mapping, basis, bessel=None, denominator=True, rpower=0, imaginary=False)`

```text
Labels from a plain {D exponent tuple: coefficient} dict.

by_exponents() and reduction.masters() return the exponents but not the
basis they were taken against, so it has to be supplied here. Passing
the wrong one is undetectable — prefer handing the Term itself to wl().

bessel takes a SphBessel, not a vector: M is order-first, so a block
without one cannot be emitted at all. It may be left out only if the
Labels is never exported. rpower and imaginary set the block prefactor
i^imaginary r^rpower, as labels() does for an averaged expression.
```

### `granada.getTower(obj, path='masters.m', **kw)`

```text
Write the master tower to a file and return the path.

The tower is the whole ladder of M(ell; alpha, beta, gamma; r) a single
integrand reduces to, each rung a rational coefficient against one label.
Read it back with Get["..."] once M is defined.
```

### `granada.labels(obj, basis=None, denominator=True, propagators=3)`

```text
The master labels and rational coefficients of one reduced Term.

basis fixes which vector is D_1, D_2, ... If it is omitted the one the
expression suggests is used, with the Bessel's vector promoted to the
front. Pass it explicitly whenever the Mathematica side has a fixed
convention — this is the joint where the two halves can silently
disagree.

denominator=False turns off the sign flip, for a Mathematica function
that takes the exponents as written rather than as denominator powers.

propagators is how many D labels the Mathematica side expects — three,
for M(ell; alpha, beta, gamma; r). It counts D labels only: the order is
not a propagator and never enters the label tuple, so this check is
unaffected by it. A basis of any other size means the
reduction has not landed on that family, and emitting it anyway
produces an M of the wrong arity: legal input that matches no
definition and simply never evaluates. Pass None to skip the check.
```

### `granada.wl(obj, basis=None, name='granada', head='M', r='r', n='n', denominator=True, propagators=3, dropScaleless=False, _frame=None)`

```text
WL source for a reduction: lists of {coefficient, {exponents}}.

Data, not code — a bare list is the one thing every version of every
front end reads the same way. The trailing line assembles it under
head, which is where the closed form gets attached.

A TermSum becomes one block per Bessel structure — one per (argument,
order) pair, since each has its own D_1 and therefore its own basis, plus
a final line adding them. Nothing is shared between blocks except the
name.

Several expressions at once — a list [A1, A2], or a dict {"A1": A1} —
give one file in which each is defined on its own, under its own name,
with nothing summed across them. In a list, each name is that of the
variable holding the expression where wl() or getTower() was called, so
getTower([A1tower, A2tower]) defines A1tower and A2tower. An entry
("label", expr) names itself; so does every key of a dict. A name that
cannot be told — an expression written inline, or one held by two
variables — is refused rather than guessed. Names are made into WL
symbols (A1_tower -> A1Tower); name= is then unused.

M is order-first and so takes one more argument than the D labels alone.
A definition of the old arity will not error on the calls emitted here:
it returns them unevaluated and the sum quietly stays symbolic. The first
header line records which convention the file was written against, so the
file itself says what it expects.

dropScaleless=True leaves out the pieces without a j_ell, which are not
M integrals and would otherwise be refused. The file says how many went.
```

### class `granada.FSum(data=None)`

```text
A sum of coeff * i^ipow * (functions) * (Bessel), keyed by all but coeff.

Keys are (ipow, funcs, bessel): ipow is 0 or 1, funcs a sorted tuple
(repeats allowed, for powers), bessel a SphBessel or None.
```

Public methods and properties:

- `im`: The imaginary part as a TermSum.
- `items(self)`: (ipow, funcs, bessel, coeff) per piece, in a fixed order.
- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `re`: The real part as a TermSum, for reduce(), render() and friends.
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().

### class `granada.Func(kind, arg)`

```text
One opaque factor sin(x), cos(x) or cexp(x) = exp(i x).

Identity is mathematical in the argument, through Expr's own equality,
so cexp(SP(k+p, ref)) and cexp(SP(k, ref) + SP(p, ref)) are one factor.
```

Public methods and properties:

- `latex(self, **kw)`: The LaTeX source; keywords as for granada.latex().
- `render(self, path=None, openBrowser=False, **kw)`: A page (or, in a notebook, a typeset object); keywords as for render().

### `granada.I`

Constant: `I * (1*1)`

### `granada.cexp(x)`

```text
exp(i x).
```

### `granada.cos(x)`

_No docstring._

### `granada.sin(x)`

_No docstring._

### `granada.refAverage(obj)`

```text
The average over the direction of ref, by the identity in this module.

    refAverage(SP(k, ref) * cexp(SP(k, ref)))   ->   I * |k| r j_1(|k| r)

Accepts anything that lifts to an FSum and returns an FSum. Once no
function factors remain, .re and .im give TermSums for reduce().
```

### `granada.refReduce(expr, family, flip, *, frozen=(), prefer=None, symbol='D', dropScaleless=False, cleanInput=False, path=None, open_browser=False)`

```text
Average over ref, reduce, align, fold — and render every stage.

    T = refReduce(B, family=[k1, k2, k1 + k2], flip=k1)
    getTower(T, "run.m", basis=[k1, k2, k1 + k2], dropScaleless=True)

family   the propagator basis [D_1, D_2, D_3], as for fold() and
         getTower(). The Bessel is aligned onto family[0].
flip     the vector reflected by fold(), as in fold(obj, flip, family).
frozen, prefer   passed to reduce().

The rendered page has one line per stage — the input, then the result
of each step in vector notation — and finally the result once more in
D-notation against family, numbered and with a legend. dropScaleless
leaves out, on every line and in the returned result, the pieces without
a j_ell — so what comes back is what the page shows, and getTower()
accepts it without being told again. What it left out of the result is
shown last, in the same D-notation, or that there were no scaleless
terms. cleanInput=True
shows the input line exactly as it was typed — F2(k1, k2), P_L(k1),
sums and products as written — instead of the evaluated, expanded
form; it changes nothing but that line. path and open_browser are as
for render().

Returns the final expression, ready for getTower(); with dropScaleless,
without its scaleless pieces.
```

### `granada.g(v)`

```text
g(v) = 2 v_z / v^2 sin(v.r / 2) for a Vector v (an atom or a combination).
```

### class `granada.GString(momenta=())`

```text
A product g(v_1) g(v_2) ... g(v_n), with g(v) = 2 v_z / v^2 sin(v.r / 2).

Build it with g() and *: g(k) * g(p) * g(k + p), or g(k)**2. The product
commutes, so equality ignores the order of the factors. A GString has no
Phi, so it is not an AxialIntegrand: multiply it by one, 1 * g(k) for
Phi = 1, before peel().
```

Public methods and properties:

- `compact(self)`: g(k) g(p)^2, as LaTeX.
- `latex(self)`: The product written out: 2 k_z / k^2 sin(k.r/2) ...

### class `granada.AxialIntegrand(envelopeScalar, gstring)`

```text
Phi * g(v_1) ... g(v_n): the single term an input with g's is made of.

envelopeScalar   Phi, an Expr (kernels, P_L, scalar products), or an FSum
                 once it carries phases or i (see _phi)
gstring          the GString
rank             n, the axial rank

Built by multiplication: G2(k, p) * PL(k) * g(k) * g(p), with a phase,
F2(-k1, k3) * cexp(SP(k3 - k1, ref) / 2) * g(k1), or with the dressed
kernels of either pipeline, Fx(k, q) * G(k, p) * PL(k).
```

Public methods and properties:

- `phiTex(self, opened=True)`: Phi as it was typed, kernels as calls; empty for Phi = 1.
- `rank`

### class `granada.AxialSum(terms)`

```text
I_1 + I_2 + ...: terms with different g's, each run through a pipeline on its own.

terms   [AxialIntegrand], one per g content: terms with the same g's are
        added into one, as for AxialIntegrand

Built by adding AxialIntegrands whose g's differ, as the diagrams of one
observable: Fx(k1, k2) * G(-k1) * G(-k2) * P + Fy(-k1, k2) * G(k1) * G(-k2) * P.
feynmanReduce() runs the Feynman pipeline on each term and adds the
results, power by power of nu, into one LedgerSum;
schwingerReduce(..., midpoint=True) projects each term on its own. The
stages one at a time (peel, ...) take one term, .terms[i].
```

### class `granada.AxialTensor(integrand)`

```text
zhat_{i_1} ... zhat_{i_n} T_{i_1 ... i_n}, T = E v_{1 i_1} ... v_{n i_n}.

legs       the vectors v_a, in the order of the g's
envelope   E = Phi prod_a 2 sin(v_a.r / 2) / v_a^2, an FSum
rank       n
indices    the free index names, i, j, l, ...
integrand  the AxialIntegrand it was peeled from
```

Public methods and properties:

- `T(self)`: T with its free indices, T_{ij}.
- `components(self)`
- `envelopeTex(self)`: E written out: Phi as typed times 2^n sin ... / v^2 ...
- `zhats(self)`

### class `granada.Bracket(structure)`

```text
One delta/rhat structure S of the Ansatz, wrapping granada.decompose.Structure.

structure   the Structure: pairs carry a delta, singles an rhat
nuPower     s(S), its number of rhat slots: zhat ... zhat . S = nu^s(S)
```

Public methods and properties:

- `label(self)`: The contraction S.T in the notation of granada.decompose, T_{a a rhat}.
- `nuPower`
- `rank`
- `tex(self, indices=None)`

### class `granada.Channel(weight, probe, brackets=(), legs=())`

```text
One term C * int Q of an A_s.

weight    C, a sympy Rational: the Weingarten weights summed over the
          brackets of this power of nu and over the S' sharing the probe
probe     Q = S'.T, a scalar FSum: E prod v_a.v_b prod (v_a.r)/r
brackets  the S' whose contraction is this probe (several when legs repeat)
legs      the legs of T, to write the contraction out
```

Public methods and properties:

- `contractionTex(self)`: S'.T / E written out: (v_a . v_b) per delta, (v_a . rhat) per rhat.
- `label(self)`
- `labels(self)`

### class `granada.Projection(tensor)`

```text
int T = sum_S c_S S, regrouped by the power of nu.

tensor     the AxialTensor
brackets   the Brackets S, ordered as in granada.decompose
gram       the Gram matrix G[S', S] = S'.S, a sympy Matrix (d = 3)
weights    the Weingarten weights W, a sympy Matrix: c_S = sum_S' W[S, S'] int S'.T
channels   {nu power s: [Channel]}, int I = sum_s nu^s sum C int Q
singular   True when the brackets are dependent in d = 3 (rank 6 on) and
           W is the pseudo-inverse
```

Public methods and properties:

- `coefficientsTex(self)`: Every c_S as Weingarten weights times contractions of T, as granada.decompose writes it.
- `matrixTex(self, which='weights')`: G or W as a table, rows and columns labelled by the brackets.

### `granada.peel(integrand)`

```text
Stage 1: Phi g(v_1) ... g(v_n) = zhat_{i_1} ... zhat_{i_n} T_{i_1 ... i_n}.

    peel(G2(k, p) * g(k) * g(p))      # zhat_i zhat_j T_ij,  T_ij = E k_i p_j

Takes an AxialIntegrand only. A bare GString is refused, not wrapped:
write 1 * g(k) * g(p) for Phi = 1. So is one whose Phi carries the phase
of a Schwinger dressed kernel, e^{i k.x} or e^{i k.y}: that is for the
Schwinger pipeline at the midpoint, schwingerReduce(I, midpoint=True). A
phase in r (feynman.Fx, feynman.Fy, cexp(SP(k, ref) / 2)) is peeled.
```

### `granada.project(tensor)`

```text
Stage 2: int T = sum_S c_S S, and int I = sum_s nu^s A_s.

Takes an AxialTensor only. Each A_s is a list of Channels C * int Q, with
the probes Q scalar FSums and the weights C rationals; channels with
equal probes are merged and zero weights dropped.
```

### `granada.fullSimplify(expr, n=None)`

```text
expr, a sum of Gamma functions of arguments linear in spectral indices, as short as it goes.

See the module docstring for the four steps. Every step is an identity,
so the result equals expr wherever both are defined. The indices are
every symbol of expr named like one (n, n1, n_s, m, ...; isIndex), n
first; n given is put first whatever its name, and a list of symbols is
taken as the indices exactly.
```

### `granada.verbose(on=True)`

```text
Turn the terminal logs on (True), off (False), or to "debug" (nested calls too).
```

## `granada.feynman`

### `granada.feynman.Fx(*momenta)`

```text
F^x(k_1, ..., k_n) = F_n(k_1, ..., k_n) e^{-i (k_1 + ... + k_n).r/2}, an FSum.
```

### `granada.feynman.Fy(*momenta)`

```text
F^y(k_1, ..., k_n) = F_n(k_1, ..., k_n) e^{i (k_1 + ... + k_n).r/2}, an FSum.
```

### `granada.feynman.G(*momenta)`

```text
G(k_1, ..., k_n) = G_n(k_1, ..., k_n) g(k_1 + ... + k_n), an AxialIntegrand of rank one.
```

### `granada.feynman.peel`

Same object as `granada.peel`.

### `granada.feynman.project`

Same object as `granada.project`.

### `granada.feynman.average(projection)`

```text
Stage 3: every probe averaged over the direction of rhat (refAverage).

Takes a Projection only, and hands refAverage each Channel.probe, never
anything tensorial. Entries with equal integrands are merged, zeros
dropped.
```

### `granada.feynman.feynmanReduce(expr, *, upTo='average', path=None, openBrowser=False)`

```text
Run the Feynman pipeline on one AxialIntegrand and render every stage.

    L = feynmanReduce(G2(k, p) * PL(k) * PL(p) * g(k) * g(p) * g(k + p))

upTo     the last stage to run: "peel", "project" or "average"
path, openBrowser   as for render(): the one page with a block per stage

Returns the object the last stage produced (AxialTensor, Projection or
Ledger). A failing stage is named in the error.

expr may be a sum of terms with different g's, an AxialSum, as the
diagrams of one observable: I1 + I2. Each term is run on its own and the
Ledgers are added, power by power of nu, into one LedgerSum (a Ledger);
stopped before average, the result is the list of each term's object.

expr may also be a dict {name: AxialIntegrand}. Each is run on its own,
all of them render on the one page, each in a section under its name,
and the result is {name: the last object}:

    Ls = feynmanReduce({"term 1": I1, "term 2": I2}, path="terms.html")
```

### `granada.feynman.STAGES`

Constant: `(('peel', <function peel at 0x7f1880da7100>), ('project', <function project at 0x7f1880db4400>), ('average', <function average at 0x7f1880dc36a0>))`

### class `granada.feynman.Average(channel, average)`

```text
One probe and its average over the direction of rhat, before weighting.

channel   the Channel whose probe was averaged
average   <Q>_rhat = refAverage(channel.probe), an FSum
```

### class `granada.feynman.Entry(coefficient, monomial, rPower, bessel)`

```text
One term C' * Q' of an averaged A_s.

coefficient   C', a sympy rational with its power of i
integrand     Q', a Term: a coefficient-free monomial times r^p times one
              Bessel or none
monomial, rPower, bessel   the three parts of Q' (rPower a sympy Rational)
```

Public methods and properties:

- `integrandTex(self)`

### class `granada.feynman.Ledger(projection)`

```text
int I = sum_s nu^s A_s, each A_s a list of Entries C' * Q'.

entries      {nu power s: [Entry]}; within each, no integrand repeats
averages     {nu power s: [Average]}: each channel's probe averaged, before
             the weights are applied and like terms merged
projection   the Projection it was averaged from
```

### class `granada.feynman.LedgerSum(integrand, ledgers)`

```text
An AxialSum's Ledgers added: int I = sum_s nu^s A_s, each A_s summed over the terms.

entries     {nu power s: [Entry]}: every term's entries at that power of nu,
            added, with equal integrands merged and zeros dropped
ledgers     [Ledger], one per term, in the order of the sum's terms
integrand   the AxialSum

It is a Ledger, so whatever takes a Ledger takes it: evalTower(), toI25(),
denominators(), partialFraction(), shiftBessel(). It has no projection or
averages of its own; each term's are in .ledgers.
```

### `granada.feynman.denominators(obj)`

```text
The propagator structures of every term of obj, genuine and n-dependent.

    rep = denominators(average(project(peel(I))))
    rep.propagators          # {k1: Usage, k1 + k2 + k3: Usage, ...}
    rep.genuine, rep.nDependent    # the two kinds

See the module docstring for the rules. Returns a DenominatorReport.
```

### class `granada.feynman.DenominatorReport(obj)`

```text
The momentum combinations in the denominators of every term of an expression.

propagators   {Vector: Usage}: every v standing as a propagator, genuine or
              n-dependent; Usage.kind says which
genuine       {Vector: Usage}: v with a negative rational power of v^2
nDependent    {Vector: Usage}: v with a power of v^2 that depends on n
dotProducts   {SP: Usage}: u.v (u != v) under a negative or n-dependent power
unaveraged    {SP: Usage}: (q.ref) still depending on the direction of ref
terms         how many terms were read
structures    [Structure]: the distinct structures of the sub-terms, each once:
              its propagators and the momentum its Bessel sits on, exponents aside
loopMomenta   the momenta everything is made of
N             L(L+1)/2 for L loop momenta: the most propagators that can be
              independent, the size of a family of masters
```

Public methods and properties:

- `latex(self)`
- `render(self, path=None, openBrowser=False)`: A page under the name of the variable holding it (in a notebook, typeset).
- `termsWith(self, v)`: The labels of the terms carrying v as a propagator, genuine or n-dependent: (nu power, index) for a Ledger.

### class `granada.feynman.Structure(momenta, bessel)`

```text
One distinct propagator structure: what a sub-term has, exponents aside.

momenta    the momenta v with a genuine or n-dependent power of v^2, together
           with the momentum the Bessel sits on (whatever its power, even
           none), sorted: what a family of masters needs for the sub-term
bessel     the momentum its Bessel sits on, or None
terms      how many sub-terms have this structure
nuPowers   at which powers of nu
```

Public methods and properties:

- `compoundBessel`
- `dependent`
- `flags(self, N)`
- `size`

### `granada.feynman.partialFraction(obj, keep=())`

```text
Partial-fraction every term so its propagators are linearly independent.

    rep = partialFraction(average(project(peel(I))))
    rep.result         # the same expression, every term on independent propagators
    rep.families       # the maximal sets of propagators that appear

obj is a Ledger, a Series or Terms of Entries, or anything that lifts to an
FSum. keep lists momenta whose propagators to keep, in order of preference,
when one has to go. See the module docstring for the rules. Returns a
PartialFractionReport; obj itself is not changed.
```

### class `granada.feynman.PartialFractionReport(obj, result, tally, keep)`

```text
partialFraction(obj): the propagators before and after partial fractioning.

loopMomenta       the momenta the propagators are made of
maxIndependent    L(L+1)/2: at most that many propagators are independent
before            denominators() of the input
structuresBefore  its propagator structures, with the momenta of its Bessels
rankBefore        how many of them are independent
dependentTerms    the terms whose propagators were linearly dependent
result            the partial-fractioned expression, of the input's kind: a
                  Series of Entries per power of nu for a Ledger, Terms for
                  Terms, an FSum otherwise
after             denominators() of the result
structures        the propagator structures that can appear in it, sorted
sectors           {frozenset: terms}: each term's set of propagators
families          {frozenset: terms}: the maximal sectors, with the terms
                  of every sector inside them
besselOn          {family: set of momenta carrying a Bessel in it}
irreducible       {frozenset: terms}: dependent sets partial fractions
                  cannot reduce (several n-dependent or half-integer powers)
```

Public methods and properties:

- `latex(self)`
- `render(self, path=None, openBrowser=False)`: A page under the name of the variable holding it (in a notebook, typeset).

### `granada.feynman.shiftBessel(obj, prefer=())`

```text
Shift each term's integration momenta so its Bessel sits on one momentum.

    S = shiftBessel(average(project(peel(I))))
    denominators(S)

obj is a Ledger, a Series or Terms of Entries, or anything that lifts to an
FSum; the result is of the same kind (a Series of Entries for a Ledger, an
FSum otherwise). prefer lists momenta to shift first when there is a
choice. See the module docstring. obj itself is not changed.
```

### `granada.feynman.toI25(obj, k1, k2, k3, D=3)`

```text
Every term as an outer integral over k1 times the five-line two-loop integral.

    rep = toI25(average(project(peel(I))), k1, k2, k3)
    rep.flagged        # the terms that cannot be put in that form
    rep.integrals      # {power of nu: [I25]}

k1 is the outer momentum, on which every Bessel is put; k2 and k3 are the
inner ones. See the module docstring. obj itself is not changed.
```

### class `granada.feynman.I25Report(obj, momenta, D)`

```text
toI25(obj, k1, k2, k3): every term as an outer k1 integral times the five-line integral.

flagged      [Flag]: terms that cannot be put in the form, with the reason
integrals    {power of nu: [I25]}, like integrals merged
mappings     [Mapping], one per structure of the terms that were mapped
terms        how many terms were read; mapped, how many of them were mapped
D            the dimension of the inner integral, 3
```

Public methods and properties:

- `latex(self)`
- `render(self, path=None, openBrowser=False)`: A page under the name of the variable holding it (in a notebook, typeset).

### class `granada.feynman.I25(coefficient, nu, outer, rPower, bessel, D)`

```text
One integral of the result: c r^p (k1^2)^outer j_l(s |k1| r) I(nu_1, ..., nu_5).

coefficient   a sympy number (times i if need be)
nu            (nu_1, ..., nu_5): the power of each line in the denominator
outer         the power of k1^2 in the term itself
outerTotal    outer + D - nu_12345: with the scaling of the inner integral
rPower        the power of r in front
bessel        the SphBessel, on k1
```

Public methods and properties:

- `latex(self)`
- `outerTotal`

### `granada.feynman.evalTower(obj, master, basis=None, *, flip=None, denominator=True, propagators=3, dropScaleless=False, simplify=True, check=True, path=None, open_browser=False)`

```text
The tower of obj at your master integral, summed, simplified and rendered.

    V = evalTower(T, "M[l_, a_, b_, c_, r_] := ...", basis=[k, p, k + p])
    V.value        # the simplified result, in V.n and V.r

    S = evalTower(feynmanReduce(I), M, basis=[k, p, k + p], flip=k)
    S[1].value     # A_1;  S.value is int I = sum_s nu^s A_s

obj, basis, denominator, propagators and dropScaleless are as for
getTower(), and the tower evaluated is the one getTower() would write.
master is a Mathematica definition, a Python function, or a Master (see
master()). simplify=False leaves the sum as evaluated; check=False skips
the numerical check of the simplified result against the tower. path
and open_browser are as for render(): one page shows the master, the
tower, every master evaluated and the result.

obj may also be the Ledger feynmanReduce() returns, for a term of two
momenta. Each A_s, the entries at one power of nu added up, is then
reduced, aligned onto basis[0] and folded under flip -> -flip onto basis,
as refReduce() does, and evaluated as any tower; basis and flip are
required. The result is a TowerSeries, {power of nu: TowerValue}, whose
value is sum_s nu^s A_s. flip is for a Ledger only.

Several expressions at once, a list [A1, A2] or a dict {"A1": A1} (the
dict of Ledgers feynmanReduce() returns for several terms too), are
evaluated each on its own, on one page, as getTower() writes them each
under its own name. The result is then {name: result}.
```

### `granada.feynman.master(definition, args=None)`

```text
Your master integral, M(l, a_1, ..., a_P; r), for evalTower().

    M = master("M[l_, a_, b_, c_, r_] := Pi^(3/2) Gamma[3/2 - b] ...")
    M = master(lambda l, a, b, c, r: ...)       # sympy, may branch on its arguments
    M = master("Gamma[a] ...", args=("l", "a", "b", "c", "r"))

A string is read as Mathematica: a definition with patterns l_, a_, ...
gives the argument names, or args= names them for a bare right-hand
side. See the module docstring for what is understood and what is
refused. A Master is returned as it is.
```

### class `granada.feynman.Master(name, args, expr=None, dummies=None, fn=None, source=None)`

```text
Your closed form for M(l, a_1, ..., a_P; r), from Mathematica or Python.

name, args   the head and the argument names, as you wrote them
expr         the right-hand side, for a definition read from Mathematica
source       what you passed

Calling it, M(l, a, b, c, r), gives the sympy value at those arguments.
```

Public methods and properties:

- `arity`
- `latex(self)`
- `render(self, path=None, openBrowser=False)`
- `symbolic(self)`: The right-hand side in the argument names, or None if it cannot be had.

### class `granada.feynman.TowerValue(name, master, blocks, raw, value, checked, dropped, simplified, left=None, basis=None, dropScaleless=False)`

```text
evalTower(): the tower at your master, and its simplified sum.

value     the result, simplified: a sympy expression in n and r (and in
          any index of its own, n1 = index("n1"), ...)
raw       the same before simplification, sum of c M(...) as evaluated
blocks    [Block]: each block of the tower, its rows and their values
master    the Master
checked   (n, r, digits) where value was checked against the tower, or None;
          any other index was apart from n there (_indexValues)
dropped   how many scaleless pieces dropScaleless left out
left      those pieces, one expression; None when nothing was left out
dropScaleless   whether they were left out: the page then shows them, or
          says there were no scaleless terms
n, r      the sympy symbols of the spectral index and the separation
```

Public methods and properties:

- `masters`
- `vanishing`
- `wl(self)`: The result as Mathematica input, to compare with your own FullSimplify.

### class `granada.feynman.TowerSeries(name, master, items)`

```text
evalTower() of a Ledger: {power of nu: TowerValue}, and int I = sum_s nu^s A_s.

Each A_s is the Ledger's entries at that power of nu, added up, reduced,
aligned and folded, then evaluated as any tower is.

value      the assembled result, sum_s nu^s A_s, in nu, n and r
master     the Master
nu, n, r   the sympy symbols: nu = zhat . rhat, the spectral index, r
```

Public methods and properties:

- `value`

## `granada.schwinger`

### `granada.schwinger.Fx(*momenta)`

```text
F^x(k_1, ..., k_n) = F_n(k_1, ..., k_n) e^{i (k_1 + ... + k_n).x}, an FSum.
```

### `granada.schwinger.Fy(*momenta)`

```text
F^y(k_1, ..., k_n) = F_n(k_1, ..., k_n) e^{i (k_1 + ... + k_n).y}, an FSum.
```

### `granada.schwinger.G(*momenta)`

```text
G(k_1, ..., k_n) = G_n(k_1, ..., k_n) g(k_1 + ... + k_n), an AxialIntegrand of rank one.
```

### class `granada.schwinger.SchwingerTerm(expr, momenta=None, index=1, midpoint=False)`

```text
One product of the input, read into its structures.

typed         the product as written, an FSum of one term
expr          what is read: the product as written, or with midpoint=True
              the product at x = -r/2, y = r/2 (midpoint())
midpoint      True when it is read at the midpoint
momenta       (k_1, ..., k_L)
index         its number in the ledger, from 1
coefficient   C as a Fraction, with ipow (0 or 1) its power of i
rho, sigma    tuples of Fractions: the exponential is exp(i sum_i k_i . J_i),
              J_i = rho_i x + sigma_i y; at the midpoint J_i = rho_i r and
              sigma is 0, there being one external vector
alphas        {c: net power alpha} over the propagator-like structures
              (c . K)^2, c canonical, alpha != 0, in order
sources       {c: [(SP, exponent), ...]}: the factors each structure came from
primaries     [c] whose alpha is n-dependent or a positive integer, in order
numerators    [(c, m)]: squares (c . K)^(2m) with m = -alpha > 0
dots          [(u, v, m)]: numerator scalar products (u . K) . (v . K), u != +-v
linears       [(q, (a, b), m)]: linear factors ((q . K) . (a x + b y))^m; at
              the midpoint ((q . K) . t r)^m, (a, b) = (t, 0)
shifts        [(kind, drho, dsigma)]: one per sin or cos factor, with
              arg = sum_i k_i . (drho_i x + dsigma_i y); at the midpoint
              arg = sum_i drho_i k_i . r, dsigma = 0
shiftFactors  [Func]: those factors, as read
```

Public methods and properties:

- `C(self)`: The coefficient as a sympy number: a rational, times i if ipow.
- `loops`
- `reading`: How it is read, for captions: 'as typed', or 'as typed, then at x = −r/2, y = r/2'.
- `rows(self)`: T = the product as written (= the product at x = -r/2, y = r/2, at the midpoint).
- `termTex(self)`: What is read (at x = -r/2, y = r/2 at the midpoint) as latex() writes it, fractions at text size.
- `typedTex(self)`: The product as written.

### class `granada.schwinger.SchwingerLedger(items, momenta=None, midpoint=False)`

```text
The input of the pipeline: a list of SchwingerTerms, one per product.

    SchwingerLedger(expr)               every term of an expression
    SchwingerLedger([e1, e2, T])        expressions and terms, in order
    SchwingerLedger(expr, momenta=(k1, k2, k3))
    SchwingerLedger(expr, midpoint=True)    every term at x = -r/2, y = r/2

momenta   the integration momenta in order; by default every vector of
          the input that is not x or y, in natural order (k2 before k10)
midpoint  False: every term read in x and y; True: at x = -r/2, y = r/2
          (see the module docstring). Terms passed in are read again
          this way, from their products as written.
terms     [SchwingerTerm], numbered from 1 in the order given; the terms
          of a sum come in the algebra's order, with like terms merged
vanished  [(index, product)]: at the midpoint, the products that vanish
          at x = -r/2, y = r/2, set aside with their numbers; else empty
projections  [SchwingerProjection], one per input with G's or g's (an
          AxialIntegrand, or each term of an AxialSum), read at the
          midpoint only: its axis projected out, the products of its
          probes terms of the ledger

Every term is read on construction; a ValueError lists every refusal.
```

Public methods and properties:

- `loops`

### `granada.schwinger.getFamily(term)`

```text
The propagator family F(T) and its primary generators P, for one SchwingerTerm.
```

### `granada.schwinger.getGenerators(term)`

```text
The descendant generators D of one SchwingerTerm: quadratic, linear and shift.
```

### class `granada.schwinger.Generators(family, descendants)`

```text
The generator family G = P u D of one term.

family, descendants   what it is made of
PP, DD                the primary and the descendant generators
GG                    PP + DD, every generator with its .type
```

Public methods and properties:

- `rows(self)`

### class `granada.schwinger.Family(term)`

```text
getFamily(T): the propagator family F(T) and its primary generators.

term   the SchwingerTerm
FF     [Propagator], canonical, sorted and labelled
PP     [Primary], one per element of FF
key    the tuple of the c_b: equal keys, equal A(z)
```

Public methods and properties:

- `loops`
- `rows(self)`

### class `granada.schwinger.Descendants(term)`

```text
getGenerators(T): the descendant generators D, quadratic, linear and shift.

term   the SchwingerTerm
DD     [Quadratic | Linear | Shift], in that order of types
```

Public methods and properties:

- `needsGenericA`: True when a quadratic descendant differentiates with respect to A.
- `ofType(self, t)`
- `rows(self)`

### `granada.schwinger.getBraid(family, descendants)`

```text
The braiding algebra (A, J) of one term, with its checks; flags degenerate terms.
```

### class `granada.schwinger.Braid(family, descendants)`

```text
getBraid(F, D): the braiding algebra (A, J) of one term.

family, descendants, term   what it was built from
data        the FamilyData: A(z), the checks, det A and adj A
A           A(z), an L x L list of polynomials in the z_b
generic     True when quadratic descendants need Z for a generic A
differentiated, shifted   {'rho': [i], 'sigma': [i]}: which are acted on
flagged     None, or the reason the term goes no further
```

Public methods and properties:

- `loops`
- `rows(self)`

### `granada.schwinger.assemblePartitionFunction(braid)`

```text
Z(A, J) = (4 pi)^{-3L/2} (det A)^{-3/2} exp(-J^T adj(A) J / (4 det A)) for a Braid.
```

### class `granada.schwinger.PartitionFunction(braid)`

```text
assemblePartitionFunction(B): Z(A, J), solved.

braid      the Braid it was built from
det, adj   det A(z) and adj A(z), polynomials in the z_b
generic    the GenericGaussian (det, adj for A = (a_ij)), or None when no
           quadratic descendant needs it
```

Public methods and properties:

- `ZRows(self)`
- `loops`
- `rows(self)`
- `source(self, rho, sigma)`: (P_xx, P_xy, P_yy, u, v) at rational rho, sigma, u = adj A rho, v = adj A sigma.

### `granada.schwinger.getSchwingerForm(G, Z, evaluateDescendants=False, check=False, assembleUpTo=200, writeUpTo=2000)`

```text
The SchwingerForm of one term, from its generators G and its partition function Z.

evaluateDescendants   False: every generator unevaluated; True: the
                      descendants evaluated (see the module docstring)
check                 compare the derivatives with finite differences of Z,
                      once per set of derivatives
assembleUpTo          with evaluateDescendants, also the whole integrand as
                      one formula when every numerator N^(s) has at most
                      this many terms (assembled()); 0 never
writeUpTo             on the page, a polynomial of more terms than this (F,
                      det A, M_uv, P^(s)) is written as its first terms and
                      its size; None for every term
```

### class `granada.schwinger.SchwingerForm(generators, Z, evaluateDescendants=False, check=False, assembleUpTo=200, writeUpTo=2000)`

```text
getSchwingerForm(G, Z): one term as generators acting on Z, evaluated or not.

generators, Z, term   what it was built from
evaluated    True when the descendants are evaluated
branches     [Branch]: the shifts' branches, equal currents merged
kappa        (r, p): the constant r i^p in front, C (-i)^m (2i)^-#sin 2^-#cos
keys         the derivation keys of the quadratic and linear descendants
F            (evaluated) the polynomial F of calculus.py, the same in every branch
factorizes   True when the family splits into blocks, or is a single z_b (a
             one-loop term, trivially); False only for one block of several z_b.
             factorized() is then the integral as products of integrals over
             the blocks, when it is assembled
fullyFactorizes  True when every block is a single z_b (a one-loop term too):
             fullyFactorized() is then a sum of products of one-dimensional
             integrals, each a master integral (final.py)
assembleUpTo the most terms a numerator N^(s) of the assembled form may have
writeUpTo    the most terms a polynomial is written out with on the page (F,
             det A, M_uv, P^(s)); a longer one is its first 50 terms
             (_poly.SHOWN) and a note. None for every term
```

Public methods and properties:

- `assembled(self)`: The integrand in z as one formula: an _Assembled, or None when it would be long.
- `assembledIntegrand(self)`: The assembled form, assembled(), in sympy: for checks against integrand().
- `assembledRows(self)`: The assembled form: I(T) as one formula, then the numerators and det A it names.
- `branchF(self, branch)`: F(w^(s)): F at A = A(z) and the branch's J, in sympy (the symbols of branchIntegrand).
- `branchIntegrand(self, branch)`: F(w^(s)) (4 pi)^{-3L/2} det^{-3/2} exp(-Q^(s)) as a sympy expression, for one branch.
- `evaluatedRows(self)`
- `explicitF(self, branch)`: F^(s) exactly as the evaluated card writes it, in sympy, for checks against branchF.
- `factorized(self)`: The Schwinger integral as products of integrals over the blocks: a _Factorized.
- `factorizedIntegrand(self)`: The factorized form, factorized(), in sympy with every integral's integrand multiplied out: for checks against assembledIntegrand().
- `factorizedRows(self)`: The factorized form: the blocks, det A over them, then I(T) as a sum of products of integrals, one per block, with every constant in front.
- `factorizes`: True when the family splits into two blocks or more (det A factors), so that the term is a sum of products of integrals over the blocks, or is a single z_b, one integral already. False only for one block of several z_b.
- `fullyFactorized(self)`: The factorized form of a term whose every block is a single z_b: a _Factorized.
- `fullyFactorizes`: True when every block of the family is a single z_b, one block of one included: the integral is then a sum of products of one-dimensional integrals.
- `integrand(self)`: The whole integrand in sympy: kappa prod_b z_b^(alpha_b - 1)/Gamma(alpha_b) sum_s ...
- `kappaTex(self)`: kappa = C (-i)^m (2i)^-#sin 2^-#cos, as a row, or None when kappa = C.
- `loops`
- `unevaluatedRows(self)`: I = C D J |_(point), then C, D, J, Delta and the P's, each defined once.

### `granada.schwinger.schwingerReduce(expr, *, momenta=None, midpoint=None, evaluateDescendants=False, check=True, assembleUpTo=200, writeUpTo=2000, path=None, openBrowser=False, termsPerPage=500, finalExpression=True)`

```text
Run the Schwinger pipeline over every term and write the page.

    R = schwingerReduce(G2(k1, k2) * PL(k1) * PL(k2) / SP(k1 + k2, k1 + k2)
                        * sin(SP(k1, x - y) / 2) * cexp(SP(k1, x) + SP(k2, y)),
                        evaluateDescendants=True, path="schwinger.html")

expr          a SchwingerLedger, or what SchwingerLedger takes
momenta       as for SchwingerLedger
midpoint      False: in x and y; True: every term at x = -r/2, y = r/2,
              the descendants built from that (ledger.py). None (the
              default): a ledger's own reading, else False. A ledger read
              the other way is read again.
evaluateDescendants   show the evaluated form too
check         compare every distinct set of derivatives with finite
              differences of Z (with evaluateDescendants)
assembleUpTo  with evaluateDescendants, a term whose numerators N^(s) have
              at most this many terms is also written as one formula, the
              Assembled card; 0 for none
writeUpTo     a polynomial on the page (F, det A, M_uv, P^(s)) of more terms
              than this is written as its first terms and its size, so that a
              page stays readable and light; the forms keep it whole (.F).
              None writes every term
path          the page; with more than termsPerPage terms, an index page
              there and pages path-0001.html, ... beside it. In a notebook
              without path, a small result is shown inline.
termsPerPage  terms per page
finalExpression   with evaluateDescendants, every term that fully factorizes
              as products of master integrals, the sums they make up, and
              each simplified (final.py): .final, and the Result section of
              the page

Returns a SchwingerReduction: .forms, .flagged, .pages, .final.
```

### class `granada.schwinger.SchwingerReduction(ledger, forms, flagged, evaluated, pages=())`

```text
What schwingerReduce() returns.

ledger      the SchwingerLedger
forms       [SchwingerForm], one per processed term, in order
flagged     [Flagged], the terms that went no further
pages       the paths written
factorizing, notFactorizing   the numbers of the processed terms whose
            family splits into blocks, and of those whose family does not
fullyFactorizing   the numbers of those whose every block is a single z_b
final       the FinalExpression (final.py): every term that fully factorizes
            as products of master integrals, and the sums they make up;
            None without evaluateDescendants or with finalExpression=False
```

Public methods and properties:

- `factorizing`
- `fullyFactorizing`
- `notFactorizing`

### `granada.schwinger.master(e, Q)`

```text
M(e; Q) = int_0^inf dz z^e exp(-Q / (4 z)), from derivedMaster() at a = e + 1, c = Q / 4.
```

### `granada.schwinger.getFinalExpression(reduction)`

```text
The final expression of a SchwingerReduction: a FinalExpression. See the module docstring.
```

### class `granada.schwinger.FinalExpression(reduction)`

```text
The final expression of a SchwingerReduction, from the terms that fully factorize.

values     {term number: TermValue}, every term that fully factorizes and is
           finite: a TermValues
const      the numbers of the flagged terms (scaleless or contact): const
missing    {term number: reason}: the terms that are not evaluated, a Missing
inputs     [InputResult], one per input with G's
plain      the sum of the terms of no input with G's, simplified; None when
           there are none, or one of them is missing
total      {s: A_s} over the whole ledger, simplified, a NuSeries: s = 0 alone
           without G's; None when a term is missing
hasConst   True when anything is written as const

The total is const + sum_s nu^s total[s]: totalExpr(), in sympy. Every one
of these shows itself: render(R.final), render([R.final.total,
R.final.missing]), latex(R.final.values[1]), and in a notebook.
```

Public methods and properties:

- `complete`
- `totalExpr(self)`: const + sum_s nu^s A_s, in sympy; None when a term is missing.

## `granada.decompose`

### `granada.decompose.decompose(n: 'int', dim: 'Optional[int]' = None) -> 'Decomposition'`

```text
Build the delta/rhat Ansatz for a rank-n tensor and solve for its coefficients.

``dim`` is the spatial dimension; ``None`` keeps it as a symbol ``d``.
```

### class `granada.decompose.Decomposition(n: 'int', dim: 'object', structures: 'List[Structure]', coefficients: 'List[Dict[int, sympy.Expr]]', projector_coefficients: 'List[Dict[int, sympy.Expr]]' = <factory>, singular: 'bool' = False) -> None`

```text
Decomposition(n: 'int', dim: 'object', structures: 'List[Structure]', coefficients: 'List[Dict[int, sympy.Expr]]', projector_coefficients: 'List[Dict[int, sympy.Expr]]' = <factory>, singular: 'bool' = False)
```

Public methods and properties:

- `coefficient_matrix(self) -> 'sympy.Matrix'`
- `gram_matrix(self) -> 'sympy.Matrix'`
- `to_html(self) -> 'str'`
- `to_latex(self) -> 'str'`

### class `granada.decompose.Structure(pairs: 'Tuple[Pair, ...]', singles: 'Tuple[int, ...]') -> None`

```text
Product of delta's (``pairs``) and rhat's (``singles``) on slots 0..n-1.
```

Public methods and properties:

- `k`
