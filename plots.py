import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from paths import (
    AMPACITY_DURATION_CURVE_PNG,
    MAX_DIFFERENCE_AND_WIND_PNG,
    OVERVIEW_10_CASES_PNG,
    ZOOM_LAST_7_DAYS_PNG,
    ensure_output_dir,
)
from physics import dynamic_absorptivity, dynamic_emissivity


def plot_overview_10_cases(results_list) -> None:
    ensure_output_dir()
    print("\n[1/4] Plotting overview chart for 10 cases...")
    fig1, axes1 = plt.subplots(nrows=5, ncols=2, figsize=(18, 24))
    for i, ax in enumerate(axes1.flatten()):
        if i >= len(results_list):
            break
        df_case = results_list[i]
        start_yr_aging = i * 3
        e_val, a_val = dynamic_emissivity(start_yr_aging), dynamic_absorptivity(start_yr_aging)

        ax.plot(df_case["timestamp"], df_case["fixed_ampacity"], label=f"Fixed at Cycle Start (e={e_val:.3f}, a={a_val:.3f})", color="dimgrey", linestyle="--", linewidth=2)
        ax.plot(df_case["timestamp"], df_case["dynamic_ampacity"], label="Dynamic Ampacity", color="royalblue", linewidth=1.5)
        ax.set_title(f"Case {i+1}: Period {2014+i*3} - {2014+i*3+2}", fontsize=12, fontweight="bold")
        ax.grid(True, linestyle=":", alpha=0.7)
        ax.legend(loc="best", fontsize=9)

    fig1.suptitle("EVALUATION OF AGING IMPACT ON THAP CHAM DLR MODEL (30 YEARS)", fontsize=18, fontweight="bold", y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(OVERVIEW_10_CASES_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig1)


def plot_zoom_last_7_days(results_list) -> None:
    ensure_output_dir()
    print("[2/4] Plotting zoomed-in chart for the last 7 days...")
    fig2, axes2 = plt.subplots(nrows=5, ncols=2, figsize=(18, 24))
    for i, ax in enumerate(axes2.flatten()):
        if i >= len(results_list):
            break
        df_case = results_list[i]
        df_week = df_case[df_case["timestamp"] >= (df_case["timestamp"].iloc[-1] - pd.Timedelta(days=7))]

        ax.plot(df_week["timestamp"], df_week["fixed_ampacity"], label="Fixed Ampacity", color="dimgrey", linestyle="--", linewidth=2)
        ax.plot(df_week["timestamp"], df_week["dynamic_ampacity"], label="Dynamic Ampacity", color="royalblue", linewidth=1.5)
        ax.set_title(f"Case {i+1} (Last 7 Days)", fontsize=12, fontweight="bold")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%d/%m"))
        ax.grid(True, linestyle=":", alpha=0.7)
        ax.legend(loc="best", fontsize=9)

    fig2.suptitle("ZOOM INTO THE LAST 7 DAYS IN EACH 3-YEAR PERIOD", fontsize=18, fontweight="bold", y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(ZOOM_LAST_7_DAYS_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig2)


def plot_max_difference_and_wind(results_list) -> None:
    ensure_output_dir()
    print("[3/4] Analyzing max difference and plotting with wind speed...")
    fig3, axes3 = plt.subplots(nrows=5, ncols=2, figsize=(18, 24))

    for i, ax in enumerate(axes3.flatten()):
        if i >= len(results_list):
            break
        df_case = results_list[i].copy()

        df_case["diff"] = (df_case["fixed_ampacity"] - df_case["dynamic_ampacity"]).abs()
        row_max = df_case.loc[df_case["diff"].idxmax()]
        peak_time, max_diff_val = row_max["timestamp"], row_max["diff"]

        df_zoom = df_case[
            (df_case["timestamp"] >= peak_time - pd.Timedelta(days=1))
            & (df_case["timestamp"] <= peak_time + pd.Timedelta(days=1))
        ]

        start_yr_aging = i * 3
        fixed_e_val = dynamic_emissivity(start_yr_aging)
        fixed_a_val = dynamic_absorptivity(start_yr_aging)

        l1 = ax.plot(df_zoom["timestamp"], df_zoom["fixed_ampacity"], label=f"Fixed Ampacity (e={fixed_e_val:.3f}, a={fixed_a_val:.3f})", color="dimgrey", linestyle="--", linewidth=2)
        l2 = ax.plot(df_zoom["timestamp"], df_zoom["dynamic_ampacity"], label="Dynamic Ampacity", color="royalblue", linewidth=1.5)
        ax.set_ylabel("Load Current (A)", fontsize=10, fontweight="bold")

        ax.scatter([peak_time] * 2, [row_max["fixed_ampacity"], row_max["dynamic_ampacity"]], color="red", s=60, zorder=5)
        ax.plot([peak_time, peak_time], [row_max["fixed_ampacity"], row_max["dynamic_ampacity"]], color="red", linestyle=":", linewidth=2)
        ax.annotate(f"Max Diff: {max_diff_val:.1f} A", xy=(peak_time, row_max["fixed_ampacity"]), xytext=(10, 15),
                    textcoords="offset points", color="darkred", fontweight="bold", bbox=dict(boxstyle="round", fc="yellow", alpha=0.5))

        ax2 = ax.twinx()
        l3 = ax2.plot(df_zoom["timestamp"], df_zoom["wind_speed_m_s"], label="Wind Speed", color="teal", alpha=0.6, linewidth=1.5)
        ax2.fill_between(df_zoom["timestamp"], 0, df_zoom["wind_speed_m_s"], color="teal", alpha=0.1)
        ax2.set_ylabel("Wind Speed (m/s)", color="teal", fontsize=10)
        ax2.set_ylim(0, max(1.0, df_zoom["wind_speed_m_s"].max() * 2.5))

        ax.set_title(f'Case {i+1}: Maximum Difference ({peak_time.strftime("%d/%m/%Y %H:%M")})', fontsize=12, fontweight="bold")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%d/%m"))
        ax.grid(True, linestyle=":", alpha=0.7)

        lines = l1 + l2 + l3
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc="upper left", fontsize=9)

    fig3.suptitle("MAXIMUM DIFFERENCE LOCATION & CORRELATION WITH WIND SPEED", fontsize=18, fontweight="bold", y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(MAX_DIFFERENCE_AND_WIND_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig3)


def plot_ampacity_duration_curve(results_list, static_amp: float = 850.0) -> None:
    ensure_output_dir()
    print("[4/4] Plotting Ampacity Duration Curve...")
    plt.figure(figsize=(12, 7))

    sorted_fixed = np.sort(np.concatenate([df["fixed_ampacity"].values for df in results_list]))[::-1]
    sorted_dyn = np.sort(np.concatenate([df["dynamic_ampacity"].values for df in results_list]))[::-1]
    x_pct = np.linspace(0, 100, len(sorted_fixed))

    plt.plot(x_pct, sorted_fixed, label="DLR (Assumed Fixed Parameters)", color="dimgrey", linestyle="--", linewidth=2)
    plt.plot(x_pct, sorted_dyn, label="DLR (Dynamic Calculation based on Actual Aging)", color="royalblue", linewidth=2)
    plt.axhline(y=static_amp, color="red", linestyle="-", linewidth=2.5, label=f"Traditional Static Line Rating Limit (SLR = {static_amp}A)")

    plt.fill_between(x_pct, static_amp, sorted_dyn, where=(sorted_dyn > static_amp), color="royalblue", alpha=0.15, label="Additional Optimal Capacity via DLR")

    plt.title("AMPACITY DURATION CURVE - 30 YEARS TOTAL", fontsize=15, fontweight="bold")
    plt.xlabel("Percentage of Operation Time over 30 Years (%)", fontsize=12, fontweight="bold")
    plt.ylabel("Safe Load Current Capacity (Ampere)", fontsize=12, fontweight="bold")
    plt.xlim(0, 100)
    plt.grid(True, which="both", linestyle="--", alpha=0.7)
    plt.legend(loc="upper right", fontsize=11)

    plt.tight_layout()
    plt.savefig(AMPACITY_DURATION_CURVE_PNG, dpi=300)
    plt.show()


def plot_main_dlr_charts(results_list, static_amp: float = 850.0) -> None:
    plot_overview_10_cases(results_list)
    plot_zoom_last_7_days(results_list)
    plot_max_difference_and_wind(results_list)
    plot_ampacity_duration_curve(results_list, static_amp=static_amp)
