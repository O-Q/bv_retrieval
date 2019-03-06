import sys
import pickle  # For serializing data
import os.path  # For checking whether a file exist

from nltk.stem import PorterStemmer as ps  # For stemming and word tokenization


def isint(s):
    try:
        int(s)
    except ValueError:
        return False
    return True


# Takes a file that has a list of files
def getInputFiles(filelist):
    with open(filelist) as f:
        return [a for a in f.read().split("\n") if a != ""]


files = os.listdir('./docs')
for i in range(len(files)):
    files[i] = './docs/' + files[i];


# Removes most special characters and caps
def preprocess(data):
    for p in "!.,:@#$%^&?<>*()[}{]-=;/\"\\\t\n":
        if p in '\n;?:!.,.':
            data = data.replace(p, ' ')
        else:
            data = data.replace(p, '')
    return data.lower()


# For each file, opens and adds it to the hashmap
def createPositionalIndex(files):
    index = {}
    for i in range(len(files)):
        with open(files[i]) as f:
            doc = [a for a in preprocess(f.read()).split(' ') if a != ""]
        for idx, word in enumerate(doc):
            stemmed = ps().stem(word)
            if not stemmed in index:
                index[stemmed] = [(i, idx)]
            else:
                index[stemmed].append((i, idx))
    print(index)
    return index


# shows a preview based on the positions and the how
# much text to show around the data found
def showPreview(docs, radius):
    for i, doc_id in docs:
        print(str(i + 1) + ".(" + files[doc_id].split("/")[-1] + ")")
    print()


# Serialization/Positional Index
pi = {}
if os.path.isfile("index_data"):  # if we have indexed the docs we just load it
    print("Loading data...")
    with open("index_data", "rb") as f:
        pi = pickle.load(f)
        print(pi)
else:
    print("Processing and serializing data for future use...")
    pi = createPositionalIndex(files)
    with open("index_data", "wb") as f:
        pickle.dump(pi, f)


def andOp(index, words):
    for i in range(len(words)):
        words[i] = ps().stem(preprocess(words[i]).replace(' ', ''))
    docs = [[]]
    for i in range(len(words)):
        for doc, ind in index[words[i]]:
            docs[i].append(doc)
        docs[i] = set(docs[i])

    res = []
    if len(words) == 2:
        for i in range(len(docs[0])):
            for j in range(len(docs[1])):
                if docs[0][i] == docs[1][j]:
                    res.append(docs[0][i])
    if len(words) == 3:
        for i in range(len(docs[0])):
            for j in range(len(docs[1])):
                for k in range(len(docs[2])):
                    if docs[0][i] == docs[1][j] == docs[2][k]:
                        res.append(docs[0][i])
    return res


def orOp(index, words):
    for i in range(len(words)):
        words[i] = ps().stem(preprocess(words[i]).replace(' ', ''))
    docs = []
    res = []
    for i in range(len(words)):
        for doc, ind in index[words[i]]:
            docs.append(doc)
        docs = set(docs)
    return res


# User interface and positional index querying
while True:
    print("Enter Query: ")
    sys.stdout.write("'/exit' to close > ")
    q = [a for a in input().lower().split(' ') if a != ""]
    for i in range(q):
        q[i] = q[i].lower()

    matches = []
    words = [q[0]]
    operators = []
    rad1 = -1
    rad2 = -1
    if q[1] == 'near' and q[4] == 'near':
        words.append(q[3])
        words.append(q[6])
        operators.append('near')
        operators.append('near')
        rad1 = int(q[2])
        rad2 = int(q[5])

    elif q[1] == 'near':
        words.append(q[3])
        words.append(q[5])
        operators.append('near')
        operators.append(q[4])
        rad1 = int(q[2])

    elif q[3] == 'near':
        words.append(q[2])
        words.append(q[5])
        operators.append(q[1])
        operators.append('near')
        rad1 = int(q[4])
    else:
        words.append(q[2])
        words.append(q[4])
        operators.append(q[1])
        operators.append(q[3])

    if q[1] == 'and':

    if len(q) == 1 and q[0] == '/exit':
        exit()
    elif len(q) == 2:
        word1, word2 = q
        word1 = ps().stem(preprocess(word1).replace(' ', ''))
        word2 = ps().stem(preprocess(word2).replace(' ', ''))
        print("Searching... \n")
        for doc1, index1 in pi[word1]:
            for doc2, index2 in pi[word2]:
                if doc1 != doc2: continue
                if index1 == (index2 - 1): matches.append((doc1, index1))
        showPreview(matches, 5)
    elif len(q) == 3:
        word1, word2, l = q
        if not isint(l):
            print("arg 3 needs to be an int\n")
            continue
        word1 = ps().stem(preprocess(word1).replace(' ', ''))
        word2 = ps().stem(preprocess(word2).replace(' ', ''))
        print("Searching... \n")
        rad = int(l)
        for doc1, index1 in pi[word1]:
            for doc2, index2 in pi[word2]:
                if doc1 != doc2: continue
                abs_pos = abs(index1 - index2)
                # when abs_pos is 0, the word is itself
                if abs_pos <= rad and abs_pos != 0: matches.append((doc1, index1))
        showPreview(matches, 5 if rad <= 5 else rad)
    else:
        print("Needs to have 2 or 3 args\n")
