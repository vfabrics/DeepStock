#-*- coding: utf-8 -*-
import pymongo
import codecs
import sys
import datetime
import time
import random
import pickle
sys.getdefaultencoding()

HOST = '10.0.1.201'
PORT = 27017
DB_NAME = "news"
COLLECTION_NAME = "naver"

def connect_mongodb(host, port, db_name, collection_name):

    conn = pymongo.MongoClient(host, port)
    db = conn['news']
    collection = db['naver']

    return collection

def get_data(collection, word):

    total_count = 100
    count = 0

    print("word : ", word)
    for cursor in collection.find({"content":{'$regex':word}}):
        count = count + 1
        if '_id' in cursor.keys():
            index = cursor['_id']
            if total_count == count:
                break
            else:
                print("%d/%d\tindex : %s"%(count, total_count, index))
                if 'content' in cursor.keys():
                    content = cursor['content']

                    filename = "word_contents/"+word+"_"+index.replace("|", "-")+".txt"
                    with codecs.open(filename, "w", "utf-8") as f_content:
                        print("filename : %s\n"%(filename))
                        f_content.write(content)

collection = connect_mongodb(HOST, PORT, DB_NAME, COLLECTION_NAME)

def get_company_contents_data(collection, filename):
    with open(filename) as f:
        lines = f.read().splitlines()

    for word in lines:
        get_data(collection, word)

get_company_contents_data(collection, "company.txt")

def get_content_data(collection, date):

    total_count = 100
    count = 0

    for cursor in collection.find({"articleDate":{'$regex':date}}):
        count = count + 1
        index = cursor['_id']
        print("%d/%d\tindex : %s"%(count, total_count, index))
        if 'content' in cursor.keys():
            content = cursor['content']

            filename = "news_content/"+index.replace("|", "-")+".txt"
            with codecs.open(filename, "w", "utf-8") as f_content:
                print("filename : %s\n"%(filename))
                f_content.write(content)

def content_to_file(collection, date):

    index = collection.find()

    count = 0
    total_count = collection.count()
    f_index = open("news_index_naver.txt", "w")
    f_no_index = open("news_no_index_naver.txt", "w")

    for cursor in collection.find({"articleDate":{'$regex':date}}):
        count = count + 1
        index = cursor['_id']
        print("%d/%d\tindex : %s"%(count, total_count, index))
        if 'content' in cursor.keys():
            content = cursor['content']

            f_index.write(index)
            f_index.write("\n")

            filename = "news_content/"+index.replace("|", "-")+".txt"
            with codecs.open(filename, "w", "utf-8") as f_content:
                print("filename : %s\n"%(filename))
                f_content.write(content)
        else:
            f_no_index.write(index)
            f_no_index.write("\n")

    f_index.close()
    f_no_index.close()

collection = connect_mongodb(HOST, PORT, DB_NAME, COLLECTION_NAME)
get_company_contents_data(collection, "company.txt")

def get_contents_from_db():
    _limit = 100

    for year in range(2017, 2014, -1):
        for month in range(12, 0, -1):
            for day in range(31, 0, -1):

                print("%d-%d-%d"%(year, month, day))
                content_list = []
                hashValue_list = []
                try:
                    if day == 1:
                        dt_end = datetime.datetime(year, month, day)
                        end = time.mktime(dt_end.timetuple())
                        start = end - 86400

                    else:
                        dt_start = datetime.datetime(year, month, day - 1)
                        dt_end = datetime.datetime(year, month, day)
                        start = time.mktime(dt_start.timetuple())
                        end = time.mktime(dt_end.timetuple())

                except:
                    print("no date")

                else:
                    print("find date | ", end='')
                    cursor = collection.find({"articleAt":{'$gte':start, '$lt':end}})
                    print("set date list | ", end='')
                    date_list = [x['_id'] for x in cursor]
                    print("list shuffle | ")
                    random.shuffle(date_list)

                    if len(date_list) > 100:
                        print("date_list size : %d\n"%(len(date_list)), end='')

                        i = 0
                        while i<_limit and i<len(date_list):
                            cur = collection.find({"_id":str(date_list[i])})
                            if 'content' in cur[0] and 'hashValue' in cur[0]:
                                _content = cur[0]['content']
                                if len(_content) > 50:
                                    _hashValue = cur[0]['hashValue']
                                    content_list.append(_content)
                                    hashValue_list.append(_hashValue)
                                else:
                                    _limit = _limit + 1
                            else:
                                _limit = _limit + 1
                            i += 1

                        contents_filename = "contents/%d-%d-%d.pickle"%(year, month, day)
                        hashValue_filename = "hashValue/%d-%d-%d_label.pickle"%(year, month, day)
                        with open(contents_filename, 'wb') as fp:
                            pickle.dump(content_list, fp)

                        with open(hashValue_filename, 'wb') as fp:
                            pickle.dump(hashValue_list, fp)

                        '''
                        with codecs.open(filename, "w", "utf-8") as f_content:
                            print("filename : %s\n"%(filename))
                            for content in content_list:
                                f_content.write("%s\n"%(content))
                        '''

get_contents_from_db()

################################################################################################


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


year = 2017
month = 6
day = 29

for year in range(2017, 2016, -1):
    for month in range(6, 5, -1):
        for day in range(31, 0, -1):

            contents_list = []
            hashValue_list = []
            contents_filename = "contents/%d-%d-%d.pickle"%(year, month, day)
            hashValue_filename = "hashValue/%d-%d-%d_label.pickle"%(year, month, day)

            contents_list.append(load_data(contents_filename))
            hashValue_list.append(load_data(hashValue_filename))




def text_to_sequence(sentence, dictionary):
    ret = []
    for word in sentence:
        if word in dictionary.keys():
           ret.append(dictionary[word])

    return ret


def convert2DListto1DList(list):
    result = []
    index = 0
    for element in list:
        print(index, end='')
        for subElement in element:
            result.append(subElement)
        index += 1

    return result

