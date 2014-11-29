import sys, math, pickle

def load_obj(name):
    #reader = csv.reader(open(name, 'r'))
    #return dict(x for x in reader)
    with open(name, 'rb') as fp:
        return pickle.load(fp)

def save_obj(obj, name ):
    #writer = csv.writer(open(name, 'w'))
    #for key, value in obj.items():
    #    writer.writerow([key,value])
    # listWriter = csv.DictWriter(open(name, 'wb'), fieldnames=obj[obj.keys()[0]].keys(), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # for a in obj:
    #     listWriter.writerow(a)
     with open(name, 'wb') as fp:
         pickle.dump(obj, fp, pickle.HIGHEST_PROTOCOL)

def load_lexicon(f):
    return load_obj(f)

def merge_dicts(l1, l2):
    lex = {}
    words = set(l1.keys()) | set(l2.keys())
    for w in words:
        lex[w] = l1.get(w, 0) + l2.get(w, 0)
    return lex

def build_lexicon(f, remove_n_words):
     with open(f, 'r') as f:
        lexicon = {}
        pentagrams = f.readlines()
        for pentagram in pentagrams:
            number_occurences = int(pentagram[0])
            words = pentagram.split()[1:]
            for w in words:
                if w not in lexicon:
                    lexicon[w] = 0
                lexicon[w] += number_occurences
        lex = list(lexicon.items())
        lex.sort(key=lambda x: -x[1])
        lex = lex[remove_n_words:]
        return dict(lex)

def bag_of_words(f, lexicon):
    vectors = {} # word => {w1: occ1, w2: occ2}
    with open(f, 'r') as f:
        pentagrams = f.readlines()
        print(len(pentagrams))
        for pentagram in pentagrams:
            number_occurences = int(pentagram[0])
            words = pentagram.split()[1:]

            for currentWord in words:
                if currentWord not in vectors:
                    vectors[currentWord] = {}
                for otherWord in words :
                    if otherWord is not currentWord:
                        if otherWord not in vectors[currentWord]:
                            vectors[currentWord][otherWord] = 0
                        vectors[currentWord][otherWord] += number_occurences

        return vectors
            
def tf_idf(bag_of_words, lexicon):
    #
    # bag_of_words.keys() => contexts
    # bag_of_words.values().keys() => tous les mots
    #
    n = len(bag_of_words)

    descriptions = {} # word => {context: dij}
    tf = {} # word => {context => double}
    context_counter = {} # document counter (df)

    for word in bag_of_words.keys():
        for jth_word in bag_of_words[word]:
            tf_ij = bag_of_words[word][jth_word] #the number of times the jth word type occurs in the ith context
            if jth_word not in tf:
                tf[jth_word] = {} 
            tf[jth_word][word] = tf_ij
            if jth_word not in context_counter:
                context_counter[jth_word] = 0
            context_counter[jth_word] += 1

    document_frequencies = {}
    g = {}
    for word in context_counter:
        document_frequencies[word] = context_counter[word] / n
        g[word] = -math.log(document_frequencies[word])
    
    for word in bag_of_words.keys():
        if word not in descriptions:
            descriptions[word] = {}
        if word in tf:
            for context in list(tf[word].keys()):
                descriptions[word][context] = tf[word][context] * document_frequencies[context]

    return descriptions

def sim(descriptions, w1, w2):
    dotProduct = 0
    for context in descriptions[w1]:
        if context in descriptions[w2]:
            s = descriptions[w1][context] * descriptions[w2][context]
            dotProduct += s
    lenW1 = 0
    for v in descriptions[w1].values():
        lenW1 += v*v
    lenW1 = math.sqrt(lenW1)
    lenW2 = 0
    for v in descriptions[w2].values():
        lenW2 += v*v
    lenW2 = math.sqrt(lenW2)
    # print(dotProduct)
    # print(lenW1)
    # print(lenW2)
    if (lenW1 * lenW2) == 0:
        return 0
    return dotProduct / (lenW1 * lenW2)

def creerLexique():
    lex = build_lexicon(sys.argv[1], int(sys.argv[2]))
    save_obj(lex, sys.argv[3])

def loadLexique():
    return load_obj(sys.argv[3])

def top20WordsLexicon(lexicon):
    lex = list(lexicon.items())
    lex.sort(key=lambda x: -x[1])
    for w in lex[:20]:
        print("{} : {}".format(w[0], w[1]))

def printTDIDFOfFurnaceAndFireworks(descriptions):
    print("fireworks: {}".format(descriptions["fireworks"]))
    print("furnace: {}".format(descriptions["furnace"]))

def printBagOfWordsOfFurnaceAndFireworks(bag):
    print("fireworks: {}".format(bag["fireworks"]))
    print("furnace: {}".format(bag["furnace"]))

def print10MostSimilarQueries(descriptions, lexicon):
    words = ["happy", "italy", "jump", "japan", "plane", "good", "planes", "october"]

    for word in words:
        similarWords = [(sim(descriptions, word, w), w) for w in lexicon]
        similarWords.sort()
        for simWord in similarWords[:11]:
            print(simWord)
    

if __name__ == '__main__':
    lex = build_lexicon("w5_.txt", 250)
    save_obj(lex, "lexicon.pkl")
    # lex = loadLexique() 

    bag = bag_of_words(sys.argv[1], lex)
    save_obj(bag, "bag.pkl")
    # bag = load_obj(sys.argv[2])

    descriptions = tf_idf(bag, lex)
    save_obj(descriptions, "descriptions.pkl")
    # descriptions = load_obj("descriptions.pkl")

    # top20WordsLexicon(lex)

    # printBagOfWordsOfFurnaceAndFireworks(bag)

    # printTDIDFOfFurnaceAndFireworks(descriptions)

    print10MostSimilarQueries(descriptions, lex)