from dataclasses import dataclass, field
import json

#####
# Build the bracket for the simulation to run through
#####

@dataclass
class Player:
    name: str = ""

@dataclass
class Team:
    players: field(default_factory=list)
    score: int = 0
    seed: int = 0
    gamesWon: int = 0
    gamesLost: int = 0
    goalsScored: int = 0
    goalsConceded: int = 0
    points: int = 0

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
    elimPointValue: int
    nextNode: any
    seeds: list = field(default_factory=list)
    teams: list = field(default_factory=list)
    series: list = field(default_factory=list)

@dataclass
class SwissNode:
    name: str
    nextNode: any
    seeds: list = field(default_factory=list)
    teams: list = field(default_factory=list)

@dataclass
class BracketNode:
    name: str
    series: Series
    elimPointValue: int
    winDest: str
    loseDest: str
    nextNode: any
    seeds: list = field(default_factory=list)

class Bracket:

    def __init__(self, bracketJson, teamJson):
        bracketData = json.load(open(bracketJson))
        teamData = json.load(open(teamJson))
         

bracket = Bracket("C:/Users/mdog9/source/repos/rl-bracket-simulator/sampleBracket.json", "C:/Users/mdog9/source/repos/rl-bracket-simulator/sampleTeams.json")