# Output Files

This folder stores generated reports and figures.

Main simulation outputs:

```text
case_percentage_comparison_report.txt
1_overview_10_cases.png
2_zoom_last_7_days.png
3_max_difference_and_wind.png
4_ampacity_duration_curve.png
```

Comparison outputs:

```text
compare_emissivity_function.png
compare_ieee_transient_model.png
```

Regenerate the main outputs with:

```powershell
python .\__main__.py
```

Regenerate the comparison outputs with:

```powershell
python .\compare.py
```
