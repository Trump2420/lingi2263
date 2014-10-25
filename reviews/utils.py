import sys, json, pickle
import csv

def load_obj(name):
    reader = csv.reader(open(name, 'r'))
    return dict(x for x in reader)
    # with open(name, 'rb') as fp:
    #     return pickle.load(fp)

def save_obj(obj, name ):
    writer = csv.writer(open(name, 'w'))
    for key, value in obj.items():
        writer.writerow([key,value])
    # listWriter = csv.DictWriter(open(name, 'wb'), fieldnames=obj[obj.keys()[0]].keys(), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # for a in obj:
    #     listWriter.writerow(a)
    # with open(name, 'wb') as fp:
    #     pickle.dump(obj, fp, pickle.HIGHEST_PROTOCOL)

def load_lexicon(f):
    return load_obj(f)

def merge_dicts(l1, l2):
    lex = {}
    words = set(l1.keys()) | set(l2.keys())
    for w in words:
        lex[w] = l1.get(w, 0) + l2.get(w, 0)
    return lex