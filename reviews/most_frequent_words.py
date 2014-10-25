import sys
from utils import load_lexicon
import operator

def most_frequent_words(lexicon, n):
    lexicon = {k : int(v) for k,v in lexicon.items()}
    sorted_lex = sorted(lexicon.items(), key=operator.itemgetter(1))
    most_freq = sorted_lex[-n:]
    most_freq.reverse()
    return most_freq

if __name__ == '__main__':
    if len(sys.argv) > 2:
        lex = load_lexicon(sys.argv[1])
        for freq in most_frequent_words(lex, int(sys.argv[2])):
            print("{} {}".format(freq[0], freq[1]))