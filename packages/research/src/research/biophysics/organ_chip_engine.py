"""
Computational Engine for Phase 108: Organ-on-a-Chip Microphysiological Fluidic Dynamics.
Implements Navier-Stokes laminar flow modeling, wall shear stress (dyn/cm^2),
Reynolds number calculation, and endothelial barrier permeation dynamics (TEER).
"""
import math
from typing import List, Dict, Any, Optional

class MicrofluidicBiochipEngine:
    def compute_fluidic_parameters(
        self,
        flow_rate_ul_min: float,
        width_um: float,
        height_um: float,
        viscosity_cp: float = 1.0,
        density_g_cm3: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculates mean flow velocity (mm/s), hydraulic diameter, Reynolds number (Re),
        and wall shear stress tau (dyn/cm^2).
        tau = (6 * mu * Q) / (w * h^2)
        """
        # Convert Q: uL/min to mm^3/s -> 1 uL = 1 mm^3, /60 s
        q_mm3_s = flow_rate_ul_min / 60.0
        
        # Dimensions in mm
        w_mm = width_um / 1000.0
        h_mm = height_um / 1000.0
        area_mm2 = w_mm * h_mm
        
        # Mean velocity v = Q / A (mm/s)
        velocity_mm_s = q_mm3_s / max(1e-6, area_mm2)
        
        # Hydraulic diameter Dh = 4A / P = 2*w*h / (w + h) in mm
        dh_mm = (2.0 * w_mm * h_mm) / max(1e-6, (w_mm + h_mm))
        
        # Viscosity in Pa*s (1 cP = 1e-3 Pa*s = 1e-3 N*s/m^2)
        # Re = (rho * v * Dh) / mu
        # rho in kg/m^3 = 1000, v in m/s = velocity_mm_s * 1e-3, Dh in m = dh_mm * 1e-3
        reynolds = (1000.0 * (velocity_mm_s * 1e-3) * (dh_mm * 1e-3)) / max(1e-6, (viscosity_cp * 1e-3))
        
        # Wall Shear Stress tau = (6 * mu * Q) / (w * h^2) in dyn/cm^2 (or Pa)
        # In rectangular microchannels: tau (dyn/cm^2) = (6 * (viscosity_cp*0.01 Poise) * (Q in cm^3/s)) / (w_cm * h_cm^2)
        q_cm3_s = q_mm3_s * 1e-3
        w_cm = w_mm * 0.1
        h_cm = h_mm * 0.1
        mu_poise = viscosity_cp * 0.01
        
        tau_dyn_cm2 = (6.0 * mu_poise * q_cm3_s) / max(1e-9, (w_cm * (h_cm ** 2)))

        return {
            "flow_velocity_mm_s": round(velocity_mm_s, 3),
            "reynolds_number": round(reynolds, 4),
            "shear_stress_dyn_cm2": round(tau_dyn_cm2, 2)
        }

    def simulate_organ_chip(
        self,
        chip_name: str,
        organ_type: str = "BLOOD_BRAIN_BARRIER",
        flow_rate_ul_min: float = 30.0,
        viscosity_cp: float = 1.0,
        channel_length_mm: float = 20.0
    ) -> Dict[str, Any]:
        """
        Simulates two-channel microfluidic co-culture chip (Vascular apical + Interstitial basolateral).
        """
        # Channel 1: Vascular channel (apical)
        apical_params = self.compute_fluidic_parameters(
            flow_rate_ul_min=flow_rate_ul_min,
            width_um=500.0,
            height_um=150.0,
            viscosity_cp=viscosity_cp
        )
        
        # Channel 2: Interstitial channel (basolateral)
        basal_params = self.compute_fluidic_parameters(
            flow_rate_ul_min=flow_rate_ul_min * 0.2,
            width_um=500.0,
            height_um=150.0,
            viscosity_cp=viscosity_cp
        )

        channels = [
            {
                "channel_name": "Vascular_Apical_Channel",
                "width_um": 500.0,
                "height_um": 150.0,
                "length_mm": channel_length_mm,
                "flow_velocity_mm_s": apical_params["flow_velocity_mm_s"],
                "reynolds_number": apical_params["reynolds_number"]
            },
            {
                "channel_name": "Interstitial_Basolateral_Channel",
                "width_um": 500.0,
                "height_um": 150.0,
                "length_mm": channel_length_mm,
                "flow_velocity_mm_s": basal_params["flow_velocity_mm_s"],
                "reynolds_number": basal_params["reynolds_number"]
            }
        ]

        # Calculate TEER (Ohm*cm^2) based on physiological shear stress (optimal tau ~ 3-10 dyn/cm^2)
        tau = apical_params["shear_stress_dyn_cm2"]
        teer = round(1200.0 * (1.0 - math.exp(-max(0.1, tau) / 2.0)) + 300.0, 1)

        # Generate axial shear stress profiles along chip length
        shear_profiles = []
        n_points = 5
        for i in range(n_points):
            pos_mm = round((i / (n_points - 1)) * channel_length_mm, 1)
            permeation = round(max(2.0, 20.0 * math.exp(-teer / 800.0)), 2)
            tight_junc = round(min(99.0, 60.0 + (teer / 1500.0) * 38.0), 1)
            
            shear_profiles.append({
                "axial_position_mm": pos_mm,
                "wall_shear_stress": tau,
                "drug_permeation_pct": permeation,
                "tight_junction_expression": tight_junc
            })

        return {
            "chip_name": chip_name,
            "organ_type": organ_type,
            "fluid_viscosity_cp": viscosity_cp,
            "perfusion_flow_rate_ul_min": flow_rate_ul_min,
            "shear_stress_dyn_cm2": tau,
            "endothelial_barrier_integrity_teer": teer,
            "channels": channels,
            "shear_profiles": shear_profiles
        }
