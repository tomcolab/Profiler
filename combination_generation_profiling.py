from pstats import Stats
from unittest import TestCase
import numpy as np
import pandas as pd

from permutations import Permutations
import cProfile


class ProfileCombinations(TestCase):

    def setUp(self):
        normal_profile_selection = np.array([1000, 2000, 3000, 5000])
        cutting_tolerance = 10
        profiles_df = pd.read_excel("offerte_lilo_1.xlsx")
        self.dataset = profiles_df.sort_values(profiles_df.columns[0], ascending=False)

        self.permutations = Permutations(self.dataset.copy(), normal_profile_selection, cutting_tolerance)
        #self.depth = self.permutations.get_permutation_depth()
        #self.permuted_dict = self.permutations.get_permuted_dataframes(self.dataset, self.depth)

    def test_profile_get_combination_depth(self):
        self.pr = cProfile.Profile()
        self.pr.enable()
        self.depth = self.permutations.get_permutation_depth()


        p = Stats(self.pr)
        p.strip_dirs()
        p.sort_stats('cumtime')
        p.print_stats()
        print
        "\n--->>>"

    def test_profile_combination_generator(self):
        self.pr = cProfile.Profile()
        self.pr.enable()
        self.depth = self.permutations.get_permutation_depth()
        self.combinations_df = self.permutations.get_combinations_dataframe(self.dataset)
        p = Stats(self.pr)
        p.strip_dirs()
        p.sort_stats('cumtime')
        p.print_stats()
        print
        "\n--->>>"


