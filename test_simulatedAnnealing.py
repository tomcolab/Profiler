from unittest import TestCase
import pandas as pd
import numpy as np

from permutations import Permutations
from simulated_annealing import SimulatedAnnealing


class TestSimulatedAnnealing(TestCase):

    def setUp(self):
        profiles_df = pd.read_excel("profillängen.xlsx")
        self.dataset = profiles_df.sort_values(profiles_df.columns[0], ascending=False)
        self.normal_profile_selection = np.array([1000, 2000, 3000, 5000])
        self.cutting_tolerance = 10

        # check for permutation depth
        permutations = Permutations(profiles_df.copy(), self.normal_profile_selection, self.cutting_tolerance)
        permutation_depth = permutations.get_permutation_depth()

        # create permutations of values
        perm_df_dict = permutations.get_permuted_dataframes(profiles_df, permutation_depth)


s
    def test_simulate_annealing(self):
        cycles = 100
        trials = 50
        P_start = 0.7
        P_end = 0.001

        self.simulated_annealing = SimulatedAnnealing(self.dataset, cycles, trials, P_start, P_end)
