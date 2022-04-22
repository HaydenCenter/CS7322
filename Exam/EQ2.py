from pprint import pprint

class Word:
    def __init__(self, word, tag):
        self.word = word
        self.tag = tag

    def __str__(self):
        return f'{self.word}{self.tag}'

    def __repr__(self):
        return self.__str__()

words = [
    Word("<", "<"),
    Word("A", "1"),
    Word("C", "2"),
    Word("D", "3"),
    Word("A", "3"),
    Word("A", "2"),
    Word("D", "1"),
    Word(">", ">"),
    Word("<", "<"),
    Word("B", "2"),
    Word("C", "2"),
    Word("B", "1"),
    Word("A", "3"),
    Word("A", "3"),
    Word(">", ">"),
    Word("<", "<"),
    Word("D", "3"),
    Word("D", "1"),
    Word("A", "3"),
    Word("B", "2"),
    Word(">", ">"),
]

# get transition P(tag given prev_tag)
def getTransitionProb(prev_tag, tag, t_count):
    # get sum of prev_tag
    denom = sum(t_count[prev_tag].values())
    num = t_count[prev_tag][tag]
    return num / denom

# get emission P(word given tag)
def getEmissionProb(tag, word, e_count):
    # get sum of prev_tag
    denom = sum(e_count[tag].values())
    num = e_count[tag][word]
    return num / denom

def calculate(words):
    # [tag][word]
    e_count = {
        "1":{
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
        },
        "2":{
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
        },
        "3":{
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
        },
    }
    e_prob = {
        "1":{
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
        },
        "2":{
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
        },
        "3":{
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
        },
    }

    # [prev_tag][tag]
    t_count = {
        "<": {
            "1": 0,
            "2": 0,
            "3": 0,
            ">": 0
        },
        "1": {
            "1": 0,
            "2": 0,
            "3": 0,
            ">": 0
        },
        "2": {
            "1": 0,
            "2": 0,
            "3": 0,
            ">": 0
        },
        "3": {
            "1": 0,
            "2": 0,
            "3": 0,
            ">": 0
        },
    }
    t_prob = {
        "<": {
            "1": 0,
            "2": 0,
            "3": 0,
            ">": 0
        },
        "1": {
            "1": 0,
            "2": 0,
            "3": 0,
            ">": 0
        },
        "2": {
            "1": 0,
            "2": 0,
            "3": 0,
            ">": 0
        },
        "3": {
            "1": 0,
            "2": 0,
            "3": 0,
            ">": 0
        },
    }

    prev_tag = words[0].tag
    for word in words[1:]:

        # calculate emission
        if word.word not in ["<", ">"]:
            e_count[word.tag][word.word] = e_count[word.tag][word.word] + 1

        # calculate t_count
        if word.tag != "<":
            t_count[prev_tag][word.tag] = t_count[prev_tag][word.tag] + 1

        prev_tag = word.tag

    print("Transition counts")
    pprint(t_count)
    print("Emission counts")
    pprint(e_count)

    for prev_tag in t_prob:
        for tag in t_prob[prev_tag]:
            t_prob[prev_tag][tag] = getTransitionProb(prev_tag, tag, t_count)

    for tag in e_prob:
        for word in e_prob[tag]:
            e_prob[tag][word] = getEmissionProb(tag, word, e_count)

    print("Transition probs")
    pprint(t_prob)
    print("Emission probs")
    pprint(e_prob)

    return (t_prob, e_prob)

def update(words, t_prob, e_prob):
    sentences = [
        words[1:7],
        words[9:14],
        words[16:20]
    ]

    result = []

    for s in sentences:
        new_s = [Word("<", "<")]
        maxProb = [dict({"1": '0', "2": '0', "3": '0'}) for i in range(len(s))]
        choice  = [dict({"1": '0', "2": '0', "3": '0'}) for i in range(len(s))]
        
        tags = ["1", "2", "3"]

        for tag in tags:
            maxProb[0][tag] = t_prob["<"][tag] * e_prob[tag][s[0].word]

        for i in range(1, len(s) - 1):
            for tag in tags:
                choices = {"1": None, "2": None, "3": None}
                for prev_tag in choices:
                    prob = maxProb[i - 1][prev_tag] * t_prob[prev_tag][tag] * e_prob[tag][s[i].word]
                    choices[prev_tag] = prob
                if sum(choices.values()) == 0:
                    best = '0'
                else:
                    best = max(choices, key=choices.get)

                choice[i][tag] = best
                maxProb[i][tag] = choices.get(best, 0)

        for tag in tags:
            choices = {"1": None, "2": None, "3": None}
            for prev_tag in choices:
                prob = maxProb[-2][prev_tag] * t_prob[prev_tag][tag] * e_prob[tag][s[-1].word] * t_prob[tag][">"]
                choices[prev_tag] = prob
            if sum(choices.values()) == 0:
                best = '0'
            else:
                best = max(choices, key=choices.get)

            choice[-1][tag] = best
            maxProb[-1][tag] = choices.get(best, 0)

        for i, probs in enumerate(maxProb):
            new_s.append(Word(s[i].word, max(probs, key=probs.get)))

        pprint([["{:.6f}".format(p) for p in w.values()] for w in maxProb])
        pprint([[p for p in w.values()] for w in choice])
        new_s.append(Word(">", ">"))
        result.append(new_s)
    
    pprint(result)

    return result

t_prob, e_prob = calculate(words)
words = [word for s in update(words, t_prob, e_prob) for word in s]
calculate(words)