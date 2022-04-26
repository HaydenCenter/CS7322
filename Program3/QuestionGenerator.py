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

    person_ss = wordnet.synset('person.n.01')
    synsets = wordnet.synsets(token.text, pos=wordnet.NOUN)
    count = 0
    total = 0
    for synset in synsets:
        x = sum(lemma.count() for lemma in synset.lemmas() if lemma.name() == token.lemma_)
        total += x
        if person_ss in synset.lowest_common_hypernyms(person_ss):
            count += x

    if count > 0 and total / count > 0.5:
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

def printWithReplacement(phrase, sent, verb, question_word):
    for token in sent[:getEnd(sent)]:
        if token == verb:
            if verb.text[0] == '\'': print(' ', end="")
            print(conjugateVerb(verb), end=verb.whitespace_)
        elif token.i == phrase.start:
            print(question_word, end=phrase[-1].whitespace_)
        elif token not in phrase.subtree:
            print(token.text_with_ws, end="")
    print("?")

def getQuestionWord(phrase, root):
    capital = phrase.start == 0
    person = isPerson(root)
    question_word = "who" if person else "what"
    if capital:
        question_word = question_word.capitalize()

    return question_word


def getSubjectQuestion(sent):
    noun = next(chunk.root for chunk in sent.noun_chunks if chunk.root.dep_ == "nsubj")
    noun_phrase = sent[noun.left_edge.i:noun.right_edge.i + 1]

    verb = sent.root
    if verb.tag_ == 'VBG':
        verb = [c for c in verb.children if c.dep_ == "aux"][-1]

    qw = getQuestionWord(noun_phrase, noun)
    printWithReplacement(noun_phrase, sent, verb, question_word=qw)

def getDirectionObjectQuestion(sent):
    dobjs = [token for token in sent if token.dep_ == "dobj"]
    if dobjs:
        dobj = dobjs[0]
        dobj_phrase = sent[dobj.left_edge.i:dobj.right_edge.i + 1]

        qw = getQuestionWord(dobj_phrase, dobj)
        printWithReplacement(dobj_phrase, sent, verb=None, question_word=qw)    
def getQuestions(sent):
    print(f'\n{sent}')

    doc = next(nlp(sent).sents)

    # Questions
    getSubjectQuestion(doc)
    getDirectionObjectQuestion(doc)

interactive = True

if interactive:
    sentence = input("Enter a sentence: ")
    getQuestions(sentence)
else:
    f = open("example.txt")
    sentences = f.read().splitlines()
    for sentence in sentences:
        getQuestions(sentence)