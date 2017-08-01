#-*- coding: utf-8 -*-
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