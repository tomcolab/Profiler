import math
import random


class SimulatedAnnealing:
    def __init__(self, dataset, cycles, trials_per_cycle, P_start, P_end):
        self.cycles = cycles
        self.trials_per_cycle = trials_per_cycle
        self.accepted_solutions = 0.0
        self.start_probability = P_start
        self.end_probability = P_end
        self.initial_temperature = -1.0 / math.log(self.start_probability)
        self.final_temperature = -1.0 / math.log(self.end_probability)
        self.fractional_reduction = (self.final_temperature / self.initial_temperature)**(1.0 / (cycles - 1.0))

        # set initial dataset
        self.original_dataset = dataset
        self.dataset = self.original_dataset
        # calculate initial costs
        self.initial_costs = self.__get_costs(dataset)

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
        pass

    def __get_neighbour(self):
        pass

    def __is_worse_solution_accepted(self, delta_costs, delta_costs_avg, current_temperature):

        probability = math.exp(-delta_costs / (delta_costs_avg * current_temperature))
        if random.random() < probability:
            return True

        else:
            return False
