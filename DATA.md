# Data and Output Files

## Input Data

Place all required datasets in the `data/` directory. The paths are configured in
`paths.py`.

Required files:

```text
data/dlr_weather_trang_thap_cham_30_years.csv
data/emissivity_above_15kv_rural_atmosphere.xlsx
data/Emissivity_above_15kv_industrial_atmosphere.xlsx
data/parameter_220kv_thap_cham.xlsx
```

The main simulation currently uses:

- `dlr_weather_trang_thap_cham_30_years.csv`

The comparison function plot uses:

- `emissivity_above_15kv_rural_atmosphere.xlsx`

## Main Simulation Outputs

Running:

```powershell
python .\__main__.py
```

creates or updates:

```text
output/case_percentage_comparison_report.txt
output/1_overview_10_cases.png
output/2_zoom_last_7_days.png
output/3_max_difference_and_wind.png
output/4_ampacity_duration_curve.png
```

## Comparison Outputs

Running:

```powershell
python .\compare.py
```

creates or updates:

```text
output/compare_emissivity_function.png
output/compare_ieee_transient_model.png
```

## Version-Control Note

The `output/` directory is not ignored by `.gitignore`, so final figures and
reports can be committed when they are part of the research submission package.
