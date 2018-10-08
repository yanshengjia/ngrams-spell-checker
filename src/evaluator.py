# !/usr/bin/env python3
# -*- coding:utf-8 -*-  
# @author: Shengjia Yan
# @date: 2018-10-08 Monday
# @email: i@yanshengjia.com
# Copyright @ Shengjia Yan. All Rights Reserved.


import re
import json
import codecs
from time import time
from collections import Counter
from spell import *

import logging
logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] (%(asctime)s) (%(name)s) %(message)s',
        handlers=[
            logging.FileHandler('../data/log/spell.log', encoding='utf8'),
            logging.StreamHandler()
        ])
logger = logging.getLogger('evaluator')


class Evaluator:
    def __init__(self):
        self.spell_checker = SpellChecker()
        self.ielts_path = '../data/testset/ielts.json'
        self.result_path = '../data/result/result.json'
        self.test_set = self._load_dataset(self.ielts_path)
        self.result = []

    def _load_dataset(self, data_path):
        with codecs.open(data_path, 'r', encoding='utf8', errors='ignore') as in_file:
            data_set = []
            for line in in_file:
                line = line.strip()
                line_dict = json.loads(line)
                data_set.append(line_dict)
        return data_set
      
    def evaluate(self, save=True):
        self.ielts_typo_counter = 0
        self.detected_typo_counter = 0
        self.corrected_typo_counter = 0
        self.recall = 0.0
        self.precision = 0.0
        self.f1_score = 0.0

        case_num = 0
        for case in self.test_set:
            print(case_num)
            error_sentences = case['ERRORSENTS']
            for sentence_dict in error_sentences:
                sentence  = sentence_dict['SENT']
                typo_list = self.spell_checker.check(sentence)
                errors    = sentence_dict['ERRORS']
                for error in errors:
                    error['detected'] = 'False'
                    error['corrected'] = 'False'
                    if error['type'] == 'SPL':
                        self.ielts_typo_counter += 1
                        for typo_dict in typo_list:
                            if int(error['start']) == typo_dict['start']:
                                error['detected'] = 'True'
                                self.detected_typo_counter += 1
                                if error['answer'].lower() == typo_dict['correction']:
                                    error['corrected'] = 'True'
                                    self.corrected_typo_counter += 1
                                break
            self.result.append(case)
            case_num += 1
        
        self.recall = float(self.detected_typo_counter) / self.ielts_typo_counter
        self.precision = float(self.corrected_typo_counter) / self.detected_typo_counter
        self.f1_score = (2 * self.precision * self.recall) / (self.recall + self.precision)
        logger.info('IELTS typo quantity: {}'.format(self.ielts_typo_counter))
        logger.info('Detected typo quantity: {}'.format(self.detected_typo_counter))
        logger.info('Corrected typo quantity: {}'.format(self.corrected_typo_counter))
        logger.info('RECALL: {:.3f}, PRECISION: {:.3f}, F1: {:.3f}'.format(self.recall, self.precision, self.f1_score))

        if save:
            self._save_result()

    def _save_result(self):
        with open(self.result_path, 'w') as result_file:
            for res in self.result:
                res_json = json.dumps(res)
                result_file.write(res_json + '\n')
            logger.info('Result saved in {}'.format(self.result_path))

    def get_bad_case(self):
        pass

    def detection_speedtest(self):
        t0 = time()
        word_counter = 0

        case_num = 0
        for case in self.test_set:
            print(case_num)
            error_sentences = case['ERRORSENTS']
            for sentence_dict in error_sentences:
                sentence = sentence_dict['SENT']
                word_list = self.spell_checker.words(sentence)
                sentence_size = len(word_list)
                word_counter += sentence_size
                for word in word_list:
                    self.spell_checker.detect(word)
            case_num += 1

        t1 = time()
        logger.info("word sum: {}".format(word_counter))
        logger.info("detection time: {:.3f}s".format( t1 - t0 ))
        logger.info("detection time (per 100 words): {:.10f}s".format( (time() - t0) * 100.0 / word_counter ))


def main():
    evaluator = Evaluator()
    # evaluator.evaluate()
    evaluator.detection_speedtest()


if __name__ == '__main__':
    main()
