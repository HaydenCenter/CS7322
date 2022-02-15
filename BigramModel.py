import os, sys
import re
import nltk
import numpy

from nltk import word_tokenize, sent_tokenize, bigrams

class BigramModel:
    def __init__(self, name = "default", dirName = '.', ext = '*', toload = False, smooth = 0, stopWordList = [], otherWordList = [], singlesen = False):
        print(" | ".join(map(str, [name, dirName, ext, toload, smooth, stopWordList, otherWordList, singlesen]))) # DEBUG

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        if not os.path.isdir(dirName):
            sys.exit("Invalid file path: " + dirName)

        
        dirPath = os.path.abspath(dirName)

        # Filtering files by extension
        if ext == '*':
            files = os.listdir(dirPath)
        else:
            files = [fileName for fileName in os.listdir(dirPath) if os.path.splitext(fileName)[-1] in [ext, '.' + ext]]

        for fileName in files:
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


            # Removing stopwords
            tokens = [token for token in tokens if token not in stopWordList]

            # Removing non-alphanumeric words
            tokens = [token for token in tokens if re.search("(.*\w+.*)", token)]

            # Replacing tokens in other word list
            tokens = ["<O>" if token in otherWordList else token for token in tokens]

            print(tokens) # DEBUG
            break # DEBUG

    def __tokenize(self, text, tokens = []):
        tokens.append("<S>")
        for word in word_tokenize(text):
            tokens.append(word)
        tokens.append("<E>")

bg = BigramModel(dirName="documents") # DEBUG