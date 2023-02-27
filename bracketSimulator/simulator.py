from dataclasses import dataclass, field, fields
from bracket import Bracket
import itertools
import pandas as pd
import json
import os
import numpy as np
from tqdm import tqdm
import asyncio
from tqdm.asyncio import tqdm_asyncio
import concurrent.futures
import cProfile

@dataclass
class QualificationScenario:
    teamName: str
    placement: int
    count: int
    conditionals: list = field(default_factory=list)

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

@dataclass
class Standing:
    position: str
    placement: str
    points: int

class SimulateAllScenarios:

    def __init__(self, bracketJson, teamJson, qualPlacement):
        simsRun = 0
        simTeamList = self.getTeamList(teamJson)
        qualDf = pd.DataFrame(columns = ['team', 'startingPoints', 'seed', 'totalQuals', 'qualChance', 'clinched', 'eliminated', 'complex'])
        pd.set_option('display.max_colwidth', None)
        bracket = Bracket(bracketJson, teamJson)
        qualDf = self.populateQualDataframe(qualDf, simTeamList)
        for i, scenario in tqdm(enumerate(self.getSimScenarios(bracket.nodeList))):
            # standingsDf = pd.DataFrame(columns = ['team', 'placement', 'totalPoints'])
            bracket.resetBracket(bracket.bracketRootNode)
            self.runBracketScenario(bracket, scenario)
            standingsArray = bracket.getBracketStandings()
            # standingsDf = bracket.getBracketStandings(standingsDf)
            # for j, row in standingsDf.iterrows():
            for j, row in enumerate(standingsArray):
                # if the team has qualified, add that scenario to the team object and increment totalQuals for that team in qualDf
                if j + 1 <= qualPlacement:
                    # [0] = team, [1] = placement, [2] = points
                    for team in simTeamList:
                        if team.name == row[0]:
                            placementExists = False
                            for qs in team.qualificationScenarios:
                                if qs.placement == row[1]:
                                    placementExists = True
                                    qs.count += 1
                                    break
                            if not placementExists:
                                team.qualificationScenarios.append(QualificationScenario(team.name, row[1], 1))
                            qualDf.loc[qualDf['team'] == team.name, 'totalQuals'] += 1
                            break
                # if the team has not qualified, add the placement to nonQualPlacements in the team object
                else:
                    for team in simTeamList:
                        if team.name == row[0]:
                            if row[1] not in team.nonQualPlacements:
                                team.nonQualPlacements.append(row[1])
                            break

            simsRun += 1
        qualDf = qualDf.assign(qualChance = lambda x: (x['totalQuals'] / simsRun))
        qualDf = self.populateSimpleScenarios(qualDf, simTeamList)
        # print(qualDf)
        cwd = os.getcwd()
        fileName = cwd + "/test.csv"
        qualDf.to_csv(fileName)
        print("sims run: ", simsRun)
        # for team in simTeamList:
        #     print("---- TEAM ----")
        #     print(team)

        print("--- INITIATING COMPLEX SCENARIO CALCULATIONS ---")
        
        # complex scenario run
        for i, scenario in tqdm(enumerate(self.getSimScenarios(bracket.nodeList))):
            # standingsDf = pd.DataFrame(columns = ['team', 'placement', 'totalPoints'])
            bracket.resetBracket(bracket.bracketRootNode)
            self.runBracketScenario(bracket, scenario)
            standingsArray = bracket.getBracketStandings()
            # standingsDf = bracket.getBracketStandings(standingsDf)
            # for j, row in standingsDf.iterrows():
            for j, row in enumerate(standingsArray):
                team = self.getTeamByName(simTeamList, row[0])
                if row[1] in team.complexScenarios and j + 1 <= qualPlacement:
                    scenarioExists = False
                    for cqs in team.complexQualScenarios:
                        if cqs.placement == row[1]:
                            scenarioExists = True
                            cqs.count += 1
                            # for k, opp in standingsDf.iterrows():
                            for opp in standingsArray:
                                if opp[0] != row[0]:
                                    scenarioInConditionals = False
                                    for cs in cqs.conditionals:
                                        if cs.teamName == opp[0] and cs.placement == opp[1]:
                                            scenarioInConditionals = True
                                            cs.count += 1
                                            break
                                    if not scenarioInConditionals:
                                        cqs.conditionals.append(QualificationScenario(opp[0], opp[1], 1))
                    if not scenarioExists:
                        team.complexQualScenarios.append(QualificationScenario(row[0], row[1], 1))
                        # for k, opp in standingsDf.iterrows():
                        for opp in standingsArray:
                            if opp[0] != row[0]:
                                team.complexQualScenarios[len(team.complexQualScenarios) - 1].conditionals.append(QualificationScenario(opp[0], opp[1], 1))
                # simTeamList = self.overwriteTeamInList(simTeamList, team)
        
        # print(simTeamList[4])
        for cqs in simTeamList[4].complexQualScenarios:
            print(cqs.placement, cqs.count)
            for cs in cqs.conditionals:
                print(cs)

    async def simulate_async(self, bracket, simTeamList, qualDf, qualPlacement, num_simulations):
        tasks = []
        for scenario in self.getSimScenarios(bracket.nodeList):
            tasks.append(asyncio.ensure_future(self.run_scenario(bracket, scenario, simTeamList, qualDf, qualPlacement)))
        pbar = tqdm_asyncio(asyncio.as_completed(tasks), total=len(tasks))
        for f in pbar:
            await f

    async def run_scenario(self, bracket, scenario, simTeamList, qualDf, qualPlacement):
        bracket.resetBracket(bracket.bracketRootNode)
        self.runBracketScenario(bracket, scenario)
        standingsArray = bracket.getBracketStandings()
        
        for j, row in enumerate(standingsArray):
            if j + 1 <= qualPlacement:
                for team in simTeamList:
                    if team.name == row[0]:
                        placementExists = False
                        for qs in team.qualificationScenarios:
                            if qs.placement == row[1]:
                                placementExists = True
                                qs.count += 1
                                break
                        if not placementExists:
                            team.qualificationScenarios.append(QualificationScenario(team.name, row[1], 1))
                        qualDf.loc[qualDf['team'] == team.name, 'totalQuals'] += 1
                        break
            else:
                for team in simTeamList:
                    if team.name == row[0]:
                        if row[1] not in team.nonQualPlacements:
                            team.nonQualPlacements.append(row[1])
                        break

    def generateComplexScenarioReport(self, team):
        for cqs in team.complexQualScenarios:
            return

    def getTeamByName(self, simTeamList, name):
        for team in simTeamList:
            if team.name == name:
                return team

    def overwriteTeamInList(self, simTeamList, team):
        for simTeam in simTeamList:
            if team.name == simTeam.name:
                simTeam = team
                print(simTeam)
        return simTeamList

    def populateQualDataframe(self, qualDf, teamList):
        for team in teamList:
            qualDf.loc[len(qualDf.index)] = [team.name, team.startingPoints, team.seed, 0, 0, "", "", ""]
        return qualDf

    def getTeamList(self, teamJson):
        teamData = json.load(open(teamJson))
        teamList = []
        for team in teamData:
            teamList.append(Team(team, teamData[team]["Points"], teamData[team]["Seed"]))
            # print(teamData[team])
        return teamList

    def populateSimpleScenarios(self, qualDf, simTeamList):
        for team in simTeamList:
            simpleQualPlacements = []
            complexQualPlacements = []
            simpleElimPlacements = []
            for qs in team.qualificationScenarios:
                if qs.placement in team.nonQualPlacements:
                    complexQualPlacements.append(qs.placement)
                else:
                    simpleQualPlacements.append(qs.placement)
            for placement in team.nonQualPlacements:
                if placement not in simpleElimPlacements and placement not in complexQualPlacements:
                    simpleElimPlacements.append(placement)
            qualDf.loc[qualDf['team'] == team.name, 'clinched'] = str(simpleQualPlacements)
            qualDf.loc[qualDf['team'] == team.name, 'eliminated'] = str(simpleElimPlacements)
            qualDf.loc[qualDf['team'] == team.name, 'complex'] = str(complexQualPlacements)
            team.complexScenarios = complexQualPlacements
        return qualDf

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


