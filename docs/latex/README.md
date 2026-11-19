# Printable diagram documentation

- [Read the A4 article (PDF)](diagram-explained.pdf)
- [Edit the LaTeX source](diagram-explained.tex)

The article follows the actual diagram's four columns and row order. It includes
a short project description, a black-and-white reading map, sensor and GPIO
explanations, relay/power wiring, exact control rules, worked examples, simulation
steps, energy calculations, troubleshooting, and the scope of the validation.

Formatting uses the standard `article` class, A4 paper, 11-point default
Computer Modern serif text, 25 mm margins, and black text/graphics on white.
Links are uncoloured. No external image files or bibliography tools are needed.

From the repository root, compile twice with pdfLaTeX (MiKTeX or TeX Live):

```powershell
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=docs/latex docs/latex/diagram-explained.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=docs/latex docs/latex/diagram-explained.tex
```

The second pass resolves table and figure references. Required packages are
listed in the source preamble; the LaTeX installation must provide them.
The PDF is committed for readers who do not have LaTeX installed.
