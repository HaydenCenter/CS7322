import os, sys
import re
import nltk
import numpy
from nltk.corpus import stopwords

from nltk import sent_tokenize, RegexpTokenizer, bigrams

class BigramModel:
    def __init__(self, name = "default", dirName = '.', ext = '*', toload = False, smooth = 0, stopWordList = [], otherWordList = [], singlesen = False):
        print(" | ".join(map(str, [name, dirName, ext, toload, smooth, stopWordList, otherWordList, singlesen]))) # DEBUG

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

        self.bigramCounts = {}
        self.wordCounts = {}
        self.totalBigrams = 0.0
        self.totalWords = 0.0

        for fileName in files:
            print(fileName) # DEBUG

            # Getting text from file and converting to lowercase
            file = open(dirPath + "\\" + fileName)
            text = file.read().lower()

            # Tokenizing with or without sentence breaks according to singlesen
            tokens = []
            if singlesen:
                self.__tokenize(text, stopWordList, otherWordList, tokens)
            else:  
                sentences = sent_tokenize(text)
                for sentence in sentences:
                    self.__tokenize(sentence, stopWordList, otherWordList, tokens)

            bgs = bigrams(tokens)

            self.totalWords = self.__count(tokens, self.wordCounts, self.totalWords)
            self.totalBigrams = self.__count(bgs, self.bigramCounts, self.totalBigrams)

            # break # DEBUG

        # print(self.totalWords) # DEBUG
        # print(self.totalBigrams) # DEBUG
        # print(dict(sorted(self.bigramCounts.items(), key=lambda item: item[1]))) # DEBUG
        # print(sorted(self.bigramCounts.items())) # DEBUG

    def __tokenize(self, text, stopWordList, otherWordList, tokens):
        words = RegexpTokenizer("[\w']+").tokenize(text)

        # Removing stopwords
        words = [word for word in words if word not in stopWordList]

        # Removing non-alphanumeric words
        words = [word for word in words if re.search("(.*\w+.*)", word)]

        # Replacing tokens in other word list
        words = ["<O>" if word in otherWordList else word for word in words]

        if words:
            tokens.append("^")
            for word in words:
                tokens.append(word)
            tokens.append("$")

    def __count(self, collection, counts, total):
        for item in collection:
            total = total + 1
            if item in counts:
                counts[item] = counts[item] + 1
            else:
                counts[item] = 1
        
        return total

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

bg = BigramModel(dirName="documents", toload=False, stopWordList=stopwords.words('english'), otherWordList=[], singlesen=False) # DEBUG
# bg = BigramModel(dirName="_prog1", singlesen=False, stopWordList=["is", "a"]) # DEBUG