# sim = SimulateAllScenarios("../bracket.json", "../sampleTeams.json", 2)
# sim = SimulateAllScenarios("../rlcsInvitationalBracket.json", "../rlcaInvitationalNARosters.json", 5)

class SimulateStandings:

    def __init__(self, teamJson, standingsJson, qualPlacement):
        simsRun = 0
        simTeamList = self.getTeamList(teamJson)
        standingsObjectList = self.getStandings(standingsJson)
        qualDf = pd.DataFrame(columns = ['team', 'startingPoints', 'seed', 'totalQuals', 'qualChance', 'clinched', 'eliminated', 'complex'])
        qualDf = self.populateQualDataframe(qualDf, simTeamList)
        if len(simTeamList) != len(standingsObjectList):
            print("Team list needs to be the same length as standings list.")
            exit(1)
        for i, scenario in tqdm(enumerate(itertools.permutations(simTeamList))):
            standingsArray = self.buildStandingArray(scenario, standingsObjectList)
            for j, row in enumerate(standingsArray):
                # if the team has qualified, add that scenario to the team object and increment totalQuals for that team in qualDf
                if j + 1 <= qualPlacement:
                    # [0] = team, [1] = placement, [2] = points
                    for team in simTeamList:
                        if team.name == row[0]:
                            placementExists = False
                            for qs in team.qualificationScenarios:
                                if qs.placement == row[1]:
                                    placementExists = True
                                    qs.count += 1
                                    break
                            if not placementExists:
                                team.qualificationScenarios.append(QualificationScenario(team.name, row[1], 1))
                            qualDf.loc[qualDf['team'] == team.name, 'totalQuals'] += 1
                            break
                # if the team has not qualified, add the placement to nonQualPlacements in the team object
                else:
                    for team in simTeamList:
                        if team.name == row[0]:
                            if row[1] not in team.nonQualPlacements:
                                team.nonQualPlacements.append(row[1])
                            break

            simsRun += 1
        qualDf = qualDf.assign(qualChance = lambda x: (x['totalQuals'] / simsRun))
        qualDf = self.populateSimpleScenarios(qualDf, simTeamList)
        # print(qualDf)
        cwd = os.getcwd()
        fileName = cwd + "/test.csv"
        qualDf.to_csv(fileName)

    def buildStandingArray(self, scenario, standingsObjectList):
        # [0] = team, [1] = placement, [2] = points
        standingsList = []
        for i, team in enumerate(scenario):
            standingObject = self.getStandingsObjectFromPlacement(str(i + 1), standingsObjectList)
            standingsList.append([team.name, standingObject.placement, standingObject.points + team.startingPoints])
        standingsArray = np.array(standingsList)
        sortedStandingsArray = np.flipud(standingsArray[standingsArray[:, 2].astype(float).argsort()])
        return sortedStandingsArray
    
    def getStandingsObjectFromPlacement(self, position, standingsObjectList):
        for standing in standingsObjectList:
            if standing.position == position:
                return standing

    def getTeamList(self, teamJson):
        teamData = json.load(open(teamJson))
        teamList = []
        for team in teamData:
            teamList.append(Team(team, teamData[team]["Points"], teamData[team]["Seed"]))
            # print(teamData[team])
        return teamList

    def getStandings(self, standingsJson):
        standingsData = json.load(open(standingsJson))
        standings = []
        for standing in standingsData:
            standings.append(Standing(standing, standingsData[standing]["placement"], standingsData[standing]["points"]))
        return standings

    def populateQualDataframe(self, qualDf, teamList):
        for team in teamList:
            qualDf.loc[len(qualDf.index)] = [team.name, team.startingPoints, team.seed, 0, 0, "", "", ""]
        return qualDf

    def populateSimpleScenarios(self, qualDf, simTeamList):
        for team in simTeamList:
            simpleQualPlacements = []
            complexQualPlacements = []
            simpleElimPlacements = []
            for qs in team.qualificationScenarios:
                if qs.placement in team.nonQualPlacements:
                    complexQualPlacements.append(qs.placement)
                else:
                    simpleQualPlacements.append(qs.placement)
            for placement in team.nonQualPlacements:
                if placement not in simpleElimPlacements and placement not in complexQualPlacements:
                    simpleElimPlacements.append(placement)
            qualDf.loc[qualDf['team'] == team.name, 'clinched'] = str(simpleQualPlacements)
            qualDf.loc[qualDf['team'] == team.name, 'eliminated'] = str(simpleElimPlacements)
            qualDf.loc[qualDf['team'] == team.name, 'complex'] = str(complexQualPlacements)
            team.complexScenarios = complexQualPlacements
        return qualDf

# sim = SimulateStandings("../rlcaInvitationalNARosters.json", "../standings.json", 5)


bracketJson = "../bracket.json"
teamJson = "../sampleTeams.json"
qualPlacement = 2

# create an instance of the simulation class
# sim = SimulateAllScenarios(bracketJson, teamJson, qualPlacement)
sim = SimulateAllScenarios("../rlcsInvitationalBracket.json", "../rlcaInvitationalNARosters.json", 5)

# set the number of simulations to run in parallel
num_sims = 4

# create a thread pool to run the simulations asynchronously
with concurrent.futures.ThreadPoolExecutor(max_workers=num_sims) as executor:
    # create a list of tasks to run asynchronously
    tasks = [executor.submit(sim) for _ in range(num_sims)]

    # wait for all tasks to complete
    concurrent.futures.wait(tasks)

# # create an instance of the simulation class
# sim = SimulateAllScenarios(bracketJson, teamJson, qualPlacement)

# # run the simulation using cProfile to profile the code
# cProfile.runctx('sim', globals(), locals())