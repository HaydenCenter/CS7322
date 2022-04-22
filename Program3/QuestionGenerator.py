import spacy
from nltk.corpus import wordnet
from pattern.text.en import conjugate, PAST, PRESENT, SG, PL

nlp = spacy.load("en_core_web_sm")

try:
    print(conjugate('gave'))
except:
    pass

def isPerson(token):
    if token.pos_ == "PROPN" or "Prs" in token.morph.get("PronType"):
        return True

    for synset in wordnet.synsets(token.text, pos=wordnet.NOUN):
        person_ss = wordnet.synset('person.n.01')
        if person_ss in synset.lowest_common_hypernyms(person_ss):
            return True
    
    return False

def getEnd(doc):
    if doc[-1].is_punct:
        return -1
    return None

def conjugateVerb(token):
    param_map = {
        "Sing": SG,
        "Plur": PL,
        "Past": PAST,
        "Pres": PRESENT,
    }

    m = token.morph
    tense = m.get("Tense")
    if tense: 
        tense  = param_map.get(tense[0], None)
    else:
        tense = None

    if not tense:
        return token.lemma_
    else:
        return conjugate(token.lemma_, tense, 3, SG)



def getSubjectQuestion(sent):
    noun = next(chunk.root for chunk in sent.noun_chunks if chunk.root.dep_ == "nsubj")
    subject = sent[noun.left_edge.i:noun.right_edge.i + 1]

    verb = sent.root
    if verb.tag_ == 'VBG':
        verb = [c for c in verb.children if c.dep_ == "aux"][-1]

    
    conjugateVerb(verb)

    capital = subject.start == 0
    person = isPerson(noun)
    question_word = "who" if person else "what"
    if capital:
        question_word = question_word.capitalize()

    for token in sent[:getEnd(sent)]:
        if token == verb:
            if verb.text[0] == '\'': print(' ', end="")
            print(conjugateVerb(verb), end=verb.whitespace_)
        elif token.i == subject.start:
            print(question_word, end=subject[-1].whitespace_)
        elif token not in subject.subtree:
            print(token.text_with_ws, end="")
    print("?")

def getQuestions(sent):
    doc = nlp(sent)

    # Questions
    getSubjectQuestion(next(doc.sents)) 

    print(sent)
    print()

interactive = False

if interactive:
    # sentence = input("Enter a sentence: ")
    getQuestions("Samantha, Elizabeth, and Joan are on the committee.")
else:
    f = open("example.txt")
    sentences = f.read().splitlines()
    for sentence in sentences:
        getQuestions(sentence)