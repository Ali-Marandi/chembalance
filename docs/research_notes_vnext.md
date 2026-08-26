# ChemBalance — Research Notes for Next Release

## Product capability signals

Comparable stoichiometry tools frame the primary workflow around a balanced equation, conversion between molar amount, mass, and particle count, limiting-reagent analysis, theoretical yield, percent yield, and transparent calculation steps. Pearson’s stoichiometry calculator describes conversions between moles, grams, and particles based on balanced equations. The Learnbin advanced balancer documents value in exact fraction arithmetic, hydrate and ion support, a stoichiometry breakdown, and visible molar masses. These signals support a v1.1 focus on explainable mass-to-mole conversion and visual composition, rather than attempting reaction prediction.

Mass-percent composition should be calculated per compound as:

> element mass percentage = `(atom count × atomic weight) ÷ compound molar mass × 100`

The values must sum to 100% within display precision. The clearest desktop visual is a horizontal bar chart paired with an accessible table listing each element, atom count, atomic mass contribution, and percentage.

## Cross-platform CI/CD finding

GitHub’s official documentation states that `jobs.<job_id>.strategy.matrix` expands one job into separate runs for each combination of matrix variables, including operating systems. This provides the appropriate structure for native packaging on `windows-latest`, `macos-latest`, and `ubuntu-latest`. PyInstaller is designed to package Python applications on the target operating system, so each runner should produce only its own native distributable.

## Sources

1. GitHub Docs, [Running variations of jobs in a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations), accessed 26 August 2026.
2. Pearson, [Stoichiometry Calculator](https://www.pearson.com/channels/calculators/stoichiometry-calculator), accessed 26 August 2026.
3. Learnbin Lab, [Advanced Chemical Equation Balancer](https://lab.learnbin.net/tools/advanced-chemical-equation-balancer/), accessed 26 August 2026.
