# !/usr/bin/python
# -*- coding:utf-8 -*-  
# @author: Shengjia Yan
# @date: 2017-11-17 Friday
# @email: i@yanshengjia.com

import re
import json
import codecs
from collections import Counter

def words(text):
    return re.findall(r'\w+', text.lower())     # \w+ matches one or more word characters (i.e., [a-zA-Z0-9_]).

WORDS = Counter(words(open('../data/big.txt').read()))

# probability of 'word'
def P(word, N=sum(WORDS.values())):
    return WORDS[word] / float(N)

# most probable spelling correction for word
def correction(word): 
    return max(candidates(word), key=P)

# generate possible spelling corrections for word
def candidates(word): 
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

# the subset of `words` that appear in the dictionary of WORDS
def known(words): 
    return set(w for w in words if w in WORDS)

# all edits that are one edit away from `word`
def edits1(word):
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

# all edits that are two edits away from `word`.
def edits2(word):
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def saveDict(path):
    with codecs.open(path, mode='w', encoding='UTF8') as dict_file:
        # big_dict = sorted(WORDS.items(), key=lambda x: x[1], reverse=True)
        big_dict = json.dumps(WORDS, ensure_ascii=False)
        dict_file.write(big_dict)

def main():
    print len(WORDS)
    print sum(WORDS.values())
    print WORDS.most_common(10)
    print max(WORDS, key=P)
    print P('the')
    print P('outrivaled')
    print P('unmentioned')
    
if __name__ == '__main__':
    main()


