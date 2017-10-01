import itertools
import pandas as pd


class Permutations:
    def __init__(self, dataset, raw_profiles, cutting_tolerance):
        self.cutting_tolerance = cutting_tolerance
        self.dataset = dataset.sort_values(dataset.columns[0])
        self.raw_profiles = raw_profiles

    def get_permutation_depth(self):
        max_raw_profile_length = self.raw_profiles.max()
        permutation_depth = 1

        for length in self.dataset.values:
            diff = max_raw_profile_length - length
            if diff >= self.cutting_tolerance:
                max_raw_profile_length = diff
            else:
                break
            permutation_depth = permutation_depth + 1

        return permutation_depth

    def drop_from_permutation_dataframes(self, current_profile_id, permutations_dfs_dict):
        for key in permutations_dfs_dict:
            for depth in range(1, key + 1):
                drop_series = permutations_dfs_dict[key].loc[
                    permutations_dfs_dict[key]["Id" + str(depth)] == current_profile_id]
                permutations_dfs_dict[key] = permutations_dfs_dict[key].drop(drop_series.index)

        return permutations_dfs_dict

    def sums_of_permutations(self, permut_df, id_df):
        sum_dict = {}
        index = 0
        for tuple in permut_df.itertuples(index=False, name=None):
            sum_dict[index] = sum(tuple)
            index = index + 1

        sum_df = pd.DataFrame()
        sum_df = sum_df.from_dict(sum_dict)
        sum_df = sum_df.T
        sum_df.columns = ["sum"]
        sum_df = sum_df.join(id_df)
        sum_df = sum_df.sort_values("sum")
        return sum_df

    def get_permuted_dataframes(self, profiles_df, max_depth):
        out_dict = {}
        for depth in range(1, max_depth + 1):
            permut = self.get_permuted_values_df(profiles_df, depth)
            permut_ind = self.get_permuted_profile_ids_df(profiles_df, depth)
            permut_ind.columns = self.get_id_list(depth)
            sum_df = self.sums_of_permutations(permut, permut_ind)

            # delete permutations longer then longest raw profile
            sum_df = self.drop_to_long_permutations(sum_df)

            # add already used flag column
            sum_df["used"] = 0
            out_dict[depth] = sum_df

        return out_dict

    def get_permuted_values_df(self, profiles_df, depth):
        permut_list = list(itertools.permutations(profiles_df.values, depth))
        permut_df = pd.DataFrame(permut_list)
        return permut_df

    def get_permuted_profile_ids_df(self, profiles_df, depth):
        permut_list = list(itertools.permutations(profiles_df.index, depth))
        permut_df = pd.DataFrame(permut_list)
        return permut_df

    def get_id_list(self, depth):
        id_list = []
        for i in range(1, depth + 1):
            id_list.append("Id" + str(i))
        return id_list

    def drop_to_long_permutations(self, permutation_df):
        permutation_df = permutation_df.drop(permutation_df.where(permutation_df["sum"] > self.raw_profiles.max()))
        return permutation_df
