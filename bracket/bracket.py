from dataclasses import dataclass, field
from typing import Optional
import json

#####
# Build the bracket for the simulation to run through
#####

@dataclass
class Player:
    name: str = ""

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

@dataclass
class Series:
    team1: Team
    team2: Team
    bestOf: int
    team1Score: int
    team2Score: int
    winner: Team
    loser: Team

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

@dataclass
class GroupsNode:
    name: str
    elimPointsValue: int
    seeds: list
    teams: list = field(default_factory=list)
    series: list = field(default_factory=list)
    results: list = field(default_factory=list)
    nextNode: any = None

@dataclass
class SwissNode:
    name: str
    nextNode: any = None
    seeds: list = field(default_factory=list)
    teams: list = field(default_factory=list)

@dataclass
class BracketNode:
    name: str
    elimPointsValue: int
    elimPlacing: str
    team1Name: str
    team2Name: str
    winPointsValue: int = 0
    team1Node: any = None
    team2Node: any = None
    series: Series = None
    nextNode: any = None


class Bracket:

    def __init__(self, bracketJson, teamJson):
        bracketData = json.load(open(bracketJson))
        teamData = json.load(open(teamJson))
        nodeList = []
        teamList = []
        # creating each node
        for node in bracketData:
            if "Bracket" in node:
                if "Final" in node:
                    nodeList.append(BracketNode(node, node["ElimPointsValue"], node["ElimPlacing"], node["Team1"], node["Team2"], node["WinPointsValue"]))
                else:
                    nodeList.append(BracketNode(node, node["ElimPointsValue"], node["ElimPlacing"], node["Team1"], node["Team2"]))
            elif "Group" in node:
                nodeList.append(GroupsNode(node, node["ElimPointValue"], node["ElimPlacing"], node["Seeds"]))
        # populating team objects
        for team in teamData:
            playerList = []
            playerList.append(Player(team["P1"]))
            playerList.append(Player(team["P2"]))
            playerList.append(Player(team["P3"]))
            teamList.append(Team(team["Name"], playerList, team["Score"], team["Seed"]))
        # populating groups with teams
        for node in nodeList:
            if "Group" in node.name:
                node.teams = self.findTeams(teamList, node.seeds)
                node.results = node.teams # will be reordered after games are run
        # connecting nodes to create bracket
        for node in nodeList:
            if "Bracket" in node.name:
                node.team1Node = self.findNode(nodeList, node.team1Name)
                node.team2Node = self.findNode(nodeList, node.team2Name)
        # enable two-way traversal
        self.setNextNodes(self.findFinalNode(nodeList), None, 0)
        self.bracketNode = self.findFinalNode(nodeList)

    def findFinalNode(self, nodeList):
        for node in nodeList:
            if "Final" in node.name: return node

    def findNode(self, nodeList, nodeName):
        if "Bracket" in nodeName:
            for node in nodeList:
                if node.name == nodeName:
                    return node
            print("Error: Bracket Node not found: " + nodeName)
            exit(1)
        elif "Group" in nodeName:
            nameList = nodeName.split(" ")
            groupResult = int(nameList[2]) - 1
            groupName = nameList[0] + " " + nameList[1]
            for node in nodeList:
                if node.name == groupName:
                    return node.results[groupResult]
            print("Error: Group Node not found: " + nodeName)
            exit(1)
        else:
            print("Error: Invalid node name: " + nodeName)
            exit(1)

    def findTeams(self, teamList, seeds):
        newTeamList = []
        for team in teamList:
            if team.seed in seeds:
                newTeamList.append(team)
        return newTeamList

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
        
bracket = Bracket("C:/Users/mdog9/source/repos/rl-bracket-simulator/sampleBracket.json", "C:/Users/mdog9/source/repos/rl-bracket-simulator/sampleTeams.json")