# !/usr/bin/python
# -*- coding:utf-8 -*-  
# @author: Shengjia Yan
# @date: 2017-11-17 Friday
# @email: i@yanshengjia.com

import re
import json
import nltk
import codecs
import string
from collections import Counter
from time import time
from nltk.tokenize.treebank import TreebankWordTokenizer

import logging
logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] (%(asctime)s) (%(name)s) %(message)s',
        handlers=[
            logging.FileHandler('../data/log/spell.log', encoding='utf8'),
            logging.StreamHandler()
        ])
logger = logging.getLogger('spell')


class SpellChecker:
    def __init__(self):
        self.corpus_path = '../data/corpus/corpus.txt'
        self.lm_path = '../data/lm/lm.json'
        self.lm = self.load_lm()
        self.word_dict = Counter(self.words(open(self.corpus_path).read()))
        self._word_tokenizer = TreebankWordTokenizer()

    def load_lm(self):
        logger.info('Loading n-grams language model...')
        t0 = time()
        with open(self.lm_path) as lm_json:
            lm = json.load(lm_json)
        logger.info("   Done in {:.3f}s".format(time() - t0))
        return lm

    def get_dict_size(self):
        unique_word_number = len(self.word_dict)
        return unique_word_number

    def words(self, text):
        return re.findall(r'\w+', text.lower())
    
    def tokenize(self, text):
        return self._word_tokenizer.tokenize(text)

    def span_tokenize(self, text):
        token_list = []     # [{'token': the, 'index': 0, 'start': 0, 'end': 6, 'length': 6}]
        start = 0
        index = 0
        for word_token in self.tokenize(text):
            token_dict = {}
            start = text.find(word_token, start)
            length = len(word_token)
            end = start + length
            token_dict['index']  = index
            token_dict['start']  = start
            token_dict['end']    = end
            token_dict['length'] = length
            token_dict['token']  = word_token
            token_list.append(token_dict)
            start = end
            index += 1
        return token_list
    
    def known(self, words):
        '''
        the subset of `words` that appear in the dictionary of WORDS
        '''
        return set(w for w in words if w in self.word_dict)

    def edits1(self, word):
        '''
        all edits that are one edit away from 'word'
        '''
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word): 
        '''
        all edits that are two edits away from 'word'
        '''
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def lookup(self, word):
        '''
        return True if the word exists in the dictionary
        '''
        if word in self.word_dict:
            return True
        else:
            return False
    
    def candidates(self, word):
        '''
        generate possible spelling corrections for word
        '''
        return self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word))

    def probability(self, c, b, a):
        '''
        ngrams (n up to 3) conditional probability of 'word' with backoff strategy
        P(c | a b)
        a b c
        c: candidate, always in our word list
        a b: words before c, may or may not in our word list
        '''
        abc = a + ' ' + b + ' ' + c
        ab = a + ' ' + b
        bc = b + ' ' + c

        if abc in self.lm:
            p = pow(10, float(self.lm[abc]['log_p']))
        else:
            if ab in self.lm:
                if bc in self.lm:
                    p = pow(10, float(self.lm[ab]['log_bw']) + float(self.lm[bc]['log_p']))
                else:
                    p = pow(10, float(self.lm[ab]['log_bw']) + float(self.lm[b]['log_bw']) + float(self.lm[c]['log_p']))
            else:
                if bc in self.lm:
                    p = pow(10, float(self.lm[bc]['log_p']))
                else:
                    if b in self.lm:
                        p = pow(10, float(self.lm[b]['log_bw']) + float(self.lm[c]['log_p']))
                    else:
                        p = pow(10, float(self.lm[c]['log_p']))
        return p

    def detect(self, word):
        '''
        return True if the word is a typo
        '''
        if word in set(string.punctuation):
            return False
        if word.replace('.', '', 1).isdigit():
            return False
        if len(word) == 1 and word.isalpha():
            return False

        if self.lookup(word) or self.lookup(word.lower()):
            return False
        else:
            return True
    
    def correct(self, word, pre1, pre2):
        '''
        generate most probable spelling correction for typo 'word'
        '''
        candidates_list = self.candidates(word)
        correction_dict = {}
        rank_list = []

        for candidate in candidates_list:
            try:
                p = self.probability(candidate, pre1, pre2)
                correction_dict[candidate] = p
            except:
                correction_dict[candidate] = 0

        if not candidates_list:
            correction = '<unk>'
        else:
            correction = max(correction_dict, key=correction_dict.get)
        correction_list = sorted(correction_dict.items(), key=lambda x: x[1], reverse=True)

        for item in correction_list:
            rank_list.append(item[0])
        return correction, rank_list

    def check(self, sentence):
        token_list = self.span_tokenize(sentence)
        typo_list  = []     # [{'typo': appll, 'correction': apple, 'start': 0, 'end': 5, 'offset': 5}]

        for token_dict in token_list:
            token = token_dict['token']
            if self.detect(token):
                index = token_dict['index']

                if index == 0:
                    pre1, pre2 = '', ''
                elif index == 1:
                    pre1, pre2 = token_list[index - 1]['token'], ''
                else:
                    pre1, pre2 = token_list[index - 1]['token'], token_list[index - 2]['token']

                correction, rank_list = self.correct(token, pre1, pre2)

                typo_dict = {}
                typo_dict['typo'] = token
                typo_dict['correction'] = correction
                typo_dict['start'] = token_dict['start']
                typo_dict['end'] = token_dict['end']
                typo_dict['length'] = token_dict['length']
                typo_list.append(typo_dict)
        return typo_list


def main():
    speller = SpellChecker()
    dict_size = speller.get_dict_size()
    print(dict_size)

if __name__ == '__main__':
    main()

