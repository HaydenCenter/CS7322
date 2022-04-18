import sys

f = open('HW2Q1.txt', 'w')
orig_stdout = sys.stdout
sys.stdout = f

class Rule:
    def __init__(self, parent, children, prob):
        self.parent = parent
        self.children = children
        self.prob = prob
        self.terminal = len(children) == 1
        self.descendants = None

    def __str__(self):
        if self.terminal:
            children = self.children
        else:
            children = self.children[0] + self.children[1]
        return f'{self.parent}->{children}'

grammar = [
    Rule("S", ("A", "B"), 0.3),
    Rule("S", ("A", "C"), 0.3),
    Rule("S", ("B", "C"), 0.4),
    Rule("A", ("A", "B"), 0.25),
    Rule("A", ("C", "B"), 0.3),
    Rule("A", ("B", "A"), 0.2),
    Rule("A", "a", 0.25),
    Rule("B", ("B", "A"), 0.3),
    Rule("B", ("C", "A"), 0.15),
    Rule("B", ("C", "C"), 0.25),
    Rule("B", "b", 0.3),
    Rule("C", ("B", "A"), 0.2),
    Rule("C", ("C", "B"), 0.2),
    Rule("C", "b", 0.15),
    Rule("C", "c", 0.15)
]

rulesDict = {}
rulesConsideredDict = {}

def getRules(text, printRulesConsidered=False):
    if text in rulesDict.keys():
        rules = rulesDict[text]
        rulesConsidered = rulesConsideredDict[text]
    elif len(text) == 1:
        rules = [rule for rule in grammar if rule.children == text]
        rulesConsidered = rules
    else:
        rules = []
        for i in range(1, len(text)):
            first = getRules(text[0:i])
            second = getRules(text[i:len(text)])
            for f in first:
                for s in second:
                    children = (f.parent, s.parent)
                    for rule in grammar:
                        if rule.children == children:
                            r = Rule(rule.parent, children, f.prob * s.prob * rule.prob)
                            r.descendants = (f, s)
                            rules.append(r)


        result = {}
        for rule in rules:
            if rule.parent not in result.keys() or rule.prob > result[rule.parent].prob:
                result[rule.parent] = rule

        rulesConsidered = rules
        rules = list(result.values())
    
    if printRulesConsidered:
        print("Rules considered: ", end="")
        print(", ".join([r.__str__() for r in rulesConsidered]))

    rulesDict[text] = rules
    rulesConsideredDict[text] = rulesConsidered
    return rules
        
text = "babca"

for length in range(1, len(text) + 1):
    for i in range(0, len(text) + 1 - length):
        j = i + length
        print(f'Entry ({i},{j}): Corresponding String: "{text[i:j]}"')
        rules = getRules(text[i:j], printRulesConsidered=True)
        print(f'Final results to be stored: (Rules/Overall prob): ', end="")
        print(", ".join([f'{r.__str__()} ({r.prob})' for r in rules]))
        print()

f.close()

sys.stdout = orig_stdout

rules = getRules(text)
root = [r for r in rules if r.parent == "S"][0]

def printTree(node, level=0):
    padding = level * ["\t"]
    print("".join(padding), end="")
    print(node, " ", node.prob)
    if node.descendants:
        [printTree(d, level + 1) for d in node.descendants]

printTree(root)