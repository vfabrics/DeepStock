#-*- coding: utf-8 -*-
import os
import codecs
import pickle
import get_contents_data_from_db as g
import argparse
import numpy as np
from gensim.models import word2vec
from konlpy.tag import Twitter
tw = Twitter()

# ---------------------------
# data read
# ---------------------------
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

# ---------------------------
# 저장된 기사 데이터 및 레이블 읽기
# ---------------------------
def get_data_set(y, m, d):
    # y = year
    # m = month
    # d = day
    # 2017.06.31 부터 이전으로 계산
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


# ---------------------------
# 기사의 단어를 딕셔너리에 있는 단어의 인덱스로 변환 (딕셔너리에 없는 단어 제외)
# ---------------------------
def texts_to_sequences(text, dic):
    res = [dic[word] for word in text if word in dic]
    return res


# ---------------------------
# 단어 파싱 및 품사 형태로 저장
# 정규화 및 어근화
# ---------------------------
def tokenize(doc, tw):
    return ['/'.join(t) for t in tw.pos(doc, norm=True , stem=True)]


# ---------------------------
# 단어 파싱
# ---------------------------
def tokenize_word(doc, tw):
    return [t[0] for t in tw.pos(doc, norm=True , stem=True)]


# ---------------------------
# 문서의 단어를 이용해서 단어의 인덱스 사전 생성
# ---------------------------
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


# ---------------------------
# 2D list -> 1D list
# ---------------------------
def convert2DListto1DList(list):
    result = []
    for element in list:
        for subElement in element:
            result.append(subElement)

    return result


# ---------------------------
# 기사의 종류를 one-hot 인코딩으로 변환
# ---------------------------
def label_to_list(labels):
    # one-hot encoding
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


def strToBool(v):
    return v.lower() in ("true", "yes", "t", "1")

