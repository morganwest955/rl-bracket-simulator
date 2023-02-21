from dataclasses import dataclass, field, fields
from bracket import Bracket
import itertools
import pandas as pd
import json

#TODO: fix bug incrementing a team's totalQuals in qualDf

@dataclass
class QualificationScenario:
    teamName: str
    placement: int
    count: int
    conditional: list = field(default_factory=list)

@dataclass
class Team:
    name: str
    startingPoints: int
    chanceToQualify: float = 0.0
    nonQualPlacements: list = field(default_factory=list)
    qualificationScenarios: list = field(default_factory=list)
    tiebreakerScenarios: list = field(default_factory=list)

class SimulateAllScenarios:

    def __init__(self, bracketJson, teamJson, qualPlacement):
        simsRun = 0
        simTeamList = self.getTeamList(teamJson)
        qualDf = pd.DataFrame(columns = ['team', 'startingPoints', 'totalQuals', 'qualChance'])
        bracket = Bracket(bracketJson, teamJson)
        qualDf = self.populateQualDataframe(qualDf, bracket.teamList)
        for i, scenario in enumerate(self.getSimScenarios(bracket.nodeList)):
            standingsDf = pd.DataFrame(columns = ['team', 'placement', 'totalPoints'])
            bracket.resetBracket(bracket.bracketRootNode)
            self.runBracketScenario(bracket, scenario)
            standingsDf = bracket.getBracketStandings(standingsDf)
            if i == 3: print(standingsDf)
            for j, row in standingsDf.iterrows():
                # if the team has qualified, add that scenario to the team object and increment totalQuals for that team in qualDf
                if j + 1 <= qualPlacement:
                    for team in simTeamList:
                        if team.name == row["team"]:
                            placementExists = False
                            for qs in team.qualificationScenarios:
                                if qs.placement == row["placement"]:
                                    placementExists = True
                                    qs.count += 1
                                    break
                            if not placementExists:
                                team.qualificationScenarios.append(QualificationScenario(team.name, row["placement"], 1))
                            qualDf.loc[qualDf['team'] == team.name, 'totalQuals'] += 1
                            break
                # if the team has not qualified, add the placement to nonQualPlacements in the team object
                else:
                    for team in simTeamList:
                        if team.name == row["team"]:
                            if row["placement"] not in team.nonQualPlacements:
                                team.nonQualPlacements.append(row["placement"])
                            break

            simsRun += 1
        print(qualDf)
        print("sims run: ", simsRun)
        print(simTeamList[0])

    def populateQualDataframe(self, qualDf, teamList):
        for team in teamList:
            qualDf.loc[len(qualDf.index)] = [team.name, team.points, 0, 0]
        return qualDf

    def getTeamList(self, teamJson):
        teamData = json.load(open(teamJson))
        teamList = []
        for team in teamData:
            teamList.append(Team(team, teamData[team]["Points"]))
        return teamList

    # Get every possible full bracket scenario
    # YIELD example: {'Bracket Final': [2, 1], 'Bracket Semifinal 1': [2, 1], 'Bracket Semifinal 2': [2, 1], 'Group A': (4, 3, 2, 1), 'Group B': (4, 3, 2, 1)}
    ### Co-written by ChatGPT
    def getSimScenarios(self, nodeList):
        # Find all nodes that have possible outcomes
        nodes = [node for node in nodeList if node.getPossibleOutcomes()]

        # Create a dictionary that maps each node name to its possible outcomes
        outcomes = {node.name: node.getPossibleOutcomes() for node in nodes}

        # Generate all possible permutations of outcomes using itertools.product
        permutations = itertools.product(*outcomes.values())

        # Iterate over the permutations and yield a dictionary for each one
        for p in permutations:
            scenario = dict(zip(outcomes.keys(), p))
            yield scenario

    def runBracketScenario(self, bracket, scenario):
        for key in reversed(scenario.keys()):
            node = bracket.findNodeFromRoot(bracket.bracketRootNode, key)
            if "Bracket" in node.name:
                node.setSeries()
            node.setResults(scenario[key])
        return


sim = SimulateAllScenarios("../bracket.json", "../sampleTeams.json", 5)
