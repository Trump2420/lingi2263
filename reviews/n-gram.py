import sys
import operator
import re
from utils import *
from os import listdir
from os.path import isfile, join

def build_ngram_from_text(f, n):
    with open(f, 'r') as f:
        text = "\t".join(f.readlines())
        ngram = {} # (n-words) => nb. occurences
        prev_words = []
        text = text.replace("&\tamp\t;", "&")
        text = text.replace("&\tquot\t;", '"')

        words = text.split('\t')
        compound_word = ""
        date_regex = r"\d+/\d+/\d+"
        end_sentence = ".!?"
        is_start_sentence = True
        start_sentence = []
        skip = "(,)"
        is_compound_word = False

        for w in range(len(words)):
            words[w] = words[w].strip()
            if is_start_sentence and words[w] not in end_sentence:
                start_sentence.append(w)
                is_start_sentence = False
            if words[w] == "he" or words[w] == "she":
                words[w] = "he/she"
            if words[w] in skip:
                words[w] = ""
            if re.search(date_regex, words[w]) is not None:
                words[w] = 'DATE'
            if words[w] in end_sentence:
                is_start_sentence = True
            if words[w].startswith("_"):
                is_compound_word = True
            if is_compound_word:
                compound_word += words[w]
                words[w] = ""
            if words[w].endswith("_"):
                is_compound_word = False
                words[w] = compound_word
                compound_word = ""

        for s in start_sentence[::-1]:
            words.insert(s, "<s>")

        words = [x for x in words if x]
        
        for i in range(len(words)):
            n_tuple = tuple(words[i-n:i])
            if n_tuple not in ngram:
                ngram[n_tuple] = 0
            ngram[n_tuple] += 1
        return ngram

def frequency_of_frequencies(ngram):
    current_ngram_count = 0
    frequencies = {}

    for value in set(ngram.values()):
        frequencies[value] = len([x for x in ngram.values() if x == value])

    return frequencies

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

        freq_oFreqs = frequency_of_frequencies(merged_gram)
        
        save_obj(freq_oFreqs, sys.argv[4])
