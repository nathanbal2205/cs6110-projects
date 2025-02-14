import random
import copy

class NormalFormGame:
    def __init__(self, num_row_actions, num_col_actions, row_rewards, col_rewards):
        self.num_row_actions = num_row_actions
        self.num_col_actions = num_col_actions
        self.row_rewards = row_rewards  # 2D list for row player rewards
        self.col_rewards = col_rewards  # 2D list for column player rewards

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as f:
            actions_line = f.readline().strip()
            num_row_actions, num_col_actions = map(int, actions_line.split())
            
            row_rewards_line = f.readline().strip()
            row_rewards = list(map(int, row_rewards_line.split()))
            
            col_rewards_line = f.readline().strip()
            col_rewards = list(map(int, col_rewards_line.split()))

        if len(row_rewards) != num_row_actions * num_col_actions:
            raise ValueError("Row player rewards do not match the expected number of actions.")
        if len(col_rewards) != num_row_actions * num_col_actions:
            raise ValueError("Column player rewards do not match the expected number of actions.")

        row_rewards_matrix = [row_rewards[i * num_col_actions:(i + 1) * num_col_actions] for i in range(num_row_actions)]
        col_rewards_matrix = [col_rewards[i * num_col_actions:(i + 1) * num_col_actions] for i in range(num_row_actions)]

        return cls(num_row_actions, num_col_actions, row_rewards_matrix, col_rewards_matrix)
    
    def find_strongly_dominated_strategies(self):
        row_dominated = []
        col_dominated = []
        
        for r1 in range(self.num_row_actions):
            for r2 in range(self.num_row_actions):
                if r1 != r2:  # Compare only different strategies
                    if all(self.row_rewards[r2][c] > self.row_rewards[r1][c] for c in range(self.num_col_actions)):
                        if r1 not in row_dominated:  # Avoid duplicates
                            row_dominated.append(r1)

        for c1 in range(self.num_col_actions):
            for c2 in range(self.num_col_actions):
                if c1 != c2:  # Compare only different strategies
                    if all(self.col_rewards[r][c2] > self.col_rewards[r][c1] for r in range(self.num_row_actions)):
                        if c1 not in col_dominated:  # Avoid duplicates
                            col_dominated.append(c1)

        if not row_dominated:
            print("No strongly dominated strategies for Row Player.")
        else:
            print("Strongly Dominated Strategies for Row Player:", row_dominated)

        if not col_dominated:
            print("No strongly dominated strategies for Column Player.")
        else:
            print("Strongly Dominated Strategies for Column Player:", col_dominated)

    def is_weakly_dominated(self, player_rewards, strategy_idx, other_strategy_idx, opponent_actions):
        strictly_better_in_at_least_one = False

        for o in range(opponent_actions):
            if player_rewards[other_strategy_idx][o] < player_rewards[strategy_idx][o]:
                return False  # This strategy is not dominated in this column
            if player_rewards[other_strategy_idx][o] > player_rewards[strategy_idx][o]:
                strictly_better_in_at_least_one = True

        return strictly_better_in_at_least_one  # Strategy is weakly dominated if it's strictly better in at least one case

    def iteratively_remove_weakly_dominated_strategies(self):
        print("After Iteratively Removing Weakly Dominated Strategies:")

        local_row_rewards = copy.deepcopy(self.row_rewards)
        local_col_rewards = copy.deepcopy(self.col_rewards)
        local_num_row_actions = self.num_row_actions
        local_num_col_actions = self.num_col_actions

        while True:
            row_dominated = None
            col_dominated = None

            # Check for weakly dominated strategies for the row player
            row_dominated_found = False
            for r1 in range(local_num_row_actions):
                for r2 in range(local_num_row_actions):
                    if r1 != r2 and self.is_weakly_dominated(local_row_rewards, r1, r2, local_num_col_actions):
                        row_dominated = r1
                        row_dominated_found = True
                        break
                if row_dominated_found:
                    break

            # Remove the row player's weakly dominated strategy if found
            if row_dominated_found:
                print(f"Removing weakly dominated strategy {row_dominated} for Row Player.")
                local_row_rewards.pop(row_dominated)
                local_col_rewards.pop(row_dominated)
                local_num_row_actions -= 1
                continue 

            # Check for weakly dominated strategies for the column player
            col_dominated_found = False
            for c1 in range(local_num_col_actions):
                for c2 in range(local_num_col_actions):
                    if c1 != c2:
                        col_strategy_c1 = [local_col_rewards[r][c1] for r in range(local_num_row_actions)]
                        col_strategy_c2 = [local_col_rewards[r][c2] for r in range(local_num_row_actions)]

                        if self.is_weakly_dominated([col_strategy_c1, col_strategy_c2], 0, 1, local_num_row_actions):
                            col_dominated = c1
                            col_dominated_found = True
                            break
                if col_dominated_found:
                    break

            # Remove the column player's weakly dominated strategy if found
            if col_dominated_found:
                print(f"Removing weakly dominated strategy {col_dominated} for Column Player.")
                for row in local_row_rewards:
                    row.pop(col_dominated)
                for col in local_col_rewards:
                    col.pop(col_dominated)
                local_num_col_actions -= 1
                continue
            
            if not row_dominated_found and not col_dominated_found:
                break

        print("Remaining Row Player Rewards Matrix:")
        for row in local_row_rewards:
            print(row)
        print("Remaining Column Player Rewards Matrix:")
        for col in local_col_rewards:
            print(col)

    def find_pure_strategy_equilibria(self):
        equilibria = []

        for r in range(self.num_row_actions):
            for c in range(self.num_col_actions):
                # Check if row player is playing optimally for this column
                row_player_best_response = all(
                    self.row_rewards[r][c] >= self.row_rewards[r_other][c]
                    for r_other in range(self.num_row_actions)
                )

                # Check if column player is playing optimally for this row
                col_player_best_response = all(
                    self.col_rewards[r][c] >= self.col_rewards[r][c_other]
                    for c_other in range(self.num_col_actions)
                )

                # If both players are playing optimally, we have a Nash equilibrium
                if row_player_best_response and col_player_best_response:
                    equilibria.append((self.row_rewards[r][c], self.col_rewards[r][c]))

        if equilibria:
            print("Pure Strategy Nash Equilibria (Row Player, Column Player):", equilibria)
        else:
            print("No Pure Strategy Nash Equilibria found.")

    def find_pareto_optimal_solutions(self):
        pareto_optimal = []

        for r1 in range(self.num_row_actions):
            for c1 in range(self.num_col_actions):
                is_pareto_optimal = True
                for r2 in range(self.num_row_actions):
                    for c2 in range(self.num_col_actions):
                        # Check if (r2, c2) dominates (r1, c1)
                        if (self.row_rewards[r2][c2] >= self.row_rewards[r1][c1] and
                            self.col_rewards[r2][c2] >= self.col_rewards[r1][c1] and
                            (self.row_rewards[r2][c2] > self.row_rewards[r1][c1] or
                             self.col_rewards[r2][c2] > self.col_rewards[r1][c1])):
                            is_pareto_optimal = False
                            break
                    if not is_pareto_optimal:
                        break

                if is_pareto_optimal:
                    pareto_optimal.append((self.row_rewards[r1][c1], self.col_rewards[r1][c1]))

        if pareto_optimal:
            print("Pareto Optimal Solutions (Row Player Payoff, Column Player Payoff):", pareto_optimal)
        else:
            print("No Pareto Optimal Solutions found.")

    def find_minimax_strategy(self):
        row_max_regret = []
        for r in range(self.num_row_actions):
            max_regret = float('-inf')
            for c in range(self.num_col_actions):
                best_possible_payoff = max(self.row_rewards[r2][c] for r2 in range(self.num_row_actions))  # Best row reward for this column
                actual_payoff = self.row_rewards[r][c]
                regret = best_possible_payoff - actual_payoff
                max_regret = max(max_regret, regret)
            row_max_regret.append(max_regret)

        if all(r == row_max_regret[0] for r in row_max_regret):
            print(f"Row Player: All strategies have the same minimax regret: {row_max_regret[0]}. No single best option.")
        else:
            row_minimax_strategy = min(range(self.num_row_actions), key=lambda r: row_max_regret[r])
            print(f"Row Player's Minimax Strategy: {row_minimax_strategy} (Minimized Maximum Regret: {row_max_regret[row_minimax_strategy]})")

        # Calculate minimax strategy for the Column Player
        col_max_regret = []
        for c in range(self.num_col_actions):
            max_regret = float('-inf')
            for r in range(self.num_row_actions):
                best_possible_payoff = max(self.col_rewards[r][c2] for c2 in range(self.num_col_actions))  # Best column reward for this row
                actual_payoff = self.col_rewards[r][c]
                regret = best_possible_payoff - actual_payoff
                max_regret = max(max_regret, regret)
            col_max_regret.append(max_regret)

        if all(c == col_max_regret[0] for c in col_max_regret):
            print(f"Column Player: All strategies have the same minimax regret: {col_max_regret[0]}. No single best option.")
        else:
            col_minimax_strategy = min(range(self.num_col_actions), key=lambda c: col_max_regret[c])
            print(f"Column Player's Minimax Strategy: {col_minimax_strategy} (Minimized Maximum Regret: {col_max_regret[col_minimax_strategy]})")

    def find_maximin_strategy(self):
        row_minimums = [min(self.row_rewards[r]) for r in range(self.num_row_actions)] 
        row_maximin_value = max(row_minimums) 

        if all(value == row_minimums[0] for value in row_minimums):
            print(f"Row Player: All strategies have the same maximin value: {row_maximin_value}. No single best option.")
        else:
            row_maximin_strategy = row_minimums.index(row_maximin_value) 
            print(f"Row Player's Maximin Strategy: {row_maximin_strategy} (Maximum of Minimum Payoff: {row_maximin_value})")

        col_minimums = [min([self.col_rewards[r][c] for r in range(self.num_row_actions)]) for c in range(self.num_col_actions)]
        col_maximin_value = max(col_minimums) 

        if all(value == col_minimums[0] for value in col_minimums):
            print(f"Column Player: All strategies have the same maximin value: {col_maximin_value}. No single best option.")
        else:
            col_maximin_strategy = col_minimums.index(col_maximin_value) 
            print(f"Column Player's Maximin Strategy: {col_maximin_strategy} (Maximum of Minimum Payoff: {col_maximin_value})")

    def simulate_repeated_play(self, num_rounds, row_strategy, col_strategy):
        row_scores = 0
        col_scores = 0
        last_row_action = None 
        last_col_action = None 

        for round_num in range(num_rounds):
            row_action = row_strategy(self.num_row_actions, last_col_action) 
            col_action = col_strategy(self.num_col_actions, last_row_action) 

            row_scores += self.row_rewards[row_action][col_action]
            col_scores += self.col_rewards[row_action][col_action]

            last_row_action = row_action
            last_col_action = col_action

            if round_num % 10 == 0:
                print(f"Round {round_num + 1}: Row Player chooses {row_action}, Column Player chooses {col_action} -> "
                    f"Row Score: {self.row_rewards[row_action][col_action]}, Column Score: {self.col_rewards[row_action][col_action]}")

        print(f"\nTotal Row Player Score after {num_rounds} rounds: {row_scores}")
        print(f"Total Column Player Score after {num_rounds} rounds: {col_scores}")
    
    def display(self):
        print("Number of Row Actions:", self.num_row_actions)
        print("Number of Column Actions:", self.num_col_actions)
        print("Row Player Rewards Matrix:")
        for row in self.row_rewards:
            print(row)
        print("Column Player Rewards Matrix:")
        for row in self.col_rewards:
            print(row)

