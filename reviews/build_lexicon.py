import sys
from os import listdir
from os.path import isfile, join
import json, re
from utils import *

def build_lexicon_from_file(f):
    with open(f, 'r') as f:
        lexicon = {}
        sentences = f.readlines()
        for s in sentences:
            s = s.replace("&\tamp\t;", "&")
            s = s.replace("&\tquot\t;", '"')
            l = build_lexicon_from_sentence(s)
            lexicon = merge_dicts(lexicon, l)
        return lexicon

def build_lexicon_from_sentence(s):
    date_regex = r"\d+/\d+/\d+"
    end_sentence = ".!?"
    lexicon = {}
    lexicon["<s>"] = 0
    start_sentence = True
    words = s.split('\t')
    skip = "(,)"
    for w in words:
        w = w.strip()
        if start_sentence and w not in end_sentence:
            lexicon["<s>"] += 1
            start_sentence = False
        if w == "he" or w == "she":
            w = "he/she"
        if w in skip:
            continue
        if re.search(date_regex, w) is not None:
            w = 'DATE'
        if w in end_sentence:
            start_sentence = True
        if w not in lexicon:
            lexicon[w] = 0
        lexicon[w] += 1

    return lexicon

def build_lexicon_from_repository(repo):
    lexicons = [ build_lexicon_from_file(join(repo,f)) for f in listdir(repo) if isfile(join(repo,f)) and not f.startswith('.') ]
    lex = {}
    for l in lexicons:
        lex = merge_dicts(lex, l)
    return lex        

if __name__ == '__main__':
    if len(sys.argv) > 3:
        first_lex = build_lexicon_from_repository(sys.argv[1])
        second_lex = build_lexicon_from_repository(sys.argv[2])
        lex = merge_dicts(first_lex, second_lex)
        save_obj(lex, sys.argv[3])
    # build_lexicon_from_file(sys.argv[1])