# ChemBalance Desktop

**ChemBalance Desktop** is a local-first Windows workbench for balancing chemical equations with exact rational linear algebra. It turns atom-conservation constraints, and net charge where supplied, into a matrix and returns the smallest positive whole-number coefficient ratio without floating-point rounding.

> **Scope.** ChemBalance verifies mathematical conservation. It does not predict products, establish chemical feasibility, determine reaction conditions, or replace hazard assessment and professional chemical judgment.

## Highlights

| Capability | Description |
| --- | --- |
| Exact balancing | Fraction-based Gaussian elimination avoids rounding drift and finds the smallest positive integer ratio. |
| Professional desktop UI | A polished Windows interface with keyboard-first input, high-DPI scaling, dark appearance, examples, copy, and text export. |
| Rich formula syntax | Supports nested groups, square-bracketed coordination groups, hydrates, Unicode subscripts, leading hydrate multipliers, and bracketed ionic charges. |
| Transparent verification | Shows the atom count on both sides for every element, checks net charge when applicable, and lists coefficients and molar masses. |
| Local history | Stores up to 100 recent calculations only on the current computer. There is no telemetry or network calculation service. |
| Reproducible releases | GitHub Actions runs tests, builds the Windows executable, packages a ZIP archive, and includes a SHA-256 checksum for tagged releases. |

## Get the Windows application

Download the latest `ChemBalance-windows-x64.zip` from the repository’s [Releases](../../releases) page. Extract it into a writable folder and run `ChemBalance.exe`. No separate Python installation is required for the packaged application.

Windows may display a SmartScreen warning for a newly published unsigned executable. This is expected until the project gains a code-signing certificate. Download only from the project’s official GitHub Releases page and, when required, compare the ZIP file against the accompanying `.sha256` checksum.

## Use the workbench

Enter one reactant side and one product side separated by `->`, `→`, `=`, or `⇌`, then select **Balance equation** or press `Ctrl+Enter`.

| Input | Result |
| --- | --- |
| `H2 + O2 -> H2O` | `2H₂ + O₂ → 2H₂O` |
| `Fe + O2 -> Fe2O3` | `4Fe + 3O₂ → 2Fe₂O₃` |
| `Ca(OH)2 + H3PO4 -> Ca3(PO4)2 + H2O` | `3Ca(OH)₂ + 2H₃PO₄ → Ca₃(PO₄)₂ + 6H₂O` |
| `CuSO4·5H2O -> CuSO4 + H2O` | `CuSO₄·5H₂O → CuSO₄ + 5H₂O` |
| `[Fe^2+] + [MnO4^-] + [H^+] -> [Fe^3+] + [Mn^2+] + H2O` | `5Fe²⁺ + MnO₄⁻ + 8H⁺ → 5Fe³⁺ + Mn²⁺ + 4H₂O` |

### Input reference

The parser accepts conventional element symbols, integer subscripts, nested parentheses, and square brackets. Hydrates may use a period or middle dot, for example `CuSO4.5H2O` or `CuSO4·5H2O`. For ionic charge, use a caret inside brackets, such as `[Fe^2+]`, `[MnO4^-]`, or `[H^+]`.

When a reaction has no unique positive balance, ChemBalance provides an actionable message instead of silently choosing an arbitrary solution. Equations with multiple independent reactions should be separated and balanced individually.

## Develop locally

ChemBalance requires Python 3.10 or newer. Create an isolated environment, install the desktop dependencies, and run the application:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Run the complete test suite with:

```bash
python -m unittest -v
```

The UI smoke test is suitable for a headless validation environment:

```bash
QT_QPA_PLATFORM=offscreen python ui_smoke_test.py
```

## Build a local executable

The release workflow builds Windows packages on a native `windows-latest` runner. To package locally on Windows, install the dependencies and run:

```powershell
python -m PyInstaller --noconfirm --clean --windowed --name ChemBalance app.py
Compress-Archive -Path dist/ChemBalance/* -DestinationPath dist/ChemBalance-windows-x64.zip -Force
Get-FileHash dist/ChemBalance-windows-x64.zip -Algorithm SHA256
```

The resulting folder is self-contained; distribute the ZIP archive instead of the executable alone.

## Release process

The workflow at [`.github/workflows/windows-release.yml`](.github/workflows/windows-release.yml) runs the core suite across Python 3.10–3.13, performs a desktop smoke test, and packages the Windows application. Pushing a tag beginning with `v` publishes the ZIP archive and its SHA-256 checksum to GitHub Releases.

```bash
git tag v1.0.0
git push origin v1.0.0
```

## License

ChemBalance is distributed under the [MIT License](LICENSE).
