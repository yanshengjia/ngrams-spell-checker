# !/usr/bin/python
# -*- coding:utf-8 -*-  
# @author: Shengjia Yan
# @date: 2017-11-29 Wednesday
# @email: i@yanshengjia.com

import json
import codecs

class ARPAParser:
    def __init__(self, parent=None):
        self.parent = parent
        self.n_max = 3
        self.lm_path = '../data/lm/corpus.lm'
        self.arpa_file = open(self.lm_path, 'r')
        self.info = ''
        self.lm = {}
        self.output_path = '../data/lm/lm.json'

    # the n in ngrams up to 3
    def extract(self):
        n = 1
        current = 1
        counter = 0
        for line in self.arpa_file.readlines():
            counter += 1            # line number starts from 1
            line = line.strip()     # line: probability\tngrams\tbackoff_weight, ngrams:[word1 word2 word3]

            if line == '' or line=='\\data\\' or line=='\\end\\':
                continue
            if counter >= 3 and counter <= (self.n_max + 2):
                self.info += line + '\n'
                continue
            if line == "\\" + str(n) + "-grams:":
                current = n
                n += 1
                continue

            list = line.split('\t')
            dict = {}
            dict['log_p'] = list[0]
            if len(list) == 3:     # backoff weight exist
                dict['log_bw'] = list[2]
            else:   # backoff weight doesn't exist (equals to 1, log10(bw)==0)
                dict['log_bw'] = 0.0
            self.lm[list[1]] = dict
    
    def saveLM(self):
        with open(self.output_path, 'w') as output_file:
            lm = json.dumps(self.lm, ensure_ascii=False)
            output_file.write(lm)

def main():
    parser =  ARPAParser()
    parser.extract()
    parser.saveLM()

if __name__ == "__main__":
    main()