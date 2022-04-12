import os
import requests
from math import log
from statistics import mean

# Pass in a list of words
# MODES
#   0: Mean Log Edge Count
def cohesion(words, mode=0):
    if mode == 0:
        return mean_log_edge_count(words)

def mean_log_edge_count(words):
    counts = []
    for i in range(0, len(words)):
        for j in range(i, len(words)):
            if i != j:
                print(words[i], words[j])
                result = requests.get(f'http://api.conceptnet.io/query?node=/c/en/{words[i]}&other=/c/en/{words[j]}').json()
                counts.append(len(result['edges']))

    return(mean([log(count + 1) for count in counts]))

topics = {}

for file in os.listdir("data"):
    f = open("data/" + file, "r")
    text = f.read()
    rows = [row.split(" ") for row in text.split("\n")]
    topics[file[:-4]] = dict((row[1], row[0]) for row in rows)

results = [cohesion(list(topic.keys())) for topic in topics.values()]
print(results)
