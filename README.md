# Dynamic Line Rating Model with Conductor Aging Effects

This repository contains a Python implementation of a Dynamic Line Rating (DLR)
workflow for a 220 kV ACSR overhead transmission line, based on IEEE Std
738-2023 physics and an aging-enhanced emissivity/absorptivity model.

The code is organized so that the original IEEE 738-2023 heat balance functions,
the aging enhancement, plotting routines, path configuration, and simulation
entrypoint are separated into dedicated modules.

## Repository Structure

```text
.
├── __main__.py              # Main entrypoint for the DLR simulation
├── compare.py               # Comparison plots for emissivity function and IEEE transient model
├── paths.py                 # Centralized data and output paths
├── physics.py               # IEEE 738-2023 physics and aging enhancement functions
├── plots.py                 # Figure generation and export routines
├── simulation.py            # DLR simulation pipeline and percentage report export
├── data/                    # Required input datasets
├── output/                  # Generated reports and figures
├── requirements.txt         # Pip dependencies
├── environment.yml          # Conda environment definition
└── DATA.md                  # Dataset and output description
```

## Requirements

Python 3.11 or newer is recommended.

Install dependencies with pip:

```powershell
python -m pip install -r requirements.txt
```

Or create a Conda environment:

```powershell
conda env create -f environment.yml
conda activate DynamicLineRating
```

## Input Data

The required input files must be stored in the `data/` folder:

```text
data/dlr_weather_trang_thap_cham_30_years.csv
data/emissivity_above_15kv_rural_atmosphere.xlsx
data/Emissivity_above_15kv_industrial_atmosphere.xlsx
data/parameter_220kv_thap_cham.xlsx
```

See [DATA.md](DATA.md) for details.

## Run the Main Simulation

From the repository root:

```powershell
python .\__main__.py
```

The simulation reads the weather dataset, calculates 10 three-year cases, writes
the percentage comparison report, and exports the four main figures into
`output/`.

Generated main outputs:

```text
output/case_percentage_comparison_report.txt
output/1_overview_10_cases.png
output/2_zoom_last_7_days.png
output/3_max_difference_and_wind.png
output/4_ampacity_duration_curve.png
```

## Run Comparison Figures

```powershell
python .\compare.py
```

This generates:

```text
output/compare_emissivity_function.png
output/compare_ieee_transient_model.png
```

## Module Notes

- `physics.py` contains the original IEEE 738-2023 physics functions used by
  the transient comparison model.
- `physics.py` also contains the aging enhancement functions
  `dynamic_emissivity()` and `dynamic_absorptivity()`, used by the main DLR
  simulation.
- `simulation.py` applies the aging-enhanced parameters over time and writes the
  case percentage comparison report.
- `plots.py` preserves the plotting formats used for the reported figures.

## Reproducibility

The main calculation constants, figure names, plotting styles, and output image
formats are intentionally kept stable so that the generated outputs remain
consistent with the manuscript figures.
