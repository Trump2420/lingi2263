import sys
import operator
from utils import *
from os import listdir
from os.path import isfile, join

def build_ngram_from_text(f, n):
    with open(f, 'r') as f:
        text = "\t".join(f.readlines())
        ngram = {} # (n-words) => nb. occurences
        prev_words = []
        words = text.split('\t')
        for i in range(len(words)):
            n_tuple = str(tuple(words[i-n:i]))
            if n_tuple not in ngram:
                ngram[n_tuple] = 0
            ngram[n_tuple] += 1
        return ngram

def build_ngram_from_repository(repo, n):
    ngrams = [ build_ngram_from_text(join(repo,f), n) for f in listdir(repo) if isfile(join(repo,f)) and not f.startswith('.') ]
    gram = {}
    for g in ngrams:
        gram = merge_dicts(gram, g)
    return gram        

if __name__ == '__main__':
    # n = 2
    # merged_gram = build_ngram_from_text(sys.argv[1], n)
    # print(merged_gram)
    # save_obj(merged_gram, sys.argv[2])
    if len(sys.argv) > 4:
        n = int(sys.argv[3])
        first_gram = build_ngram_from_repository(sys.argv[1], n)
        second_gram = build_ngram_from_repository(sys.argv[2], n)
        merged_gram = merge_dicts(first_gram, second_gram)
        save_obj(merged_gram, sys.argv[4])
