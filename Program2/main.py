from PLSI import PLSI

plsi = PLSI(dirName="Program2/_test", randomInit="", topicCount=3, iterations=2, toLoad=True)
print(plsi.getDocumentTopic(docName="a.txt"))
[print(x, y) for x, y in plsi.getAllDocumentTopic()]
print(plsi.getTopicWordVector(0, topCount=1))
print(plsi.getTopicWordVectorAll(topCount=1))
plsi.ExtendedPrint("_data")
plsi.save()