# Spell Checker

对一篇给定的英文作文，基于 Dictionary Lookup 的方法识别其中的错别字 (Spell Checking)，然后用编辑距离和 N-grams 语言模型相结合的方法给出错别字的候选修正单词。

目前在500篇带有随机生成错别字的测试集上，自动修正的准确率为 90.2%。

***

Spell Checking: Dictionary Lookup

Auto Correction:

* Edit Distance <= 2
* N-grams (n up to 3)