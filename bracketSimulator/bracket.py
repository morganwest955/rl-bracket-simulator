from dataclasses import dataclass, field, fields
from typing import Optional
import json
import traceback
import itertools
import pandas as pd

#####
# Build the bracket for the simulation to run through
#####

# Class to store information for each player
@dataclass
class Player:
    name: str = ""
    def printClass(self):
        print("-- PLAYER --")
        for field in fields(self):
            if getattr(self, field.name) is not None and hasattr(getattr(self, field.name), 'printClass'):
                print(field.name, ": ")
                getattr(self, field.name).printClass()
            else:
                print(f"{field.name}: {getattr(self, field.name)}")
        print("-- END PLAYER --")

# Class to store information for each team
@dataclass
class Team:
    name: str
    players: field(default_factory=list)
    score: int = 0
    seed: int = 0
    points: int = 0
    gamesWon: int = 0
    gamesLost: int = 0
    goalsScored: int = 0
    goalsConceded: int = 0
    finishPlace: str = ""
    def printClass(self):
        print("---- TEAM ----")
        for field in fields(self):
            if getattr(self, field.name) is not None and hasattr(getattr(self, field.name), 'printClass'):
                print(field.name, ": ")
                getattr(self, field.name).printClass()
            else:
                print(f"{field.name}: {getattr(self, field.name)}")
        print("---- END TEAM ----")

# Class to store information for each series
@dataclass
class Series:
    team1: Team
    team2: Team
    bestOf: int
    team1Score: int = 0
    team2Score: int = 0
    winner: Team = None
    loser: Team = None

    # Write the results of the series to the participating teams.
    def writeResults(self, team1Score, team2Score):
        self.team1Score = team1Score
        self.team2Score = team2Score
        self.team1.gamesWon += team1Score
        self.team1.gamesLost += team2Score
        self.team2.gamesWon += team2Score
        self.team2.gamesLost += team1Score
        if team1Score > team2Score:
            self.winner = self.team1
            self.loser = self.team2 
        else:
            self.winner = self.team2 
            self.loser = self.team1
    def printClass(self):
        print("~~ SERIES ~~")
        for field in fields(self):
            if getattr(self, field.name) is not None and hasattr(getattr(self, field.name), 'printClass'):
                print(field.name, ": ")
                getattr(self, field.name).printClass()
            else:
                print(f"{field.name}: {getattr(self, field.name)}")
        print("~~ END SERIES ~~")

# Class to store information for each group node
@dataclass
class GroupsNode:
    name: str
    elimPointsValue: int
    elimPlacing: str
    seeds: list
    bestOf: int
    elimResults: list
    teams: list = field(default_factory=list)
    series: list = field(default_factory=list)
    results: list = field(default_factory=list)
    nextNode: any = None
    # Get all of the permutations of placements
    def getPossibleOutcomes(self):
        groupPermutation = []
        for i in range(1, len(self.teams) + 1):
            groupPermutation.append(i)
        return itertools.permutations(groupPermutation)
    # Set the results of the group given the resultList
    def setResults(self, resultList):
        for i, r in enumerate(resultList):
            self.results[i] = self.teams[r - 1]
        for i, r in enumerate(self.results):
            if i + 1 in self.elimResults:
                r.finishPlace = self.elimPlacing
                r.points = self.elimPointsValue
    def printClass(self):
        print("~~~~ GROUP ~~~~")
        for field in fields(self):
            if field.name not in ('nextNode'):
                if getattr(self, field.name) is not None and hasattr(getattr(self, field.name), 'printClass'):
                    print(field.name, ": ")
                    getattr(self, field.name).printClass()
                else:
                    print(f"{field.name}: {getattr(self, field.name)}")
        print("~~~~ END GROUP ~~~~")
        


# Class to store information for each swiss node
@dataclass
class SwissNode:
    name: str
    bestOf: str
    nextNode: any = None
    seeds: list = field(default_factory=list)
    teams: list = field(default_factory=list)
    def printClass(self):
        for field in fields(self):
            if getattr(self, field.name) is not None and hasattr(getattr(self, field.name), 'printClass'):
                print(field.name, ": ")
                getattr(self, field.name).printClass()
            else:
                print(f"{field.name}: {getattr(self, field.name)}")

