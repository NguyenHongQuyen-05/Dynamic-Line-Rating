import pandas as pd

from paths import CASE_PERCENT_REPORT_TXT, WEATHER_CSV, ensure_output_dir
from physics import (
    ConductorProperties,
    WeatherConditions,
    dynamic_absorptivity,
    dynamic_emissivity,
    steady_state_current,
)
from plots import plot_main_dlr_charts


MAX_TEMP = 90.0
STATIC_AMP = 850.0
CLEAR_SKY_COEFFS = (-42.2391, 63.8044, -1.9220, 3.46921e-2, -3.61118e-4, 1.94318e-6, -4.07608e-9)


def run_aging_dlr_simulation_10_cases(csv_file_path: str | None = None, max_allowable_temp: float = 90.0):
    csv_file_path = str(csv_file_path or WEATHER_CSV)
    print(f"Reading weather data from: {csv_file_path}...")
    df = pd.read_csv(csv_file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    thap_cham_conductor = ConductorProperties(27.5, 0.23, 0.33, 1310, 9.1338e-5, 7.4766e-5, 75.0, 20.0)

    all_cases_results = []
    base_date = pd.Timestamp("2014-01-01 00:00:00")

    for case_num in range(1, 11):
        cal_start_year = 2014 + (case_num - 1) * 3
        cal_end_year = cal_start_year + 2
        start_year_aging = (case_num - 1) * 3

        print(f"Calculating Case {case_num}: Actual data from {cal_start_year} to {cal_end_year}...")
        mask = (df["timestamp"].dt.year >= cal_start_year) & (df["timestamp"].dt.year <= cal_end_year)
        df_case_weather = df[mask].copy()

        if df_case_weather.empty:
            continue

        fixed_e = dynamic_emissivity(start_year_aging)
        fixed_a = dynamic_absorptivity(start_year_aging)

        case_data = {
            "timestamp": df_case_weather["timestamp"].values,
            "wind_speed_m_s": df_case_weather["wind_speed_m_s"].values,
            "fixed_ampacity": [],
            "dynamic_ampacity": [],
            "x_years": [],
        }

        for index, row in df_case_weather.iterrows():
            ts = row["timestamp"]
            x_years = (ts - base_date).total_seconds() / (365.2425 * 24 * 3600.0)

            weather = WeatherConditions(
                row["ambient_temp_c"], row["wind_speed_m_s"], row["wind_angle_deg"],
                35.0, 11.758, ts.timetuple().tm_yday, ts.hour + ts.minute / 60.0, CLEAR_SKY_COEFFS, 90.0
            )

            thap_cham_conductor.emissivity, thap_cham_conductor.absorptivity = fixed_e, fixed_a
            case_data["fixed_ampacity"].append(steady_state_current(max_allowable_temp, thap_cham_conductor, weather))

            thap_cham_conductor.emissivity, thap_cham_conductor.absorptivity = dynamic_emissivity(x_years), dynamic_absorptivity(x_years)
            case_data["dynamic_ampacity"].append(steady_state_current(max_allowable_temp, thap_cham_conductor, weather))
            case_data["x_years"].append(x_years)

        all_cases_results.append(pd.DataFrame(case_data))

    return all_cases_results


def write_statistics_report(results_list, static_ampacity=850.0, output_file=CASE_PERCENT_REPORT_TXT):
    ensure_output_dir()
    lines = []
    lines.append("===============================================================================")
    lines.append(f" STATISTICAL REPORT: DLR vs SLR CAPACITY GAIN (Static Line Rating = {static_ampacity}A) ")
    lines.append("===============================================================================")

    for i, df_case in enumerate(results_list):
        start_cal_year = 2014 + i * 3
        years = [start_cal_year, start_cal_year + 1, start_cal_year + 2]
        lines.append("")
        lines.append(f"---> CASE {i+1} (Period: {start_cal_year} - {start_cal_year+2}) <---")

        if not pd.api.types.is_datetime64_any_dtype(df_case["timestamp"]):
            df_case["timestamp"] = pd.to_datetime(df_case["timestamp"])

        for yr in years:
            df_yr = df_case[df_case["timestamp"].dt.year == yr]
            if df_yr.empty:
                continue

            mean_fixed = df_yr["fixed_ampacity"].mean()
            mean_dyn = df_yr["dynamic_ampacity"].mean()

            pct_inc_fixed = ((mean_fixed - static_ampacity) / static_ampacity) * 100
            pct_inc_dyn = ((mean_dyn - static_ampacity) / static_ampacity) * 100

            lines.append(f"  * Year {yr}: Avg Fixed Ampacity = {mean_fixed:.1f}A (+{pct_inc_fixed:.2f}%) | Avg Dynamic Ampacity = {mean_dyn:.1f}A (+{pct_inc_dyn:.2f}%)")

        mean_fixed_all = df_case["fixed_ampacity"].mean()
        mean_dyn_all = df_case["dynamic_ampacity"].mean()

        pct_inc_fixed_all = ((mean_fixed_all - static_ampacity) / static_ampacity) * 100
        pct_inc_dyn_all = ((mean_dyn_all - static_ampacity) / static_ampacity) * 100

        lines.append(f"  => 3-YEAR SUMMARY: Avg Fixed = {mean_fixed_all:.1f}A (+{pct_inc_fixed_all:.2f}%) | Avg Dynamic = {mean_dyn_all:.1f}A (+{pct_inc_dyn_all:.2f}%)")
        lines.append("-" * 80)

    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Statistical percentage report exported to: {output_file}")


def main() -> None:
    try:
        results_list = run_aging_dlr_simulation_10_cases(WEATHER_CSV, max_allowable_temp=MAX_TEMP)
        if not results_list:
            raise ValueError("No valid data to run the simulation!")

        write_statistics_report(results_list, static_ampacity=STATIC_AMP)
        plot_main_dlr_charts(results_list, static_amp=STATIC_AMP)

        print("\nSuccessfully completed! The percentage report and 4 charts have been exported to the output directory.")

    except FileNotFoundError:
        print(f"ERROR: File '{WEATHER_CSV}' not found. Please create the CSV file to run.")


if __name__ == "__main__":
    main()