# Example strategies
def random_row_strategy(num_row_actions, round_num):
    return random.randint(0, num_row_actions - 1)  # Player 1 chooses randomly from available actions

def random_col_strategy(num_col_actions, last_action):
    return random.randint(0, num_col_actions - 1)  # Player 2 chooses randomly from available actions

def always_choose_first_row(num_row_actions, round_num):
    return 0  # Player 1 always chooses option 0

def always_choose_first_col(num_col_actions, last_action):
    return 0  # Player 2 always chooses option 0

def tit_for_tat(num_actions, last_action):
    if last_action is None or last_action >= num_actions:  # Check for valid last_action
        return 0 
    return last_action  # Mimic the last action of the row player

def always_choose_last_col(num_col_actions, round_num):
    return num_col_actions - 1

file_path = ['prog4A.txt', 'prog4B.txt', 'prog4C.txt']
game = NormalFormGame.from_file(file_path[2])

game.find_strongly_dominated_strategies()
print()
game.iteratively_remove_weakly_dominated_strategies()
print()
game.find_pure_strategy_equilibria()
print()
game.find_pareto_optimal_solutions()
print()
game.find_minimax_strategy()
print()
game.find_maximin_strategy()
print()
# print("Simulation Strategies with Row = Random and Col = Random:")
# game.simulate_repeated_play(num_rounds=100, row_strategy=random_row_strategy, col_strategy=random_col_strategy)

# print("\nSimulation Strategies with Row = Random and Col = Always Choose First:")
# game.simulate_repeated_play(num_rounds=100, row_strategy=random_row_strategy, col_strategy=always_choose_first_col)

# print("\nSimulation Strategies with Row = Random and Col = Always Choose Last:")
# game.simulate_repeated_play(num_rounds=100, row_strategy=random_row_strategy, col_strategy=always_choose_last_col)

# print("\nSimulation Strategies with Row = Random and Col = Tit for Tat:")
# game.simulate_repeated_play(num_rounds=100, row_strategy=random_row_strategy, col_strategy=tit_for_tat)

# print("\nSimulation Strategies with Row = Tit for Tat and Col = Always Choose Last:")
# game.simulate_repeated_play(num_rounds=100, row_strategy=tit_for_tat, col_strategy=always_choose_last_col)

# print("\nSimulation Strategies with Row = Tit for Tat and Col = Tit for Tat:")
# game.simulate_repeated_play(num_rounds=100, row_strategy=tit_for_tat, col_strategy=tit_for_tat)

# game.display()