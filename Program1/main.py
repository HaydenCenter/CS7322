from BigramModel import BigramModel

bg = BigramModel(dirName="Program1\\documents")
bg.save()
print("\n".join([str(i) for i in bg.getAll()]))