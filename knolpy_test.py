#-*- coding: utf-8 -*-
from soynlp.tokenizer import RegexTokenizer, MaxScoreTokenizer
import pprint
import codecs
from krwordrank.word import KRWordRank
import numpy as np

from krwordrank.hangle import normalize
import pickle
from konlpy.tag import Twitter

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
    contents_list = []
    hashValue_list = []
    for year in range(2017, y, -1):
        for month in range(6, m, -1):
            for day in range(31, d, -1):

                contents_filename = "contents/%d-%d-%d.pickle"%(year, month, day)
                hashValue_filename = "hashValue/%d-%d-%d_label.pickle"%(year, month, day)

                contents = load_data(contents_filename)
                hashValue = load_data(hashValue_filename)

                if contents and hashValue:
                    contents_list.append(contents)
                    hashValue_list.append(hashValue)

    return contents_list, hashValue_list

def texts_to_sequences(text, dic):
    #res = []
    res = [dic[word] for word in text if word in dic]
    #for word in text:
    #    if word in dic:
    #        res.append(dic[word])

    return res


def tokenize(doc, tw):
    return ['/'.join(t) for t in tw.pos(doc, norm=True , stem=True)]

def tokenize_word(doc, tw):
    return [t[0] for t in tw.pos(doc, norm=True , stem=True)]


def create_dictionary(doc):
    # tokenize
    tokens = [t for d in train_docs for t in d]
    dict = list(set(tokens))

    index = 1
    dic = {}
    for word in dict:
        dic[word] = index
        index += 1

    return dic


def convert2DListto1DList(list):
    result = []
    for element in list:
        for subElement in element:
            result.append(subElement)

    return result


def label_to_list(labels):
    res = np.zeros([len(labels), 6])
    index = 0
    for label in labels:
        if label == 3:
            res[index,0] = 1
        elif label == 4:
            res[index,1] = 1
        elif label == 6:
            res[index,2] = 1
        elif label == 7:
            res[index,3] = 1
        elif label == 8:
            res[index,4] = 1
        elif label == 10:
            res[index,5] = 1

        index += 1

    return res


# load docs
#contents_list, labels_list = get_data_set(2016, 5, 10)
contents_list, labels_list = get_data_set(2016, 0, 0)
tw = Twitter()

from joblib import Parallel, delayed

ttrain_docs = Parallel(n_jobs=6)(delayed([tokenize(row, tw) for contents in contents_list for row in contents]))

train_docs = [tokenize(row, tw) for contents in contents_list for row in contents]
dic = create_dictionary(train_docs)
res = [texts_to_sequences(docs, dic) for docs in train_docs]
with open("contents_list.pickle", 'wb') as fp:
    pickle.dump(contents_list, fp)

with open("labels_list.pickle", 'wb') as fp:
    pickle.dump(labels_list, fp)

index = 0
for start in range(0, len(train_docs), 20000):
    f = "docs/train_doc_"+str(index)+".pickle"
    index += 1
    with open(f, 'wb') as fp:
        end = start+20000
        if end > len(train_docs):
            end = len(train_docs)
        pickle.dump(train_docs[start:end], fp)

with open("dic.pickle", 'wb') as fp:
    pickle.dump(dic, fp)

with open("res.pickle", 'wb') as fp:
    pickle.dump(res, fp)

######################################################
with open("contents_list.pickle", 'rb') as fp:
    contents_list = pickle.load(fp)

with open("labels_list.pickle", 'rb') as fp:
    labels_list = pickle.load(fp)

with open("dic.pickle", 'rb') as fp:
    dic = pickle.load(fp)

with open("res.pickle", 'rb') as fp:
    res = pickle.load(fp)

start = 0
f = "docs/train_doc_"+str(start)+".pickle"
with open(f, 'rb') as fp:
    train_docs = pickle.load(fp)

for start in range(1, 9):
    f = "docs/train_doc_"+str(start)+".pickle"
    print("fname : %s"%f)

    with open(f, 'rb') as fp:
        train_docs = train_docs + pickle.load(fp)

# 2d to 1d
_res = convert2DListto1DList(res)
# _res = sum(res, [])
_labels = sum(labels_list, [])


from gensim.models import word2vec
model = word2vec.Word2Vec(train_docs)
model.init_sims(replace=True)

model.similarity(*tokenize('LG', tw), *tokenize(u'삼성', tw))

from konlpy.utils import pprint

pprint(model.most_similar(positive=tokenize('cj', tw), topn=100))


words = "삼성"
word_similarity = []
#for contents in contents_list[0]:

contents = contents_list[0][0]
train_docs = tokenize(contents, tw)
for words in train_docs:
    try:
        word_similarity.append(model.similarity(words, *tokenize(u'삼성', tw)))
    except:
        print("error : %s"%words)

import numpy as np
temp = np.array(word_similarity)
temp_sort = np.sort(temp)[::-1]

print(contents)

for row in contents:
    train_docs = tokenize(row, tw)
    for words in train_docs:
        word_similarity.append(model.similarity(*tokenize(words, tw), *tokenize(u'삼성', tw)))

news_list = [
"CJ",
"LG",
"SK",
u"교보",
u"넥슨",
u"동양",
u"두산",
u"롯데",
u"삼성",
u"제일모직",
u"포스코",
u"한전",
u"한진",
u"한화",
u"현대"]

word_similarity = np.zeros([15, 15, 20])
i = 0
for news in news_list:
    file = "list_"+news+".txt"
    print("file : ", file)

    with open(file, "r") as f:
        contents_file_list = f.read().splitlines()
        print(contents_file_list)
    # print(contents_file_list)
    k = 0
    for file in contents_file_list:
        if k < 20:
            contents = None

            # 기사읽기
            with codecs.open("word_contents/"+file, "r", "utf-8") as f:
                contents = f.read().splitlines()

            for row in contents:
                print(row)
                train_docs = tokenize(row, tw)
                j = 0
                for company in news_list:
                    temp = []
                    for words in train_docs:
                        try:
                            temp.append(model.similarity(words, *tokenize(company, tw)))
                        except:
                            print("error : ", words)
                    temp_sort = np.sort(temp)[::-1]

                    word_similarity[i,j,k] = np.sum(temp_sort[0:10])/10.0
                    print("[%d %d %d] = %f"%(i,j,k, word_similarity[i,j,k]))
                    j += 1
                k += 1
    i += 1


filelist= "word_contents.txt"
f = open(filelist, "r")
f.read().splitlines()


import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
font_fname = 'c:/windows/fonts/NanumGothic.ttf'     # A font of your choice
font_name = font_manager.FontProperties(fname=font_fname).get_name()
rc('font', family=font_name)
for i in range(0,15):
    fig = plt.figure()
    fig = plt.title(str(news_list[i]))
    fig = plt.xticks(range(len(news_list)), news_list, rotation=45)
    fig = plt.plot(word_similarity[i,:,0:5])
