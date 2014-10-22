import sys, json

def load_obj(name):
    with open(name, 'r') as fp:
        return json.load(fp)

def save_obj(obj, name ):
    with open(name, 'w') as fp:
        json.dump(obj, fp)

def load_lexicon(f):
    return load_obj(f)

def merge_dicts(l1, l2):
    lex = {}
    words = set(l1.keys()) | set(l2.keys())
    for w in words:
        lex[w] = l1.get(w, 0) + l2.get(w, 0)
    return lex