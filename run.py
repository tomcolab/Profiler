import yaml
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List
from pathlib import Path

from simulated_annealing import SimulatedAnnealing


@dataclass
class Config:
    profile_lengths: np.ndarray
    cutting_tolerance_mm: int
    input_filepath: Path
    output_filepath: Path
    

def load_and_sort(config):
    profile_df = pd.read_excel(config.input_filepath)
    profile_df = profile_df.sort_values(profile_df.columns[0], ascending=False)
    return profile_df


def main():
    with open('input_config.yml', 'r') as file:
        yaml_config = yaml.safe_load(file)
        
    config = Config(
        np.asarray(yaml_config["Rohprofile"]), 
        yaml_config['Schnitttoleranz'], 
        yaml_config['Pfad-Input-Profile-XLS'], 
        yaml_config['Pfad-Output-Bestellliste-XLS'])



    sorted_df = load_and_sort(config)
    
    sa_parameter = {
            "cycles": 1000,
            "trails": 10,
            "P_start": 0.7,
            "P_end": 0.001
        }
    
    parameter = json.dumps(sa_parameter)

    simulated_annealing = SimulatedAnnealing(sorted_df, config.profile_lengths, config.cutting_tolerance_mm, parameter)
    simulated_annealing.start()

    best_costs = simulated_annealing.best_results_list
    print(best_costs)
    
    # export to excel


if __name__ == "__main__":
    main()



