
'''
Author : Adil Moujahid
Email : adil.mouja@gmail.com
Description: Simulations of Schelling's segregation model

Modified by Nathan Bal
'''

import matplotlib.pyplot as plt
import numpy as np
import itertools
import random
import copy


class Schelling:
    def __init__(self, width, height, empty_ratio, similarity_thresholds, n_iterations, colors=2):
        self.agents = None
        self.width = width
        self.height = height
        self.colors = colors
        self.empty_ratio = empty_ratio
        self.similarity_thresholds = similarity_thresholds
        self.n_iterations = n_iterations

    def populate(self):
        self.empty_houses = []
        self.agents = {}
        # print("Populate ",  self.width ,  self.height)
        self.all_houses = list(itertools.product(range(self.width), range(self.height)))
        # print(self.all_houses)
        random.shuffle(self.all_houses)


        self.n_empty = int(self.empty_ratio * len(self.all_houses))
        self.empty_houses = self.all_houses[:self.n_empty]
        #print(self.empty_houses)

        self.remaining_houses = self.all_houses[self.n_empty:]
        houses_by_color = [self.remaining_houses[i::self.colors] for i in range(self.colors)]
        # print("Houses by color ", houses_by_color[0])
        for i in range(self.colors):
            # create agents for each color
            dict2 = dict(zip(houses_by_color[i], [i + 1] * len(houses_by_color[i])))
            self.agents = {**self.agents, **dict2}
        # print("dictionary",self.agents)

    # A minimalistic function focused purely on moving agents until they are satisfied
    def update(self):
        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            n_changes = 0
            for agent in self.old_agents:
                if self.is_unsatisfied(agent[0], agent[1]):
                    agent_race = self.agents[agent]
                    empty_house = random.choice(self.empty_houses)
                    self.agents[empty_house] = agent_race
                    del self.agents[agent]
                    self.empty_houses.remove(empty_house)
                    self.empty_houses.append(agent)
                    n_changes += 1
            if i % 30 == 0:
                print(f"Iteration: {i+1} , Similarity Thresholds: {self.similarity_thresholds}. Number of changes: {n_changes}")
            #print 'Iteration: %d , Number of changes: %d' %(i+1, n_changes)
            if n_changes == 0:
                print(f"All agents are satisfied after {i+1} iterations!")
                break

    # Provides more feedback during the simulation, which is useful if you want to monitor
    # the simulation’s progress or understand how much movement is occurring.
    def move_locations(self):
        total_distance=0
        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            n_changes = 0
            for agent in self.old_agents:
                if self.is_unsatisfied(agent[0], agent[1]):
                    agent_color = self.agents[agent]
                    empty_house = random.choice(self.empty_houses)
                    self.agents[empty_house] = agent_color
                    del self.agents[agent]
                    self.empty_houses.remove(empty_house)
                    self.empty_houses.append(agent)
                    total_distance += abs(empty_house[0] - agent[0])+ abs(empty_house[1] - agent[1])
                    n_changes += 1
            if i%30==0:
                print(f"Iteration: {i+1} , Similarity Thresholds: {self.similarity_thresholds}. Number of changes: {n_changes} total distance: {total_distance}")
            if n_changes == 0:
                print(f"All agents are satisfied after {i+1} iterations! with total distance of {total_distance}")
                break

    def move_locations_with_early_stopping(self):
        total_distance = 0
        prev_n_changes = float('inf')  # Initialize with a large number
        min_changes_threshold = 1  # To track when no meaningful changes are happening
        change_threshold = 5

        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            n_changes = 0

            for agent in self.old_agents:
                if self.is_unsatisfied(agent[0], agent[1]):
                    agent_color = self.agents[agent]
                    empty_house = random.choice(self.empty_houses)
                    
                    self.agents[empty_house] = agent_color
                    del self.agents[agent]
                    
                    self.empty_houses.remove(empty_house)
                    self.empty_houses.append(agent)
                    
                    total_distance += abs(empty_house[0] - agent[0]) + abs(empty_house[1] - agent[1])
                    n_changes += 1

            if i % 3 == 0:
                print(f"EARLY Iteration: {i+1}, Similarity Thresholds: {self.similarity_thresholds}. "
                    f"Number of changes: {n_changes}, Total distance: {total_distance}")

            change_diff = abs(n_changes - prev_n_changes)
            if change_diff < change_threshold:
                print(f"Stopping early after {i+1} iterations due to less than {change_threshold} changes between iterations.")
                break

            prev_n_changes = n_changes

            if n_changes < min_changes_threshold:
                print(f"All agents are satisfied after {i+1} iterations!")
                break

    def move_and_swap_locations(self):
        total_distance = 0
        total_swaps = 0
        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            n_changes = 0
            unsatisfied_agents = [agent for agent in self.old_agents if self.is_unsatisfied(agent[0], agent[1])]
            random.shuffle(unsatisfied_agents)

            for agent1 in unsatisfied_agents:
                if agent1 not in self.agents:  # Check if agent1 still exists
                    continue
                
                agent1_color = self.agents[agent1]

                swapped = False
                for agent2 in unsatisfied_agents:
                    if agent1 == agent2 or agent2 not in self.agents:  # Skip if it's the same or agent2 doesn't exist anymore
                        continue

                    agent2_color = self.agents[agent2]

                    self.agents[agent1] = agent2_color
                    self.agents[agent2] = agent1_color

                    if not self.is_unsatisfied(agent1[0], agent1[1]) and not self.is_unsatisfied(agent2[0], agent2[1]):
                        n_changes += 1
                        total_swaps += 1
                        swapped = True
                        break  # Move to the next agent after successful swap
                    else:
                        self.agents[agent1] = agent1_color
                        self.agents[agent2] = agent2_color

                if not swapped and self.is_unsatisfied(agent1[0], agent1[1]):
                    if self.empty_houses:  # Check if there are empty houses available
                        empty_house = random.choice(self.empty_houses)
                        self.agents[empty_house] = agent1_color
                        del self.agents[agent1]
                        self.empty_houses.remove(empty_house)
                        self.empty_houses.append(agent1)
                        total_distance += abs(empty_house[0] - agent1[0]) + abs(empty_house[1] - agent1[1])
                        n_changes += 1

            if i % 30 == 0:
                print(f"Iteration: {i+1}, Similarity Thresholds: {self.similarity_thresholds}. Number of changes: {n_changes}, Total distance: {total_distance}, Number of swaps: {total_swaps}")

            if n_changes == 0:
                print(f"All agents are satisfied! with {i} iterations")
                break

    # agents prefer to move to locations that are closer to their current location, we need to introduce
    # a cost associated with the distance traveled during moves.
    def move_with_neighborhood_preference(self, neighborhood_radius=5):
        total_distance = 0
        total_cost = 0
        total_swaps = 0
        for i in range(self.n_iterations):
            self.old_agents = copy.deepcopy(self.agents)
            n_changes = 0
            unsatisfied_agents = [agent for agent in self.old_agents if self.is_unsatisfied(agent[0], agent[1])]
            random.shuffle(unsatisfied_agents)

            for agent1 in unsatisfied_agents:
                if agent1 not in self.agents:
                    continue

                agent1_color = self.agents[agent1]
                swapped = False

                nearby_empty_houses = [
                    empty_house for empty_house in self.empty_houses
                    if abs(empty_house[0] - agent1[0]) + abs(empty_house[1] - agent1[1]) <= neighborhood_radius
                ]

                for agent2 in unsatisfied_agents:
                    if agent1 == agent2 or agent2 not in self.agents:  # Skip if it's the same or agent2 doesn't exist anymore
                        continue

                    agent2_color = self.agents[agent2]

                    self.agents[agent1] = agent2_color
                    self.agents[agent2] = agent1_color

                    if not self.is_unsatisfied(agent1[0], agent1[1]) and not self.is_unsatisfied(agent2[0], agent2[1]):
                        n_changes += 1
                        total_swaps += 1
                        swapped = True
                        break 
                    else:
                        self.agents[agent1] = agent1_color
                        self.agents[agent2] = agent2_color

                if not swapped and self.is_unsatisfied(agent1[0], agent1[1]):
                    if nearby_empty_houses:
                        empty_house = random.choice(nearby_empty_houses)
                    else:
                        empty_house = random.choice(self.empty_houses)

                    move_distance = abs(empty_house[0] - agent1[0]) + abs(empty_house[1] - agent1[1])  # Manhattan distance
                    total_distance += move_distance
                    total_cost += move_distance

                    self.agents[empty_house] = agent1_color
                    del self.agents[agent1]
                    self.empty_houses.remove(empty_house)
                    self.empty_houses.append(agent1)
                    n_changes += 1

            if i % 30 == 0:
                print(f"Iteration: {i+1}, Similarity Thresholds: {self.similarity_thresholds}. Number of changes: {n_changes}, Total cost: {total_cost}, Number of swaps: {total_swaps}")

            if n_changes == 0:
                print(f"All agents are satisfied! with {i} iterations with total cost of {total_cost}")
                break

    def is_unsatisfied(self, x, y):

        myColor = self.agents[(x, y)]
        count_similar = 0
        count_different = 0

        if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
            if self.agents[(x - 1, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if y > 0 and (x, y - 1) not in self.empty_houses:
            if self.agents[(x, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
            if self.agents[(x + 1, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and (x - 1, y) not in self.empty_houses:
            if self.agents[(x - 1, y)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
            if self.agents[(x + 1, y)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
            if self.agents[(x - 1, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
            if self.agents[(x, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
            if self.agents[(x + 1, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1

        # Use color-specific similarity threshold if available
        threshold = self.similarity_thresholds.get(myColor, self.similarity_thresholds)  # Get specific or default
        if (count_similar + count_different) == 0:
            return False
        else:
            return float(count_similar) / (count_similar + count_different) < threshold

    # def move_to_empty(self, x, y):
    #     color = self.agents[(x, y)]
    #     empty_house = random.choice(self.empty_houses)
    #     self.updated_agents[empty_house] = color
    #     del self.updated_agents[(x, y)]
    #     self.empty_houses.remove(empty_house)
    #     self.empty_houses.append((x, y))

    def plot(self, title, file_name):
        fig, ax = plt.subplots()
        # If you want to run the simulation with more than 7 colors, you should set agent_colors accordingly
        agent_colors = {1: 'b', 2: 'r', 3: 'g', 4: 'c', 5: 'm', 6: 'y', 7: 'k'}
        marker_size = 150/self.width  # no logic here, I just played around with it
        for agent in self.agents:
            ax.scatter(agent[0] + 0.5, agent[1] + 0.5,s=marker_size, color=agent_colors[self.agents[agent]])

        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig(file_name)

    def calculate_similarity(self):
        similarity = []
        for agent in self.agents:
            count_similar = 0
            count_different = 0
            x = agent[0]
            y = agent[1]
            color = self.agents[(x, y)]
            if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
                if self.agents[(x - 1, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if y > 0 and (x, y - 1) not in self.empty_houses:
                if self.agents[(x, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
                if self.agents[(x + 1, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and (x - 1, y) not in self.empty_houses:
                if self.agents[(x - 1, y)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
                if self.agents[(x + 1, y)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
                if self.agents[(x - 1, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
                if self.agents[(x, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
                if self.agents[(x + 1, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            try:
                similarity.append(float(count_similar) / (count_similar + count_different))
            except:
                similarity.append(1)
        return sum(similarity) / len(similarity)
    
    def print_satisfied_percent_color(self):
        satisfied_count = {color: 0 for color in set(self.agents.values())}
        total_count = {color: 0 for color in set(self.agents.values())}

        # Loop through all agents to calculate satisfaction for each color
        for agent in self.agents:
            agent_color = self.agents[agent]
            total_count[agent_color] += 1

            if not self.is_unsatisfied(agent[0], agent[1]):  
                satisfied_count[agent_color] += 1

        # Calculate percentage satisfied per color
        for color in satisfied_count.keys():
            if total_count[color] > 0: 
                percentage_satisfied = (satisfied_count[color] / total_count[color]) * 100
                print(f"Color {color}: {percentage_satisfied:.2f}% of agents are satisfied")
            else:
                print(f"Color {color}: 0% satisfied (no agents of this color exist)")


def main():
    # #First Simulation
    schelling_1 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.3}, 200, 2)
    schelling_1.populate()
    schelling_1.move_locations()
    schelling_1.print_satisfied_percent_color()
    schelling_1.plot('Schelling Model 1 with 2 colors: Final State with Happiness Threshold 30%', 
    'schelling_30_final.png')

    # schelling_2 = Schelling(50, 50, 0.3, {1: 0.5, 2: 0.5}, 200, 2)
    # schelling_2.populate()
    # schelling_2.move_locations()
    # schelling_2.print_satisfied_percent_color()
    # schelling_2.plot('Schelling Model 2 with 2 colors: Final State with Happiness Threshold 50%',
    #                  'schelling_50_final.png')

    # schelling_3 = Schelling(50, 50, 0.3, {1: 0.7, 2: 0.7}, 200, 2)
    # schelling_3.populate()
    # schelling_3.move_locations()
    # schelling_3.print_satisfied_percent_color()
    # schelling_3.plot('Schelling Model 3 with 2 colors: Final State with Happiness Threshold 70%',
    #                  'schelling_70_final.png')
    
    # schelling_31 = Schelling(50, 50, 0.3, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_31.populate()
    # schelling_31.move_locations()
    # schelling_31.print_satisfied_percent_color()
    # schelling_31.plot('Schelling Model 3 with 2 colors: Final State with Happiness Threshold 80%',
    #                  'schelling_80_final.png')



    # #Second Simulation Measuring Segregation
    # similarity_threshold_ratio = {}
    # for i in np.arange(0, 0.7, 0.1):
    #     print(f"Running with Similarity Threshold: {i}")
    #     schelling = Schelling(50, 50, 0.3, i, 500, 2)
    #     schelling.populate()
    #     schelling.update()
    #     schelling.print_satisfied_percent_color()
    #     similarity_threshold_ratio[i] = schelling.calculate_similarity()
    #     print()

    # fig, ax = plt.subplots()
    # plt.plot(similarity_threshold_ratio.keys(), similarity_threshold_ratio.values(), 'ro')
    # ax.set_title('Similarity Threshold vs. Mean Similarity Ratio', fontsize=15, fontweight='bold')
    # ax.set_xlim([0, 1])
    # ax.set_ylim([0, 1.1])
    # ax.set_xlabel("Similarity Threshold")
    # ax.set_ylabel("Mean Similarity Ratio")
    # plt.savefig('schelling_segregationCompare.png')



    # Third Simulation: Visualizing final state with different thresholds for 2 colors
    # schelling_4 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.5}, 200, 2)
    # schelling_4.populate()
    # schelling_4.move_locations()
    # schelling_4.print_satisfied_percent_color()
    # schelling_4.plot('Schelling Model 4 with 2 colors: Final State with Thresholds 30% and 50%', 
    #                  'schelling_4_30_50_final.png')
    # print()

    # schelling_5 = Schelling(50, 50, 0.3, {1: 0.4, 2: 0.6}, 200, 2)
    # schelling_5.populate()
    # schelling_5.move_locations()
    # schelling_5.print_satisfied_percent_color()
    # schelling_5.plot('Schelling Model 5 with 2 colors: Final State with Thresholds 40% and 60%', 
    #                  'schelling_5_40_60_final.png')
    # print()
    
    # schelling_6 = Schelling(50, 50, 0.3, {1: 0.2, 2: 0.7}, 200, 2)
    # schelling_6.populate()
    # schelling_6.move_locations()
    # schelling_6.print_satisfied_percent_color()
    # schelling_6.plot('Schelling Model 6 with 2 colors: Final State with Thresholds 20% and 70%', 
    #                  'schelling_6_20_70_final.png')
    


    # Fourth Simulation: to test early stopping
    # schelling_7 = Schelling(50, 50, 0.3, {1: 0.4, 2: 0.6}, 200, 2)
    # schelling_7.populate()
    # schelling_7.move_locations_with_early_stopping()
    # schelling_7.print_satisfied_percent_color()
    # schelling_7.plot('Schelling Model 7 with Early Stopping and Thresholds 40% and 60%',
    #                  'schelling_40_60_early_stopping_final.png')

    # schelling_7 = Schelling(50, 50, 0.3, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_7.populate()
    # schelling_7.move_locations_with_early_stopping()
    # schelling_7.print_satisfied_percent_color()
    # schelling_7.plot('Schelling Model 7 with Early Stopping and Thresholds 40% and 60%',
    #                  'schelling_80_early_stopping_final.png')



    # Fifth Simulation: Swapping locations for improvement with other agents
    # schelling_8 = Schelling(50, 50, 0.3, {1: 0.4, 2: 0.6}, 200, 2)
    # schelling_8.populate()
    # schelling_8.move_and_swap_locations()
    # schelling_8.print_satisfied_percent_color()
    # schelling_8.plot('Schelling Swap Model 1 with 2 colors: Final State with Threshold 40% and 60%', 
    #                  'schelling_40_60_swap_final.png')

    # schelling_9 = Schelling(50, 50, 0.3, {1: 0.2, 2: 0.7}, 200, 2)
    # schelling_9.populate()
    # schelling_9.move_and_swap_locations()
    # schelling_9.print_satisfied_percent_color()
    # schelling_9.plot('Schelling Swap Model 2 with 2 colors: Final State with Threshold 20% and 70%',
    #                  'schelling_20_70_swap_final.png')

    # schelling_10 = Schelling(50, 50, 0.3, {1: 0.7, 2: 0.7}, 200, 2)
    # schelling_10.populate()
    # schelling_10.move_and_swap_locations()
    # schelling_10.print_satisfied_percent_color()
    # schelling_10.plot('Schelling Swap Model 3 with 2 colors: Final State with Threshold 70%',
    #                  'schelling_70_swap_final.png')
    
    # schelling_101 = Schelling(50, 50, 0.3, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_101.populate()
    # schelling_101.move_and_swap_locations()
    # schelling_101.print_satisfied_percent_color()
    # schelling_101.plot('Schelling Swap Model 3 with 2 colors: Final State with Threshold 80%',
    #                  'schelling_80_swap_final.png')



    # Sixth Simulation: agents prefer to move to locations that are closer to their current location.
    # schelling_8 = Schelling(50, 50, 0.3, {1: 0.3, 2: 0.3}, 200, 2)
    # schelling_8.populate()
    # schelling_8.move_with_neighborhood_preference()
    # schelling_8.print_satisfied_percent_color()
    # schelling_8.plot('Schelling Neighborhood Model 1 with 2 colors: Final State with Threshold 30%', 
    #                  'schelling_30_Neighborhood_final.png')

    # schelling_9 = Schelling(50, 50, 0.3, {1: 0.2, 2: 0.7}, 200, 2)
    # schelling_9.populate()
    # schelling_9.move_with_neighborhood_preference()
    # schelling_9.print_satisfied_percent_color()
    # schelling_9.plot('Schelling Neighborhood Model 2 with 2 colors: Final State with Threshold 50%',
    #                  'schelling_20_70_Neighborhood_final.png')

    # schelling_10 = Schelling(50, 50, 0.3, {1: 0.7, 2: 0.7}, 200, 2)
    # schelling_10.populate()
    # schelling_10.move_with_neighborhood_preference()
    # schelling_10.print_satisfied_percent_color()
    # schelling_10.plot('Schelling Neighborhood Model 3 with 2 colors: Final State with Threshold 70%',
    #                  'schelling_70_Neighborhood_final.png')
    
    # schelling_101 = Schelling(50, 50, 0.3, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_101.populate()
    # schelling_101.move_with_neighborhood_preference()
    # schelling_101.print_satisfied_percent_color()
    # schelling_101.plot('Schelling Neighborhood Model 3 with 2 colors: Final State with Threshold 80%',
    #                  'schelling_80_Neighborhood_final.png')
    


    # Seventh Simulation: Test the swapping and neighorhood algorithms with different percentage of emptiness
    # schelling_101 = Schelling(50, 50, 0.1, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_101.populate()
    # schelling_101.move_with_neighborhood_preference()
    # schelling_101.print_satisfied_percent_color()
    # schelling_101.plot('Schelling Neighborhood Model 3 with 2 colors: Final State with Threshold 80%',
    #                  'schelling_80_10_empty_Neighborhood_final.png')
    
    # schelling_101 = Schelling(50, 50, 0.1, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_101.populate()
    # schelling_101.move_locations()
    # schelling_101.print_satisfied_percent_color()
    # schelling_101.plot('Schelling Neighborhood Model 3 with 2 colors: Final State with Threshold 80%',
    #                  'schelling_80_10_empty_final.png')
    
    # schelling_101 = Schelling(50, 50, 0.5, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_101.populate()
    # schelling_101.move_and_swap_locations()
    # schelling_101.print_satisfied_percent_color()
    # schelling_101.plot('Schelling Neighborhood Model 3 with 2 colors: Final State with Threshold 80%',
    #                  'schelling_80_50_empty_Swap_final.png')
    
    # schelling_101 = Schelling(50, 50, 0.8, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_101.populate()
    # schelling_101.move_and_swap_locations()
    # schelling_101.print_satisfied_percent_color()
    # schelling_101.plot('Schelling Neighborhood Model 3 with 2 colors: Final State with Threshold 80%',
    #                  'schellin_80_80_empty_Swap_final.png')
    
    # schelling_101 = Schelling(50, 50, 0.8, {1: 0.8, 2: 0.8}, 200, 2)
    # schelling_101.populate()
    # schelling_101.move_with_neighborhood_preference()
    # schelling_101.print_satisfied_percent_color()
    # schelling_101.plot('Schelling Neighborhood Model 3 with 2 colors: Final State with Threshold 80%',
    #                  'schelling_80_80_empty_Neighborhood_final.png')

if __name__ == "__main__":
    main()