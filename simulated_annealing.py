import json
import math
import random
import numpy as np


class SimulatedAnnealing:
    #TODO: How to load dataset, permutations, cutting_tolerance and raw profile configuration?
    def __init__(self, dataset, permutation_dict, parameter):
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
        self.permutation_dict = permutation_dict

        # set initial dataset
        self.original_dataset = dataset
        self.dataset = self.original_dataset
        # calculate initial costs
        self.initial_costs = self.__get_costs(dataset)

    def get_random_solution(self, dataset_dict, combinations_df, raw_profile_list):
        """
        This function returns a random solution by randomly choosing permutations and a random fitting raw profile.
        :param dataset_dict: the profiles to cut
        :param combinations_df: combinations of the profiles as dataframe
        :param raw_profile_list: the available raw profiles
        :return random profile cutting solution dictionary containing raw profiles as key and a list of cuts as values.
        """
        random_solution_dict = {}
        is_profile_left = True

        while is_profile_left:
            random_combination = combinations_df[combinations_df["used"] == 0].sample(n=1)
            # gather all profile ids from random combination
            id_list = []
            for column in random_combination.iteritems():
                if "Id" in column[0]:
                    id_list.append(column[1].values)

            #cleanup id list
            id_list = [value for value in id_list if not math.isnan(value)]

            for id in id_list:

                # search all combinations using the id columns and set them to 1
                for depth in range(1, len(combinations_df.columns) - 1):
                    drop_series = combinations_df.loc[combinations_df["Id" + str(depth)] == id[0]]  # TODO: comment this
                    combinations_df.at[drop_series.index.tolist(), "used"] = 1

            #select randomly a fitting raw profile and add to the combination
            self.__get_costs(random_combination)
            random_combination["raw length"] =

            random_solution_dict[np.asscalar(random_combination.index.values)] = random_combination
            # check if there are combinations left
            if combinations_df["used"].all():
                is_profile_left = False

            #FIXME: Refactor function using smaller units

        return random_solution_dict

    def simulate_annealing(self):
        self.accepted_solutions += 1.0
        current_temperature = self.initial_temperature
        delta_costs_avg = 0.0
        old_costs = self.initial_costs

        for cycle in range(self.cycles):
            print('Cycle: ' + str(cycle) + ' using Temperature: ' + str(current_temperature))
            for trial in self.trials_per_cycle:

                # generate random neighbour
                neighbour = self.__get_neighbour()

                # calculate new costs
                new_costs = self.__get_costs()

                delta_costs = abs(new_costs, old_costs)

                # compute acceptance probability when necessery
                if (new_costs > old_costs):
                    if cycle == 0 and trial == 0: delta_costs_avg = delta_costs
                    accept_worse_solution = self.__is_worse_solution_accepted
                else:
                    accept_worse_solution = True

                if accept_worse_solution:
                    # change new solution to current solutiion
                    self.dataset = neighbour

                    # increment accepted solutions:
                    self.accepted_solutions += 1

                # TODO: Why is this average needed? For probability computation?
                delta_costs_avg = (delta_costs_avg * (
                self.accepted_solutions - 1.0) + delta_costs) / self.accepted_solutions

            # record best value for this cycle

            # lower the temperature for the next cycle
            current_temperature = self.fractional_reduction * current_temperature

    def __get_costs(self, dataset):

        #The dataset should be a dict of profiles having a the permutation id as id and containing cuts as
        #list

        #get id lengths

        #sum up the lengths

    def __get_neighbour(self):
        pass

    def __is_worse_solution_accepted(self, delta_costs, delta_costs_avg, current_temperature):

        probability = math.exp(-delta_costs / (delta_costs_avg * current_temperature))
        if random.random() < probability:
            return True

        else:
            return False
