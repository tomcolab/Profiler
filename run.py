import yaml
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List
from pathlib import Path

from simulated_annealing import SimulatedAnnealing
from RawProfile import RawProfile



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

def sum_of_scraps(cuttings: List[RawProfile]):
    scrap_sum = 0
    for raw_profile in cuttings:
        scrap_sum+= raw_profile.scrap
            
    return scrap_sum

def best_solution(best_costs):
    verschnitt = sum_of_scraps(best_costs[0])
    result = best_costs[0]
    for solution in best_costs:
        verschnitt_neu = sum_of_scraps(solution)
        if verschnitt_neu < verschnitt:
            verschnitt = verschnitt_neu
            result = solution
    return result

def bestellliste(yaml_config, result):
    bestellliste = {}
    for rohprofillänge in yaml_config["Rohprofile"]:
        bestellliste[rohprofillänge] = 0

    for raw_profile in result:
        bestellliste[raw_profile.length] =+ 1
        
    with open('bestellliste_rohprofile_in_mm.yaml', 'w') as file:  
        yaml.dump(bestellliste, file)

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
            "cycles": 100,
            "trails": 10,
            "P_start": 0.7,
            "P_end": 0.001
        }
    
    parameter = json.dumps(sa_parameter)

    simulated_annealing = SimulatedAnnealing(sorted_df, config.profile_lengths, config.cutting_tolerance_mm, parameter)
    simulated_annealing.start()

    best_costs = simulated_annealing.best_results_list
    
    result = best_solution(best_costs)
    bestellliste(yaml_config, result)
    
    # Vorbereitungsliste
    rohprofil_ids = {}
    for raw_profile in result:
        rohprofil_ids[raw_profile.id] = int(raw_profile.length)
        
    with open('rohprofil_labeling.yaml', 'w') as file:  
        yaml.dump(rohprofil_ids, file, default_flow_style=False, sort_keys=False)
    
    # create konfektionsliste
    cuts = []
    for raw_profile in result: 
        for cut in raw_profile.cut_list:
            cuts.append(cut)
            
    cuts.sort(key=lambda cut: cut.raw_profile_id, reverse=False)
        
    # combine ids 1-1 means profile-id 1 - cut 1
    konfektionsliste = {}
    for cut in cuts:
        id = str(cut.raw_profile_id) + "-" + str(cut.cut_id) + "-" + str(cut.profile_id)
        konfektionsliste[id]  = int(cut.length)
        
    # write them to yaml
            
    with open('konfektionsliste.yaml', 'w') as file:  
        yaml.dump(konfektionsliste, file)

if __name__ == "__main__":
    main()



