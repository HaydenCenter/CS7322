import os, sys
import re
import numpy as np, pandas as pd
from io import StringIO
from genericpath import exists
from nltk import sent_tokenize, RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer

class PLSI:
    def __init__(self, name="default", dirName='.', ext='*', toLoad=False, stopWordList=[],
                       ignoreCase=True, stem=None, topicCount=2, iterations=2):

        # region Preprocessing
        self.name = name

        if toLoad:
            if not exists(name + ".plsi"):
                sys.exit("Invalid model name: " + name + ". File " + name + ".plsi does not exist")
            f = open(name + ".plsi", "r")
            
            # try:
            text = f.read().split("<>\n")
            self.z = pd.read_csv(StringIO(text[0]), header=0, index_col=0)
            self.d = pd.read_csv(StringIO(text[1]), header=0, index_col=0)
            self.z.rename(mapper=int, axis=1, inplace=True)
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


        for col in z:
            total = z[col].sum()
            for word, n in z[col].iteritems():
                z.at[word, col] = n / total
        for col in d:
            total = d[col].sum()
            for topic, n in d[col].iteritems():
                d.at[topic, col] = n / total
        # endregion first iteration


        # region iterate
        for i in range(iterations):
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

        self.z = z
        self.d = d

    def getDocumentTopic(self, docNum=-1, docName=""):
        if docNum >= len(self.d.columns) or docNum < 0:
            vector = self.d.get(docName, default=[])
        else:
            vector = self.d.iloc[:, docNum]

        return list(vector)

    def getAllDocumentTopic(self):
        return [(col, self.getDocumentTopic(docName=col)) for col in self.d.columns]

    def getTopicWordVector(self, topicNum, topCount=10):
        if topicNum >= len(self.z.columns) or topicNum < 0:
            return {}
        
        vector = self.z[topicNum].sort_values(ascending=False)
        if topCount > 0:
            vector = vector[:topCount]
        return vector.to_dict()

    def getTopicWordVectorAll(self, topCount=10):
        return[self.getTopicWordVector(topic, topCount) for topic in self.z.columns]

    def ExtendedPrint(self, dnamSuffix=""):
        dirName = self.name + dnamSuffix
        if not os.path.exists(dirName): os.mkdir(dirName)
        f = open(dirName + "\\document-topics", "w+")
        for doc in self.d.columns:
            f.write(doc)
            [f.write(f' {x}') for x in self.d[doc]]
            f.write('\n')
        f.close()

        for topic in self.z.columns:
            f = open(f'{dirName}\\topic_{topic + 1}', "w")
            [f.write(f'{word} {x}\n') for word, x in self.getTopicWordVector(topic, topCount=-1).items()]
            f.close()

    def save(self):
        f = open(self.name + ".plsi", "w")
        f.write("<>\n".join([self.z.to_csv(), self.d.to_csv()]))
        f.close()


plsi = PLSI(dirName="Program2/_test", topicCount=3, iterations=1, toLoad=True)
print(plsi.getDocumentTopic(docName="a.txt"))
[print(x, y) for x, y in plsi.getAllDocumentTopic()]
print(plsi.getTopicWordVector(0, topCount=1))
print(plsi.getTopicWordVectorAll(topCount=1))
plsi.ExtendedPrint("_data")
plsi.save()