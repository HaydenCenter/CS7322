from BigramModel import BigramModel

bg = BigramModel(dirName="Program1\\documents", smooth=.1)
bg.save()
print("\n".join([str(i) for i in bg.getAll(sortMethod=2)]))