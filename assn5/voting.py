
import numpy
import copy

CAND = 0  # subscript of list which represents the candidate
SCORE = 1  # subscript of list which represents the score of the candidate
PLACE = 2  # subscript of list which represents the ranking, lowest is best

def print_connections(c, voters, candidates):
    print("CONNECTIONS")
    for i in range(voters):
        print(f"Voter {i+1:2d}:", end=" ")
        for j in range(voters):
            print(c[i][j], end=" ")
        print()
    print()

def print_rankings(r, voters, candidates, ordered):
    print("CANDIDATE Rankings")
    for i in range(voters):
        print(f"Voter {i+1:2d}:", end=" ")
        for j in range(candidates):
            print(r[i][j], end='')
        print(" ORDER ", ordered[i])
    print()


def create_voting(voters, candidates):
    connections = [[0 for _ in range(voters)] for _ in range(voters)]
    ordered = [[] for _ in range(voters)]
    numpy.random.seed(1052)
    
    for i in range(voters):
        conn = round(numpy.random.uniform(0, voters / 2))  # random number of connections
        for _ in range(conn):
            connectTo = numpy.random.randint(0, voters)
            if connectTo != i:
                connections[i][connectTo] = 1
            
    print_connections(connections, voters, candidates)

    candidateRanking = [[list() for _ in range(candidates)] for _ in range(voters)]
    for i in range(voters):
        for j in range(candidates):
            candidateRanking[i][j] = [j + 1, round(numpy.random.uniform(0, 100)) / 10, 0]
        
        sorted_candidates = sorted(candidateRanking[i], reverse=True, key=lambda v: v[SCORE])
        ordered[i] = [sorted_candidates[k][CAND] for k in range(candidates)]
        for v in range(candidates):
            candidate = sorted_candidates[v][CAND] - 1  # candidate index
            candidateRanking[i][candidate][PLACE] = v + 1
            
    print_rankings(candidateRanking, voters, candidates, ordered)
    
    return candidateRanking, ordered, connections


def ranked_choice_voting(candidateRanking, ordered, voters, candidates):
    print("PERFORMING RANKED CHOICE VOTING")
    remaining_candidates = set(range(1, candidates + 1))
    
    while len(remaining_candidates) > 1:
        first_choice_counts = {cand: 0 for cand in remaining_candidates}
        last_choice_counts = {cand: 0 for cand in remaining_candidates}
        
        for i in range(voters):
            for rank, candidate in enumerate(ordered[i]):
                if candidate in remaining_candidates:
                    if rank == 0:  # First choice
                        first_choice_counts[candidate] += 1
                    if rank == len(ordered[i]) - 1:  # Last choice
                        last_choice_counts[candidate] += 1
                    break
        
        min_first_choice = min(first_choice_counts.values())
        min_candidates = [cand for cand, count in first_choice_counts.items() if count == min_first_choice]
        
        if len(min_candidates) > 1:
            print(f"Tie detected among candidates {min_candidates} with {min_first_choice} first-choice votes each.")
            tie_breaker = sorted(min_candidates, key=lambda cand: -last_choice_counts[cand])
            to_eliminate = tie_breaker[0]
            remaining_candidates.remove(to_eliminate)
            print(f"Breaking the tie by eliminating candidate {to_eliminate} with the most last-choice votes.")
        else:
            to_eliminate = min_candidates[0]
            remaining_candidates.remove(to_eliminate)
            print(f"Eliminating candidate {to_eliminate} with {first_choice_counts[to_eliminate]} first-choice votes.")
        
        # Update each voter's preference list to remove the eliminated candidate
        for i in range(voters):
            ordered[i] = [cand for cand in ordered[i] if cand != to_eliminate]
    
    # Declare the last remaining candidate as the winner
    winner = remaining_candidates.pop()
    print(f"The winner is candidate {winner}!")
    return winner


def calculate_social_welfare(candidateRanking, ordered, voters, winner):
    total_cardinal_utility = 0
    total_ordinal_utility = 0

    print("\nCalculating Social Welfare for the Winner (Candidate {})".format(winner))
    print("Voter\tCardinal Utility\tOrdinal Utility")
    
    for i in range(voters):
        first_choice = ordered[i][0]  # The voter's first choice
        # Cardinal utility calculation
        first_choice_score = candidateRanking[i][first_choice - 1][SCORE]
        winner_score = candidateRanking[i][winner - 1][SCORE]
        cardinal_utility = abs(first_choice_score - winner_score)
        total_cardinal_utility += cardinal_utility
        
        # Ordinal utility calculation
        first_choice_rank = candidateRanking[i][first_choice - 1][PLACE]
        winner_rank = candidateRanking[i][winner - 1][PLACE]
        ordinal_utility = abs(first_choice_rank - winner_rank)
        total_ordinal_utility += ordinal_utility
        
        print(f"{i + 1}\t{cardinal_utility:.2f}\t\t\t{ordinal_utility}")
    
    print("\nTotal Cardinal Utility (Social Welfare): {:.2f}".format(total_cardinal_utility))
    print("Total Ordinal Utility (Social Welfare):", total_ordinal_utility,"\n")


