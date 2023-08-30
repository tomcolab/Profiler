import json
import math
import random
import numpy as np
import pandas as pd
import uuid
from RawProfile import RawProfile
from typing import List


class SimulatedAnnealing:
    #TODO: How to load dataset, permutations, cutting_tolerance and raw profile configuration?
    def __init__(self, dataset: pd.DataFrame, raw_profiles: np.ndarray, cutting_tolerance_mm: int, parameter: str):
        #SA configuration

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

        self.cuttings = self.random_solution(self.dataset, self.raw_profiles)
        self.initial_costs = self.__get_costs(self.cuttings)

        self.best_results_list = []


    def random_raw_profile(self, raw_profiles: np.ndarray) -> RawProfile: 
        profile = random.choice(raw_profiles)
        return RawProfile(uuid.uuid4().hex, raw_profiles)


    def random_solution(self, dataset: pd.DataFrame, raw_profiles) -> dict:
        
        raw_profile = self.random_raw_profile(raw_profiles)
                
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
            
                elif raw_profile.is_raw() and (raw_profile.length() < profile_length):
                    raw_profile = self.random_raw_profile(raw_profiles)
                
                else:
                    raw_profile.scrap_remainder()    
                    cuttings.append(raw_profile)
                    raw_profile = self.random_raw_profile(raw_profiles)
        
        
        raw_profile.scrap_remainder()
        cuttings.append(raw_profile)
        return cuttings
        

    def start(self):
        self.accepted_solutions += 1.0
        current_temperature = self.initial_temperature
        delta_costs_avg = 0.0
        old_costs = self.initial_costs

        for cycle in range(self.cycles):
            print('Cycle: ' + str(cycle) + ' using Temperature: ' + str(current_temperature) + "Best Costs: " + str(old_costs))
            for trial in range(self.trials_per_cycle):

                # generate random neighbour
                neighbour = self.__get_neighbour(self.raw_profile_dict)

                # calculate new costs
                new_costs = self.__get_costs(neighbour)
                delta_costs = abs(new_costs - old_costs)

                # compute acceptance probability when necessery
                if (new_costs > old_costs):
                    if cycle == 0 and trial == 0: delta_costs_avg = delta_costs
                    accept_worse_solution = self.__is_worse_solution_accepted(delta_costs, delta_costs_avg, current_temperature)
                else:
                    accept_worse_solution = True

                if accept_worse_solution:
                    self.raw_profile_dict = neighbour
                    old_costs = new_costs
                    self.accepted_solutions += 1

                # TODO: Why is this average needed? For probability computation?
                delta_costs_avg = (delta_costs_avg * (
                self.accepted_solutions - 1.0) + delta_costs) / self.accepted_solutions

            # record best value for this cycle
            self.best_results_list.append(self.raw_profile_dict)
            #print("Best Costs: ", old_costs)

            # lower the temperature for the next cycle
            current_temperature = self.fractional_reduction * current_temperature

    def __sum_of_scraps(self, cuttings: List[RawProfile]) -> float:
        scrap_sum = 0
        for raw_profile in cuttings:
            scrap_sum+= raw_profile.scrap
            
        return scrap_sum

    def __get_costs(self, cuttings):
        return self.__sum_of_scraps(cuttings) #TODO: use dependency injection


    def __get_neighbour(self, raw_profile_dict):
        #get random profile from dict
        profile_dict = raw_profile_dict.copy()

        dict_count = len(raw_profile_dict)
        id_list = []
        for i in range(int(dict_count/3)):
            random_raw_profile_key = random.choice(list(profile_dict))
            random_raw_profile = profile_dict[random_raw_profile_key]
            del profile_dict[random_raw_profile_key]

            #get all profile ids from cutlist

            for cut in random_raw_profile.cut_list:
                id_list.append(cut.profile_id)

            #release corresponding used combinations from combinations_df
            for index, row in self.combinations_df.iterrows():
                row_id_list = []
                for column in row.iteritems():
                    if "Id" in column[0]:
                        row_id_list.append(column[1])

                    row_id_list = [value for value in row_id_list if not math.isnan(value)]
                self.raw_profiles
                if(set(row_id_list) <= set(id_list)):
                    self.combinations_df.at[index.tolist(), "used"] = 0

        random_solution_dict = self.get_random_solution(self.dataset, self.combinations_df, self.raw_profiles)
        profile_dict.update(random_solution_dict)
        return profile_dict

    def __is_worse_solution_accepted(self, delta_costs, delta_costs_avg, current_temperature):

        probability = math.exp(-delta_costs / (delta_costs_avg * current_temperature))
        if random.random() < probability:
            return True

        else:
            return False


    def _get_random_leq_raw_profile(self, raw_profile_id, raw_profile_list, random_combination):
        raw_profile_is_smaller = 1
        while (raw_profile_is_smaller):
            raw_profile = RawProfile(raw_profile_id, random.choice(raw_profile_list))
            if (raw_profile.length >= np.ndarray.item(random_combination["sum"].values)):
                raw_profile_is_smaller = 0

        return raw_profile