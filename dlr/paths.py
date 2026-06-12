from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

WEATHER_CSV = DATA_DIR / "dlr_weather_trang_thap_cham_30_years.csv"
RURAL_EMISSIVITY_XLSX = DATA_DIR / "emissivity_above_15kv_rural_atmosphere.xlsx"
INDUSTRIAL_EMISSIVITY_XLSX = DATA_DIR / "Emissivity_above_15kv_industrial_atmosphere.xlsx"
CONDUCTOR_PARAMS_XLSX = DATA_DIR / "parameter_220kv_thap_cham.xlsx"

OVERVIEW_10_CASES_PNG = OUTPUT_DIR / "1_overview_10_cases.png"
ZOOM_LAST_7_DAYS_PNG = OUTPUT_DIR / "2_zoom_last_7_days.png"
MAX_DIFFERENCE_AND_WIND_PNG = OUTPUT_DIR / "3_max_difference_and_wind.png"
AMPACITY_DURATION_CURVE_PNG = OUTPUT_DIR / "4_ampacity_duration_curve.png"
CASE_PERCENT_REPORT_TXT = OUTPUT_DIR / "case_percentage_comparison_report.txt"
COMPARE_EMISSIVITY_FUNCTION_PNG = OUTPUT_DIR / "compare_emissivity_function.png"
COMPARE_IEEE_TRANSIENT_MODEL_PNG = OUTPUT_DIR / "compare_ieee_transient_model.png"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR
