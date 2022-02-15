import os, sys
import nltk
import numpy

class BigramModel:
    def __init__(self, name = "default", dirName = '.', ext = '*', toload = False, smooth = 0, stopWordList = [], otherWordList = [], singlesen = False):
        print(name)
        print(dirName)
        print(ext)
        print(toload)
        print(smooth)
        print(stopWordList)
        print(otherWordList)
        print(singlesen)

        if not os.path.isdir(dirName):
            sys.exit("Invalid file path: " + dirName)

        
