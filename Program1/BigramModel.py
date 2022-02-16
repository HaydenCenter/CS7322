import os, sys
import re
import nltk
import numpy
from nltk.corpus import stopwords

from nltk import sent_tokenize, RegexpTokenizer, bigrams

# TODO: otherWordList

class BigramModel:
    def __init__(self, name = "default", dirName = '.', ext = '*', toload = False, smooth = 0, stopWordList = [], otherWordList = [], singlesen = False):
        if toload:
            print("TODO")
            return

        if not os.path.isdir(dirName):
            sys.exit("Invalid file path: " + dirName)

        
        dirPath = os.path.abspath(dirName)

        # Filtering files by extension
        if ext == '*':
            files = os.listdir(dirPath)
        else:
            files = [fileName for fileName in os.listdir(dirPath) if os.path.splitext(fileName)[-1] in [ext, '.' + ext]]

        # Setting up add-k smoothing
        if smooth > 1:
            smooth = 0
        self.smooth = smooth

        self.stopWordList = stopWordList
        self.otherWordList = otherWordList

        self.bigramCounts = {}
        self.wordCounts = {}

        for fileName in files:
            print(fileName) # DEBUG

            # Getting text from file and converting to lowercase
            file = open(dirPath + "\\" + fileName)
            text = file.read().lower()

            # Tokenizing with or without sentence breaks according to singlesen
            tokens = []
            if singlesen:
                self.__tokenize(text, tokens)
            else:  
                sentences = sent_tokenize(text)
                for sentence in sentences:
                    self.__tokenize(sentence, tokens)

            bgs = bigrams(tokens)

            self.uniqueWords = len(self.wordCounts)
            self.__count(tokens, self.wordCounts)
            self.__count(bgs, self.bigramCounts)

    def __tokenize(self, text, tokens):
        words = RegexpTokenizer("[\w']+").tokenize(text)

        # Removing stopwords
        words = [word for word in words if word not in self.stopWordList]

        # Removing non-alphanumeric words
        words = [word for word in words if re.search("(.*\w+.*)", word)]

        if words:
            tokens.append("^")
            for word in words:
                tokens.append(word)
            tokens.append("$")

    def __count(self, collection, counts):
        for item in collection:
            if item == ("$", "^"):
                continue

            if item in counts:
                counts[item] = counts[item] + 1
            else:
                counts[item] = 1

    # def __getWordList(self, word):
    #     if word in self.otherWordList:
    #         return self.otherWordList
    #     else:
    #         return [word]

    def __probCalc(self, w1, w2):
        f = None
        k = self.smooth
        n = self.wordCounts[w1]
        v = self.uniqueWords
        if (w1, w2) in self.bigramCounts:
            f = self.bigramCounts[(w1,w2)]
        elif w1 in self.wordCounts and w2 in self.wordCounts:
            f = 0
        else:
            return -1

        return (f + k) / (n + k * v)

    def getProb(self, w1, w2):
        return self.__probCalc(w1, w2)



    def __getProbListHelper(self, word, sortMethod, index):
        if word not in self.wordCounts:
            return []

        result = []
        for bigram in self.bigramCounts:
            if bigram[index] == word:
                prob = self.getProb(bigram[0], bigram[1])
                result.append((bigram[not index], prob))

        if sortMethod == 1:
            return sorted(result)
        elif sortMethod == 2:
            return sorted(result, reverse=True, key=lambda tuple: tuple[1])
        else:
            return result

    def getProbList(self, w1, sortMethod = 0):
        return self.__getProbListHelper(w1, sortMethod, index = 0)

    def getProbList2(self, w2, sortMethod = 0):
        return self.__getProbListHelper(w2, sortMethod, index = 1)

    def getAll(self, sortMethod = 0):
        result = [(bg[0], bg[1], self.getProb(bg[0], bg[1])) for bg in self.bigramCounts]

        if sortMethod == 1:
            return sorted(result, key=lambda tuple: (tuple[0], tuple[1]))
        elif sortMethod == 2:
            return sorted(result, reverse=True, key=lambda tuple: tuple[2])
        elif sortMethod == 3:
            return sorted(result, key=lambda tuple: (tuple[1], tuple[0]))
        else:
            return result

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

bg = BigramModel(dirName="Program1\\documents", toload=False, smooth=1, stopWordList=stopwords.words('english'), otherWordList=[], singlesen=False) # DEBUG
# bg = BigramModel(dirName="Program1\\_prog1", singlesen=False, stopWordList=["is", "a"], otherWordList=["dog", "cat", "good"], smooth=0) # DEBUG
# [print(i) for i in bg.getAll(sortMethod=2)]
f = open("output.txt", "w").write("\n".join([str(i) for i in bg.getAll(sortMethod=2)]))
# [print(bigram) for bigram in bg.getProbList("tony", sortMethod=2)]