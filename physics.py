"""
Physics functions for IEEE Std 738-2023 and the aging-enhanced DLR model.

The first section is the original IEEE calculation set used by compare_model.py.
The second section adds the aging functions used only by the main DLR pipeline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# =========================================================================
# IEEE 738-2023 ORIGINAL PHYSICS
# =========================================================================


@dataclass
class ConductorProperties:
    diameter_mm: float
    emissivity: float
    absorptivity: float
    heat_capacity: float
    resistance_ref_high: float
    resistance_ref_low: float
    T_ref_high: float
    T_ref_low: float

    @property
    def diameter_m(self) -> float:
        return self.diameter_mm / 1000.0

    @property
    def projected_area_per_length(self) -> float:
        return self.diameter_m

    def resistance_at(self, T_c: float) -> float:
        slope = (self.resistance_ref_high - self.resistance_ref_low) / (
            self.T_ref_high - self.T_ref_low
        )
        return slope * (T_c - self.T_ref_low) + self.resistance_ref_low


@dataclass
class WeatherConditions:
    ambient_temp_c: float
    wind_speed_m_s: float
    wind_angle_deg: float
    elevation_m: float
    latitude_deg: float
    day_of_year: int
    time_of_day_hours: float
    solar_coeffs: tuple[float, float, float, float, float, float, float]
    line_azimuth_deg: float


def mean_film_temperature(T_s: float, T_a: float) -> float:
    return 0.5 * (T_s + T_a)


def dynamic_viscosity(T_film: float, use_SI: bool = True) -> float:
    T_k = T_film + 273.0
    if use_SI:
        numerator = 1.458e-6 * (T_k ** 1.5)
        denominator = T_film + 383.4
    else:
        numerator = 9.806e-7 * (T_k ** 1.5)
        denominator = T_film + 383.4
    return numerator / denominator


def air_density(T_film: float, elevation_m: float, use_SI: bool = True) -> float:
    if use_SI:
        rho0 = 1.293 - 1.525e-4 * elevation_m + 6.379e-9 * (elevation_m ** 2)
        return rho0 / (1.0 + 0.00367 * T_film)
    else:
        elevation_ft = elevation_m * 3.28084
        rho0 = 0.080695 - 2.901e-6 * elevation_ft + 3.7e-11 * (elevation_ft ** 2)
        return rho0 / (1.0 + 0.00367 * T_film)


def thermal_conductivity_air(T_film: float, use_SI: bool = True) -> float:
    if use_SI:
        return 2.424e-2 + 7.477e-5 * T_film - 4.407e-9 * T_film ** 2
    return 7.388e-3 + 2.279e-5 * T_film - 1.343e-9 * T_film ** 2


def reynolds_number(diameter_m: float, rho_f: float, v_w: float, mu_f: float) -> float:
    return diameter_m * rho_f * v_w / mu_f


def hour_angle(time_of_day_hours: float) -> float:
    return (time_of_day_hours - 12.0) * 15.0


def solar_declination(day_of_year: int) -> float:
    return 23.45 * math.sin(math.radians((284.0 + day_of_year) / 365.0 * 360.0))


def solar_altitude(latitude_deg: float, declination_deg: float, hour_angle_deg: float) -> float:
    lat_rad = math.radians(latitude_deg)
    dec_rad = math.radians(declination_deg)
    omega_rad = math.radians(hour_angle_deg)
    value = math.cos(lat_rad) * math.cos(dec_rad) * math.cos(omega_rad) + math.sin(lat_rad) * math.sin(dec_rad)
    value = max(min(value, 1.0), -1.0)
    return math.degrees(math.asin(value))


def solar_azimuth(latitude_deg: float, declination_deg: float, hour_angle_deg: float) -> float:
    lat_rad = math.radians(latitude_deg)
    dec_rad = math.radians(declination_deg)
    omega_rad = math.radians(hour_angle_deg)

    numerator = math.sin(omega_rad)
    denominator = math.sin(lat_rad) * math.cos(omega_rad) - math.cos(lat_rad) * math.tan(dec_rad)

    if denominator == 0:
        chi_deg = 90.0 if numerator > 0 else -90.0
    else:
        chi_val = numerator / denominator
        chi_deg = math.degrees(math.atan(chi_val))

    if -180.0 <= hour_angle_deg < 0.0:
        C = 0.0 if chi_deg >= 0.0 else 180.0
    elif 0.0 <= hour_angle_deg < 180.0:
        C = 180.0 if chi_deg >= 0.0 else 360.0
    else:
        C = 0.0

    Z_c = C + chi_deg
    return Z_c % 360.0


def solar_intensity(H_c_deg: float, coeffs: tuple[float, float, float, float, float, float, float]) -> float:
    A, B, C, D, E, F, G = coeffs
    H = H_c_deg
    return A + B * H + C * (H ** 2) + D * (H ** 3) + E * (H ** 4) + F * (H ** 5) + G * (H ** 6)


def elevation_correction(elevation_m: float) -> float:
    return 1.0 + 1.148e-4 * elevation_m - 1.108e-8 * (elevation_m ** 2)


def wind_direction_factor(phi_deg: float) -> float:
    phi_rad = math.radians(phi_deg)
    return 1.194 - math.cos(phi_rad) + 0.194 * math.cos(2.0 * phi_rad) + 0.368 * math.sin(2.0 * phi_rad)


def convective_heat_loss(T_s: float, T_a: float, conductor: ConductorProperties, weather: WeatherConditions, use_SI: bool = True) -> float:
    T_film = mean_film_temperature(T_s, T_a)
    mu_f = dynamic_viscosity(T_film, use_SI=use_SI)
    rho_f = air_density(T_film, weather.elevation_m, use_SI=use_SI)
    k_f = thermal_conductivity_air(T_film, use_SI=use_SI)

    D0 = conductor.diameter_m
    delta_T = T_s - T_a

    if use_SI:
        q_cn = 3.645 * (rho_f ** 0.5) * (D0 ** 0.75) * (delta_T ** 1.25)
    else:
        q_cn = 1.825 * (rho_f ** 0.5) * (D0 ** 0.75) * (delta_T ** 1.25)

    q_c1 = 0.0
    q_c2 = 0.0
    if weather.wind_speed_m_s > 0.0:
        v_w = weather.wind_speed_m_s
        N_Re = reynolds_number(D0, rho_f, v_w, mu_f)
        K_angle = wind_direction_factor(weather.wind_angle_deg)
        q_c1 = K_angle * (1.01 + 1.35 * (N_Re ** 0.52)) * k_f * delta_T
        q_c2 = K_angle * 0.754 * (N_Re ** 0.6) * k_f * delta_T

    return max(q_cn, q_c1, q_c2)


def radiated_heat_loss(T_s: float, T_a: float, conductor: ConductorProperties, use_SI: bool = True) -> float:
    D0 = conductor.diameter_m
    epsilon = conductor.emissivity
    term_s = (T_s + 273.0) / 100.0
    term_a = (T_a + 273.0) / 100.0
    constant = 17.8 if use_SI else 1.656
    return constant * D0 * epsilon * (term_s ** 4 - term_a ** 4)


def solar_heat_gain(conductor: ConductorProperties, weather: WeatherConditions) -> float:
    omega_deg = hour_angle(weather.time_of_day_hours)
    decl_deg = solar_declination(weather.day_of_year)
    H_c_deg = solar_altitude(weather.latitude_deg, decl_deg, omega_deg)
    Z_c_deg = solar_azimuth(weather.latitude_deg, decl_deg, omega_deg)

    Q_s = solar_intensity(H_c_deg, weather.solar_coeffs)
    K_solar = elevation_correction(weather.elevation_m)
    Q_se = K_solar * Q_s

    theta_rad = math.acos(
        math.cos(math.radians(H_c_deg))
        * math.cos(math.radians(Z_c_deg - weather.line_azimuth_deg))
    )

    A_prime = conductor.projected_area_per_length
    qs = conductor.absorptivity * Q_se * math.sin(theta_rad) * A_prime
    return max(qs, 0.0)


def steady_state_current(T_c: float, conductor: ConductorProperties, weather: WeatherConditions) -> float:
    qc = convective_heat_loss(T_c, weather.ambient_temp_c, conductor, weather)
    qr = radiated_heat_loss(T_c, weather.ambient_temp_c, conductor)
    qs = solar_heat_gain(conductor, weather)
    R_T = conductor.resistance_at(T_c)
    numerator = qc + qr - qs
    if numerator <= 0.0 or R_T <= 0.0:
        return 0.0
    return math.sqrt(numerator / R_T)


def transient_temperature(current_profile: np.ndarray, initial_temp_c: float, conductor: ConductorProperties, weather: WeatherConditions, dt: float = 1.0) -> np.ndarray:
    n = len(current_profile)
    temps = np.zeros(n + 1)
    temps[0] = initial_temp_c
    mCp = conductor.heat_capacity
    for i in range(n):
        T_avg = temps[i]
        I = current_profile[i]
        R_T = conductor.resistance_at(T_avg)
        qc = convective_heat_loss(T_avg, weather.ambient_temp_c, conductor, weather)
        qr = radiated_heat_loss(T_avg, weather.ambient_temp_c, conductor)
        qs = solar_heat_gain(conductor, weather)

        dT_dt = (R_T * I ** 2 + qs - qc - qr) / mCp
        temps[i + 1] = T_avg + dT_dt * dt
    return temps


# =========================================================================
# AGING ENHANCEMENT USED BY THE MAIN DLR MODEL
# =========================================================================


def dynamic_emissivity(x_years: float) -> float:
    return 0.23 + (0.93 - 0.23) * (1.0 - math.exp(-0.159 * x_years))


def dynamic_absorptivity(x_years: float) -> float:
    val = 0.33 + (0.93 - 0.23) * (1.0 - math.exp(-0.159 * x_years))
    return min(val, 0.93)


def apply_aging_coefficients(conductor: ConductorProperties, x_years: float) -> ConductorProperties:
    conductor.emissivity = dynamic_emissivity(x_years)
    conductor.absorptivity = dynamic_absorptivity(x_years)
    return conductor
