import json
import math
import random
import numpy as np
import pandas as pd
import uuid
from RawProfile import RawProfile
from typing import List


class SimulatedAnnealing:
    def __init__(self, dataset: pd.DataFrame, raw_profiles: np.ndarray, cutting_tolerance_mm: int, parameter: str):

        self.parameter = json.loads(parameter)

        self.cycles = self.parameter["cycles"]
        self.trials_per_cycle = self.parameter["trails"]
        self.accepted_solutions = 0.0
        self.start_probability = self.parameter["P_start"]
        self.end_probability = self.parameter["P_end"]
        self.initial_temperature = -1.0 / math.log(self.start_probability)
        self.final_temperature = -1.0 / math.log(self.end_probability)
        self.fractional_reduction = (self.final_temperature / self.initial_temperature)**(1.0 / (self.cycles - 1.0))

        # set initial dataset
        self.original_dataset = dataset
        self.dataset = dataset
        self.raw_profiles = raw_profiles
        self.cutting_tolerance_mm = cutting_tolerance_mm

        self.cuttings = self.__random_solution(self.dataset, self.raw_profiles)
        self.initial_costs = self.__get_costs(self.cuttings)

        self.best_results_list = []

    def start(self):
        self.accepted_solutions += 1.0
        current_temperature = self.initial_temperature
        delta_costs_avg = 0.0
        old_costs = self.initial_costs

        for cycle in range(self.cycles):
            print('Cycle: ' + str(cycle) + ' using Temperature: ' + str(current_temperature) + "Best Costs: " + str(old_costs))
            for trial in range(self.trials_per_cycle):

                neighbour = self.__get_neighbour(self.dataset, self.raw_profiles)
                new_costs = self.__get_costs(neighbour)
                delta_costs = abs(new_costs - old_costs)

        
                if (new_costs > old_costs):
                    if cycle == 0 and trial == 0: delta_costs_avg = delta_costs
                    accept_worse_solution = self.__is_worse_solution_accepted(delta_costs, delta_costs_avg, current_temperature)
                else:
                    accept_worse_solution = True


                if accept_worse_solution:
                    self.cuttings = neighbour
                    old_costs = new_costs
                    self.accepted_solutions += 1

                delta_costs_avg = (delta_costs_avg * (self.accepted_solutions - 1.0) + delta_costs) / self.accepted_solutions

            self.best_results_list.append(self.cuttings)

            current_temperature = self.__lower_temperature(current_temperature)

    def __lower_temperature(self, current_temperature):
        return self.fractional_reduction * current_temperature

    def __sum_of_scraps(self, cuttings: List[RawProfile]) -> float:
        scrap_sum = 0
        for raw_profile in cuttings:
            scrap_sum+= raw_profile.scrap
            
        return scrap_sum

    def __get_costs(self, cuttings):
        return self.__sum_of_scraps(cuttings) #TODO: use dependency injection

    def __get_neighbour(self, dataset: pd.DataFrame, raw_profiles: np.ndarray):
        return self.__random_solution(dataset, raw_profiles)

    def __is_worse_solution_accepted(self, delta_costs, delta_costs_avg, current_temperature):

        probability = math.exp(-delta_costs / (delta_costs_avg * current_temperature))
        if random.random() < probability:
            return True

        else:
            return False
        
    def __random_raw_profile(self, raw_profiles: np.ndarray) -> RawProfile: 
        profile = random.choice(raw_profiles)
        return RawProfile(uuid.uuid4().hex, profile)

    def __random_solution(self, dataset: pd.DataFrame, raw_profiles) -> List[RawProfile]:
        
        raw_profile = self.__random_raw_profile(raw_profiles)
                
        cuttings = []
        for id in range(dataset.size):
            profile_length = dataset['Profillängen'].loc[id]
            
            raw_profile_is_to_short = True
            while raw_profile_is_to_short:
                if raw_profile.remainder == profile_length:
                    raw_profile.cut(id, profile_length)
                    raw_profile_is_to_short = False
                
                elif raw_profile.remainder > profile_length + self.cutting_tolerance_mm:
                    raw_profile.cut(id, profile_length + self.cutting_tolerance_mm)
                    raw_profile_is_to_short = False
            
                elif raw_profile.is_raw() and (raw_profile.length < profile_length):
                    raw_profile = self.__random_raw_profile(raw_profiles)
                
                else:
                    raw_profile.scrap_remainder()    
                    cuttings.append(raw_profile)
                    raw_profile = self.__random_raw_profile(raw_profiles)
        
        
        raw_profile.scrap_remainder()
        cuttings.append(raw_profile)
        return cuttings