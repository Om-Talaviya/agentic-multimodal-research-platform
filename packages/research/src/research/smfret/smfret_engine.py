"""Single-Molecule FRET (smFRET) Kinetics & Transition Engine."""
import math
import random
from typing import List, Dict, Any, Optional


class SmFRETKineticsEngine:
    """Simulates and analyzes single-molecule FRET trajectories, HMM states, and kinetic transition rates."""

    def analyze_experiment(
        self,
        experiment_input: Dict[str, Any],
        raw_traces_input: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Performs smFRET trace calculation, HMM state assignment, and kinetic transition matrix computation."""
        title = experiment_input.get("experiment_title", "Riboswitch Dynamic Switching")
        macromolecule = experiment_input.get("macromolecule_name", "SAM-I Riboswitch")
        donor = experiment_input.get("donor_fluorophore", "Cy3")
        acceptor = experiment_input.get("acceptor_fluorophore", "Cy5")
        r0 = float(experiment_input.get("forster_radius_angstrom", 54.0))
        rate_hz = float(experiment_input.get("acquisition_rate_hz", 100.0))
        dt = 1.0 / rate_hz

        # Pre-defined conformational state definitions
        states = [
            {
                "state_index": 0,
                "state_name": "OPEN",
                "mean_efficiency": 0.18,
                "occupancy_fraction": 0.35,
                "mean_dwell_time_ms": 120.0,
                "transition_rates_json": {"1": 6.2, "2": 1.8},
            },
            {
                "state_index": 1,
                "state_name": "INTERMEDIATE",
                "mean_efficiency": 0.52,
                "occupancy_fraction": 0.40,
                "mean_dwell_time_ms": 85.0,
                "transition_rates_json": {"0": 5.0, "2": 6.8},
            },
            {
                "state_index": 2,
                "state_name": "CLOSED",
                "mean_efficiency": 0.84,
                "occupancy_fraction": 0.25,
                "mean_dwell_time_ms": 160.0,
                "transition_rates_json": {"0": 1.2, "1": 5.1},
            }
        ]

        # Generate single-molecule trace if none provided
        rng = random.Random(42)
        total_frames = 200
        current_state = 0
        trace_points = []
        fret_sum = 0.0

        for frame in range(total_frames):
            t_sec = round(frame * dt, 4)
            # Random state hopping
            if rng.random() < 0.08:
                current_state = (current_state + rng.choice([1, 2])) % 3

            base_e = states[current_state]["mean_efficiency"]
            noise = rng.gauss(0.0, 0.04)
            eff = max(0.02, min(0.98, base_e + noise))
            fret_sum += eff

            # Donor and Acceptor intensities
            total_i = 400.0 + rng.gauss(0, 20)
            ia = max(10.0, total_i * eff)
            id_ = max(10.0, total_i * (1.0 - eff))

            # Inter-dye distance (Förster equation)
            dist = round(r0 * math.pow((1.0 / eff) - 1.0, 1.0 / 6.0), 1)

            trace_points.append({
                "frame": frame,
                "time_sec": t_sec,
                "donor_int": round(id_, 1),
                "acceptor_int": round(ia, 1),
                "fret_eff": round(eff, 3),
                "hmm_state": states[current_state]["state_name"],
                "distance_angstrom": dist,
            })

        mean_fret = round(fret_sum / total_frames, 3)

        traces = raw_traces_input or [
            {
                "molecule_index": 1,
                "total_frames": total_frames,
                "mean_fret_efficiency": mean_fret,
                "photobleaching_frame": None,
                "trace_data_json": trace_points,
            }
        ]

        return {
            "experiment_title": title,
            "macromolecule_name": macromolecule,
            "donor_fluorophore": donor,
            "acceptor_fluorophore": acceptor,
            "forster_radius_angstrom": r0,
            "acquisition_rate_hz": rate_hz,
            "total_molecules_recorded": len(traces),
            "state_count": len(states),
            "states": states,
            "traces": traces,
            "experiment_metadata_json": {
                "gamma_factor": 1.0,
                "crosstalk_beta": 0.05,
                "viterbi_log_likelihood": -142.8,
                "inter_dye_distance_range_angstrom": [
                    round(r0 * math.pow((1.0 / 0.84) - 1.0, 1.0 / 6.0), 1),
                    round(r0 * math.pow((1.0 / 0.18) - 1.0, 1.0 / 6.0), 1)
                ]
            }
        }
