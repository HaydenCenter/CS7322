import os, sys
import re
import numpy as np, pandas as pd
from genericpath import exists
from nltk import sent_tokenize, RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer

class PLSI:
    def __init__(self, name="default", dirName='.', ext='*', toLoad=False, stopWordList=[],
                       ignoreCase=True, stem=None, topicCount=2, iterations=2):

        # region Preprocessing
        if toLoad:
            if not exists(name + ".plsi"):
                sys.exit("Invalid model name: " + name + ". File " + name + ".plsi does not exist")
            f = open(name + ".plsi", "r")
            model = f.read().splitlines()
            
            try:
                print("TODO: Load Model")
            except:
                sys.exit("Invalid model format") 
            return

        if not os.path.isdir(dirName):
            sys.exit("Invalid file path: " + dirName)

        dirPath = os.path.abspath(dirName)

        # Filtering files by extension
        if ext == '*':
            files = os.listdir(dirPath)
        else:
            files = [fileName for fileName in os.listdir(dirPath) if os.path.splitext(fileName)[-1] in [ext, '.' + ext]]

        probs = {}
        wordSet = set()
        for fileName in files:
            # Getting text from file and converting to lowercase
            file = open(dirPath + "\\" + fileName)
            text = file.read()
            file.close()

            sentences = sent_tokenize(text)
            words = []
            for sentence in sentences:
                tokens = RegexpTokenizer("[\w']+").tokenize(sentence)
                for token in tokens:
                    words.append(token)

            # Removing stopwords
            words = [word for word in words if word not in stopWordList]
            
            # Removing non-alphanumeric words
            words = [word for word in words if re.search("(.*\w+.*)", word)]

            # Convert to lower case
            if ignoreCase:
                words = [word.lower() for word in words]

            if stem == "snowball":
                stemmer = SnowballStemmer("english")
                words = [stemmer.stem(word) for word in words]

            probs[fileName] = pd.DataFrame(data=0, columns=words, index=range(topicCount))
            [wordSet.add(word) for word in words]

        # endregion Preprocessing

        z = pd.DataFrame(data=0, columns=range(topicCount), index=sorted(wordSet))
        d = pd.DataFrame(data=0, index=range(topicCount),   columns=files)
        
        # region first iteration
        for docNum, doc in enumerate(files):
            for wordNum, word in enumerate(probs[doc].columns):
                topic = (docNum + wordNum) % topicCount
                z.at[word, topic] = z.at[word, topic] + 1
                d.at[topic, doc] = d.at[topic, doc] + 1

        print(z)
        print(d)

        for col in z:
            total = z[col].sum()
            for word, n in z[col].iteritems():
                z.at[word, col] = n / total
        for col in d:
            total = d[col].sum()
            for topic, n in d[col].iteritems():
                d.at[topic, col] = n / total
        # endregion first iteration

        print(z)
        print(d)

        # region iterate
        for i in range(iterations - 1):
            # Generating word probabilities
            for docNum, doc in enumerate(files):
                for word in probs[doc].columns:
                    numerators = []
                    for topic in z.columns:
                        wordGivenTopic = z.at[word, topic]
                        topicGivenDoc = d.at[topic, doc]
                        numerators.append(wordGivenTopic * topicGivenDoc)
                    
                    denom = sum(numerators)
                    for topic in z.columns:
                        probs[doc].at[topic, word] = numerators[topic] / denom
            
            # Updating document topic vectors
            for doc in files:
                for topic in z.columns:
                    d.at[topic, doc] = probs[doc].loc[topic].sum() / probs[doc].values.sum()

            # Updating topic word vectors
            for topic in z.columns:
                vectors = [probs[doc].loc[topic] for doc in files]
                for word in z.index:
                    numer = sum([v.loc[word].sum() if word in v.index else 0 for v in vectors])
                    denom = sum([v.sum() for v in vectors])
                    z.at[word, topic] = numer / denom
        # endregion iterate

        [print(doc, '\n', probs[doc]) for doc in probs]
        print(z)
        print(d)

plsi = PLSI(dirName="Program1\\_prog1")