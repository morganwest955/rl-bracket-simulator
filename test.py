import itertools

# Define the list of teams
teams = ['Team 1', 'Team 2', 'Team 3', 'Team 4', 'Team 5', 'Team 6', 'Team 7', 'Team 8']

# Define the number of teams and the number of groups
num_teams = len(teams)
num_groups = 2
teams_per_group = num_teams // num_groups

# Generate all possible permutations of the matches within each group
group_matches = []
for i in range(num_groups):
    group_teams = teams[i*teams_per_group:(i+1)*teams_per_group]
    group_matches.append(list(itertools.permutations(group_teams, 2)))

# Generate all possible permutations of the matches within each stage of the tournament
stage_matches = []
for stage in [group_matches, list(itertools.permutations(teams, 2))]:
    stage_matches.append(list(itertools.product(*stage)))

# Generate all possible permutations of the tournament bracket
tournament_permutations = list(itertools.product(*stage_matches))

# Print the number of possible permutations
print(len(tournament_permutations))
