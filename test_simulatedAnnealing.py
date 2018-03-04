import json
import random
from unittest import TestCase
import pandas as pd
import numpy as np

from permutations import Permutations
from simulated_annealing import SimulatedAnnealing

import matplotlib.pyplot as plt

class TestSimulatedAnnealing(TestCase):

    def setUp(self):
        profiles_df = pd.read_excel("profillängen.xlsx")
        self.dataset = profiles_df.sort_values(profiles_df.columns[0], ascending=False)
        self.normal_profile_selection = np.array([1000, 2000, 3000, 5000])
        self.cutting_tolerance = 10

        # check for permutation depth
        permutations = Permutations(profiles_df.copy(), self.normal_profile_selection, self.cutting_tolerance)
        self.combinations_df = permutations.get_combinations_dataframe(self.dataset)

        #create random solution
        #initial_solution = get_random_solution(self.dataset, self.combinations_df, self.normal_profile_selection)





    def test_simulate_annealing(self):
        sa_parameter = {
            "cycles": 100,
            "trails": 50,
            "P_start": 0.7,
            "P_end": 0.001
        }
        parameter = json.dumps(sa_parameter)

        self.simulated_annealing = SimulatedAnnealing(self.dataset, self.combinations_df, self.normal_profile_selection, parameter)
        self.simulated_annealing.start()

        best_costs = self.simulated_annealing.best_results_list

        best_scrap_list = []
        for profile_dict in best_costs:
            scrap_sum = 0
            for uuid, raw_profile in profile_dict.items():
                scrap_sum += raw_profile.scrap

            best_scrap_list.append(scrap_sum)

        plt.plot(best_scrap_list)
        plt.show()



    def test_random_solution_generation(self):

        sa_parameter = {
            "cycles": 100,
            "trails": 50,
            "P_start": 0.7,
            "P_end":0.001
        }
        parameter = json.dumps(sa_parameter)

        self.simulated_annealing = SimulatedAnnealing(self.dataset, self.combinations_df, parameter)
        dict = self.simulated_annealing.get_random_solution(self.dataset, self.combinations_df, self.normal_profile_selection)
        print(dict)
        W
        #check if all id's are present

        #check if selected combinations fit in the corresponding raw profile