def social_network_influence(voters, connections, ordered, candidateRanking):
    """
    This function calculates how many voters change their votes based on the influence of neighbors.
    If the voter’s current first choice is not the most popular choice among neighbors, 
    the voter considers switching to the neighbors' most popular choice.
    """
    updated_ordered = copy.deepcopy(ordered)
    changes = 0  # Track how many voters change their first choice

    for i in range(voters):
        neighbors = [j for j in range(voters) if connections[i][j] == 1]
        if not neighbors:
            continue
        
        neighbor_votes = {}
        for neighbor in neighbors:
            top_choice = updated_ordered[neighbor][0]
            neighbor_votes[top_choice] = neighbor_votes.get(top_choice, 0) + 1

        current_first_choice = updated_ordered[i][0]
        sorted_choices = sorted(neighbor_votes.items(), key=lambda x: -x[1])
        
        # Strategy based on the most popular neighbor choice 
        if sorted_choices and sorted_choices[0][0] != current_first_choice:
            most_popular_neighbor_choice = sorted_choices[0][0]
            updated_ordered[i] = [most_popular_neighbor_choice] + \
                                  [c for c in updated_ordered[i] if c != most_popular_neighbor_choice]
            changes += 1

    return updated_ordered, changes


def perform_social_voting_rounds(voters, connections, ordered, candidateRanking, max_rounds=100):
    print("SOCIAL NETWORK VOTING")
    rounds = 0
    while rounds < max_rounds:
        updated_ordered, changes = social_network_influence(voters, connections, ordered, candidateRanking)
        
        if changes == 0:  
            print(f"\nSystem stabilized after {rounds} rounds.")
            break

        rounds += 1
        ordered = updated_ordered
        print(f"Round {rounds}: {changes} voters changed their first choice.")
    
    if rounds == max_rounds:
        print("\nMax rounds reached without stabilization. The system did not converge.")

    return ordered, rounds


def calculate_plurality_winner(ordered, candidates):
    vote_counts = {c: 0 for c in range(1, candidates + 1)}
    for pref in ordered:
        vote_counts[pref[0]] += 1

    winner = max(vote_counts, key=vote_counts.get)
    print(f"\nPlurality Winner after Stabilization: Candidate {winner}")
    return winner


def calculate_borda_winner(candidateRanking, voters, candidates):
    # Initialize a dictionary to hold Borda scores for each candidate
    print("SIMULATION WITH BORDA")
    borda_scores = {c: 0 for c in range(1, candidates + 1)}

    for i in range(voters):
        for candidate, ranking in enumerate(candidateRanking[i]):
            cand_index = ranking[CAND]  # Candidate ID (1-based index)
            position = ranking[PLACE] - 1  # Borda points, zero-indexed rank
            borda_scores[cand_index] += (candidates - 1 - position)

    winner = max(borda_scores, key=borda_scores.get)
    
    print("\nBorda Scores:")
    for candidate, score in borda_scores.items():
        print(f"Candidate {candidate}: {score} points")

    print(f"\nBorda Winner: Candidate {winner}")
    return winner


def create_clustered_connections(voters, candidates, num_clusters=5):
    """
    Creates a clustered social network, where voters are divided into a set number of 
    clusters. Each voter is more likely to connect with others in their cluster, 
    simulating real-world social groups.
    """
    print("SIMULATION WITH CLUSTERED CONNECTIONS\n")
    connections = [[0 for _ in range(voters)] for _ in range(voters)]
    cluster_size = voters // num_clusters

    numpy.random.seed(1052)
    for cluster in range(num_clusters):
        cluster_start = cluster * cluster_size
        cluster_end = min((cluster + 1) * cluster_size, voters)

        # Connect within the cluster
        for i in range(cluster_start, cluster_end):
            num_connections = round(numpy.random.uniform(0, cluster_size / 2))
            for _ in range(num_connections):
                connect_to = numpy.random.randint(cluster_start, cluster_end)
                if connect_to != i:
                    connections[i][connect_to] = 1

        # Optional: Add a few random connections outside the cluster for realism
        for i in range(cluster_start, cluster_end):
            if numpy.random.random() < 0.2:  # 20% chance to connect outside the cluster
                connect_to = numpy.random.randint(0, voters)
                if connect_to != i:
                    connections[i][connect_to] = 1

    return connections


if __name__ == '__main__':
    voters = 20
    candidates = 5
    num_clusters = 5
    candidateRanking, ordered, connections = create_voting(voters, candidates)
   
    # Part 1 with out of Ranked Choice Voting winner and the social welfare for that outcome
    winner = ranked_choice_voting(copy.deepcopy(candidateRanking), copy.deepcopy(ordered), voters, candidates)
    calculate_social_welfare(candidateRanking, ordered, voters, winner)
    print("\n")

    # PART 2: Simulate social network model and strategic voting
    stabilized_ordered, total_rounds = perform_social_voting_rounds(voters, connections, copy.deepcopy(ordered), copy.deepcopy(candidateRanking))
    plurality_winner = calculate_plurality_winner(stabilized_ordered, candidates)
    calculate_social_welfare(candidateRanking, ordered, voters, plurality_winner)
    print("\n")

    # Extra: Calculate Borda winner
    borda_winner = calculate_borda_winner(candidateRanking, voters, candidates)
    calculate_social_welfare(candidateRanking, ordered, voters, borda_winner)
    print("\n")

    # Extra: Clustered Connection Simulation for Social Voting
    clustered_connections = create_clustered_connections(voters, candidates, num_clusters)
    clustered_stabilized_ordered, clustered_total_rounds = perform_social_voting_rounds(
        voters, clustered_connections, copy.deepcopy(ordered), copy.deepcopy(candidateRanking)
    )
    clustered_plurality_winner = calculate_plurality_winner(clustered_stabilized_ordered, candidates)
    calculate_social_welfare(candidateRanking, ordered, voters, clustered_plurality_winner)
