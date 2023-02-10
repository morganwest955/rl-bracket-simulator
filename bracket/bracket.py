from dataclasses import dataclass, field

#####
# Build the bracket for the simulation to run through
#####

@dataclass
class Player:
    name: str

@dataclass
class Team:
    players: field(default_factory=list)
    score: int
    seed: int
    gamesWon: int
    gamesLost: int

@dataclass
class GroupsNode:
    name: str
    seeds = field(default_factory=list)
    teams = field(default_factory=list)
    destinations = field(default_factory=list)
    def runGames(self):
        return 0

@dataclass
class SwissNode:
    name: str
    seeds = field(default_factory=list)
    teams = field(default_factory=list)
    destinations = field(default_factory=list)

@dataclass
class BracketNode:
    name: str
    seeds: field(default_factory=list) = []
    winDest: str
    loseDest: str

@dataclass
class Bracket:
    name: str
    prevNodes: field(default_factory=list)