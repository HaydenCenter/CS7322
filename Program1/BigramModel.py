import os, sys
import re
from genericpath import exists
from nltk import sent_tokenize, RegexpTokenizer, bigrams

class BigramModel:
    def __init__(self, name = "default", dirName = '.', ext = '*', toload = False, smooth = 0, stopWordList = [], otherWordList = [], singlesen = False):
        # Maps words in otherWordList to '#' and all others to themselves
        # Used to group otherWordList words into bigrams
        self.bigramMap = {}
        self.wordMap = {}

        # Stores the frequencies of each bigram and word in the corpus
        # (stores grouped words and bigrams)
        self.bigramCounts = {}
        self.wordCounts = {}

        # Setting up add-k smoothing
        if smooth > 1:
            smooth = 0
        self.smooth = smooth

        self.name = name

        if toload:
            if not exists(name + ".bgmodel"):
                sys.exit("Invalid model name: " + name + ". File " + name + ".bgmodel does not exist")
            f = open(name + ".bgmodel", "r")
            model = f.read().splitlines()
            
            try:
                wordMapData = self.__getModelData(model)
                bigramMapData = self.__getModelData(model)
                wordCountsData = self.__getModelData(model)
                bigramCountsData = self.__getModelData(model)

                for k, v in wordMapData:
                    self.wordMap[k] = v

                for k1, k2, v1, v2 in bigramMapData:
                    self.bigramMap[(k1, k2)] = (v1, v2)

                for k, v in wordCountsData:
                    self.wordCounts[k] = int(v)

                for k1, k2, v in bigramCountsData:
                    self.bigramCounts[(k1, k2)] = int(v)

                self.uniqueWords = len(self.wordMap) 
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

        self.stopWordList = stopWordList
        self.otherWordList = otherWordList

        for fileName in files:
            # Getting text from file and converting to lowercase
            file = open(dirPath + "\\" + fileName)
            text = file.read().lower()

            # Tokenizing with or without sentence breaks according to singlesen
            words = []
            if singlesen:
                self.__tokenize(text, words)
            else:  
                sentences = sent_tokenize(text)
                for sentence in sentences:
                    self.__tokenize(sentence, words)

            for word in words:
                # Map words in otherWordList to the same value
                if word not in self.wordMap:
                    self.wordMap[word] = "#" if word in self.otherWordList else word

                # Update frequencies using key from map
                key = self.wordMap[word]
                if key in self.wordCounts:
                    self.wordCounts[key] = self.wordCounts[key] + 1
                else:
                    self.wordCounts[key] = 1

            self.uniqueWords = len(self.wordMap)
            bgs = bigrams(words)

            for bg in bgs:
                # Ignore bigrams representing the end of one and start of the next sentence
                if bg == ("$", "^"):
                    continue

                # Group bigrams together based on grouped words
                if bg not in self.bigramMap:
                    w1 = self.wordMap[bg[0]]
                    w2 = self.wordMap[bg[1]]
                    self.bigramMap[bg] = (w1, w2)

                key = self.bigramMap[bg]
                if key in self.bigramCounts:
                    self.bigramCounts[key] = self.bigramCounts[key] + 1
                else:
                    self.bigramCounts[key] = 1

    def __tokenize(self, text, result):
        words = RegexpTokenizer("[\w']+").tokenize(text)

        # Removing stopwords
        words = [word for word in words if word not in self.stopWordList]

        # Removing non-alphanumeric words
        words = [word for word in words if re.search("(.*\w+.*)", word)]

        if words:
            result.append("^")
            for word in words:
                result.append(word)
            result.append("$")

    def __getModelData(self, model):
        n = int(model.pop(0))
        modelData = model[0:n]
        del model[0:n]
        return [line.split('\t') for line in modelData]


    def getProb(self, w1, w2):
        f = None
        k = self.smooth
        n = self.wordCounts[self.wordMap[w1]]
        v = self.uniqueWords
        if (w1, w2) in self.bigramMap:
            key = self.bigramMap[(w1, w2)]
            f = self.bigramCounts[key]
        elif w1 in self.wordMap and w2 in self.wordMap:
            f = 0
        else:
            return -1

        return (f + k) / (n + k * v)

    def getProbList(self, w1, sortMethod = 0):
        return self.__getProbListHelper(w1, sortMethod, index = 0)

    def getProbList2(self, w2, sortMethod = 0):
        return self.__getProbListHelper(w2, sortMethod, index = 1)

    def __getProbListHelper(self, word, sortMethod, index):
        if word not in self.wordMap:
            return []

        result = []
        for bigram in self.bigramMap:
            if bigram[index] == word:
                prob = self.getProb(bigram[0], bigram[1])
                result.append((bigram[not index], prob))

        if sortMethod == 1:
            return sorted(result)
        elif sortMethod == 2:
            return sorted(result, reverse=True, key=lambda tuple: tuple[1])
        else:
            return result

    def getAll(self, sortMethod = 0):
        result = [(bg[0], bg[1], self.getProb(bg[0], bg[1])) for bg in self.bigramMap]

        if sortMethod == 1:
            return sorted(result, key=lambda tuple: (tuple[0], tuple[1]))
        elif sortMethod == 2:
            return sorted(result, reverse=True, key=lambda tuple: tuple[2])
        elif sortMethod == 3:
            return sorted(result, key=lambda tuple: (tuple[1], tuple[0]))
        else:
            return result

    def save(self):
        f = open(self.name + ".bgmodel", "w")

        # Saving wordMap
        f.write(f'{len(self.wordMap)}\n')
        f.write(''.join([f'{word}\t{self.wordMap[word]}\n' for word in self.wordMap]))

        # Saving bigramMap
        f.write(f'{len(self.bigramMap)}\n')
        f.write(''.join([f'{bg[0]}\t{bg[1]}\t{self.bigramMap[bg][0]}\t{self.bigramMap[bg][1]}\n' for bg in self.bigramMap]))

        # Saving wordCounts
        f.write(f'{len(self.wordCounts)}\n')
        f.write(''.join([f'{word}\t{self.wordCounts[word]}\n' for word in self.wordCounts]))

        # Saving bigramCounts
        f.write(f'{len(self.bigramCounts)}\n')
        f.write(''.join([f'{bg[0]}\t{bg[1]}\t{self.bigramCounts[bg]}\n' for bg in self.bigramCounts]))

        f.close()