# Class to store information for each bracket node
@dataclass
class BracketNode:
    name: str
    elimPointsValue: int
    elimPlacing: str
    team1Name: str
    team2Name: str
    bestOf: int
    winPointsValue: int = 0
    team1Node: any = None
    team2Node: any = None
    series: Series = None
    team1GroupSeed: int = 0
    team2GroupSeed: int = 0
    nextNode: any = None
    # Return the possible permutations of outcomes.
    def getPossibleOutcomes(self):
        return [[1,2],[2,1]]
    # Set the results of the node to the player objects.
    def setResults(self, resultList):
        if resultList[0] == 1: 
            self.series.winner = self.series.team1
            self.series.loser = self.series.team2
        else:
            self.series.winner = self.series.team2
            self.series.loser = self.series.team1
        self.series.loser.points += self.elimPointsValue
        self.series.loser.finishPlace = self.elimPlacing
        if "Final" in self.name:
            self.series.winner.points += self.winPointsValue
            self.series.winner.finishPlace = "1st"
    # Set up the series given previous node results.
    def setSeries(self):
        if "Bracket" in self.team1Node.name:
            team1 = self.team1Node.series.winner
        elif "Group" in self.team1Node.name:
            team1 = self.team1Node.results[self.team1GroupSeed - 1]
        if "Bracket" in self.team2Node.name:
            team2 = self.team2Node.series.winner
        elif "Group" in self.team2Node.name:
            team2 = self.team2Node.results[self.team2GroupSeed - 1]
        self.series = Series(team1, team2, self.bestOf)
    def printClass(self):
        print("~~~~ BRACKET ~~~~")
        for field in fields(self):
            if field.name not in ('team1Node', 'team2Node', 'nextNode'):
                if getattr(self, field.name) is not None and hasattr(getattr(self, field.name), 'printClass'):
                    print(field.name, ": ")
                    getattr(self, field.name).printClass()
                else:
                    print(f"{field.name}: {getattr(self, field.name)}")
        print("~~~~ END BRACKET ~~~~")

