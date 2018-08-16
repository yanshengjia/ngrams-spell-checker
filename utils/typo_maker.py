# !/usr/bin/python
# -*- coding:utf-8 -*-  
# @author: Shengjia Yan
# @date: 2017-12-04 Monday
# @email: i@yanshengjia.com

import re
import json
import codecs
import random
from collections import Counter


class TypoMaker:
    def __init__(self, parent=None):
        self.parent = parent
        self.typo_size = 3
        self.corpus_path = '../../data/corpus/17zuoye/raw/all.txt'
        self.word_dict = Counter(self.words(open(self.corpus_path).read()))
        self.raw_path = '../data/testset/raw/raw_'
        self.essay_path = '../data/testset/essay/essay_'
        self.typo_path = '../data/testset/typo/typo_'

    def words(self, text):
        return re.findall(r'\w+', text.lower())

    # return True if the word exists in the dictionary
    def lookup(self, word):
        if word in self.word_dict:
            return True
        else:
            return False
    
    # modify 1 or 2 letters in a correct word to make a typo
    # 80% modify 1 letter, 20% modify 2 letters
    def mistake(self, word):
        word_size = len(word)
        letter_list = list(word)
        dice = random.randint(0, 9)
        choice = 2 if dice < 2 else 1

        if choice == 1:
            position = random.randint(0, word_size - 1)
            letter_list[position] = self.random_letter(word[position])
        else:
            position1 = random.randint(0, word_size - 1)
            position2 = random.randint(0, word_size - 1)
            while position1 == position2:
                position2 = random.randint(0, word_size - 1)
            letter_list[position1] = self.random_letter(word[position1])
            letter_list[position2] = self.random_letter(word[position2])
        typo = "".join(letter_list)
        if self.lookup(typo):
            return self.mistake(word)
        else:
            return typo
    
    # return a random lowercase letter
    def random_letter(self, letter):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        alphabet = alphabet.replace(letter, '')
        new_letter = random.choice(alphabet)
        return new_letter

    def generate_testset(self, quantity):
        counter = 0
        with codecs.open(self.corpus_path, mode='r', encoding='UTF8') as corpus_file:
            for line in corpus_file.readlines():
                line = line.strip()
                raw = line
                word_list = self.words(line)
                word_quantity = len(word_list)

                if word_quantity < 100:
                    continue
                counter += 1
                if counter > quantity:
                    break
                
                raw_path = self.raw_path + str(counter) + '.txt'
                essay_path = self.essay_path + str(counter) + '.txt'
                typo_path = self.typo_path + str(counter) + '.txt'
                typo_str = ""
                typo_quantity = int(word_quantity * 0.1)

                for i in range(typo_quantity):
                    low = i * 10
                    high = i * 10 + 9
                    if high >= word_quantity:
                        high = word_quantity - 1
                    position = random.randint(low, high)
                    word = word_list[position]

                    if len(word) <= self.typo_size:
                        continue

                    # filter words which contain any digit
                    if any(ch.isdigit() for ch in word):
                        continue

                    typo = self.mistake(word)
                    word_list[position] = typo
                    typo_str += word + ': ' + typo + '\n'

                essay = " ".join(word_list)

                with codecs.open(raw_path, mode='w', encoding='UTF8') as raw_file:
                    raw_file.write(raw)
                with codecs.open(essay_path, mode='w', encoding='UTF8') as essay_file:
                    essay_file.write(essay)
                with codecs.open(typo_path, mode='w', encoding='UTF8') as typo_file:
                    typo_file.write(typo_str)

def main():
    type_maker = TypoMaker()
    type_maker.generate_testset(500)

if __name__ == "__main__":
    main()