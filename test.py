# import itertools

# # Define the list of teams
# teams = ['Team 1', 'Team 2', 'Team 3', 'Team 4', 'Team 5', 'Team 6', 'Team 7', 'Team 8']

# # Define the number of teams and the number of groups
# num_teams = len(teams)
# num_groups = 2
# teams_per_group = num_teams // num_groups

# # Generate all possible permutations of the matches within each group
# group_matches = []
# for i in range(num_groups):
#     group_teams = teams[i*teams_per_group:(i+1)*teams_per_group]
#     group_matches.append(list(itertools.permutations(group_teams, 2)))

# # Generate all possible permutations of the matches within each stage of the tournament
# stage_matches = []
# for stage in [group_matches, list(itertools.permutations(teams, 2))]:
#     stage_matches.append(list(itertools.product(*stage)))

# # Generate all possible permutations of the tournament bracket
# tournament_permutations = list(itertools.product(*stage_matches))

# # Print the number of possible permutations
# print(len(tournament_permutations))

# import numpy as np

# Sample_array = np.array([[100, 101, 500, 104], [201, 202, 203, 204], [301, 300, 600, 307]])
# print("This is Sample 2D array :","\n", Sample_array)

# Index = 2

# Array_sort = Sample_array[Sample_array[:,Index].argsort()]

# print("The original array is:","\n","\n", Sample_array, "\n")
# print("The sorted array is:", "\n", "\n", Array_sort)



# import numpy as np

# outcomes = {'Bracket Final': [1, 2], 'Bracket Semifinal 1': [1, 2], 'Bracket Semifinal 2': [1, 2], 'Bracket Quarterfinal 1': [1, 2], 'Bracket Quarterfinal 2': [1, 2], 'Bracket Quarterfinal 3': [1, 2], 'Bracket Quarterfinal 4': [1, 2], 'Bracket Round 1 1': [1, 2], 'Bracket Round 1 2': [1, 2], 'Bracket Round 1 3': [1, 2], 'Bracket Round 1 4': [1, 2], 'Group A': (1, 2, 3, 4), 'Group B': (1, 2, 3, 4), 'Group C': (1, 2, 3, 4), 'Group D': (1, 2, 3, 4)}

# # Create an array to hold the number of outcomes for each node
# num_outcomes = np.zeros(len(outcomes))

# # Loop over the nodes and calculate the number of outcomes for each one
# for i, node in enumerate(outcomes):
#     if isinstance(outcomes[node], tuple):
#         num_outcomes[i] = len(outcomes[node]) ** 4
#     else:
#         num_outcomes[i] = len(outcomes[node])

# # Calculate the total number of scenarios
# total_scenarios = np.prod(num_outcomes)

# print(total_scenarios)

# # 8,796,093,022,208



from dataclasses import dataclass, field, fields
import json
import itertools
import math

@dataclass
class Team:
    name: str
    startingPoints: int
    seed: int
    nonQualPlacements: list = field(default_factory=list)
    qualificationScenarios: list = field(default_factory=list)
    tiebreakerScenarios: list = field(default_factory=list)
    complexScenarios: list = field(default_factory=list)
    complexQualScenarios: list = field(default_factory=list)

def getTeamList(teamJson):
    teamData = json.load(open(teamJson))
    teamList = []
    for team in teamData:
        teamList.append(Team(team, teamData[team]["Points"], teamData[team]["Seed"]))
        # print(teamData[team])
    return teamList

simTeamList = getTeamList("rlcaInvitationalNARosters.json")

n = len(simTeamList)
num_permutations = math.factorial(n) // math.factorial(n-n)
print(num_permutations)

# for i, scenario in enumerate(itertools.permutations(simTeamList)):
#     for item in scenario:
#         print(item)
#     print("--------------")
#     if i > 4: exit(0)

# 20,922,789,888,000