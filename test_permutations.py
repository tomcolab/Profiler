from unittest import TestCase
import numpy as np
import pandas as pd

from permutations import Permutations


class TestPermutations(TestCase):

    def setUp(self):
        normal_profile_selection = np.array([1000, 2000, 3000, 5000])
        cutting_tolerance = 10
        profiles_df = pd.read_excel("profillängen.xlsx")
        self.dataset = profiles_df.sort_values(profiles_df.columns[0], ascending=False)

        self.permutations = Permutations(self.dataset.copy(), normal_profile_selection, cutting_tolerance)
        self.depth = self.permutations.get_permutation_depth()
        self.permuted_dict = self.permutations.get_permuted_dataframes(self.dataset, self.depth)


    def test_permutation_depth_calculation(self):
        """
        Tests if the calculated permutation depth is correct for the given dataset.
        """
        self.assertEqual(5, self.depth)

    def test_permuted_dataframes_sums(self):
        """
        Tests if the dictionary, containing permuted dataframes for every permutation depth,
        contains only permutations which sum() is smaller than the largest raw profile.
        """
        for key in self.permuted_dict:
            self.assertFalse((self.permuted_dict[key]["sum"].values > 5000).all())

    def test_number_of_permutation_dataframes(self):
        permutation_df_counter = 0
        for _ in self.permuted_dict:
            permutation_df_counter+=1

        self.assertEqual(self.depth, permutation_df_counter)

    def test_permutation_dataframe_merging(self):
        permutations_df = self.permutations.merge_permutation_dataframes(self.permuted_dict)
        self.assertEqual(len(permutations_df.columns), self.depth + 2)

    def test_get_combinations(self):
        combinations_df = self.permutations.get_combinations_dataframe(self.dataset)
        self.assertEqual(len(combinations_df.columns), self.depth + 2)