# Class to build and navigate the full tournament bracket
class Bracket:

    def __init__(self, bracketJson, teamJson):
        bracketData = json.load(open(bracketJson))
        teamData = json.load(open(teamJson))
        nodeList = []
        teamList = []
        # creating each node
        for node in bracketData:
            if "Bracket" in node:
                try:
                    if "Final" in node:
                        nodeList.append(BracketNode(node, bracketData[node]["ElimPointsValue"], bracketData[node]["ElimPlacing"], bracketData[node]["Team1"], bracketData[node]["Team2"], bracketData[node]["BestOf"], bracketData[node]["WinPointsValue"]))
                    else:                   
                        nodeList.append(BracketNode(node, bracketData[node]["ElimPointsValue"], bracketData[node]["ElimPlacing"], bracketData[node]["Team1"], bracketData[node]["Team2"], bracketData[node]["BestOf"]))
                except Exception as e:
                    print("ERROR: Bracket node does not have all valid fields. Check README for valid examples: " + node)
                    print(e)
                    traceback.print_exc()
                    exit(1)
            elif "Group" in node:
                try:
                    nodeList.append(GroupsNode(node, bracketData[node]["ElimPointsValue"], bracketData[node]["ElimPlacing"], bracketData[node]["Seeds"], bracketData[node]["BestOf"], bracketData[node]["ElimResults"]))
                except Exception as e:
                    print("ERROR: Group node does not have all valid fields. Check README for valid examples: " + node)
                    print(e)
                    traceback.print_exc()
                    exit(1)
        # populating team objects
        for team in teamData:
            playerList = []
            playerList.append(Player(teamData[team]["P1"]))
            playerList.append(Player(teamData[team]["P2"]))
            playerList.append(Player(teamData[team]["P3"]))
            teamList.append(Team(team, playerList, teamData[team]["Points"], teamData[team]["Seed"]))
        # populating groups with teams
        for node in nodeList:
            if "Group" in node.name:
                node.teams = self.findTeamsForGroups(teamList, node.seeds)
                node.results = node.teams # will be reordered after games are run
        # connecting nodes to create bracket
        for node in nodeList:
            if "Bracket" in node.name:
                node.team1Node = self.findNodeFromList(nodeList, node.team1Name)
                if "Group" in node.team1Name:
                    nameList = node.team1Name.split(" ")
                    node.team1GroupSeed = int(nameList[2])
                node.team2Node = self.findNodeFromList(nodeList, node.team2Name)
                if "Group" in node.team2Name:
                    nameList = node.team2Name.split(" ")
                    node.team2GroupSeed = int(nameList[2])
        # enable two-way traversal
        self.setNextNodes(self.findFinalNode(nodeList), None, 0)
        self.bracketRootNode = self.findFinalNode(nodeList)
        self.nodeList = nodeList
        self.teamList = teamList

    def buildBracket(self, bracketJson):
        bracketData = json.load(open(bracketJson))
        nodeList = []        
        # creating each node
        for node in bracketData:
            if "Bracket" in node:
                try:
                    if "Final" in node:
                        nodeList.append(BracketNode(node, bracketData[node]["ElimPointsValue"], bracketData[node]["ElimPlacing"], bracketData[node]["Team1"], bracketData[node]["Team2"], bracketData[node]["BestOf"], bracketData[node]["WinPointsValue"]))
                    else:                   
                        nodeList.append(BracketNode(node, bracketData[node]["ElimPointsValue"], bracketData[node]["ElimPlacing"], bracketData[node]["Team1"], bracketData[node]["Team2"], bracketData[node]["BestOf"]))
                except Exception as e:
                    print("ERROR: Bracket node does not have all valid fields. Check README for valid examples: " + node)
                    print(e)
                    traceback.print_exc()
                    exit(1)
            elif "Group" in node:
                try:
                    nodeList.append(GroupsNode(node, bracketData[node]["ElimPointsValue"], bracketData[node]["ElimPlacing"], bracketData[node]["Seeds"], bracketData[node]["BestOf"], bracketData["ElimResults"]))
                except Exception as e:
                    print("ERROR: Group node does not have all valid fields. Check README for valid examples: " + node)
                    print(e)
                    traceback.print_exc()
                    exit(1)
        # connecting nodes to create bracket
        for node in nodeList:
            if "Bracket" in node.name:
                node.team1Node = self.findNodeFromList(nodeList, node.team1Name)
                if "Group" in node.team1Name:
                    nameList = node.team1Name.split(" ")
                    node.team1GroupSeed = int(nameList[2])
                node.team2Node = self.findNodeFromList(nodeList, node.team2Name)
                if "Group" in node.team2Name:
                    nameList = node.team2Name.split(" ")
                    node.team2GroupSeed = int(nameList[2])
        # enable two-way traversal
        self.setNextNodes(self.findFinalNode(nodeList), None, 0)
        self.bracketRootNode = self.findFinalNode(nodeList)
        self.nodeList = nodeList
    
    def populateBracket(self, teamJson, nodeList):
        teamData = json.load(open(teamJson))
        teamList = []
        # populating team objects
        for team in teamData:
            playerList = []
            playerList.append(Player(teamData[team]["P1"]))
            playerList.append(Player(teamData[team]["P2"]))
            playerList.append(Player(teamData[team]["P3"]))
            teamList.append(Team(team, playerList, teamData[team]["Points"], teamData[team]["Seed"]))
        # populating groups with teams
        for node in nodeList:
            if "Group" in node.name:
                node.teams = self.findTeamsForGroups(teamList, node.seeds)
                node.results = node.teams # will be reordered after games are run
        self.teamList = teamList

    def resetBracket(self, node):
        if "Bracket" in node.name:
            node.series = None
            self.resetBracket(node.team1Node)
            self.resetBracket(node.team2Node)
        elif "Group" in node.name:
            lenResults = len(node.results)
            resetResults = []
            for i in range(0, lenResults):
                resetResults.append(i)
            node.results = resetResults
        for team in self.teamList:
            team.points = 0

    # Find the root (Final) node from the node list generated with the input JSON
    # RETURN: node
    def findFinalNode(self, nodeList):
        for node in nodeList:
            if "Final" in node.name: return node

    # Find a node from the node list generated with the input JSON given the node name
    # RETURN: node
    def findNodeFromList(self, nodeList, nodeName):
        if "Bracket" in nodeName:
            for node in nodeList:
                if node.name == nodeName:
                    return node
            print("ERROR: Bracket Node not found: " + nodeName)
            exit(1)
        elif "Group" in nodeName:
            nameList = nodeName.split(" ")
            groupName = nameList[0] + " " + nameList[1]
            for node in nodeList:
                if node.name == groupName:
                    return node
            print("ERROR: Group Node not found: " + nodeName)
            exit(1)
        else:
            print("ERROR: Invalid node name: " + nodeName)
            exit(1)

    # Find the teams to populate a group given a list of seeds
    # RETURN: List of Teams
    def findTeamsForGroups(self, teamList, seeds):
        newTeamList = []
        for team in teamList:
            if seeds.count(team.seed) == 1:
                newTeamList.append(team)
        return newTeamList

    # Build connections from leaf nodes to root node
    def setNextNodes(self, node, nextNode, layer):
        if "Bracket" not in node.name:
            node.nextNode = nextNode
            return
        if layer == 0: 
            self.setNextNodes(node.team1Node, node, layer + 1)
            self.setNextNodes(node.team2Node, node, layer + 1)
        node.nextNode = nextNode
        self.setNextNodes(node.team1Node, node, layer + 1)
        self.setNextNodes(node.team2Node, node, layer + 1)

    def findNodeFromRoot(self, node, nodeName):
        if node.name == nodeName:
            return node
        if "Bracket" in node.name:
            if node.team1Node:
                foundNode = self.findNodeFromRoot(node.team1Node, nodeName)
                if foundNode:
                    return foundNode
            if node.team2Node:
                foundNode = self.findNodeFromRoot(node.team2Node, nodeName)
                if foundNode:
                    return foundNode
        return None

    def findTeamFromRoot(self, node, teamName):
        if "Bracket" in node.name:
            if "Final" in node.name:
                if teamName == node.series.winner.name: return node.series.winner
            if teamName == node.series.loser.name: return node.series.loser
            if node.team1Node:
                foundTeam = self.findTeamFromRoot(node.team1Node, teamName)
                if foundTeam:
                    return foundTeam
            if node.team2Node:
                foundTeam = self.findTeamFromRoot(node.team2Node, teamName)
                if foundTeam:
                    return foundTeam
        elif "Group" in node.name:
            for placement in node.elimResults:
                if teamName == node.results[placement].name: return node.results[placement]
        return None

    # Navigate to the next node in the bracket
    # RETURN node
    def getNextNode(self, node):
        return node.nextNode

    # Create a df of the standings of all teams sorted by total points
    def getBracketStandings(self, standingsDf):
        for team in self.teamList:
            standingsDf.loc[len(standingsDf.index)] = [team.name, team.finishPlace, team.points]        
        return standingsDf.sort_values(by = "totalPoints", ascending = False)

    # Traverse the bracket and print out every node
    def printBracketTraversal(self, node):
        print("--------------------------")
        node.printClass()
        print("--------------------------")
        if "Bracket" in node.name:
            if None != node.team1Node:
                self.printBracketTraversal(node.team1Node)
            if None != node.team2Node:
                self.printBracketTraversal(node.team2Node)
        elif "Group" in node.name:
            print("Seeds: " + str(node.seeds))
            print("Teams: " + str(node.teams))
            if None != node.results: print("Results: " + str(node.results))
            return
        
# bracket = Bracket("../bracket.json", "../sampleTeams.json")
# bracket.printBracketTraversal(bracket.bracketRootNode)