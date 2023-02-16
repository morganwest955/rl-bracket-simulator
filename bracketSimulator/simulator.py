from bracket import Bracket
import itertools

class SimulateAllScenarios:

    def __init__(self, bracketJson, teamJson):
        bracket = Bracket(bracketJson, teamJson)
        # bracket.printBracketTraversal(bracket.bracketRootNode)
        for i, scenario in enumerate(self.getSimScenarios(bracket.nodeList)):
            # print("scenario ", i)
            self.runBracketScenario(bracket, scenario)
            if i == 5: 
                print("~~~~~~~~~~~~~~~~~~~~~~")
                bracket.printBracketTraversal(bracket.bracketRootNode)

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
            node = bracket.findNodeFromRoott(bracket.bracketRootNode, key)
            if "Bracket" in node.name:
                node.setSeries()
            node.setResults(scenario[key])
        return


sim = SimulateAllScenarios("../bracket.json", "../sampleTeams.json")
