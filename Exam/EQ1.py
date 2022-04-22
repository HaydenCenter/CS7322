from nltk.corpus import wordnet as wn

board_1 = wn.synsets("board")[0]
board_2 = wn.synsets("board")[5]

print(board_1.hyponyms())
print(board_2.hyponyms())

hypo_1 = board_1.hyponyms()
hypo_2 = board_2.hyponyms()

for ss in wn.synsets("board"):
    hyper = ss.hypernyms()
    print(ss)
    for h in hyper:
        print(h.path_similarity(ss))
        for h1 in h.hypernyms():
            print(h1.path_similarity(ss))
            for h2 in h1.hypernyms():
                print(h2.path_similarity(ss))
                for h3 in h2.hypernyms():
                    print("H3",h3)
                    print(h3.path_similarity(ss))

print(wn.synset('board.n.03').hyponyms())