############################################################
if __name__ == "__main__":


    ###########################
    # argument parser
    ###########################
    parser = argparse.ArgumentParser()
    parser.add_argument("--l", default='False', type=str, help="data load")
    parser.add_argument("--t", default='False', type=str, help="test")
    parser.add_argument("--g", default='False', type=str, help="graph")
    args = parser.parse_args()

    flag_load = strToBool(args.l)
    flag_test = strToBool(args.t)
    flag_graph = strToBool(args.g)

    ###########################
    # STEP 1. Set Data
    # Create Dataset or Load Dataset
    ###########################

    #if flag_load == False:
    if os.path.isfile("contents_list.pickle")  == False:
        print("Get Data from DB")
        collection = g.connect_mongodb(g.HOST, g.PORT, g.DB_NAME, g.COLLECTION_NAME)
        g.get_contents_from_db()
        contents_list, labels_list = get_data_set(2016, 0, 0)

        train_docs = [tokenize(row, tw) for contents in contents_list for row in contents]

        print("Create Dictionary")
        dic = create_dictionary(train_docs)

        print("Texts to Sequences")
        res = [texts_to_sequences(docs, dic) for docs in train_docs]

        print("Save Data")

        # -------------------------
        # save data
        # -------------------------

        # 전체 기사
        with open("contents_list.pickle", 'wb') as fp:
            pickle.dump(contents_list, fp)

        # 종류
        with open("labels_list.pickle", 'wb') as fp:
            pickle.dump(labels_list, fp)

        # 파싱된 기사
        index = 0
        for start in range(0, len(train_docs), 20000):
            f = "docs/train_doc_"+str(index)+".pickle"
            index += 1
            with open(f, 'wb') as fp:
                end = start+20000
                if end > len(train_docs):
                    end = len(train_docs)
                pickle.dump(train_docs[start:end], fp)

        # 딕셔너리
        with open("dic.pickle", 'wb') as fp:
            pickle.dump(dic, fp)

        # index로 표현된 기사
        with open("res.pickle", 'wb') as fp:
            pickle.dump(res, fp)

    else:
        print("Load Data")

        # -------------------------
        # load data
        # -------------------------
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

    #######################################################################

    ###########################
    # STEP 2. Create Word2Vec Model using Gensim Library
    # Save model.pickle
    ###########################
    if os.path.isfile("model.pickle"):
        print("Load Model File")
        with open("model.pickle", 'rb') as fp:
            model = pickle.load(fp)
    else:
        print("Create Word2Vec model")
        # create model
        model = word2vec.Word2Vec(train_docs)

        print("Save Model File")
        with open("model.pickle", 'wb') as fp:
            pickle.dump(model, fp)

    model.init_sims(replace=True)
    #####################################################################################################

    #-----------------------------
    # test
    #-----------------------------
    if flag_test == True:

        # gensim test
        model.similarity(*tokenize('LG', tw), *tokenize(u'삼성', tw))

        from konlpy.utils import pprint

        # 상위 100 출력
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

        temp = np.array(word_similarity)
        temp_sort = np.sort(temp)[::-1]

        print(contents)

        for row in contents:
            train_docs = tokenize(row, tw)
            for words in train_docs:
                word_similarity.append(model.similarity(*tokenize(words, tw), *tokenize(u'삼성', tw)))
    #####################################################################################################

    print("Get Company List")

    # 회사 리스트
    with open('company.txt') as f:
        news_list = f.read().splitlines()

    '''
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
    '''

    ###########################
    # STEP 3. Similarity Test
    # 유사도 결과 저장 (pickle)
    ###########################
    if flag_graph == False:
        #----------------------------------
        # 기사 유사도 테스트
        #----------------------------------
        word_similarity = np.zeros([15, 15, 20])
        i = 0
        for news in news_list:
            file = "list_"+news+".txt"
            print("file : ", file)

            with open(file, "r") as f:
                contents_file_list = f.read().splitlines()
                #print(contents_file_list)

            # print(contents_file_list)
            k = 0
            for file in contents_file_list:
                if k < 20:
                    contents = None

                    # 기사읽기
                    print("Read Contents : %s"%(file))
                    with codecs.open("word_contents/"+file, "r", "utf-8") as f:
                        contents = f.read().splitlines()

                    for row in contents:
                        #print(row)
                        train_docs = tokenize(row, tw)
                        j = 0
                        for company in news_list:
                            temp = []
                            for words in train_docs:
                                try:
                                    temp.append(model.similarity(words, *tokenize(company, tw)))
                                except:
                                    pass
                                    #print("error : ", words)
                            temp_sort = np.sort(temp)[::-1]

                            word_similarity[i,j,k] = np.sum(temp_sort[0:10])/10.0
                            #print("[%d %d %d] = %f"%(i,j,k, word_similarity[i,j,k]))
                            j += 1
                        k += 1
            i += 1


        # ----------------------------
        # save word_similarity result
        # ----------------------------
        with open("result.pickle", 'wb') as fp:
            pickle.dump(word_similarity, fp)


    ###########################
    # STEP 4. Save result graph
    ###########################
    if flag_graph == True:
        # ----------------------------
        # 기사 유사도 그래프
        # ----------------------------
        print("Graph")
        import matplotlib.pyplot as plt
        from matplotlib import font_manager, rc

        with open("result.pickle", 'rb') as fp:
            word_similarity = pickle.load(fp)

        font_fname = 'c:/windows/fonts/NanumGothic.ttf'     # A font of your choice
        font_name = font_manager.FontProperties(fname=font_fname).get_name()
        rc('font', family=font_name)
        for i in range(0,15):
            fig = plt.figure()
            fig = plt.title(str(news_list[i]))
            fig = plt.xticks(range(len(news_list)), news_list, rotation=45)
            fig = plt.plot(word_similarity[i,:,0:5])
            filename = "graph_"+str(news_list[i]+".png")
            plt.savefig(filename)
