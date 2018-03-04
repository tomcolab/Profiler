import json
import math
import random
import numpy as np
import uuid
from RawProfile import RawProfile


class SimulatedAnnealing:
    #TODO: How to load dataset, permutations, cutting_tolerance and raw profile configuration?
    def __init__(self, dataset, combinations_df, normal_profile_selection, parameter):
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
        self.combinations_df = combinations_df
        self.normal_profile_selection = normal_profile_selection

        self.raw_profile_dict = self.get_random_solution(self.dataset,
                                                         self.combinations_df,
                                                         self.normal_profile_selection)
        self.initial_costs = self.__get_costs(self.raw_profile_dict)

        self.best_results_list = []


    def get_random_solution(self, dataset_df, combinations_df, raw_profile_list):
        """
        This function returns a random solution by randomly choosing permutations and a random fitting raw profile.
        :param dataset_dict: the profiles to cut
        :param combinations_df: combinations of the profiles as dataframe
        :param raw_profile_list: the available raw profiles
        :return random profile cutting solution dictionary containing raw profiles as key and a list of cuts as values.
        """

        raw_profile_dict = {}
        is_profile_left = True
        while is_profile_left:
            raw_profile_id = uuid.uuid4().hex
            random_combination = combinations_df[combinations_df["used"] == 0].sample(n=1)
            id_list = self.__get_random_combination_ids(random_combination)
            raw_profile = self._get_random_leq_raw_profile(id_list, raw_profile_list, random_combination)

            #cut profile for each profile id
            for id in id_list:
                raw_profile.cut_profile(id[0], np.asscalar(dataset_df.loc[id].values))

            raw_profile.scrap_remainder()
            raw_profile_dict[raw_profile_id] = raw_profile
            self.__set_used(combinations_df, id_list)

            # check if there are combinations left
            if combinations_df["used"].all():
                is_profile_left = False

        return raw_profile_dict

    def start(self):
        self.accepted_solutions += 1.0
        current_temperature = self.initial_temperature
        delta_costs_avg = 0.0
        old_costs = self.initial_costs

        for cycle in range(self.cycles):
            print('Cycle: ' + str(cycle) + ' using Temperature: ' + str(current_temperature))
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
            print("Best Costs: ", old_costs)

            # lower the temperature for the next cycle
            current_temperature = self.fractional_reduction * current_temperature

    def __get_costs(self, raw_profile_dict):
        #return the sum of the scraps
        scrap_sum = 0
        for uuid, raw_profile in raw_profile_dict.items():
            scrap_sum += raw_profile.scrap
        return scrap_sum

    def __get_neighbour(self, raw_profile_dict):
        #get random profile from dict
        profile_dict = raw_profile_dict.copy()

        for i in range(2):
            random_raw_profile_key = random.choice(list(profile_dict))
            random_raw_profile = profile_dict[random_raw_profile_key]
            del profile_dict[random_raw_profile_key]

            #get all profile ids from cutlist
            id_list = []
            for cut in random_raw_profile.cut_list:
                id_list.append(cut.profile_id)


            #release corresponding used combinations from combinations_df
            for index, row in self.combinations_df.iterrows():
                row_id_list = []
                for column in row.iteritems():
                    if "Id" in column[0]:
                        row_id_list.append(column[1])

                    row_id_list = [value for value in row_id_list if not math.isnan(value)]
                self.normal_profile_selection
                if(set(row_id_list) <= set(id_list)):
                    self.combinations_df.at[index.tolist(), "used"] = 0

        random_solution_dict = self.get_random_solution(self.dataset, self.combinations_df, self.normal_profile_selection)
        profile_dict.update(random_solution_dict)
        return profile_dict

    def __is_worse_solution_accepted(self, delta_costs, delta_costs_avg, current_temperature):

        probability = math.exp(-delta_costs / (delta_costs_avg * current_temperature))
        if random.random() < probability:
            return True

        else:
            return False

    def __get_random_combination_ids(self, random_combination):
        # gather all profile ids from random combination
        id_list = []
        for column in random_combination.iteritems():
            if "Id" in column[0]:
                id_list.append(column[1].values)

        # cleanup id list
        id_list = [value for value in id_list if not math.isnan(value)]

        return id_list

    def __set_used(self, combinations_df, id_list):
        for id in id_list:
            # search all combinations using the id columns and set them to 1
            for depth in range(1, len(combinations_df.columns) - 1):
                drop_series = combinations_df.loc[combinations_df["Id" + str(depth)] == id[0]]
                combinations_df.at[drop_series.index.tolist(), "used"] = 1

    def _get_random_leq_raw_profile(self, raw_profile_id, raw_profile_list, random_combination):
        raw_profile_is_smaller = 1
        while (raw_profile_is_smaller):
            raw_profile = RawProfile(raw_profile_id, random.choice(raw_profile_list))
            if (raw_profile.length >= np.asscalar(random_combination["sum"].values)):
                raw_profile_is_smaller = 0

        return raw_profile