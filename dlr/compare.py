import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

from paths import (
    COMPARE_EMISSIVITY_FUNCTION_PNG,
    COMPARE_IEEE_TRANSIENT_MODEL_PNG,
    RURAL_EMISSIVITY_XLSX,
    ensure_output_dir,
)
from physics import ConductorProperties, WeatherConditions, transient_temperature


def compare_emissivity_function(file_path: str | None = None) -> None:
    file_path = str(file_path or RURAL_EMISSIVITY_XLSX)

    try:
        df = pd.read_excel(file_path)
        x_data = df["Time"].values
        y_data = df["Coefficient"].values
    except FileNotFoundError:
        print("Excel file not found. Using mock data for demonstration...")
        x_data = np.array([5, 15, 30, 50, 75, 90])
        y_data = np.array([0.75, 0.88, 0.91, 0.92, 0.925, 0.928])

    k_values = []
    for x, y in zip(x_data, y_data):
        if x > 0 and 0.23 < y < 0.93:
            k = -(1 / x) * np.log(1 - (y - 0.23) / 0.7)
            k_values.append(k)

    k_mean = np.mean(k_values) if k_values else 0.384
    _ = k_mean

    plt.figure(figsize=(10, 6))

    plt.scatter(x_data, y_data, color="black", marker="o", s=50, zorder=5, label="Field Data: Emissivity (>15kV, Rural Atmosphere)")

    x_line = np.linspace(0, 100, 500)

    y_empirical = 0.23 + (0.7 * x_line) / (1.22 + x_line)
    plt.plot(x_line, y_empirical, color="blue", linewidth=2, zorder=3, label="Empirical Function")

    y_proposed = 0.23 + 0.7 * (1 - np.exp(-0.159 * x_line))
    plt.plot(x_line, y_proposed, color="red", linestyle="--", linewidth=2, zorder=4, label=f"Proposed Function (k={0.159:.4f})")

    plt.xlim(0, 100)
    plt.ylim(0, 1)

    plt.xlabel("Conductor Age (Years)", fontsize=12)
    plt.ylabel("Emissivity Coefficient", fontsize=12)
    plt.title("Goodness-of-Fit: Empirical vs. Proposed Emissivity Functions", fontsize=14, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.7)
    plt.legend(fontsize=12, loc="lower right")

    ensure_output_dir()
    plt.savefig(COMPARE_EMISSIVITY_FUNCTION_PNG, dpi=300, bbox_inches="tight")
    plt.show()


def compare_ieee_transient_model() -> None:
    print("Starting Transient Temperature simulation...")

    drake_conductor_transient = ConductorProperties(
        diameter_mm=28.14,
        emissivity=0.8,
        absorptivity=0.8,
        heat_capacity=1310.0,
        resistance_ref_high=1.220e-4,
        resistance_ref_low=7.283e-5,
        T_ref_high=200.0,
        T_ref_low=25.0,
    )

    clear_sky_coeffs = (-42.2391, 63.8044, -1.9220, 3.46921e-2, -3.61118e-4, 1.94318e-6, -4.07608e-9)
    weather = WeatherConditions(
        ambient_temp_c=40.0,
        wind_speed_m_s=0.61,
        wind_angle_deg=90.0,
        elevation_m=0.0,
        latitude_deg=30.0,
        day_of_year=161,
        time_of_day_hours=11.0,
        solar_coeffs=clear_sky_coeffs,
        line_azimuth_deg=90.0,
    )

    dt_step = 10.0
    time_steps_sec = np.arange(0, 1801, dt_step)
    time_steps_min = time_steps_sec / 60.0

    num_steps = len(time_steps_sec) - 1
    current_profile_1200 = np.full(num_steps, 1200.0)
    current_profile_1400 = np.full(num_steps, 1400.0)

    temps_1200 = transient_temperature(
        current_profile_1200,
        initial_temp_c=100.0,
        conductor=drake_conductor_transient,
        weather=weather,
        dt=dt_step,
    )

    temps_1400 = transient_temperature(
        current_profile_1400,
        initial_temp_c=100.0,
        conductor=drake_conductor_transient,
        weather=weather,
        dt=dt_step,
    )

    doc_time = np.array([0, 5, 10, 15, 20, 25, 30])
    doc_temp_1200 = np.array([100.0, 106.9, 111.4, 114.5, 116.5, 117.6, 118.2])
    doc_temp_1400 = np.array([100.0, 116.8, 127.8, 134.8, 139.4, 142.3, 143.7])

    time_smooth = np.linspace(0, 30, 300)
    spline_1200 = make_interp_spline(doc_time, doc_temp_1200, k=3)
    spline_1400 = make_interp_spline(doc_time, doc_temp_1400, k=3)

    doc_smooth_1200 = spline_1200(time_smooth)
    doc_smooth_1400 = spline_1400(time_smooth)

    plt.figure(figsize=(10, 6))

    plt.plot(time_smooth, doc_smooth_1200, label="IEEE  (1200 A)", color="red", linewidth=2.5, linestyle="-", zorder=1)
    plt.plot(time_smooth, doc_smooth_1400, label="IEEE  (1400 A)", color="red", linewidth=2.5, linestyle="-", zorder=1)

    plt.plot(time_steps_min, temps_1200, label="Simulation (1200 A)", color="blue", linewidth=2.5, linestyle="--", zorder=2)
    plt.plot(time_steps_min, temps_1400, label="Simulation (1400 A)", color="blue", linewidth=2.5, linestyle="--", zorder=2)

    plt.xlim(0, 30)
    plt.ylim(100, 150)

    plt.grid(True, which="both", linestyle="-", linewidth=0.5, alpha=0.7)
    plt.xlabel("Time (min)", fontsize=12)
    plt.ylabel("Conductor Temperature (°C)", fontsize=12)

    plt.legend(loc="upper left", fontsize=11)

    plt.title("Comparison:  Simulation  vs IEEE 738-2023 ", fontsize=14, fontweight="bold")
    plt.tight_layout()

    ensure_output_dir()
    plt.savefig(COMPARE_IEEE_TRANSIENT_MODEL_PNG, dpi=300, bbox_inches="tight")
    plt.show()


def main() -> None:
    compare_emissivity_function()
    compare_ieee_transient_model()


if __name__ == "__main__":
    main()
