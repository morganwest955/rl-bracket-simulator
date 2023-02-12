from dataclasses import dataclass, field
from typing import Optional
import json
import traceback

#####
# Build the bracket for the simulation to run through
#####

# Class to store information for each player
@dataclass
class Player:
    name: str = ""

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

# Class to store information for each group node
@dataclass
class GroupsNode:
    name: str
    elimPointsValue: int
    seeds: list
    bestOf: int
    teams: list = field(default_factory=list)
    series: list = field(default_factory=list)
    results: list = field(default_factory=list)
    nextNode: any = None

# Class to store information for each swiss node
@dataclass
class SwissNode:
    name: str
    bestOf: str
    nextNode: any = None
    seeds: list = field(default_factory=list)
    teams: list = field(default_factory=list)

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

# Class to build and navigate the full tournament bracket
class Bracket:

    def __init__(self, bracketJson, teamJson):
        bracketData = json.loads(open(bracketJson))
        teamData = json.loads(open(teamJson))
        nodeList = []
        teamList = []
        # creating each node
        for node in bracketData:
            if "Bracket" in node:
                if "Final" in node:
                    try:
                        print(node)
                        print(node["ElimPointsValue"], type(node["ElimPointsValue"]))
                        print(node["ElimPlacing"], type(node["ElimPlacing"]))
                        print(node["Team1"], type(node["Team1"]))
                        print(node["Team2"], type(node["Team2"]))
                        print(node["BestOf"], type(node["BestOf"]))
                        print(node["WinPointsValue"], type(node["WinPointsValue"]))
                        nodeList.append(BracketNode(node, node["ElimPointsValue"], node["ElimPlacing"], node["Team1"], node["Team2"], node["BestOf"], node["WinPointsValue"]))
                    except Exception as e:
                        print("ERROR: Bracket node does not have all valid fields. Check README for valid examples: " + node)
                        print(e)
                        traceback.print_exc()
                        exit(1)
                else:
                    try:
                        nodeList.append(BracketNode(node, node["ElimPointsValue"], node["ElimPlacing"], node["Team1"], node["Team2"], node["BestOf"]))
                    except Exception as e:
                        print("ERROR: Bracket node does not have all valid fields. Check README for valid examples: " + node)
                        print(e)
                        traceback.print_exc()
                        exit(1)
            elif "Group" in node:
                try:
                    nodeList.append(GroupsNode(node, node["ElimPointValue"], node["ElimPlacing"], node["Seeds"], node["BestOf"]))
                except Exception as e:
                    print("ERROR: Group node does not have all valid fields. Check README for valid examples: " + node)
                    print(e)
                    traceback.print_exc()
                    exit(1)
        # populating team objects
        for team in teamData:
            playerList = []
            playerList.append(Player(team["P1"]))
            playerList.append(Player(team["P2"]))
            playerList.append(Player(team["P3"]))
            teamList.append(Team(team, playerList, team["Score"], team["Seed"]))
        # populating groups with teams
        for node in nodeList:
            if "Group" in node.name:
                node.teams = self.findTeamsForGroups(teamList, node.seeds)
                node.results = node.teams # will be reordered after games are run
        # connecting nodes to create bracket
        for node in nodeList:
            if "Bracket" in node.name:
                node.team1Node = self.findNodeFromList(nodeList, node.team1Name)
                if "Group" in node.team1Node.name:
                    nameList = node.team1Node.name.split(" ")
                    node.team1GroupSeed = int(nameList[2]) - 1
                node.team2Node = self.findNodeFromList(nodeList, node.team2Name)
                if "Group" in node.team2Node.name:
                    nameList = node.team2Node.name.split(" ")
                    node.team2GroupSeed = int(nameList[2]) - 1
        # enable two-way traversal
        self.setNextNodes(self.findFinalNode(nodeList), None, 0)
        self.bracketRootNode = self.findFinalNode(nodeList)

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
            if team.seed in seeds:
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

    # Navigate the bracket from the root node and find a leaf node given the name
    # RETURN: node
    def findNodeFromRoot(self, node, nodeName):
        if node.name == nodeName:
            return node
        if "Bracket" in node.name:
            if None != node.team1:
                self.findNodeFromRoot(node.team1, nodeName)
            if None != node.team2:
                self.findNodeFromRoot(node.team2, nodeName)
        print("ERROR: Reached end of bracket, cannod find node: " + nodeName)

    # Navigate to the next node in the bracket
    # RETURN node
    def getNextNode(self, node):
        return node.nextNode

    def setBracketSeries(self, node):
        team1 = None
        team2 = None
        if "Bracket" in node.team1.name:
            team1 = node.team1.series.winner
        elif "Group" in node.team1.name:
            team1 = node.team1.results[node.team1GroupSeed]
        if "Bracket" in node.team2.name:
            team2 = node.team2.series.winner
        elif "Group" in node.team2.name:
            team2 = node.team2.results[node.team2GroupSeed]
        node.series = Series(team1, team2, node.bestOf)
        
bracket = Bracket("C:/Users/mdog9/source/repos/rl-bracket-simulator/bracket.json", "C:/Users/mdog9/source/repos/rl-bracket-simulator/sampleTeams.json")