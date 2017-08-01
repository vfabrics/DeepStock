#-*- coding: utf-8 -*-
from soynlp.tokenizer import RegexTokenizer, MaxScoreTokenizer
import pprint
from krwordrank.word import KRWordRank

from krwordrank.hangle import normalize
import pickle

def load_data(filename):
    data_list = []
    try:
        with open(filename, 'rb') as fp:
            data = pickle.load(fp)
            data_list.append(data)
            print("read : %s"%(filename))
        return data_list[0]

    except:
        print("error : %s"%(filename))

def get_data_set(y, m, d):
    for year in range(2017, y, -1):
        for month in range(6, m, -1):
            for day in range(31, d, -1):

                contents_list = []
                hashValue_list = []
                contents_filename = "contents/%d-%d-%d.pickle"%(year, month, day)
                hashValue_filename = "hashValue/%d-%d-%d_label.pickle"%(year, month, day)

                contents_list.append(load_data(contents_filename))
                hashValue_list.append(load_data(hashValue_filename))

    return contents_list, hashValue_list

def get_texts_scores(docs):
    docs = [doc for doc in docs if len(doc) == 2]

    return docs

texts_list, labels_list = get_data_set(2016, 5, 10)

tokenizer = MaxScoreTokenizer()
pprint.pprint(tokenizer.tokenize(texts_list[0][0]))


min_count = 3   # 단어의 최소 출현 빈도수 (그래프 생성 시)
max_length = 10 # 단어의 최대 길이
wordrank_extractor = KRWordRank(min_count, max_length)

beta = 0.85    # PageRank의 decaying factor beta
max_iter = 10
verbose = True
keywords, rank, graph = wordrank_extractor.extract(texts_list[0][94], beta, max_iter, verbose)


for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True)[:30]:
    print('%8s:\t%.4f' % (word, r))

top_keywords = []

for texts in texts_list:
    wordrank_extractor = KRWordRank(min_count, max_length)
    try:
        keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter, verbose=False)
    except:
        print("no vocabs")
    else:
        top_keywords.append(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:100])
        print(len(top_keywords))

for texts in texts_list:
    wordrank_extractor = KRWordRank(min_count, max_length)
    keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter, verbose=False)
    top_keywords.append(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:100])
    print(len(top_keywords))

for k in range(100):
    message = '  --  '.join(['%8s (%.3f)' % (top_keywords[i][k][0], top_keywords[i][k][1]) for i in range(3)])
    print(message)

for k in range(100):
    message = '  --  '.join(['%8s (%.3f)' % (top_keywords[1][k][0], top_keywords[1][k][1]) ])
    print(message)

from konlpy.tag import Twitter
twitter = Twitter()

word = twitter.pos(texts_list[0][0], norm=True, stem=True, )
twitter.phrases()

pprint.pprint(word)